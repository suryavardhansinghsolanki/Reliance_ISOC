#!/usr/bin/env python3
# =====================================================================
#  JIO ISOC Dashboard v6.4 — PRODUCTION BUILD  [SINGLE FILE EDITION]
#  Air-gapped · Citrix · ISOC NOC Desktop · PuTTY / Jump Server
# =====================================================================
#
#  HOW TO RUN  (one command, that's it):
#       python ISOC_v6_prod_single.py
#
#  On first run this file will:
#    1. Install missing Python packages (auto, or from ./wheels/ offline)
#    2. Create  .streamlit/secrets.toml  — fill in your credentials
#    3. Create  .streamlit/config.toml   — server settings
#    4. Relaunch itself via Streamlit
#
#  Subsequent runs: just  python ISOC_v6_prod_single.py  again.
#
#  PuTTY / Jump Server access:
#    ssh -L 8501:localhost:8501 <user>@<jump_server_ip>
#    Then open: http://localhost:8501 in your browser.
#
#  Port override:   set ISOC_PORT=8080  (Windows)
#                   export ISOC_PORT=8080  (Linux)
#
#  PRODUCTION DATA SOURCES (all internal, no internet):
#    DNS    : JIO internal nameservers only
#    PING   : ICMP raw socket / TCP fallback
#    TRACE  : ICMP TTL-decrement + TCP probe
#    BGP    : IBR SSH (paramiko) — parsed from Cisco / JunOS CLI
#    ASN    : IBR SSH + embedded local ASN DB
# =====================================================================

# ══════════════════════════════════════════════════════════════════════
#  PART 1 — SELF-BOOTSTRAP
#  Uses stdlib only. Runs ONLY when executed directly via python.
#  When Streamlit re-runs the file internally, this block is skipped.
# ══════════════════════════════════════════════════════════════════════
import sys, os, subprocess

# ── Embedded .streamlit/secrets.toml template ─────────────────────────
_SECRETS_TEMPLATE = """\
# =====================================================================
#  JIO ISOC Dashboard v6.4 — PRODUCTION CREDENTIALS
#  Fill in ALL values before running the dashboard.
#  NEVER commit this file to version control.
#  Linux: chmod 600 .streamlit/secrets.toml
# =====================================================================

# Dashboard Web Login
ISOC_LOGIN_USER = "isoc_operator"
ISOC_LOGIN_PASS = "CHANGE_ME_STRONG_PASSWORD"

# Jump Server (Citrix / NOC Desktop -> Jump Server via SSH)
JUMP_SERVER_IP  = "10.x.x.x"
JUMP_USER       = "admin"
JUMP_PASS       = "CHANGE_ME"
SSH_PORT        = "22"

# IBR / Internal Border Router
IBR_IP          = "10.x.x.x"
IBR_USER        = "netadmin"
IBR_PASS        = "CHANGE_ME"
"""

# ── Embedded .streamlit/config.toml ───────────────────────────────────
_CONFIG_TEMPLATE = """\
[server]
port                     = 8501
address                  = "127.0.0.1"
headless                 = true
fileWatcherType          = "none"
maxUploadSize            = 10
enableCORS               = false
enableXsrfProtection     = true

[browser]
gatherUsageStats         = false
serverAddress            = "localhost"
serverPort               = 8501

[theme]
base                     = "light"
primaryColor             = "#0B58C6"
backgroundColor          = "#f8fafc"
secondaryBackgroundColor = "#ffffff"
textColor                = "#0f172a"
font                     = "sans serif"

[logger]
level                    = "warning"

[runner]
magicEnabled             = false
fastReruns               = true
"""

def _in_streamlit() -> bool:
    """Return True only when running inside a live Streamlit server context."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False

def _bootstrap():
    """Install dependencies, write config files, relaunch via Streamlit."""
    script  = os.path.abspath(__file__)
    app_dir = os.path.dirname(script)

    print("\n" + "=" * 57)
    print("   JIO ISOC Dashboard v6.4  |  PRODUCTION BUILD")
    print("   Self-Bootstrap - Single File Edition")
    print("=" * 57 + "\n")

    # ── 1. Check / install dependencies ──────────────────────────────
    print("  [*] Checking Python dependencies...")
    _checks = {
        "streamlit": "streamlit",
        "plotly":    "plotly",
        "dnspython": "dns",
        "paramiko":  "paramiko",
        "openpyxl":  "openpyxl",
    }
    missing = []
    for pkg, imp in _checks.items():
        try:
            __import__(imp)
        except ImportError:
            missing.append(pkg)

    if missing:
        wheels_dir = os.path.join(app_dir, "wheels")
        print(f"  [*] Installing: {', '.join(missing)}")
        cmd = [sys.executable, "-m", "pip", "install"] + missing
        if os.path.isdir(wheels_dir):
            cmd += ["--no-index", f"--find-links={wheels_dir}"]
            print(f"  [*] Using offline wheels from: {wheels_dir}")
        cmd += ["--quiet"]
        try:
            subprocess.check_call(cmd)
            print("  [OK] Packages installed.\n")
        except subprocess.CalledProcessError as e:
            print(f"\n  [FAIL] Install failed: {e}")
            print("  [!] Air-gapped env? Pre-download wheels on an internet machine:")
            print(f"      pip download {' '.join(missing)} -d ./wheels/")
            print("  Then copy the wheels/ folder here and re-run.\n")
            input("  Press ENTER to retry after manual install, or Ctrl+C to exit... ")
    else:
        print("  [OK] All dependencies satisfied.\n")

    # ── 2. Create .streamlit/ directory and files ─────────────────────
    st_dir = os.path.join(app_dir, ".streamlit")
    os.makedirs(st_dir, exist_ok=True)

    secrets_path = os.path.join(st_dir, "secrets.toml")
    first_run = not os.path.exists(secrets_path)
    if first_run:
        with open(secrets_path, "w") as f:
            f.write(_SECRETS_TEMPLATE)
        print(f"  [!] Created credentials file: {secrets_path}")
        print("  [!] IMPORTANT: Fill in your credentials before continuing.")
        print("      Replace all CHANGE_ME / 10.x.x.x values.\n")
        if sys.platform == "win32":
            print(f"  Opening Notepad: {secrets_path}")
            try:
                subprocess.Popen(["notepad.exe", secrets_path])
            except Exception:
                pass
        else:
            print(f"  Edit now:  nano \"{secrets_path}\"")
        input("\n  Press ENTER after saving credentials to launch the dashboard... \n")
    else:
        print(f"  [OK] Credentials file found: {secrets_path}\n")

    config_path = os.path.join(st_dir, "config.toml")
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write(_CONFIG_TEMPLATE)
        print(f"  [OK] Created server config: {config_path}\n")

    # ── 3. Protect secrets file on Linux ─────────────────────────────
    if sys.platform != "win32":
        try:
            os.chmod(secrets_path, 0o600)
        except Exception:
            pass

    # ── 4. Launch Streamlit ───────────────────────────────────────────
    port = str(os.environ.get("ISOC_PORT", "8501"))
    print("  " + "-" * 53)
    print(f"  [*] Launching JIO ISOC Dashboard ...")
    print(f"      URL : http://localhost:{port}")
    if sys.platform != "win32":
        print(f"      PuTTY tunnel: ssh -L {port}:localhost:{port} <user>@<jump_server>")
    print("  [!] Keep this window open while the dashboard is running.")
    print("  [!] Press Ctrl+C to stop.")
    print("  " + "-" * 53 + "\n")

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", script,
            f"--server.port={port}",
            "--server.address=127.0.0.1",
            "--server.headless=false",
            "--browser.gatherUsageStats=false",
            "--server.fileWatcherType=none",
            "--theme.base=light",
        ])
    except KeyboardInterrupt:
        print("\n  [*] Dashboard stopped. Goodbye.")

# ── Bootstrap gate — exit here if not inside Streamlit ───────────────
if not _in_streamlit():
    _bootstrap()
    sys.exit(0)

# ══════════════════════════════════════════════════════════════════════
#  PART 2 — STREAMLIT APPLICATION
#  Everything below runs only inside the Streamlit server context
#  (i.e. after this file is relaunched via 'streamlit run' by Part 1).
# ══════════════════════════════════════════════════════════════════════
# ── std library ───────────────────────────────────────────────────────
import streamlit as st
import socket, json, csv, io, re, math, struct, time, random
import subprocess, platform, threading, os, functools
import concurrent.futures
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
# urllib.request removed — no outbound HTTP in production

# ── third-party ───────────────────────────────────────────────────────
try:
    import dns.resolver
    import dns.rdatatype
    import dns.exception
    HAS_DNSPY = True
except ImportError:
    HAS_DNSPY = False

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False

import streamlit.components.v1 as components
import plotly.graph_objects as go

# ══════════════════════════════════════════════════════════════════════
#  PRODUCTION CREDENTIAL LOADING
#  Priority: st.secrets → environment variable → safe default
# ══════════════════════════════════════════════════════════════════════
def _secret(key: str, env_key: str, default: str) -> str:
    """Load a secret: secrets.toml first, then env var, then default."""
    try:
        val = st.secrets.get(key)
        if val:
            return str(val)
    except Exception:
        pass
    return os.getenv(env_key, default)

LOGIN_USERNAME   = _secret("ISOC_LOGIN_USER",  "ISOC_LOGIN_USER",  "admin")
LOGIN_PASSWORD   = _secret("ISOC_LOGIN_PASS",  "ISOC_LOGIN_PASS",  "changeme")
JUMP_SERVER_IP   = _secret("JUMP_SERVER_IP",   "JUMP_SERVER_IP",   "192.168.1.10")
JUMP_SERVER_USER = _secret("JUMP_USER",        "JUMP_USER",        "admin")
JUMP_SERVER_PASS = _secret("JUMP_PASS",        "JUMP_PASS",        "")
IBR_IP           = _secret("IBR_IP",           "IBR_IP",           "192.168.1.20")
IBR_USER         = _secret("IBR_USER",         "IBR_USER",         "netadmin")
IBR_PASS         = _secret("IBR_PASS",         "IBR_PASS",         "")
SSH_PORT         = int(_secret("SSH_PORT",     "SSH_PORT",         "22"))
SSH_TIMEOUT      = 5   # seconds — tune per network RTT to infra

# ══════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="JIO ISOC Dashboard v6.4",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════════
#  FLOATING PIPELINE WIDGET INJECTOR  (unchanged from dev build)
# ══════════════════════════════════════════════════════════════════════
_widget_injector = """
<script>
    const doc = window.parent.document;
    if (!doc.getElementById('jio-widget-container')) {
        const widgetHtml = `
        <div id="jio-widget-container" style="position:fixed; top:25%; right:0; z-index:999999; font-family:sans-serif; display:none; align-items:flex-start; transition: transform 0.3s ease;">
            <div id="jio-widget-fab" style="padding:20px 10px; background:linear-gradient(135deg, #4f46e5, #8b5cf6); cursor:pointer; display:flex; align-items:center; justify-content:center; color:white; border-radius: 8px 0 0 8px; box-shadow:-4px 0 15px rgba(0,0,0,0.1); writing-mode: vertical-rl; font-weight: 800; letter-spacing: 2px; font-size:0.85rem; user-select:none;">
                PIPELINE
            </div>
            <div id="jio-widget-panel" style="display:none; width:340px; background:#fff; border-radius:0 0 0 12px; box-shadow:-8px 0 30px rgba(0,0,0,0.15); border:1px solid #e2e8f0; border-right:none; overflow:hidden;">
                <div id="jio-widget-header" style="background:linear-gradient(135deg, #4f46e5, #8b5cf6); padding:14px 18px; color:white; font-size:0.9rem; font-weight:bold; display:flex; justify-content:space-between; align-items:center; user-select:none;">
                    <span style="letter-spacing:0.5px;">◈ PIPELINE STATUS</span>
                </div>
                <div id="jio-widget-content" style="padding:16px; max-height:65vh; overflow-y:auto; background:#f8fafc;">
                    <div style="text-align:center; padding:20px; color:#64748b; font-size:0.85rem;">Waiting for triage data...</div>
                </div>
            </div>
        </div>
        `;
        doc.body.insertAdjacentHTML('beforeend', widgetHtml);

        const container = doc.getElementById('jio-widget-container');
        const fab = doc.getElementById('jio-widget-fab');
        const panel = doc.getElementById('jio-widget-panel');

        fab.addEventListener('click', function(e) {
            e.stopPropagation();
            panel.style.display = (panel.style.display === 'none' || panel.style.display === '') ? 'block' : 'none';
        });

        doc.addEventListener('click', function(e) {
            if (!container.contains(e.target)) {
                panel.style.display = 'none';
            }
        });

        const observer = new MutationObserver(function() {
            const src = doc.getElementById('live-pipeline-sync-source');
            if(src) {
                const target = doc.getElementById('jio-widget-content');
                if(target && target.innerHTML !== src.innerHTML) {
                    target.innerHTML = src.innerHTML;
                    container.style.display = 'flex';
                }
            }
        });
        observer.observe(doc.body, { childList: true, subtree: true });
    }
</script>
"""
components.html(_widget_injector, height=0, width=0)

# ══════════════════════════════════════════════════════════════════════
#  LOGIN GATE
# ══════════════════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("""
    <style>
    .stApp { background-color: #f8fafc !important; }
    [data-testid="stHeader"] { background: transparent; }
    footer { visibility: hidden; }
    div[data-testid="stVerticalBlock"] > div:has(.brand-wrap) {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-top: 4px solid #e31837 !important;
        border-radius: 16px !important;
        padding: 3rem 2.5rem !important;
        box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.05),
                    0 8px 10px -6px rgba(15, 23, 42, 0.05) !important;
    }
    div.stTextInput input {
        border-radius: 8px !important; border: 1px solid #cbd5e1 !important;
        background-color: #f8fafc !important; color: #0f172a !important;
        font-family: "Segoe UI", Arial, sans-serif !important;
        padding: 0.6rem 1rem !important; transition: all 0.2s ease-in-out !important;
    }
    div.stTextInput input:focus {
        border-color: #0f3cc9 !important;
        box-shadow: 0 0 0 3px rgba(15, 60, 201, 0.15) !important;
        background-color: #ffffff !important;
    }
    div.stTextInput label p {
        font-family: "Segoe UI", Arial, sans-serif !important;
        font-weight: 600 !important; color: #334155 !important; font-size: 0.85rem !important;
    }
    div.stButton > button {
        background: #0f3cc9 !important; color: #ffffff !important;
        border: none !important; border-radius: 8px !important;
        font-family: "Segoe UI", Arial, sans-serif !important;
        font-size: 0.9rem !important; font-weight: 700 !important;
        padding: 0.7rem 1.5rem !important; width: 100% !important;
        box-shadow: 0 4px 12px rgba(15, 60, 201, 0.25) !important;
    }
    div.stButton > button:hover { background: #0c32aa !important; color: #ffffff !important; }
    .brand-wrap { text-align: center; margin-bottom: 1.5rem; }
    .brand-logo { font-size: 2.5rem; font-weight: 800; color: #0f3cc9; letter-spacing: -1.5px; line-height: 1; }
    .brand-title { font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-top: 0.4rem; }
    .brand-subtitle { font-family: Consolas, monospace; font-size: 0.62rem; color: #64748b; letter-spacing: 2px; text-transform: uppercase; margin-top: 0.3rem; }
    </style>
    """, unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 3, 1])
    with center_col:
        st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="brand-wrap">
            <div class="brand-logo">JIO</div>
            <div class="brand-title">Internal ISOC Dashboard</div>
            <div class="brand-subtitle">Production Build · Network Edition v6.4</div>
        </div>
        """, unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        submitted = st.button("Login", use_container_width=True)
        if submitted:
            if username == LOGIN_USERNAME and password == LOGIN_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Invalid operator credentials. Please verify and try again.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════
#  SIDEBAR — logout + SSH connection status
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🛡️ JIO ISOC v6.4 · PROD")
    st.caption("Operator Session Authenticated")
    if st.button("🔒 Logout Session", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown("---")
    st.markdown("**🔗 Infrastructure Links**")
    st.markdown(f"`JUMP` `{JUMP_SERVER_IP}:{SSH_PORT}`")
    st.markdown(f"`IBR ` `{IBR_IP}:{SSH_PORT}`")
    st.markdown("---")
    st.markdown("**ℹ️ Build Info**")
    st.caption("Air-gapped production build\nNo internet access required\nAll data via JIO infra SSH")

# ══════════════════════════════════════════════════════════════════════
#  INTERNAL-ONLY DNS CONFIG  (no external resolvers in production)
# ══════════════════════════════════════════════════════════════════════
DNS_OPTIONS: Dict[str, list] = {
    "5G/Sub6":    ["2405:200:800::11"],
    "LTE/Mobility": ["2405:200:800::1", "49.45.0.1"],
    "FTTX/UBR":   ["2405:200:800::3", "49.45.0.3"],
    "Enterprise": ["2405:200:800::4", "49.45.0.4"],
}
DNS_LABELS = list(DNS_OPTIONS.keys())
NAT64_PREFIX = "64:ff9b::"

# ══════════════════════════════════════════════════════════════════════
#  LOCAL ASN DATABASE  — JIO known peers + Indian/global transit
#  (replaces Cymru DNS — works fully offline)
#  Format: asn → (org_name, country_code, rir)
# ══════════════════════════════════════════════════════════════════════
_LOCAL_ASN_DB: Dict[int, Tuple[str, str, str]] = {
    # ── JIO / Reliance ─────────────────────────────────────────────
    55836:  ("Reliance Jio Infocomm Limited",            "IN", "APNIC"),
    18101:  ("Reliance Communications Limited",          "IN", "APNIC"),
    # ── Indian ISPs ────────────────────────────────────────────────
    9829:   ("BSNL — Bharat Sanchar Nigam Ltd",          "IN", "APNIC"),
    45609:  ("Bharti Airtel Ltd",                        "IN", "APNIC"),
    24560:  ("Bharti Airtel Ltd",                        "IN", "APNIC"),
    132165: ("Vodafone Idea Limited",                    "IN", "APNIC"),
    38266:  ("BSNL — Bharat Sanchar Nigam Ltd",         "IN", "APNIC"),
    17813:  ("MTNL — Mahanagar Telephone Nigam Ltd",    "IN", "APNIC"),
    45271:  ("TATA Communications Limited",              "IN", "APNIC"),
    55644:  ("Mahanagar Telephone Nigam Limited",        "IN", "APNIC"),
    10029:  ("SIFY Technologies Limited",                "IN", "APNIC"),
    38697:  ("Hathway Cable and Datacom Ltd",            "IN", "APNIC"),
    55410:  ("Vodafone India Limited",                   "IN", "APNIC"),
    139872: ("Reliance Jio Infocomm Limited (GW)",      "IN", "APNIC"),
    136702: ("JIO — National Long Distance",             "IN", "APNIC"),
    # ── Global Transit / Tier-1 ────────────────────────────────────
    6453:   ("TATA Communications (America) Inc",        "US", "ARIN"),
    3356:   ("Lumen Technologies (Level 3)",             "US", "ARIN"),
    1299:   ("Telia Company AB",                         "SE", "RIPE"),
    174:    ("Cogent Communications",                    "US", "ARIN"),
    2914:   ("NTT America, Inc.",                        "US", "ARIN"),
    6461:   ("Zayo Bandwidth",                           "US", "ARIN"),
    3257:   ("GTT Communications Inc.",                  "DE", "RIPE"),
    1221:   ("Telstra Corporation Ltd",                  "AU", "APNIC"),
    4766:   ("Korea Telecom",                            "KR", "APNIC"),
    3320:   ("Deutsche Telekom AG",                      "DE", "RIPE"),
    5511:   ("Orange S.A.",                              "FR", "RIPE"),
    701:    ("Verizon Business (UUNET)",                 "US", "ARIN"),
    7018:   ("AT&T Services, Inc.",                      "US", "ARIN"),
    # ── Cloud / CDN ────────────────────────────────────────────────
    15169:  ("Google LLC",                               "US", "ARIN"),
    16509:  ("Amazon.com, Inc.",                         "US", "ARIN"),
    14618:  ("Amazon Technologies Inc.",                 "US", "ARIN"),
    8075:   ("Microsoft Corporation",                    "US", "ARIN"),
    20940:  ("Akamai Technologies, Inc.",                "US", "ARIN"),
    13335:  ("Cloudflare, Inc.",                         "US", "ARIN"),
    32934:  ("Meta Platforms, Inc.",                     "US", "ARIN"),
    # ── APNIC / IANA ───────────────────────────────────────────────
    4608:   ("APNIC Pty Ltd",                            "AU", "APNIC"),
    1:      ("APNIC Research",                           "AU", "APNIC"),
}

# RIR mapping for known ASN ranges (broad heuristic)
def _rir_for_asn(asn: int) -> str:
    if asn in _LOCAL_ASN_DB:
        return _LOCAL_ASN_DB[asn][2]
    if 4608 <= asn <= 7675 or 9216 <= asn <= 10239 or 17408 <= asn <= 18431 or \
       23552 <= asn <= 24575 or 24832 <= asn <= 25599 or 38912 <= asn <= 39935 or \
       45056 <= asn <= 46079 or 55296 <= asn <= 56319 or 58368 <= asn <= 59391 or \
       131072 <= asn <= 141625:
        return "APNIC"
    if 1024 <= asn <= 7679 or 7680 <= asn <= 8191 or 12288 <= asn <= 13311 or \
       15360 <= asn <= 16383 or 20480 <= asn <= 21503 or 24576 <= asn <= 25599:
        return "RIPE"
    if asn <= 1024 or (7168 <= asn <= 7295):
        return "ARIN"
    return "UNKNOWN"

# ══════════════════════════════════════════════════════════════════════
#  SSH CONNECTION POOL  (module-level — persists across Streamlit reruns)
# ══════════════════════════════════════════════════════════════════════
_SSH_POOL: Dict[str, any] = {}
_SSH_POOL_LOCK = threading.Lock()

def _get_pooled_ssh(host: str, port: int, user: str, password: str) -> Tuple[Optional[any], str]:
    """Return a live pooled SSH client or create a new one."""
    if not HAS_PARAMIKO:
        return None, "paramiko not installed — pip install paramiko"
    key = f"{user}@{host}:{port}"
    with _SSH_POOL_LOCK:
        if key in _SSH_POOL:
            client = _SSH_POOL[key]
            try:
                transport = client.get_transport()
                if transport and transport.is_active():
                    return client, ""
            except Exception:
                pass
            try:
                client.close()
            except Exception:
                pass
            del _SSH_POOL[key]

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                host, port=port, username=user, password=password,
                timeout=SSH_TIMEOUT, auth_timeout=SSH_TIMEOUT,
                banner_timeout=SSH_TIMEOUT,
                allow_agent=False, look_for_keys=False,
            )
            _SSH_POOL[key] = client
            return client, ""
        except paramiko.AuthenticationException:
            return None, f"Authentication failed for {user}@{host}"
        except paramiko.SSHException as e:
            return None, f"SSH protocol error: {e}"
        except socket.timeout:
            return None, f"Connection timeout to {host}:{port}"
        except OSError as e:
            return None, f"Network error: {e}"
        except Exception as e:
            return None, str(e)

def _ssh_exec(client, cmd: str, timeout: int = SSH_TIMEOUT) -> Tuple[str, str]:
    """Execute a single command on an open SSH client. Returns (stdout, stderr)."""
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode("utf-8", "ignore").strip()
        err = stderr.read().decode("utf-8", "ignore").strip()
        return out[:3000], err[:300]
    except Exception as e:
        return "", str(e)

# ══════════════════════════════════════════════════════════════════════
#  BGP OUTPUT PARSER  — Cisco IOS / IOS-XR / JunOS
# ══════════════════════════════════════════════════════════════════════
def parse_bgp_show_output(output: str) -> Dict:
    """
    Parse 'show bgp ipv4 unicast <ip>' output from Cisco or JunOS.
    Returns dict with: asn, prefix, next_hop, local_pref, med, as_path, bgp_prefixes.
    """
    result: Dict = {
        "asn": 0, "prefix": "", "next_hop": "", "local_pref": 100,
        "med": 0, "as_path": [], "bgp_prefixes": 0,
    }
    if not output or "[✗]" in output:
        return result

    # ── Prefix ──────────────────────────────────────────────────────
    m = re.search(r"BGP routing table entry for ([\d.:/]+)", output, re.I)
    if not m:
        m = re.search(r"((?:\d{1,3}\.){3}\d{1,3}/\d{1,2})\s+\*?\[BGP", output)
    if m:
        result["prefix"] = m.group(1).strip()

    # ── AS Path ─────────────────────────────────────────────────────
    m = re.search(r"AS[_ ]?path[:\s]+([\d\s\(\)]+)", output, re.I)
    if not m:
        # Cisco inline: lines that are only whitespace + ASNs + optional trailing letter
        m = re.search(r"^\s+((?:\d+\s+)+\d+)\s*[EIe\?]?\s*$", output, re.MULTILINE)
    if m:
        asns = [x for x in re.findall(r"\d+", m.group(1)) if int(x) < 4294967296]
        result["as_path"] = [int(x) for x in asns]
        if asns:
            result["asn"] = int(asns[-1])  # rightmost = origin AS

    # ── Next Hop ────────────────────────────────────────────────────
    # Cisco:  "  X.X.X.X from X.X.X.X"  or  "  Next Hop: X.X.X.X"
    # JunOS:  "> to X.X.X.X via ge-..."
    m = re.search(r"^\s+((?:\d{1,3}\.){3}\d{1,3})\s+from\s+", output, re.MULTILINE)
    if not m:
        m = re.search(r">\s+to\s+((?:\d{1,3}\.){3}\d{1,3})\s+via", output)
    if not m:
        m = re.search(r"Next[ -]?Hop[:\s]+((?:\d{1,3}\.){3}\d{1,3})", output, re.I)
    if m:
        result["next_hop"] = m.group(1)

    # ── Local Preference ────────────────────────────────────────────
    m = re.search(r"localpref\s+(\d+)", output, re.I)
    if not m:
        m = re.search(r"Local[- ]?Pref[:\s]+(\d+)", output, re.I)
    if m:
        result["local_pref"] = int(m.group(1))

    # ── MED/Metric ──────────────────────────────────────────────────
    m = re.search(r"metric\s+(\d+)", output, re.I)
    if m:
        result["med"] = int(m.group(1))

    return result

def parse_bgp_summary_output(output: str) -> Tuple[int, int]:
    """Parse 'show bgp summary' — returns (total_prefixes, peer_count)."""
    if not output or "[✗]" in output:
        return 0, 0
    # Peer count: lines that start with an IPv4 peer address
    peer_lines = re.findall(
        r"^\s*((?:\d{1,3}\.){3}\d{1,3})\s+\d+\s+\d+\s+\d+\s+\d+",
        output, re.MULTILINE
    )
    peers = len(peer_lines)
    # Total prefixes from Cisco "Total number of prefixes X" or JunOS
    m = re.search(r"Total\s+(?:number\s+of\s+)?prefix(?:es)?[:\s]+(\d+)", output, re.I)
    if not m:
        m = re.search(r"(\d+)\s+network", output, re.I)
    prefixes = int(m.group(1)) if m else 0
    return prefixes, peers

# ══════════════════════════════════════════════════════════════════════
#  ASN LOOKUP — offline, from IBR output + local DB
# ══════════════════════════════════════════════════════════════════════
def lookup_asn_from_bgp_data(ip: str, bgp_data: Dict, summary_output: str = "") -> Tuple[Optional["ASNInfo"], str]:
    """
    Build ASNInfo from parsed IBR BGP data + local ASN DB.
    No internet calls — 100% offline.
    """
    asn      = bgp_data.get("asn", 0)
    prefix   = bgp_data.get("prefix", "")
    next_hop = bgp_data.get("next_hop", "")
    lp       = bgp_data.get("local_pref", 100)
    as_path  = bgp_data.get("as_path", [])

    # Resolve org / country / rir from local DB
    if asn and asn in _LOCAL_ASN_DB:
        org, country, rir = _LOCAL_ASN_DB[asn]
    elif asn:
        org     = f"AS{asn} (unknown peer)"
        country = "XX"
        rir     = _rir_for_asn(asn)
    else:
        org, country, rir = "Unknown", "XX", "UNKNOWN"

    # Handle for display (strip " - XX" suffixes)
    handle = re.sub(r",?\s*[A-Z]{2}\s*$", "", org).strip()
    handle_match = re.match(r"^([A-Z0-9_\-]+)", handle.upper())
    handle = handle_match.group(1) if handle_match else f"AS{asn}"

    # IRR validity: known in local DB = registered
    irr_valid = (asn in _LOCAL_ASN_DB) or (rir in ("APNIC", "ARIN", "RIPE") and asn > 0)

    # RPKI — derive from IRR; no external API call
    rpki = "Valid" if irr_valid else ("NotFound" if asn > 0 else "Unknown")

    # Prefix / routes / peers from summary
    bgp_prefixes, peer_count = parse_bgp_summary_output(summary_output)

    # Fallback prefix derivation
    if not prefix and "." in ip:
        parts = ip.split(".")
        prefix = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"

    ai = ASNInfo(
        asn=asn, handle=handle, org=org, country=country, rir=rir,
        irr_valid=irr_valid, rpki=rpki,
        num_routes=bgp_prefixes, num_peers=peer_count,
    )

    # ── Human-readable raw output for the Raw Terminal pane ─────────
    as_path_str = " → ".join(str(x) for x in as_path) if as_path else "N/A"
    raw = (
        f"[JIO ISOC PRODUCTION — IBR-sourced BGP Lookup, No Internet]\n"
        f"{'─'*55}\n"
        f"Target IP  : {ip}\n"
        f"ASN        : AS{asn} ({org})\n"
        f"Country    : {country}  |  RIR : {rir}\n"
        f"Prefix     : {prefix}\n"
        f"Next-Hop   : {next_hop}\n"
        f"Local-Pref : {lp}\n"
        f"AS-Path    : {as_path_str}\n"
        f"{'─'*55}\n"
        f"[IRR]   {'✓ Valid (in local ASN registry)' if irr_valid else '⚠ Not in local DB — route-leak risk'}\n"
        f"[RPKI]  {rpki}  (derived from IRR)\n"
        f"[RIR]   {rir}  |  Country: {country}\n"
        f"[Size]  {bgp_prefixes:,} prefixes  |  {peer_count} peers  (from IBR summary)\n"
    )
    return ai, raw

# ══════════════════════════════════════════════════════════════════════
#  CSS  (identical to dev build — no changes)
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }
.main .block-container { padding: 2rem 2rem 4rem; max-width: 1600px; }

.hdr { background: var(--secondary-background-color); border: 1px solid rgba(0, 86, 179, 0.15); border-top: 5px solid #0B58C6; border-radius: 10px; padding: 1.5rem 2rem; display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05); }
.hdr-logo { display: flex; align-items: center; gap: 1rem; }
.hdr-jio { font-size: 2.5rem; font-weight: 900; color: #0B58C6; letter-spacing: -1px; line-height: 1; }
.hdr-title { font-size: 1.25rem; font-weight: 800; color: var(--text-color); letter-spacing: -0.3px; margin-bottom: 0.2rem; }
.hdr-sub { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.8rem; color: #6b7280; letter-spacing: 1px; margin-top: 2px; font-weight: 600; }

div[data-testid="stTabs"] button { font-family: 'JetBrains Mono', Consolas, monospace !important; font-size: 0.95rem !important; font-weight: 700 !important; letter-spacing: 0.5px !important; padding: 0.6rem 1.2rem !important; }
div.stButton > button { background: #0B58C6 !important; color: #ffffff !important; font-family: 'JetBrains Mono', Consolas, monospace !important; font-size: 0.9rem !important; font-weight: 700 !important; letter-spacing: 1px !important; padding: 0.6rem 1.2rem !important; border: none !important; border-radius: 6px !important; box-shadow: 0 4px 10px rgba(11, 88, 198, 0.25) !important; transition: all 0.2s ease-in-out !important; }
div.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 15px rgba(11, 88, 198, 0.4) !important; background: #0040cc !important; }

.badge { display: inline-block; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: 800; font-family: 'JetBrains Mono', Consolas, monospace; letter-spacing: 0.5px; }
.b-ok   { background: rgba(40, 167, 69, 0.15); color: #1e7e34; border: 1px solid rgba(40, 167, 69, 0.3); }
.b-warn { background: rgba(255, 193, 7, 0.15); color: #d39e00; border: 1px solid rgba(255, 193, 7, 0.3); }
.b-err  { background: rgba(220, 53, 69, 0.15); color: #c82333; border: 1px solid rgba(220, 53, 69, 0.3); }

.pipeline { display: flex; flex-direction: column; gap: 6px; }
.pip-step { display: flex; align-items: center; gap: 0.8rem; padding: 0.6rem 1rem; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); background: var(--secondary-background-color); font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.85rem; }
.pip-step.done { border-color: rgba(40,167,69,0.5); background: rgba(40,167,69,0.08); }
.pip-step.warn { border-color: rgba(255,193,7,0.5); background: rgba(255,193,7,0.08); }
.pip-step.err  { border-color: rgba(220,53,69,0.5); background: rgba(220,53,69,0.08); }
.pip-step.run  { border-color: #0B58C6; background: rgba(11,88,198,0.05); box-shadow: 0 0 8px rgba(11,88,198,0.2); }
.pip-step.pending { border-color: rgba(128,128,128,0.3); background: transparent; opacity: 0.6; }
.pip-icon { font-size: 1.1rem; width: 20px; text-align: center; }
.pip-text { flex: 1; }
.pip-label { font-weight: 700; color: var(--text-color); font-size: 0.9rem; }
.pip-sub { color: #6b7280; font-size: 0.75rem; margin-top: 2px; font-weight: 500; }
.pip-badge { font-size: 0.75rem; font-weight: 800; padding: 0.2rem 0.5rem; border-radius: 4px; white-space: nowrap; }
.pb-done { background: rgba(40,167,69,0.2); color: #1e7e34; }
.pb-skip { background: rgba(128,128,128,0.2); color: #6c757d; }
.pb-run  { background: rgba(0,123,255,0.2); color: #0056b3; }
.pb-err  { background: rgba(220,53,69,0.2); color: #c82333; }

#jio-widget-content .pipeline { gap: 4px; }
#jio-widget-content .pip-step { padding: 0.4rem 0.6rem; font-size: 0.75rem; border-radius: 6px; }
#jio-widget-content .pip-label { font-size: 0.75rem; line-height: 1.1; }
#jio-widget-content .pip-sub   { font-size: 0.6rem;  line-height: 1.1; }
#jio-widget-content .pip-badge { font-size: 0.6rem;  padding: 0.15rem 0.35rem; }

.panel { background: var(--secondary-background-color); border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
.panel-hdr { background: rgba(0, 123, 255, 0.03); border-bottom: 1px solid rgba(0,0,0,0.06); padding: 0.6rem 1rem; display: flex; align-items: center; gap: 0.6rem; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.85rem; font-weight: 800; color: var(--text-color); letter-spacing: 1px; }
.panel-body { padding: 1rem; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.85rem; color: var(--text-color); line-height: 1.6; }

.hop-table { width: 100%; border-collapse: collapse; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.85rem; }
.hop-table th { color: #6b7280; padding: 0.6rem 0.8rem; text-align: left; border-bottom: 2px solid rgba(0,0,0,0.1); font-weight: 800; letter-spacing: 1px; }
.hop-table td { padding: 0.5rem 0.8rem; border-bottom: 1px solid rgba(0,0,0,0.05); color: var(--text-color); font-weight: 500; }
.hop-table tr:hover td { background: rgba(0,123,255,0.03); }

.mini-stats { display: flex; gap: 0.8rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.mini-stat { background: var(--secondary-background-color); border: 1px solid rgba(0,0,0,0.08); border-radius: 8px; padding: 1rem 0.5rem; flex: 1; min-width: 90px; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: center; }
.ms-lbl { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.7rem; color: #6b7280; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 800; text-transform: uppercase; }
.ms-num { font-size: 1.5rem; font-weight: 900; color: #0B58C6; line-height: 1.1; margin-top: auto; }

.slabel { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.85rem; letter-spacing: 1px; color: #4b5563; font-weight: 800; text-transform: uppercase; margin-bottom: 0.5rem; }

.rtbl { width: 100%; border-collapse: separate; border-spacing: 0 4px; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.85rem; table-layout: fixed; }
.rtbl th { color: #6b7280; padding: 0.5rem 0.8rem; text-align: left; font-size: 0.8rem; letter-spacing: 1px; font-weight: 800; white-space: nowrap; overflow: hidden; }
.rtbl td { padding: 0.6rem 0.8rem; background: var(--secondary-background-color); border-top: 1px solid rgba(0,0,0,0.05); border-bottom: 1px solid rgba(0,0,0,0.05); color: var(--text-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }
.rtbl td:first-child { border-left: 1px solid rgba(0,0,0,0.05); border-radius: 6px 0 0 6px; }
.rtbl td:last-child  { border-right: 1px solid rgba(0,0,0,0.05); border-radius: 0 6px 6px 0; }
.rtbl tr.sel td { background: rgba(11,88,198,0.05); border-color: #0B58C6; border-top: 1px solid #0B58C6; border-bottom: 1px solid #0B58C6; }
.rtbl tr.sel td:first-child { border-left: 1px solid #0B58C6; }
.rtbl tr.sel td:last-child  { border-right: 1px solid #0B58C6; }
.rtbl tr:hover td { background: rgba(0,0,0,0.02); }
.domain-cell { font-weight: 800; color: var(--text-color); font-size: 0.9rem; }
.ip-count-chip { background: rgba(11, 88, 198, 0.1); color: #0B58C6; padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.75rem; font-weight: 800; }
.invalid-domain { color: #dc3545 !important; text-decoration: line-through; }
code, pre { font-size: 0.85rem !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  DATA CLASSES  (identical to dev build)
# ══════════════════════════════════════════════════════════════════════
@dataclass
class HopInfo:
    num: int
    ip: str
    hostname: str
    latency_ms: float
    network: str
    is_anomaly: bool = False
    anomaly_reason: str = ""

@dataclass
class ASNInfo:
    asn: int
    handle: str
    org: str
    country: str
    rir: str
    irr_valid: bool
    rpki: str
    num_routes: int
    num_peers: int

@dataclass
class IPAnalysis:
    ip: str
    ip_version: int = 4
    is_synthetic_v6: bool = False
    ping_raw: str = ""
    traceroute_raw: str = ""
    ibr_raw: str = ""
    bgp_raw: str = ""
    hops: List[HopInfo] = field(default_factory=list)
    asn_info: Optional[ASNInfo] = None
    peer_asn: int = 0
    prefix: str = ""
    next_hop: str = ""
    local_pref: int = 100
    avg_latency: float = 0.0
    packet_loss: float = 0.0
    ping_ok: bool = False
    bgp_prefixes: int = 0
    health: str = "healthy"
    bottleneck_hop: int = 0

@dataclass
class SiteReport:
    domain: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    valid: bool = True
    fetch_time: float = 0.0
    resolved_ips: List[str] = field(default_factory=list)
    resolved_ipv4: List[str] = field(default_factory=list)
    resolved_ipv6: List[str] = field(default_factory=list)
    synthetic_ipv6: List[str] = field(default_factory=list)
    primary_ip: str = ""
    dns_raw: str = ""
    jump_raw: str = ""
    ip_analyses: List[IPAnalysis] = field(default_factory=list)
    health: str = "healthy"
    steps_status: dict = field(default_factory=lambda: {
        "dns": "pending", "ping": "pending", "traceroute": "pending",
        "ibr": "pending", "bgp": "pending", "asn": "pending", "jump": "pending"
    })
    avg_latency: float = 0.0
    packet_loss: float = 0.0
    peer_asn: int = 0
    prefix: str = ""
    asn_info: Optional[ASNInfo] = None
    dns_server_used: str = "49.45.0.1"
    dns_profile: str = "LTE/Mobility"
    invalid_reason: str = ""

# ══════════════════════════════════════════════════════════════════════
#  UTILITY — ICMP checksum, resolver builder, NAT64 synthesis
# ══════════════════════════════════════════════════════════════════════
def _icmp_checksum(data: bytes) -> int:
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + (data[i + 1] if i + 1 < len(data) else 0)
        s += w
    s = (s >> 16) + (s & 0xFFFF)
    s += (s >> 16)
    return ~s & 0xFFFF

def _build_resolver(server: str, timeout: float = 1.5) -> "dns.resolver.Resolver":
    r = dns.resolver.Resolver(configure=False)
    r.nameservers = [server]
    r.timeout  = timeout
    r.lifetime = timeout + 1.5
    return r

def _ipv4_to_nat64(ipv4: str) -> str:
    try:
        parts = ipv4.split(".")
        a, b, c, d = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
        hi = (a << 8) | b
        lo = (c << 8) | d
        return f"64:ff9b::{hi:04x}:{lo:04x}"
    except Exception:
        return "64:ff9b::0:0"

# ══════════════════════════════════════════════════════════════════════
#  DNS STEP  — internal nameservers only
# ══════════════════════════════════════════════════════════════════════
def step_dns(domain: str, dns_profile: str = "LTE/Mobility", req_proto: str = "Both") -> Tuple[List[str], str, str, List[str], List[str], List[str]]:
    servers = DNS_OPTIONS.get(dns_profile, ["49.45.0.1"])
    lines = [
        f"; Query time: {datetime.now().strftime('%H:%M:%S UTC')}",
        f"; DNS Profile: {dns_profile}  [INTERNAL — Production Build]",
        "",
    ]
    ipv4_list: List[str] = []
    ipv6_list: List[str] = []
    synth_v6:  List[str] = []
    success_server = None
    confirmed_nxdomain = False

    if not HAS_DNSPY:
        try:
            results = socket.getaddrinfo(domain, None)
            seen: set = set()
            for r in results:
                ip = r[4][0]
                if ip not in seen:
                    seen.add(ip)
                    if ":" not in ip: ipv4_list.append(ip)
                    else: ipv6_list.append(ip)
            if not ipv4_list and not ipv6_list:
                lines.append("; [socket fallback] No addresses returned — NXDOMAIN/NODATA")
                return [], "\n".join(lines), "err", [], [], []
            lines.append("; [socket.getaddrinfo fallback — dnspython not installed]")
            success_server = "OS Resolver (fallback)"
        except socket.gaierror as e:
            lines.append(f"; ERROR: {e}")
            return [], "\n".join(lines), "err", [], [], []
    else:
        for server in servers:
            resolver = _build_resolver(server, timeout=1.5)
            lines.append(f"$ nslookup {domain} {server}")
            srv_v4: List[str] = []
            srv_v6: List[str] = []
            try:
                if req_proto in ("Both", "IPv4"):
                    try:
                        for rr in resolver.resolve(domain, "A"):
                            srv_v4.append(rr.address)
                    except dns.resolver.NXDOMAIN:
                        lines.append(f";; NXDOMAIN — {domain} does not exist (authoritative from {server}).")
                        confirmed_nxdomain = True; break
                    except (dns.resolver.NoAnswer, dns.exception.Timeout, Exception):
                        pass

                if req_proto in ("Both", "IPv6"):
                    try:
                        for rr in resolver.resolve(domain, "AAAA"):
                            srv_v6.append(rr.address)
                    except dns.resolver.NXDOMAIN:
                        lines.append(f";; NXDOMAIN — {domain} does not exist (authoritative from {server}).")
                        confirmed_nxdomain = True; break
                    except (dns.resolver.NoAnswer, dns.exception.Timeout, Exception):
                        pass

                if srv_v4 or srv_v6:
                    ipv4_list = srv_v4; ipv6_list = srv_v6
                    success_server = server; break
                else:
                    lines.append(f";; No records from {server}, trying next...")
            except dns.resolver.NXDOMAIN:
                lines.append(f";; NXDOMAIN from {server}.")
                confirmed_nxdomain = True; break
            except (dns.exception.Timeout, Exception) as e:
                lines.append(f";; Failed on {server}: {e}. Failing over...")

        if confirmed_nxdomain or (not success_server and not ipv4_list and not ipv6_list):
            reason = "NXDOMAIN" if confirmed_nxdomain else "NXDOMAIN/NODATA/TIMEOUT"
            lines.append(f";; {reason}")
            return [], "\n".join(lines), "err", [], [], []

        if ipv4_list:
            lines.append(";; ANSWER SECTION (A):")
            for ip in ipv4_list: lines.append(f"{domain}. IN A  {ip}")
        if ipv6_list:
            lines.append(";; ANSWER SECTION (AAAA):")
            for ip in ipv6_list: lines.append(f"{domain}. IN AAAA  {ip}")

    # NAT64 synthesis
    if ipv4_list and req_proto in ("Both", "IPv6"):
        lines.append(""); lines.append(";; Synthesising NAT64 (64:ff9b::/96) from IPv4 records:")
        for ip4 in ipv4_list:
            sv6 = _ipv4_to_nat64(ip4)
            if sv6 not in synth_v6: synth_v6.append(sv6)
            lines.append(f";; NAT64: {ip4}  →  {sv6}")

    all_ips = list(dict.fromkeys(ipv4_list + ipv6_list))
    prim = all_ips[0] if all_ips else "0.0.0.0"
    lines += [
        "",
        f";; {len(ipv4_list)} A record(s) | {len(ipv6_list)} AAAA record(s)"
        + (f" | {len(synth_v6)} NAT64 synthetic" if synth_v6 else ""),
        f";; Primary → {prim}",
        f";; Successful DNS Server: {success_server or 'None'}",
    ]
    return all_ips, "\n".join(lines), "ok", ipv4_list, ipv6_list, synth_v6

# ══════════════════════════════════════════════════════════════════════
#  PING — ICMP raw socket with TCP fallback (unchanged from dev build)
# ══════════════════════════════════════════════════════════════════════
def _tcp_probe(host: str, ports: list = None, count: int = 10, timeout: float = 2.0) -> Tuple[bool, float, float, str]:
    if ports is None: ports = [443, 80, 53, 8080, 22]
    latencies = []; lines = [f"$ tcp-probe {host}  (ICMP unavailable — TCP port probe)"]
    recv = 0; family = socket.AF_INET6 if ":" in host else socket.AF_INET
    for _ in range(count):
        for port in ports:
            s = None
            try:
                s = socket.socket(family, socket.SOCK_STREAM)
                s.settimeout(timeout)
                t0 = time.perf_counter()
                s.connect((host, port))
                rtt = (time.perf_counter() - t0) * 1000
                latencies.append(rtt); lines.append(f"TCP {host}:{port}  time={rtt:.1f}ms")
                recv += 1; break
            except Exception: continue
            finally:
                if s is not None:
                    try: s.close()
                    except: pass
        else:
            lines.append("All TCP ports timed out")
    loss = round((count - recv) / count * 100, 1)
    avg  = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
    if latencies:
        lines.append(f"\n{count} probes, {recv} OK, {loss}% loss  "
                     f"rtt min/avg/max = {min(latencies):.1f}/{avg:.1f}/{max(latencies):.1f} ms")
    return recv > 0, avg, loss, "\n".join(lines)

def _icmp_ping(host: str, count: int = 10, timeout: float = 1.0) -> Tuple[bool, float, float, str]:
    family = socket.AF_INET6 if ":" in host else socket.AF_INET
    try:
        if family == socket.AF_INET: dest_ip = socket.gethostbyname(host)
        else: dest_ip = socket.getaddrinfo(host, None, family)[0][4][0]
    except Exception as e:
        return False, 0.0, 100.0, f"Cannot resolve {host}: {e}"

    ID = (os.getpid() ^ random.randint(1, 0xFFFF)) & 0xFFFF
    latencies: List[float] = []; lines = [f"$ ping -c {count} {host}", f"PING {host} ({dest_ip}) 56(84) bytes of data."]
    received = 0

    def _pkt_v4(seq):
        hdr = struct.pack("!BBHHH", 8, 0, 0, ID, seq); data = b"JIO-ISOC" * 7
        cs  = _icmp_checksum(hdr + data)
        return struct.pack("!BBHHH", 8, 0, cs, ID, seq) + data

    def _pkt_v6(seq):
        hdr = struct.pack("!BBHHH", 128, 0, 0, ID, seq)
        return hdr + b"JIO-ISOC" * 7

    sock = None
    try:
        proto = socket.IPPROTO_ICMPV6 if family == socket.AF_INET6 else socket.IPPROTO_ICMP
        sock  = socket.socket(family, socket.SOCK_RAW, proto)
        sock.settimeout(timeout)
    except Exception:
        return _tcp_probe(dest_ip, count=count, timeout=timeout)

    try:
        for seq in range(1, count + 1):
            pkt = _pkt_v4(seq) if family == socket.AF_INET else _pkt_v6(seq)
            t0  = time.perf_counter()
            try:
                if family == socket.AF_INET: sock.sendto(pkt, (dest_ip, 0))
                else: sock.sendto(pkt, (dest_ip, 0, 0, 0))
                while True:
                    raw, addr = sock.recvfrom(4096)
                    rtt = (time.perf_counter() - t0) * 1000
                    if family == socket.AF_INET:
                        ihl = (raw[0] & 0x0F) * 4
                        if len(raw) < ihl + 8: continue
                        if raw[ihl] == 0 and struct.unpack("!H", raw[ihl+4:ihl+6])[0] == ID:
                            lines.append(f"64 bytes from {addr[0]}: icmp_seq={seq} ttl={raw[8]} time={rtt:.1f} ms")
                            latencies.append(rtt); received += 1; break
                    else:
                        if len(raw) < 8: continue
                        if raw[0] == 129 and struct.unpack("!H", raw[4:6])[0] == ID:
                            lines.append(f"Response from {addr[0]}: icmp_seq={seq} time={rtt:.1f} ms")
                            latencies.append(rtt); received += 1; break
            except socket.timeout:
                lines.append(f"Request timeout for icmp_seq {seq}")
            except Exception:
                pass
            time.sleep(0.05)
    finally:
        try: sock.close()
        except: pass

    loss = round((count - received) / count * 100, 1)
    avg  = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
    lines += ["", f"--- {host} ping statistics ---",
              f"{count} packets transmitted, {received} received, {loss}% packet loss",
              f"rtt min/avg/max = {min(latencies):.1f}/{avg:.1f}/{max(latencies):.1f} ms" if latencies else ""]
    return received > 0, avg, loss, "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════
#  TRACEROUTE  (unchanged from dev build)
# ══════════════════════════════════════════════════════════════════════
def _subprocess_traceroute(host: str, ipv6: bool = False, max_hops: int = 30) -> Tuple[List[HopInfo], str]:
    system = platform.system()
    if system == "Windows":
        cmd = ["tracert", "-d", "-w", "500", "-h", str(max_hops), host]
    elif ipv6:
        for bin_ in ["traceroute6", "traceroute"]:
            if subprocess.run(["which", bin_], capture_output=True).returncode == 0:
                cmd = [bin_, "-n", "-q", "3", "-w", "1", "-m", str(max_hops), host]; break
        else:
            return [], ""
    else:
        if subprocess.run(["which", "traceroute"], capture_output=True).returncode == 0:
            cmd = ["traceroute", "-n", "-q", "3", "-w", "1", "-m", str(max_hops), host]
        else:
            return [], ""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        raw = result.stdout or result.stderr
        return _parse_traceroute_output(raw, host), raw
    except Exception:
        return [], ""

def _parse_traceroute_output(output: str, dest: str) -> List[HopInfo]:
    hops = []; seen_nums: set = set()
    ip_pattern = r'((?:\d{1,3}\.){3}\d{1,3}|(?:[a-fA-F0-9]{1,4}:){2,7}[a-fA-F0-9]{1,4})'
    for line in output.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith(("Tracing", "traceroute", "over a maximum")): continue
        m_hop = re.match(r'^(\d+)\s+', line)
        if not m_hop: continue
        num = int(m_hop.group(1))
        if num in seen_nums: continue
        seen_nums.add(num)
        ips   = re.findall(ip_pattern, line)
        times = [float(x) for x in re.findall(r'([\d\.]+)\s*ms', line)]
        if ips and times:
            hops.append(HopInfo(num=num, ip=ips[0], hostname=ips[0], latency_ms=min(times), network=""))
        elif "*" in line:
            hops.append(HopInfo(num=num, ip="*", hostname="*", latency_ms=0.0, network="-"))
    return hops

def _raw_icmp_traceroute(dest_ip: str, max_hops: int = 30, timeout: float = 0.5) -> Tuple[List[HopInfo], str]:
    lines   = [f"traceroute to {dest_ip}, {max_hops} hops max, 3 probes per hop"]
    hops    = []; ID = (os.getpid() ^ random.randint(1, 0xFFFF)) & 0xFFFF; reached = False
    for ttl in range(1, max_hops + 1):
        hop_ip = "*"; hostname = "*"; rtts = []
        for _ in range(3):
            recv_sock = send_sock = None
            try:
                recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                recv_sock.settimeout(timeout)
                send_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
                hdr = struct.pack("!BBHHH", 8, 0, 0, ID, ttl); data = b"JIOISOC" * 4
                cs  = _icmp_checksum(hdr + data)
                pkt = struct.pack("!BBHHH", 8, 0, cs, ID, ttl) + data
                t0  = time.perf_counter()
                send_sock.sendto(pkt, (dest_ip, 0))
                try:
                    while True:
                        raw, addr = recv_sock.recvfrom(4096)
                        elapsed = (time.perf_counter() - t0) * 1000
                        ihl = (raw[0] & 0x0F) * 4
                        if len(raw) < ihl + 1: continue
                        if raw[ihl] in (0, 3, 11):
                            hop_ip = addr[0]
                            if hostname == "*":
                                try: hostname = socket.gethostbyaddr(hop_ip)[0]
                                except: hostname = hop_ip
                            rtts.append(elapsed); break
                except socket.timeout:
                    pass
            except Exception:
                pass
            finally:
                for s in (send_sock, recv_sock):
                    if s:
                        try: s.close()
                        except: pass
        min_rtt = min(rtts) if rtts else 0.0
        if hop_ip != "*":
            lines.append(f"  {ttl:2d}  {hostname} ({hop_ip})  {' '.join(f'{r:.1f} ms' for r in rtts)}  [Min: {min_rtt:.1f} ms]")
        else:
            lines.append(f"  {ttl:2d}  * * *")
        hops.append(HopInfo(num=ttl, ip=hop_ip, hostname=hostname, latency_ms=round(min_rtt, 1), network=""))
        if hop_ip == dest_ip: reached = True; break
    if not reached:
        for port in [443, 80, 53]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1); t0 = time.perf_counter(); s.connect((dest_ip, port))
                rtt = (time.perf_counter() - t0) * 1000; s.close()
                n   = len(hops) + 1
                lines.append(f"  {n:2d}  {dest_ip} ({dest_ip})  {rtt:.1f} ms  [TCP:{port}]")
                hops.append(HopInfo(num=n, ip=dest_ip, hostname=dest_ip, latency_ms=round(rtt, 1), network="destination"))
                break
            except: pass
    return hops, "\n".join(lines)

def run_traceroute(ip: str, ipv6: bool = False, max_hops: int = 30) -> Tuple[List[HopInfo], str]:
    hops, raw = _subprocess_traceroute(ip, ipv6=ipv6, max_hops=max_hops)
    if hops: return hops, raw
    if not ipv6:
        hops, raw = _raw_icmp_traceroute(ip, max_hops=max_hops)
        if hops: return hops, raw
    return [], f"traceroute {ip}: no binary or raw socket available"

# ══════════════════════════════════════════════════════════════════════
#  ANOMALY DETECTION  (unchanged)
# ══════════════════════════════════════════════════════════════════════
def detect_anomalies(hops: List[HopInfo]) -> Tuple[int, str]:
    valid = [(h.num, h.latency_ms) for h in hops if h.ip != "*" and h.latency_ms > 0]
    if len(valid) < 2: return 0, ""
    bottleneck_hop = 0; max_jump = 0.0; descriptions = []
    for i in range(1, len(valid)):
        jump = valid[i][1] - valid[i-1][1]
        if jump > max_jump: max_jump = jump; bottleneck_hop = valid[i][0]
    for h in hops:
        for i, (num, ms) in enumerate(valid):
            if h.num == num and i > 0:
                jump = ms - valid[i-1][1]
                if jump > 50:
                    h.is_anomaly = True; h.anomaly_reason = f"+{jump:.0f}ms spike"
                    descriptions.append(f"Hop {num} ({h.ip}): +{jump:.0f}ms jump")
                elif ms > 150:
                    h.is_anomaly = True; h.anomaly_reason = f"High RTT: {ms:.0f}ms"
                    descriptions.append(f"Hop {num} ({h.ip}): high latency {ms:.0f}ms")
    star_hops = [h for h in hops if h.ip == "*"]
    if len(star_hops) > 3:
        descriptions.append(f"{len(star_hops)} non-responding hops — ICMP rate-limited or filtered")
    return bottleneck_hop, "; ".join(descriptions) if descriptions else "No significant anomalies"

# ══════════════════════════════════════════════════════════════════════
#  SSH FUNCTIONS — production-safe, pooled, with real output parsing
# ══════════════════════════════════════════════════════════════════════
def _paramiko_ssh(host: str, port: int, user: str, password: str,
                  commands: List[str], label: str) -> str:
    lines = [f"$ ssh {user}@{host} -p {port}  [{label}]"]
    if not HAS_PARAMIKO:
        lines.append("[✗] paramiko not installed — pip install paramiko")
        return "\n".join(lines)
    client, err = _get_pooled_ssh(host, port, user, password)
    if not client:
        lines.append(f"[✗] Connection failed: {err}")
        lines.append(f"[!] Verify: host={host}  port={port}  user={user}")
        lines.append("[!] Check .streamlit/secrets.toml or environment variables.")
        return "\n".join(lines)
    transport = client.get_transport()
    cipher = transport.get_security_options().ciphers[0] if transport else "negotiated"
    lines.append(f"[✓] SSH handshake OK — {cipher}  (pooled session)")
    lines.append(f"[✓] Authenticated as '{user}'")
    for cmd in commands:
        lines.append(f"\n{label}# {cmd}")
        out, err_msg = _ssh_exec(client, cmd)
        if out:   lines.append(out)
        if err_msg: lines.append(f"[stderr] {err_msg}")
    return "\n".join(lines)

def connect_jump_server(target_ip: str) -> str:
    cmds = [
        "show version | include uptime",
        f"show ip route {target_ip}",
        f"ping {target_ip} repeat 10",
    ]
    return _paramiko_ssh(JUMP_SERVER_IP, SSH_PORT, JUMP_SERVER_USER, JUMP_SERVER_PASS,
                         cmds, label="JUMP-SERVER")

def connect_ibr(target_ip: str) -> str:
    """Run BGP/route commands on IBR and return the full raw output."""
    cmds = [
        f"show bgp ipv4 unicast {target_ip}",
        f"show route {target_ip}",
        f"show bgp summary | head 30",
    ]
    return _paramiko_ssh(IBR_IP, SSH_PORT, IBR_USER, IBR_PASS, cmds, label="IBR")

def _extract_ibr_sections(ibr_raw: str) -> Tuple[str, str]:
    """
    Split full IBR output into (bgp_unicast_section, bgp_summary_section).
    Heuristic: split on 'IBR# show bgp summary' command marker.
    """
    bgp_section = ibr_raw
    summary_section = ""
    # Split on the summary command line
    parts = re.split(r"IBR#\s*show bgp summary", ibr_raw, flags=re.IGNORECASE)
    if len(parts) >= 2:
        bgp_section = parts[0]
        summary_section = parts[1]
    return bgp_section, summary_section

# ══════════════════════════════════════════════════════════════════════
#  HOP ASN ANNOTATION — local DB only (offline)
# ══════════════════════════════════════════════════════════════════════
def _asn_label_for_hop(ip: str) -> str:
    """Best-effort ASN label for a traceroute hop — local DB, no internet."""
    if not ip or ip == "*": return ""
    # Check known JIO ranges heuristically
    try:
        parts = ip.split(".")
        if len(parts) != 4: return ""
        a, b = int(parts[0]), int(parts[1])
        if a == 49 and b == 44:  return "AS55836 JIO"
        if a == 49 and b == 45:  return "AS55836 JIO"
        if a == 49 and b == 46:  return "AS55836 JIO"
        if a == 182 and b == 79: return "AS45609 AIRTEL"
        if a == 125 and b == 18: return "AS9829 BSNL"
        if a == 61  and b == 0:  return "AS9829 BSNL"
    except Exception:
        pass
    return ""

# ══════════════════════════════════════════════════════════════════════
#  IP ANALYSIS — orchestrates ping, trace, IBR SSH, BGP/ASN parsing
# ══════════════════════════════════════════════════════════════════════
def analyse_ip(ip: str, use_ibr: bool = True, domain: str = "",
               r_ref: Optional[SiteReport] = None) -> IPAnalysis:
    is_v6   = ":" in ip
    is_nat64 = ip.startswith("64:ff9b:") or ip.startswith("64:ff9b::")
    a = IPAnalysis(ip=ip, ip_version=6 if is_v6 else 4, is_synthetic_v6=is_nat64)

    # Resolve NAT64 → real IPv4 for probing
    probe_ip = ip
    if is_nat64:
        try:
            hex_parts = ip.split("::")[-1]
            parts = hex_parts.split(":")
            if len(parts) == 2:
                a_b = int(parts[0], 16); c_d = int(parts[1], 16)
                probe_ip = f"{a_b>>8}.{a_b&0xFF}.{c_d>>8}.{c_d&0xFF}"
        except Exception:
            pass

    tr_ip = probe_ip  # Use real IPv4 for SSH/BGP commands

    # ── PING ──────────────────────────────────────────────────────
    if r_ref: r_ref.steps_status["ping"] = "run"
    if is_v6 and not is_nat64:
        a.ping_ok, a.avg_latency, a.packet_loss, a.ping_raw = _tcp_probe(ip, count=10, timeout=2.0)
    else:
        a.ping_ok, a.avg_latency, a.packet_loss, a.ping_raw = _icmp_ping(probe_ip, count=10, timeout=1.0)
    if r_ref: r_ref.steps_status["ping"] = "ok" if a.ping_ok else "err"

    # ── TRACEROUTE ────────────────────────────────────────────────
    if r_ref: r_ref.steps_status["traceroute"] = "run"
    tr_target = ip if (is_v6 and not is_nat64) else probe_ip
    a.hops, a.traceroute_raw = run_traceroute(tr_target, ipv6=(is_v6 and not is_nat64))
    if r_ref: r_ref.steps_status["traceroute"] = "ok" if a.hops else "err"

    # ── IBR SSH + BGP/ASN PARSING ─────────────────────────────────
    if use_ibr:
        if r_ref: r_ref.steps_status["ibr"] = "run"
        a.ibr_raw = connect_ibr(tr_ip)
        ibr_ok = "[✓]" in a.ibr_raw
        if r_ref: r_ref.steps_status["ibr"] = "ok" if ibr_ok else "err"

        if r_ref: r_ref.steps_status["bgp"] = "run"
        bgp_section, summary_section = _extract_ibr_sections(a.ibr_raw)
        bgp_data = parse_bgp_show_output(bgp_section)
        asn_info, radb = lookup_asn_from_bgp_data(tr_ip, bgp_data, summary_section)
        a.asn_info     = asn_info
        a.peer_asn     = asn_info.asn if asn_info else 0
        a.prefix       = bgp_data.get("prefix", "")
        a.next_hop     = bgp_data.get("next_hop", tr_ip)
        a.local_pref   = bgp_data.get("local_pref", 100)
        a.bgp_prefixes = asn_info.num_routes if asn_info else 0

        # Combine raw IBR output with parsed ASN block
        a.bgp_raw = (
            f"[BGP Intelligence — IBR SSH + Local ASN DB]\n"
            f"IBR# show bgp ipv4 unicast {tr_ip}\n"
            f"{bgp_section.strip()}\n\n"
            f"{radb}"
        )
        if r_ref: r_ref.steps_status["bgp"] = "ok"

        # Prefix fallback
        if not a.prefix and "." in tr_ip:
            pts = tr_ip.split(".")
            a.prefix = f"{pts[0]}.{pts[1]}.{pts[2]}.0/24"

        if r_ref: r_ref.steps_status["asn"] = "ok"
    else:
        # IBR disabled — use local DB only
        if r_ref:
            r_ref.steps_status.update({"ibr": "skip", "bgp": "skip", "asn": "run"})
        bgp_data = {}
        asn_info, radb = lookup_asn_from_bgp_data(tr_ip, bgp_data)
        a.asn_info = asn_info
        a.bgp_raw  = radb
        if r_ref: r_ref.steps_status["asn"] = "ok"

    # ── HOP ASN ANNOTATION ────────────────────────────────────────
    for h in a.hops:
        if h.ip and h.ip not in ("*", ""):
            h.network = _asn_label_for_hop(h.ip)

    # ── ANOMALY DETECTION ────────────────────────────────────────
    a.bottleneck_hop, _ = detect_anomalies(a.hops)

    # ── HEALTH ASSESSMENT ─────────────────────────────────────────
    irr_warn = a.asn_info and not a.asn_info.irr_valid
    if irr_warn: a.health = "critical"
    elif not a.ping_ok or a.packet_loss > 0: a.health = "degraded"
    else: a.health = "healthy"

    return a

# ══════════════════════════════════════════════════════════════════════
#  DOMAIN ANALYSIS ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════
def analyse_domain(r: SiteReport, use_ibr: bool = True,
                   dns_profile: str = "LTE/Mobility",
                   req_proto: str = "Both") -> SiteReport:
    t_start = time.perf_counter()
    domain = r.domain

    r.steps_status["dns"] = "run"
    all_ips, r.dns_raw, dns_st, ipv4_list, ipv6_list, synth_v6 = step_dns(domain, dns_profile, req_proto)
    r.steps_status["dns"] = dns_st

    if dns_st == "err":
        r.valid = False
        if   "NXDOMAIN" in r.dns_raw:         r.invalid_reason = "NXDOMAIN"
        elif "TIMEOUT"  in r.dns_raw.upper():  r.invalid_reason = "DNS Timeout / Unreachable"
        elif "NODATA"   in r.dns_raw.upper():  r.invalid_reason = "NODATA — no records returned"
        else:                                  r.invalid_reason = "NXDOMAIN / unresolvable"
        r.health = "critical"
        r.steps_status.update({"ping":"skip","ibr":"skip","bgp":"skip",
                                "asn":"skip","traceroute":"skip","jump":"skip"})
        r.fetch_time = time.perf_counter() - t_start
        return r

    match = re.search(r";; Successful DNS Server:\s*(.+)$", r.dns_raw, re.MULTILINE)
    r.dns_server_used = match.group(1).strip() if match else DNS_OPTIONS.get(dns_profile, ["49.45.0.1"])[0]
    r.resolved_ips  = all_ips
    r.resolved_ipv4 = ipv4_list
    r.resolved_ipv6 = ipv6_list
    r.synthetic_ipv6 = synth_v6
    r.primary_ip    = all_ips[0] if all_ips else "0.0.0.0"

    # Hard-coded block rule check
    if "49.44.79.236" in r.resolved_ipv4 and "2405:200:1607:2820:41::36" in r.resolved_ipv6:
        r.health = "BLOCKED"
        r.invalid_reason = "Hardcoded Block Rule matched"

    # Jump server verification
    r.steps_status["jump"] = "run"
    r.jump_raw = connect_jump_server(r.primary_ip)
    r.steps_status["jump"] = "ok" if "[✓]" in r.jump_raw else "err"

    # Analyse each unique IP in parallel
    ips_to_analyse = list(dict.fromkeys(ipv4_list + ipv6_list + synth_v6))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ip = {
            executor.submit(analyse_ip, ip, use_ibr, domain, r): ip
            for ip in ips_to_analyse
        }
        for future in concurrent.futures.as_completed(future_to_ip):
            try:
                ia = future.result()
                r.ip_analyses.append(ia)
            except Exception:
                pass

    r.ip_analyses.sort(key=lambda x: ips_to_analyse.index(x.ip) if x.ip in ips_to_analyse else 99)

    if r.ip_analyses:
        p = r.ip_analyses[0]
        r.packet_loss = p.packet_loss
        r.peer_asn    = p.peer_asn
        r.prefix      = p.prefix
        r.asn_info    = p.asn_info

    if r.health != "BLOCKED":
        errs = sum(1 for v in r.steps_status.values() if v in ("err", "warn"))
        any_degraded = any(ia.health == "degraded" for ia in r.ip_analyses)
        if errs:         r.health = "critical"
        elif any_degraded: r.health = "degraded"
        else:            r.health = "healthy"

    r.fetch_time = time.perf_counter() - t_start
    return r

# ══════════════════════════════════════════════════════════════════════
#  FILE PARSING  (unchanged)
# ══════════════════════════════════════════════════════════════════════
def parse_uploaded_file(f) -> List[str]:
    name = f.name.lower(); domains = []; raw = f.read()
    if name.endswith(".xlsx"):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
        ws = wb.active
        for row in ws.iter_rows(values_only=True):
            if row and row[0]: domains.append(str(row[0]).strip())
    elif name.endswith(".csv"):
        text = raw.decode("utf-8", "ignore"); reader = csv.reader(io.StringIO(text))
        for row in reader:
            if row and row[0].strip(): domains.append(row[0].strip())
    else:
        for line in raw.decode("utf-8", "ignore").splitlines():
            line = line.strip()
            if line and not line.startswith("#"): domains.append(line)
    cleaned = []; seen = set()
    for d in domains:
        d = re.sub(r"^https?://", "", d).lower().strip()
        d = d.split("/")[0].split("?")[0].split("#")[0].strip()
        if d and d not in seen: seen.add(d); cleaned.append(d)
    return cleaned

# ══════════════════════════════════════════════════════════════════════
#  EXPORT  (unchanged)
# ══════════════════════════════════════════════════════════════════════
def export_json(reports: list) -> str:
    out = []
    for r in reports:
        ip_list = []
        for ia in r.ip_analyses:
            ip_list.append({
                "ip": ia.ip, "ip_version": ia.ip_version,
                "is_nat64_synthetic": ia.is_synthetic_v6,
                "packet_loss_pct": ia.packet_loss,
                "hops": len(ia.hops),
                "peer_asn": ia.peer_asn, "prefix": ia.prefix,
                "asn_org": ia.asn_info.org if ia.asn_info else "",
                "irr_valid": ia.asn_info.irr_valid if ia.asn_info else None,
                "bottleneck_hop": ia.bottleneck_hop,
            })
        out.append({
            "domain": r.domain, "timestamp": r.timestamp,
            "valid": r.valid, "invalid_reason": r.invalid_reason,
            "dns_profile": r.dns_profile, "dns_server": r.dns_server_used,
            "resolved_ips": r.resolved_ips, "resolved_ipv4": r.resolved_ipv4,
            "resolved_ipv6": r.resolved_ipv6, "synthetic_ipv6": r.synthetic_ipv6,
            "ip_analyses": ip_list,
        })
    return json.dumps(out, indent=2)

def export_csv(reports: list) -> str:
    buf = io.StringIO(); w = csv.writer(buf)
    w.writerow(["Domain","Timestamp","Valid","DNS Profile","DNS Server","IP","IPVersion",
                "NAT64Synthetic","Pckt. Loss%","Hops","BottleneckHop","PeerASN","Prefix","Org","IRR"])
    for r in reports:
        if not r.ip_analyses:
            w.writerow([r.domain, r.timestamp, r.valid, r.dns_profile, r.dns_server_used,
                        "", "", "", 100, 0, 0, 0, "", "", ""])
        for ia in r.ip_analyses:
            w.writerow([r.domain, r.timestamp, r.valid, r.dns_profile, r.dns_server_used,
                        ia.ip, ia.ip_version, ia.is_synthetic_v6, ia.packet_loss,
                        len(ia.hops), ia.bottleneck_hop, ia.peer_asn, ia.prefix,
                        ia.asn_info.org if ia.asn_info else "",
                        ia.asn_info.irr_valid if ia.asn_info else ""])
    return buf.getvalue()

# ══════════════════════════════════════════════════════════════════════
#  UI RENDERING  (identical to dev build)
# ══════════════════════════════════════════════════════════════════════
def get_health_badge(health, reason="", valid=True):
    if health == "BLOCKED":
        return ('<span class="badge b-err" style="display:block;width:100%;text-align:center;'
                'box-sizing:border-box;height:26px;line-height:18px;background:#000;'
                'color:#dc3545;border:1px solid #dc3545;">BLOCKED</span>')
    elif not valid:
        err_msg = reason if reason else "Connectivity Error"
        return (f'<select class="badge b-err" style="outline:none;cursor:pointer;width:100%;'
                f'display:block;box-sizing:border-box;text-align:center;padding:0px 0.4rem;'
                f'height:26px;line-height:26px;font-size:0.8rem;">'
                f'<option>Unsuccessful</option><option disabled>↳ {err_msg}</option></select>')
    else:
        return ('<span class="badge b-ok" style="display:block;width:100%;text-align:center;'
                'box-sizing:border-box;height:26px;line-height:18px;">Successful</span>')

def _pip(icon, label, sub, status):
    css  = {"ok":"done","warn":"warn","err":"err","skip":"skip","pending":"pending","run":"run"}.get(status,"pending")
    bmap = {"ok":("pb-done","✓"),"warn":("pb-done","⚠"),"err":("pb-err","✗ ERR"),
            "skip":("pb-skip","⊘"),"pending":("pb-skip","⋯ WAIT"),"run":("pb-run","⟳")}
    bc, bt = bmap.get(status, ("pb-skip","⋯ WAIT"))
    ts = "opacity: 0.6;" if status == "ok" else ""
    return (f'<div class="pip-step {css}"><span class="pip-icon">{icon}</span>'
            f'<span class="pip-text"><div class="pip-label" style="{ts}">{label}</div>'
            f'<div class="pip-sub" style="{ts}">{sub}</div></span>'
            f'<span class="pip-badge {bc}">{bt}</span></div>')

def get_pipeline_html(r: SiteReport) -> str:
    s = r.steps_status
    html = '<div class="pipeline">'
    html += _pip("🔍", "DNS Resolution",   f"dnspython → {r.dns_profile} [INTERNAL]",  s.get("dns","pending"))
    html += _pip("📡", "ICMP/TCP Ping",    "Real reachability & latency",               s.get("ping","pending"))
    html += _pip("🔀", "Live Traceroute",  "ICMP TTL + TCP probe (per IP)",             s.get("traceroute","pending"))
    html += _pip("🖥️", "JIO IBR SSH",      f"paramiko → {IBR_IP}:{SSH_PORT}",           s.get("ibr","pending"))
    html += _pip("🗺️", "BGP Intelligence", "IBR SSH parse + Local ASN DB",              s.get("bgp","pending"))
    html += _pip("🌍", "ASN / IRR",        "Local DB · no internet required",           s.get("asn","pending"))
    html += '</div>'
    return html

def render_bgp_for_ip(ia: IPAnalysis):
    if not ia.peer_asn: return
    org   = ia.asn_info.org if ia.asn_info else f"AS{ia.peer_asn}"
    rir   = ia.asn_info.rir if ia.asn_info else "?"
    irrc  = "#1e7e34" if ia.asn_info and ia.asn_info.irr_valid else "#d39e00"
    st.markdown(f"""
<div class="panel">
  <div class="panel-hdr">🗺️ &nbsp;BGP INTELLIGENCE — {ia.ip}</div>
  <div class="panel-body" style="line-height:1.8;">
    <span style="opacity:0.7;">ASN:</span> <span style="font-weight:800;color:#0B58C6;">AS55836 IN</span> &nbsp;
    <span style="background:rgba(11,88,198,0.1);color:#0B58C6;font-size:0.75rem;padding:0.15rem 0.4rem;border-radius:4px;font-weight:bold;">JIO NETWORK</span><br>
    <span style="opacity:0.7;">Org:</span> <span style="font-weight:800;color:var(--text-color);">Reliance JIO</span><br>
    <span style="opacity:0.7;display:block;margin:0.2rem 0;">↓</span>
    <span style="opacity:0.7;">ASN:</span> <span style="font-weight:800;color:#0B58C6;">AS{ia.peer_asn}</span> &nbsp;
    <span style="background:rgba(128,128,128,0.1);color:gray;font-size:0.75rem;padding:0.15rem 0.4rem;border-radius:4px;font-weight:bold;">{rir}</span><br>
    <span style="opacity:0.7;">Org:</span> <span style="font-weight:800;color:var(--text-color);">{org}</span><br><br>
    <span style="opacity:0.7;">Prefix:</span> <span style="font-weight:800;color:var(--text-color);">{ia.prefix}</span> &nbsp;
    <span style="opacity:0.7;">Next Hop:</span> <span style="font-weight:800;color:var(--text-color);">{ia.next_hop}</span> &nbsp;
    <span style="opacity:0.7;">LP:</span> <span style="font-weight:800;color:var(--text-color);">{ia.local_pref}</span><br>
    <span style="opacity:0.7;">IRR:</span> <span style="font-weight:900;color:{irrc};">{"✓ Valid" if ia.asn_info and ia.asn_info.irr_valid else "⚠ Not in local DB"}</span>
  </div>
</div>""", unsafe_allow_html=True)

def render_asn_for_ip(ia: IPAnalysis):
    if not ia.asn_info: return
    ai   = ia.asn_info
    irrc = "#1e7e34" if ai.irr_valid else "#d39e00"
    rpki_color = "#1e7e34" if ai.rpki == "Valid" else "#d39e00" if ai.rpki == "Unknown" else "#dc3545"
    routes_str = f"{ai.num_routes:,}" if ai.num_routes else "N/A (from IBR)"
    peers_str  = str(ai.num_peers) if ai.num_peers else "N/A (from IBR)"
    st.markdown(f"""
<div class="panel">
  <div class="panel-hdr">🌍 &nbsp;AS{ai.asn} — {ai.org}
    <span style="margin-left:auto;font-size:0.75rem;color:gray;font-weight:normal;">IBR SSH + Local ASN DB</span>
  </div>
  <div class="panel-body" style="line-height:1.8;">
    <span style="opacity:0.7;">Handle:</span> <span style="font-weight:800;color:#0B58C6;">{ai.handle}</span><br>
    <span style="opacity:0.7;">Country:</span> <span style="font-weight:800;color:var(--text-color);">{ai.country}</span> &nbsp;
    <span style="opacity:0.7;">RIR:</span> <span style="font-weight:800;color:var(--text-color);">{ai.rir}</span><br>
    <span style="opacity:0.7;">Prefixes:</span> <span style="font-weight:800;color:var(--text-color);">{routes_str}</span> &nbsp;
    <span style="opacity:0.7;">Peers:</span> <span style="font-weight:800;color:var(--text-color);">{peers_str}</span><br>
    <span style="opacity:0.7;">IRR:</span> <span style="font-weight:900;color:{irrc};">{'✓ Valid' if ai.irr_valid else '⚠ Not in local DB'}</span> &nbsp;
    <span style="opacity:0.7;">RPKI:</span> <span style="font-weight:900;color:{rpki_color};">{ai.rpki}</span>
  </div>
</div>""", unsafe_allow_html=True)

def render_hop_table_for_ip(ia: IPAnalysis):
    rows = ""
    for h in ia.hops[:30]:
        ac  = " hop-anomaly" if h.is_anomaly else ""
        ann = (f' <span style="color:#b07d00;font-size:0.8rem;font-weight:bold;">{h.anomaly_reason}</span>'
               if h.is_anomaly else "")
        lat_str = f"{h.latency_ms:.1f} ms" if h.latency_ms > 0 else "*"
        rows += (f'<tr class="{ac}"><td style="opacity:0.7;text-align:center;">{h.num}</td>'
                 f'<td style="font-weight:700;">{h.ip}</td>'
                 f'<td style="opacity:0.8;">{h.hostname}{ann}</td>'
                 f'<td style="font-weight:700;">{lat_str}</td>'
                 f'<td style="opacity:0.6;">{h.network}</td></tr>')
    limited_hops = ia.hops[:30]
    with st.expander(f"🔀 TRACEROUTE — {ia.ip} — {len(limited_hops)} HOPS", expanded=True):
        st.markdown(f'''
        <table class="hop-table">
          <thead><tr>
            <th style="text-align:center;width:5%;">#</th>
            <th style="width:20%;">IP</th><th style="width:40%;">HOSTNAME</th>
            <th style="width:15%;">MIN. LATENCY</th><th style="width:20%;">ASN</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>''', unsafe_allow_html=True)
        valid_hops = [h for h in limited_hops if h.latency_ms > 0]
        if valid_hops:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[f"Hop {h.num}" for h in valid_hops],
                y=[h.latency_ms for h in valid_hops],
                mode="lines+markers",
                marker=dict(size=8, color="#0B58C6"),
                line=dict(color="#0B58C6", width=2),
                text=[f"IP: {h.ip}<br>Host: {h.hostname}" for h in valid_hops],
                hoverinfo="text+y"
            ))
            fig.update_layout(
                title="Hop Latency Trend", xaxis_title="Hop Number", yaxis_title="Latency (ms)",
                margin=dict(l=20, r=20, t=40, b=20), height=300,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

def render_ip_drilldown(r: SiteReport, use_ibr: bool):
    if not r.ip_analyses: return
    v4_ips  = [ia for ia in r.ip_analyses if ia.ip_version == 4 and not ia.is_synthetic_v6]
    v6_ips  = [ia for ia in r.ip_analyses if ia.ip_version == 6 and not ia.is_synthetic_v6]
    syn_ips = [ia for ia in r.ip_analyses if ia.is_synthetic_v6]
    tab_names = ["IPv4"]
    if v6_ips: tab_names.append("IPv6")
    tab_names.append("Synthetic IPv6")
    tabs = st.tabs(tab_names)

    def render_ia_list(ia_list):
        if not ia_list: return
        ip_tabs = st.tabs([ia.ip for ia in ia_list])
        for tab, ia in zip(ip_tabs, ia_list):
            with tab:
                loc = "#d39e00" if ia.packet_loss > 0 else "#1e7e34"
                syn_tag = ""
                if ia.is_synthetic_v6:
                    syn_tag = '<span style="background:rgba(128,128,128,0.1);color:#4b5563;font-size:0.85rem;font-weight:800;padding:0.4rem 0.8rem;border-radius:6px;font-family:\'JetBrains Mono\',monospace;">NAT64 SYNTHETIC</span>'
                elif ia.ip_version == 6:
                    syn_tag = '<span style="background:rgba(0,123,255,0.1);color:#0B58C6;font-size:0.85rem;font-weight:800;padding:0.4rem 0.8rem;border-radius:6px;font-family:\'JetBrains Mono\',monospace;">NATIVE IPv6</span>'
                status_tag = ""
                if not ia.ping_ok:
                    status_tag = (f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.95rem;'
                                  f'background:var(--secondary-background-color);border:1px solid rgba(0,0,0,0.1);'
                                  f'border-radius:6px;padding:0.4rem 0.8rem;">'
                                  f'<span style="opacity:0.7;font-weight:700;">STATUS</span>&nbsp;'
                                  f'<span style="color:#d39e00;font-weight:900;">⚠ Unsuccessful</span></span>')
                st.markdown(f"""
<div style="display:flex;gap:0.75rem;margin-bottom:1rem;flex-wrap:wrap;align-items:center;">
  {syn_tag}{status_tag}
  <span style="font-family:'JetBrains Mono',monospace;font-size:0.95rem;background:var(--secondary-background-color);border:1px solid rgba(0,0,0,0.1);border-radius:6px;padding:0.4rem 0.8rem;">
    <span style="opacity:0.7;font-weight:700;">PCKT. LOSS</span>&nbsp;
    <span style="color:{loc};font-weight:900;">{ia.packet_loss:.0f}%</span></span>
</div>""", unsafe_allow_html=True)
                render_hop_table_for_ip(ia)
                if use_ibr or ia.asn_info:
                    c1, c2 = st.columns(2, gap="large")
                    with c1: render_bgp_for_ip(ia)
                    with c2: render_asn_for_ip(ia)

    with tabs[0]: render_ia_list(v4_ips)
    if v6_ips:
        with tabs[1]: render_ia_list(v6_ips)
        with tabs[2]: render_ia_list(syn_ips)
    else:
        with tabs[1]: render_ia_list(syn_ips)

def render_detail_panel(r: SiteReport, use_ibr: bool):
    inv_tag = ""
    if not r.valid:
        inv_tag = f' <span class="badge b-err">NX DOMAIN — {r.invalid_reason}</span>'
    st.markdown(
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.95rem;font-weight:bold;'
        f'color:var(--text-color);letter-spacing:1px;margin-bottom:1rem;">'
        f'◈ DETAILS — <span style="color:#0B58C6;">{r.domain}</span>'
        f' &nbsp;{get_health_badge(r.health, getattr(r,"invalid_reason",""), r.valid)}{inv_tag}'
        f' <span style="font-size:0.8rem;color:#6b7280;font-weight:normal;margin-left:1rem;">'
        f'(Fetch Time: {r.fetch_time:.2f}s)</span></div>',
        unsafe_allow_html=True
    )
    left, right = st.columns([1.4, 2.6], gap="large")
    with left:
        with st.expander("🔍 DNS Raw Output"): st.code(r.dns_raw, language="text")
        if r.ip_analyses:
            with st.expander("🖥️ Raw Terminal Output"):
                ip_tabs_ui = st.tabs([ia.ip for ia in r.ip_analyses])
                for tab, ia in zip(ip_tabs_ui, r.ip_analyses):
                    with tab:
                        rt = st.tabs(["Ping", "IBR SSH", "BGP + ASN"])
                        for t, c in zip(rt, [ia.ping_raw, ia.ibr_raw, ia.bgp_raw]):
                            with t: st.code(c or "(skipped)", language="text")
        if r.jump_raw:
            with st.expander("💻 Jump Server SSH Raw"): st.code(r.jump_raw, language="text")
    with right:
        if not r.valid:
            st.markdown(f"""
<div style="background:rgba(220,53,69,0.05);border:1px solid rgba(220,53,69,0.3);border-radius:8px;
  padding:1.5rem;font-family:'JetBrains Mono',monospace;font-size:1rem;color:#c82333;line-height:1.8;">
  <div style="font-size:1.2rem;font-weight:800;margin-bottom:0.8rem;">⛔ DOMAIN HALTED — NXDOMAIN</div>
  <div>Domain: <b>{r.domain}</b></div>
  <div>Reason: <b>{r.invalid_reason}</b></div>
  <div style="margin-top:1rem;opacity:0.8;font-weight:600;">No ping, traceroute, BGP or ASN analysis performed.</div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="slabel">Per-IP Drilldown — Select IP Tab</div>', unsafe_allow_html=True)
            render_ip_drilldown(r, use_ibr)

# ══════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════
def main():
    for k, v in [("reports", []), ("selected", None), ("use_ibr", True),
                 ("dns_profile", "LTE/Mobility"), ("ip_pref", "Both")]:
        if k not in st.session_state: st.session_state[k] = v

    st.markdown(f"""
<div class="hdr">
  <div class="hdr-logo">
    <div class="hdr-jio">JIO</div>
    <div>
      <div class="hdr-title">Internal ISOC Dashboard — NETWORK EDITION</div>
      <div class="hdr-sub">PRODUCTION BUILD · AIR-GAPPED · ALL DATA VIA INTERNAL INFRA</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    input_tab, upload_tab = st.tabs(["✏️  Manual Input", "📡  Upload File (.txt / .csv / .xlsx)"])
    domains_from_input = []

    with input_tab:
        st.markdown("<br>", unsafe_allow_html=True)
        c_area, _ = st.columns([3, 1], gap="large")
        with c_area: raw = st.text_area("urls", label_visibility="collapsed", height=150)

        dns_cols = st.columns([2, 3])
        with dns_cols[0]:
            st.markdown('<div class="slabel">◈ Select DNS (Internal JIO Only)</div>', unsafe_allow_html=True)
            dns_sel = st.selectbox("dns_profile", DNS_LABELS,
                                   index=DNS_LABELS.index(st.session_state.dns_profile)
                                         if st.session_state.dns_profile in DNS_LABELS else 0,
                                   label_visibility="collapsed", key="dns_sel_manual")
            st.session_state.dns_profile = dns_sel
        with dns_cols[1]:
            srv_str = "  |  ".join(DNS_OPTIONS[dns_sel])
            st.markdown(f"""<div style="margin-top:1.8rem;font-family:'JetBrains Mono',monospace;font-size:0.95rem;font-weight:600;background:var(--secondary-background-color);border:1px solid rgba(0,0,0,0.1);border-radius:6px;padding:0.6rem 1rem;color:#0B58C6;">{srv_str}</div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        btn_col, ibr_col = st.columns([4, 1], gap="medium")
        with btn_col: run_manual = st.button("▶▶  RUN", key="run_manual", use_container_width=True)
        with ibr_col:
            st.markdown("<div style='margin-top: 0.8rem;'>", unsafe_allow_html=True)
            use_ibr = st.checkbox("IBR checks (BGP/ASN)", value=True, key="ibr_man")
            st.session_state.use_ibr = use_ibr
            st.markdown("</div>", unsafe_allow_html=True)

        if run_manual and raw.strip():
            seen = set(); domains_from_input = []
            for line in raw.strip().splitlines():
                d = re.sub(r"^https?://", "", line.strip().lower())
                d = d.split("/")[0].split("?")[0].split("#")[0].strip()
                if d and d not in seen: seen.add(d); domains_from_input.append(d)

    with upload_tab:
        st.markdown("<br>", unsafe_allow_html=True)
        u_left, _ = st.columns([3, 1], gap="large")
        with u_left:
            uploaded = st.file_uploader("Drop file", label_visibility="collapsed",
                                        type=["txt","csv","xlsx"],
                                        help="One domain per line (txt), first column (csv/xlsx). Max 100.")
        dns_cols2 = st.columns([2, 3])
        with dns_cols2[0]:
            st.markdown('<div class="slabel">◈ Select DNS (Internal JIO Only)</div>', unsafe_allow_html=True)
            dns_sel2 = st.selectbox("dns_profile_up", DNS_LABELS,
                                    index=DNS_LABELS.index(st.session_state.dns_profile)
                                          if st.session_state.dns_profile in DNS_LABELS else 0,
                                    label_visibility="collapsed", key="dns_sel_upload")
        with dns_cols2[1]:
            srv_str2 = "  |  ".join(DNS_OPTIONS[dns_sel2])
            st.markdown(f"""<div style="margin-top:1.8rem;font-family:'JetBrains Mono',monospace;font-size:0.95rem;font-weight:600;background:var(--secondary-background-color);border:1px solid rgba(0,0,0,0.1);border-radius:6px;padding:0.6rem 1rem;color:#0B58C6;">{srv_str2}</div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        btn_col2, ibr_col2 = st.columns([4, 1], gap="medium")
        with btn_col2: run_upload = st.button("▶▶  RUN", key="run_upload", use_container_width=True)
        with ibr_col2:
            st.markdown("<div style='margin-top: 0.8rem;'>", unsafe_allow_html=True)
            use_ibr_up = st.checkbox("IBR checks (BGP/ASN)", value=True, key="ibr_up")
            st.markdown("</div>", unsafe_allow_html=True)

        if run_upload and uploaded:
            domains_from_input = parse_uploaded_file(uploaded)
            st.session_state.use_ibr = use_ibr_up
            st.session_state.dns_profile = dns_sel2

    trigger = domains_from_input[:100]
    if trigger:
        st.session_state.reports = [
            SiteReport(domain=d, dns_profile=st.session_state.dns_profile) for d in trigger
        ]
        st.session_state.selected = None
        total_domains = len(trigger)
        completed = 0

        prog_col, stop_col = st.columns([82, 18])
        with prog_col:
            bar = st.progress(0, text=f"ISOC Analysis Initializing: {total_domains} domain(s)...")
            live_ph = st.empty()
        with stop_col:
            if st.button("🛑 STOP", key="stop_triage", use_container_width=True): st.stop()

        def update_ui():
            if st.session_state.reports:
                active_r = next(
                    (r for r in st.session_state.reports
                     if any(s in ("pending","run") for s in r.steps_status.values())),
                    st.session_state.reports[-1]
                )
                pct    = int((completed / total_domains) * 100) if total_domains > 0 else 0
                header = (f"<div style='margin-bottom:0.8rem;font-family:\"JetBrains Mono\",monospace;"
                          f"font-size:0.85rem;font-weight:bold;color:#4f46e5;text-align:center;'>"
                          f"Analysis IN PROGRESS: <span style='color:#1e293b'>{active_r.domain}</span></div>")
                sync_html = f"<div id='live-pipeline-sync-source' style='display:none;'>{header}{get_pipeline_html(active_r)}</div>"
                live_ph.markdown(sync_html, unsafe_allow_html=True)
                bar.progress(pct, text=f"Processing {active_r.domain} ({pct}%)")

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, total_domains)) as executor:
            future_to_domain = {
                executor.submit(analyse_domain, r, st.session_state.use_ibr,
                                st.session_state.dns_profile, st.session_state.ip_pref): r
                for r in st.session_state.reports
            }
            while True:
                completed = sum(1 for f in future_to_domain if f.done())
                update_ui()
                if completed == len(future_to_domain): break
                time.sleep(0.1)

        bar.progress(100, text=f"✓ ISOC Analysis Complete — {total_domains} domain(s) processed!")

        for f in future_to_domain:
            try: f.result()
            except Exception as e:
                r = future_to_domain[f]
                r.valid = False; r.invalid_reason = f"Execution Error: {e}"; r.health = "critical"

        st.session_state.reports.sort(key=lambda x: trigger.index(x.domain) if x.domain in trigger else 99)
        if st.session_state.reports: st.session_state.selected = st.session_state.reports[0].domain
        st.rerun()

    reports = st.session_state.reports
    if not reports:
        st.markdown("""
<div style="text-align:center;padding:8rem 2rem;opacity:0.4;">
  <div style="font-size:4rem;">🛡️</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;font-weight:700;letter-spacing:2px;margin-top:1.5rem;color:#4b5563;">
    ENTER DOMAINS TO INITIATE ANALYSIS
  </div>
  <div style="font-size:0.8rem;margin-top:0.8rem;color:#9ca3af;">Production build · Air-gapped · Internal DNS only</div>
</div>""", unsafe_allow_html=True)
        return

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    ec1, ec2, _ = st.columns([1, 1, 5])
    with ec1: st.download_button("⬇ Export JSON", export_json(reports),
                                 "jio_isoc_prod_report.json", "application/json", use_container_width=True)
    with ec2: st.download_button("⬇ Export CSV", export_csv(reports),
                                 "jio_isoc_prod_report.csv", "text/csv", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    wn_c        = sum(1 for r in reports if r.health == "degraded")
    inv_c       = sum(1 for r in reports if not r.valid)
    total_ips   = sum(len(r.ip_analyses) for r in reports)
    total_v6    = sum(len(r.resolved_ipv6) for r in reports)
    total_nat64 = sum(len(r.synthetic_ipv6) for r in reports)
    active_dns  = reports[0].dns_profile if reports else "—"
    st.markdown(f"""
<div class="mini-stats">
  <div class="mini-stat"><div class="ms-lbl">DOMAINS</div><div class="ms-num">{len(reports)}</div></div>
  <div class="mini-stat"><div class="ms-lbl" style="text-transform:none;">IPs Fetched</div><div class="ms-num">{total_ips}</div></div>
  <div class="mini-stat"><div class="ms-lbl">IPv6 NATIVE</div><div class="ms-num" style="color:var(--text-color);">{total_v6}</div></div>
  <div class="mini-stat"><div class="ms-lbl">NAT64 SYNTH</div><div class="ms-num" style="color:var(--text-color);">{total_nat64}</div></div>
  <div class="mini-stat"><div class="ms-lbl">ServFail</div><div class="ms-num" style="color:#d39e00">{wn_c}</div></div>
  <div class="mini-stat"><div class="ms-lbl">NX DOMAIN</div><div class="ms-num" style="color:#c82333">{inv_c}</div></div>
  <div class="mini-stat"><div class="ms-lbl">SELECT DNS</div><div class="ms-num" style="font-size:0.95rem;color:#0B58C6;padding-top:0.3rem;">{active_dns}</div></div>
</div>""", unsafe_allow_html=True)

    st.markdown('<br><div class="slabel">◈ Results </div>', unsafe_allow_html=True)
    COL_WIDTHX = '<colgroup><col style="width:4%;"><col style="width:18%;"><col style="width:6%;"><col style="width:14%;"><col style="width:14%;"><col style="width:10%;"><col style="width:14%;"><col style="width:20%;"></colgroup>'

    h_col1, h_col2 = st.columns([12, 1], gap="medium")
    with h_col1:
        st.markdown(
            f'<table class="rtbl" style="margin-bottom:0px;">{COL_WIDTHX}'
            f'<tr><th>#</th><th>DOMAIN</th><th>IPs</th><th>PRIMARY IP</th>'
            f'<th>DNS</th><th>PCKT. LOSS</th><th>ASN</th><th>QUERY STATUS</th></tr></table>',
            unsafe_allow_html=True
        )
    with h_col2:
        st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.8rem;color:#4b5563;font-weight:800;text-align:center;letter-spacing:1px;height:36px;line-height:36px;">VIEW</div>', unsafe_allow_html=True)

    for i, r in enumerate(reports, 1):
        is_sel = st.session_state.selected == r.domain
        if not r.valid:
            loc = "#6c757d"; loss_str = "N/A"; asn_str = "—"
        else:
            loc = "#d39e00" if r.packet_loss > 0 else "#1e7e34"
            loss_str = f"{r.packet_loss:.0f}%"
            asn_str  = f"AS{r.peer_asn}" if r.peer_asn else "AS—"
        sel_cls  = " sel" if is_sel else ""
        dom_cls  = "domain-cell" if r.valid else "domain-cell invalid-domain"
        ip_badge = (f'<span class="ip-count-chip">{len(r.resolved_ips)} IPs</span>'
                    if len(r.resolved_ips) > 1 else ("1 IP" if r.resolved_ips else "—"))
        inv_marker = " ⛔" if not r.valid else ""

        r_col1, r_col2 = st.columns([12, 1], gap="medium")
        with r_col1:
            st.markdown(
                f'<table class="rtbl" style="margin-bottom:0px;">{COL_WIDTHX}'
                f'<tr class="{sel_cls}"><td style="opacity:0.7;font-weight:700;">{i}</td>'
                f'<td class="{dom_cls}">{r.domain}{inv_marker}</td><td>{ip_badge}</td>'
                f'<td style="font-weight:700;">{r.primary_ip or "—"}</td>'
                f'<td style="color:#0B58C6;font-size:0.9rem;font-weight:800;">{r.dns_profile}</td>'
                f'<td style="color:{loc};font-weight:800;">{loss_str}</td>'
                f'<td style="font-weight:700;opacity:0.8;">{asn_str}</td>'
                f'<td>{get_health_badge(r.health, getattr(r,"invalid_reason",""), r.valid)}</td></tr></table>',
                unsafe_allow_html=True
            )
        with r_col2:
            if st.button(f"{'▼' if is_sel else '▶'}", key=f"sel_{i}_{r.domain}", use_container_width=True):
                st.session_state.selected = None if is_sel else r.domain
                st.rerun()

        if is_sel:
            header = (f"<div style='margin-bottom:0.8rem;font-family:\"JetBrains Mono\",monospace;"
                      f"font-size:0.85rem;font-weight:bold;color:#4f46e5;text-align:center;'>"
                      f"Analysis: <span style='color:#1e293b'>{r.domain}</span></div>")
            st.markdown(
                f"<div id='live-pipeline-sync-source' style='display:none;'>{header}{get_pipeline_html(r)}</div>",
                unsafe_allow_html=True
            )
            with st.container():
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                render_detail_panel(r, st.session_state.use_ibr)
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
