# CMS Prior Authorization ML Pipeline — Jetson Thor Setup Guide

**Document ID:** PMS-EXP-CMSPA-SETUP-001
**Version:** 1.0
**Date:** 2026-03-07
**Applies To:** MarginLogic PA Outcome Intelligence (Experiment 43)
**Target Hardware:** NVIDIA Jetson AGX Thor (JetPack 7.0)
**Prerequisites Level:** Intermediate

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Part A: HIPAA Hardening the Jetson Thor](#3-part-a-hipaa-hardening-the-jetson-thor)
4. [Part B: ML Stack Installation](#4-part-b-ml-stack-installation)
5. [Part C: PostgreSQL Feature Store Setup](#5-part-c-postgresql-feature-store-setup)
6. [Part D: MLflow Experiment Tracking](#6-part-d-mlflow-experiment-tracking)
7. [Part E: Download and Build the CMS PA Dataset](#7-part-e-download-and-build-the-cms-pa-dataset)
8. [Part F: FastAPI + Streamlit Serving](#8-part-f-fastapi--streamlit-serving)
9. [Part G: Verification Checklist](#9-part-g-verification-checklist)
10. [Troubleshooting](#10-troubleshooting)
11. [Reference Commands](#11-reference-commands)

---

## 1. Overview

This guide sets up a complete, HIPAA-compliant ML pipeline on the NVIDIA Jetson Thor for prior authorization prediction. By the end, you will have:

- A HIPAA-hardened Jetson with full-disk encryption, firewall, and audit logging
- GPU-accelerated XGBoost/LightGBM training via CUDA
- PostgreSQL feature store with encrypted connections
- MLflow for local experiment tracking (no PHI in the cloud)
- The CMS synthetic PA dataset built and loaded
- FastAPI + Streamlit ready for local serving

```mermaid
graph TB
    subgraph JETSON["NVIDIA Jetson Thor — HIPAA Hardened"]
        subgraph SEC["Security Layer"]
            LUKS["LUKS Full-Disk Encryption"]
            UFW["UFW Firewall"]
            AUDIT["auditd Logging"]
        end
        subgraph DATA["Data Layer"]
            PG[("PostgreSQL\n(Feature Store)")]
            PARQUET["Parquet Files\n(CMS Dataset)"]
        end
        subgraph ML["ML Layer"]
            XGB["XGBoost gpu_hist\n(CUDA 13.0)"]
            LGBM["LightGBM GPU"]
            SHAP["SHAP TreeExplainer"]
            MLF["MLflow\n(Local Tracking)"]
        end
        subgraph SERVE["Serving Layer"]
            API["FastAPI\n(Risk Scoring)"]
            DASH["Streamlit\n(Dashboard)"]
        end
        SEC --> DATA --> ML --> SERVE
    end
```

---

## 2. Prerequisites

| Requirement | Details |
|-------------|---------|
| **Hardware** | NVIDIA Jetson AGX Thor |
| **JetPack** | 7.0 (L4T R38, CUDA 13.0) |
| **OS** | Ubuntu 22.04 (Jetson default) |
| **Storage** | 256GB+ NVMe SSD (LUKS encryption overhead ~10%) |
| **Network** | Internet access for initial setup only; operates air-gapped after |
| **SSH Access** | From a trusted workstation only |

---

## 3. Part A: HIPAA Hardening the Jetson Thor

The HIPAA Security Rule (45 CFR 164.312) requires technical safeguards for ePHI. This section implements the four required categories: access control, audit controls, integrity controls, and transmission security.

### Step 1: Enable LUKS Full-Disk Encryption (164.312(a)(2)(iv))

LUKS encrypts data at rest. If the Jetson is stolen or decommissioned, PHI is unreadable without the passphrase.

> **Important:** LUKS is easiest to configure at OS install time. If the Jetson is already running, you can encrypt a secondary data partition instead of the root filesystem.

**Option A: Encrypt secondary data partition (recommended for existing installs)**

```bash
# Identify the data partition (adjust /dev/nvme0n1p3 to your layout)
sudo apt install cryptsetup

# Create encrypted partition (THIS DESTROYS DATA — back up first)
sudo cryptsetup luksFormat /dev/nvme0n1p3
# Enter and confirm a strong passphrase (20+ characters, store in a password manager)

# Open the encrypted partition
sudo cryptsetup luksOpen /dev/nvme0n1p3 marginlogic_data

# Create filesystem
sudo mkfs.ext4 /dev/mapper/marginlogic_data

# Mount
sudo mkdir -p /data/marginlogic
sudo mount /dev/mapper/marginlogic_data /data/marginlogic

# Set ownership
sudo chown -R marginlogic:marginlogic /data/marginlogic
```

**Auto-mount on boot (requires passphrase at boot):**

```bash
# Add to /etc/crypttab
echo "marginlogic_data /dev/nvme0n1p3 none luks" | sudo tee -a /etc/crypttab

# Add to /etc/fstab
echo "/dev/mapper/marginlogic_data /data/marginlogic ext4 defaults 0 2" | sudo tee -a /etc/fstab
```

**Option B: Full-disk encryption at install time**

If you are re-flashing the Jetson, use the NVIDIA SDK Manager and select "Enable disk encryption" during the L4T flash process. This encrypts the entire root filesystem.

**Verify encryption:**

```bash
sudo cryptsetup status marginlogic_data
# Should show: type: LUKS2, cipher: aes-xts-plain64, keysize: 512 bits
```

### Step 2: Create a Dedicated Non-Sudo User (164.312(a)(1))

All ML workloads run as an unprivileged user. This limits blast radius if the application is compromised.

```bash
# Create the user with no sudo access
sudo useradd -m -s /bin/bash -d /home/marginlogic marginlogic
sudo passwd marginlogic
# Set a strong password

# Grant access to the encrypted data directory
sudo chown -R marginlogic:marginlogic /data/marginlogic

# Grant GPU access (required for CUDA)
sudo usermod -aG video marginlogic
sudo usermod -aG render marginlogic
```

### Step 3: Configure UFW Firewall (164.312(e)(1))

Deny all inbound traffic except SSH from your specific IP.

```bash
sudo apt install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH only from your workstation IP
sudo ufw allow from <YOUR_WORKSTATION_IP> to any port 22 proto tcp

# If serving Streamlit/FastAPI to TRA during pilot (via Cloudflare Tunnel):
# Do NOT open ports 8000/8501 directly — Cloudflare Tunnel handles this
# The tunnel runs outbound, so no inbound rule is needed

# Enable
sudo ufw enable
sudo ufw status verbose
```

**Expected output:**

```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    <YOUR_WORKSTATION_IP>
```

### Step 4: Configure Audit Logging (164.312(b))

`auditd` logs all file access, authentication events, and privilege escalation — required for HIPAA audit trail.

```bash
sudo apt install auditd audispd-plugins

# Start and enable
sudo systemctl enable auditd
sudo systemctl start auditd

# Add audit rules for PHI data access
cat << 'EOF' | sudo tee /etc/audit/rules.d/marginlogic.rules
# Monitor all access to the PHI data directory
-w /data/marginlogic/ -p rwxa -k phi_data_access

# Monitor PostgreSQL data directory
-w /var/lib/postgresql/ -p rwxa -k postgres_data_access

# Monitor user authentication
-w /etc/passwd -p wa -k user_accounts
-w /etc/shadow -p wa -k user_accounts

# Monitor sudo usage
-w /var/log/auth.log -p wa -k auth_log

# Monitor SSH config changes
-w /etc/ssh/sshd_config -p wa -k ssh_config

# Monitor crontab changes
-w /var/spool/cron/ -p wa -k cron_changes
EOF

# Reload rules
sudo augenrules --load
sudo systemctl restart auditd

# Verify rules are loaded
sudo auditctl -l
```

**Test the audit trail:**

```bash
# As marginlogic user, touch a file in the PHI directory
sudo -u marginlogic touch /data/marginlogic/test_audit.txt

# Check the audit log
sudo ausearch -k phi_data_access -ts recent
# Should show the file creation event with timestamp, user, and action
```

### Step 5: Disable Unnecessary Services

```bash
# List running services
sudo systemctl list-units --type=service --state=running

# Disable services not needed for ML workloads
sudo systemctl disable --now cups.service          # Printing
sudo systemctl disable --now avahi-daemon.service   # mDNS (network discovery)
sudo systemctl disable --now bluetooth.service      # Bluetooth
sudo systemctl disable --now ModemManager.service   # Modem
sudo systemctl disable --now whoopsie.service       # Error reporting

# Disable X11/Wayland if running headless
sudo systemctl set-default multi-user.target
```

### Step 6: SSH Hardening

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

cat << 'EOF' | sudo tee /etc/ssh/sshd_config.d/marginlogic.conf
# Disable password auth (use key-based only)
PasswordAuthentication no
PubkeyAuthentication yes

# Disable root login
PermitRootLogin no

# Allow only the marginlogic and your admin user
AllowUsers marginlogic <YOUR_ADMIN_USERNAME>

# Timeout idle sessions after 15 minutes
ClientAliveInterval 300
ClientAliveCountMax 3

# Disable X11 forwarding
X11Forwarding no

# Log level
LogLevel VERBOSE
EOF

sudo systemctl restart sshd
```

**Copy your SSH key before disabling password auth:**

```bash
# From your workstation
ssh-copy-id marginlogic@<JETSON_IP>
# Test key login works BEFORE restarting sshd
```

### Step 7: Automatic Security Updates

```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
# Select "Yes" to enable automatic security updates
```

### HIPAA Technical Safeguard Verification

| HIPAA Requirement | Section | Implementation | Status |
|-------------------|---------|----------------|--------|
| Access Control — Unique User ID | 164.312(a)(2)(i) | `marginlogic` user, SSH key auth | |
| Access Control — Encryption at Rest | 164.312(a)(2)(iv) | LUKS full-disk or partition encryption | |
| Audit Controls | 164.312(b) | `auditd` with PHI-specific rules | |
| Integrity — Authentication | 164.312(c)(2) | SHA-256 checksums on data transfers | |
| Transmission Security — Encryption | 164.312(e)(2)(ii) | SSH for admin, Cloudflare Tunnel for pilot | |
| Automatic Logoff | 164.312(a)(2)(iii) | SSH `ClientAliveInterval` 5 min | |

---

## 4. Part B: ML Stack Installation

All commands run as the `marginlogic` user unless otherwise specified.

### Step 1: Python Virtual Environment

```bash
sudo -u marginlogic -i   # Switch to marginlogic user

# Create project directory on encrypted partition
mkdir -p /data/marginlogic/projects/experiment-43
cd /data/marginlogic/projects/experiment-43

# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### Step 2: Install ML Dependencies

```bash
pip install \
    pandas numpy scipy \
    scikit-learn \
    xgboost \
    lightgbm \
    shap \
    optuna \
    mlflow \
    pdfplumber \
    pyarrow \
    psycopg2-binary \
    fastapi uvicorn \
    streamlit \
    ydata-profiling \
    matplotlib seaborn
```

### Step 3: Verify GPU Access

```bash
python3 << 'PYEOF'
import xgboost as xgb
import numpy as np

# Check CUDA availability
print(f"XGBoost version: {xgb.__version__}")

# Quick GPU training test
X = np.random.randn(1000, 10)
y = (X[:, 0] > 0).astype(int)

dtrain = xgb.DMatrix(X, label=y)
params = {
    'tree_method': 'gpu_hist',
    'objective': 'binary:logistic',
    'eval_metric': 'auc',
    'verbosity': 1,
}

try:
    model = xgb.train(params, dtrain, num_boost_round=10)
    print("GPU training: SUCCESS")
except xgb.core.XGBoostError as e:
    print(f"GPU training failed: {e}")
    print("Falling back to CPU — check CUDA installation")
    params['tree_method'] = 'hist'
    model = xgb.train(params, dtrain, num_boost_round=10)
    print("CPU training: SUCCESS")
PYEOF
```

**Expected output:**

```
XGBoost version: 2.x.x
GPU training: SUCCESS
```

> **Jetson Thor note:** If `gpu_hist` fails, ensure the user is in the `video` and `render` groups (`sudo usermod -aG video,render marginlogic`) and that CUDA 13.0 is on the PATH (`export PATH=/usr/local/cuda/bin:$PATH`).

---

## 5. Part C: PostgreSQL Feature Store Setup

### Step 1: Install PostgreSQL

```bash
# As root/admin user
sudo apt install postgresql postgresql-contrib

# Start and enable
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### Step 2: Create Database and Schemas

```bash
sudo -u postgres psql << 'SQL'
-- Create the marginlogic role and database
CREATE ROLE marginlogic WITH LOGIN PASSWORD 'CHANGE_THIS_TO_STRONG_PASSWORD';
CREATE DATABASE marginlogic OWNER marginlogic;

-- Connect to the new database
\c marginlogic

-- Create schemas
CREATE SCHEMA raw AUTHORIZATION marginlogic;
CREATE SCHEMA features AUTHORIZATION marginlogic;
CREATE SCHEMA predictions AUTHORIZATION marginlogic;

-- Grant permissions
GRANT ALL ON SCHEMA raw, features, predictions TO marginlogic;

-- Enable SSL (verify in postgresql.conf)
ALTER SYSTEM SET ssl = on;
SELECT pg_reload_conf();
SQL
```

### Step 3: Enable SSL for Local Connections

```bash
# Generate self-signed certificate (for local connections only)
sudo -u postgres bash -c '
    cd /var/lib/postgresql/$(pg_lsclusters -h | awk "{print \$1}")/main
    openssl req -new -x509 -days 3650 -nodes \
        -out server.crt -keyout server.key \
        -subj "/CN=marginlogic-jetson"
    chmod 600 server.key
    chown postgres:postgres server.crt server.key
'

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Step 4: Configure pg_hba.conf for Local SSL

```bash
# Edit pg_hba.conf to require SSL for the marginlogic user
sudo bash -c 'cat >> /etc/postgresql/*/main/pg_hba.conf << EOF

# MarginLogic: require SSL for all connections
hostssl marginlogic marginlogic 127.0.0.1/32 scram-sha-256
hostssl marginlogic marginlogic ::1/128 scram-sha-256
EOF'

sudo systemctl restart postgresql
```

### Step 5: Verify Connection

```bash
# As marginlogic user
psql "host=127.0.0.1 dbname=marginlogic user=marginlogic sslmode=require" \
    -c "SELECT current_database(), current_user, ssl_is_used();"
```

**Expected output:**

```
 current_database | current_user | ssl_is_used
------------------+--------------+-------------
 marginlogic      | marginlogic  | t
```

---

## 6. Part D: MLflow Experiment Tracking

### Step 1: Configure MLflow

```bash
# Create MLflow storage directories on encrypted partition
mkdir -p /data/marginlogic/mlflow/artifacts
mkdir -p /data/marginlogic/mlflow/db

# Set environment variables (add to ~/.bashrc)
cat >> /home/marginlogic/.bashrc << 'EOF'

# MLflow configuration
export MLFLOW_TRACKING_URI="sqlite:///data/marginlogic/mlflow/db/mlflow.db"
export MLFLOW_ARTIFACT_ROOT="/data/marginlogic/mlflow/artifacts"
EOF

source /home/marginlogic/.bashrc
```

### Step 2: Start MLflow Server

```bash
mlflow server \
    --host 127.0.0.1 \
    --port 5000 \
    --backend-store-uri "sqlite:///data/marginlogic/mlflow/db/mlflow.db" \
    --default-artifact-root "/data/marginlogic/mlflow/artifacts" &

# Verify
curl -s http://127.0.0.1:5000/api/2.0/mlflow/experiments/search | python3 -m json.tool
```

> **Security note:** MLflow binds to `127.0.0.1` only — not accessible from the network. No PHI is stored in MLflow; only model metrics, hyperparameters, and model artifacts.

---

## 7. Part E: Download and Build the CMS PA Dataset

### Step 1: Clone the Repository

```bash
cd /data/marginlogic/projects
git clone git@github.com:utexas-demo/demo.git
cd demo/experiments/43-cms-prior-auth
```

### Step 2: Download CMS Source Files

```bash
mkdir -p data/raw data/processed
cd data/raw

# DE-SynPUF Sample 1 — Beneficiary Summary (2008)
curl -L -o DE1_0_2008_Beneficiary_Summary_Sample_1.zip \
  "https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_beneficiary_summary_file_sample_1.zip"

# DE-SynPUF Sample 1 — Inpatient Claims (2008-2010)
curl -L -o DE1_0_Inpatient_Claims_Sample_1.zip \
  "https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_inpatient_claims_sample_1.zip"

# DE-SynPUF Sample 1 — Outpatient Claims (2008-2010)
curl -L -o DE1_0_Outpatient_Claims_Sample_1.zip \
  "https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_outpatient_claims_sample_1.zip"

# DE-SynPUF Sample 1 — Carrier Claims 1A (2008-2010)
curl -L -o DE1_0_Carrier_Claims_Sample_1A.zip \
  "http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.zip"

# CMS Required Prior Authorization List (DMEPOS)
curl -L -o PA_Required_List.pdf \
  "https://www.cms.gov/research-statistics-data-and-systems/monitoring-programs/medicare-ffs-compliance-programs/dmepos/downloads/dmepos_pa_required-prior-authorization-list.pdf"

# CMS PA Program Statistics FY24
curl -L -o PA_Stats_FY24.pdf \
  "https://www.cms.gov/files/document/pre-claim-review-program-statistics-document-fy-24.pdf"
```

### Step 3: Extract CSVs

```bash
for f in *.zip; do unzip -o "$f" -d ../; done
cd ../..
```

### Step 4: Build the Labeled Dataset

```bash
source /data/marginlogic/projects/experiment-43/.venv/bin/activate
python3 build_dataset.py
```

**Expected output:**

```
Extracted 115 unique PA-required HCPCS codes
Carrier claims: 2,370,667
Outpatient claims: 790,790
PA required: 22,231 (0.70%)
Final dataset shape: (3161457, 30)
```

### Step 5: Load into PostgreSQL Feature Store

```bash
python3 << 'PYEOF'
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://marginlogic:CHANGE_THIS@127.0.0.1/marginlogic')

# Load training data into feature store
train = pd.read_parquet('data/processed/cms_pa_dataset_train.parquet')
train.to_sql('pa_claims_train', engine, schema='features', if_exists='replace', index=False)

val = pd.read_parquet('data/processed/cms_pa_dataset_val.parquet')
val.to_sql('pa_claims_val', engine, schema='features', if_exists='replace', index=False)

test = pd.read_parquet('data/processed/cms_pa_dataset_test.parquet')
test.to_sql('pa_claims_test', engine, schema='features', if_exists='replace', index=False)

# Load PA codes reference
pa_codes = pd.read_csv('data/processed/pa_required_codes.csv')
pa_codes.to_sql('pa_required_codes', engine, schema='raw', if_exists='replace', index=False)

print("Loaded into PostgreSQL feature store:")
for table in ['features.pa_claims_train', 'features.pa_claims_val',
              'features.pa_claims_test', 'raw.pa_required_codes']:
    schema, name = table.split('.')
    count = pd.read_sql(f"SELECT count(*) FROM {table}", engine).iloc[0, 0]
    print(f"  {table}: {count:,} rows")
PYEOF
```

---

## 8. Part F: FastAPI + Streamlit Serving

### Step 1: Verify Installation

```bash
python3 -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
python3 -c "import streamlit; print(f'Streamlit {streamlit.__version__}')"
```

### Step 2: Test FastAPI Startup

```bash
# Quick test — the full API is built in the Developer Tutorial
uvicorn --version
```

### Step 3: Cloudflare Tunnel (for Pilot Serving to TRA)

When you're ready to serve predictions to TRA during the pilot, use Cloudflare Tunnel instead of opening firewall ports. This provides zero-trust access with no inbound ports.

```bash
# Install cloudflared
curl -L --output cloudflared.deb \
    https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared.deb

# Authenticate (one-time)
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create marginlogic

# Route FastAPI (8000) and Streamlit (8501) through the tunnel
# Configure in ~/.cloudflared/config.yml — see Developer Tutorial
```

---

## 9. Part G: Verification Checklist

Run this checklist after completing all setup steps.

```bash
#!/bin/bash
echo "=== MarginLogic Jetson Thor Verification ==="

echo -n "1. LUKS encryption active:     "
sudo cryptsetup status marginlogic_data > /dev/null 2>&1 && echo "PASS" || echo "FAIL"

echo -n "2. UFW firewall enabled:        "
sudo ufw status | grep -q "Status: active" && echo "PASS" || echo "FAIL"

echo -n "3. auditd running:              "
systemctl is-active auditd > /dev/null 2>&1 && echo "PASS" || echo "FAIL"

echo -n "4. PHI audit rules loaded:      "
sudo auditctl -l | grep -q "phi_data_access" && echo "PASS" || echo "FAIL"

echo -n "5. marginlogic user exists:     "
id marginlogic > /dev/null 2>&1 && echo "PASS" || echo "FAIL"

echo -n "6. marginlogic has no sudo:     "
sudo -l -U marginlogic 2>&1 | grep -q "not allowed" && echo "PASS" || echo "FAIL"

echo -n "7. PostgreSQL running:          "
systemctl is-active postgresql > /dev/null 2>&1 && echo "PASS" || echo "FAIL"

echo -n "8. PostgreSQL SSL enabled:      "
sudo -u marginlogic psql "host=127.0.0.1 dbname=marginlogic user=marginlogic sslmode=require" \
    -tAc "SELECT ssl_is_used();" 2>/dev/null | grep -q "t" && echo "PASS" || echo "FAIL"

echo -n "9. XGBoost GPU available:       "
python3 -c "import xgboost; print('PASS')" 2>/dev/null || echo "FAIL"

echo -n "10. MLflow accessible:          "
curl -s http://127.0.0.1:5000/health > /dev/null 2>&1 && echo "PASS" || echo "RUNNING (start with mlflow server)"

echo -n "11. CMS dataset built:          "
[ -f /data/marginlogic/projects/demo/experiments/43-cms-prior-auth/data/processed/cms_pa_dataset_train.parquet ] && echo "PASS" || echo "FAIL — run build_dataset.py"

echo ""
echo "=== SSH Hardening ==="
echo -n "12. Password auth disabled:     "
sshd -T 2>/dev/null | grep -q "passwordauthentication no" && echo "PASS" || echo "CHECK"

echo -n "13. Root login disabled:        "
sshd -T 2>/dev/null | grep -q "permitrootlogin no" && echo "PASS" || echo "CHECK"
```

---

## 10. Troubleshooting

### LUKS: "No key available with this passphrase"

- You may have mistyped the passphrase. LUKS is case-sensitive and whitespace-sensitive.
- Add a backup key slot: `sudo cryptsetup luksAddKey /dev/nvme0n1p3`

### XGBoost: "CUDA error: no CUDA-capable device is detected"

```bash
# Check CUDA is accessible
nvcc --version
nvidia-smi

# Ensure marginlogic user is in video/render groups
groups marginlogic
# Should include: video render

# If groups were just added, log out and back in
```

### PostgreSQL: Connection refused

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check if it's listening on 127.0.0.1
sudo ss -tlnp | grep 5432

# Check pg_hba.conf for correct entries
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep marginlogic
```

### auditd: Rules not loading

```bash
# Check for syntax errors
sudo augenrules --check

# View audit daemon status
sudo systemctl status auditd

# Check if immutable flag is set (blocks rule changes until reboot)
sudo auditctl -s | grep enabled
# "enabled 2" means immutable — reboot required to change rules
```

---

## 11. Reference Commands

```bash
# View audit log for PHI access
sudo ausearch -k phi_data_access -ts today

# Rotate audit logs
sudo service auditd rotate

# Check disk encryption status
sudo cryptsetup status marginlogic_data

# Check firewall rules
sudo ufw status numbered

# PostgreSQL maintenance
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('marginlogic'));"

# MLflow — list experiments
curl -s http://127.0.0.1:5000/api/2.0/mlflow/experiments/search | python3 -m json.tool

# GPU memory usage
nvidia-smi

# System resource monitoring during training
htop     # CPU/memory
nvtop    # GPU utilization (install: sudo apt install nvtop)
```
