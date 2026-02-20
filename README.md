import { useState, useEffect, useRef, useCallback } from "react";

// ── Fake data generators ──────────────────────────────────────────────────────
const COUNTRIES = ["Nigeria","Kenya","Senegal","Ghana","Ethiopia","Tanzania","Cameroon","Mali","Niger","Somalia"];
const TYPOLOGIES = ["Mobile Money Smurfing","Hawala Network","Shell Company Layering","Trade Misinvoicing","Cryptocurrency Mixing","NGO Abuse","Commodity Laundering","Cross-Border Structuring"];
const NETWORKS = ["Al-Shabaab","Boko Haram","JNIM","ISIS-Sahel","Unknown Affiliate","Suspected Cell"];
const CURRENCIES = ["KES","NGN","XOF","ETB","TZS","GHS","USD"];

function rnd(a,b){return Math.floor(Math.random()*(b-a+1))+a;}
function pick(arr){return arr[rnd(0,arr.length-1)];}
function randId(){return Math.random().toString(36).slice(2,8).toUpperCase();}
function randAmount(){return (Math.random()*980000+20000).toFixed(2);}
function randScore(){return rnd(40,99);}
function timeSince(n){const d=new Date(Date.now()-n*1000);return d.toLocaleTimeString();}

function generateAlert(){
  const score=randScore();
  return {
    id:`AQT-${randId()}`,
    timestamp:Date.now()-rnd(0,86400)*1000,
    origin:pick(COUNTRIES),
    destination:pick(COUNTRIES),
    amount:randAmount(),
    currency:pick(CURRENCIES),
    typology:pick(TYPOLOGIES),
    network:pick(NETWORKS),
    score,
    severity:score>=85?"CRITICAL":score>=70?"HIGH":score>=55?"MEDIUM":"LOW",
    status:pick(["OPEN","UNDER REVIEW","ESCALATED","FROZEN"]),
    entities:rnd(2,9),
    accounts:rnd(3,18),
  };
}

function generateTransaction(){
  return {
    id:`TXN-${randId()}`,
    from:`ACC-${randId()}`,
    to:`ACC-${randId()}`,
    amount:randAmount(),
    currency:pick(CURRENCIES),
    country:pick(COUNTRIES),
    channel:pick(["Mobile Money","Bank Wire","Crypto","Hawala","Cash","Trade"]),
    flagged:Math.random()>0.65,
    time:Date.now()-rnd(0,3600)*1000,
    score:randScore(),
  };
}

function generateNode(id,type,x,y){
  return {id,type,x,y,risk:rnd(10,99),label:type==="account"?`ACC-${randId()}`:type==="entity"?pick(COUNTRIES):pick(NETWORKS)};
}

// ── Seed data ─────────────────────────────────────────────────────────────────
const INIT_ALERTS = Array.from({length:24},generateAlert);
const INIT_TXN = Array.from({length:40},generateTransaction);

// Static graph for network viz
const GRAPH_NODES = [
  {id:1,type:"entity",x:400,y:220,risk:91,label:"Shell Co. A"},
  {id:2,type:"account",x:200,y:100,risk:78,label:"ACC-NGA01"},
  {id:3,type:"account",x:600,y:100,risk:85,label:"ACC-KEN07"},
  {id:4,type:"entity",x:150,y:320,risk:62,label:"Hawala Node"},
  {id:5,type:"entity",x:650,y:310,risk:93,label:"JNIM Cell"},
  {id:6,type:"account",x:400,y:390,risk:74,label:"ACC-MLI04"},
  {id:7,type:"account",x:250,y:230,risk:55,label:"ACC-SEN02"},
  {id:8,type:"account",x:550,y:230,risk:88,label:"ACC-ETH09"},
  {id:9,type:"entity",x:80,y:190,risk:44,label:"NGO-FRNT"},
];
const GRAPH_EDGES = [
  [1,2],[1,3],[2,4],[3,5],[4,6],[5,6],[7,1],[1,8],[8,5],[9,4],[7,4],[3,8]
];

// ── Colour helpers ────────────────────────────────────────────────────────────
function severityColor(s){
  return s==="CRITICAL"?"#ff2d55":s==="HIGH"?"#ff9f0a":s==="MEDIUM"?"#ffd60a":"#30d158";
}
function riskColor(r){
  return r>=85?"#ff2d55":r>=70?"#ff9f0a":r>=50?"#ffd60a":"#30d158";
}
function statusColor(s){
  return s==="FROZEN"?"#5e5ce6":s==="ESCALATED"?"#ff2d55":s==="UNDER REVIEW"?"#ff9f0a":"#64d2ff";
}

// ── Mini sparkline ────────────────────────────────────────────────────────────
function Sparkline({data,color="#64d2ff",h=32,w=80}){
  const max=Math.max(...data),min=Math.min(...data);
  const pts=data.map((v,i)=>{
    const x=(i/(data.length-1))*w;
    const y=h-((v-min)/(max-min||1))*h;
    return `${x},${y}`;
  }).join(" ");
  return(
    <svg width={w} height={h} style={{display:"block"}}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round"/>
    </svg>
  );
}

// ── Score Ring ────────────────────────────────────────────────────────────────
function ScoreRing({score,size=48}){
  const r=size/2-4,circ=2*Math.PI*r;
  const dash=circ*(score/100);
  const color=riskColor(score);
  return(
    <svg width={size} height={size} style={{transform:"rotate(-90deg)"}}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1c2b3a" strokeWidth="3"/>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="3"
        strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
        style={{transition:"stroke-dasharray 0.5s ease"}}/>
      <text x={size/2} y={size/2+1} textAnchor="middle" dominantBaseline="middle"
        style={{fill:color,fontSize:11,fontWeight:700,fontFamily:"monospace",transform:`rotate(90deg) translate(0,-${size/2}px) translate(${size/2}px,0)`}}>
      </text>
    </svg>
  );
}

// ── Network Graph ─────────────────────────────────────────────────────────────
function NetworkGraph({alerts}){
  const [hover,setHover]=useState(null);
  const [pulse,setPulse]=useState([]);
  useEffect(()=>{
    const t=setInterval(()=>{
      const edge=GRAPH_EDGES[rnd(0,GRAPH_EDGES.length-1)];
      setPulse(p=>[...p.slice(-4),{id:Date.now(),from:edge[0],to:edge[1]}]);
    },1800);
    return()=>clearInterval(t);
  },[]);

  return(
    <div style={{position:"relative",width:"100%",height:"100%"}}>
      <svg width="100%" height="100%" viewBox="0 0 730 450" style={{position:"absolute",inset:0}}>
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        {/* Edges */}
        {GRAPH_EDGES.map(([a,b],i)=>{
          const na=GRAPH_NODES.find(n=>n.id===a);
          const nb=GRAPH_NODES.find(n=>n.id===b);
          return <line key={i} x1={na.x} y1={na.y} x2={nb.x} y2={nb.y}
            stroke="#1e3a4a" strokeWidth="1.5" opacity="0.7"/>;
        })}
        {/* Pulse animations */}
        {pulse.map(p=>{
          const na=GRAPH_NODES.find(n=>n.id===p.from);
          const nb=GRAPH_NODES.find(n=>n.id===p.to);
          if(!na||!nb)return null;
          return(
            <circle key={p.id} r="4" fill="#ff2d55" filter="url(#glow)">
              <animateMotion dur="1.2s" fill="freeze" path={`M${na.x},${na.y} L${nb.x},${nb.y}`}/>
              <animate attributeName="opacity" values="1;0" dur="1.2s" fill="freeze"/>
            </circle>
          );
        })}
        {/* Nodes */}
        {GRAPH_NODES.map(n=>{
          const c=riskColor(n.risk);
          const isH=hover===n.id;
          return(
            <g key={n.id} onMouseEnter={()=>setHover(n.id)} onMouseLeave={()=>setHover(null)}
              style={{cursor:"pointer"}}>
              {isH&&<circle cx={n.x} cy={n.y} r="22" fill={c} opacity="0.12"/>}
              <circle cx={n.x} cy={n.y} r="14" fill="#0d1f2d" stroke={c} strokeWidth={isH?2.5:1.5}
                filter={isH?"url(#glow)":"none"}/>
              <circle cx={n.x} cy={n.y} r="6" fill={c} opacity={isH?1:0.8}/>
              <text x={n.x} y={n.y+26} textAnchor="middle" fill="#7a9bb5" fontSize="9" fontFamily="monospace">
                {n.label}
              </text>
              <text x={n.x} y={n.y+36} textAnchor="middle" fill={c} fontSize="8" fontFamily="monospace">
                RISK {n.risk}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────────────────────────
export default function AquilaTrace(){
  const [tab,setTab]=useState("dashboard");
  const [alerts,setAlerts]=useState(INIT_ALERTS);
  const [txns,setTxns]=useState(INIT_TXN);
  const [selected,setSelected]=useState(null);
  const [filterSev,setFilterSev]=useState("ALL");
  const [filterStatus,setFilterStatus]=useState("ALL");
  const [searchQ,setSearchQ]=useState("");
  const [scanning,setScanning]=useState(false);
  const [scanPct,setScanPct]=useState(0);
  const [newAlertFlash,setNewAlertFlash]=useState(false);
  const [liveMode,setLiveMode]=useState(true);
  const sparkData=useRef(Array.from({length:20},()=>rnd(2,40)));

  // Live feed simulation
  useEffect(()=>{
    if(!liveMode)return;
    const t=setInterval(()=>{
      if(Math.random()>0.55){
        const a=generateAlert();
        setAlerts(prev=>[a,...prev.slice(0,49)]);
        setNewAlertFlash(true);
        setTimeout(()=>setNewAlertFlash(false),800);
      }
      setTxns(prev=>[generateTransaction(),...prev.slice(0,59)]);
      sparkData.current=[...sparkData.current.slice(1),rnd(2,40)];
    },3000);
    return()=>clearInterval(t);
  },[liveMode]);

  // Scan simulation
  const runScan=useCallback(()=>{
    setScanning(true);setScanPct(0);
    const t=setInterval(()=>{
      setScanPct(p=>{
        if(p>=100){clearInterval(t);setScanning(false);return 100;}
        return p+rnd(2,8);
      });
    },120);
  },[]);

  const filteredAlerts=alerts.filter(a=>{
    if(filterSev!=="ALL"&&a.severity!==filterSev)return false;
    if(filterStatus!=="ALL"&&a.status!==filterStatus)return false;
    if(searchQ&&!a.id.includes(searchQ.toUpperCase())&&!a.origin.toLowerCase().includes(searchQ.toLowerCase())&&!a.typology.toLowerCase().includes(searchQ.toLowerCase()))return false;
    return true;
  });

  const critical=alerts.filter(a=>a.severity==="CRITICAL").length;
  const high=alerts.filter(a=>a.severity==="HIGH").length;
  const frozen=alerts.filter(a=>a.status==="FROZEN").length;
  const flaggedTxns=txns.filter(t=>t.flagged).length;

  const css=`
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=DM+Sans:wght@300;400;500&display=swap');
    *{box-sizing:border-box;margin:0;padding:0;}
    body{background:#060e14;font-family:'DM Sans',sans-serif;color:#c8dae8;}
    ::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:#0a1820;}::-webkit-scrollbar-thumb{background:#1e3a4a;border-radius:2px;}
    @keyframes fadeSlide{from{opacity:0;transform:translateY(-8px);}to{opacity:1;transform:translateY(0);}}
    @keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.4;}}
    @keyframes scanLine{0%{top:0;}100%{top:100%;}}
    @keyframes blink{0%,100%{opacity:1;}50%{opacity:0;}}
    @keyframes flash{0%{background:#ff2d5522;}100%{background:transparent;}}
  `;

  const sideNav=[
    {id:"dashboard",icon:"⬡",label:"Dashboard"},
    {id:"alerts",icon:"◈",label:"Alerts"},
    {id:"transactions",icon:"⇄",label:"Transactions"},
    {id:"network",icon:"⬡",label:"Network Graph"},
    {id:"typologies",icon:"⬛",label:"Typologies"},
    {id:"reports",icon:"▣",label:"Reports"},
  ];

  return(
    <>
      <style>{css}</style>
      <div style={{display:"flex",height:"100vh",background:"#060e14",overflow:"hidden"}}>

        {/* Sidebar */}
        <div style={{width:64,background:"#080f17",borderRight:"1px solid #0f2030",display:"flex",flexDirection:"column",alignItems:"center",paddingTop:16,gap:4,flexShrink:0}}>
          {/* Logo */}
          <div style={{width:40,height:40,background:"linear-gradient(135deg,#0a3d5c,#0d5c8a)",borderRadius:8,display:"flex",alignItems:"center",justifyContent:"center",marginBottom:16,fontSize:18}}>
            🦅
          </div>
          {sideNav.map(n=>(
            <button key={n.id} onClick={()=>setTab(n.id)} title={n.label}
              style={{width:44,height:44,background:tab===n.id?"#0d2535":"transparent",border:"none",borderRadius:8,
                color:tab===n.id?"#64d2ff":"#3d6680",fontSize:16,cursor:"pointer",transition:"all 0.15s",
                borderLeft:tab===n.id?"2px solid #64d2ff":"2px solid transparent"}}>
              {n.icon}
            </button>
          ))}
          <div style={{flex:1}}/>
          <div style={{width:8,height:8,borderRadius:"50%",background:liveMode?"#30d158":"#3d6680",
            marginBottom:16,animation:liveMode?"pulse 2s infinite":"none"}} title={liveMode?"Live":"Paused"}/>
        </div>

        {/* Main */}
        <div style={{flex:1,display:"flex",flexDirection:"column",overflow:"hidden"}}>

          {/* Top bar */}
          <div style={{height:52,background:"#080f17",borderBottom:"1px solid #0f2030",
            display:"flex",alignItems:"center",padding:"0 20px",gap:16,flexShrink:0}}>
            <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:18,fontWeight:700,color:"#64d2ff",letterSpacing:2}}>
              AQUILA TRACE
            </div>
            <div style={{fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:"#2d6680",letterSpacing:1,marginTop:2}}>
              CTF INTELLIGENCE PLATFORM v0.1-MVP
            </div>
            <div style={{flex:1}}/>

            {/* Scan button */}
            <button onClick={runScan} disabled={scanning}
              style={{background:scanning?"#0a2535":"#0a3d5c",border:"1px solid #1e5c80",borderRadius:6,
                color:scanning?"#3d6680":"#64d2ff",fontSize:11,fontFamily:"'Share Tech Mono',monospace",
                padding:"6px 14px",cursor:scanning?"not-allowed":"pointer",letterSpacing:1}}>
              {scanning?`SCANNING ${Math.min(scanPct,100)}%`:"▶ RUN SCAN"}
            </button>

            <button onClick={()=>setLiveMode(l=>!l)}
              style={{background:"transparent",border:"1px solid #1e3a4a",borderRadius:6,
                color:liveMode?"#30d158":"#3d6680",fontSize:11,fontFamily:"'Share Tech Mono',monospace",
                padding:"6px 12px",cursor:"pointer",letterSpacing:1}}>
              {liveMode?"● LIVE":"○ PAUSED"}
            </button>

            <div style={{fontSize:10,fontFamily:"'Share Tech Mono',monospace",color:"#3d6680"}}>
              {new Date().toUTCString().slice(0,25)} UTC
            </div>
          </div>

          {/* Content */}
          <div style={{flex:1,overflow:"auto",padding:20}}>

            {/* ── DASHBOARD ── */}
            {tab==="dashboard"&&(
              <div style={{display:"grid",gap:16}}>
                {/* KPI row */}
                <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12}}>
                  {[
                    {label:"CRITICAL ALERTS",value:critical,color:"#ff2d55",sub:`+${rnd(1,5)} last hour`},
                    {label:"HIGH ALERTS",value:high,color:"#ff9f0a",sub:`${alerts.length} total open`},
                    {label:"ACCOUNTS FROZEN",value:frozen,color:"#5e5ce6",sub:"Pending legal review"},
                    {label:"FLAGGED TXNs",value:flaggedTxns,color:"#64d2ff",sub:`of ${txns.length} monitored`},
                  ].map((k,i)=>(
                    <div key={i} style={{background:"#080f17",border:"1px solid #0f2030",borderRadius:10,padding:16,
                      borderTop:`2px solid ${k.color}`,animation:newAlertFlash&&i===0?"flash 0.4s ease":"none"}}>
                      <div style={{fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:"#3d6680",letterSpacing:1,marginBottom:8}}>
                        {k.label}
                      </div>
                      <div style={{fontSize:32,fontWeight:700,fontFamily:"'Rajdhani',sans-serif",color:k.color,lineHeight:1}}>
                        {k.value}
                      </div>
                      <div style={{fontSize:10,color:"#3d6680",marginTop:6}}>{k.sub}</div>
                    </div>
                  ))}
                </div>

                {/* Middle row */}
                <div style={{display:"grid",gridTemplateColumns:"2fr 1fr",gap:12}}>
                  {/* Network graph preview */}
                  <div style={{background:"#080f17",border:"1px solid #0f2030",borderRadius:10,padding:16,height:320}}>
                    <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:12}}>
                      <div style={{fontSize:11,fontFamily:"'Share Tech Mono',monospace",color:"#64d2ff",letterSpacing:1}}>
                        ENTITY NETWORK — ACTIVE CLUSTER
                      </div>
                      <div style={{flex:1}}/>
                      <button onClick={()=>setTab("network")}
                        style={{background:"transparent",border:"1px solid #1e3a4a",borderRadius:4,color:"#3d6680",
                          fontSize:9,padding:"3px 8px",cursor:"pointer",fontFamily:"'Share Tech Mono',monospace"}}>
                        EXPAND ↗
                      </button>
                    </div>
                    <div style={{height:"calc(100% - 36px)"}}>
                      <NetworkGraph alerts={alerts}/>
                    </div>
                  </div>

                  {/* Severity breakdown */}
                  <div style={{display:"flex",flexDirection:"column",gap:12}}>
                    <div style={{background:"#080f17",border:"1px solid #0f2030",borderRadius:10,padding:16,flex:1}}>
                      <div style={{fontSize:11,fontFamily:"'Share Tech Mono',monospace",color:"#64d2ff",letterSpacing:1,marginBottom:12}}>
                        ALERT SEVERITY
                      </div>
                      {["CRITICAL","HIGH","MEDIUM","LOW"].map(s=>{
                        const cnt=alerts.filter(a=>a.severity===s).length;
                        const pct=Math.round(cnt/alerts.length*100);
                        return(
                          <div key={s} style={{marginBottom:10}}>
                            <div style={{display:"flex",justifyContent:"space-between",fontSize:10,marginBottom:4}}>
                              <span style={{color:severityColor(s),fontFamily:"'Share Tech Mono',monospace",fontSize:9}}>{s}</span>
                              <span style={{color:"#3d6680",fontFamily:"'Share Tech Mono',monospace",fontSize:9}}>{cnt} / {pct}%</span>
                            </div>
                            <div style={{height:4,background:"#0f2030",borderRadius:2,overflow:"hidden"}}>
                              <div style={{height:"100%",width:`${pct}%`,background:severityColor(s),borderRadius:2,transition:"width 0.5s"}}/>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    <div style={{background:"#080f17",border:"1px solid #0f2030",borderRadius:10,padding:16,flex:1}}>
                      <div style={{fontSize:11,fontFamily:"'Share Tech Mono',monospace",color:"#64d2ff",letterSpacing:1,marginBottom:12}}>
                        TOP TYPOLOGIES
                      </div>
                      {Object.entries(
                        alerts.reduce((acc,a)=>{acc[a.typology]=(acc[a.typology]||0)+1;return acc;},{})
                      ).sort((a,b)=>b[1]-a[1]).slice(0,4).map(([t,c])=>(
                        <div key={t} style={{display:"flex",justifyContent:"space-between",marginBottom:8,fontSize:10}}>
                          <span style={{color:"#7a9bb5"}}>{t.split(" ").slice(0,3).join(" ")}</span>
                          <span style={{color:"#ff9f0a",fontFamily:"'Share Tech Mono',monospace",fontSize:9}}>{c}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Recent alerts table */}
                <div style={{background:"#080f17",border:"1px solid #0f2030",borderRadius:10,padding:16}}>
                  <div style={{display:"flex",alignItems:"center",marginBottom:12}}>
                    <div style={{fontSize:11,fontFamily:"'Share Tech Mono',monospace",color:"#64d2ff",letterSpacing:1}}>
                      RECENT ALERTS
                    </div>
                    <div style={{flex:1}}/>
                    <button onClick={()=>setTab("alerts")}
                      style={{background:"transparent",border:"1px solid #1e3a4a",borderRadius:4,color:"#3d6680",
                        fontSize:9,padding:"3px 8px",cursor:"pointer",fontFamily:"'Share Tech Mono',monospace"}}>
                      VIEW ALL ↗
                    </button>
                  </div>
                  <AlertTable alerts={alerts.slice(0,8)} onSelect={a=>{setSelected(a);setTab("alerts");}}/>
                </div>
              </div>
            )}

            {/* ── ALERTS ── */}
            {tab==="alerts"&&(
              <div style={{display:"grid",gridTemplateColumns:selected?"1fr 380px":"1fr",gap:16}}>
                <div>
                  {/* Filters */}
                  <div style={{display:"flex",gap:10,marginBottom:14,flexWrap:"wrap"}}>
                    <input value={searchQ} onChange={e=>setSearchQ(e.target.value)}
                      placeholder="Search ID, country, typology…"
                      style={{background:"#0a1820",border:"1px solid #1e3a4a",borderRadius:6,color:"#c8dae8",
                        padding:"7px 12px",fontSize:11,flex:1,minWidth:200,fontFamily:"'Share Tech Mono',monospace",outline:"none"}}/>
                    {["ALL","CRITICAL","HIGH","MEDIUM","LOW"].map(s=>(
                      <button key={s} onClick={()=>setFilterSev(s)}
                        style={{background:filterSev===s?"#0a3d5c":"transparent",border:"1px solid",
                          borderColor:filterSev===s?"#64d2ff":"#1e3a4a",borderRadius:6,
                          color:filterSev===s?"#64d2ff":"#3d6680",fontSize:9,padding:"6px 10px",
                          cursor:"pointer",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1}}>
                        {s}
                      </button>
                    ))}
                    {["ALL","OPEN","UNDER REVIEW","ESCALATED","FROZEN"].map(s=>(
                      <button key={s} onClick={()=>setFilterStatus(s)}
                        style={{background:filterStatus===s?"#0a2535":"transparent",border:"1px solid",
                          borderColor:filterStatus===s?"#5e5ce6":"#1e3a4a",borderRadius:6,
                          color:filterStatus===s?"#9b9fff":"#3d6680",fontSize:9,padding:"6px 10px",
                          cursor:"pointer",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1}}>
                        {s}
                      </button>
                    ))}
                    <div style={{fontSize:10,color:"#3d6680",alignSelf:"center",fontFamily:"'Share Tech Mono',monospace"}}>
                      {filteredAlerts.length} results
                    </div>
                  </div>
                  <AlertTable alerts={filteredAlerts} onSelect={setSelected} selectedId={selected?.id}/>
                </div>

                {/* Detail panel */}
                {selected&&(
                  <div style={{background:"#080f17",border:"1px solid #0f2030",borderRadius:10,padding:20,
                    animation:"fadeSlide 0.2s ease",alignSelf:"start",position:"sticky",top:0}}>
                    <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:16}}>
                      <div>
                        <div style={{fontFamily:"'Share Tech Mono',monospace",fontSize:13,color:"#64d2ff"}}>{selected.id}</div>
                        <div style={{fontSize:10,color:"#3d6680",marginTop:3}}>{new Date(selected.timestamp).toLocaleString()}</div>
                      </div>
                      <button onClick={()=>setSelected(null)}
                        style={{background:"transparent",border:"none",color:"#3d6680",cursor:"pointer",fontSize:18}}>×</button>
                    </div>

                    {/* Score ring */}
                    <div style={{display:"flex",alignItems:"center",gap:16,marginBottom:20,
                      padding:14,background:"#0a1820",borderRadius:8,border:"1px solid #0f2030"}}>
                      <div style={{position:"relative",width:64,height:64}}>
                        <ScoreRing score={selected.score} size={64}/>
                        <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",
                          fontFamily:"'Rajdhani',sans-serif",fontSize:16,fontWeight:700,color:riskColor(selected.score)}}>
                          {selected.score}
                        </div>
                      </div>
                      <div>
                        <div style={{fontSize:9,color:"#3d6680",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1}}>RISK SCORE</div>
                        <div style={{fontSize:18,fontFamily:"'Rajdhani',sans-serif",fontWeight:700,
                          color:severityColor(selected.severity)}}>{selected.severity}</div>
                        <div style={{fontSize:10,color:statusColor(selected.status),marginTop:2,fontFamily:"'Share Tech Mono',monospace",fontSize:9}}>
                          ● {selected.status}
                        </div>
                      </div>
                    </div>

                    {/* Fields */}
                    {[
                      ["TYPOLOGY",selected.typology],
                      ["NETWORK",selected.network],
                      ["ORIGIN",selected.origin],
                      ["DESTINATION",selected.destination],
                      ["AMOUNT",`${parseFloat(selected.amount).toLocaleString()} ${selected.currency}`],
                      ["ENTITIES",`${selected.entities} linked entities`],
                      ["ACCOUNTS",`${selected.accounts} accounts`],
                    ].map(([k,v])=>(
                      <div key={k} style={{display:"flex",justifyContent:"space-between",padding:"8px 0",
                        borderBottom:"1px solid #0f2030",fontSize:11}}>
                        <span style={{color:"#3d6680",fontFamily:"'Share Tech Mono',monospace",fontSize:9,letterSpacing:1}}>{k}</span>
                        <span style={{color:"#c8dae8",textAlign:"right",maxWidth:200}}>{v}</span>
                      </div>
                    ))}

                    {/* AI Rationale */}
                    <div style={{marginTop:16,padding:12,background:"#0a1820",borderRadius:8,border:"1px solid #1e3a4a"}}>
                      <div style={{fontSize:9,color:"#64d2ff",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:8}}>
                        ◈ AI RATIONALE
                      </div>
                      <div style={{fontSize:11,color:"#7a9bb5",lineHeight:1.6}}>
                        Detected {selected.typology.toLowerCase()} pattern across {selected.accounts} accounts 
                        in {selected.origin}→{selected.destination} corridor. 
                        Graph analysis identified {selected.entities} co-located entities with 
                        transaction velocity anomaly. Confidence: {selected.score}%.
                      </div>
                    </div>

                    {/* Actions */}
                    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8,marginTop:16}}>
                      {[
                        {label:"FREEZE ACCOUNTS",color:"#5e5ce6"},
                        {label:"ESCALATE",color:"#ff2d55"},
                        {label:"ASSIGN",color:"#64d2ff"},
                        {label:"EXPORT REPORT",color:"#30d158"},
                      ].map(a=>(
                        <button key={a.label}
                          style={{background:"transparent",border:`1px solid ${a.color}`,borderRadius:6,
                            color:a.color,fontSize:9,padding:"8px",cursor:"pointer",
                            fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,
                            transition:"background 0.15s"}}
                          onMouseEnter={e=>e.target.style.background=a.color+"22"}
                          onMouseLeave={e=>e.target.style.background="transparent"}>
                          {a.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── TRANSACTIONS ── */}
            {tab==="transactions"&&(
              <div>
                <div style={{display:"flex",alignItems:"center",gap:12,marginBottom:16}}>
                  <div style={{fontFamily:"'Share Tech Mono',monospace",fontSize:11,color:"#64d2ff",letterSpacing:1}}>
                    TRANSACTION MONITOR
                  </div>
                  <div style={{background:"#0a1820",border:"1px solid #1e3a4a",borderRadius:6,padding:"4px 10px",
                    fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:"#ff9f0a"}}>
                    {flaggedTxns} FLAGGED
                  </div>
                  <div style={{flex:1}}/>
                  <Sparkline data={sparkData.current} color="#64d2ff" h={24} w={80}/>
                </div>
                <div style={{background:"#080f17",border:"1px solid #0f2030",borderRadius:10,overflow:"hidden"}}>
                  <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr 1fr 1fr 80px 60px",
                    padding:"10px 16px",background:"#060e14",borderBottom:"1px solid #0f2030",
                    fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:"#3d6680",letterSpacing:1}}>
                    {["TXN ID","FROM","TO","AMOUNT","CHANNEL","COUNTRY","RISK"].map(h=>(
                      <div key={h}>{h}</div>
                    ))}
                  </div>
                  <div style={{maxHeight:"calc(100vh - 200px)",overflowY:"auto"}}>
                    {txns.map((t,i)=>(
                      <div key={t.id} style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr 1fr 1fr 80px 60px",
                        padding:"10px 16px",borderBottom:"1px solid #0a1820",fontSize:11,
                        background:t.flagged?"#160a0a":i%2===0?"#080f17":"#060e14",
                        animation:i===0?"fadeSlide 0.3s ease":"none",
                        transition:"background 0.15s"}}>
                        <div style={{fontFamily:"'Share Tech Mono',monospace",fontSize:10,color:t.flagged?"#ff2d55":"#64d2ff"}}>{t.id}</div>
                        <div style={{fontFamily:"'Share Tech Mono',monospace",fontSize:9,color:"#7a9bb5"}}>{t.from}</div>
                        <div style={{fontFamily:"'Share Tech Mono',monospace",fontSize:9,color:"#7a9bb5"}}>{t.to}</div>
                        <div style={{color:"#c8dae8",fontSize:10}}>{parseFloat(t.amount).toLocaleString()} <span style={{fontSize:8,color:"#3d6680"}}>{t.currency}</span></div>
                        <div style={{fontSize:10,color:"#5a8aaa"}}>{t.channel}</div>
                        <div style={{fontSize:10,color:"#7a9bb5"}}>{t.country}</div>
                        <div style={{fontSize:10,color:riskColor(t.score),fontFamily:"'Share Tech Mono',monospace"}}>{t.score}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ── NETWORK GRAPH ── */}
            {tab==="network"&&(
              <div style={{background:"#080f17",border:"1px solid #0f2030",borderRadius:10,padding:20,height:"calc(100vh - 120px)"}}>
                <div style={{display:"flex",alignItems:"center",gap:12,marginBottom:16}}>
                  <div style={{fontFamily:"'Share Tech Mono',monospace",fontSize:11,color:"#64d2ff",letterSpacing:1}}>
                    ENTITY RELATIONSHIP NETWORK
                  </div>
                  <div style={{flex:1}}/>
                  {[{c:"#ff2d55",l:"High Risk"},{c:"#ff9f0a",l:"Medium"},{c:"#30d158",l:"Low"}].map(l=>(
                    <div key={l.l} style={{display:"flex",alignItems:"center",gap:5,fontSize:10,color:"#7a9bb5"}}>
                      <div style={{width:8,height:8,borderRadius:"50%",background:l.c}}/>
                      {l.l}
                    </div>
                  ))}
                </div>
                <div style={{height:"calc(100% - 48px)",position:"relative"}}>
                  <NetworkGraph alerts={alerts}/>
                  <div style={{position:"absolute",bottom:16,left:16,background:"#060e14",border:"1px solid #0f2030",
                    borderRadius:8,padding:12,fontSize:10,color:"#3d6680",fontFamily:"'Share Tech Mono',monospace"}}>
                    <div style={{marginBottom:4}}>● Animated pulses = active money movement</div>
                    <div>◈ Node size = risk score</div>
                  </div>
                </div>
              </div>
            )}

            {/* ── TYPOLOGIES ── */}
            {tab==="typologies"&&(
              <div style={{display:"grid",gridTemplateColumns:"repeat(2,1fr)",gap:16}}>
                {TYPOLOGIES.map(t=>{
                  const cnt=alerts.filter(a=>a.typology===t).length;
                  const pct=Math.round(cnt/alerts.length*100);
                  const countries=[...new Set(alerts.filter(a=>a.typology===t).map(a=>a.origin))].slice(0,3);
                  return(
                    <div key={t} style={{background:"#080f17",border:"1px solid #0f2030",borderRadius:10,padding:20,
                      borderLeft:"3px solid #1e5c80",transition:"border-color 0.2s",cursor:"pointer"}}
                      onMouseEnter={e=>e.currentTarget.style.borderLeftColor="#64d2ff"}
                      onMouseLeave={e=>e.currentTarget.style.borderLeftColor="#1e5c80"}>
                      <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:16,fontWeight:600,color:"#c8dae8",marginBottom:4}}>
                        {t}
                      </div>
                      <div style={{display:"flex",gap:12,marginBottom:12}}>
                        <span style={{fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:"#ff9f0a"}}>{cnt} ALERTS</span>
                        <span style={{fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:"#3d6680"}}>{pct}% OF TOTAL</span>
                      </div>
                      <div style={{height:4,background:"#0f2030",borderRadius:2,marginBottom:12}}>
                        <div style={{height:"100%",width:`${pct}%`,background:"linear-gradient(90deg,#0a4d6e,#64d2ff)",borderRadius:2}}/>
                      </div>
                      <div style={{display:"flex",gap:6}}>
                        {countries.map(c=>(
                          <span key={c} style={{background:"#0a1820",border:"1px solid #1e3a4a",borderRadius:4,
                            padding:"2px 8px",fontSize:9,color:"#5a8aaa",fontFamily:"'Share Tech Mono',monospace"}}>
                            {c}
                          </span>
                        ))}
                      </div>
                      <div style={{marginTop:12,fontSize:11,color:"#4d7a99",lineHeight:1.5}}>
                        {t==="Mobile Money Smurfing"&&"Structuring transactions below reporting thresholds across mobile wallets to avoid detection."}
                        {t==="Hawala Network"&&"Informal value transfer exploiting unregistered brokers across porous border regions."}
                        {t==="Shell Company Layering"&&"Multi-jurisdiction shell structures used to obscure beneficial ownership of terror funds."}
                        {t==="Trade Misinvoicing"&&"Over/under-invoicing of goods to disguise value transfers through legitimate trade channels."}
                        {t==="Cryptocurrency Mixing"&&"Use of mixers and chain-hopping to sever the transaction trail on-chain."}
                        {t==="NGO Abuse"&&"Exploitation of registered non-profits as conduits for moving and legitimizing terrorist financing."}
                        {t==="Commodity Laundering"&&"Use of cattle, gold, and agricultural goods as value stores and transfer mechanisms."}
                        {t==="Cross-Border Structuring"&&"Coordinated multi-country structuring designed to exploit differing AML reporting thresholds."}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* ── REPORTS ── */}
            {tab==="reports"&&(
              <div style={{display:"grid",gap:16}}>
                <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12}}>
                  {[
                    {title:"Weekly Intelligence Summary",date:"Feb 17–23, 2025",status:"READY",color:"#30d158"},
                    {title:"JNIM Network Exposure Report",date:"Feb 20, 2025",status:"READY",color:"#30d158"},
                    {title:"Mobile Money Typology Brief",date:"Feb 19, 2025",status:"GENERATING",color:"#ff9f0a"},
                    {title:"Nigeria-Kenya Corridor Analysis",date:"Feb 18, 2025",status:"READY",color:"#30d158"},
                    {title:"Crypto Mixing Cluster Report",date:"Feb 15, 2025",status:"READY",color:"#30d158"},
                    {title:"Q1 Regional Threat Assessment",date:"Mar 1, 2025",status:"SCHEDULED",color:"#3d6680"},
                  ].map((r,i)=>(
                    <div key={i} style={{background:"#080f17",border:"1px solid #0f2030",borderRadius:10,padding:20,
                      cursor:"pointer",transition:"border-color 0.2s"}}
                      onMouseEnter={e=>e.currentTarget.style.borderColor="#1e3a4a"}
                      onMouseLeave={e=>e.currentTarget.style.borderColor="#0f2030"}>
                      <div style={{display:"flex",justifyContent:"space-between",marginBottom:12}}>
                        <div style={{fontSize:22,color:"#1e3a4a"}}>▣</div>
                        <span style={{fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:r.color,letterSpacing:1}}>
                          ● {r.status}
                        </span>
                      </div>
                      <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:15,fontWeight:600,color:"#c8dae8",marginBottom:6}}>
                        {r.title}
                      </div>
                      <div style={{fontSize:10,color:"#3d6680",fontFamily:"'Share Tech Mono',monospace"}}>{r.date}</div>
                    </div>
                  ))}
                </div>
                <div style={{background:"#080f17",border:"1px solid #0f2030",borderRadius:10,padding:20}}>
                  <div style={{fontFamily:"'Share Tech Mono',monospace",fontSize:11,color:"#64d2ff",letterSpacing:1,marginBottom:16}}>
                    PLATFORM STATISTICS
                  </div>
                  <div style={{display:"grid",gridTemplateColumns:"repeat(5,1fr)",gap:16}}>
                    {[
                      {l:"Total Alerts Processed",v:alerts.length+4821},
                      {l:"Accounts Frozen (30d)",v:frozen+142},
                      {l:"Intelligence Packages",v:87},
                      {l:"FIUs Connected",v:6},
                      {l:"Avg Detection Time",v:"4.2 hrs"},
                    ].map((s,i)=>(
                      <div key={i}>
                        <div style={{fontSize:9,color:"#3d6680",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:4}}>{s.l}</div>
                        <div style={{fontSize:24,fontFamily:"'Rajdhani',sans-serif",fontWeight:700,color:"#64d2ff"}}>{s.v}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </>
  );
}

// ── Alert table component ─────────────────────────────────────────────────────
function AlertTable({alerts,onSelect,selectedId}){
  const cols=["ID","SEVERITY","ORIGIN→DEST","AMOUNT","TYPOLOGY","NETWORK","SCORE","STATUS"];
  return(
    <div style={{background:"#080f17",border:"1px solid #0f2030",borderRadius:10,overflow:"hidden"}}>
      <div style={{display:"grid",gridTemplateColumns:"100px 80px 160px 130px 200px 140px 60px 100px",
        padding:"10px 16px",background:"#060e14",borderBottom:"1px solid #0f2030",
        fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:"#3d6680",letterSpacing:1}}>
        {cols.map(c=><div key={c}>{c}</div>)}
      </div>
      <div style={{overflowY:"auto",maxHeight:"60vh"}}>
        {alerts.map((a,i)=>(
          <div key={a.id} onClick={()=>onSelect(a)}
            style={{display:"grid",gridTemplateColumns:"100px 80px 160px 130px 200px 140px 60px 100px",
              padding:"10px 16px",borderBottom:"1px solid #0a1820",fontSize:11,cursor:"pointer",
              background:a.id===selectedId?"#0a2535":i%2===0?"#080f17":"#060e14",
              animation:i===0?"fadeSlide 0.3s ease":"none",
              transition:"background 0.1s"}}
            onMouseEnter={e=>a.id!==selectedId&&(e.currentTarget.style.background="#0a1820")}
            onMouseLeave={e=>a.id!==selectedId&&(e.currentTarget.style.background=i%2===0?"#080f17":"#060e14")}>
            <div style={{fontFamily:"'Share Tech Mono',monospace",fontSize:10,color:"#64d2ff"}}>{a.id}</div>
            <div style={{color:severityColor(a.severity),fontSize:9,fontFamily:"'Share Tech Mono',monospace",fontWeight:700}}>{a.severity}</div>
            <div style={{fontSize:10,color:"#7a9bb5"}}>{a.origin} → {a.destination}</div>
            <div style={{fontSize:10,color:"#c8dae8"}}>{parseFloat(a.amount).toLocaleString()} <span style={{fontSize:8,color:"#3d6680"}}>{a.currency}</span></div>
            <div style={{fontSize:10,color:"#5a8aaa"}}>{a.typology}</div>
            <div style={{fontSize:10,color:"#7a9bb5"}}>{a.network}</div>
            <div style={{fontSize:11,fontFamily:"'Share Tech Mono',monospace",color:riskColor(a.score),fontWeight:700}}>{a.score}</div>
            <div style={{fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:statusColor(a.status)}}>● {a.status}</div>
          </div>
        ))}
      </div>
    </div>
  );
}




