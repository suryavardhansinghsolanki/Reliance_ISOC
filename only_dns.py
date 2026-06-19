# JIO ISOC Dashboard v6.4 — DNS EDITION ONLY
# ===================================================
# pip install streamlit plotly openpyxl dnspython ipwhois paramiko
# streamlit run isoc_dns_only.py

import streamlit as st
import socket, json, csv, io, re, math, struct, time, random
import subprocess, platform, threading, os, functools
import concurrent.futures
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
import urllib.request

try:
    import dns.resolver
    import dns.rdatatype
    import dns.exception
    HAS_DNSPY = True
except ImportError:
    HAS_DNSPY = False

import streamlit.components.v1 as components
import plotly.graph_objects as go 

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG & INJECTOR
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title="JIO ISOC DNS Dashboard", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

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

# ══════════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════════
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "pass"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("""
    <style>
    .stApp { background-color: #f8fafc !important; }
    [data-testid="stHeader"] { background: transparent; }
    footer { visibility: hidden; }
    div[data-testid="stVerticalBlock"] > div:has(.brand-wrap) {
        background-color: #ffffff !important; border: 1px solid #e2e8f0 !important;
        border-top: 4px solid #e31837 !important; border-radius: 16px !important;
        padding: 3rem 2.5rem !important; box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.05) !important;
    }
    div.stTextInput input { border-radius: 8px !important; border: 1px solid #cbd5e1 !important; padding: 0.6rem 1rem !important; }
    div.stButton > button { background: #0f3cc9 !important; color: #ffffff !important; border-radius: 8px !important; font-weight: 700 !important; width: 100% !important; }
    .brand-wrap { text-align: center; margin-bottom: 1.5rem; }
    .brand-logo { font-size: 2.5rem; font-weight: 800; color: #0f3cc9; letter-spacing: -1.5px; }
    .brand-title { font-size: 1.15rem; font-weight: 700; color: #0f172a; }
    </style>
    """, unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 3, 1])
    with center_col:
        st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
        st.markdown("""<div class="brand-wrap"><div class="brand-logo">JIO</div><div class="brand-title">ISOC DNS Dashboard</div></div>""", unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        if st.button("Login", use_container_width=True):
            if username == LOGIN_USERNAME and password == LOGIN_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")
    st.stop() 

with st.sidebar:
    st.markdown("### 🛡️ JIO ISOC DNS")
    if st.button("🔒 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun() 

# ══════════════════════════════════════════════════════════════
#  DNS CONFIG
# ══════════════════════════════════════════════════════════════
DNS_OPTIONS: Dict[str, list] = {
    "5G/Sub6":               ["2405:200:800::11"],
    "LTE/Mobility":          ["49.45.0.1", "2405:200:800::1"], 
    "FTTX/UBR":              ["2405:200:800::3", "49.45.0.3"],
    "Enterprise":            ["2405:200:800::4", "49.45.0.4"],
    "Google DNS (IPv4)":     ["8.8.8.8", "8.8.4.4"],
    "Google DNS (IPv6)":     ["2001:4860:4860::8888", "2001:4860:4860::8844"],
    "Cloudflare DNS (IPv4)": ["1.1.1.1", "1.0.0.1"],
    "Cloudflare DNS (IPv6)": ["2606:4700:4700::1111", "2606:4700:4700::1001"],
}
DNS_LABELS = list(DNS_OPTIONS.keys())
NAT64_PREFIX = "64:ff9b::"

# ══════════════════════════════════════════════════════════════
#  CSS  
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
.main .block-container { padding: 2rem 2rem 4rem; max-width: 1600px; }
.hdr { background: var(--secondary-background-color); border: 1px solid rgba(0, 86, 179, 0.15); border-top: 5px solid #0B58C6; border-radius: 10px; padding: 1.5rem 2rem; display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem; }
.hdr-logo { display: flex; align-items: center; gap: 1rem; }
.hdr-jio { font-size: 2.5rem; font-weight: 900; color: #0B58C6; letter-spacing: -1px; line-height: 1; }
.hdr-title { font-size: 1.25rem; font-weight: 800; color: var(--text-color); }
div.stButton > button { background: #0B58C6 !important; color: #ffffff !important; font-weight: 700 !important; border-radius: 6px !important; }
.badge { display: inline-block; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: 800; }
.b-ok   { background: rgba(40, 167, 69, 0.15); color: #1e7e34; border: 1px solid rgba(40, 167, 69, 0.3); }
.b-err  { background: rgba(220, 53, 69, 0.15); color: #c82333; border: 1px solid rgba(220, 53, 69, 0.3); }
.pipeline { display: flex; flex-direction: column; gap: 6px; }
.pip-step { display: flex; align-items: center; gap: 0.8rem; padding: 0.6rem 1rem; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); background: var(--secondary-background-color); font-size: 0.85rem; }
.pip-step.done { border-color: rgba(40,167,69,0.5); background: rgba(40,167,69,0.08); }
.pip-step.skip { border-color: rgba(128,128,128,0.3); opacity: 0.5; }
.pip-icon { font-size: 1.1rem; width: 20px; text-align: center; }
.pip-text { flex: 1; }
.pip-label { font-weight: 700; font-size: 0.9rem; }
.pip-badge { font-size: 0.75rem; font-weight: 800; padding: 0.2rem 0.5rem; border-radius: 4px; }
.pb-done { background: rgba(40,167,69,0.2); color: #1e7e34; }
.pb-skip { background: rgba(128,128,128,0.2); color: #6c757d; }
.mini-stats { display: flex; gap: 0.8rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.mini-stat { background: var(--secondary-background-color); border: 1px solid rgba(0,0,0,0.08); border-radius: 8px; padding: 1rem 0.5rem; flex: 1; min-width: 90px; text-align: center; }
.ms-lbl { font-size: 0.7rem; color: #6b7280; font-weight: 800; margin-bottom: 6px; }
.ms-num { font-size: 1.5rem; font-weight: 900; color: #0B58C6; }
.rtbl { width: 100%; border-collapse: separate; border-spacing: 0 4px; font-size: 0.85rem; text-align: left; }
.rtbl th { color: #6b7280; padding: 0.5rem 0.8rem; }
.rtbl td { padding: 0.6rem 0.8rem; background: var(--secondary-background-color); border-top: 1px solid rgba(0,0,0,0.05); border-bottom: 1px solid rgba(0,0,0,0.05); }
.rtbl tr.sel td { background: rgba(11, 88, 198, 0.05); border-color: #0B58C6; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DATA CLASSES
# ══════════════════════════════════════════════════════════════
@dataclass
class IPAnalysis:
    ip: str
    ip_version: int = 4
    is_synthetic_v6: bool = False
    health: str = "healthy"

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
    ip_analyses: List[IPAnalysis] = field(default_factory=list)
    health: str = "healthy"
    steps_status: dict = field(default_factory=lambda: {
        "dns": "pending", "ping": "skip", "traceroute": "skip",
        "ibr": "skip", "bgp": "skip", "asn": "skip", "jump": "skip"
    })
    dns_server_used: str = "8.8.8.8"
    dns_profile: str = "Google DNS (IPv4)"
    invalid_reason: str = ""

def _build_resolver(server: str, timeout: float = 3.0) -> "dns.resolver.Resolver":
    r = dns.resolver.Resolver(configure=False)
    r.nameservers = [server]
    r.timeout  = timeout
    r.lifetime = timeout + 1.0
    return r

def _ipv4_to_nat64(ipv4: str) -> str:
    try:
        parts = ipv4.split(".")
        a, b, c, d = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
        hi = (a << 8) | b
        lo = (c << 8) | d
        return f"64:ff9b::{hi:04x}:{lo:04x}"
    except Exception:
        return f"64:ff9b::0:0"

def step_dns(domain: str, dns_profile: str = "Google DNS (IPv4)", req_proto: str = "Both") -> Tuple[List[str], str, str, List[str], List[str], List[str]]:
    servers = DNS_OPTIONS.get(dns_profile, ["8.8.8.8"])
    lines = [f"; Query time: {datetime.now().strftime('%H:%M:%S UTC')}", f"; DNS Profile: {dns_profile}", ""]
    ipv4_list, ipv6_list, synth_v6 = [], [], []
    success_server = None
    confirmed_nxdomain = False

    if not HAS_DNSPY:
        lines.append("; ERROR: dnspython not installed. Cannot perform strict profile resolution.")
        return [], "\n".join(lines), "err", [], [], []

    for server in servers:
        resolver = _build_resolver(server, timeout=3.0)
        lines.append(f"$ nslookup {domain} {server}")
        server_ipv4, server_ipv6 = [], []
        try:
            if req_proto in ["Both", "IPv4"]:
                try:
                    for rr in resolver.resolve(domain, "A"): server_ipv4.append(rr.address)
                except dns.resolver.NXDOMAIN:
                    confirmed_nxdomain = True
                    break
                except Exception: pass

            if req_proto in ["Both", "IPv6"]:
                try:
                    for rr in resolver.resolve(domain, "AAAA"): server_ipv6.append(rr.address)
                except dns.resolver.NXDOMAIN:
                    confirmed_nxdomain = True
                    break
                except Exception: pass

            if server_ipv4 or server_ipv6:
                ipv4_list, ipv6_list, success_server = server_ipv4, server_ipv6, server
                break
        except dns.resolver.NXDOMAIN:
            confirmed_nxdomain = True
            break
        except Exception: continue

    if confirmed_nxdomain or (not success_server and not ipv4_list and not ipv6_list):
        lines.append(f";; NXDOMAIN/NODATA")
        return [], "\n".join(lines), "err", [], [], []

    if ipv4_list:
        lines.append(f";; ANSWER SECTION (A):")
        for ip in ipv4_list: lines.append(f"{domain}. IN A  {ip}")
    if ipv6_list:
        lines.append(f";; ANSWER SECTION (AAAA):")
        for ip in ipv6_list: lines.append(f"{domain}. IN AAAA  {ip}")

    if ipv4_list and req_proto in ["Both", "IPv6"]:
        lines.append("\n;; Synthesising NAT64 (64:ff9b::/96) from ALL IPv4 records:")
        for ip4 in ipv4_list:
            sv6 = _ipv4_to_nat64(ip4)
            if sv6 not in synth_v6: synth_v6.append(sv6)
            lines.append(f";; NAT64: {ip4}  →  {sv6}")

    all_ips = list(dict.fromkeys(ipv4_list + ipv6_list)) 
    prim = all_ips[0] if all_ips else "0.0.0.0"
    lines += ["", f";; {len(ipv4_list)} A | {len(ipv6_list)} AAAA | {len(synth_v6)} NAT64", f";; Primary → {prim}", f";; Successful DNS Server: {success_server}"]
    return all_ips, "\n".join(lines), "ok", ipv4_list, ipv6_list, synth_v6

def analyse_ip(ip: str) -> IPAnalysis:
    is_v6  = ":" in ip
    is_nat64 = ip.startswith("64:ff9b:") or ip.startswith("64:ff9b::")
    return IPAnalysis(ip=ip, ip_version=6 if is_v6 else 4, is_synthetic_v6=is_nat64)

def analyse_domain(r: SiteReport, dns_profile: str = "Google DNS (IPv4)") -> SiteReport:
    t_start = time.perf_counter()
    r.steps_status["dns"] = "run"
    all_ips, r.dns_raw, dns_st, ipv4_list, ipv6_list, synth_v6 = step_dns(r.domain, dns_profile, "Both")
    r.steps_status["dns"] = dns_st

    if dns_st == "err":
        r.valid, r.health, r.invalid_reason = False, "critical", "NXDOMAIN or Unreachable"
        r.fetch_time = time.perf_counter() - t_start
        return r

    match = re.search(r";; Successful DNS Server:\s*(.+)$", r.dns_raw, re.MULTILINE)
    r.dns_server_used = match.group(1).strip() if match else DNS_OPTIONS.get(dns_profile, ["8.8.8.8"])[0]

    r.resolved_ips, r.resolved_ipv4, r.resolved_ipv6, r.synthetic_ipv6 = all_ips, ipv4_list, ipv6_list, synth_v6
    r.primary_ip = all_ips[0] if all_ips else "0.0.0.0"

    ips_to_analyse = list(dict.fromkeys(ipv4_list + ipv6_list + synth_v6))
    for ip in ips_to_analyse:
        r.ip_analyses.append(analyse_ip(ip))

    if "49.44.79.236" in r.resolved_ipv4 and "2405:200:1607:2820:41::36" in r.resolved_ipv6:
        r.health = "BLOCKED"
        r.invalid_reason = "Hardcoded Block Rule matched"
    else:
        errs  = sum(1 for v in r.steps_status.values() if v == "err" or v == "warn")
        any_degraded = any(ia.health == "degraded" for ia in r.ip_analyses)
        if errs: r.health = "critical"
        elif any_degraded: r.health = "degraded"
        else: r.health = "healthy"

    r.fetch_time = time.perf_counter() - t_start
    return r

def get_health_badge(health, reason="", valid=True):
    # MODIFIED: Standardized base style for perfect pixel height alignment & updated Rosy Pink color
    base_style = "display: block; width: 100%; text-align: center; box-sizing: border-box; height: 32px; line-height: 20px; border-radius: 6px; font-weight: 700;"
    
    if health == "BLOCKED":
        return f'<span class="badge" style="{base_style} background: #ffe4e6; color: #e11d48; border: 1px solid #fda4af;">BLOCKED</span>'
    elif not valid:
        err_msg = reason if reason else "Connectivity Error"
        return f'<select class="badge" style="outline:none; cursor:pointer; {base_style} background: rgba(220, 53, 69, 0.15); color: #c82333; border: 1px solid rgba(220, 53, 69, 0.3); padding: 0px 0.4rem; height: 32px; line-height: 30px; font-size:0.8rem;"><option>Unsuccessful</option><option disabled>↳ {err_msg}</option></select>'
    else:
        return f'<span class="badge" style="{base_style} background: #dcfce7; color: #16a34a; border: 1px solid #86efac;">Successful</span>'

def _pip(icon, label, sub, status):
    css  = "done" if status == "ok" else "skip"
    bc, bt = ("pb-done","✓") if status == "ok" else ("pb-skip","⊘ SKIP")
    text_style = "opacity: 0.6;" if status == "ok" else "opacity: 0.5;"
    return (f'<div class="pip-step {css}"><span class="pip-icon">{icon}</span>'
            f'<span class="pip-text"><div class="pip-label" style="{text_style}">{label}</div>'
            f'<div class="pip-sub" style="{text_style}">{sub}</div></span><span class="pip-badge {bc}">{bt}</span></div>')

def get_pipeline_html(r: SiteReport) -> str:
    html = '<div class="pipeline">'
    html += _pip("🔍", "DNS Resolution", f"dnspython → {r.dns_profile}", r.steps_status.get("dns","pending"))
    html += _pip("📡", "ICMP/TCP Ping", "Disabled", "skip")
    html += _pip("🔀", "Live Traceroute", "Disabled", "skip")
    html += _pip("🗺️", "BGP / Routing", "Disabled", "skip")
    html += '</div>'
    return html

def render_ip_drilldown(r: SiteReport):
    if not r.ip_analyses: return
    v4_ips = [ia for ia in r.ip_analyses if ia.ip_version == 4 and not ia.is_synthetic_v6]
    v6_ips = [ia for ia in r.ip_analyses if ia.ip_version == 6 and not ia.is_synthetic_v6]
    syn_ips = [ia for ia in r.ip_analyses if ia.is_synthetic_v6]
    
    tab_names = ["IPv4"]
    if v6_ips: tab_names.append("IPv6")
    tab_names.append("Synthetic IPv6")
    
    tabs = st.tabs(tab_names)
    
    def render_ia_list(ia_list):
        if not ia_list: return
        for ia in ia_list:
            syn_tag = "NAT64 SYNTHETIC" if ia.is_synthetic_v6 else ("NATIVE IPv6" if ia.ip_version==6 else "IPv4")
            st.markdown(f"**{ia.ip}** &nbsp; — &nbsp; `{syn_tag}`")

    with tabs[0]: render_ia_list(v4_ips)
    if v6_ips:
        with tabs[1]: render_ia_list(v6_ips)
        with tabs[2]: render_ia_list(syn_ips)
    else:
        with tabs[1]: render_ia_list(syn_ips)

def render_detail_panel(r: SiteReport):
    st.markdown(f'<div style="font-weight:bold;margin-bottom:1rem;">◈ DETAILS — <span style="color:#0B58C6;">{r.domain}</span></div>', unsafe_allow_html=True)
    left, right = st.columns([1.4, 2.6], gap="large")
    with left:
        with st.expander("🔍 DNS Raw Output", expanded=True): st.code(r.dns_raw, language="text")
    with right:
        if r.valid:
            st.markdown('**Discovered IPs (DNS Only)**')
            render_ip_drilldown(r)

def main():
    if "reports" not in st.session_state: st.session_state.reports = []
    if "selected" not in st.session_state: st.session_state.selected = None
    if "dns_profile" not in st.session_state: st.session_state.dns_profile = "Google DNS (IPv4)"

    st.markdown('<div class="hdr"><div class="hdr-logo"><div class="hdr-jio">JIO</div><div><div class="hdr-title">ISOC Dashboard — DNS EDITION</div></div></div></div>', unsafe_allow_html=True)

    c_area, c_opts = st.columns([3, 1], gap="large")
    
    with c_area: 
        raw = st.text_area("urls", label_visibility="collapsed", height=150, placeholder="Enter domains here...")
        uploaded_file = st.file_uploader("📂 Or bulk upload domains (CSV / JSON)", type=["csv", "json"])
    
    with c_opts:
        dns_sel = st.selectbox("◈ Select DNS", DNS_LABELS, index=DNS_LABELS.index(st.session_state.dns_profile))
        st.session_state.dns_profile = dns_sel
        st.markdown(f"`{' | '.join(DNS_OPTIONS[dns_sel])}`")
        run_manual = st.button("▶▶ RUN DNS LOOKUP", use_container_width=True)

    if run_manual:
        domains_from_input = [d.strip() for d in raw.strip().splitlines() if d.strip()]
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.json'):
                    file_data = json.load(uploaded_file)
                    if isinstance(file_data, list):
                        domains_from_input.extend([str(d).strip() for d in file_data])
                elif uploaded_file.name.endswith('.csv'):
                    content = uploaded_file.read().decode('utf-8')
                    reader = csv.reader(io.StringIO(content))
                    for row in reader:
                        if row and row[0].strip():
                            domains_from_input.append(row[0].strip())
            except Exception as e:
                st.error(f"Failed to parse uploaded file: {e}")

        domains_from_input = list(dict.fromkeys(filter(None, domains_from_input)))

        if domains_from_input:
            # MODIFIED: Input limit increased from 100 to 150
            st.session_state.reports = [SiteReport(domain=d, dns_profile=dns_sel) for d in domains_from_input[:150]]
            st.session_state.selected = None
            
            with st.spinner("Resolving DNS..."):
                for r in st.session_state.reports:
                    analyse_domain(r, dns_sel)
            
            st.session_state.selected = st.session_state.reports[0].domain if st.session_state.reports else None
            st.rerun()

    reports = st.session_state.reports
    if not reports: return

    st.markdown("<hr>", unsafe_allow_html=True)
    total_ips = sum(len(r.ip_analyses) for r in reports)
    
    st.markdown(f"""
    <div class="mini-stats">
      <div class="mini-stat"><div class="ms-lbl">DOMAINS</div><div class="ms-num">{len(reports)}</div></div>
      <div class="mini-stat"><div class="ms-lbl">TOTAL IPs FETCHED</div><div class="ms-num">{total_ips}</div></div>
      <div class="mini-stat"><div class="ms-lbl">DNS USED</div><div class="ms-num" style="font-size:1rem;">{reports[0].dns_profile}</div></div>
    </div>""", unsafe_allow_html=True)

    dl_col1, dl_col2, _ = st.columns([1.5, 1.5, 4])
    report_dicts = [{"Domain": r.domain, "Primary IP": r.primary_ip, "Total IPs": len(r.resolved_ips), "Health": r.health, "DNS Profile": r.dns_profile, "IPv4": ", ".join(r.resolved_ipv4), "IPv6": ", ".join(r.resolved_ipv6)} for r in reports]
    
    with dl_col1:
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=report_dicts[0].keys())
        writer.writeheader()
        writer.writerows(report_dicts)
        st.download_button("⬇ Download as CSV", data=csv_buffer.getvalue(), file_name=f"dns_report_{int(time.time())}.csv", mime="text/csv", use_container_width=True)
        
    with dl_col2:
        json_data = json.dumps(report_dicts, indent=2)
        st.download_button("⬇ Download as JSON", data=json_data, file_name=f"dns_report_{int(time.time())}.json", mime="application/json", use_container_width=True)

    # MODIFIED: Perfectly aligned Custom Header mapping the exact table widths used below
    col_h1, col_h2 = st.columns([12, 1])
    with col_h1:
        st.markdown('''
        <table class="rtbl" style="margin-bottom: -10px;">
            <tr>
                <th style="width:24%">DOMAIN</th>
                <th style="width:24%">PRIMARY IP</th>
                <th style="width:12%; text-align:center;">TOTAL IPs</th>
                <th style="width:20%">DNS</th>
                <th style="width:20%; text-align:center;">STATUS</th>
            </tr>
        </table>
        ''', unsafe_allow_html=True)
    with col_h2:
        st.markdown('<div style="color:#6b7280; font-size:0.85rem; font-weight:bold; text-align:center; padding-top:0.5rem;">VIEW</div>', unsafe_allow_html=True)
    
    for i, r in enumerate(reports):
        is_sel = st.session_state.selected == r.domain
        col1, col2 = st.columns([12, 1])
        
        # MODIFIED: Extracted Total IPs into its own distinct aligned column 
        with col1:
            st.markdown(f'''
            <table class="rtbl">
                <tr>
                    <td style="width:24%"><b>{r.domain}</b></td>
                    <td style="width:24%">{r.primary_ip or "—"}</td>
                    <td style="width:12%; text-align:center; font-weight:bold; color:#475569;">{len(r.resolved_ips)}</td>
                    <td style="width:20%; color:#0B58C6;">{r.dns_profile}</td>
                    <td style="width:20%">{get_health_badge(r.health, r.invalid_reason, r.valid)}</td>
                </tr>
            </table>
            ''', unsafe_allow_html=True)
        
        with col2:
            if st.button("▼" if is_sel else "▶", key=f"btn_{i}", use_container_width=True):
                st.session_state.selected = None if is_sel else r.domain
                st.rerun()

        if is_sel:
            st.markdown("<br>", unsafe_allow_html=True)
            render_detail_panel(r)
            st.markdown("<br>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
