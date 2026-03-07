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

**Verify Step 1:**

```bash
# 1a. Confirm LUKS volume is active
sudo cryptsetup status marginlogic_data
# Expected: type: LUKS2, cipher: aes-xts-plain64, keysize: 512 bits

# 1b. Confirm the encrypted partition is mounted
mount | grep marginlogic_data
# Expected: /dev/mapper/marginlogic_data on /data/marginlogic type ext4 (rw,relatime)

# 1c. Confirm data is writable on the encrypted partition
touch /data/marginlogic/test_luks && rm /data/marginlogic/test_luks && echo "PASS: writable" || echo "FAIL"

# 1d. Confirm crypttab entry exists (for auto-mount on boot)
grep marginlogic_data /etc/crypttab && echo "PASS: crypttab configured" || echo "FAIL: missing crypttab entry"

# 1e. Confirm fstab entry exists
grep marginlogic_data /etc/fstab && echo "PASS: fstab configured" || echo "FAIL: missing fstab entry"
```

> **All 5 checks must pass before proceeding.**

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

**Verify Step 2:**

```bash
# 2a. Confirm user exists with correct shell and home
id marginlogic
# Expected: uid=XXXX(marginlogic) gid=XXXX(marginlogic) groups=XXXX(marginlogic),video,render

# 2b. Confirm user has NO sudo privileges
sudo -l -U marginlogic 2>&1 | grep -q "not allowed" && echo "PASS: no sudo" || echo "FAIL: user has sudo access — remove from sudo group"

# 2c. Confirm home directory exists
[ -d /home/marginlogic ] && echo "PASS: home dir exists" || echo "FAIL"

# 2d. Confirm user owns the encrypted data directory
stat -c '%U:%G' /data/marginlogic
# Expected: marginlogic:marginlogic

# 2e. Confirm GPU group membership
groups marginlogic | grep -q "video" && groups marginlogic | grep -q "render" && echo "PASS: GPU groups" || echo "FAIL: missing video/render groups"
```

> **All 5 checks must pass before proceeding.**

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

**Verify Step 3:**

```bash
# 3a. Confirm UFW is active
sudo ufw status | head -1
# Expected: Status: active

# 3b. Confirm default deny incoming
sudo ufw status verbose | grep -q "deny (incoming)" && echo "PASS: deny incoming" || echo "FAIL"

# 3c. Confirm only SSH is allowed (and only from your IP)
RULE_COUNT=$(sudo ufw status numbered | grep -c "ALLOW IN")
[ "$RULE_COUNT" -eq 1 ] && echo "PASS: exactly 1 inbound rule" || echo "WARNING: $RULE_COUNT inbound rules — review with: sudo ufw status numbered"

# 3d. Confirm no dangerous ports are open (8000, 8501, 5432, 5000)
for port in 8000 8501 5432 5000; do
    sudo ufw status | grep -q "$port.*ALLOW" && echo "FAIL: port $port is open — should be blocked" || echo "PASS: port $port blocked"
done

# 3e. Confirm UFW is enabled on boot
sudo systemctl is-enabled ufw && echo "PASS: UFW enabled on boot" || echo "FAIL: enable with: sudo systemctl enable ufw"
```

> **All 5 checks must pass before proceeding.**

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

**Verify Step 4:**

```bash
# 4a. Confirm auditd is running
systemctl is-active auditd && echo "PASS: auditd active" || echo "FAIL: start with: sudo systemctl start auditd"

# 4b. Confirm auditd is enabled on boot
systemctl is-enabled auditd && echo "PASS: auditd enabled on boot" || echo "FAIL"

# 4c. Confirm all 6 audit rule keys are loaded
for key in phi_data_access postgres_data_access user_accounts auth_log ssh_config cron_changes; do
    sudo auditctl -l | grep -q "$key" && echo "PASS: rule '$key' loaded" || echo "FAIL: rule '$key' missing"
done

# 4d. Confirm the rules file exists on disk (survives reboot)
[ -f /etc/audit/rules.d/marginlogic.rules ] && echo "PASS: rules file exists" || echo "FAIL: rules file missing"

# 4e. End-to-end audit trail test
sudo -u marginlogic touch /data/marginlogic/audit_verify_test
sleep 1
sudo ausearch -k phi_data_access -ts recent | grep -q "audit_verify_test" && echo "PASS: audit trail working" || echo "FAIL: audit event not captured"
sudo -u marginlogic rm /data/marginlogic/audit_verify_test
```

> **All checks must pass before proceeding. Pay special attention to 4c — all 6 rules must be loaded.**

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

**Verify Step 5:**

```bash
# 5a. Confirm each service is disabled (some may not exist on your system — that's OK)
for svc in cups avahi-daemon bluetooth ModemManager whoopsie; do
    STATUS=$(systemctl is-active $svc 2>/dev/null)
    if [ "$STATUS" = "inactive" ] || [ "$STATUS" = "" ]; then
        echo "PASS: $svc is stopped"
    else
        echo "FAIL: $svc is still running — disable with: sudo systemctl disable --now $svc"
    fi
done

# 5b. Confirm headless mode (no GUI)
BOOT_TARGET=$(systemctl get-default)
[ "$BOOT_TARGET" = "multi-user.target" ] && echo "PASS: headless mode (multi-user.target)" || echo "WARNING: boot target is $BOOT_TARGET — run: sudo systemctl set-default multi-user.target"

# 5c. Count total running services (should be minimal)
RUNNING=$(systemctl list-units --type=service --state=running --no-pager | grep -c "running")
echo "INFO: $RUNNING services running — review if >20: sudo systemctl list-units --type=service --state=running"
```

> **5a and 5b must pass. Review 5c if the count seems high.**

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

**Verify Step 6:**

```bash
# 6a. Confirm password authentication is disabled
sudo sshd -T 2>/dev/null | grep -i "passwordauthentication" | grep -q "no" && echo "PASS: password auth disabled" || echo "FAIL: password auth still enabled"

# 6b. Confirm root login is disabled
sudo sshd -T 2>/dev/null | grep -i "permitrootlogin" | grep -q "no" && echo "PASS: root login disabled" || echo "FAIL: root login still allowed"

# 6c. Confirm X11 forwarding is disabled
sudo sshd -T 2>/dev/null | grep -i "x11forwarding" | grep -q "no" && echo "PASS: X11 forwarding disabled" || echo "FAIL"

# 6d. Confirm idle timeout is configured (ClientAliveInterval should be 300)
ALIVE=$(sudo sshd -T 2>/dev/null | grep -i "clientaliveinterval" | awk '{print $2}')
[ "$ALIVE" = "300" ] && echo "PASS: idle timeout 300s" || echo "WARNING: ClientAliveInterval is $ALIVE (expected 300)"

# 6e. Confirm the config drop-in file exists
[ -f /etc/ssh/sshd_config.d/marginlogic.conf ] && echo "PASS: SSH config file exists" || echo "FAIL: config file missing"

# 6f. Test SSH key login works (run from your workstation, not the Jetson)
echo "MANUAL CHECK: From your workstation, run: ssh marginlogic@<JETSON_IP> 'echo SSH_KEY_LOGIN_OK'"
echo "              Confirm it connects without asking for a password."
```

> **Checks 6a-6e must pass. Complete 6f manually from your workstation before proceeding.**

### Step 7: Automatic Security Updates

```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
# Select "Yes" to enable automatic security updates
```

**Verify Step 7:**

```bash
# 7a. Confirm unattended-upgrades is installed
dpkg -l | grep -q unattended-upgrades && echo "PASS: unattended-upgrades installed" || echo "FAIL: install with: sudo apt install unattended-upgrades"

# 7b. Confirm auto-updates are enabled
grep -r "Unattended-Upgrade" /etc/apt/apt.conf.d/20auto-upgrades 2>/dev/null | grep -q '"1"' && echo "PASS: auto-updates enabled" || echo "FAIL: run: sudo dpkg-reconfigure -plow unattended-upgrades"

# 7c. Confirm the unattended-upgrades service is active
systemctl is-active unattended-upgrades && echo "PASS: service active" || echo "WARNING: service not active"

# 7d. Dry-run to confirm it can find updates
sudo unattended-upgrades --dry-run --debug 2>&1 | head -5
echo "INFO: Review output above — should show 'Allowed origins' with security updates listed"
```

> **Checks 7a-7c must pass. Review 7d output for sanity.**

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

**Verify Step 1:**

```bash
# B1a. Confirm venv is active (prompt should show (.venv))
which python3
# Expected: /data/marginlogic/projects/experiment-43/.venv/bin/python3

# B1b. Confirm Python version
python3 --version
# Expected: Python 3.10+ (JetPack 7.0 ships 3.10 or 3.11)

# B1c. Confirm pip is upgraded
pip --version
# Should show pip 24.x+ from the .venv path

# B1d. Confirm project directory is on encrypted partition
df /data/marginlogic/projects/experiment-43 | grep -q "marginlogic_data" && echo "PASS: on encrypted partition" || echo "WARNING: not on LUKS partition — check mount"
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

**Verify Step 2:**

```bash
# B2a. Confirm all critical packages are importable
python3 << 'PYEOF'
import sys
packages = [
    ("pandas", "pandas"), ("numpy", "numpy"), ("scipy", "scipy"),
    ("sklearn", "scikit-learn"), ("xgboost", "xgboost"), ("lightgbm", "lightgbm"),
    ("shap", "shap"), ("optuna", "optuna"), ("mlflow", "mlflow"),
    ("pdfplumber", "pdfplumber"), ("pyarrow", "pyarrow"),
    ("psycopg2", "psycopg2-binary"), ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"), ("streamlit", "streamlit"),
]
failed = []
for mod, pkg in packages:
    try:
        __import__(mod)
    except ImportError:
        failed.append(pkg)
if failed:
    print(f"FAIL: Missing packages: {', '.join(failed)}")
    print(f"  Fix: pip install {' '.join(failed)}")
    sys.exit(1)
else:
    print(f"PASS: All {len(packages)} packages installed")
PYEOF
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

**Verify Step 3:**

```bash
# B3a. Confirm CUDA toolkit is accessible
nvcc --version
# Expected: Cuda compilation tools, release 13.0

# B3b. Confirm GPU is visible
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
# Expected: NVIDIA Jetson AGX Thor, XXXXX MiB

# B3c. Confirm the XGBoost GPU test above printed "GPU training: SUCCESS"
# If it printed "CPU training: SUCCESS" instead, fix the CUDA setup before proceeding

# B3d. Quick LightGBM GPU check
python3 -c "
import lightgbm as lgb
print(f'LightGBM {lgb.__version__}')
print('GPU device:', 'available' if lgb.LGBMClassifier(device='gpu') else 'not found')
print('PASS')
" 2>/dev/null && echo "" || echo "WARNING: LightGBM GPU may need manual build — see Troubleshooting"
```

> **B3a-B3c must pass. B3d is informational — LightGBM GPU is optional.**

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

**Verify Step 1:**

```bash
# C1a. Confirm PostgreSQL is running
systemctl is-active postgresql && echo "PASS: PostgreSQL running" || echo "FAIL"

# C1b. Confirm PostgreSQL is enabled on boot
systemctl is-enabled postgresql && echo "PASS: PostgreSQL enabled on boot" || echo "FAIL"

# C1c. Confirm PostgreSQL version
sudo -u postgres psql -c "SELECT version();" | head -3
# Expected: PostgreSQL 14.x or 15.x
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

**Verify Step 2:**

```bash
# C2a. Confirm database exists
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname='marginlogic';" | grep -q "marginlogic" && echo "PASS: database exists" || echo "FAIL"

# C2b. Confirm role exists
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname='marginlogic';" | grep -q "marginlogic" && echo "PASS: role exists" || echo "FAIL"

# C2c. Confirm all 3 schemas exist
for schema in raw features predictions; do
    sudo -u postgres psql -d marginlogic -tAc "SELECT schema_name FROM information_schema.schemata WHERE schema_name='$schema';" | grep -q "$schema" && echo "PASS: schema '$schema' exists" || echo "FAIL: schema '$schema' missing"
done

# C2d. Confirm SSL is set to 'on'
sudo -u postgres psql -tAc "SHOW ssl;" | grep -q "on" && echo "PASS: SSL enabled" || echo "FAIL: SSL not enabled"
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

**Verify Step 3:**

```bash
# C3a. Confirm certificate files exist with correct permissions
sudo -u postgres ls -la /var/lib/postgresql/*/main/server.{crt,key}
# Expected: server.key should be -rw------- (600), owned by postgres:postgres

# C3b. Confirm PostgreSQL loaded the certificate
sudo -u postgres psql -tAc "SHOW ssl_cert_file;"
# Expected: a path to server.crt (or 'server.crt' if relative)
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

**Verify Step 4:**

```bash
# C4a. Confirm pg_hba.conf has the SSL-required entries
sudo grep "hostssl.*marginlogic" /etc/postgresql/*/main/pg_hba.conf
# Expected: two lines — one for 127.0.0.1/32, one for ::1/128

# C4b. Confirm PostgreSQL restarted cleanly after config change
systemctl is-active postgresql && echo "PASS: PostgreSQL running after config change" || echo "FAIL: PostgreSQL failed to restart — check: sudo journalctl -u postgresql"
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

**If `ssl_is_used` shows `t`, PostgreSQL is fully configured. If it shows `f` or the connection fails, review Steps 3-4.**

> **All Part C checks must pass. The final connection test (Step 5) is the definitive verification that database, role, schemas, SSL certificates, and pg_hba.conf are all correctly configured.**

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

**Verify Step 1:**

```bash
# D1a. Confirm directories exist on encrypted partition
[ -d /data/marginlogic/mlflow/artifacts ] && [ -d /data/marginlogic/mlflow/db ] && echo "PASS: MLflow dirs exist" || echo "FAIL"

# D1b. Confirm environment variables are set
echo "MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI"
echo "MLFLOW_ARTIFACT_ROOT=$MLFLOW_ARTIFACT_ROOT"
# Both should point to /data/marginlogic/mlflow/...

# D1c. Confirm variables are persisted in .bashrc
grep -q "MLFLOW_TRACKING_URI" /home/marginlogic/.bashrc && echo "PASS: .bashrc configured" || echo "FAIL: env vars not in .bashrc"
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

**Verify Step 2:**

```bash
# D2a. Confirm MLflow server is responding
curl -s http://127.0.0.1:5000/api/2.0/mlflow/experiments/search > /dev/null && echo "PASS: MLflow API responding" || echo "FAIL: MLflow not running — check process"

# D2b. Confirm MLflow is only listening on localhost (not exposed to network)
ss -tlnp | grep 5000 | grep -q "127.0.0.1" && echo "PASS: MLflow bound to localhost only" || echo "FAIL: MLflow may be exposed — check binding"

# D2c. Confirm the SQLite database was created
[ -f /data/marginlogic/mlflow/db/mlflow.db ] && echo "PASS: MLflow database created" || echo "FAIL: database not found"
```

> **Security note:** MLflow binds to `127.0.0.1` only — not accessible from the network. No PHI is stored in MLflow; only model metrics, hyperparameters, and model artifacts.

> **All D2 checks must pass before proceeding.**

---

## 7. Part E: Download and Build the CMS PA Dataset

### Step 1: Clone the Repository

```bash
cd /data/marginlogic/projects
git clone git@github.com:utexas-demo/demo.git
cd demo/experiments/43-cms-prior-auth
```

**Verify Step 1:**

```bash
# E1a. Confirm repo was cloned successfully
[ -f /data/marginlogic/projects/demo/experiments/43-cms-prior-auth/build_dataset.py ] && echo "PASS: repo cloned" || echo "FAIL: build_dataset.py not found"

# E1b. Confirm we're in the right directory
pwd
# Expected: /data/marginlogic/projects/demo/experiments/43-cms-prior-auth
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

**Verify Step 2:**

```bash
# E2a. Confirm all 6 files were downloaded
EXPECTED_FILES=("DE1_0_2008_Beneficiary_Summary_Sample_1.zip" "DE1_0_Inpatient_Claims_Sample_1.zip" "DE1_0_Outpatient_Claims_Sample_1.zip" "DE1_0_Carrier_Claims_Sample_1A.zip" "PA_Required_List.pdf" "PA_Stats_FY24.pdf")
for f in "${EXPECTED_FILES[@]}"; do
    [ -f "data/raw/$f" ] && echo "PASS: $f downloaded" || echo "FAIL: $f missing"
done

# E2b. Confirm files are not empty (minimum 1KB)
for f in data/raw/*.zip data/raw/*.pdf; do
    SIZE=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null)
    [ "$SIZE" -gt 1024 ] && echo "PASS: $(basename $f) is ${SIZE} bytes" || echo "FAIL: $(basename $f) is too small (${SIZE} bytes) — re-download"
done
```

### Step 3: Extract CSVs

```bash
for f in *.zip; do unzip -o "$f" -d ../; done
cd ../..
```

**Verify Step 3:**

```bash
# E3a. Confirm CSV files were extracted
CSV_COUNT=$(ls data/*.csv 2>/dev/null | wc -l)
[ "$CSV_COUNT" -ge 4 ] && echo "PASS: $CSV_COUNT CSV files extracted" || echo "FAIL: expected 4+ CSVs, found $CSV_COUNT"

# E3b. Confirm key CSV files exist and have data (check header + at least 1 data line)
for csv in data/DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv data/DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.csv data/DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.csv data/DE1_0_2008_to_2010_Inpatient_Claims_Sample_1.csv; do
    if [ -f "$csv" ]; then
        LINES=$(wc -l < "$csv")
        echo "PASS: $(basename $csv) — $LINES lines"
    else
        echo "FAIL: $(basename $csv) not found"
    fi
done
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

**Verify Step 4:**

```bash
# E4a. Confirm output Parquet files were created
for split in train val test; do
    FILE="data/processed/cms_pa_dataset_${split}.parquet"
    [ -f "$FILE" ] && echo "PASS: $FILE exists ($(du -h "$FILE" | cut -f1))" || echo "FAIL: $FILE missing"
done

# E4b. Confirm PA codes CSV was created
[ -f data/processed/pa_required_codes.csv ] && echo "PASS: PA codes CSV exists" || echo "FAIL"

# E4c. Confirm dataset statistics match expectations
python3 << 'PYEOF'
import pandas as pd
train = pd.read_parquet('data/processed/cms_pa_dataset_train.parquet')
val = pd.read_parquet('data/processed/cms_pa_dataset_val.parquet')
test = pd.read_parquet('data/processed/cms_pa_dataset_test.parquet')
total = len(train) + len(val) + len(test)
pa_total = train['pa_required'].sum() + val['pa_required'].sum() + test['pa_required'].sum()
pa_pct = pa_total / total * 100
print(f"Total claims: {total:,} (expected ~3.16M)")
print(f"PA required: {pa_total:,} ({pa_pct:.2f}%) (expected ~22K, ~0.70%)")
print(f"Features: {train.shape[1]} (expected 30)")
if total > 3_000_000 and pa_total > 20_000 and train.shape[1] == 30:
    print("PASS: Dataset statistics match expectations")
else:
    print("WARNING: Statistics differ from expected — review build_dataset.py output")
PYEOF
```

> **All E4 checks must pass before loading into PostgreSQL.**

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

**Verify Step 5:**

```bash
# E5a. Confirm all 4 tables exist with correct row counts
python3 << 'PYEOF'
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://marginlogic:CHANGE_THIS@127.0.0.1/marginlogic')
tables = {
    'features.pa_claims_train': 2_200_000,   # ~70% of 3.16M
    'features.pa_claims_val': 470_000,        # ~15%
    'features.pa_claims_test': 470_000,       # ~15%
    'raw.pa_required_codes': 100,             # ~115 codes
}
all_pass = True
for table, min_rows in tables.items():
    count = pd.read_sql(f"SELECT count(*) FROM {table}", engine).iloc[0, 0]
    if count >= min_rows:
        print(f"PASS: {table} — {count:,} rows")
    else:
        print(f"FAIL: {table} — {count:,} rows (expected >= {min_rows:,})")
        all_pass = False
if all_pass:
    print("\nPASS: All tables loaded correctly")
else:
    print("\nFAIL: Some tables have fewer rows than expected — re-run Step 5")
PYEOF

# E5b. Confirm SSL is used for the connection
psql "host=127.0.0.1 dbname=marginlogic user=marginlogic sslmode=require" \
    -tAc "SELECT ssl_is_used();" | grep -q "t" && echo "PASS: PostgreSQL connection uses SSL" || echo "FAIL: SSL not active"
```

> **All Part E checks must pass. The dataset is now ready for training.**

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

**Verify Steps 1-2:**

```bash
# F1a. Confirm FastAPI version
python3 -c "import fastapi; print(f'PASS: FastAPI {fastapi.__version__}')" || echo "FAIL: FastAPI not installed"

# F1b. Confirm Streamlit version
python3 -c "import streamlit; print(f'PASS: Streamlit {streamlit.__version__}')" || echo "FAIL: Streamlit not installed"

# F1c. Confirm uvicorn is available
uvicorn --version && echo "PASS" || echo "FAIL: uvicorn not installed"

# F1d. Quick FastAPI startup test (start, verify, stop)
python3 << 'PYEOF' &
from fastapi import FastAPI
import uvicorn
app = FastAPI()
@app.get("/health")
def health(): return {"status": "ok"}
uvicorn.run(app, host="127.0.0.1", port=8199, log_level="error")
PYEOF
sleep 2
curl -s http://127.0.0.1:8199/health | grep -q "ok" && echo "PASS: FastAPI serves requests" || echo "FAIL: FastAPI did not respond"
kill %1 2>/dev/null
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

**Verify Step 3:**

```bash
# F3a. Confirm cloudflared is installed
cloudflared version && echo "PASS: cloudflared installed" || echo "FAIL: cloudflared not installed"

# F3b. Confirm tunnel was created
cloudflared tunnel list | grep -q "marginlogic" && echo "PASS: tunnel 'marginlogic' exists" || echo "FAIL: tunnel not created — run: cloudflared tunnel create marginlogic"

# F3c. Confirm tunnel credentials file exists
[ -f ~/.cloudflared/*.json ] && echo "PASS: tunnel credentials found" || echo "FAIL: no credentials — run: cloudflared tunnel login"

# F3d. Confirm no inbound ports are open for web traffic (tunnels are outbound-only)
sudo ufw status | grep -E "8000|8501" | grep "ALLOW" && echo "FAIL: web ports open in firewall — Cloudflare Tunnel makes this unnecessary" || echo "PASS: no inbound web ports (tunnel handles this)"
```

> **F3a-F3b must pass. F3d confirms the zero-trust architecture is maintained.**

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
