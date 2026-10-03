# IoT Shield — Network Threat Detection System

Real-time IoT network security threat detection using ML ensemble with Firebase bridge and cloud-ready Streamlit dashboard.

## Project Info
- **Degree**: B.E. CSE 7th Sem, VTU — Global Academy of Technology
- **Course**: CSEP23605
- **Dataset**: IoT-23 (Stratosphere IPS Lab) — 6M rows

## System Architecture

```
[Local Monitored Network]
          │
          ▼
   step5_live.py (Scapy Packet Capture)
          │
          ▼
   ML Ensemble (Random Forest + XGBoost)
          │
          ▼
   Firebase Realtime Database (HTTPS push)
          │
          ▼
[Streamlit Cloud Dashboard (step4_dashboard.py)]
   ├── Real-time Telemetry & Alert Stream
   ├── Class Analytics & Confusion Matrix
   └── AI Security Assistant (Gemini / Groq / Ollama)
```

| Layer | Description | Tools | Deployment Target |
|-------|-------------|-------|-------------------|
| L1 | Data Collection | IoT-23 CSV + Scapy | Local Sensor Node |
| L2 | Preprocessing | pandas, MinMaxScaler | Local Sensor Node |
| L3 | Feature Engineering | Categorical Encoders, Feature Selection | Local Sensor Node |
| L4 | ML Detection | Random Forest + XGBoost ensemble | Local Sensor Node |
| L5 | Telemetry Bridge | Firebase Realtime Database | Cloud Bridge |
| L6 | Dashboard & AI | Streamlit + Plotly + Gemini/Groq | Streamlit Community Cloud |

## Results
| Model | Accuracy |
|-------|----------|
| Random Forest | 99.99% |
| XGBoost | 100.00% |
| Ensemble (RF×0.45 + XGB×0.55) | 100.00% |

## Classes
- `benign` — normal traffic
- `ddos` — Distributed Denial of Service
- `malware` — Okiru botnet, C&C traffic
- `portscan` — Horizontal port scanning

---

## Local Setup & Detection Backend

### 1. Environment Installation
```bash
conda create -n iotfinal python=3.11
conda activate iotfinal
pip install -r requirements-local.txt
```

### 2. Prepare Data and Train Models (One-Time)
```bash
python step1_prepare.py
python step2_train.py
```

### 3. Run Live Packet Capture (Local Node)
Run in an **Administrator** shell with Npcap installed:
```bash
python step5_live.py --reset
```

### 4. Or Run Simulation Mode (No Admin Rights Needed)
```bash
python step5_simulate.py --reset --speed 2
```

---

## Streamlit Cloud Deployment

1. **Repository Settings**:
   - **Repository**: Your GitHub repo URL
   - **Branch**: `main`
   - **Main file path**: `step4_dashboard.py`
   - **Python version**: `3.11`

2. **Streamlit Secrets** (in App Settings -> Secrets):
   ```toml
   FIREBASE_DB_URL = "https://your-project-default-rtdb.region.firebasedatabase.app"
   GEMINI_API_KEY = "your_google_ai_studio_key"
   # or
   GROQ_API_KEY = "your_groq_api_key"
   ```

3. **Deploy**: Streamlit Cloud will install dependencies from `requirements.txt` and run the live dashboard.

---

## Base Paper
Maghrabi, L.A. (2024). "Automated Network Intrusion Detection for Internet of Things."
IEEE Access, vol. 12, pp. 30839–30851. DOI: 10.1109/ACCESS.2024.3369237