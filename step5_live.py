"""
step5_live.py — IoT Shield Live Capture & Detection
Run as Administrator: python step5_live.py
Writes: data/live_alerts.json
        data/live_stats.json
"""

import os
import sys
import json
import time
import threading
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Firebase Realtime Database bridge — pushes alerts/stats to the cloud dashboard.
# Safe no-op if firebase isn't configured (see firebase_sync.py).
import firebase_sync

import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import sniff, IP, TCP, UDP, conf

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR   = os.path.join(BASE_DIR, "models")
DATA_DIR    = os.path.join(BASE_DIR, "data")
ALERTS_FILE = os.path.join(DATA_DIR, "live_alerts.json")
STATS_FILE  = os.path.join(DATA_DIR, "live_stats.json")
STATUS_FILE = os.path.join(DATA_DIR, "system_status.json")
DEVICES_FILE= os.path.join(DATA_DIR, "devices.json")
os.makedirs(DATA_DIR, exist_ok=True)

REQUIRED_MODEL_FILES = [
    "rf_model.pkl", "xgb_model.pkl", "scaler.pkl",
    "label_enc.pkl", "cat_encoders.pkl", "feature_cols.pkl"
]
missing_models = [m for m in REQUIRED_MODEL_FILES if not os.path.exists(os.path.join(MODEL_DIR, m))]
if missing_models:
    print(f"[!] Missing trained model files in {MODEL_DIR}: {', '.join(missing_models)}")
    print("[!] Please run 'python step2_train.py' first to train and generate the models.")
    sys.exit(1)

print("[*] Loading models...")
rf_model     = joblib.load(os.path.join(MODEL_DIR, "rf_model.pkl"))
xgb_model    = joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl"))
scaler       = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
label_enc    = joblib.load(os.path.join(MODEL_DIR, "label_enc.pkl"))
cat_encoders = joblib.load(os.path.join(MODEL_DIR, "cat_encoders.pkl"))
feature_cols = joblib.load(os.path.join(MODEL_DIR, "feature_cols.pkl"))

CLASSES = list(label_enc.classes_)
print(f"[*] Classes : {CLASSES}")
print(f"[*] Features: {feature_cols}")

_model_ready = True
_start_time = datetime.now(timezone.utc).isoformat()
_detected_iface_name = "Wi-Fi"
_capture_active = False
_firebase_write_ok = False
_last_packet_time = None

_observed_devices = {}
_devices_lock = threading.Lock()

SEVERITY = {
    "benign":   "none",
    "ddos":     "critical",
    "malware":  "critical",
    "portscan": "high",
}

_flows = defaultdict(lambda: {
    "ts": None, "orig_ip": None,
    "orig_pkts": 0, "orig_ip_bytes": 0,
    "resp_pkts": 0, "resp_ip_bytes": 0,
    "missed_bytes": 0,
    "proto": "", "service": "", "conn_state": "SF",
    "id.orig_p": 0, "id.resp_p": 0,
})
_flow_lock = threading.Lock()

_stats = {
    "total": 0, "threats": 0, "critical": 0, "benign": 0,
    "start_time": datetime.now().isoformat(),
}

_alerts = []
_alerts_lock = threading.Lock()
MAX_ALERTS = 200
_pkt_count = 0


    while True:
        time.sleep(5)
        _write_stats()
        _sync_firebase()
        _sync_system_status("online")
        _sync_devices()
        with _pkt_lock: n=_pkt_count
        print(f"[~] Packets: {n:,}  |  Flows: {len(_flows)}  |  Scored: {len(_scored)}  |  Alerts: {_stats['total']}")

def _pick_interface():
    global _detected_iface_name
    SKIP_KEYWORDS = [
        "loopback", "virtual", "vpn", "bluetooth",
        "wi-fi direct", "miniport", "npcap"
    ]
    PREFER_KEYWORDS = [
        "wireless", "wi-fi", "wifi", "wlan", "802.11",  # WiFi
        "ethernet", "local area",                         # Ethernet
        "remote ndis", "usb",                             # USB tethering
        "mobile", "hotspot", "tethering",                 # Hotspot
    ]
    try:
        ifaces = conf.ifaces
        candidates = []
        for name, iface in ifaces.items():
            desc = str(getattr(iface, "description", "")).lower()
            if any(k in desc for k in SKIP_KEYWORDS):
                continue
            score = 0
            for i, kw in enumerate(PREFER_KEYWORDS):
                if kw in desc:
                    score = len(PREFER_KEYWORDS) - i
                    break
            if score > 0:
                candidates.append((score, name, desc))

        if candidates:
            candidates.sort(reverse=True)
            for score, name, desc in candidates:
                print(f"    Found: {desc} [{name}]")
            chosen = candidates[0][1]
            _detected_iface_name = candidates[0][2]
            print(f"[*] Auto-selected: {_detected_iface_name}")
            return chosen

    except Exception as e:
        print(f"[!] Interface detection error: {e}")

    print("[*] Using Scapy default interface")
    _detected_iface_name = "Default Interface"
    return None

def _init_files():
    import sys
    reset = "--reset" in sys.argv
    if reset or not os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE,"w") as f: json.dump([],f)
        if reset: print("[*] Alert feed cleared.")
    if reset or not os.path.exists(STATS_FILE):
        _write_stats()

if __name__ == "__main__":
    print("="*60)
    print("  IoT Shield - Live Capture  (Ctrl+C to stop)")
    print("  Use --reset to clear alerts on startup")
    print("="*60)
    _init_files()
    if "--reset" in sys.argv:
        firebase_sync.push([], _stats, force=True)  # clear the cloud feed too
    if firebase_sync.is_configured():
        print("[*] Firebase : bridge enabled (cloud dashboard will receive live data)")
    else:
        print("[*] Firebase : not configured — writing local files only")
    
    # Send immediate initial online heartbeat
    _sync_system_status("online")

    threading.Thread(target=_stats_flusher, daemon=True).start()
    iface = _pick_interface()
    print(f"[*] Alert feed : {ALERTS_FILE}")
    print(f"[*] Score after: {_SCORE_AFTER} originator packets\n")
    try:
        if iface:
            print(f"[*] Starting capture on selected interface...")
            sniff(iface=iface, filter="ip", prn=_packet_callback, store=False)
        else:
            print(f"[*] Starting capture on all interfaces...")
            sniff(filter="ip", prn=_packet_callback, store=False)
    except PermissionError:
        print("\n[!] Run as Administrator.")
    except KeyboardInterrupt:
        print(f"\n[*] Stopped. Total scored: {_stats['total']}")
        _capture_active = False
        _sync_system_status("offline")
        _write_stats()
        _sync_firebase(force=True)