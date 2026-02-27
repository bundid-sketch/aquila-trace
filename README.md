import { useState, useEffect, useRef, useCallback } from "react";

/* ═══════════════════════════════════════════════════════════════════
   AQUILATRACE  —  Counter-Terrorism Finance Intelligence Platform
   Niru Hackathon MVP  |  Security & Defence Track
   ═══════════════════════════════════════════════════════════════════ */

// ── FONTS via Google ──────────────────────────────────────────────
const fontLink = document.createElement("link");
fontLink.rel = "stylesheet";
fontLink.href = "https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow+Condensed:wght@300;400;600;700;900&family=Barlow:wght@300;400;500&display=swap";
document.head.appendChild(fontLink);

// ── DESIGN TOKENS ────────────────────────────────────────────────
const T = {
  bg0:      "#020508",
  bg1:      "#040C14",
  bg2:      "#071222",
  surface:  "#091828",
  border:   "#0E2438",
  borderHi: "#1A4060",
  accent:   "#00D4FF",
  accentDim:"#0099BB",
  red:      "#FF2D4B",
  amber:    "#FF9500",
  green:    "#00FF88",
  purple:   "#A855F7",
  textHi:   "#E8F4FF",
  textMid:  "#7BAAC8",
  textLo:   "#2A5070",
  fontMono: "'Share Tech Mono', monospace",
  fontHead: "'Barlow Condensed', sans-serif",
  fontBody: "'Barlow', sans-serif",
};

// ── GLOBAL STYLES ────────────────────────────────────────────────
const globalStyle = document.createElement("style");
globalStyle.textContent = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: ${T.bg1}; }
  ::-webkit-scrollbar-thumb { background: ${T.border}; border-radius: 2px; }
  ::-webkit-scrollbar-thumb:hover { background: ${T.borderHi}; }

  @keyframes pulse-ring {
    0%   { transform: scale(1);   opacity: 0.8; }
    100% { transform: scale(2.8); opacity: 0; }
  }
  @keyframes scanline {
    0%   { transform: translateY(-100%); }
    100% { transform: translateY(100vh); }
  }
  @keyframes flicker {
    0%,100% { opacity: 1; } 92% { opacity: 1; } 93% { opacity: 0.85; } 95% { opacity: 1; } 97% { opacity: 0.9; }
  }
  @keyframes data-stream {
    0%   { transform: translateY(0);    opacity: 1; }
    100% { transform: translateY(-60px); opacity: 0; }
  }
  @keyframes fade-up {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes blink {
    0%,100% { opacity: 1; } 50% { opacity: 0; }
  }
  @keyframes slide-in-right {
    from { opacity: 0; transform: translateX(40px); }
    to   { opacity: 1; transform: translateX(0); }
  }
  @keyframes radar-sweep {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
  }
  @keyframes node-ping {
    0%   { box-shadow: 0 0 0 0 rgba(0,212,255,0.6); }
    70%  { box-shadow: 0 0 0 12px rgba(0,212,255,0); }
    100% { box-shadow: 0 0 0 0 rgba(0,212,255,0); }
  }
  .fade-up { animation: fade-up 0.5s ease forwards; }
  .slide-in { animation: slide-in-right 0.4s ease forwards; }
  .ai-typing::after {
    content: '▋';
    animation: blink 0.8s infinite;
    color: ${T.accent};
  }
  input, select, textarea { font-family: ${T.fontMono}; }
  button { font-family: ${T.fontHead}; }
`;
document.head.appendChild(globalStyle);

// ═══════════════════════════════════════════════════════════════════
// DATASET
// ═══════════════════════════════════════════════════════════════════
const NETWORK_NODES = [
  { id:"N-001", label:"Al-Khalil Trading",  type:"shell",   risk:94, lat:12.65, lon:-8.00, country:"Mali",         funds:2400000,  connections:["N-003","N-005","N-009"] },
  { id:"N-002", label:"Sahel Fin. Svcs",    type:"hawala",  risk:81, lat:13.51, lon:2.11,  country:"Niger",        funds:890000,   connections:["N-001","N-006"] },
  { id:"N-003", label:"Crypto Wallet 7F2A", type:"crypto",  risk:97, lat:11.86, lon:15.52, country:"Chad",         funds:5100000,  connections:["N-001","N-004","N-007"] },
  { id:"N-004", label:"Green Horizon NGO",  type:"ngo",     risk:88, lat:11.99, lon:8.51,  country:"Nigeria",      funds:1750000,  connections:["N-003","N-008"] },
  { id:"N-005", label:"Desert Star Hold.",  type:"shell",   risk:72, lat:18.73, lon:15.96, country:"Chad",         funds:670000,   connections:["N-001","N-006","N-010"] },
  { id:"N-006", label:"Al-Nour Foundation", type:"ngo",     risk:85, lat:32.89, lon:13.18, country:"Libya",        funds:3200000,  connections:["N-002","N-005","N-009"] },
  { id:"N-007", label:"Atlas Capital Ltd",  type:"broker",  risk:61, lat:30.04, lon:31.24, country:"Egypt",        funds:440000,   connections:["N-003","N-010"] },
  { id:"N-008", label:"Rapid Growth Inv.",  type:"broker",  risk:78, lat:15.56, lon:32.53, country:"Sudan",        funds:1100000,  connections:["N-004","N-009"] },
  { id:"N-009", label:"Trans-Sahara Log.",  type:"front",   risk:91, lat:16.77, lon:-3.00, country:"Mali",         funds:2900000,  connections:["N-001","N-006","N-008"] },
  { id:"N-010", label:"Horizon Trust",      type:"trust",   risk:56, lat:33.89, lon:9.54,  country:"Tunisia",      funds:320000,   connections:["N-005","N-007"] },
];

const ASSETS = [
  { id:"AST-00001", type:"Cash Bundle",           entity:"Al-Khalil Trading Co.", country:"Mali",         riskScore:87, riskLevel:"CRITICAL", status:"Under Investigation", analyst:"Amara Diallo",    flagged:"2024-01-15", value:2400000 },
  { id:"AST-00002", type:"Hawala Transfer",        entity:"Sahel Fin. Services",   country:"Niger",        riskScore:72, riskLevel:"HIGH",     status:"Active",              analyst:"Kwame Mensah",    flagged:"2024-01-18", value:890000  },
  { id:"AST-00003", type:"Cryptocurrency Wallet",  entity:"Ahmed Musa Al-Farouq",  country:"Libya",        riskScore:97, riskLevel:"CRITICAL", status:"Frozen",              analyst:"Zara Nkrumah",   flagged:"2024-01-10", value:5100000 },
  { id:"AST-00004", type:"Prepaid Card Network",   entity:"Unknown Actor",          country:"Sudan",        riskScore:45, riskLevel:"MEDIUM",   status:"Watchlist",           analyst:"Ibrahim Okonkwo",flagged:"2024-01-22", value:185000  },
  { id:"AST-00005", type:"Shell Company",          entity:"Green Horizon NGO",      country:"Nigeria",      riskScore:88, riskLevel:"CRITICAL", status:"Under Investigation", analyst:"Chidi Kamau",     flagged:"2024-01-12", value:1750000 },
  { id:"AST-00006", type:"Real Estate Portfolio",  entity:"Trans-Sahara Logistics", country:"Mali",         riskScore:91, riskLevel:"CRITICAL", status:"Seized",              analyst:"Amara Diallo",    flagged:"2024-01-08", value:2900000 },
  { id:"AST-00007", type:"Mobile Money Network",   entity:"Al-Nour Foundation",     country:"Libya",        riskScore:85, riskLevel:"CRITICAL", status:"Frozen",              analyst:"Halima Mwangi",   flagged:"2024-01-20", value:3200000 },
  { id:"AST-00008", type:"NGO Account",            entity:"Rapid Growth Inv.",       country:"Sudan",        riskScore:78, riskLevel:"HIGH",     status:"Active",              analyst:"Moussa Balogun",  flagged:"2024-01-25", value:1100000 },
  { id:"AST-00009", type:"Trade Invoice Fraud",    entity:"Atlas Capital Ltd",       country:"Egypt",        riskScore:61, riskLevel:"HIGH",     status:"Watchlist",           analyst:"Abebe Hassan",    flagged:"2024-01-28", value:440000  },
  { id:"AST-00010", type:"Bearer Bond",            entity:"Horizon Trust Fund",      country:"Tunisia",      riskScore:56, riskLevel:"MEDIUM",   status:"Active",              analyst:"Kwame Mensah",    flagged:"2024-02-01", value:320000  },
];

const GPS_EVENTS = [
  { id:"EVT-001", assetId:"AST-00001", ts:"2024-01-29 02:34", lat:12.38, lon:-1.49, location:"Ouagadougou", country:"Burkina Faso", moveType:"Night Movement",       speed:0,   conf:96.2, border:"NO",  alert:"YES", severity:"CRITICAL" },
  { id:"EVT-002", assetId:"AST-00003", ts:"2024-01-29 09:15", lat:11.85, lon:15.50, location:"N'Djamena",   country:"Chad",         moveType:"Border Crossing",      speed:75,  conf:97.5, border:"YES", alert:"YES", severity:"CRITICAL" },
  { id:"EVT-003", assetId:"AST-00004", ts:"2024-01-29 22:50", lat:13.51, lon:2.12,  location:"Niamey",      country:"Niger",        moveType:"Suspicious Loitering", speed:0,   conf:94.3, border:"NO",  alert:"YES", severity:"HIGH"     },
  { id:"EVT-004", assetId:"AST-00006", ts:"2024-01-30 03:12", lat:16.76, lon:-3.00, location:"Timbuktu",    country:"Mali",         moveType:"Night Movement",       speed:18,  conf:96.8, border:"NO",  alert:"YES", severity:"CRITICAL" },
  { id:"EVT-005", assetId:"AST-00007", ts:"2024-01-30 16:40", lat:15.56, lon:32.54, location:"Khartoum",    country:"Sudan",        moveType:"Border Crossing",      speed:88,  conf:98.1, border:"YES", alert:"YES", severity:"CRITICAL" },
  { id:"EVT-006", assetId:"AST-00002", ts:"2024-01-31 14:20", lat:12.62, lon:-8.02, location:"Bamako",      country:"Mali",         moveType:"Slow Movement",        speed:32,  conf:88.1, border:"NO",  alert:"NO",  severity:"MEDIUM"   },
  { id:"EVT-007", assetId:"AST-00005", ts:"2024-01-31 11:05", lat:11.98, lon:8.51,  location:"Kano",        country:"Nigeria",      moveType:"Fast Transit",         speed:118, conf:82.7, border:"NO",  alert:"NO",  severity:"HIGH"     },
  { id:"EVT-008", assetId:"AST-00008", ts:"2024-02-01 08:25", lat:32.90, lon:13.18, location:"Tripoli",     country:"Libya",        moveType:"Stationary",           speed:0,   conf:79.4, border:"NO",  alert:"NO",  severity:"MEDIUM"   },
];

const AUDIT_LOGS = [
  { id:"LOG-001", ts:"2024-01-29 08:23", userId:"USR-0001", username:"amara.diallo",    action:"FREEZE_REQUEST",  module:"Asset Registry",  target:"AST-00003", desc:"Crypto wallet freeze request submitted to partner agency — $5.1M at risk", outcome:"SUCCESS" },
  { id:"LOG-002", ts:"2024-01-29 09:01", userId:"USR-0005", username:"chidi.kamau",     action:"ESCALATION",      module:"Alert Engine",    target:"AST-00006", desc:"Real estate portfolio case escalated — Trans-Sahara Logistics network link confirmed", outcome:"SUCCESS" },
  { id:"LOG-003", ts:"2024-01-29 09:45", userId:"USR-0003", username:"fatima.ahmed",    action:"LOGIN_FAILED",    module:"Authentication",  target:"USR-0003",  desc:"Failed authentication — account suspended pending security review", outcome:"FAILED"  },
  { id:"LOG-004", ts:"2024-01-29 10:12", userId:"USR-0002", username:"kwame.mensah",    action:"ALERT_TRIGGER",   module:"Alert Engine",    target:"EVT-002",   desc:"AI engine flagged border crossing — 97.5% confidence, N'Djamena checkpoint", outcome:"SUCCESS" },
  { id:"LOG-005", ts:"2024-01-30 07:58", userId:"USR-0004", username:"ibrahim.okonkwo", action:"GPS_INGEST",      module:"GPS Tracker",     target:"EVT-004",   desc:"Batch GPS feed ingested — Night movement in Timbuktu corridor confirmed", outcome:"SUCCESS" },
  { id:"LOG-006", ts:"2024-01-30 11:30", userId:"USR-0008", username:"zara.nkrumah",    action:"RECORD_UPDATE",   module:"Asset Registry",  target:"AST-00007", desc:"Risk score updated to CRITICAL — mobile money network expansion detected", outcome:"SUCCESS" },
  { id:"LOG-007", ts:"2024-01-30 14:22", userId:"USR-0001", username:"amara.diallo",    action:"AI_ANALYSIS",     module:"AI Engine",       target:"N-003",     desc:"AI threat graph analysis completed — 3-hop network identified linking to designated entity", outcome:"SUCCESS" },
  { id:"LOG-008", ts:"2024-01-31 08:45", userId:"USR-0010", username:"halima.mwangi",   action:"REPORT_GENERATE", module:"Reporting",       target:"RPT-0041",  desc:"Financial intelligence report generated for FATF Africa Group submission", outcome:"SUCCESS" },
  { id:"LOG-009", ts:"2024-01-31 10:05", userId:"USR-0002", username:"kwame.mensah",    action:"LOGIN_FAILED",    module:"Authentication",  target:"USR-0002",  desc:"Failed login — anomalous IP geolocation detected (outside operational zone)", outcome:"FAILED"  },
  { id:"LOG-010", ts:"2024-01-31 13:18", userId:"USR-0007", username:"abebe.hassan",    action:"SEIZURE_ORDER",   module:"Legal",           target:"AST-00006", desc:"Seizure order executed — Trans-Sahara Logistics real estate portfolio frozen", outcome:"SUCCESS" },
];

// ── AI RESPONSE TEMPLATES ────────────────────────────────────────
const AI_RESPONSES = {
  default: [
    { delay: 0,    text: "Initializing AQUILA threat analysis engine..." },
    { delay: 1200, text: "Cross-referencing FATF watchlists and INTERPOL Red Notices..." },
    { delay: 2400, text: "Mapping transaction graph — identifying 3-hop network connections..." },
    { delay: 3600, text: "Analysis complete." },
  ],
  "analyze network": {
    title: "THREAT NETWORK ANALYSIS",
    content: `AQUILA AI has identified a **Tier-1 financing network** operating across the Sahel corridor with high confidence (94.7%).

**Key Findings:**
• **Hub entity:** Al-Khalil Trading Co. (N-001) acts as primary value aggregator, connecting 4 sub-networks across Mali, Chad, and Libya
• **Total funds at risk:** $17.4M USD equivalent across 10 identified nodes
• **Highest-risk path:** N-001 → N-003 (Crypto Wallet) → N-004 (NGO) — $6.85M untraced flow
• **Velocity anomaly:** 340% increase in transaction frequency detected over 72h window

**Recommended Actions:**
1. Immediate freeze request on Crypto Wallet 7F2A (N-003) — $5.1M exposure
2. Coordinate with Libyan FIU on Al-Nour Foundation (N-006) accounts
3. Issue INTERPOL Purple Notice on Trans-Sahara Logistics leadership

**Confidence:** 94.7% | **Model:** AQUILA-GRAPH-v2 | **Processing time:** 1.4s`,
  },
  "risk report": {
    title: "RISK ASSESSMENT REPORT",
    content: `**PORTFOLIO RISK SUMMARY — Q1 2024**

**Critical Assets (Action Required):**
• AST-00003 — Crypto Wallet ($5.1M) — FROZEN ✓
• AST-00006 — Real Estate ($2.9M) — SEIZED ✓  
• AST-00007 — Mobile Money ($3.2M) — FROZEN ✓
• AST-00001 — Cash Bundle ($2.4M) — UNDER INVESTIGATION
• AST-00005 — Shell Company ($1.75M) — UNDER INVESTIGATION

**Aggregate Exposure:** $18.3M USD across 10 tracked assets
**Recovery Rate:** 34% ($6.2M frozen/seized)
**Network Disruption Score:** 67/100

**Regional Threat Intensity:**
🔴 Mali — CRITICAL (2 active hubs)
🔴 Libya — CRITICAL (NGO front network)  
🟠 Sudan — HIGH (border transit routes active)
🟠 Niger — HIGH (hawala node confirmed)
🟡 Tunisia — MEDIUM (passive broker node)`,
  },
  "border crossings": {
    title: "BORDER CROSSING INTELLIGENCE",
    content: `**ACTIVE BORDER INCIDENTS — LAST 48H**

**EVT-002 — N'Djamena Checkpoint (CRITICAL)**
• Asset: Crypto Wallet 7F2A (AST-00003)
• Direction: Chad → Sudan
• Speed: 75 km/h | Confidence: 97.5%
• AI Assessment: Known smuggling route — Tibesti corridor match

**EVT-005 — Khartoum Crossing (CRITICAL)**  
• Asset: Al-Nour Foundation Mobile Money (AST-00007)
• Direction: Sudan → Ethiopia
• Speed: 88 km/h | Confidence: 98.1%
• AI Assessment: 3rd crossing in 14 days — pattern matches hawala mule profile

**Predictive Alert:** Based on movement patterns, AQUILA AI projects **72% probability** of a third crossing event in the Niger-Mali border zone within 96 hours.

**Recommended:** Deploy physical surveillance asset to Gao/Menaka corridor.`,
  },
  "who is": {
    title: "ENTITY INTELLIGENCE PROFILE",
    content: `**ENTITY ANALYSIS — Al-Khalil Trading Co.**

**Designation Status:** Under Investigation — FATF VASP Watch
**Jurisdiction:** Registered in Mali, operational in 4 countries
**Established:** 2019 (following dissolution of predecessor entity)

**Financial Intelligence:**
• Total tracked flows: $2.4M (2023-2024)
• Primary currency: XOF (CFA Franc), USD, USDT
• Banking relationships: 3 uncooperative jurisdictions identified

**Network Position:** Central hub — highest betweenness centrality in the tracked graph (0.71)

**Associated Individuals:** 2 flagged persons of interest (names classified)
**Shell Company Links:** Desert Star Holdings, Trans-Sahara Logistics

**AQUILA Threat Score: 94/100 — CRITICAL**
Recommend immediate referral to Egmont Group for financial intelligence exchange.`,
  },
};

const getAIResponse = (query) => {
  const q = query.toLowerCase();
  if (q.includes("network") || q.includes("graph") || q.includes("connect")) return AI_RESPONSES["analyze network"];
  if (q.includes("risk") || q.includes("report") || q.includes("summary")) return AI_RESPONSES["risk report"];
  if (q.includes("border") || q.includes("crossing") || q.includes("transit")) return AI_RESPONSES["border crossings"];
  if (q.includes("who") || q.includes("entity") || q.includes("al-khalil") || q.includes("company")) return AI_RESPONSES["who is"];
  return {
    title: "AQUILA ANALYSIS",
    content: `Query processed: **"${query}"**

**AI Assessment:** No exact pattern match found in current threat database. Initiating broad-spectrum analysis...

**Related Findings:**
• 10 active assets under surveillance across 8 countries
• $18.3M total funds exposure identified
• 5 CRITICAL-rated entities requiring immediate action
• 3 confirmed border crossing incidents in 48h window

**Suggestion:** Try querying "analyze network", "risk report", or "border crossings" for detailed intelligence reports.

**AQUILA Confidence:** 72% | Recommend analyst review for unstructured queries.`,
  };
};

// ═══════════════════════════════════════════════════════════════════
// UTILITY COMPONENTS
// ═══════════════════════════════════════════════════════════════════
const riskColor  = (l) => ({ CRITICAL: T.red, HIGH: T.amber, MEDIUM: "#FFD60A", LOW: T.green }[l] || T.textMid);
const typeColor  = (t) => ({ shell: T.red, crypto: T.purple, ngo: T.amber, hawala: "#FF6B6B", broker: T.accent, front: T.red, trust: T.textMid }[t] || T.accent);
const actionColor= (a) => ({ ALERT_TRIGGER: T.red, ESCALATION: T.amber, FREEZE_REQUEST: T.purple, LOGIN_FAILED: T.red, SEIZURE_ORDER: T.red, AI_ANALYSIS: T.accent, RECORD_UPDATE: T.accent, GPS_INGEST: T.green, REPORT_GENERATE: T.green, LOGIN_SUCCESS: T.green }[a] || T.textMid);
const fmt$       = (n) => n >= 1e6 ? `$${(n/1e6).toFixed(1)}M` : `$${(n/1e3).toFixed(0)}K`;

const Badge = ({ label, color, size = 10 }) => (
  <span style={{ background: color + "20", color, border: `1px solid ${color}50`, borderRadius: 2, padding: `2px ${size === 10 ? 7 : 10}px`, fontSize: size, fontFamily: T.fontMono, letterSpacing: 1.5, whiteSpace: "nowrap", fontWeight: 600 }}>
    {label}
  </span>
);

const GlowDot = ({ color, size = 8, ping = false }) => (
  <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
    <div style={{ width: size, height: size, borderRadius: "50%", background: color, boxShadow: `0 0 ${size}px ${color}` }} />
    {ping && <div style={{ position:"absolute", inset:0, borderRadius:"50%", background: color, animation:"pulse-ring 1.5s ease-out infinite" }} />}
  </div>
);

const SectionLabel = ({ children, accent }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
    <div style={{ width: 2, height: 14, background: accent || T.accent }} />
    <span style={{ fontFamily: T.fontHead, fontSize: 11, fontWeight: 700, letterSpacing: 3, color: T.textMid, textTransform: "uppercase" }}>{children}</span>
  </div>
);

const Divider = () => <div style={{ height: 1, background: T.border, margin: "16px 0" }} />;

// Animated counter
function Counter({ value, duration = 1200 }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let start = 0;
    const step = value / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= value) { setDisplay(value); clearInterval(timer); }
      else setDisplay(Math.floor(start));
    }, 16);
    return () => clearInterval(timer);
  }, [value, duration]);
  return <>{display.toLocaleString()}</>;
}

// Typewriter
function TypeWriter({ text, speed = 18, onDone }) {
  const [shown, setShown] = useState("");
  useEffect(() => {
    setShown("");
    let i = 0;
    const timer = setInterval(() => {
      i++;
      setShown(text.slice(0, i));
      if (i >= text.length) { clearInterval(timer); onDone?.(); }
    }, speed);
    return () => clearInterval(timer);
  }, [text]);
  return <span>{shown}</span>;
}

// Radar spinner
const Radar = ({ size = 60 }) => (
  <div style={{ width: size, height: size, borderRadius: "50%", border: `1px solid ${T.border}`, position: "relative", overflow: "hidden" }}>
    {[0.25, 0.5, 0.75].map(r => (
      <div key={r} style={{ position:"absolute", inset:`${(1-r)*50}%`, borderRadius:"50%", border:`1px solid ${T.border}` }} />
    ))}
    <div style={{ position:"absolute", inset:0, background: `conic-gradient(transparent 270deg, ${T.accent}40 360deg)`, animation:"radar-sweep 2s linear infinite", borderRadius:"50%" }} />
    <div style={{ position:"absolute", top:"50%", left:"50%", width:2, height:"50%", background:T.accent, transformOrigin:"0 0", animation:"radar-sweep 2s linear infinite", opacity:0.8 }} />
  </div>
);

// ═══════════════════════════════════════════════════════════════════
// THREAT NETWORK MAP (SVG canvas)
// ═══════════════════════════════════════════════════════════════════
function ThreatNetworkMap({ onNodeSelect, selectedNode }) {
  const W = 700, H = 420;
  const toXY = (lat, lon) => ({
    x: ((lon + 18) / 70) * (W - 60) + 30,
    y: ((37 - lat) / 72) * (H - 40) + 20,
  });

  const nodePositions = NETWORK_NODES.map(n => ({ ...n, ...toXY(n.lat, n.lon) }));

  const edges = [];
  NETWORK_NODES.forEach(n => {
    n.connections.forEach(cid => {
      const from = nodePositions.find(p => p.id === n.id);
      const to   = nodePositions.find(p => p.id === cid);
      if (from && to && n.id < cid) {
        const bothCritical = n.risk >= 80 && NETWORK_NODES.find(x=>x.id===cid)?.risk >= 80;
        edges.push({ from, to, hot: bothCritical });
      }
    });
  });

  return (
    <div style={{ position: "relative", background: T.bg1, border: `1px solid ${T.border}`, borderRadius: 8, overflow: "hidden" }}>
      {/* Scanline overlay */}
      <div style={{ position:"absolute", inset:0, pointerEvents:"none", zIndex:10, overflow:"hidden" }}>
        <div style={{ position:"absolute", top:0, left:0, right:0, height:2, background:`linear-gradient(transparent, ${T.accent}30, transparent)`, animation:"scanline 4s linear infinite", opacity:0.4 }} />
      </div>
      {/* Grid */}
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width:"100%", display:"block" }}>
        <defs>
          <radialGradient id="mapGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%"   stopColor={T.bg2} />
            <stop offset="100%" stopColor={T.bg0} />
          </radialGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <rect width={W} height={H} fill="url(#mapGrad)" />
        {/* Grid lines */}
        {Array.from({length:9},(_,i)=>(
          <line key={`h${i}`} x1={0} y1={i*H/8} x2={W} y2={i*H/8} stroke={T.border} strokeWidth={0.5} />
        ))}
        {Array.from({length:12},(_,i)=>(
          <line key={`v${i}`} x1={i*W/11} y1={0} x2={i*W/11} y2={H} stroke={T.border} strokeWidth={0.5} />
        ))}
        {/* Africa outline (simplified) */}
        <polygon
          points="195,25 270,20 340,28 395,42 435,68 462,108 478,148 486,190 478,232 464,268 442,298 418,330 392,362 358,390 318,404 278,395 248,372 220,345 198,310 180,272 168,232 162,190 170,148 182,108 192,70"
          fill={T.bg2} stroke={T.borderHi} strokeWidth={1} opacity={0.7}
        />
        {/* Edges */}
        {edges.map((e, i) => (
          <g key={i}>
            <line x1={e.from.x} y1={e.from.y} x2={e.to.x} y2={e.to.y}
              stroke={e.hot ? T.red : T.borderHi} strokeWidth={e.hot ? 1.5 : 1}
              strokeDasharray={e.hot ? "none" : "4,4"} opacity={e.hot ? 0.7 : 0.4}
            />
            {e.hot && (
              <circle r={3} fill={T.red} opacity={0.9}>
                <animateMotion dur="3s" repeatCount="indefinite" path={`M${e.from.x},${e.from.y} L${e.to.x},${e.to.y}`} />
              </circle>
            )}
          </g>
        ))}
        {/* Nodes */}
        {nodePositions.map(n => {
          const color = n.risk >= 85 ? T.red : n.risk >= 70 ? T.amber : T.accent;
          const isSelected = selectedNode?.id === n.id;
          const r = Math.max(8, Math.min(16, n.risk / 8));
          return (
            <g key={n.id} onClick={() => onNodeSelect(n)} style={{ cursor: "pointer" }} filter="url(#glow)">
              {n.risk >= 80 && <circle cx={n.x} cy={n.y} r={r + 8} fill={color} opacity={0.12}>
                <animate attributeName="r" values={`${r+4};${r+14};${r+4}`} dur="2s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.15;0.05;0.15" dur="2s" repeatCount="indefinite" />
              </circle>}
              <circle cx={n.x} cy={n.y} r={r} fill={isSelected ? "#fff" : color} opacity={isSelected ? 1 : 0.9}
                stroke={isSelected ? color : color} strokeWidth={isSelected ? 3 : 1} />
              <circle cx={n.x} cy={n.y} r={r-3} fill={T.bg1} opacity={0.6} />
              <text x={n.x} y={n.y + r + 12} textAnchor="middle" fontSize={8.5} fill={T.textMid} fontFamily={T.fontMono}>
                {n.label.length > 14 ? n.label.slice(0,13)+"…" : n.label}
              </text>
              <text x={n.x} y={n.y + r + 22} textAnchor="middle" fontSize={7.5} fill={color} fontFamily={T.fontMono} fontWeight="bold">
                {n.risk}
              </text>
            </g>
          );
        })}
      </svg>
      {/* Legend */}
      <div style={{ position:"absolute", bottom:12, left:12, background: T.surface+"EE", border:`1px solid ${T.border}`, borderRadius:6, padding:"8px 12px", fontSize:9, fontFamily:T.fontMono }}>
        {[[T.red,"≥85 CRITICAL"],[T.amber,"70-84 HIGH"],[T.accent,"<70 MEDIUM"]].map(([c,l])=>(
          <div key={l} style={{display:"flex",alignItems:"center",gap:6,color:T.textMid,marginBottom:3}}>
            <div style={{width:7,height:7,borderRadius:"50%",background:c,boxShadow:`0 0 4px ${c}`}}/>{l}
          </div>
        ))}
        <div style={{display:"flex",alignItems:"center",gap:6,color:T.textMid,marginTop:4}}>
          <div style={{width:14,height:1.5,background:T.red,opacity:0.7}}/> HOT LINK
        </div>
      </div>
      {/* Live indicator */}
      <div style={{ position:"absolute", top:12, right:12, display:"flex", alignItems:"center", gap:6, background:T.surface+"CC", borderRadius:4, padding:"4px 10px", border:`1px solid ${T.border}` }}>
        <GlowDot color={T.green} size={6} ping />
        <span style={{ fontSize:9, fontFamily:T.fontMono, color:T.green, letterSpacing:2 }}>LIVE FEED</span>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// AI ANALYST PANEL
// ═══════════════════════════════════════════════════════════════════
function AIAnalystPanel() {
  const [messages, setMessages] = useState([
    { role: "system", text: "AQUILA AI ANALYST ONLINE\nCounter-terrorism finance intelligence engine ready.\nAssets tracked: 10 | Active alerts: 5 | Network nodes: 10\n\nType a query or try: 'analyze network' · 'risk report' · 'border crossings'", ts: "NOW" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadStep, setLoadStep] = useState(0);
  const bottomRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loadStep]);

  const formatMd = (text) => {
    return text.split("\n").map((line, i) => {
      const bold = line.replace(/\*\*(.*?)\*\*/g, (_, m) => `<strong style="color:${T.textHi}">${m}</strong>`);
      const isHeader = line.startsWith("**") && line.endsWith("**");
      return <div key={i} style={{ marginBottom: 3, color: isHeader ? T.accent : T.textMid }} dangerouslySetInnerHTML={{ __html: bold }} />;
    });
  };

  const sendQuery = async () => {
    if (!input.trim() || loading) return;
    const query = input.trim();
    setInput("");
    setMessages(m => [...m, { role: "user", text: query, ts: new Date().toLocaleTimeString() }]);
    setLoading(true);
    setLoadStep(0);

    // Simulate AI processing steps
    const steps = AI_RESPONSES.default;
    for (let i = 0; i < steps.length - 1; i++) {
      await new Promise(r => setTimeout(r, steps[i+1].delay - steps[i].delay));
      setLoadStep(i + 1);
    }

    await new Promise(r => setTimeout(r, 600));
    const resp = getAIResponse(query);
    setLoading(false);
    setMessages(m => [...m, { role: "ai", title: resp.title, text: resp.content, ts: new Date().toLocaleTimeString() }]);
  };

  const QUICK = ["analyze network", "risk report", "border crossings", "who is Al-Khalil"];

  return (
    <div style={{ display:"flex", flexDirection:"column", height:"100%", background:T.bg1 }}>
      {/* Header */}
      <div style={{ padding:"14px 20px", borderBottom:`1px solid ${T.border}`, display:"flex", alignItems:"center", gap:12, flexShrink:0 }}>
        <Radar size={36} />
        <div>
          <div style={{ fontFamily:T.fontHead, fontSize:14, fontWeight:700, color:T.accent, letterSpacing:2 }}>AQUILA AI ANALYST</div>
          <div style={{ fontFamily:T.fontMono, fontSize:9, color:T.textMid, letterSpacing:1 }}>THREAT INTELLIGENCE ENGINE · ONLINE</div>
        </div>
        <div style={{ marginLeft:"auto", display:"flex", gap:6 }}>
          {["FATF","INTERPOL","UN-CTED"].map(s=>(
            <span key={s} style={{fontFamily:T.fontMono,fontSize:8,color:T.green,border:`1px solid ${T.green}40`,borderRadius:2,padding:"2px 6px"}}>{s}</span>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex:1, overflowY:"auto", padding:"16px 20px", display:"flex", flexDirection:"column", gap:14 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ animation:"fade-up 0.3s ease" }}>
            {msg.role === "user" ? (
              <div style={{ display:"flex", justifyContent:"flex-end" }}>
                <div style={{ background:`${T.accent}15`, border:`1px solid ${T.accent}40`, borderRadius:"8px 8px 2px 8px", padding:"10px 14px", maxWidth:"80%", fontFamily:T.fontMono, fontSize:12, color:T.textHi }}>
                  <span style={{color:T.accent,marginRight:8}}>›</span>{msg.text}
                </div>
              </div>
            ) : msg.role === "system" ? (
              <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:6, padding:"12px 16px" }}>
                <pre style={{ fontFamily:T.fontMono, fontSize:10, color:T.textMid, whiteSpace:"pre-wrap", lineHeight:1.8 }}>{msg.text}</pre>
              </div>
            ) : (
              <div style={{ background:T.surface, border:`1px solid ${T.borderHi}`, borderRadius:"2px 8px 8px 8px", padding:"14px 16px" }}>
                <div style={{ fontFamily:T.fontHead, fontSize:11, fontWeight:700, color:T.accent, letterSpacing:2, marginBottom:10 }}>⬡ {msg.title}</div>
                <div style={{ fontFamily:T.fontBody, fontSize:12, lineHeight:1.8 }}>{formatMd(msg.text)}</div>
                <div style={{ marginTop:10, fontFamily:T.fontMono, fontSize:9, color:T.textLo }}>AQUILA-v2 · {msg.ts} · Encrypted transmission</div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:"2px 8px 8px 8px", padding:"14px 16px" }}>
            {AI_RESPONSES.default.slice(0, loadStep + 1).map((s, i) => (
              <div key={i} style={{ fontFamily:T.fontMono, fontSize:10, color: i === loadStep ? T.accent : T.textLo, marginBottom:4, display:"flex", alignItems:"center", gap:8 }}>
                <span>{i < loadStep ? "✓" : "›"}</span>
                {i === loadStep ? <TypeWriter text={s.text} speed={15} /> : s.text}
              </div>
            ))}
            {loadStep === AI_RESPONSES.default.length - 1 && (
              <span style={{ fontFamily:T.fontMono, fontSize:10, color:T.accent }} className="ai-typing"> </span>
            )}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Quick prompts */}
      <div style={{ padding:"8px 20px", display:"flex", gap:6, flexWrap:"wrap", borderTop:`1px solid ${T.border}`, flexShrink:0 }}>
        {QUICK.map(q=>(
          <button key={q} onClick={()=>{setInput(q);}} style={{ background:T.surface, border:`1px solid ${T.border}`, color:T.textMid, fontSize:9, fontFamily:T.fontMono, padding:"4px 10px", borderRadius:3, cursor:"pointer", letterSpacing:1 }}>
            {q}
          </button>
        ))}
      </div>

      {/* Input */}
      <div style={{ padding:"12px 20px", borderTop:`1px solid ${T.border}`, display:"flex", gap:8, flexShrink:0 }}>
        <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&sendQuery()}
          placeholder="Query intelligence database..."
          style={{ flex:1, background:T.surface, border:`1px solid ${T.borderHi}`, borderRadius:4, padding:"10px 14px", color:T.textHi, fontSize:12, fontFamily:T.fontMono, outline:"none" }}
        />
        <button onClick={sendQuery} disabled={loading}
          style={{ background: loading ? T.border : T.accent, border:"none", borderRadius:4, padding:"10px 18px", color: loading ? T.textLo : T.bg0, fontSize:12, fontFamily:T.fontHead, fontWeight:700, letterSpacing:2, cursor: loading?"not-allowed":"pointer" }}>
          {loading ? "…" : "SEND"}
        </button>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// VIEWS
// ═══════════════════════════════════════════════════════════════════

// ── COMMAND CENTER (Dashboard) ────────────────────────────────────
function CommandCenter() {
  const [selectedNode, setSelectedNode] = useState(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setTick(x => x + 1), 3000);
    return () => clearInterval(t);
  }, []);

  const totalFunds = NETWORK_NODES.reduce((s,n)=>s+n.funds,0);
  const critCount  = ASSETS.filter(a=>a.riskLevel==="CRITICAL").length;
  const alertCount = GPS_EVENTS.filter(e=>e.alert==="YES").length;

  return (
    <div style={{ display:"grid", gridTemplateColumns:"1fr 340px", gridTemplateRows:"auto 1fr", gap:16, height:"100%", padding:20, overflow:"hidden" }}>
      {/* KPI Strip */}
      <div style={{ gridColumn:"1/-1", display:"flex", gap:12 }}>
        {[
          { label:"TOTAL EXPOSURE",    val:fmt$(totalFunds),           sub:"across tracked network",    color:T.red,    icon:"◈" },
          { label:"CRITICAL ASSETS",   val:critCount,                  sub:"immediate action required", color:T.red,    icon:"⚠" },
          { label:"ACTIVE ALERTS",     val:alertCount,                 sub:"high-confidence events",    color:T.amber,  icon:"◉" },
          { label:"NETWORK NODES",     val:NETWORK_NODES.length,       sub:"entities mapped",           color:T.accent, icon:"⬡" },
          { label:"COUNTRIES COVERED", val:8,                          sub:"operational zones",         color:T.purple, icon:"⊠" },
          { label:"AI CONFIDENCE",     val:"94.7%",                    sub:"threat model accuracy",     color:T.green,  icon:"▲" },
        ].map(k=>(
          <div key={k.label} style={{ flex:1, background:T.surface, border:`1px solid ${T.border}`, borderTop:`2px solid ${k.color}`, borderRadius:6, padding:"14px 16px", animation:"fade-up 0.6s ease" }}>
            <div style={{ fontFamily:T.fontHead, fontSize:9, fontWeight:600, letterSpacing:2.5, color:T.textMid, marginBottom:8 }}>{k.icon} {k.label}</div>
            <div style={{ fontFamily:T.fontMono, fontSize:24, fontWeight:800, color:k.color, lineHeight:1 }}>{k.val}</div>
            <div style={{ fontFamily:T.fontBody, fontSize:10, color:T.textLo, marginTop:5 }}>{k.sub}</div>
          </div>
        ))}
      </div>

      {/* Network map */}
      <div style={{ display:"flex", flexDirection:"column", gap:12, overflow:"hidden" }}>
        <SectionLabel>LIVE THREAT NETWORK — SAHEL &amp; NORTH AFRICA</SectionLabel>
        <ThreatNetworkMap onNodeSelect={setSelectedNode} selectedNode={selectedNode} />
        {/* Recent events ticker */}
        <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:6, padding:"10px 14px" }}>
          <SectionLabel>LIVE INTELLIGENCE FEED</SectionLabel>
          <div style={{ display:"flex", flexDirection:"column", gap:6, maxHeight:120, overflowY:"auto" }}>
            {GPS_EVENTS.filter(e=>e.alert==="YES").slice(0,4).map((e,i)=>(
              <div key={e.id} style={{ display:"flex", alignItems:"center", gap:10, fontFamily:T.fontMono, fontSize:10, animation:`fade-up 0.4s ease ${i*0.1}s both` }}>
                <GlowDot color={e.severity==="CRITICAL"?T.red:T.amber} size={6} ping={i===0} />
                <span style={{color:T.textLo}}>{e.ts}</span>
                <Badge label={e.severity} color={riskColor(e.severity)} size={9} />
                <span style={{color:T.textMid}}>{e.moveType} — {e.location}, {e.country}</span>
                {e.border==="YES" && <Badge label="BORDER" color={T.purple} size={9} />}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right: node detail + AI teaser */}
      <div style={{ display:"flex", flexDirection:"column", gap:12, overflow:"hidden" }}>
        {/* Node detail */}
        <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:6, padding:16, flexShrink:0 }}>
          <SectionLabel>NODE INTELLIGENCE</SectionLabel>
          {!selectedNode ? (
            <div style={{ fontFamily:T.fontMono, fontSize:11, color:T.textLo, lineHeight:2 }}>
              Select a node on the network map<br/>to view entity intelligence profile.
            </div>
          ) : (
            <div style={{ animation:"fade-up 0.3s ease" }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:12 }}>
                <div>
                  <div style={{ fontFamily:T.fontHead, fontSize:16, fontWeight:700, color:T.textHi }}>{selectedNode.label}</div>
                  <div style={{ fontFamily:T.fontMono, fontSize:10, color:T.textMid, marginTop:2 }}>{selectedNode.id} · {selectedNode.country}</div>
                </div>
                <Badge label={selectedNode.risk >= 85 ? "CRITICAL" : selectedNode.risk >= 70 ? "HIGH" : "MEDIUM"} color={selectedNode.risk>=85?T.red:selectedNode.risk>=70?T.amber:T.accent} />
              </div>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:8, marginBottom:12 }}>
                {[["RISK SCORE", selectedNode.risk+"/100", selectedNode.risk>=85?T.red:T.amber],["FUNDS TRACKED",fmt$(selectedNode.funds),T.textHi],["TYPE",selectedNode.type.toUpperCase(),typeColor(selectedNode.type)],["CONNECTIONS",selectedNode.connections.length+" nodes",T.accent]].map(([k,v,c])=>(
                  <div key={k} style={{background:T.bg2,borderRadius:4,padding:"8px 10px"}}>
                    <div style={{fontFamily:T.fontMono,fontSize:8,color:T.textLo,marginBottom:3}}>{k}</div>
                    <div style={{fontFamily:T.fontMono,fontSize:12,color:c,fontWeight:600}}>{v}</div>
                  </div>
                ))}
              </div>
              {/* Risk bar */}
              <div style={{ height:4, background:T.border, borderRadius:2, overflow:"hidden", marginBottom:8 }}>
                <div style={{ width:`${selectedNode.risk}%`, height:"100%", background:`linear-gradient(90deg, ${T.amber}, ${T.red})`, borderRadius:2 }} />
              </div>
              <div style={{ fontFamily:T.fontMono, fontSize:9, color:T.textLo }}>
                Connected to: {selectedNode.connections.join(" · ")}
              </div>
            </div>
          )}
        </div>

        {/* Mini AI panel */}
        <div style={{ flex:1, background:T.surface, border:`1px solid ${T.borderHi}`, borderRadius:6, overflow:"hidden", display:"flex", flexDirection:"column" }}>
          <div style={{ padding:"10px 14px", borderBottom:`1px solid ${T.border}`, display:"flex", alignItems:"center", gap:8, flexShrink:0 }}>
            <GlowDot color={T.accent} size={7} ping />
            <span style={{ fontFamily:T.fontHead, fontSize:11, fontWeight:700, color:T.accent, letterSpacing:2 }}>AQUILA AI — QUICK QUERY</span>
          </div>
          <div style={{ flex:1, padding:"12px 14px", fontFamily:T.fontMono, fontSize:10, color:T.textMid, lineHeight:1.9, overflowY:"auto" }}>
            <span style={{ color:T.green }}>›</span> Engine status: <span style={{ color:T.green }}>ONLINE</span><br/>
            <span style={{ color:T.green }}>›</span> Models loaded: GRAPH-v2, RISK-SCORE-v4, GEO-PATTERN<br/>
            <span style={{ color:T.green }}>›</span> Watchlists synced: FATF, INTERPOL, UN Security Council<br/>
            <span style={{ color:T.textLo }}>Open AI Analyst tab for full intelligence interface →</span>
          </div>
        </div>

        {/* Impact stat */}
        <div style={{ background:`linear-gradient(135deg, ${T.red}15, ${T.surface})`, border:`1px solid ${T.red}40`, borderRadius:6, padding:"14px 16px" }}>
          <div style={{ fontFamily:T.fontHead, fontSize:9, fontWeight:600, letterSpacing:2, color:T.red, marginBottom:8 }}>MISSION IMPACT</div>
          <div style={{ fontFamily:T.fontMono, fontSize:11, color:T.textMid, lineHeight:2 }}>
            <div><span style={{color:T.green}}>$6.2M</span> frozen / seized</div>
            <div><span style={{color:T.accent}}>3 networks</span> disrupted this quarter</div>
            <div><span style={{color:T.amber}}>12 referrals</span> to partner agencies</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── ASSET REGISTRY ────────────────────────────────────────────────
function AssetRegistry() {
  const [search, setSearch]   = useState("");
  const [riskF, setRiskF]     = useState("ALL");
  const [statusF, setStatusF] = useState("ALL");
  const [selected, setSelected] = useState(null);

  const filtered = ASSETS.filter(a => {
    const q = search.toLowerCase();
    return (!q || [a.id,a.type,a.entity,a.country].some(s=>s.toLowerCase().includes(q)))
      && (riskF   === "ALL" || a.riskLevel === riskF)
      && (statusF === "ALL" || a.status    === statusF);
  });

  return (
    <div style={{ display:"flex", height:"100%", overflow:"hidden" }}>
      {/* Table area */}
      <div style={{ flex:1, display:"flex", flexDirection:"column", overflow:"hidden" }}>
        {/* Filters */}
        <div style={{ padding:"16px 24px", borderBottom:`1px solid ${T.border}`, background:T.surface, display:"flex", gap:10, alignItems:"center", flexWrap:"wrap", flexShrink:0 }}>
          <div style={{ position:"relative", flex:1, maxWidth:360 }}>
            <span style={{ position:"absolute", left:12, top:"50%", transform:"translateY(-50%)", color:T.textLo, fontSize:12 }}>⌕</span>
            <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search assets, entities, countries..."
              style={{ width:"100%", background:T.bg2, border:`1px solid ${T.border}`, borderRadius:4, padding:"8px 14px 8px 30px", color:T.textHi, fontSize:11, fontFamily:T.fontMono, outline:"none" }} />
          </div>
          {[["riskF",setRiskF,["ALL","CRITICAL","HIGH","MEDIUM","LOW"],"Risk Level"],["statusF",setStatusF,["ALL","Under Investigation","Frozen","Seized","Active","Watchlist"],"Status"]].map(([key,setter,opts,label])=>(
            <select key={key} onChange={e=>setter(e.target.value)} style={{ background:T.bg2, border:`1px solid ${T.border}`, borderRadius:4, padding:"8px 12px", color:T.textMid, fontSize:11, fontFamily:T.fontMono, cursor:"pointer", outline:"none" }}>
              {opts.map(o=><option key={o} value={o}>{o===opts[0]?`All ${label}s`:o}</option>)}
            </select>
          ))}
          <span style={{ fontFamily:T.fontMono, fontSize:10, color:T.textLo, marginLeft:"auto" }}>{filtered.length} RECORDS</span>
        </div>

        {/* Table */}
        <div style={{ overflowY:"auto", flex:1 }}>
          <table style={{ width:"100%", borderCollapse:"collapse" }}>
            <thead style={{ position:"sticky", top:0, zIndex:5, background:T.surface }}>
              <tr>
                {["ASSET ID","TYPE","ENTITY","COUNTRY","VALUE","RISK SCORE","RISK LEVEL","STATUS","ANALYST"].map(h=>(
                  <th key={h} style={{ padding:"10px 16px", textAlign:"left", fontFamily:T.fontHead, fontSize:9, fontWeight:700, letterSpacing:2, color:T.textLo, borderBottom:`1px solid ${T.border}`, whiteSpace:"nowrap" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((a,i)=>(
                <tr key={a.id} onClick={()=>setSelected(a)} style={{ background: selected?.id===a.id ? `${T.accent}12` : i%2===0 ? T.bg2 : "transparent", cursor:"pointer", borderBottom:`1px solid ${T.border}30`, transition:"background 0.15s" }}>
                  <td style={{ padding:"11px 16px", fontFamily:T.fontMono, fontSize:11, color:T.accent, whiteSpace:"nowrap" }}>{a.id}</td>
                  <td style={{ padding:"11px 16px", fontFamily:T.fontBody, fontSize:12, color:T.textMid, whiteSpace:"nowrap" }}>{a.type}</td>
                  <td style={{ padding:"11px 16px", fontFamily:T.fontBody, fontSize:12, color:T.textHi, maxWidth:180 }}>{a.entity}</td>
                  <td style={{ padding:"11px 16px", fontFamily:T.fontMono, fontSize:11, color:T.textMid }}>{a.country}</td>
                  <td style={{ padding:"11px 16px", fontFamily:T.fontMono, fontSize:11, color:T.green, whiteSpace:"nowrap" }}>{fmt$(a.value)}</td>
                  <td style={{ padding:"11px 16px" }}>
                    <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                      <div style={{ width:52, height:4, background:T.border, borderRadius:2, overflow:"hidden" }}>
                        <div style={{ width:`${a.riskScore}%`, height:"100%", background:`linear-gradient(90deg,${T.amber},${riskColor(a.riskLevel)})` }} />
                      </div>
                      <span style={{ fontFamily:T.fontMono, fontSize:11, color:riskColor(a.riskLevel), fontWeight:600 }}>{a.riskScore}</span>
                    </div>
                  </td>
                  <td style={{ padding:"11px 16px" }}><Badge label={a.riskLevel} color={riskColor(a.riskLevel)} /></td>
                  <td style={{ padding:"11px 16px" }}><Badge label={a.status} color={({Active:T.green,"Under Investigation":T.amber,Frozen:T.accent,Seized:T.red,Watchlist:T.purple,Closed:T.textMid}[a.status]||T.textMid)} /></td>
                  <td style={{ padding:"11px 16px", fontFamily:T.fontBody, fontSize:11, color:T.textLo, whiteSpace:"nowrap" }}>{a.analyst}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail panel */}
      {selected && (
        <div style={{ width:300, background:T.surface, borderLeft:`1px solid ${T.border}`, overflowY:"auto", padding:22, flexShrink:0, animation:"slide-in-right 0.3s ease" }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:18 }}>
            <span style={{ fontFamily:T.fontHead, fontSize:11, fontWeight:700, color:T.textMid, letterSpacing:3 }}>ASSET PROFILE</span>
            <button onClick={()=>setSelected(null)} style={{ background:"none", border:"none", color:T.textLo, cursor:"pointer", fontSize:18, lineHeight:1 }}>×</button>
          </div>
          {/* Risk gauge */}
          <div style={{ background:`${riskColor(selected.riskLevel)}15`, border:`1px solid ${riskColor(selected.riskLevel)}40`, borderRadius:6, padding:"16px 18px", marginBottom:18, textAlign:"center" }}>
            <div style={{ fontFamily:T.fontMono, fontSize:9, color:T.textLo, letterSpacing:2, marginBottom:6 }}>THREAT SCORE</div>
            <div style={{ fontFamily:T.fontMono, fontSize:44, fontWeight:800, color:riskColor(selected.riskLevel), lineHeight:1, textShadow:`0 0 20px ${riskColor(selected.riskLevel)}` }}>{selected.riskScore}</div>
            <div style={{ marginTop:8 }}><Badge label={selected.riskLevel} color={riskColor(selected.riskLevel)} size={11} /></div>
          </div>

          {[["ID",selected.id],["Type",selected.type],["Entity",selected.entity],["Country",selected.country],["Value",fmt$(selected.value)],["Status",selected.status],["Analyst",selected.analyst],["Date Flagged",selected.flagged]].map(([k,v])=>(
            <div key={k} style={{ marginBottom:12, paddingBottom:12, borderBottom:`1px solid ${T.border}` }}>
              <div style={{ fontFamily:T.fontMono, fontSize:9, color:T.textLo, letterSpacing:2, marginBottom:3 }}>{k.toUpperCase()}</div>
              <div style={{ fontFamily:k==="ID"?T.fontMono:T.fontBody, fontSize:12, color: k==="Value"?T.green:T.textHi }}>{v}</div>
            </div>
          ))}

          {/* AI mini-assessment */}
          <div style={{ background:`${T.accent}10`, border:`1px solid ${T.accent}30`, borderRadius:6, padding:"12px 14px" }}>
            <div style={{ fontFamily:T.fontMono, fontSize:9, color:T.accent, letterSpacing:2, marginBottom:8 }}>AQUILA AI ASSESSMENT</div>
            <div style={{ fontFamily:T.fontBody, fontSize:11, color:T.textMid, lineHeight:1.7 }}>
              {selected.riskLevel === "CRITICAL"
                ? `Immediate interdiction recommended. This asset shows patterns consistent with known terrorist financing typologies. Coordinate with regional FIU.`
                : selected.riskLevel === "HIGH"
                ? `Elevated monitoring required. Transaction velocity anomalies detected. Request formal STR from reporting institution.`
                : `Passive surveillance recommended. No immediate action required. Continue monitoring for pattern changes.`}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── AUDIT TRAIL ────────────────────────────────────────────────────
function AuditTrail() {
  const [search, setSearch] = useState("");
  const [actionF, setActionF] = useState("ALL");
  const [outcomeF, setOutcomeF] = useState("ALL");

  const filtered = AUDIT_LOGS.filter(l => {
    const q = search.toLowerCase();
    return (!q || [l.id,l.username,l.action,l.desc,l.target].some(s=>s.toLowerCase().includes(q)))
      && (actionF  === "ALL" || l.action  === actionF)
      && (outcomeF === "ALL" || l.outcome === outcomeF);
  });

  const allActions = [...new Set(AUDIT_LOGS.map(l=>l.action))];

  return (
    <div style={{ display:"flex", flexDirection:"column", height:"100%", overflow:"hidden" }}>
      {/* Filters */}
      <div style={{ padding:"16px 24px", borderBottom:`1px solid ${T.border}`, background:T.surface, display:"flex", gap:10, alignItems:"center", flexShrink:0 }}>
        <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search logs..."
          style={{ flex:1, maxWidth:340, background:T.bg2, border:`1px solid ${T.border}`, borderRadius:4, padding:"8px 14px", color:T.textHi, fontSize:11, fontFamily:T.fontMono, outline:"none" }} />
        <select onChange={e=>setActionF(e.target.value)} style={{ background:T.bg2, border:`1px solid ${T.border}`, borderRadius:4, padding:"8px 12px", color:T.textMid, fontSize:11, fontFamily:T.fontMono, cursor:"pointer", outline:"none" }}>
          <option value="ALL">All Actions</option>
          {allActions.map(a=><option key={a} value={a}>{a}</option>)}
        </select>
        <select onChange={e=>setOutcomeF(e.target.value)} style={{ background:T.bg2, border:`1px solid ${T.border}`, borderRadius:4, padding:"8px 12px", color:T.textMid, fontSize:11, fontFamily:T.fontMono, cursor:"pointer", outline:"none" }}>
          <option value="ALL">All Outcomes</option>
          <option value="SUCCESS">SUCCESS</option>
          <option value="FAILED">FAILED</option>
        </select>
        <span style={{ fontFamily:T.fontMono, fontSize:10, color:T.textLo, marginLeft:"auto" }}>{filtered.length} ENTRIES</span>
      </div>

      {/* Timeline */}
      <div style={{ overflowY:"auto", flex:1, padding:"20px 28px" }}>
        {filtered.map((l, i) => {
          const ac = actionColor(l.action);
          const isFailed = l.outcome === "FAILED";
          return (
            <div key={l.id} style={{ display:"flex", gap:20, marginBottom:0, animation:`fade-up 0.3s ease ${i*0.04}s both` }}>
              {/* Timeline */}
              <div style={{ display:"flex", flexDirection:"column", alignItems:"center", width:16, flexShrink:0, paddingTop:4 }}>
                <div style={{ width:10, height:10, borderRadius:"50%", background: isFailed ? T.red : ac, boxShadow:`0 0 8px ${isFailed?T.red:ac}`, flexShrink:0 }} />
                {i < filtered.length-1 && <div style={{ width:1, flex:1, background:T.border, marginTop:4, marginBottom:0, minHeight:40 }} />}
              </div>
              {/* Card */}
              <div style={{ flex:1, background:isFailed?`${T.red}08`:T.surface, border:`1px solid ${isFailed?T.red+"30":T.border}`, borderRadius:6, padding:"12px 16px", marginBottom:10 }}>
                <div style={{ display:"flex", alignItems:"center", gap:8, flexWrap:"wrap", marginBottom:6 }}>
                  <Badge label={l.action} color={isFailed?T.red:ac} />
                  <span style={{ fontFamily:T.fontMono, fontSize:9, color:T.textLo, background:T.bg2, padding:"2px 8px", borderRadius:3 }}>{l.module}</span>
                  <span style={{ fontFamily:T.fontMono, fontSize:9, color:T.accent }}>{l.target}</span>
                  {isFailed && <Badge label="FAILED" color={T.red} size={9} />}
                  <span style={{ fontFamily:T.fontMono, fontSize:9, color:T.textLo, marginLeft:"auto" }}>{l.ts}</span>
                </div>
                <div style={{ fontFamily:T.fontBody, fontSize:12, color:T.textMid, marginBottom:8, lineHeight:1.5 }}>{l.desc}</div>
                <div style={{ display:"flex", gap:14, fontFamily:T.fontMono, fontSize:9, color:T.textLo }}>
                  <span>👤 <span style={{color:T.accent}}>{l.username}</span></span>
                  <span>🔑 {l.userId}</span>
                  <span>🔗 {l.id}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── SPLASH SCREEN ──────────────────────────────────────────────────
function SplashScreen({ onEnter }) {
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState(0);
  const phases = ["INITIALIZING SECURE CHANNEL…", "LOADING THREAT DATABASE…", "SYNCING PARTNER AGENCIES…", "AQUILATRACE READY"];

  useEffect(() => {
    const t = setInterval(() => {
      setProgress(p => {
        if (p >= 100) { clearInterval(t); setTimeout(onEnter, 500); return 100; }
        return p + 2;
      });
    }, 40);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    setPhase(Math.min(3, Math.floor(progress / 25)));
  }, [progress]);

  return (
    <div style={{ position:"fixed", inset:0, background:T.bg0, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", zIndex:1000, animation:"flicker 8s infinite" }}>
      {/* Animated background */}
      <div style={{ position:"absolute", inset:0, overflow:"hidden", opacity:0.15 }}>
        {Array.from({length:20},(_,i)=>(
          <div key={i} style={{ position:"absolute", left:`${i*5.5}%`, top:0, bottom:0, width:1, background:`linear-gradient(${T.accent}, transparent)`, opacity: Math.random()*0.8+0.2, animationDelay:`${Math.random()*2}s` }} />
        ))}
      </div>

      <div style={{ textAlign:"center", zIndex:1 }}>
        {/* Eagle icon */}
        <div style={{ fontSize:64, marginBottom:24, textShadow:`0 0 40px ${T.accent}`, lineHeight:1 }}>◈</div>

        <div style={{ fontFamily:T.fontHead, fontSize:52, fontWeight:900, color:T.textHi, letterSpacing:8, marginBottom:4 }}>AQUILATRACE</div>
        <div style={{ fontFamily:T.fontMono, fontSize:12, color:T.textMid, letterSpacing:6, marginBottom:48 }}>COUNTER-TERRORISM FINANCE INTELLIGENCE</div>

        {/* Progress bar */}
        <div style={{ width:400, marginBottom:20 }}>
          <div style={{ height:2, background:T.border, borderRadius:1, overflow:"hidden", marginBottom:10 }}>
            <div style={{ width:`${progress}%`, height:"100%", background:`linear-gradient(90deg, ${T.accentDim}, ${T.accent})`, boxShadow:`0 0 12px ${T.accent}`, transition:"width 0.1s" }} />
          </div>
          <div style={{ display:"flex", justifyContent:"space-between", fontFamily:T.fontMono, fontSize:9, color:T.textLo }}>
            <span style={{ color:T.accent }}>{phases[phase]}</span>
            <span>{progress}%</span>
          </div>
        </div>

        {/* Partner logos */}
        <div style={{ display:"flex", gap:16, justifyContent:"center", marginTop:32 }}>
          {["INTERPOL","FATF","AU PEACE & SECURITY","UN CTED","EGMONT GROUP"].map(p=>(
            <span key={p} style={{ fontFamily:T.fontMono, fontSize:8, color:T.textLo, border:`1px solid ${T.border}`, borderRadius:3, padding:"3px 8px", letterSpacing:1 }}>{p}</span>
          ))}
        </div>
      </div>

      {/* Scanline */}
      <div style={{ position:"absolute", inset:0, pointerEvents:"none", backgroundImage:`repeating-linear-gradient(0deg, transparent, transparent 2px, ${T.bg0}08 2px, ${T.bg0}08 4px)` }} />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// ROOT APP
// ═══════════════════════════════════════════════════════════════════
const VIEWS = [
  { id:"command",  label:"COMMAND CENTER", icon:"◈" },
  { id:"ai",       label:"AI ANALYST",     icon:"⬡" },
  { id:"assets",   label:"ASSET REGISTRY", icon:"▤" },
  { id:"audit",    label:"AUDIT TRAIL",    icon:"≡" },
];

export default function AquilaTrace() {
  const [splash, setSplash] = useState(true);
  const [view, setView]     = useState("command");
  const [time, setTime]     = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  if (splash) return <SplashScreen onEnter={() => setSplash(false)} />;

  return (
    <div style={{ display:"flex", flexDirection:"column", height:"100vh", background:T.bg0, color:T.textHi, fontFamily:T.fontBody, overflow:"hidden", animation:"flicker 12s infinite" }}>

      {/* ── TOP NAV ── */}
      <div style={{ display:"flex", alignItems:"stretch", borderBottom:`1px solid ${T.border}`, background:T.surface, flexShrink:0, height:54 }}>
        {/* Brand */}
        <div style={{ display:"flex", alignItems:"center", gap:12, padding:"0 24px", borderRight:`1px solid ${T.border}`, minWidth:220 }}>
          <div style={{ fontSize:22, color:T.accent, textShadow:`0 0 15px ${T.accent}` }}>◈</div>
          <div>
            <div style={{ fontFamily:T.fontHead, fontSize:15, fontWeight:900, color:T.textHi, letterSpacing:4, lineHeight:1 }}>AQUILATRACE</div>
            <div style={{ fontFamily:T.fontMono, fontSize:8, color:T.textLo, letterSpacing:2 }}>INTELLIGENCE PLATFORM</div>
          </div>
        </div>

        {/* Nav */}
        <div style={{ display:"flex", alignItems:"stretch", gap:2, padding:"0 12px", flex:1 }}>
          {VIEWS.map(v => (
            <button key={v.id} onClick={() => setView(v.id)} style={{
              background: view===v.id ? `${T.accent}18` : "transparent",
              border: "none",
              borderBottom: view===v.id ? `2px solid ${T.accent}` : "2px solid transparent",
              color: view===v.id ? T.textHi : T.textLo,
              padding: "0 20px",
              cursor: "pointer",
              fontFamily: T.fontHead,
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: 2,
              display: "flex",
              alignItems: "center",
              gap: 8,
              transition: "all 0.15s",
            }}>
              <span style={{ color: view===v.id ? T.accent : "inherit" }}>{v.icon}</span>
              {v.label}
            </button>
          ))}
        </div>

        {/* Status bar */}
        <div style={{ display:"flex", alignItems:"center", gap:20, padding:"0 24px", borderLeft:`1px solid ${T.border}`, fontFamily:T.fontMono, fontSize:10 }}>
          <div style={{ display:"flex", alignItems:"center", gap:6 }}>
            <GlowDot color={T.green} size={6} ping />
            <span style={{ color:T.green, letterSpacing:1 }}>SECURE</span>
          </div>
          <div style={{ display:"flex", flexDirection:"column", alignItems:"flex-end" }}>
            <span style={{ color:T.textMid, fontSize:9 }}>{time.toUTCString().split(" ").slice(0,-1).join(" ")}</span>
            <span style={{ color:T.textLo, fontSize:8, letterSpacing:1 }}>ANALYST · TOP SECRET</span>
          </div>
        </div>
      </div>

      {/* ── THREAT ALERT BANNER ── */}
      <div style={{ background:`linear-gradient(90deg, ${T.red}25, ${T.red}10, transparent)`, borderBottom:`1px solid ${T.red}30`, padding:"5px 24px", display:"flex", gap:16, alignItems:"center", flexShrink:0 }}>
        <GlowDot color={T.red} size={7} ping />
        <span style={{ fontFamily:T.fontHead, fontSize:10, fontWeight:700, color:T.red, letterSpacing:2 }}>CRITICAL ALERT</span>
        <span style={{ fontFamily:T.fontMono, fontSize:10, color:T.textMid }}>AST-00003 (Crypto Wallet · $5.1M) — Border crossing confirmed N'Djamena checkpoint · Freeze order active</span>
        <span style={{ marginLeft:"auto", fontFamily:T.fontMono, fontSize:9, color:T.textLo }}>EVT-002 · 2024-01-29 09:15 UTC · CONF 97.5%</span>
      </div>

      {/* ── MAIN CONTENT ── */}
      <div style={{ flex:1, overflow:"hidden" }}>
        {view === "command" && <CommandCenter />}
        {view === "ai"      && <AIAnalystPanel />}
        {view === "assets"  && <AssetRegistry />}
        {view === "audit"   && <AuditTrail />}
      </div>

      {/* ── STATUS FOOTER ── */}
      <div style={{ height:24, background:T.bg1, borderTop:`1px solid ${T.border}`, display:"flex", alignItems:"center", gap:20, padding:"0 20px", flexShrink:0 }}>
        {[["NODES",NETWORK_NODES.length],["ASSETS",ASSETS.length],["EVENTS",GPS_EVENTS.length],["LOGS",AUDIT_LOGS.length]].map(([k,v])=>(
          <span key={k} style={{ fontFamily:T.fontMono, fontSize:9, color:T.textLo, letterSpacing:1 }}>{k}: <span style={{color:T.textMid}}>{v}</span></span>
        ))}
        <span style={{ fontFamily:T.fontMono, fontSize:9, color:T.textLo, marginLeft:"auto" }}>AQUILATRACE v1.0 · NIRU HACKATHON 2024 · SECURITY &amp; DEFENCE TRACK</span>
      </div>
    </div>
  );
}


