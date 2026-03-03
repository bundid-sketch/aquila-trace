<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>AquilaTrace 3.1 — Live Scanner</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
/* ═══════════════════════════════════════════════
   AQUILATRACE 3.1 — GLOBAL STYLES
   Counter-Terrorism Financing Detection Platform
   ═══════════════════════════════════════════════ */
*{margin:0;padding:0;box-sizing:border-box;}
:root{
  --bg:#050c1a;
  --panel:#0a1628;
  --border:#1a2d4a;
  --sky:#38bdf8;
  --purple:#818cf8;
  --green:#34d399;
  --red:#ef4444;
  --orange:#fb923c;
  --yellow:#fbbf24;
  --pink:#f472b6;
  --text:#e2e8f0;
  --muted:#4b6080;
  --card:#0d1f38;
}
body{
  background:var(--bg);
  color:var(--text);
  font-family:'Segoe UI',system-ui,sans-serif;
  min-height:100vh;
  overflow-x:hidden;
}

/* ── HEADER ── */
header{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:0 20px;
  height:52px;
  background:var(--panel);
  border-bottom:1px solid var(--border);
  position:sticky;
  top:0;
  z-index:100;
}
.logo{display:flex;align-items:center;gap:8px;}
.logo-icon{
  width:30px;height:30px;border-radius:50%;
  background:linear-gradient(135deg,#0ea5e9,#6366f1);
  display:flex;align-items:center;justify-content:center;
  font-weight:800;font-size:12px;
}
.logo-text{font-size:17px;font-weight:800;letter-spacing:2px;}
.logo-text .a{color:var(--sky);}
.logo-text .b{color:#fff;}
.logo-ver{font-size:10px;color:var(--muted);margin-left:4px;}
.hdr-r{display:flex;align-items:center;gap:14px;font-size:11px;color:var(--muted);}
.live-pill{
  display:flex;align-items:center;gap:5px;
  background:rgba(52,211,153,.1);
  border:1px solid rgba(52,211,153,.3);
  padding:3px 10px;border-radius:20px;
  color:var(--green);font-size:11px;
}
.live-dot{
  width:6px;height:6px;border-radius:50%;
  background:var(--green);
  animation:pulse 1.2s infinite;
}
.scan-pill{
  display:flex;align-items:center;gap:5px;
  background:rgba(239,68,68,.1);
  border:1px solid rgba(239,68,68,.3);
  padding:3px 10px;border-radius:20px;
  color:#f87171;font-size:11px;cursor:pointer;
}
.scan-pill.off{
  background:rgba(100,116,139,.1);
  border-color:rgba(100,116,139,.3);
  color:var(--muted);
}
.scan-dot{
  width:6px;height:6px;border-radius:50%;
  background:#f87171;animation:pulse 0.8s infinite;
}
@keyframes pulse{
  0%,100%{opacity:1;transform:scale(1);}
  50%{opacity:.4;transform:scale(.8);}
}

/* ── NAV ── */
nav{
  display:flex;gap:0;padding:0 20px;
  background:var(--panel);
  border-bottom:1px solid var(--border);
  overflow-x:auto;
}
nav button{
  padding:10px 16px;font-size:12px;font-weight:500;
  background:none;border:none;color:var(--muted);
  cursor:pointer;border-bottom:2px solid transparent;
  transition:.2s;white-space:nowrap;
}
nav button:hover{color:var(--text);}
nav button.active{color:var(--sky);border-bottom-color:var(--sky);}

/* ── MAIN / TABS ── */
main{padding:16px 20px;max-width:1400px;margin:0 auto;}
.tab{display:none;}
.tab.active{display:block;}

/* ── SCANNER BAR ── */
.scanner-bar{
  background:var(--card);border:1px solid var(--border);
  border-radius:10px;padding:12px 16px;margin-bottom:14px;
  display:flex;align-items:center;gap:16px;flex-wrap:wrap;
}
.scan-status{font-size:12px;font-weight:600;flex:1;}
.scan-counters{display:flex;gap:14px;}
.sc{text-align:center;}
.sc-val{font-size:18px;font-weight:700;}
.sc-lbl{font-size:10px;color:var(--muted);}

/* ── BUTTONS ── */
.btn{
  padding:6px 14px;border-radius:7px;
  font-size:11px;font-weight:600;
  cursor:pointer;border:none;transition:.2s;
}
.btn-sky{
  background:rgba(56,189,248,.12);
  color:var(--sky);
  border:1px solid rgba(56,189,248,.3);
}
.btn-sky:hover{background:rgba(56,189,248,.22);}
.btn-red{
  background:rgba(239,68,68,.12);
  color:#f87171;
  border:1px solid rgba(239,68,68,.3);
}
.btn-red:hover{background:rgba(239,68,68,.22);}
.btn-green{
  background:rgba(52,211,153,.12);
  color:var(--green);
  border:1px solid rgba(52,211,153,.3);
}

/* ── LIVE FEED ── */
.feed-wrap{
  height:400px;overflow-y:auto;
  display:flex;flex-direction:column-reverse;
}
.feed-item{
  display:flex;align-items:center;gap:10px;
  padding:9px 12px;
  border-bottom:1px solid rgba(26,45,74,.6);
  font-size:12px;
  animation:fadeIn .4s ease;
}
@keyframes fadeIn{
  from{opacity:0;transform:translateY(-6px);}
  to{opacity:1;transform:translateY(0);}
}
.feed-item.flagged{background:rgba(239,68,68,.04);}
.feed-time{color:var(--muted);font-size:10px;width:52px;flex-shrink:0;font-family:monospace;}
.feed-type{width:70px;flex-shrink:0;}
.feed-icon{font-size:14px;width:22px;text-align:center;}
.feed-main{flex:1;}
.feed-entity{font-weight:600;color:var(--text);}
.feed-detail{color:var(--muted);font-size:11px;}
.feed-risk{width:46px;text-align:right;font-weight:700;font-size:13px;}
.feed-actions{display:flex;gap:5px;flex-shrink:0;}
.mini-badge{font-size:9px;padding:2px 7px;border-radius:10px;font-weight:600;}
.mb-clean{background:rgba(52,211,153,.1);color:var(--green);border:1px solid rgba(52,211,153,.25);}
.mb-flag{background:rgba(239,68,68,.1);color:#f87171;border:1px solid rgba(239,68,68,.25);}
.mb-warn{background:rgba(251,191,36,.1);color:var(--yellow);border:1px solid rgba(251,191,36,.25);}

/* ── KPI GRID ── */
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px;}
@media(max-width:800px){.kpi-grid{grid-template-columns:repeat(2,1fr);}}
.kpi{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px;}
.kpi-lbl{font-size:10px;color:var(--muted);margin-bottom:4px;}
.kpi-val{font-size:26px;font-weight:700;}
.kpi-sub{font-size:10px;color:var(--muted);margin-top:2px;}

/* ── PANELS ── */
.panel{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px;margin-bottom:14px;}
.panel-title{font-size:12px;font-weight:600;color:#94a3b8;margin-bottom:12px;text-transform:uppercase;letter-spacing:.5px;}

/* ── GRID LAYOUTS ── */
.g2{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
@media(max-width:700px){.g2{grid-template-columns:1fr;}}
.g3{display:grid;grid-template-columns:2fr 1fr;gap:14px;}
@media(max-width:700px){.g3{grid-template-columns:1fr;}}

/* ── ALERT ROWS ── */
.alert-row{
  display:flex;align-items:center;justify-content:space-between;
  background:var(--panel);border:1px solid var(--border);
  border-radius:10px;padding:11px 14px;margin-bottom:8px;
  cursor:pointer;transition:.2s;
}
.alert-row:hover{border-color:var(--sky);}

/* ── BADGES ── */
.badge{font-size:10px;padding:2px 9px;border-radius:20px;font-weight:600;}
.badge.critical{background:rgba(239,68,68,.15);color:#f87171;border:1px solid rgba(239,68,68,.3);}
.badge.high{background:rgba(251,146,60,.15);color:#fb923c;border:1px solid rgba(251,146,60,.3);}
.badge.medium{background:rgba(251,191,36,.15);color:var(--yellow);border:1px solid rgba(251,191,36,.3);}

/* ── WALLET CARDS ── */
.wallet-card{
  background:var(--panel);border:1px solid var(--border);
  border-radius:10px;padding:14px;margin-bottom:10px;transition:.2s;
}
.wallet-card:hover{border-color:var(--sky);}
.w-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;}
.w-chain{font-size:11px;font-weight:700;color:var(--sky);}
.w-flag{
  font-size:9px;padding:2px 8px;border-radius:10px;
  background:rgba(239,68,68,.12);color:#f87171;
  border:1px solid rgba(239,68,68,.25);
}
.w-addr{font-family:monospace;font-size:11px;color:#64748b;margin-bottom:8px;}
.w-stats{display:flex;gap:12px;font-size:11px;color:var(--muted);}
.prog{height:4px;background:#1e3a5f;border-radius:2px;}
.prog-f{height:4px;border-radius:2px;background:linear-gradient(90deg,#f59e0b,#ef4444);}

/* ── NETWORK CANVAS ── */
#netCanvas{width:100%;border-radius:10px;background:#060f1e;border:1px solid var(--border);display:block;}
.node-popup{
  position:absolute;background:#0d1f38;
  border:1px solid var(--border);border-radius:10px;
  padding:14px;font-size:12px;width:180px;
  pointer-events:none;display:none;
}
.node-popup.show{display:block;}

/* ── AI BOX ── */
.ai-box{
  background:#060f1e;border:1px solid var(--border);
  border-radius:10px;padding:16px;
  font-size:13px;line-height:1.75;color:#cbd5e1;
  min-height:100px;white-space:pre-wrap;
}
.ai-input{
  width:100%;background:var(--panel);
  border:1px solid var(--border);border-radius:8px;
  padding:9px 14px;color:var(--text);font-size:13px;outline:none;margin-bottom:8px;
}
.ai-input:focus{border-color:var(--sky);}

/* ── QUICK CARDS ── */
.quick-cards{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:14px;}
@media(max-width:600px){.quick-cards{grid-template-columns:1fr;}}
.qc{
  background:var(--panel);border:1px solid var(--border);
  border-radius:10px;padding:14px;cursor:pointer;transition:.2s;
}
.qc:hover{border-color:var(--sky);background:rgba(56,189,248,.05);}

/* ── OPS ── */
.op-prog{height:4px;background:#1e3a5f;border-radius:2px;}
.op-fill{height:4px;border-radius:2px;background:linear-gradient(90deg,#0ea5e9,#6366f1);}

/* ── MODAL ── */
.modal-overlay{
  display:none;position:fixed;inset:0;
  background:rgba(0,0,0,.75);z-index:200;
  align-items:center;justify-content:center;
}
.modal-overlay.show{display:flex;}
.modal{
  background:var(--card);border:1px solid var(--border);
  border-radius:14px;padding:22px;
  max-width:560px;width:92%;max-height:82vh;overflow-y:auto;
}
.modal-title{font-size:14px;font-weight:700;color:var(--sky);margin-bottom:14px;}
.modal-close{float:right;background:none;border:none;color:var(--muted);font-size:17px;cursor:pointer;margin-top:-2px;}

/* ── TYPING ANIMATION ── */
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.2;}}
.typing::after{content:'▋';animation:blink .7s infinite;color:var(--sky);}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:#1e3a5f;border-radius:2px;}
</style>
</head>
<body>

<!-- ═══════════════════════════════════════
     HEADER
     ═══════════════════════════════════════ -->
<header>
  <div class="logo">
    <div class="logo-icon">AQ</div>
    <div class="logo-text">
      <span class="a">AQUILA</span><span class="b">TRACE</span>
      <span class="logo-ver">v3.1</span>
    </div>
  </div>
  <div class="hdr-r">
    <div class="live-pill"><div class="live-dot"></div>LIVE</div>
    <div class="scan-pill" id="scanPill" onclick="toggleScan()">
      <div class="scan-dot"></div>
      <span id="scanPillTxt">SCANNING</span>
    </div>
    <span id="clock" style="font-family:monospace;font-size:11px;"></span>
    <span style="font-size:11px;">NCB Nairobi</span>
    <div style="width:27px;height:27px;border-radius:50%;background:linear-gradient(135deg,#0369a1,#4f46e5);
         display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;">OP</div>
  </div>
</header>

<!-- ═══════════════════════════════════════
     NAVIGATION
     ═══════════════════════════════════════ -->
<nav>
  <button class="active" onclick="switchTab('live',this)">📡 Live Scanner</button>
  <button onclick="switchTab('overview',this)">📊 Overview</button>
  <button onclick="switchTab('mpesa',this)">📱 M-PESA Monitor</button>
  <button onclick="switchTab('crypto',this)">🔗 Crypto Trace</button>
  <button onclick="switchTab('network',this)">🕸 Network Graph</button>
  <button onclick="switchTab('ai',this)">🤖 AI Analysis</button>
  <button onclick="switchTab('ops',this)">🛡 Operations</button>
</nav>

<!-- ═══════════════════════════════════════
     MAIN CONTENT
     ═══════════════════════════════════════ -->
<main>

  <!-- ── TAB 1: LIVE SCANNER ── -->
  <div id="tab-live" class="tab active">

    <!-- Scanner Status Bar -->
    <div class="scanner-bar">
      <div>
        <div style="font-size:11px;color:var(--muted);margin-bottom:2px;">SCAN STATUS</div>
        <div class="scan-status" id="scanStatusTxt" style="color:var(--green);">● Active — Monitoring all streams</div>
      </div>
      <div class="scan-counters">
        <div class="sc"><div class="sc-val" style="color:var(--sky)"  id="sc-total">0</div><div class="sc-lbl">Scanned</div></div>
        <div class="sc"><div class="sc-val" style="color:var(--yellow)" id="sc-warn">0</div><div class="sc-lbl">Warnings</div></div>
        <div class="sc"><div class="sc-val" style="color:var(--red)"  id="sc-flag">0</div><div class="sc-lbl">Flagged</div></div>
        <div class="sc"><div class="sc-val" style="color:var(--green)" id="sc-clean">0</div><div class="sc-lbl">Clean</div></div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <button class="btn btn-sky"  onclick="scanNow()">⚡ Force Scan</button>
        <button class="btn btn-red"  onclick="clearFeed()">🗑 Clear</button>
        <button class="btn" style="background:rgba(129,140,248,.1);color:var(--purple);border:1px solid rgba(129,140,248,.3);"
                onclick="toggleScan()">⏸ Pause</button>
      </div>
      <div style="font-size:10px;color:var(--muted);text-align:right;line-height:1.8;">
        <div>M-PESA <span style="color:var(--green)">●</span></div>
        <div>Crypto  <span style="color:var(--green)">●</span></div>
        <div>Network <span style="color:var(--green)">●</span></div>
      </div>
    </div>

    <!-- Stream Filter Buttons -->
    <div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap;">
      <button class="btn btn-sky" id="ff-all"     onclick="setFeedFilter('all',this)"     style="background:rgba(56,189,248,.2);">All Streams</button>
      <button class="btn btn-sky" id="ff-mpesa"   onclick="setFeedFilter('mpesa',this)">📱 M-PESA</button>
      <button class="btn btn-sky" id="ff-crypto"  onclick="setFeedFilter('crypto',this)">🔗 Crypto</button>
      <button class="btn btn-sky" id="ff-network" onclick="setFeedFilter('network',this)">🕸 Network</button>
      <button class="btn btn-red" id="ff-flagged" onclick="setFeedFilter('flagged',this)">🚨 Flagged Only</button>
    </div>

    <!-- Live Feed Panel -->
    <div class="panel" style="padding:0;overflow:hidden;">
      <div style="display:flex;justify-content:space-between;padding:10px 14px;
                  border-bottom:1px solid var(--border);font-size:11px;color:var(--muted);">
        <span>TIME</span>
        <span style="width:70px">TYPE</span>
        <span style="flex:1">ENTITY / TRANSACTION</span>
        <span style="width:46px;text-align:right">RISK</span>
        <span style="width:80px;text-align:right">STATUS</span>
        <span style="width:60px"></span>
      </div>
      <div class="feed-wrap" id="liveFeed"></div>
    </div>
    <div style="font-size:10px;color:var(--muted);text-align:center;margin-top:6px;">
      Click 🤖 on any flagged row to run AI analysis · Auto-scanning every 1.8s
    </div>
  </div><!-- /tab-live -->

  <!-- ── TAB 2: OVERVIEW ── -->
  <div id="tab-overview" class="tab">
    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-lbl">Total Scanned (Session)</div><div class="kpi-val" style="color:var(--sky)"    id="ov-total">0</div><div class="kpi-sub">All streams</div></div>
      <div class="kpi"><div class="kpi-lbl">Flagged Entities</div>      <div class="kpi-val" style="color:var(--red)"    id="ov-flag">0</div><div class="kpi-sub">Risk ≥ 70</div></div>
      <div class="kpi"><div class="kpi-lbl">Alerts Generated</div>      <div class="kpi-val" style="color:var(--orange)" id="ov-alerts">147</div><div class="kpi-sub">+live</div></div>
      <div class="kpi"><div class="kpi-lbl">Wallets Traced</div>        <div class="kpi-val" style="color:var(--purple)" id="ov-wallets">891</div><div class="kpi-sub">6 chains</div></div>
    </div>
    <div class="g3">
      <div class="panel"><div class="panel-title">Transaction Volume — Live (60s window)</div><canvas id="txChart" height="150"></canvas></div>
      <div class="panel"><div class="panel-title">Risk Distribution</div><canvas id="riskChart" height="150"></canvas></div>
    </div>
    <div class="panel"><div class="panel-title">Regional Threat Map — Kenya</div><canvas id="regionChart" height="90"></canvas></div>
  </div><!-- /tab-overview -->

  <!-- ── TAB 3: M-PESA MONITOR ── -->
  <div id="tab-mpesa" class="tab">
    <div class="panel">
      <div class="panel-title">M-PESA Live Transaction Monitor</div>
      <div style="display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap;">
        <div class="kpi" style="flex:1;min-width:120px;"><div class="kpi-lbl">Transactions Scanned</div><div class="kpi-val" style="color:var(--sky)"    id="mp-tpm">0</div></div>
        <div class="kpi" style="flex:1;min-width:120px;"><div class="kpi-lbl">Smurfing Alerts</div>      <div class="kpi-val" style="color:var(--red)"    id="mp-smrf">0</div></div>
        <div class="kpi" style="flex:1;min-width:120px;"><div class="kpi-lbl">SIM-Box Clusters</div>     <div class="kpi-val" style="color:var(--orange)" id="mp-sim">0</div></div>
        <div class="kpi" style="flex:1;min-width:120px;"><div class="kpi-lbl">Flagged Agents</div>       <div class="kpi-val" style="color:var(--yellow)" id="mp-agt">0</div></div>
      </div>
      <canvas id="mpesaChart" height="120"></canvas>
    </div>
    <div class="panel">
      <div class="panel-title">Flagged M-PESA Transactions</div>
      <div id="mpesaList" style="max-height:280px;overflow-y:auto;"></div>
    </div>
  </div><!-- /tab-mpesa -->

  <!-- ── TAB 4: CRYPTO TRACE ── -->
  <div id="tab-crypto" class="tab">
    <div class="panel">
      <div class="panel-title">Live Wallet Monitoring</div>
      <div style="display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap;">
        <div class="kpi" style="flex:1;min-width:120px;"><div class="kpi-lbl">Wallets Monitored</div><div class="kpi-val" style="color:var(--sky)"    id="cr-wm">847</div></div>
        <div class="kpi" style="flex:1;min-width:120px;"><div class="kpi-lbl">Mixer Detected</div>   <div class="kpi-val" style="color:var(--red)"    id="cr-mix">0</div></div>
        <div class="kpi" style="flex:1;min-width:120px;"><div class="kpi-lbl">Bridge Hops</div>       <div class="kpi-val" style="color:var(--orange)" id="cr-hop">0</div></div>
        <div class="kpi" style="flex:1;min-width:120px;"><div class="kpi-lbl">USDT Flagged</div>      <div class="kpi-val" style="color:var(--purple)" id="cr-usdt">0</div></div>
      </div>
      <canvas id="cryptoChart" height="110"></canvas>
    </div>

    <!-- Live flagged wallet cards injected here -->
    <div id="cryptoWallets"></div>

    <!-- Cross-Chain Flow Visualizer -->
    <div class="panel">
      <div class="panel-title">Cross-Chain Laundering Flow Visualizer</div>
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
        <div style="background:var(--panel);border:1px solid var(--sky);border-radius:8px;padding:7px 12px;font-size:11px;">
          🔶 BTC<br><span style="font-size:9px;color:var(--muted)">1A1z...eCC8</span>
        </div>
        <span style="color:var(--muted)">→</span>
        <div style="background:var(--panel);border:1px solid var(--red);border-radius:8px;padding:7px 12px;font-size:11px;">
          🌪 Mixer<br><span style="font-size:9px;color:var(--muted)">ChipMixer</span>
        </div>
        <span style="color:var(--muted)">→</span>
        <div style="background:var(--panel);border:1px solid var(--purple);border-radius:8px;padding:7px 12px;font-size:11px;">
          🌉 USDT Bridge<br><span style="font-size:9px;color:var(--muted)">TRC-20</span>
        </div>
        <span style="color:var(--muted)">→</span>
        <div style="background:var(--panel);border:1px solid var(--orange);border-radius:8px;padding:7px 12px;font-size:11px;">
          ⚡ TRX<br><span style="font-size:9px;color:var(--muted)">TXyz9...k2Lm</span>
        </div>
        <span style="color:var(--muted)">→</span>
        <div style="background:var(--panel);border:1px solid var(--yellow);border-radius:8px;padding:7px 12px;font-size:11px;">
          🔗 BEP20<br><span style="font-size:9px;color:var(--muted)">0xBEef...dA12</span>
        </div>
        <span style="color:var(--muted)">→</span>
        <div style="background:var(--panel);border:1px solid var(--green);border-radius:8px;padding:7px 12px;font-size:11px;">
          💵 Cash-Out<br><span style="font-size:9px;color:var(--muted)">Mombasa</span>
        </div>
      </div>
    </div>
  </div><!-- /tab-crypto -->

  <!-- ── TAB 5: NETWORK GRAPH ── -->
  <div id="tab-network" class="tab">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
      <div style="font-size:14px;font-weight:600;">Live Entity Network — GNN Cluster Map</div>
      <div style="display:flex;gap:8px;">
        <button class="btn btn-sky"   onclick="runLinkPrediction()">⚡ Link Prediction</button>
        <button class="btn btn-green" onclick="addLiveNode()">+ Live Node</button>
      </div>
    </div>
    <div style="position:relative;">
      <canvas id="netCanvas" style="height:380px;"></canvas>
      <!-- Node detail popup -->
      <div class="node-popup" id="nodePop">
        <div style="font-weight:700;color:var(--sky);margin-bottom:8px;" id="np-title"></div>
        <div style="font-size:11px;color:var(--muted);display:grid;grid-template-columns:1fr 1fr;gap:4px;">
          <span>Type</span>  <span style="color:var(--text)"             id="np-type"></span>
          <span>Risk</span>  <span style="color:var(--red);font-weight:700" id="np-risk"></span>
          <span>Links</span> <span style="color:var(--text)"             id="np-links"></span>
          <span>Seen</span>  <span style="color:var(--text)"             id="np-seen"></span>
        </div>
      </div>
    </div>
    <div id="netLegend" style="display:flex;gap:10px;flex-wrap:wrap;margin-top:8px;font-size:11px;color:var(--muted);"></div>
    <div id="predBox" style="display:none;" class="panel">
      <div class="panel-title">🔮 GNN Predicted Future Links</div>
      <div id="predContent"></div>
    </div>
  </div><!-- /tab-network -->

  <!-- ── TAB 6: AI ANALYSIS ── -->
  <div id="tab-ai" class="tab">
    <div class="quick-cards">

      <div class="qc" onclick="runAI('Summarize the most critical terrorism financing threats currently active across Kenya, focusing on mobile money, hawala networks, and crypto. Give a structured intel brief with threat level and recommended actions.')">
        <div style="font-size:18px;margin-bottom:6px;">🔍</div>
        <div style="font-size:12px;font-weight:600;margin-bottom:3px;">Live Threat Summary</div>
        <div style="font-size:11px;color:var(--muted);">Current TF threat landscape brief</div>
      </div>

      <div class="qc" onclick="runAI('Analyze smurfing patterns in M-PESA networks in Kenya. Describe how micro-deposits are structured, which agent corridors are most exploited, and what ML signatures identify these patterns. Give 5 specific detection rules.')">
        <div style="font-size:18px;margin-bottom:6px;">📱</div>
        <div style="font-size:12px;font-weight:600;margin-bottom:3px;">M-PESA Smurfing Deep Dive</div>
        <div style="font-size:11px;color:var(--muted);">Analyze layering in mobile money</div>
      </div>

      <div class="qc" onclick="runAI('Explain the BTC→USDT→TRX→BEP20 cross-chain laundering route. Who uses it, how do mixers and bridges obscure the trail, and what on-chain analytics techniques can law enforcement in Africa use to trace and disrupt it?')">
        <div style="font-size:18px;margin-bottom:6px;">🔗</div>
        <div style="font-size:12px;font-weight:600;margin-bottom:3px;">Crypto Laundering Routes</div>
        <div style="font-size:11px;color:var(--muted);">Cross-chain obfuscation breakdown</div>
      </div>

      <div class="qc" onclick="runAI('Describe how hawala networks in East Africa (Kenya, Somalia, Ethiopia border areas) are used to finance terrorism. Explain key corridors like Mandera and Moyale, how informal value transfer evades detection, and how AquilaTrace graph analytics can map these networks.')">
        <div style="font-size:18px;margin-bottom:6px;">🕌</div>
        <div style="font-size:12px;font-weight:600;margin-bottom:3px;">Hawala Network Mapping</div>
        <div style="font-size:11px;color:var(--muted);">East Africa IVTS corridors</div>
      </div>

      <div class="qc" onclick="runAI('Generate a detailed INTERPOL-ready intelligence report for Operation Sabre Horn — targeting hawala and mobile money terrorism financing networks in the Mandera–Moyale corridor. Include: executive summary, threat actors, financial flows, recommended actions, and legal basis for Kenya.')">
        <div style="font-size:18px;margin-bottom:6px;">📋</div>
        <div style="font-size:12px;font-weight:600;margin-bottom:3px;">INTERPOL Report Generator</div>
        <div style="font-size:11px;color:var(--muted);">Auto-generate Op. Sabre Horn report</div>
      </div>

      <div class="qc" onclick="runAI('Explain how SIM-box operations in Kenya collude with M-PESA agents to launder kidnap-ransom proceeds. How do they structure cash flows, what device fingerprints are detectable, and what joint DCI–Safaricom–CBK intervention is most effective?')">
        <div style="font-size:18px;margin-bottom:6px;">📡</div>
        <div style="font-size:12px;font-weight:600;margin-bottom:3px;">SIM-Box Collusion Analysis</div>
        <div style="font-size:11px;color:var(--muted);">Telecom-financial crime nexus</div>
      </div>

    </div><!-- /quick-cards -->

    <div class="panel">
      <div class="panel-title">Custom Intelligence Query</div>
      <textarea class="ai-input" id="aiInput" rows="3"
        placeholder="Ask AquilaTrace AI anything… e.g. 'How do Ponzi schemes in Nairobi feed into terrorism financing networks?' or paste raw transaction data for instant analysis."></textarea>
      <div style="display:flex;gap:8px;margin-bottom:12px;">
        <button class="btn btn-sky" onclick="sendAI()" style="flex:1;padding:9px;">🤖 Analyze →</button>
        <button class="btn" style="background:rgba(100,116,139,.1);border:1px solid var(--border);color:var(--muted);"
                onclick="document.getElementById('aiBox').textContent='';document.getElementById('aiInput').value=''">Clear</button>
      </div>
      <div class="panel-title">AI Intelligence Response</div>
      <div class="ai-box" id="aiBox">Select a quick analysis or type a custom query above to generate AI-powered intelligence insights.</div>
    </div>
  </div><!-- /tab-ai -->

  <!-- ── TAB 7: OPERATIONS ── -->
  <div id="tab-ops" class="tab">
    <div class="g2">
      <div>
        <div style="font-size:11px;color:var(--muted);margin-bottom:8px;font-weight:600;letter-spacing:.5px;">ACTIVE OPERATIONS</div>
        <div id="opsList"></div>
      </div>
      <div>
        <div style="font-size:11px;color:var(--muted);margin-bottom:8px;font-weight:600;letter-spacing:.5px;">SECURE INTEL FEED</div>
        <div id="feedList"></div>
      </div>
    </div>
    <div class="panel">
      <div class="panel-title">Agency Network Status</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;" id="agencyStatus"></div>
    </div>
  </div><!-- /tab-ops -->

</main>

<!-- ═══════════════════════════════════════
     AI ANALYSIS MODAL
     ═══════════════════════════════════════ -->
<div class="modal-overlay" id="modalOverlay"
     onclick="if(event.target===this)this.classList.remove('show')">
  <div class="modal">
    <button class="modal-close"
            onclick="document.getElementById('modalOverlay').classList.remove('show')">✕</button>
    <div class="modal-title" id="modalTitle">Analysis</div>
    <div id="modalBody" style="font-size:13px;line-height:1.8;color:#cbd5e1;"></div>
  </div>
</div>

<!-- ═══════════════════════════════════════
     JAVASCRIPT — ALL LOGIC
     ═══════════════════════════════════════ -->
<script>

/* ──────────────────────────────────────────
   CLOCK
   ────────────────────────────────────────── */
setInterval(() => {
  document.getElementById('clock').textContent =
    new Date().toUTCString().slice(17, 25) + ' UTC';
}, 1000);


/* ──────────────────────────────────────────
   TAB NAVIGATION
   ────────────────────────────────────────── */
function switchTab(id, btn) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  btn.classList.add('active');
  if (id === 'network') setTimeout(drawNet, 60);
}


/* ──────────────────────────────────────────
   SCAN STATE & COUNTERS
   ────────────────────────────────────────── */
let scanning    = true;
let scanInterval = null;
let totScanned  = 0, totWarn = 0, totFlag = 0, totClean = 0;
let feedFilter  = 'all';
let feedItems   = [];
let mpesaTx     = [], mpesaFlagged = [];
let cryptoFlagged = [];
let mpSmrf = 0, mpSim = 0, mpAgt = 0;
let crMix  = 0, crHop = 0, crUsdt = 0;
let txData  = { c: Array(30).fill(0), f: Array(30).fill(0) };
let riskBuckets = [0, 0, 0, 0]; // clean / low / medium / high


/* ──────────────────────────────────────────
   MOCK DATA POOLS
   ────────────────────────────────────────── */
const MPESA_AGENTS   = ['KE-04912','KE-07821','KE-01134','KE-09234','KE-05517','KE-03391'];
const MPESA_NAMES    = ['Wanjiku M.','Otieno K.','Muthoni A.','Kamau J.','Aisha M.','Hassan O.','Kipchoge R.','Njoroge P.'];
const MPESA_TYPES    = ['Transfer','Deposit','Withdrawal','Paybill','Buy Goods','Agent Float'];
const MPESA_PATTERNS = ['Smurfing','Normal','Normal','Normal','SIM-Box','Normal','Normal','Micro-deposit cluster','Normal','Normal'];
const CRYPTO_CHAINS  = ['BTC','ETH','USDT-TRC20','BNB','TRX','USDT-ERC20'];
const CRYPTO_FLAGS   = ['Peel Chain','Mixer Output','Bridge Hop','Stealth Addr','Dusting','Normal','Normal','Normal','Normal'];
const CRYPTO_ADDRS   = ['1A1z...eCC8','0xA3f...91b','TXyz...k2Lm','0xBEef...dA','bnb1...x9k2','3J98...nK4'];
const NET_TYPES      = ['wallet','agent','shell','hawala','sim','crypto','mule'];
const NET_FLAGS      = ['New entity','Sudden activity spike','Linked to flagged wallet','Hawala correspondent','Coordinated burst','Mixer interaction','Normal'];
const REGIONS        = ['Nairobi','Mombasa','Mandera','Kisumu','Moyale','Lamu','Eldoret'];

const randInt  = (a, b) => Math.floor(Math.random() * (b - a + 1)) + a;
const randItem = arr => arr[randInt(0, arr.length - 1)];
const fmtAmt   = v => 'KES ' + v.toLocaleString();
const nowStr   = () => new Date().toTimeString().slice(0, 8);
const riskColor= r => r >= 80 ? 'var(--red)' : r >= 55 ? 'var(--orange)' : 'var(--yellow)';


/* ──────────────────────────────────────────
   TRANSACTION GENERATORS
   ────────────────────────────────────────── */

/** Generate a synthetic M-PESA transaction */
function genMpesaTx() {
  const pat    = randItem(MPESA_PATTERNS);
  const isFlag = pat !== 'Normal';
  const risk   = isFlag ? randInt(60, 97) : randInt(5, 35);
  const amt    = isFlag ? randInt(500, 9900) : randInt(100, 50000);
  return {
    id: 'MP-' + randInt(100000, 999999),
    time: nowStr(), type: 'mpesa',
    agent: randItem(MPESA_AGENTS),
    name:  randItem(MPESA_NAMES),
    txType: randItem(MPESA_TYPES),
    pattern: pat, amt, risk,
    region: randItem(REGIONS),
    flagged: isFlag
  };
}

/** Generate a synthetic crypto wallet event */
function genCryptoTx() {
  const flag   = randItem(CRYPTO_FLAGS);
  const isFlag = flag !== 'Normal';
  const risk   = isFlag ? randInt(65, 96) : randInt(8, 40);
  return {
    id: 'CR-' + randInt(100000, 999999),
    time: nowStr(), type: 'crypto',
    chain: randItem(CRYPTO_CHAINS),
    addr:  randItem(CRYPTO_ADDRS),
    flag, risk,
    amt:    (Math.random() * 50 + 0.1).toFixed(4),
    region: randItem(['Unknown','Nairobi','Offshore','Mombasa']),
    flagged: isFlag
  };
}

/** Generate a synthetic network entity event */
function genNetworkEvent() {
  const flag   = randItem(NET_FLAGS);
  const isFlag = flag !== 'Normal' && Math.random() > 0.35;
  const risk   = isFlag ? randInt(62, 95) : randInt(10, 45);
  return {
    id: 'NE-' + randInt(100000, 999999),
    time: nowStr(), type: 'network',
    entity: 'Entity-' + Math.random().toString(36).slice(2, 7).toUpperCase(),
    ntype:  randItem(NET_TYPES),
    flag, risk,
    conns:  randInt(1, 12),
    region: randItem(REGIONS),
    flagged: isFlag
  };
}


/* ──────────────────────────────────────────
   LIVE FEED RENDERING
   ────────────────────────────────────────── */

function renderFeedItem(tx) {
  // Apply current stream filter
  const show =
    feedFilter === 'all' ||
    feedFilter === tx.type ||
    (feedFilter === 'flagged' && tx.flagged);
  if (!show) return;

  const feed = document.getElementById('liveFeed');
  const div  = document.createElement('div');
  div.className = 'feed-item' + (tx.flagged ? ' flagged' : '');
  if (tx.flagged) div.style.cursor = 'pointer';

  let icon = '', typeLabel = '', detail = '';

  if (tx.type === 'mpesa') {
    icon      = '📱';
    typeLabel = `<span style="color:var(--sky)">M-PESA</span>`;
    detail    = `${tx.name} · Agent ${tx.agent} · ${fmtAmt(tx.amt)} · ${tx.region}`;
  } else if (tx.type === 'crypto') {
    icon      = '🔗';
    typeLabel = `<span style="color:var(--purple)">CRYPTO</span>`;
    detail    = `${tx.chain} · ${tx.addr} · ${tx.amt} ${tx.chain.split('-')[0]} · ${tx.flag}`;
  } else {
    icon      = '🕸';
    typeLabel = `<span style="color:var(--green)">NETWORK</span>`;
    detail    = `${tx.entity} (${tx.ntype}) · ${tx.conns} links · ${tx.region}`;
  }

  const badge = tx.flagged
    ? `<span class="mini-badge mb-flag">FLAGGED</span>`
    : tx.risk > 45
      ? `<span class="mini-badge mb-warn">WARN</span>`
      : `<span class="mini-badge mb-clean">CLEAN</span>`;

  const txSafe = JSON.stringify(tx).replace(/'/g, "\\'");
  div.innerHTML = `
    <div class="feed-time">${tx.time}</div>
    <div class="feed-type">${icon} ${typeLabel}</div>
    <div class="feed-main">
      <div class="feed-entity">${tx.id}</div>
      <div class="feed-detail">${detail}</div>
    </div>
    <div class="feed-risk" style="color:${riskColor(tx.risk)}">${tx.risk}</div>
    <div style="width:80px;text-align:right">${badge}</div>
    <div class="feed-actions">
      ${tx.flagged
        ? `<button class="btn btn-sky" style="font-size:9px;padding:3px 7px;"
             onclick="aiModal(event,'${tx.id}','${tx.type}',${tx.risk},'${txSafe}')">🤖</button>`
        : ''}
    </div>`;

  feed.prepend(div);
  // Cap feed at 200 DOM rows for performance
  while (feed.children.length > 200) feed.removeChild(feed.lastChild);
}


/* Feed filter toggle */
function setFeedFilter(f, btn) {
  feedFilter = f;
  document.querySelectorAll('[id^="ff-"]').forEach(b => {
    b.style.background = 'rgba(56,189,248,.12)';
  });
  btn.style.background = 'rgba(56,189,248,.25)';

  // Rebuild visible feed
  document.getElementById('liveFeed').innerHTML = '';
  [...feedItems].reverse().slice(0, 200).forEach(tx => renderFeedItem(tx));
}


/* ──────────────────────────────────────────
   SCAN TICK — called every 1.8 seconds
   ────────────────────────────────────────── */
function scanTick() {
  const n = randInt(1, 3);
  for (let i = 0; i < n; i++) {
    const r = Math.random();
    let tx;
    if      (r < 0.40) tx = genMpesaTx();
    else if (r < 0.70) tx = genCryptoTx();
    else               tx = genNetworkEvent();

    feedItems.push(tx);
    totScanned++;

    if (tx.flagged) {
      totFlag++;
      updateFlaggedLists(tx);
    } else if (tx.risk > 45) {
      totWarn++;
    } else {
      totClean++;
    }

    renderFeedItem(tx);
    updateChartData(tx);
  }
  updateCounters();
}


/* ──────────────────────────────────────────
   COUNTER UPDATES
   ────────────────────────────────────────── */
function updateCounters() {
  const s = id => document.getElementById(id);
  s('sc-total').textContent  = totScanned;
  s('sc-warn').textContent   = totWarn;
  s('sc-flag').textContent   = totFlag;
  s('sc-clean').textContent  = totClean;
  s('ov-total').textContent  = totScanned;
  s('ov-flag').textContent   = totFlag;
  s('ov-alerts').textContent = 147 + totFlag;
  s('mp-tpm').textContent    = mpesaTx.length;
  s('mp-smrf').textContent   = mpSmrf;
  s('mp-sim').textContent    = mpSim;
  s('mp-agt').textContent    = mpAgt;
  s('cr-mix').textContent    = crMix;
  s('cr-hop').textContent    = crHop;
  s('cr-usdt').textContent   = crUsdt;
}


/* ──────────────────────────────────────────
   FLAGGED LIST UPDATES (M-PESA / Crypto)
   ────────────────────────────────────────── */
function updateFlaggedLists(tx) {
  if (tx.type === 'mpesa') {
    mpesaFlagged.unshift(tx);
    if (tx.pattern === 'Smurfing')              mpSmrf++;
    if (tx.pattern === 'SIM-Box')               mpSim++;
    mpAgt++;
    renderMpesaFlagged();
  } else if (tx.type === 'crypto') {
    cryptoFlagged.unshift(tx);
    if (tx.flag === 'Mixer Output')             crMix++;
    if (tx.flag === 'Bridge Hop')               crHop++;
    if (tx.chain.includes('USDT'))              crUsdt++;
    renderCryptoWallets();
  }
}

function renderMpesaFlagged() {
  const el = document.getElementById('mpesaList');
  if (!el) return;
  el.innerHTML = mpesaFlagged.slice(0, 30).map(tx => {
    const safe = JSON.stringify(tx).replace(/'/g, "\\'");
    return `
    <div class="alert-row"
         onclick="aiModal(event,'${tx.id}','mpesa',${tx.risk},'${safe}')">
      <div>
        <div style="font-size:12px;font-weight:600">${tx.id} · Agent ${tx.agent}</div>
        <div style="font-size:11px;color:var(--muted)">${tx.name} · ${fmtAmt(tx.amt)} · ${tx.pattern} · ${tx.region}</div>
      </div>
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-weight:700;color:${riskColor(tx.risk)}">${tx.risk}</span>
        <span class="badge critical">Flagged</span>
      </div>
    </div>`;
  }).join('');
}

function renderCryptoWallets() {
  const el = document.getElementById('cryptoWallets');
  if (!el) return;
  el.innerHTML = cryptoFlagged.slice(0, 4).map(tx => {
    const safe = JSON.stringify(tx).replace(/'/g, "\\'");
    return `
    <div class="wallet-card">
      <div class="w-top">
        <div class="w-chain">${tx.chain}</div>
        <span class="w-flag">${tx.flag}</span>
      </div>
      <div class="w-addr">${tx.addr}</div>
      <div class="w-stats">
        <span>Amount: <span style="color:var(--text)">${tx.amt} ${tx.chain.split('-')[0]}</span></span>
        <span>Risk:   <span style="color:var(--orange);font-weight:700">${tx.risk}/100</span></span>
        <span>Region: <span style="color:var(--text)">${tx.region}</span></span>
      </div>
      <div class="prog"><div class="prog-f" style="width:${tx.risk}%"></div></div>
      <button class="btn btn-sky" style="margin-top:8px;font-size:10px;"
              onclick="aiModal(event,'${tx.id}','crypto',${tx.risk},'${safe}')">
        🤖 AI Trace →
      </button>
    </div>`;
  }).join('');
}


/* ──────────────────────────────────────────
   SCAN CONTROL
   ────────────────────────────────────────── */
function toggleScan() {
  scanning = !scanning;
  const pill  = document.getElementById('scanPill');
  const ptxt  = document.getElementById('scanPillTxt');
  const stxt  = document.getElementById('scanStatusTxt');
  if (scanning) {
    pill.classList.remove('off');
    ptxt.textContent    = 'SCANNING';
    stxt.style.color    = 'var(--green)';
    stxt.textContent    = '● Active — Monitoring all streams';
    scanInterval = setInterval(scanTick, 1800);
  } else {
    pill.classList.add('off');
    ptxt.textContent    = 'PAUSED';
    stxt.style.color    = 'var(--muted)';
    stxt.textContent    = '⏸ Paused';
    clearInterval(scanInterval);
  }
}

function scanNow()  { for (let i = 0; i < randInt(3, 6); i++) scanTick(); }
function clearFeed(){ document.getElementById('liveFeed').innerHTML = ''; feedItems = []; }


/* ──────────────────────────────────────────
   CHART SETUP & LIVE UPDATE
   ────────────────────────────────────────── */
let txChart, riskChart, regionChart, mpesaChart, cryptoChart;

function initCharts() {
  const g = { color: '#4b6080', grid: 'rgba(255,255,255,.04)' };
  const xHide = { ticks: { display: false }, grid: { color: g.grid } };
  const yShow = { ticks: { color: g.color, font: { size: 10 } }, grid: { color: g.grid } };

  /* Transaction volume (rolling 30-tick window) */
  txChart = new Chart(document.getElementById('txChart'), {
    type: 'line',
    data: {
      labels: Array(30).fill(''),
      datasets: [
        { label: 'Clean',   data: [...txData.c], borderColor: '#38bdf8', backgroundColor: 'rgba(56,189,248,.06)', fill: true, tension: .4, pointRadius: 0 },
        { label: 'Flagged', data: [...txData.f], borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,.06)',  fill: true, tension: .4, pointRadius: 0 }
      ]
    },
    options: { animation: false, responsive: true, plugins: { legend: { labels: { color: g.color, font: { size: 10 } } } }, scales: { x: xHide, y: yShow } }
  });

  /* Risk distribution doughnut */
  riskChart = new Chart(document.getElementById('riskChart'), {
    type: 'doughnut',
    data: {
      labels: ['Clean', 'Low', 'Medium', 'High'],
      datasets: [{ data: [...riskBuckets], backgroundColor: ['#34d399','#38bdf8','#fbbf24','#ef4444'], borderWidth: 0 }]
    },
    options: { animation: false, responsive: true, plugins: { legend: { labels: { color: g.color, font: { size: 10 } }, position: 'right' } } }
  });

  /* Regional threat bar */
  regionChart = new Chart(document.getElementById('regionChart'), {
    type: 'bar',
    data: {
      labels: REGIONS,
      datasets: [{ label: 'Threat Score', data: REGIONS.map(() => randInt(20, 80)), backgroundColor: ['#38bdf8','#818cf8','#f472b6','#34d399','#fb923c','#a78bfa','#fbbf24'], borderRadius: 4 }]
    },
    options: { animation: false, responsive: true, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: g.color }, grid: { color: g.grid } }, y: yShow } }
  });

  /* M-PESA rolling volume */
  mpesaChart = new Chart(document.getElementById('mpesaChart'), {
    type: 'line',
    data: {
      labels: Array(30).fill(''),
      datasets: [
        { label: 'Flagged', data: Array(30).fill(0), borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,.08)', fill: true, tension: .4, pointRadius: 0 },
        { label: 'Volume',  data: Array(30).fill(0), borderColor: '#38bdf8', backgroundColor: 'rgba(56,189,248,.05)', fill: true, tension: .4, pointRadius: 0 }
      ]
    },
    options: { animation: false, responsive: true, plugins: { legend: { labels: { color: g.color, font: { size: 10 } } } }, scales: { x: xHide, y: yShow } }
  });

  /* Crypto flagged wallet bar */
  cryptoChart = new Chart(document.getElementById('cryptoChart'), {
    type: 'bar',
    data: {
      labels: Array(20).fill(''),
      datasets: [{ label: 'Flagged Wallets', data: Array(20).fill(0), backgroundColor: 'rgba(129,140,248,.4)', borderColor: '#818cf8', borderWidth: 1, borderRadius: 3 }]
    },
    options: { animation: false, responsive: true, plugins: { legend: { labels: { color: g.color, font: { size: 10 } } } }, scales: { x: xHide, y: yShow } }
  });
}

/** Push new data into live charts */
function updateChartData(tx) {
  txData.c = [...txData.c.slice(1), tx.flagged ? 0 : 1];
  txData.f = [...txData.f.slice(1), tx.flagged ? 1 : 0];

  if      (tx.risk < 30) riskBuckets[0]++;
  else if (tx.risk < 55) riskBuckets[1]++;
  else if (tx.risk < 75) riskBuckets[2]++;
  else                   riskBuckets[3]++;

  if (txChart)   { txChart.data.datasets[0].data = [...txData.c]; txChart.data.datasets[1].data = [...txData.f]; txChart.update('none'); }
  if (riskChart) { riskChart.data.datasets[0].data = [...riskBuckets]; riskChart.update('none'); }

  if (regionChart && totScanned % 15 === 0) {
    regionChart.data.datasets[0].data = REGIONS.map(() => randInt(20, 90));
    regionChart.update('none');
  }
  if (mpesaChart && totScanned % 3 === 0) {
    mpesaChart.data.datasets[0].data = [...mpesaChart.data.datasets[0].data.slice(1), mpesaFlagged.length];
    mpesaChart.data.datasets[1].data = [...mpesaChart.data.datasets[1].data.slice(1), mpesaTx.length];
    mpesaChart.update('none');
  }
  if (cryptoChart && totScanned % 3 === 0) {
    cryptoChart.data.datasets[0].data = [...cryptoChart.data.datasets[0].data.slice(1), cryptoFlagged.length];
    cryptoChart.update('none');
  }
}


/* ──────────────────────────────────────────
   NETWORK GRAPH — Canvas-based GNN Visualizer
   ────────────────────────────────────────── */
const NODE_COLORS = {
  wallet: '#38bdf8', agent: '#f472b6', shell: '#fb923c',
  hawala: '#a78bfa', terror: '#ef4444', sim: '#34d399',
  crypto: '#fbbf24', mule: '#818cf8'
};

let netNodes = [
  { id: 'Wallet A',    x: .18, y: .20, type: 'wallet', risk: 87 },
  { id: 'Agent 04912', x: .42, y: .40, type: 'agent',  risk: 94 },
  { id: 'Shell Co.',   x: .65, y: .18, type: 'shell',  risk: 81 },
  { id: 'Hawala Node', x: .55, y: .68, type: 'hawala', risk: 75 },
  { id: 'Cell #7',     x: .80, y: .46, type: 'terror', risk: 96 },
  { id: 'SIM Cluster', x: .25, y: .65, type: 'sim',    risk: 76 },
  { id: 'Crypto Mixer',x: .70, y: .80, type: 'crypto', risk: 88 },
];
let netEdges  = [[0,1],[1,2],[1,3],[2,4],[3,4],[5,1],[5,3],[3,6],[6,4]];
let predEdges = [];
let selNode   = null;
let showPred  = false;

function drawNet() {
  const cvs = document.getElementById('netCanvas');
  if (!cvs) return;
  const W = cvs.offsetWidth, H = 380;
  cvs.width = W; cvs.height = H;
  const ctx = cvs.getContext('2d');
  ctx.clearRect(0, 0, W, H);

  /* Draw existing edges */
  netEdges.forEach(([a, b]) => {
    const na = netNodes[a], nb = netNodes[b];
    ctx.beginPath();
    ctx.moveTo(na.x * W, na.y * H);
    ctx.lineTo(nb.x * W, nb.y * H);
    ctx.strokeStyle = 'rgba(56,189,248,.15)';
    ctx.lineWidth   = 1.5;
    ctx.setLineDash([]);
    ctx.stroke();
  });

  /* Draw predicted edges (dashed yellow) */
  if (showPred) {
    predEdges.forEach(([a, b]) => {
      const na = netNodes[a], nb = netNodes[b];
      if (!na || !nb) return;
      ctx.beginPath();
      ctx.moveTo(na.x * W, na.y * H);
      ctx.lineTo(nb.x * W, nb.y * H);
      ctx.strokeStyle = 'rgba(251,191,36,.55)';
      ctx.lineWidth   = 1.5;
      ctx.setLineDash([5, 4]);
      ctx.stroke();
    });
    ctx.setLineDash([]);
  }

  /* Draw nodes */
  netNodes.forEach((n, i) => {
    const x = n.x * W, y = n.y * H;
    const r = selNode === i ? 22 : 16;
    const c = NODE_COLORS[n.type] || '#94a3b8';

    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle   = c + '22'; ctx.fill();
    ctx.strokeStyle = c;
    ctx.lineWidth   = selNode === i ? 2.5 : 1.5;
    ctx.stroke();

    ctx.fillStyle     = c;
    ctx.font          = 'bold 7px sans-serif';
    ctx.textAlign     = 'center';
    ctx.textBaseline  = 'middle';
    ctx.fillText(n.type.toUpperCase(), x, y);

    ctx.fillStyle = '#94a3b8';
    ctx.font      = '9px sans-serif';
    ctx.fillText(n.id, x, y + r + 9);
  });

  /* Legend */
  const leg = document.getElementById('netLegend');
  if (leg) leg.innerHTML = Object.entries(NODE_COLORS)
    .map(([k, v]) => `
      <div style="display:flex;align-items:center;gap:4px;">
        <div style="width:9px;height:9px;border-radius:50%;background:${v}"></div>${k}
      </div>`).join('');
}

function addLiveNode() {
  const types  = Object.keys(NODE_COLORS);
  const newNode = {
    id:   'Node-' + Math.random().toString(36).slice(2, 5).toUpperCase(),
    x:    Math.random() * 0.8 + 0.1,
    y:    Math.random() * 0.7 + 0.1,
    type: randItem(types),
    risk: randInt(40, 95)
  };
  netNodes.push(newNode);
  netEdges.push([randInt(0, netNodes.length - 2), netNodes.length - 1]);
  drawNet();
}

function runLinkPrediction() {
  showPred  = true;
  predEdges = [[0, 3], [5, 6], [2, 3]];
  drawNet();
  const box = document.getElementById('predBox');
  box.style.display = 'block';
  document.getElementById('predContent').innerHTML = predEdges.map(([a, b]) => `
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:7px;font-size:12px;">
      <span style="color:var(--yellow)">⚡</span>
      <span>${netNodes[a]?.id || '?'}</span>
      <span style="color:var(--muted)">→ predicted →</span>
      <span>${netNodes[b]?.id || '?'}</span>
      <span style="color:var(--muted);font-size:10px;">
        ${(Math.random() * 0.2 + 0.76).toFixed(2)} confidence
      </span>
    </div>`).join('');
}

/* Canvas click — node selection */
document.addEventListener('DOMContentLoaded', () => {
  const cvs = document.getElementById('netCanvas');
  if (!cvs) return;

  cvs.addEventListener('click', e => {
    const rect = cvs.getBoundingClientRect();
    const mx   = (e.clientX - rect.left) * (cvs.width  / rect.width);
    const my   = (e.clientY - rect.top)  * (cvs.height / rect.height);
    const H    = cvs.height;
    let found  = null;

    netNodes.forEach((n, i) => {
      if (Math.hypot(mx - n.x * cvs.width, my - n.y * H) < 22) found = i;
    });

    selNode = found;
    const pop = document.getElementById('nodePop');

    if (found !== null) {
      const n = netNodes[found];
      document.getElementById('np-title').textContent = n.id;
      document.getElementById('np-type').textContent  = n.type;
      document.getElementById('np-risk').textContent  = n.risk + '/100';
      document.getElementById('np-links').textContent = netEdges.filter(([a, b]) => a === found || b === found).length;
      document.getElementById('np-seen').textContent  = randInt(1, 59) + 'm ago';

      const px = Math.min(n.x * cvs.offsetWidth + 20, cvs.offsetWidth - 200);
      const py = Math.max(n.y * H - 80, 10);
      pop.style.left     = px + 'px';
      pop.style.top      = py + 'px';
      pop.style.position = 'absolute';
      pop.classList.add('show');
    } else {
      pop.classList.remove('show');
    }
    drawNet();
  });

  cvs.addEventListener('mousemove', e => {
    const rect = cvs.getBoundingClientRect();
    const mx   = (e.clientX - rect.left) * (cvs.width  / rect.width);
    const my   = (e.clientY - rect.top)  * (cvs.height / rect.height);
    let over   = false;
    netNodes.forEach(n => {
      if (Math.hypot(mx - n.x * cvs.width, my - n.y * cvs.height) < 22) over = true;
    });
    cvs.style.cursor = over ? 'pointer' : 'default';
  });
});


/* ──────────────────────────────────────────
   AI MODAL — per-item analysis
   ────────────────────────────────────────── */
function aiModal(ev, id, type, risk, txJson) {
  ev.stopPropagation();
  let tx;
  try { tx = JSON.parse(txJson); } catch { tx = { id, type, risk }; }

  document.getElementById('modalTitle').textContent = `🤖 AI Analysis — ${id}`;
  document.getElementById('modalBody').innerHTML =
    `<div id="mAI" style="font-size:12px;line-height:1.8;color:#94a3b8;min-height:60px;white-space:pre-wrap;"></div>`;
  document.getElementById('modalOverlay').classList.add('show');

  let prompt = '';
  if (type === 'mpesa') {
    prompt = `You are AquilaTrace AI. Analyze this M-PESA transaction alert:
ID: ${tx.id}
Agent: ${tx.agent}
Name: ${tx.name}
Amount: KES ${tx.amt}
Pattern: ${tx.pattern}
Risk Score: ${tx.risk}/100
Region: ${tx.region}

Provide a concise 3-part intelligence brief:
1) Threat assessment
2) Likely TF method and how funds flow
3) Recommended law enforcement action in Kenya.`;
  } else if (type === 'crypto') {
    prompt = `You are AquilaTrace AI. Analyze this crypto wallet alert:
ID: ${tx.id}
Chain: ${tx.chain}
Address: ${tx.addr}
Flag: ${tx.flag}
Amount: ${tx.amt}
Risk Score: ${tx.risk}/100

Provide:
1) Laundering technique assessment
2) Likely threat actor and fund destination
3) Blockchain disruption recommendations for African law enforcement.`;
  } else {
    prompt = `You are AquilaTrace AI. Analyze this network entity alert:
ID: ${tx.id}
Entity: ${tx.entity}
Type: ${tx.ntype}
Flag: ${tx.flag}
Connections: ${tx.conns}
Risk Score: ${tx.risk}/100
Region: ${tx.region}

Provide:
1) Network role assessment
2) How this entity enables TF
3) Recommended targeted intervention.`;
  }

  streamAI(prompt, document.getElementById('mAI'));
}


/* ──────────────────────────────────────────
   ANTHROPIC API — STREAMING
   ────────────────────────────────────────── */
const SYSTEM_PROMPT = `You are AquilaTrace AI — an advanced counter-terrorism financing intelligence system deployed across Africa. You specialize in mobile money fraud, hawala networks, crypto laundering, network entity analysis, and cross-border terrorism financing in East Africa. Provide concise, structured, actionable intelligence briefs for law enforcement. Be specific about Kenya, Somalia, and East Africa when relevant.`;

async function streamAI(prompt, el) {
  el.textContent = '';
  el.classList.add('typing');
  try {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model:      'claude-sonnet-4-20250514',
        max_tokens: 1000,
        system:     SYSTEM_PROMPT,
        stream:     true,
        messages:   [{ role: 'user', content: prompt }]
      })
    });
    const reader = res.body.getReader();
    const dec    = new TextDecoder();
    let buf      = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const lines = buf.split('\n');
      buf = lines.pop();

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const data = line.slice(6);
        if (data === '[DONE]') continue;
        try {
          const j = JSON.parse(data);
          if (j.type === 'content_block_delta' && j.delta?.text)
            el.textContent += j.delta.text;
        } catch { /* ignore parse errors on partial chunks */ }
      }
    }
  } catch (err) {
    el.textContent = '⚠ API error: ' + err.message;
  }
  el.classList.remove('typing');
}

function runAI(prompt) {
  switchTab('ai', document.querySelector('nav button:nth-child(6)'));
  const box = document.getElementById('aiBox');
  box.textContent = '';
  streamAI(prompt, box);
}

function sendAI() {
  const q = document.getElementById('aiInput').value.trim();
  if (!q) return;
  const box = document.getElementById('aiBox');
  box.textContent = '';
  streamAI(q, box);
}


/* ──────────────────────────────────────────
   OPERATIONS TAB RENDER
   ────────────────────────────────────────── */
function renderOps() {
  const OPS = [
    { name: 'Op. Sabre Horn', partners: 'DCI + AFRIPOL + NIS',   status: 'Active',  p: 72, region: 'Mandera/Somalia'  },
    { name: 'Op. Dark Bridge', partners: 'INTERPOL + CBK + DCI', status: 'Active',  p: 45, region: 'Nairobi/Mombasa'  },
    { name: 'Op. Sand Veil',   partners: 'NIS + KRA + EACC',     status: 'Pending', p: 18, region: 'Moyale Corridor'  },
  ];
  const FEED = [
    { a: 'AFRIPOL',  m: 'New hawala node identified — Moyale corridor.',         t: '5m',  c: 'var(--sky)'    },
    { a: 'INTERPOL', m: 'Cross-border crypto alert: TZA→KEN flow, $240k USDT.', t: '22m', c: 'var(--purple)'  },
    { a: 'CBK',      m: 'Suspicious RTGS batch — 3 accounts frozen.',            t: '1h',  c: 'var(--green)'  },
    { a: 'NIS',      m: 'Group-7 cell financing routed via Lamu port.',          t: '2h',  c: 'var(--orange)' },
    { a: 'DCI',      m: 'Arrest: M-PESA super-agent linked to smurfing ring.',   t: '3h',  c: 'var(--pink)'   },
  ];
  const AGENCIES = [
    ['INTERPOL','green'],['AFRIPOL','green'],['DCI Kenya','green'],['CBK','green'],
    ['NIS','yellow'],['KRA','green'],['EACC','yellow'],['SAFARICOM','green']
  ];

  document.getElementById('opsList').innerHTML = OPS.map(o => `
    <div class="panel" style="margin-bottom:10px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
        <div style="font-size:13px;font-weight:600">${o.name}</div>
        <span class="badge ${o.status === 'Active' ? 'high' : 'medium'}">${o.status}</span>
      </div>
      <div style="font-size:11px;color:var(--muted);margin-bottom:8px">${o.partners} · ${o.region}</div>
      <div style="display:flex;justify-content:space-between;font-size:10px;color:var(--muted);margin-bottom:3px">
        <span>Progress</span><span>${o.p}%</span>
      </div>
      <div class="op-prog"><div class="op-fill" style="width:${o.p}%"></div></div>
    </div>`).join('');

  document.getElementById('feedList').innerHTML = FEED.map(f => `
    <div style="display:flex;gap:10px;background:var(--panel);border-radius:8px;
                padding:9px;margin-bottom:6px;font-size:11px;">
      <span style="font-weight:700;color:${f.c};width:58px;flex-shrink:0">${f.a}</span>
      <span style="color:#94a3b8;flex:1">${f.m}</span>
      <span style="color:var(--muted)">${f.t}</span>
    </div>`).join('');

  document.getElementById('agencyStatus').innerHTML = AGENCIES.map(([a, s]) => `
    <div style="background:var(--panel);border:1px solid var(--border);border-radius:8px;
                padding:7px 13px;font-size:11px;display:flex;align-items:center;gap:6px;">
      <span style="width:6px;height:6px;border-radius:50%;
                   background:${s === 'green' ? 'var(--green)' : 'var(--yellow)'};
                   display:inline-block"></span>${a}
    </div>`).join('');
}


/* ──────────────────────────────────────────
   BOOT — initialise everything on page load
   ────────────────────────────────────────── */
window.addEventListener('load', () => {
  initCharts();
  renderOps();

  // Pre-warm the feed with initial events
  for (let i = 0; i < 8; i++) scanTick();

  // Start live scanning loop
  scanInterval = setInterval(scanTick, 1800);

  // Re-draw network graph on window resize
  window.addEventListener('resize', () => {
    if (document.getElementById('tab-network').classList.contains('active'))
      drawNet();
  });
});

</script>
</body>
</html>
