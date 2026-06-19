<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JIO ISOC Dashboard v6.4</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  /* ── Base ── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background-color: #f8fafc;
    color: #0f172a;
    min-height: 100vh;
  }

  /* ── LOGIN PAGE ── */
  #login-page {
    display: flex;
    align-items: flex-start;
    justify-content: center;
    min-height: 100vh;
    background: #f8fafc;
    padding: 5vh 1rem 2rem;
  }
  .login-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-top: 4px solid #e31837;
    border-radius: 16px;
    padding: 3rem 2.5rem;
    width: 100%;
    max-width: 380px;
    box-shadow: 0 20px 25px -5px rgba(15,23,42,0.05), 0 8px 10px -6px rgba(15,23,42,0.05);
  }
  .brand-wrap { text-align: center; margin-bottom: 1.5rem; }
  .brand-logo { font-size: 2.5rem; font-weight: 800; color: #0f3cc9; letter-spacing: -1.5px; line-height: 1; }
  .brand-title { font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-top: 0.4rem; }
  .brand-subtitle { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.62rem; color: #64748b; letter-spacing: 2px; text-transform: uppercase; margin-top: 0.3rem; }
  .field-label { font-family: 'Segoe UI', Arial, sans-serif; font-weight: 600; color: #334155; font-size: 0.85rem; display: block; margin-bottom: 0.4rem; margin-top: 1rem; }
  .field-input {
    width: 100%;
    border-radius: 8px;
    border: 1px solid #cbd5e1;
    background-color: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 0.6rem 1rem;
    font-size: 0.95rem;
    outline: none;
    transition: all 0.2s ease-in-out;
  }
  .field-input:focus {
    border-color: #0f3cc9;
    box-shadow: 0 0 0 3px rgba(15,60,201,0.15);
    background-color: #ffffff;
  }
  .login-spacer { height: 10px; }
  .btn-login {
    background: #0f3cc9;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    padding: 0.7rem 1.5rem;
    width: 100%;
    box-shadow: 0 4px 12px rgba(15,60,201,0.25);
    cursor: pointer;
    margin-top: 1rem;
    transition: background 0.2s;
  }
  .btn-login:hover { background: #0c32aa; }
  .login-error {
    background: rgba(220,53,69,0.08);
    border: 1px solid rgba(220,53,69,0.3);
    color: #c82333;
    border-radius: 6px;
    padding: 0.5rem 0.8rem;
    font-size: 0.85rem;
    margin-top: 0.8rem;
    display: none;
  }

  /* ── MAIN APP ── */
  #main-app { display: none; }

  /* ── SIDEBAR ── */
  .sidebar {
    position: fixed;
    top: 0; left: -260px;
    width: 260px;
    height: 100vh;
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
    z-index: 1000;
    padding: 1.5rem 1.2rem;
    transition: left 0.3s ease;
    box-shadow: 2px 0 20px rgba(0,0,0,0.08);
    overflow-y: auto;
  }
  .sidebar.open { left: 0; }
  .sidebar h3 { font-size: 1rem; font-weight: 800; color: #0f172a; margin-bottom: 0.3rem; }
  .sidebar .caption { font-size: 0.78rem; color: #64748b; margin-bottom: 1rem; }
  .sidebar hr { border: none; border-top: 1px solid #e2e8f0; margin: 0.8rem 0; }
  .sidebar .sb-section { font-weight: 700; font-size: 0.85rem; color: #0f172a; margin-bottom: 0.4rem; }
  .sidebar .sb-code { font-family: 'JetBrains Mono', monospace; background: #f1f5f9; border-radius: 4px; padding: 0.25rem 0.5rem; font-size: 0.78rem; color: #334155; display: block; margin-bottom: 0.3rem; }
  .sidebar .sb-build { font-size: 0.75rem; color: #64748b; line-height: 1.7; }
  .btn-logout {
    background: #0B58C6;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    padding: 0.5rem 1rem;
    width: 100%;
    cursor: pointer;
    margin-bottom: 0.5rem;
    transition: background 0.2s;
  }
  .btn-logout:hover { background: #0040cc; }
  .sidebar-overlay {
    display: none;
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.2);
    z-index: 999;
  }
  .sidebar-overlay.active { display: block; }

  /* ── TOPBAR ── */
  .topbar {
    position: sticky; top: 0; z-index: 100;
    background: #f8fafc;
    padding: 0.5rem 1.5rem;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #e2e8f0;
  }
  .topbar-menu-btn {
    background: none; border: none; cursor: pointer;
    font-size: 1.3rem; color: #6b7280; margin-right: 0.8rem;
    padding: 0.2rem 0.4rem;
  }
  .topbar-title { font-size: 0.8rem; color: #9ca3af; font-family: 'JetBrains Mono', monospace; }

  /* ── LAYOUT ── */
  .app-body { padding: 2rem 2rem 4rem; max-width: 1600px; margin: 0 auto; }

  /* ── HEADER ── */
  .hdr {
    background: #ffffff;
    border: 1px solid rgba(0,86,179,0.15);
    border-top: 5px solid #0B58C6;
    border-radius: 10px;
    padding: 1.5rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  }
  .hdr-logo { display: flex; align-items: center; gap: 1rem; }
  .hdr-jio { font-size: 2.5rem; font-weight: 900; color: #0B58C6; letter-spacing: -1px; line-height: 1; }
  .hdr-title { font-size: 1.25rem; font-weight: 800; color: #0f172a; letter-spacing: -0.3px; margin-bottom: 0.2rem; }
  .hdr-sub { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.8rem; color: #6b7280; letter-spacing: 1px; margin-top: 2px; font-weight: 600; }

  /* ── TABS ── */
  .tabs-bar { display: flex; gap: 0; border-bottom: 2px solid #e2e8f0; margin-bottom: 1.5rem; }
  .tab-btn {
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    padding: 0.6rem 1.2rem;
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    cursor: pointer;
    color: #6b7280;
    transition: all 0.15s;
    margin-bottom: -2px;
  }
  .tab-btn.active { color: #0B58C6; border-bottom-color: #0B58C6; }
  .tab-btn:hover:not(.active) { color: #0f172a; background: rgba(0,0,0,0.02); }
  .tab-panel { display: none; }
  .tab-panel.active { display: block; }

  /* ── FORM ELEMENTS ── */
  .slabel { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.85rem; letter-spacing: 1px; color: #4b5563; font-weight: 800; text-transform: uppercase; margin-bottom: 0.5rem; }
  textarea.domain-input {
    width: 100%;
    height: 150px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    resize: vertical;
    background: #ffffff;
    color: #0f172a;
    outline: none;
    transition: border-color 0.2s;
  }
  textarea.domain-input:focus { border-color: #0B58C6; box-shadow: 0 0 0 3px rgba(11,88,198,0.1); }
  select.dns-select {
    width: 100%;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 0.5rem 0.8rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    background: #ffffff;
    color: #0f172a;
    outline: none;
    cursor: pointer;
    transition: border-color 0.2s;
  }
  select.dns-select:focus { border-color: #0B58C6; }
  .dns-server-display {
    margin-top: 1.8rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem;
    font-weight: 600;
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 6px;
    padding: 0.6rem 1rem;
    color: #0B58C6;
  }
  .row-2col { display: grid; grid-template-columns: 2fr 3fr; gap: 1rem; margin-bottom: 1rem; }
  .row-btn { display: grid; grid-template-columns: 4fr 1fr; gap: 0.8rem; align-items: center; margin-top: 1rem; }
  .btn-run {
    background: #0B58C6;
    color: #ffffff;
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 6px;
    box-shadow: 0 4px 10px rgba(11,88,198,0.25);
    transition: all 0.2s ease-in-out;
    cursor: pointer;
    width: 100%;
  }
  .btn-run:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(11,88,198,0.4); background: #0040cc; }
  .ibr-check { display: flex; align-items: center; gap: 0.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #374151; margin-top: 0.8rem; cursor: pointer; }
  .ibr-check input { accent-color: #0B58C6; width: 15px; height: 15px; cursor: pointer; }
  .file-drop-zone {
    border: 2px dashed #cbd5e1;
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    color: #9ca3af;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
  }
  .file-drop-zone:hover, .file-drop-zone.drag-over { border-color: #0B58C6; background: rgba(11,88,198,0.03); color: #0B58C6; }
  .file-drop-zone input[type=file] { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
  .file-name-display { font-size: 0.8rem; color: #0B58C6; font-weight: 700; margin-top: 0.5rem; }

  /* ── PROGRESS ── */
  .progress-wrap { margin: 1.2rem 0; display: none; }
  .progress-row { display: grid; grid-template-columns: 6fr 1fr; gap: 0.5rem; align-items: center; }
  .progress-bar-bg { background: #e2e8f0; border-radius: 99px; height: 12px; overflow: hidden; }
  .progress-bar-fill { height: 100%; background: linear-gradient(90deg, #0B58C6, #4f46e5); border-radius: 99px; transition: width 0.3s ease; width: 0%; }
  .progress-text { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #6b7280; margin-top: 0.3rem; }
  .btn-stop {
    background: #dc3545; color: #fff; border: none; border-radius: 6px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 700;
    padding: 0.5rem 0.8rem; cursor: pointer; width: 100%;
  }
  .btn-stop:hover { background: #b02a37; }

  /* ── BADGES ── */
  .badge { display: inline-block; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: 800; font-family: 'JetBrains Mono', Consolas, monospace; letter-spacing: 0.5px; }
  .b-ok   { background: rgba(40,167,69,0.15); color: #1e7e34; border: 1px solid rgba(40,167,69,0.3); }
  .b-warn { background: rgba(255,193,7,0.15); color: #d39e00; border: 1px solid rgba(255,193,7,0.3); }
  .b-err  { background: rgba(220,53,69,0.15); color: #c82333; border: 1px solid rgba(220,53,69,0.3); }
  .badge-blocked {
    display: block; width: 100%; text-align: center; box-sizing: border-box;
    height: 26px; line-height: 18px; background: #000; color: #dc3545;
    border: 1px solid #dc3545; border-radius: 4px;
    font-size: 0.8rem; font-weight: 800; font-family: 'JetBrains Mono', monospace;
    padding: 0.25rem 0.6rem;
  }
  .badge-ok-full {
    display: block; width: 100%; text-align: center; box-sizing: border-box;
    height: 26px; line-height: 18px;
    background: rgba(40,167,69,0.15); color: #1e7e34;
    border: 1px solid rgba(40,167,69,0.3); border-radius: 4px;
    font-size: 0.8rem; font-weight: 800; font-family: 'JetBrains Mono', monospace;
  }
  .badge-err-select {
    width: 100%; display: block; box-sizing: border-box;
    text-align: center; padding: 0px 0.4rem;
    height: 26px; line-height: 26px; font-size: 0.8rem;
    background: rgba(220,53,69,0.15); color: #c82333;
    border: 1px solid rgba(220,53,69,0.3); border-radius: 4px;
    font-weight: 800; font-family: 'JetBrains Mono', monospace;
    outline: none; cursor: pointer;
  }

  /* ── MINI STATS ── */
  .mini-stats { display: flex; gap: 0.8rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
  .mini-stat { background: #ffffff; border: 1px solid rgba(0,0,0,0.08); border-radius: 8px; padding: 1rem 0.5rem; flex: 1; min-width: 90px; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: center; }
  .ms-lbl { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.7rem; color: #6b7280; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 800; text-transform: uppercase; }
  .ms-num { font-size: 1.5rem; font-weight: 900; color: #0B58C6; line-height: 1.1; margin-top: auto; }

  /* ── RESULTS TABLE ── */
  .rtbl { width: 100%; border-collapse: separate; border-spacing: 0 4px; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.85rem; table-layout: fixed; }
  .rtbl th { color: #6b7280; padding: 0.5rem 0.8rem; text-align: left; font-size: 0.8rem; letter-spacing: 1px; font-weight: 800; white-space: nowrap; overflow: hidden; }
  .rtbl td { padding: 0.6rem 0.8rem; background: #ffffff; border-top: 1px solid rgba(0,0,0,0.05); border-bottom: 1px solid rgba(0,0,0,0.05); color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }
  .rtbl td:first-child { border-left: 1px solid rgba(0,0,0,0.05); border-radius: 6px 0 0 6px; }
  .rtbl td:last-child  { border-right: 1px solid rgba(0,0,0,0.05); border-radius: 0 6px 6px 0; }
  .rtbl tr.sel td { background: rgba(11,88,198,0.05); border-color: #0B58C6; border-top: 1px solid #0B58C6; border-bottom: 1px solid #0B58C6; }
  .rtbl tr.sel td:first-child { border-left: 1px solid #0B58C6; }
  .rtbl tr.sel td:last-child  { border-right: 1px solid #0B58C6; }
  .rtbl tr:hover td { background: rgba(0,0,0,0.02); }
  .domain-cell { font-weight: 800; color: #0f172a; font-size: 0.9rem; }
  .ip-count-chip { background: rgba(11,88,198,0.1); color: #0B58C6; padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.75rem; font-weight: 800; }
  .invalid-domain { color: #dc3545 !important; text-decoration: line-through; }
  .results-grid { display: grid; grid-template-columns: 1fr 48px; gap: 0.5rem; align-items: start; }
  .view-col-header { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #4b5563; font-weight: 800; text-align: center; letter-spacing: 1px; height: 36px; line-height: 36px; }
  .btn-view {
    background: #0B58C6; color: #fff; border: none; border-radius: 6px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; font-weight: 700;
    padding: 0.4rem 0; cursor: pointer; width: 100%;
    box-shadow: 0 2px 6px rgba(11,88,198,0.2);
  }
  .btn-view:hover { background: #0040cc; }

  /* ── DETAIL PANEL ── */
  .detail-panel { margin-top: 0.5rem; margin-bottom: 1rem; }
  .detail-panel-inner { display: grid; grid-template-columns: 1.4fr 2.6fr; gap: 1.5rem; margin-top: 1rem; }
  .panel { background: #ffffff; border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
  .panel-hdr { background: rgba(0,123,255,0.03); border-bottom: 1px solid rgba(0,0,0,0.06); padding: 0.6rem 1rem; display: flex; align-items: center; gap: 0.6rem; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.85rem; font-weight: 800; color: #0f172a; letter-spacing: 1px; }
  .panel-body { padding: 1rem; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.85rem; color: #0f172a; line-height: 1.6; }
  .expander { border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; margin-bottom: 0.8rem; overflow: hidden; }
  .expander-hdr { padding: 0.7rem 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 700; color: #374151; cursor: pointer; background: #fafafa; display: flex; align-items: center; justify-content: space-between; user-select: none; }
  .expander-hdr:hover { background: #f1f5f9; }
  .expander-hdr .arrow { transition: transform 0.2s; font-size: 0.75rem; color: #9ca3af; }
  .expander-hdr.open .arrow { transform: rotate(90deg); }
  .expander-body { display: none; padding: 1rem; background: #ffffff; }
  .expander-body.open { display: block; }
  pre.code-block { background: #1e293b; color: #e2e8f0; padding: 1rem; border-radius: 6px; font-size: 0.85rem; font-weight: 600; overflow-x: auto; white-space: pre-wrap; word-break: break-all; line-height: 1.5; }

  /* ── HOP TABLE ── */
  .hop-table { width: 100%; border-collapse: collapse; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.85rem; }
  .hop-table th { color: #6b7280; padding: 0.6rem 0.8rem; text-align: left; border-bottom: 2px solid rgba(0,0,0,0.1); font-weight: 800; letter-spacing: 1px; }
  .hop-table td { padding: 0.5rem 0.8rem; border-bottom: 1px solid rgba(0,0,0,0.05); color: #0f172a; font-weight: 500; }
  .hop-table tr:hover td { background: rgba(0,123,255,0.03); }
  .hop-anomaly td { background: rgba(255,193,7,0.06); }

  /* ── PIPELINE ── */
  .pipeline { display: flex; flex-direction: column; gap: 6px; }
  .pip-step { display: flex; align-items: center; gap: 0.8rem; padding: 0.6rem 1rem; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); background: #ffffff; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.85rem; }
  .pip-step.done { border-color: rgba(40,167,69,0.5); background: rgba(40,167,69,0.08); }
  .pip-step.warn { border-color: rgba(255,193,7,0.5); background: rgba(255,193,7,0.08); }
  .pip-step.err  { border-color: rgba(220,53,69,0.5); background: rgba(220,53,69,0.08); }
  .pip-step.run  { border-color: #0B58C6; background: rgba(11,88,198,0.05); box-shadow: 0 0 8px rgba(11,88,198,0.2); }
  .pip-step.pending { border-color: rgba(128,128,128,0.3); background: transparent; opacity: 0.6; }
  .pip-icon { font-size: 1.1rem; width: 20px; text-align: center; }
  .pip-text { flex: 1; }
  .pip-label { font-weight: 700; color: #0f172a; font-size: 0.9rem; }
  .pip-sub { color: #6b7280; font-size: 0.75rem; margin-top: 2px; font-weight: 500; }
  .pip-badge { font-size: 0.75rem; font-weight: 800; padding: 0.2rem 0.5rem; border-radius: 4px; white-space: nowrap; }
  .pb-done { background: rgba(40,167,69,0.2); color: #1e7e34; }
  .pb-skip { background: rgba(128,128,128,0.2); color: #6c757d; }
  .pb-run  { background: rgba(0,123,255,0.2); color: #0056b3; }
  .pb-err  { background: rgba(220,53,69,0.2); color: #c82333; }

  /* ── PIPELINE WIDGET ── */
  #jio-widget-container {
    position: fixed; top: 25%; right: 0; z-index: 999999;
    font-family: sans-serif; display: none; align-items: flex-start;
    transition: transform 0.3s ease;
  }
  #jio-widget-fab {
    padding: 20px 10px;
    background: linear-gradient(135deg, #4f46e5, #8b5cf6);
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    color: white; border-radius: 8px 0 0 8px;
    box-shadow: -4px 0 15px rgba(0,0,0,0.1);
    writing-mode: vertical-rl; font-weight: 800; letter-spacing: 2px;
    font-size: 0.85rem; user-select: none;
  }
  #jio-widget-panel {
    display: none; width: 340px; background: #fff; border-radius: 0 0 0 12px;
    box-shadow: -8px 0 30px rgba(0,0,0,0.15); border: 1px solid #e2e8f0;
    border-right: none; overflow: hidden;
  }
  #jio-widget-header {
    background: linear-gradient(135deg, #4f46e5, #8b5cf6);
    padding: 14px 18px; color: white; font-size: 0.9rem; font-weight: bold;
    display: flex; justify-content: space-between; align-items: center;
    user-select: none; letter-spacing: 0.5px;
  }
  #jio-widget-content {
    padding: 16px; max-height: 65vh; overflow-y: auto; background: #f8fafc;
  }
  #jio-widget-content .pipeline { gap: 4px; }
  #jio-widget-content .pip-step { padding: 0.4rem 0.6rem; font-size: 0.75rem; border-radius: 6px; }
  #jio-widget-content .pip-label { font-size: 0.75rem; line-height: 1.1; }
  #jio-widget-content .pip-sub   { font-size: 0.6rem;  line-height: 1.1; }
  #jio-widget-content .pip-badge { font-size: 0.6rem;  padding: 0.15rem 0.35rem; }

  /* ── IP TABS ── */
  .sub-tabs-bar { display: flex; gap: 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 1rem; flex-wrap: wrap; }
  .sub-tab-btn {
    font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; font-weight: 700;
    padding: 0.45rem 1rem; background: none; border: none; border-bottom: 2px solid transparent;
    cursor: pointer; color: #6b7280; transition: all 0.15s; margin-bottom: -1px;
  }
  .sub-tab-btn.active { color: #0B58C6; border-bottom-color: #0B58C6; }
  .sub-tab-panel { display: none; }
  .sub-tab-panel.active { display: block; }

  /* ── EXPORT BUTTONS ── */
  .export-row { display: flex; gap: 0.8rem; margin: 1rem 0; }
  .btn-export {
    background: #0B58C6; color: #fff; border: none; border-radius: 6px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 700;
    padding: 0.5rem 1.2rem; cursor: pointer; text-decoration: none; display: inline-block;
    transition: background 0.2s;
  }
  .btn-export:hover { background: #0040cc; }

  /* ── EMPTY STATE ── */
  .empty-state { text-align: center; padding: 8rem 2rem; opacity: 0.4; }
  .empty-state .es-icon { font-size: 4rem; }
  .empty-state .es-msg { font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; font-weight: 700; letter-spacing: 2px; margin-top: 1.5rem; color: #4b5563; }
  .empty-state .es-sub { font-size: 0.8rem; margin-top: 0.8rem; color: #9ca3af; }

  /* ── BLOCKED / HALTED ── */
  .halted-box {
    background: rgba(220,53,69,0.05); border: 1px solid rgba(220,53,69,0.3); border-radius: 8px;
    padding: 1.5rem; font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #c82333; line-height: 1.8;
  }
  .halted-box .halted-title { font-size: 1.2rem; font-weight: 800; margin-bottom: 0.8rem; }
  .halted-box .halted-footer { margin-top: 1rem; opacity: 0.8; font-weight: 600; }

  /* ── RESPONSIVE ── */
  @media (max-width: 900px) {
    .detail-panel-inner { grid-template-columns: 1fr; }
    .row-2col { grid-template-columns: 1fr; }
    .mini-stats { gap: 0.5rem; }
    .mini-stat { min-width: 70px; }
    .app-body { padding: 1rem 0.8rem 3rem; }
  }

  code, pre { font-size: 0.85rem !important; font-weight: 600 !important; }
  hr.section-hr { border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0; }
</style>
</head>
<body>

<!-- ═══════════════════════════════════════════════ LOGIN PAGE ═══ -->
<div id="login-page">
  <div class="login-card">
    <div class="brand-wrap">
      <div class="brand-logo">JIO</div>
      <div class="brand-title">Internal ISOC Dashboard</div>
      <div class="brand-subtitle">Production Build · Network Edition v6.4</div>
    </div>
    <label class="field-label" for="login-user">Username</label>
    <input class="field-input" type="text" id="login-user" placeholder="Enter your username" autocomplete="username">
    <label class="field-label" for="login-pass">Password</label>
    <input class="field-input" type="password" id="login-pass" placeholder="Enter your password" autocomplete="current-password">
    <div class="login-spacer"></div>
    <button class="btn-login" onclick="doLogin()">Login</button>
    <div class="login-error" id="login-error">❌ Invalid operator credentials. Please verify and try again.</div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════ MAIN APP ═══ -->
<div id="main-app">

  <!-- SIDEBAR OVERLAY -->
  <div class="sidebar-overlay" id="sb-overlay" onclick="closeSidebar()"></div>

  <!-- SIDEBAR -->
  <div class="sidebar" id="sidebar">
    <h3>🛡️ JIO ISOC v6.4 · PROD</h3>
    <div class="caption">Operator Session Authenticated</div>
    <button class="btn-logout" onclick="doLogout()">🔒 Logout Session</button>
    <hr>
    <div class="sb-section">🔗 Infrastructure Links</div>
    <span class="sb-code">JUMP  10.x.x.x:22</span>
    <span class="sb-code">IBR   10.x.x.x:22</span>
    <hr>
    <div class="sb-section">ℹ️ Build Info</div>
    <div class="sb-build">Air-gapped production build<br>No internet access required<br>All data via JIO infra SSH</div>
  </div>

  <!-- TOPBAR -->
  <div class="topbar">
    <button class="topbar-menu-btn" onclick="openSidebar()">☰</button>
    <span class="topbar-title">JIO ISOC Dashboard v6.4 — PRODUCTION</span>
  </div>

  <!-- BODY -->
  <div class="app-body">

    <!-- HEADER -->
    <div class="hdr">
      <div class="hdr-logo">
        <div class="hdr-jio">JIO</div>
        <div>
          <div class="hdr-title">Internal ISOC Dashboard — NETWORK EDITION</div>
          <div class="hdr-sub">PRODUCTION BUILD · AIR-GAPPED · ALL DATA VIA INTERNAL INFRA</div>
        </div>
      </div>
    </div>

    <!-- INPUT TABS -->
    <div class="tabs-bar">
      <button class="tab-btn active" onclick="switchTab('manual', this)">✏️ &nbsp;Manual Input</button>
      <button class="tab-btn" onclick="switchTab('upload', this)">📡 &nbsp;Upload File (.txt / .csv / .xlsx)</button>
    </div>

    <!-- MANUAL INPUT TAB -->
    <div class="tab-panel active" id="tab-manual">
      <div style="margin-bottom:1rem;">
        <textarea class="domain-input" id="domain-textarea" placeholder="Enter one domain per line&#10;e.g.&#10;google.com&#10;jio.com&#10;airtel.in"></textarea>
      </div>
      <div class="row-2col">
        <div>
          <div class="slabel">◈ Select DNS (Internal JIO Only)</div>
          <select class="dns-select" id="dns-select-manual" onchange="updateDnsDisplay('manual')">
            <option value="5G/Sub6">5G/Sub6</option>
            <option value="LTE/Mobility" selected>LTE/Mobility</option>
            <option value="FTTX/UBR">FTTX/UBR</option>
            <option value="Enterprise">Enterprise</option>
          </select>
        </div>
        <div>
          <div class="dns-server-display" id="dns-display-manual">2405:200:800::1  |  49.45.0.1</div>
        </div>
      </div>
      <div class="row-btn">
        <button class="btn-run" onclick="runAnalysis()">▶▶ &nbsp;RUN</button>
        <label class="ibr-check">
          <input type="checkbox" id="ibr-manual" checked>
          IBR checks (BGP/ASN)
        </label>
      </div>
    </div>

    <!-- UPLOAD TAB -->
    <div class="tab-panel" id="tab-upload">
      <div style="max-width:75%;margin-bottom:1rem;">
        <div class="file-drop-zone" id="drop-zone"
             ondragover="event.preventDefault();this.classList.add('drag-over')"
             ondragleave="this.classList.remove('drag-over')"
             ondrop="handleFileDrop(event)">
          <div>📁 Drop file here or click to browse</div>
          <div style="font-size:0.75rem;margin-top:0.3rem;color:#9ca3af;">One domain per line (txt), first column (csv/xlsx). Max 100.</div>
          <input type="file" id="file-input" accept=".txt,.csv,.xlsx" onchange="handleFileSelect(event)">
        </div>
        <div class="file-name-display" id="file-name-display"></div>
      </div>
      <div class="row-2col">
        <div>
          <div class="slabel">◈ Select DNS (Internal JIO Only)</div>
          <select class="dns-select" id="dns-select-upload" onchange="updateDnsDisplay('upload')">
            <option value="5G/Sub6">5G/Sub6</option>
            <option value="LTE/Mobility" selected>LTE/Mobility</option>
            <option value="FTTX/UBR">FTTX/UBR</option>
            <option value="Enterprise">Enterprise</option>
          </select>
        </div>
        <div>
          <div class="dns-server-display" id="dns-display-upload">2405:200:800::1  |  49.45.0.1</div>
        </div>
      </div>
      <div class="row-btn">
        <button class="btn-run" onclick="runUploadAnalysis()">▶▶ &nbsp;RUN</button>
        <label class="ibr-check">
          <input type="checkbox" id="ibr-upload" checked>
          IBR checks (BGP/ASN)
        </label>
      </div>
    </div>

    <!-- PROGRESS -->
    <div class="progress-wrap" id="progress-wrap">
      <div class="progress-row">
        <div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" id="progress-fill"></div></div>
          <div class="progress-text" id="progress-text">ISOC Analysis Initializing...</div>
        </div>
        <button class="btn-stop" onclick="stopAnalysis()">🛑 STOP</button>
      </div>
    </div>

    <!-- RESULTS SECTION -->
    <div id="results-section" style="display:none;">
      <br><hr class="section-hr"><br>

      <!-- EXPORT -->
      <div class="export-row">
        <button class="btn-export" onclick="exportJSON()">⬇ Export JSON</button>
        <button class="btn-export" onclick="exportCSV()">⬇ Export CSV</button>
      </div>

      <!-- MINI STATS -->
      <div class="mini-stats" id="mini-stats"></div>

      <!-- RESULTS LABEL -->
      <div style="margin-bottom:0.5rem;"><span class="slabel">◈ Results</span></div>

      <!-- RESULTS TABLE -->
      <div class="results-grid" id="results-grid">
        <table class="rtbl" id="results-header-table">
          <colgroup>
            <col style="width:4%"><col style="width:18%"><col style="width:6%">
            <col style="width:14%"><col style="width:14%"><col style="width:10%">
            <col style="width:14%"><col style="width:20%">
          </colgroup>
          <tr>
            <th>#</th><th>DOMAIN</th><th>IPs</th><th>PRIMARY IP</th>
            <th>DNS</th><th>PCKT. LOSS</th><th>ASN</th><th>QUERY STATUS</th>
          </tr>
        </table>
        <div class="view-col-header">VIEW</div>
      </div>

      <div id="results-rows"></div>

      <!-- EMPTY STATE (shown before analysis) -->
      <div class="empty-state" id="empty-state" style="display:none;">
        <div class="es-icon">🛡️</div>
        <div class="es-msg">ENTER DOMAINS TO INITIATE ANALYSIS</div>
        <div class="es-sub">Production build · Air-gapped · Internal DNS only</div>
      </div>
    </div>

    <!-- INITIAL EMPTY STATE -->
    <div class="empty-state" id="initial-empty-state">
      <div class="es-icon">🛡️</div>
      <div class="es-msg">ENTER DOMAINS TO INITIATE ANALYSIS</div>
      <div class="es-sub">Production build · Air-gapped · Internal DNS only</div>
    </div>

  </div><!-- /app-body -->
</div><!-- /main-app -->

<!-- ═══════════════════════════════════════ PIPELINE WIDGET ═══ -->
<div id="jio-widget-container">
  <div id="jio-widget-fab" onclick="toggleWidget()">PIPELINE</div>
  <div id="jio-widget-panel">
    <div id="jio-widget-header">◈ PIPELINE STATUS</div>
    <div id="jio-widget-content">
      <div style="text-align:center;padding:20px;color:#64748b;font-size:0.85rem;">Waiting for triage data...</div>
    </div>
  </div>
</div>

<script>
// ═══════════════════════════════════════════════════════════════════════
//  CONFIG
// ═══════════════════════════════════════════════════════════════════════
const DNS_OPTIONS = {
  "5G/Sub6":      ["2405:200:800::11"],
  "LTE/Mobility": ["2405:200:800::1", "49.45.0.1"],
  "FTTX/UBR":    ["2405:200:800::3", "49.45.0.3"],
  "Enterprise":   ["2405:200:800::4", "49.45.0.4"],
};

// Demo credentials (match secrets.toml defaults)
const LOGIN_USERNAME = "isoc_operator";
const LOGIN_PASSWORD = "CHANGE_ME_STRONG_PASSWORD";

// App state
let appReports = [];
let selectedDomain = null;
let stopFlag = false;

// ═══════════════════════════════════════════════════════════════════════
//  LOGIN
// ═══════════════════════════════════════════════════════════════════════
function doLogin() {
  const u = document.getElementById('login-user').value.trim();
  const p = document.getElementById('login-pass').value;
  const err = document.getElementById('login-error');
  // Accept any non-empty credentials for UI demo
  if (u && p) {
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('main-app').style.display = 'block';
    err.style.display = 'none';
  } else {
    err.style.display = 'block';
  }
}

document.getElementById('login-pass').addEventListener('keydown', e => {
  if (e.key === 'Enter') doLogin();
});
document.getElementById('login-user').addEventListener('keydown', e => {
  if (e.key === 'Enter') document.getElementById('login-pass').focus();
});

function doLogout() {
  closeSidebar();
  document.getElementById('main-app').style.display = 'none';
  document.getElementById('login-page').style.display = 'flex';
  document.getElementById('login-user').value = '';
  document.getElementById('login-pass').value = '';
  appReports = []; selectedDomain = null;
  document.getElementById('results-section').style.display = 'none';
  document.getElementById('initial-empty-state').style.display = 'block';
}

// ═══════════════════════════════════════════════════════════════════════
//  SIDEBAR
// ═══════════════════════════════════════════════════════════════════════
function openSidebar()  { document.getElementById('sidebar').classList.add('open'); document.getElementById('sb-overlay').classList.add('active'); }
function closeSidebar() { document.getElementById('sidebar').classList.remove('open'); document.getElementById('sb-overlay').classList.remove('active'); }

// ═══════════════════════════════════════════════════════════════════════
//  TABS
// ═══════════════════════════════════════════════════════════════════════
function switchTab(name, btn) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('tab-' + name).classList.add('active');
}

// ═══════════════════════════════════════════════════════════════════════
//  DNS DISPLAY
// ═══════════════════════════════════════════════════════════════════════
function updateDnsDisplay(which) {
  const sel = document.getElementById('dns-select-' + which).value;
  const servers = DNS_OPTIONS[sel] || [];
  document.getElementById('dns-display-' + which).textContent = servers.join('  |  ');
}

// ═══════════════════════════════════════════════════════════════════════
//  FILE UPLOAD
// ═══════════════════════════════════════════════════════════════════════
let uploadedDomains = [];

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) processFile(file);
}

function handleFileDrop(e) {
  e.preventDefault();
  document.getElementById('drop-zone').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) processFile(file);
}

function processFile(file) {
  document.getElementById('file-name-display').textContent = '📄 ' + file.name;
  const reader = new FileReader();
  reader.onload = function(ev) {
    const text = ev.target.result;
    uploadedDomains = text.split(/[\r\n,]+/)
      .map(d => d.replace(/^https?:\/\//i, '').split('/')[0].split('?')[0].split('#')[0].trim().toLowerCase())
      .filter(d => d && d.includes('.'));
    uploadedDomains = [...new Set(uploadedDomains)].slice(0, 100);
  };
  reader.readAsText(file);
}

// ═══════════════════════════════════════════════════════════════════════
//  ANALYSIS — SIMULATED (UI demo; replace with real API calls)
// ═══════════════════════════════════════════════════════════════════════
function parseDomains(raw) {
  const seen = new Set(); const out = [];
  for (const line of raw.trim().split(/\n/)) {
    let d = line.trim().toLowerCase().replace(/^https?:\/\//i, '').split('/')[0].split('?')[0].split('#')[0].trim();
    if (d && !seen.has(d)) { seen.add(d); out.push(d); }
  }
  return out;
}

function runAnalysis() {
  const raw = document.getElementById('domain-textarea').value;
  const domains = parseDomains(raw).slice(0, 100);
  if (!domains.length) return;
  const dnsProfile = document.getElementById('dns-select-manual').value;
  const useIbr = document.getElementById('ibr-manual').checked;
  startAnalysis(domains, dnsProfile, useIbr);
}

function runUploadAnalysis() {
  if (!uploadedDomains.length) { alert('Please upload a file first.'); return; }
  const dnsProfile = document.getElementById('dns-select-upload').value;
  const useIbr = document.getElementById('ibr-upload').checked;
  startAnalysis(uploadedDomains, dnsProfile, useIbr);
}

function stopAnalysis() { stopFlag = true; }

async function startAnalysis(domains, dnsProfile, useIbr) {
  stopFlag = false;
  appReports = [];
  selectedDomain = null;

  document.getElementById('initial-empty-state').style.display = 'none';
  document.getElementById('results-section').style.display = 'none';
  document.getElementById('progress-wrap').style.display = 'block';
  document.getElementById('jio-widget-container').style.display = 'flex';
  showPipelineWaiting();

  const total = domains.length;
  let completed = 0;

  for (const domain of domains) {
    if (stopFlag) break;
    updateProgress(completed, total, domain);
    showPipelineRunning(domain, dnsProfile, useIbr);
    const report = await simulateAnalysis(domain, dnsProfile, useIbr);
    appReports.push(report);
    completed++;
    updateProgress(completed, total, domain);
  }

  document.getElementById('progress-fill').style.width = '100%';
  document.getElementById('progress-text').textContent = `✓ ISOC Analysis Complete — ${total} domain(s) processed!`;
  setTimeout(() => {
    document.getElementById('progress-wrap').style.display = 'none';
    renderResults(dnsProfile);
  }, 800);
}

function updateProgress(done, total, domain) {
  const pct = total > 0 ? Math.round((done / total) * 100) : 0;
  document.getElementById('progress-fill').style.width = pct + '%';
  document.getElementById('progress-text').textContent =
    done < total ? `Processing ${domain} (${pct}%)` : `Processing... (${pct}%)`;
}

// Simulated analysis — generates realistic-looking mock data
async function simulateAnalysis(domain, dnsProfile, useIbr) {
  await sleep(280 + Math.random() * 320);
  const servers = DNS_OPTIONS[dnsProfile] || ["49.45.0.1"];
  const rand = (a, b) => Math.floor(Math.random() * (b - a + 1)) + a;
  const randFloat = (a, b) => (Math.random() * (b - a) + a).toFixed(1);
  const INVALID_RATE = 0.12;
  const isInvalid = Math.random() < INVALID_RATE;

  if (isInvalid) {
    return {
      domain, dnsProfile, valid: false, health: 'critical',
      invalid_reason: Math.random() < 0.5 ? 'NXDOMAIN' : 'DNS Timeout / Unreachable',
      primary_ip: '', resolved_ips: [], resolved_ipv4: [], resolved_ipv6: [],
      synthetic_ipv6: [], packet_loss: 0, peer_asn: 0, ip_analyses: [],
      dns_raw: `; Query time: ${new Date().toISOString()}\n; DNS Profile: ${dnsProfile}\n$ nslookup ${domain} ${servers[0]}\n;; NXDOMAIN — ${domain} does not exist (authoritative from ${servers[0]}).`,
      jump_raw: '', fetch_time: 0.42,
      steps_status: { dns:'err', ping:'skip', traceroute:'skip', ibr:'skip', bgp:'skip', asn:'skip', jump:'skip' }
    };
  }

  const ipA = `${rand(1,220)}.${rand(10,250)}.${rand(1,254)}.${rand(1,254)}`;
  const ipB = `${rand(1,220)}.${rand(10,250)}.${rand(1,254)}.${rand(1,254)}`;
  const hasV6 = Math.random() > 0.45;
  const ipV6 = hasV6 ? `2404:6800:4007:${rand(800,820).toString(16)}::${rand(200,280).toString(16)}` : null;
  const loss = Math.random() < 0.15 ? rand(5, 60) : 0;
  const asn = randomASN();
  const latency = parseFloat(randFloat(2, 85));

  const synthV6 = ipv4ToNat64(ipA);

  const hops = generateHops(ipA);

  return {
    domain, dnsProfile, valid: true,
    health: loss > 0 ? 'degraded' : 'healthy',
    invalid_reason: '',
    primary_ip: ipA,
    resolved_ips: [ipA, ipB],
    resolved_ipv4: [ipA, ipB],
    resolved_ipv6: ipV6 ? [ipV6] : [],
    synthetic_ipv6: [synthV6],
    packet_loss: loss,
    peer_asn: asn.asn,
    asn_info: asn,
    dns_server_used: servers[0],
    ip_analyses: buildIPAnalyses([ipA, ipB], ipV6 ? [ipV6] : [], [synthV6], asn, loss, latency, hops, useIbr),
    dns_raw: buildDnsRaw(domain, dnsProfile, servers, ipA, ipB, ipV6, synthV6),
    jump_raw: `[✓] SSH Jump Server connection established\n> ping ${ipA}: 5 packets sent, 5 received`,
    fetch_time: parseFloat(randFloat(0.8, 3.2)),
    steps_status: {
      dns:'ok', ping: loss>0?'warn':'ok', traceroute:'ok',
      ibr: useIbr?'ok':'skip', bgp: useIbr?'ok':'skip', asn:'ok', jump:'ok'
    }
  };
}

function randomASN() {
  const DB = [
    {asn:55836,org:'Reliance Jio Infocomm Limited',country:'IN',rir:'APNIC',handle:'JIO',irr_valid:true,rpki:'Valid',num_routes:12000,num_peers:48},
    {asn:9829, org:'BSNL — Bharat Sanchar Nigam Ltd',country:'IN',rir:'APNIC',handle:'BSNL',irr_valid:true,rpki:'Valid',num_routes:5400,num_peers:32},
    {asn:45609,org:'Bharti Airtel Ltd',country:'IN',rir:'APNIC',handle:'AIRTEL',irr_valid:true,rpki:'Valid',num_routes:8200,num_peers:55},
    {asn:15169,org:'Google LLC',country:'US',rir:'ARIN',handle:'GOOGLE',irr_valid:true,rpki:'Valid',num_routes:21000,num_peers:180},
    {asn:13335,org:'Cloudflare, Inc.',country:'US',rir:'ARIN',handle:'CLOUDFLARE',irr_valid:true,rpki:'Valid',num_routes:19000,num_peers:220},
    {asn:16509,org:'Amazon.com, Inc.',country:'US',rir:'ARIN',handle:'AMAZON',irr_valid:true,rpki:'Valid',num_routes:35000,num_peers:310},
    {asn:8075, org:'Microsoft Corporation',country:'US',rir:'ARIN',handle:'MSFT',irr_valid:true,rpki:'Valid',num_routes:27000,num_peers:195},
    {asn:32934,org:'Meta Platforms, Inc.',country:'US',rir:'ARIN',handle:'META',irr_valid:true,rpki:'Valid',num_routes:16000,num_peers:142},
    {asn:20940,org:'Akamai Technologies, Inc.',country:'US',rir:'ARIN',handle:'AKAMAI',irr_valid:true,rpki:'Valid',num_routes:4200,num_peers:98},
  ];
  return DB[Math.floor(Math.random() * DB.length)];
}

function ipv4ToNat64(ip) {
  const p = ip.split('.').map(Number);
  const hi = ((p[0]<<8)|p[1]).toString(16).padStart(4,'0');
  const lo = ((p[2]<<8)|p[3]).toString(16).padStart(4,'0');
  return `64:ff9b::${hi}:${lo}`;
}

function generateHops(targetIp) {
  const hops = [];
  const n = Math.floor(Math.random() * 8) + 6;
  let latency = 1.5;
  for (let i = 1; i <= n; i++) {
    latency += Math.random() * 12 + 1;
    hops.push({
      num: i,
      ip: i === n ? targetIp : `10.${Math.floor(Math.random()*254)+1}.${Math.floor(Math.random()*254)+1}.${Math.floor(Math.random()*254)+1}`,
      hostname: i === n ? targetIp : (Math.random() > 0.4 ? `ae${i}-core${Math.floor(Math.random()*4)+1}.jio.net` : '*'),
      latency_ms: parseFloat(latency.toFixed(1)),
      network: i <= 3 ? 'AS55836 JIO' : (i > n-2 ? 'AS' + Math.floor(Math.random()*60000+1000) : ''),
      is_anomaly: latency > 60 && i > 4,
      anomaly_reason: latency > 60 && i > 4 ? '⚠ High latency spike' : ''
    });
  }
  return hops;
}

function buildIPAnalyses(v4, v6, synth, asn, loss, latency, hops, useIbr) {
  const analyses = [];
  for (const ip of v4) {
    analyses.push({
      ip, ip_version: 4, is_synthetic_v6: false,
      ping_ok: loss === 0, packet_loss: loss, avg_latency: latency,
      peer_asn: asn.asn, asn_info: asn, prefix: ip.split('.').slice(0,3).join('.') + '.0/24',
      next_hop: ip.split('.').slice(0,3).join('.') + '.1',
      local_pref: 100, bgp_prefixes: asn.num_routes, health: loss>0?'degraded':'healthy',
      hops,
      ping_raw: buildPingRaw(ip, loss, latency),
      ibr_raw: useIbr ? `[✓] IBR SSH Connected\nIBR# show bgp ipv4 unicast ${ip}\nBGP routing table entry for ${ip.split('.').slice(0,3).join('.')}.0/24\nAS path: 55836 ${asn.asn}\nLocal preference: 100` : '(IBR disabled)',
      bgp_raw: `[JIO ISOC PRODUCTION — IBR-sourced BGP Lookup]\n${'─'.repeat(55)}\nTarget IP  : ${ip}\nASN        : AS${asn.asn} (${asn.org})\nCountry    : ${asn.country}  |  RIR : ${asn.rir}\nPrefix     : ${ip.split('.').slice(0,3).join('.')}.0/24\nNext-Hop   : ${ip.split('.').slice(0,3).join('.')}.1\nLocal-Pref : 100\nAS-Path    : 55836 → ${asn.asn}\n${'─'.repeat(55)}\n[IRR]   ✓ Valid (in local ASN registry)\n[RPKI]  Valid  (derived from IRR)\n[RIR]   ${asn.rir}  |  Country: ${asn.country}\n[Size]  ${asn.num_routes.toLocaleString()} prefixes  |  ${asn.num_peers} peers`
    });
  }
  for (const ip of v6) {
    analyses.push({
      ip, ip_version: 6, is_synthetic_v6: false,
      ping_ok: true, packet_loss: 0, avg_latency: latency + 2,
      peer_asn: asn.asn, asn_info: asn, prefix: ip.split(':').slice(0,4).join(':') + '::/64',
      next_hop: '', local_pref: 100, bgp_prefixes: asn.num_routes, health: 'healthy',
      hops: [], ping_raw: buildPingRaw(ip, 0, latency+2),
      ibr_raw: '', bgp_raw: ''
    });
  }
  for (const ip of synth) {
    analyses.push({
      ip, ip_version: 6, is_synthetic_v6: true,
      ping_ok: loss === 0, packet_loss: loss, avg_latency: latency,
      peer_asn: asn.asn, asn_info: asn, prefix: '', next_hop: '',
      local_pref: 100, bgp_prefixes: 0, health: loss>0?'degraded':'healthy',
      hops: [], ping_raw: buildPingRaw(ip, loss, latency),
      ibr_raw: '', bgp_raw: ''
    });
  }
  return analyses;
}

function buildPingRaw(ip, loss, latency) {
  if (loss > 0)
    return `PING ${ip}: 10 packets\nRequest timeout for icmp_seq 2\nRequest timeout for icmp_seq 5\n--- ${ip} ping statistics ---\n10 packets transmitted, ${10-Math.floor(loss/10)} received, ${loss}% packet loss\nrtt min/avg/max = ${(latency*0.8).toFixed(1)}/${latency.toFixed(1)}/${(latency*1.4).toFixed(1)} ms`;
  return `PING ${ip}: 10 packets\n64 bytes from ${ip}: icmp_seq=1 ttl=55 time=${(latency*0.9).toFixed(1)} ms\n64 bytes from ${ip}: icmp_seq=2 ttl=55 time=${latency.toFixed(1)} ms\n64 bytes from ${ip}: icmp_seq=3 ttl=55 time=${(latency*1.05).toFixed(1)} ms\n--- ${ip} ping statistics ---\n10 packets transmitted, 10 received, 0% packet loss\nrtt min/avg/max = ${(latency*0.8).toFixed(1)}/${latency.toFixed(1)}/${(latency*1.3).toFixed(1)} ms`;
}

function buildDnsRaw(domain, dnsProfile, servers, ipA, ipB, ipV6, synthV6) {
  const ts = new Date().toTimeString().slice(0,8) + ' UTC';
  let raw = `; Query time: ${ts}\n; DNS Profile: ${dnsProfile}  [INTERNAL — Production Build]\n\n$ nslookup ${domain} ${servers[0]}\n;; ANSWER SECTION (A):\n${domain}. IN A  ${ipA}\n${domain}. IN A  ${ipB}\n`;
  if (ipV6) raw += `;; ANSWER SECTION (AAAA):\n${domain}. IN AAAA  ${ipV6}\n`;
  raw += `\n;; Synthesising NAT64 (64:ff9b::/96) from IPv4 records:\n;; NAT64: ${ipA}  →  ${synthV6}\n\n;; 2 A record(s) | ${ipV6?1:0} AAAA record(s) | 1 NAT64 synthetic\n;; Primary → ${ipA}\n;; Successful DNS Server: ${servers[0]}`;
  return raw;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ═══════════════════════════════════════════════════════════════════════
//  PIPELINE WIDGET
// ═══════════════════════════════════════════════════════════════════════
function toggleWidget() {
  const panel = document.getElementById('jio-widget-panel');
  panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
}

document.addEventListener('click', e => {
  const wc = document.getElementById('jio-widget-container');
  if (wc && !wc.contains(e.target)) document.getElementById('jio-widget-panel').style.display = 'none';
});

function showPipelineWaiting() {
  document.getElementById('jio-widget-content').innerHTML =
    '<div style="text-align:center;padding:20px;color:#64748b;font-size:0.85rem;">Waiting for triage data...</div>';
}

function showPipelineRunning(domain, dnsProfile, useIbr) {
  const s = { dns:'run', ping:'pending', traceroute:'pending', ibr:'pending', bgp:'pending', asn:'pending', jump:'pending' };
  document.getElementById('jio-widget-content').innerHTML =
    `<div style='margin-bottom:0.8rem;font-family:JetBrains Mono,monospace;font-size:0.85rem;font-weight:bold;color:#4f46e5;text-align:center;'>Analysis IN PROGRESS: <span style='color:#1e293b'>${esc(domain)}</span></div>` +
    buildPipelineHTML(s, dnsProfile, useIbr);
}

function buildPipelineHTML(s, dnsProfile, useIbr) {
  const IBR_IP = '10.x.x.x'; const SSH_PORT = 22;
  const steps = [
    {icon:'🔍', label:'DNS Resolution',   sub:`dnspython → ${dnsProfile} [INTERNAL]`,        key:'dns'},
    {icon:'📡', label:'ICMP/TCP Ping',    sub:'Real reachability & latency',                 key:'ping'},
    {icon:'🔀', label:'Live Traceroute',  sub:'ICMP TTL + TCP probe (per IP)',               key:'traceroute'},
    {icon:'🖥️', label:'JIO IBR SSH',      sub:`paramiko → ${IBR_IP}:${SSH_PORT}`,            key:'ibr'},
    {icon:'🗺️', label:'BGP Intelligence', sub:'IBR SSH parse + Local ASN DB',               key:'bgp'},
    {icon:'🌍', label:'ASN / IRR',        sub:'Local DB · no internet required',             key:'asn'},
  ];
  let html = '<div class="pipeline">';
  for (const st of steps) {
    const status = s[st.key] || 'pending';
    const cssMap = {ok:'done',warn:'warn',err:'err',skip:'skip',pending:'pending',run:'run'};
    const badgeMap = {ok:['pb-done','✓'],warn:['pb-done','⚠'],err:['pb-err','✗ ERR'],skip:['pb-skip','⊘'],pending:['pb-skip','⋯ WAIT'],run:['pb-run','⟳']};
    const css = cssMap[status] || 'pending';
    const [bc, bt] = badgeMap[status] || ['pb-skip','⋯ WAIT'];
    const dim = status==='ok' ? 'opacity:0.6;' : '';
    html += `<div class="pip-step ${css}"><span class="pip-icon">${st.icon}</span><span class="pip-text"><div class="pip-label" style="${dim}">${st.label}</div><div class="pip-sub" style="${dim}">${st.sub}</div></span><span class="pip-badge ${bc}">${bt}</span></div>`;
  }
  html += '</div>';
  return html;
}

// ═══════════════════════════════════════════════════════════════════════
//  RENDER RESULTS
// ═══════════════════════════════════════════════════════════════════════
function renderResults(dnsProfile) {
  const reports = appReports;
  document.getElementById('initial-empty-state').style.display = 'none';
  document.getElementById('results-section').style.display = 'block';

  // Mini stats
  const wn_c = reports.filter(r => r.health === 'degraded').length;
  const inv_c = reports.filter(r => !r.valid).length;
  const total_ips = reports.reduce((s,r) => s + r.resolved_ips.length, 0);
  const total_v6 = reports.reduce((s,r) => s + r.resolved_ipv6.length, 0);
  const total_nat64 = reports.reduce((s,r) => s + r.synthetic_ipv6.length, 0);
  const active_dns = reports[0]?.dnsProfile || '—';

  document.getElementById('mini-stats').innerHTML = `
    <div class="mini-stat"><div class="ms-lbl">DOMAINS</div><div class="ms-num">${reports.length}</div></div>
    <div class="mini-stat"><div class="ms-lbl" style="text-transform:none;">IPs Fetched</div><div class="ms-num">${total_ips}</div></div>
    <div class="mini-stat"><div class="ms-lbl">IPv6 NATIVE</div><div class="ms-num" style="color:#0f172a;">${total_v6}</div></div>
    <div class="mini-stat"><div class="ms-lbl">NAT64 SYNTH</div><div class="ms-num" style="color:#0f172a;">${total_nat64}</div></div>
    <div class="mini-stat"><div class="ms-lbl">ServFail</div><div class="ms-num" style="color:#d39e00;">${wn_c}</div></div>
    <div class="mini-stat"><div class="ms-lbl">NX DOMAIN</div><div class="ms-num" style="color:#c82333;">${inv_c}</div></div>
    <div class="mini-stat"><div class="ms-lbl">SELECT DNS</div><div class="ms-num" style="font-size:0.95rem;color:#0B58C6;padding-top:0.3rem;">${active_dns}</div></div>
  `;

  // Rows
  const rowsEl = document.getElementById('results-rows');
  rowsEl.innerHTML = '';
  const COL = '<colgroup><col style="width:4%"><col style="width:18%"><col style="width:6%"><col style="width:14%"><col style="width:14%"><col style="width:10%"><col style="width:14%"><col style="width:20%"></colgroup>';

  reports.forEach((r, idx) => {
    const i = idx + 1;
    const isSel = selectedDomain === r.domain;
    const locColor = !r.valid ? '#6c757d' : (r.packet_loss > 0 ? '#d39e00' : '#1e7e34');
    const lossStr = !r.valid ? 'N/A' : `${r.packet_loss.toFixed(0)}%`;
    const asnStr = r.peer_asn ? `AS${r.peer_asn}` : 'AS—';
    const ipCount = r.resolved_ips.length;
    const ipBadge = ipCount > 1 ? `<span class="ip-count-chip">${ipCount} IPs</span>` : (ipCount === 1 ? '1 IP' : '—');
    const invMark = r.valid ? '' : ' ⛔';
    const domCls = r.valid ? 'domain-cell' : 'domain-cell invalid-domain';
    const selCls = isSel ? 'sel' : '';
    const healthBadge = getHealthBadge(r);
    const rowEl = document.createElement('div');
    rowEl.className = 'results-grid';
    rowEl.style.marginBottom = '2px';
    rowEl.innerHTML = `
      <table class="rtbl" style="margin-bottom:0;">
        ${COL}
        <tr class="${selCls}">
          <td style="opacity:0.7;font-weight:700;">${i}</td>
          <td class="${domCls}">${esc(r.domain)}${invMark}</td>
          <td>${ipBadge}</td>
          <td style="font-weight:700;">${r.primary_ip || '—'}</td>
          <td style="color:#0B58C6;font-size:0.9rem;font-weight:800;">${r.dnsProfile}</td>
          <td style="color:${locColor};font-weight:800;">${lossStr}</td>
          <td style="font-weight:700;opacity:0.8;">${asnStr}</td>
          <td>${healthBadge}</td>
        </tr>
      </table>
      <button class="btn-view" onclick="toggleDetail(${idx})">${isSel ? '▼' : '▶'}</button>
    `;
    rowsEl.appendChild(rowEl);

    // Detail panel
    if (isSel) {
      const detailEl = document.createElement('div');
      detailEl.className = 'detail-panel';
      detailEl.id = `detail-${idx}`;
      detailEl.innerHTML = buildDetailPanel(r);
      rowsEl.appendChild(detailEl);
      setTimeout(() => initExpanders(detailEl), 0);
    }
  });
}

function toggleDetail(idx) {
  const r = appReports[idx];
  selectedDomain = (selectedDomain === r.domain) ? null : r.domain;
  renderResults(r.dnsProfile);
  if (selectedDomain) {
    setTimeout(() => {
      const el = document.getElementById('detail-' + idx);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
  }
}

function getHealthBadge(r) {
  if (r.health === 'BLOCKED')
    return '<span class="badge-blocked">BLOCKED</span>';
  if (!r.valid) {
    const msg = r.invalid_reason || 'Connectivity Error';
    return `<select class="badge-err-select"><option>Unsuccessful</option><option disabled>↳ ${esc(msg)}</option></select>`;
  }
  return '<span class="badge-ok-full">Successful</span>';
}

function buildDetailPanel(r) {
  const invTag = !r.valid ? ` <span class="badge b-err">NX DOMAIN — ${esc(r.invalid_reason)}</span>` : '';
  let html = `
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.95rem;font-weight:bold;color:#0f172a;letter-spacing:1px;margin-bottom:1rem;">
      ◈ DETAILS — <span style="color:#0B58C6;">${esc(r.domain)}</span>
      &nbsp;${getHealthBadge(r)}${invTag}
      <span style="font-size:0.8rem;color:#6b7280;font-weight:normal;margin-left:1rem;">(Fetch Time: ${r.fetch_time.toFixed(2)}s)</span>
    </div>
    <div class="detail-panel-inner">
      <div class="detail-left">`;

  // DNS Raw
  html += makeExpander('🔍 DNS Raw Output', `<pre class="code-block">${esc(r.dns_raw)}</pre>`, true);

  // Raw terminal
  if (r.ip_analyses && r.ip_analyses.length) {
    let ipTabsHtml = '<div class="sub-tabs-bar" id="rt-tabs">';
    r.ip_analyses.forEach((ia, ii) => {
      ipTabsHtml += `<button class="sub-tab-btn${ii===0?' active':''}" onclick="switchSubTab('rt',${ii},this)">${esc(ia.ip)}</button>`;
    });
    ipTabsHtml += '</div>';
    r.ip_analyses.forEach((ia, ii) => {
      ipTabsHtml += `<div class="sub-tab-panel${ii===0?' active':''}" id="rt-panel-${ii}">`;
      ipTabsHtml += '<div class="sub-tabs-bar" id="raw-tabs-' + ii + '">';
      ['Ping','IBR SSH','BGP + ASN'].forEach((t,ti) => {
        ipTabsHtml += `<button class="sub-tab-btn${ti===0?' active':''}" onclick="switchSubTab('raw${ii}',${ti},this)">${t}</button>`;
      });
      ipTabsHtml += '</div>';
      [ia.ping_raw, ia.ibr_raw, ia.bgp_raw].forEach((c, ci) => {
        ipTabsHtml += `<div class="sub-tab-panel${ci===0?' active':''}" id="raw${ii}-panel-${ci}"><pre class="code-block">${esc(c||'(skipped)')}</pre></div>`;
      });
      ipTabsHtml += '</div>';
    });
    html += makeExpander('🖥️ Raw Terminal Output', ipTabsHtml);
  }
  if (r.jump_raw) html += makeExpander('💻 Jump Server SSH Raw', `<pre class="code-block">${esc(r.jump_raw)}</pre>`);

  html += '</div><div class="detail-right">';

  if (!r.valid) {
    html += `<div class="halted-box">
      <div class="halted-title">⛔ DOMAIN HALTED — NXDOMAIN</div>
      <div>Domain: <b>${esc(r.domain)}</b></div>
      <div>Reason: <b>${esc(r.invalid_reason)}</b></div>
      <div class="halted-footer">No ping, traceroute, BGP or ASN analysis performed.</div>
    </div>`;
  } else {
    html += '<div class="slabel">Per-IP Drilldown — Select IP Tab</div>';
    html += buildIPDrilldown(r);
  }

  html += '</div></div>';
  return html;
}

function buildIPDrilldown(r) {
  const v4 = r.ip_analyses.filter(ia => ia.ip_version===4 && !ia.is_synthetic_v6);
  const v6 = r.ip_analyses.filter(ia => ia.ip_version===6 && !ia.is_synthetic_v6);
  const syn = r.ip_analyses.filter(ia => ia.is_synthetic_v6);

  const tabNames = ['IPv4'];
  if (v6.length) tabNames.push('IPv6');
  tabNames.push('Synthetic IPv6');

  let html = '<div class="sub-tabs-bar" id="ip-tabs">';
  tabNames.forEach((t, i) => {
    html += `<button class="sub-tab-btn${i===0?' active':''}" onclick="switchSubTab('ip',${i},this)">${t}</button>`;
  });
  html += '</div>';

  const lists = [v4];
  if (v6.length) lists.push(v6);
  lists.push(syn);

  lists.forEach((list, i) => {
    html += `<div class="sub-tab-panel${i===0?' active':''}" id="ip-panel-${i}">`;
    html += renderIAList(list);
    html += '</div>';
  });
  return html;
}

function renderIAList(list) {
  if (!list || !list.length) return '<div style="padding:1rem;color:#9ca3af;font-size:0.85rem;font-family:JetBrains Mono,monospace;">No data</div>';
  let html = '<div class="sub-tabs-bar" id="ia-tabs">';
  list.forEach((ia, i) => {
    html += `<button class="sub-tab-btn${i===0?' active':''}" onclick="switchSubTab('ia'+Date.now(),${i},this,'ia-panel-wrapper')">${esc(ia.ip)}</button>`;
  });
  html += '</div>';
  list.forEach((ia, i) => {
    const loc = ia.packet_loss > 0 ? '#d39e00' : '#1e7e34';
    let synTag = '';
    if (ia.is_synthetic_v6) synTag = `<span style="background:rgba(128,128,128,0.1);color:#4b5563;font-size:0.85rem;font-weight:800;padding:0.4rem 0.8rem;border-radius:6px;font-family:'JetBrains Mono',monospace;">NAT64 SYNTHETIC</span>`;
    else if (ia.ip_version===6) synTag = `<span style="background:rgba(0,123,255,0.1);color:#0B58C6;font-size:0.85rem;font-weight:800;padding:0.4rem 0.8rem;border-radius:6px;font-family:'JetBrains Mono',monospace;">NATIVE IPv6</span>`;
    let statusTag = '';
    if (!ia.ping_ok) statusTag = `<span style="font-family:'JetBrains Mono',monospace;font-size:0.95rem;background:#f8fafc;border:1px solid rgba(0,0,0,0.1);border-radius:6px;padding:0.4rem 0.8rem;"><span style="opacity:0.7;font-weight:700;">STATUS</span>&nbsp;<span style="color:#d39e00;font-weight:900;">⚠ Unsuccessful</span></span>`;
    html += `<div class="sub-tab-panel ia-panel-wrapper${i===0?' active':''}" id="ia-panel-${i}">
      <div style="display:flex;gap:0.75rem;margin-bottom:1rem;flex-wrap:wrap;align-items:center;">
        ${synTag}${statusTag}
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.95rem;background:#f8fafc;border:1px solid rgba(0,0,0,0.1);border-radius:6px;padding:0.4rem 0.8rem;">
          <span style="opacity:0.7;font-weight:700;">PCKT. LOSS</span>&nbsp;
          <span style="color:${loc};font-weight:900;">${ia.packet_loss.toFixed(0)}%</span></span>
      </div>`;

    // Hop table
    if (ia.hops && ia.hops.length) {
      let rows = '';
      for (const h of ia.hops.slice(0,30)) {
        const ac = h.is_anomaly ? ' hop-anomaly' : '';
        const ann = h.is_anomaly ? ` <span style="color:#b07d00;font-size:0.8rem;font-weight:bold;">${h.anomaly_reason}</span>` : '';
        const latStr = h.latency_ms > 0 ? `${h.latency_ms.toFixed(1)} ms` : '*';
        rows += `<tr class="${ac}"><td style="opacity:0.7;text-align:center;">${h.num}</td><td style="font-weight:700;">${esc(h.ip)}</td><td style="opacity:0.8;">${esc(h.hostname)}${ann}</td><td style="font-weight:700;">${latStr}</td><td style="opacity:0.6;">${esc(h.network)}</td></tr>`;
      }
      html += `<div class="expander">
        <div class="expander-hdr open" onclick="toggleExpander(this)">🔀 TRACEROUTE — ${esc(ia.ip)} — ${Math.min(ia.hops.length,30)} HOPS <span class="arrow">▶</span></div>
        <div class="expander-body open">
          <table class="hop-table">
            <thead><tr><th style="text-align:center;width:5%;">#</th><th style="width:20%;">IP</th><th style="width:40%;">HOSTNAME</th><th style="width:15%;">MIN. LATENCY</th><th style="width:20%;">ASN</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </div>`;
    }

    // BGP + ASN
    if (ia.asn_info) {
      const ai = ia.asn_info;
      const irrc = ai.irr_valid ? '#1e7e34' : '#d39e00';
      const rpkiColor = ai.rpki==='Valid' ? '#1e7e34' : (ai.rpki==='Unknown' ? '#d39e00' : '#dc3545');
      html += `<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem;">
        <div class="panel">
          <div class="panel-hdr">🗺️ &nbsp;BGP INTELLIGENCE — ${esc(ia.ip)}</div>
          <div class="panel-body" style="line-height:1.8;">
            <span style="opacity:0.7;">ASN:</span> <span style="font-weight:800;color:#0B58C6;">AS55836 IN</span> &nbsp;<span style="background:rgba(11,88,198,0.1);color:#0B58C6;font-size:0.75rem;padding:0.15rem 0.4rem;border-radius:4px;font-weight:bold;">JIO NETWORK</span><br>
            <span style="opacity:0.7;">Org:</span> <span style="font-weight:800;">Reliance JIO</span><br>
            <span style="opacity:0.7;display:block;margin:0.2rem 0;">↓</span>
            <span style="opacity:0.7;">ASN:</span> <span style="font-weight:800;color:#0B58C6;">AS${ai.asn}</span> &nbsp;<span style="background:rgba(128,128,128,0.1);color:gray;font-size:0.75rem;padding:0.15rem 0.4rem;border-radius:4px;font-weight:bold;">${ai.rir}</span><br>
            <span style="opacity:0.7;">Org:</span> <span style="font-weight:800;">${esc(ai.org)}</span><br><br>
            <span style="opacity:0.7;">Prefix:</span> <span style="font-weight:800;">${esc(ia.prefix)}</span> &nbsp;
            <span style="opacity:0.7;">Next Hop:</span> <span style="font-weight:800;">${esc(ia.next_hop)}</span> &nbsp;
            <span style="opacity:0.7;">LP:</span> <span style="font-weight:800;">${ia.local_pref}</span><br>
            <span style="opacity:0.7;">IRR:</span> <span style="font-weight:900;color:${irrc};">${ai.irr_valid ? '✓ Valid' : '⚠ Not in local DB'}</span>
          </div>
        </div>
        <div class="panel">
          <div class="panel-hdr">🌍 &nbsp;AS${ai.asn} — ${esc(ai.org)} <span style="margin-left:auto;font-size:0.75rem;color:gray;font-weight:normal;">IBR SSH + Local ASN DB</span></div>
          <div class="panel-body" style="line-height:1.8;">
            <span style="opacity:0.7;">Handle:</span> <span style="font-weight:800;color:#0B58C6;">${esc(ai.handle)}</span><br>
            <span style="opacity:0.7;">Country:</span> <span style="font-weight:800;">${ai.country}</span> &nbsp;
            <span style="opacity:0.7;">RIR:</span> <span style="font-weight:800;">${ai.rir}</span><br>
            <span style="opacity:0.7;">Prefixes:</span> <span style="font-weight:800;">${ai.num_routes.toLocaleString()}</span> &nbsp;
            <span style="opacity:0.7;">Peers:</span> <span style="font-weight:800;">${ai.num_peers}</span><br>
            <span style="opacity:0.7;">IRR:</span> <span style="font-weight:900;color:${irrc};">${ai.irr_valid ? '✓ Valid' : '⚠ Not in local DB'}</span> &nbsp;
            <span style="opacity:0.7;">RPKI:</span> <span style="font-weight:900;color:${rpkiColor};">${ai.rpki}</span>
          </div>
        </div>
      </div>`;
    }
    html += '</div>';
  });
  return html;
}

function makeExpander(title, body, openByDefault=false) {
  const openCls = openByDefault ? ' open' : '';
  return `<div class="expander">
    <div class="expander-hdr${openCls}" onclick="toggleExpander(this)">${title} <span class="arrow">▶</span></div>
    <div class="expander-body${openCls}">${body}</div>
  </div>`;
}

function initExpanders(el) { /* already inlined in onclick */ }

function toggleExpander(hdr) {
  hdr.classList.toggle('open');
  hdr.nextElementSibling.classList.toggle('open');
}

function switchSubTab(group, idx, btn, panelPrefix) {
  const parent = btn.parentElement;
  parent.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const panels = parent.parentElement.querySelectorAll('.sub-tab-panel');
  panels.forEach((p, i) => p.classList.toggle('active', i === idx));
}

// ═══════════════════════════════════════════════════════════════════════
//  EXPORT
// ═══════════════════════════════════════════════════════════════════════
function exportJSON() {
  const data = JSON.stringify(appReports, null, 2);
  dlFile('jio_isoc_prod_report.json', data, 'application/json');
}

function exportCSV() {
  const hdr = ['domain','primary_ip','dns_profile','health','packet_loss','peer_asn','fetch_time','invalid_reason'];
  const rows = appReports.map(r =>
    [r.domain, r.primary_ip, r.dnsProfile, r.health, r.packet_loss, r.peer_asn||'', r.fetch_time.toFixed(2), r.invalid_reason||'']
    .map(v => `"${String(v).replace(/"/g,'""')}"`).join(',')
  );
  dlFile('jio_isoc_prod_report.csv', [hdr.join(','), ...rows].join('\n'), 'text/csv');
}

function dlFile(name, content, mime) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([content], {type: mime}));
  a.download = name; a.click();
}

// ═══════════════════════════════════════════════════════════════════════
//  UTILS
// ═══════════════════════════════════════════════════════════════════════
function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
</script>
</body>
</html>
