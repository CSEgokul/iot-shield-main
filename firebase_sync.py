"""
firebase_sync.py — IoT Shield <-> Firebase Realtime Database bridge.

WHY THIS FILE EXISTS
    Streamlit Cloud cannot run Scapy or see your LAN traffic, so the detection
    backend (step5_live.py / step5_simulate.py) has to run on your LOCAL
    machine. This module is the bridge between that local backend and the
    public cloud dashboard:

        local backend  --push-->  Firebase Realtime DB  --fetch-->  cloud dashboard

DESIGN (deliberately asymmetric)
    * WRITE side  -> firebase-admin SDK + a service-account key.  LOCAL ONLY.
                     The key is secret and must never be committed to git.
    * READ side   -> a single plain HTTPS GET against the RTDB REST API.
                     No SDK and no key needed, so the Streamlit Cloud deploy
                     stays light (it only uses `requests`, already installed).
                     This requires the DB rules to allow public read.
    * If Firebase is not configured, every function is a safe no-op, so the
      whole project still runs fully offline exactly as before.

ONE-TIME SETUP
    1. Create a Firebase project + Realtime Database.
    2. Paste your database URL into DATABASE_URL below or set FIREBASE_DB_URL.
    3. Download a service-account key -> save as firebase_key.json in project root
       (already gitignored). Only the LOCAL backend uses this file.
    4. Set the RTDB security rules to:
           { "rules": { ".read": true, ".write": false } }
    5. Locally:  pip install firebase-admin   (in your local conda/venv)
"""

import os
import json
import time
import requests

try:
    # pyrefly: ignore [missing-import]
    import firebase_admin
    # pyrefly: ignore [missing-import]
    from firebase_admin import credentials, db
except ImportError:
    firebase_admin = None  # type: ignore
    credentials = None     # type: ignore
    db = None              # type: ignore

# ── Dynamic Config Helpers ──────────────────────────────────────────────────

def get_database_url():
    """Retrieve the Firebase Realtime Database URL from Streamlit secrets,
    environment variables, or the default configured URL."""
    # 1. Try Streamlit secrets if running inside Streamlit
    try:
        # pyrefly: ignore [missing-import]
        import streamlit as st
        if hasattr(st, "secrets") and "FIREBASE_DB_URL" in st.secrets:
            val = str(st.secrets["FIREBASE_DB_URL"]).strip().rstrip("/")
            if val:
                return val
    except Exception:
        pass

    # 2. Try environment variable
    env_url = os.environ.get("FIREBASE_DB_URL", "").strip().rstrip("/")
    if env_url:
        return env_url

    # 3. Default fallback URL
    return "https://iot-shield-7ce30-default-rtdb.asia-southeast1.firebasedatabase.app"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Default module-level DATABASE_URL for backwards compatibility
DATABASE_URL = get_database_url()

# Path to the service-account key. SECRET. Local writers only. Gitignored.
_CRED_PATH = os.environ.get(
    "FIREBASE_CRED",
    os.path.join(BASE_DIR, "firebase_key.json"),
)

ALERTS_NODE = "live_alerts"
STATS_NODE = "live_stats"
STATUS_NODE = "system_status"
DEVICES_NODE = "devices"
_MIN_PUSH_INTERVAL = 2.0  # seconds — throttle writes to protect the free tier

# ── Internal write-side state ─────────────────────────────────────────────────
_db = None
_init_ok = False
_last_init_attempt = 0.0
_last_push = 0.0


def _url_ok(url=None):
    target = url or get_database_url()
    return bool(target) and "YOUR-PROJECT" not in target


def _clean_for_firebase(obj):
    """Recursively convert numpy types (int64, float64), tuples, etc.
    into standard JSON-serializable Python types for Firebase."""
    if isinstance(obj, dict):
        return {str(k): _clean_for_firebase(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean_for_firebase(v) for v in obj]
    item_fn = getattr(obj, "item", None)
    if callable(item_fn):
        try:
            return item_fn()
        except Exception:
            pass
    return obj


def _get_cert_credentials():
    """Safely obtain credentials for firebase-admin from file, environment,
    or Streamlit secrets without exposing secret keys in logs.
    Returns credentials object or None."""
    if credentials is None:
        # firebase-admin not installed (e.g. on Streamlit Cloud)
        return None

    # 1. Check Streamlit secrets (dict or json string or path)
    try:
        # pyrefly: ignore [missing-import]
        import streamlit as st
        if hasattr(st, "secrets"):
            if "firebase_key" in st.secrets:
                key_data = st.secrets["firebase_key"]
                if isinstance(key_data, (dict, list)):
                    # Pure dict conversion for Streamlit AttrDict
                    pure_dict = json.loads(json.dumps(key_data))
                    return credentials.Certificate(pure_dict)
                if isinstance(key_data, str) and os.path.isfile(key_data):
                    return credentials.Certificate(key_data)
                if isinstance(key_data, str):
                    return credentials.Certificate(json.loads(key_data))
            if "FIREBASE_KEY_JSON" in st.secrets:
                return credentials.Certificate(json.loads(st.secrets["FIREBASE_KEY_JSON"]))
    except Exception:
        pass

    # 2. Check FIREBASE_KEY_JSON environment variable (JSON string)
    env_json = os.environ.get("FIREBASE_KEY_JSON")
    if env_json:
        try:
            return credentials.Certificate(json.loads(env_json))
        except Exception:
            pass

    # 3. Check local file on disk across common search paths
    possible_paths = [
        _CRED_PATH,
        os.path.join(BASE_DIR, "firebase_key.json"),
        os.path.join(os.getcwd(), "firebase_key.json"),
        os.path.join(BASE_DIR, "data", "firebase_key.json"),
    ]
    for path in possible_paths:
        if path and os.path.isfile(path):
            try:
                return credentials.Certificate(path)
            except Exception:
                pass

    return None


def is_configured():
    """True if database URL is valid AND write credentials exist."""
    if not _url_ok():
        return False
    return _get_cert_credentials() is not None


def has_database_url():
    """True if a valid database URL is set (for read-only REST fetch on cloud)."""
    return _url_ok()


def _ensure_admin():
    """Lazily initialise firebase-admin for the WRITE side. Returns True on success.
    Safely retries if credentials were provided after initial module import."""
    global _init_ok, _db, _last_init_attempt
    if _init_ok:
        return True

    now = time.time()
    if (now - _last_init_attempt) < 5.0:
        return False
    _last_init_attempt = now

    db_url = get_database_url()
    if not _url_ok(db_url):
        print("[firebase] DATABASE_URL not set — sync disabled (writing local files only).")
        return False

    cred = _get_cert_credentials()
    if not cred:
        print("[firebase] Service-account key not found — sync disabled (local files only).")
        return False

    if firebase_admin is None or db is None:
        print("[firebase] firebase_admin package not available — sync disabled.")
        return False

    try:
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred, {"databaseURL": db_url})
        _db = db
        _init_ok = True
        print(f"[firebase] Connected -> {db_url}")
        return True
    except Exception as e:
        print(f"[firebase] Init failed ({type(e).__name__}) — sync disabled (local files only).")
        _init_ok = False
        return False


def push(alerts, stats, force=False):
    """WRITE side. Mirror the current alerts list + stats dict to the RTDB.
    Throttled to at most once per _MIN_PUSH_INTERVAL seconds unless force=True
    (use force=True on shutdown / final flush so nothing is lost)."""
    global _last_push
    if not _ensure_admin() or _db is None:
        return False
    now = time.time()
    if not force and (now - _last_push) < _MIN_PUSH_INTERVAL:
        return False
    try:
        clean_alerts = _clean_for_firebase(alerts)
        clean_stats = _clean_for_firebase(stats)
        _db.reference(ALERTS_NODE).set(clean_alerts)
        _db.reference(STATS_NODE).set(clean_stats)
        _last_push = now
        return True
    except Exception as e:
        print(f"[firebase] Push failed: {type(e).__name__}")
        return False


def push_heartbeat(status_dict):
    """WRITE side. Sends a detector heartbeat record to system_status/detector."""
    if not _ensure_admin() or _db is None:
        return False
    try:
        clean_status = _clean_for_firebase(status_dict)
        _db.reference(f"{STATUS_NODE}/detector").set(clean_status)
        return True
    except Exception as e:
        print(f"[firebase] Heartbeat push failed: {type(e).__name__}")
        return False


def push_devices(devices_dict):
    """WRITE side. Updates monitored devices record under devices/."""
    if not _ensure_admin() or _db is None:
        return False
    try:
        clean_devices = _clean_for_firebase(devices_dict)
        _db.reference(DEVICES_NODE).update(clean_devices)
        return True
    except Exception as e:
        print(f"[firebase] Devices push failed: {type(e).__name__}")
        return False


def fetch(timeout=4, include_meta=False):
    """READ side. One HTTPS GET of the whole DB.
    No SDK / key needed. Returns (alerts_list, stats_dict) by default,
    or (alerts_list, stats_dict, system_status_dict, devices_dict) if include_meta=True.
    Returns (None, None) / (None, None, None, None) on failure."""
    db_url = get_database_url()
    if not _url_ok(db_url):
        return (None, None, None, None) if include_meta else (None, None)
    try:
        r = requests.get(f"{db_url}/.json", timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, dict):
            return (None, None, None, None) if include_meta else (None, None)

        alerts = data.get(ALERTS_NODE)
        stats = data.get(STATS_NODE)
        system_status = data.get(STATUS_NODE, {})
        devices = data.get(DEVICES_NODE, {})

        # Format alerts as list safely regardless of key format
        if isinstance(alerts, dict):
            try:
                alerts = [alerts[k] for k in sorted(alerts.keys(), key=lambda x: int(x) if str(x).isdigit() else str(x))]
            except Exception:
                alerts = list(alerts.values())
        elif not isinstance(alerts, list):
            alerts = []

        if not isinstance(stats, dict):
            stats = {"total": 0, "threats": 0, "critical": 0, "benign": 0}

        if not isinstance(system_status, dict):
            system_status = {}

        if not isinstance(devices, dict):
            devices = {}

        if include_meta:
            return alerts, stats, system_status, devices
        return alerts, stats
    except Exception:
        return (None, None, None, None) if include_meta else (None, None)

