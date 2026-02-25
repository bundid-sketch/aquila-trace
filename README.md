import { useState, useEffect, useRef, useCallback } from "react";

// ═══════════════════════════════════════════════════════════════════════════════
// CONSTANTS & DATA
// ═══════════════════════════════════════════════════════════════════════════════
const COUNTRIES = ["Nigeria","Kenya","Senegal","Ghana","Ethiopia","Tanzania","Cameroon","Mali","Niger","Somalia","Sudan","DRC","Uganda","Mozambique","Chad"];
const TYPOLOGIES = ["Mobile Money Smurfing","Hawala Network","Shell Company Layering","Trade Misinvoicing","Cryptocurrency Mixing","NGO Abuse","Commodity Laundering","Cross-Border Structuring"];
const NETWORKS   = ["Al-Shabaab","Boko Haram","JNIM","ISIS-Sahel","Wagner-Linked","Unknown Affiliate","Suspected Cell"];
const CURRENCIES = ["KES","NGN","XOF","ETB","TZS","GHS","USD","XAF"];
const CHANNELS   = ["Mobile Money","Bank Wire","Crypto","Hawala","Cash","Trade Finance","Remittance"];

const ML_MODELS = [
  { id:"gnn",  name:"Graph Neural Network",  short:"GNN",     color:"#64d2ff", framework:"PyTorch Geometric", status:"DEPLOYED", version:"v3.1.2", accuracy:94.2, precision:91.8, recall:96.1, f1:93.9, fpr:4.3,  latency:38,  params:"47M",       lastTrained:"2025-02-18", samples:2840000,
    desc:"Detects suspicious entity clusters via multi-hop message-passing over transaction graphs.",
    features:[{f:"Degree centrality",v:88},{f:"Betweenness",v:74},{f:"Edge velocity",v:69},{f:"Cluster coeff.",v:61},{f:"Node embedding",v:55}] },
  { id:"xgb",  name:"XGBoost Ensemble",      short:"XGB",     color:"#30d158", framework:"XGBoost 2.0",       status:"DEPLOYED", version:"v5.0.1", accuracy:91.5, precision:89.3, recall:92.4, f1:90.8, fpr:7.1,  latency:12,  params:"2.1M trees", lastTrained:"2025-02-21", samples:6100000,
    desc:"Gradient-boosted tree ensemble on tabular transaction features. Primary individual scorer.",
    features:[{f:"Txn velocity",v:92},{f:"Amount delta",v:83},{f:"Time-of-day",v:71},{f:"Cross-border",v:68},{f:"Account age",v:52}] },
  { id:"lstm", name:"LSTM Sequence Model",   short:"LSTM",    color:"#ff9f0a", framework:"TensorFlow 2.15",   status:"DEPLOYED", version:"v2.4.0", accuracy:89.7, precision:87.1, recall:91.9, f1:89.4, fpr:9.2,  latency:61,  params:"18M",        lastTrained:"2025-02-10", samples:1920000,
    desc:"Bidirectional LSTM capturing temporal behaviour patterns over 90-day rolling windows.",
    features:[{f:"Seq. entropy",v:86},{f:"Burst pattern",v:79},{f:"Dormancy break",v:73},{f:"Recip. pattern",v:64},{f:"Hour variance",v:48}] },
  { id:"iso",  name:"Isolation Forest",      short:"iForest", color:"#bf5af2", framework:"scikit-learn 1.4",  status:"DEPLOYED", version:"v1.9.3", accuracy:82.3, precision:78.6, recall:86.0, f1:82.1, fpr:14.8, latency:8,   params:"500 trees",  lastTrained:"2025-02-01", samples:9200000,
    desc:"Unsupervised zero-day anomaly detector — catches novel typologies with no labelled examples.",
    features:[{f:"Isolation depth",v:95},{f:"Path length var.",v:81},{f:"Feature outlier",v:70},{f:"Sparse region",v:58},{f:"Contam. score",v:44}] },
  { id:"bert", name:"FinBERT NLP Engine",    short:"BERT",    color:"#ff6b6b", framework:"HuggingFace 4.38",  status:"STAGING",  version:"v1.2.0β",accuracy:88.1, precision:85.4, recall:90.7, f1:87.9, fpr:11.3, latency:145, params:"110M",       lastTrained:"2025-02-22", samples:840000,
    desc:"Fine-tuned BERT classifying memo lines and entity names for suspicious language patterns.",
    features:[{f:"Memo keywords",v:90},{f:"Entity NER",v:82},{f:"Language model",v:75},{f:"Semantic sim.",v:67},{f:"Token anomaly",v:53}] },
  { id:"gcn",  name:"GCN Risk Propagator",   short:"GCN",     color:"#ffd60a", framework:"DGL + PyTorch",     status:"TRAINING", version:"v0.8.0rc",accuracy:90.4, precision:88.2, recall:92.8, f1:90.4, fpr:8.6,  latency:52,  params:"23M",        lastTrained:"2025-02-23", samples:3400000,
    desc:"Graph Convolutional Network propagating risk scores from flagged seed nodes.",
    features:[{f:"Prop. depth",v:89},{f:"Seed risk",v:84},{f:"Edge weight",v:72},{f:"Hop atten.",v:60},{f:"Community",v:49}] },
];

const ENSEMBLE = { accuracy:96.8, precision:94.9, recall:97.3, f1:96.1, fpr:2.4 };

// Graph topology
const GRAPH_NODES = [
  {id:1,x:420,y:230,risk:91,label:"Shell Co. A",  type:"entity"},
  {id:2,x:210,y:100,risk:78,label:"ACC-NGA01",    type:"account"},
  {id:3,x:630,y:100,risk:85,label:"ACC-KEN07",    type:"account"},
  {id:4,x:150,y:330,risk:62,label:"Hawala Node",  type:"broker"},
  {id:5,x:680,y:320,risk:93,label:"JNIM Cell",    type:"threat"},
  {id:6,x:420,y:400,risk:74,label:"ACC-MLI04",    type:"account"},
  {id:7,x:260,y:240,risk:55,label:"ACC-SEN02",    type:"account"},
  {id:8,x:570,y:240,risk:88,label:"ACC-ETH09",    type:"account"},
  {id:9,x:80, y:190,risk:44,label:"NGO-FRNT",     type:"ngo"},
  {id:10,x:340,y:130,risk:67,label:"ACC-GHA03",   type:"account"},
  {id:11,x:520,y:390,risk:79,label:"Crypto Wallet",type:"crypto"},
  {id:12,x:190,y:360,risk:71,label:"Broker-B",    type:"broker"},
  {id:13,x:730,y:200,risk:58,label:"ACC-TZA05",   type:"account"},
];
const GRAPH_EDGES = [
  [1,2,920000],[1,3,1450000],[2,4,380000],[3,5,2100000],[4,6,290000],
  [5,6,560000],[7,1,740000],[1,8,830000],[8,5,1200000],[9,4,180000],
  [7,4,420000],[3,8,670000],[10,1,510000],[11,5,890000],[6,11,340000],
  [2,10,260000],[12,4,610000],[12,6,290000],[13,5,480000],[8,13,220000],
];

// Training history
function makeCurve(n,s,e,noise=0.018){
  return Array.from({length:n},(_,i)=>{
    const t=i/(n-1);
    return +(s+(e-s)*(1-Math.exp(-4*t))+(Math.random()-.5)*noise*2).toFixed(4);
  });
}
const TRAIN_HIST = {
  gnn: {tr:makeCurve(40,1.42,0.18), vl:makeCurve(40,1.55,0.23)},
  xgb: {tr:makeCurve(30,1.31,0.24), vl:makeCurve(30,1.38,0.28)},
  lstm:{tr:makeCurve(50,1.60,0.29), vl:makeCurve(50,1.74,0.35)},
  iso: {tr:makeCurve(20,0.98,0.42), vl:makeCurve(20,1.05,0.48)},
  bert:{tr:makeCurve(35,1.85,0.31), vl:makeCurve(35,1.98,0.39)},
  gcn: {tr:makeCurve(45,1.51,0.21), vl:makeCurve(45,1.63,0.27)},
};

// ═══════════════════════════════════════════════════════════════════════════════
// UTILS
// ═══════════════════════════════════════════════════════════════════════════════
const rnd  = (a,b) => Math.floor(Math.random()*(b-a+1))+a;
const pick = arr   => arr[rnd(0,arr.length-1)];
const uid  = ()    => Math.random().toString(36).slice(2,8).toUpperCase();
const fmt  = n     => Number(n).toLocaleString(undefined,{maximumFractionDigits:0});

function mkAlert(){
  const sc=rnd(40,99), m=pick(ML_MODELS.filter(x=>x.status==="DEPLOYED"));
  return {
    id:`AQT-${uid()}`, ts:Date.now()-rnd(0,86400)*1000,
    origin:pick(COUNTRIES), dest:pick(COUNTRIES),
    amount:(Math.random()*980000+20000).toFixed(2),
    currency:pick(CURRENCIES), channel:pick(CHANNELS),
    typology:pick(TYPOLOGIES), network:pick(NETWORKS),
    score:sc, sev:sc>=85?"CRITICAL":sc>=70?"HIGH":sc>=55?"MEDIUM":"LOW",
    status:pick(["OPEN","UNDER REVIEW","ESCALATED","FROZEN"]),
    entities:rnd(2,9), accounts:rnd(3,18),
    model:m.short, modelColor:m.color, conf:rnd(70,99),
  };
}
const INIT_ALERTS = Array.from({length:50},mkAlert);

// Colour helpers
const sevC  = s => s==="CRITICAL"?"#ff2d55":s==="HIGH"?"#ff9f0a":s==="MEDIUM"?"#ffd60a":"#30d158";
const riskC = r => r>=85?"#ff2d55":r>=70?"#ff9f0a":r>=50?"#ffd60a":"#30d158";
const statC = s => ({FROZEN:"#5e5ce6",ESCALATED:"#ff2d55","UNDER REVIEW":"#ff9f0a",OPEN:"#64d2ff"})[s]||"#64d2ff";
const mstC  = s => s==="DEPLOYED"?"#30d158":s==="STAGING"?"#ff9f0a":"#5e5ce6";

// ═══════════════════════════════════════════════════════════════════════════════
// GLOBAL CSS
// ═══════════════════════════════════════════════════════════════════════════════
const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&family=DM+Sans:wght@300;400;500&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#050c12;}
  ::-webkit-scrollbar{width:3px;height:3px;}
  ::-webkit-scrollbar-track{background:#080f17;}
  ::-webkit-scrollbar-thumb{background:#1a3448;border-radius:2px;}
  @keyframes fadeUp{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
  @keyframes fadeIn{from{opacity:0;}to{opacity:1;}}
  @keyframes pulse{0%,100%{opacity:1;}50%{opacity:.25;}}
  @keyframes flash{0%{background:#ff2d5528;}100%{background:transparent;}}
  @keyframes scan{0%{left:-40%;}100%{left:110%;}}
  @keyframes glow{0%,100%{box-shadow:0 0 8px #64d2ff33;}50%{box-shadow:0 0 22px #64d2ff77;}}
  @keyframes spin{to{transform:rotate(360deg);}}
  @keyframes ripple{0%{r:14;opacity:.8;}100%{r:30;opacity:0;}}
`;

// ═══════════════════════════════════════════════════════════════════════════════
// SHARED MICRO-COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════════
function Tip({children,text}){
  const [show,setShow]=useState(false);
  return(
    <div style={{position:"relative",display:"inline-flex"}}
      onMouseEnter={()=>setShow(true)} onMouseLeave={()=>setShow(false)}>
      {children}
      {show&&text&&(
        <div style={{position:"absolute",bottom:"calc(100% + 6px)",left:"50%",transform:"translateX(-50%)",
          background:"#0a1a28",border:"1px solid #1a3448",borderRadius:6,padding:"5px 9px",
          fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:"#c8dae8",
          whiteSpace:"nowrap",zIndex:9999,pointerEvents:"none",
          boxShadow:"0 4px 16px #0008"}}>
          {text}
        </div>
      )}
    </div>
  );
}

function Pill({children,color,active,onClick}){
  return(
    <button onClick={onClick}
      style={{background:active?color+"22":"transparent",
        border:`1px solid ${active?color+"88":"#1a3448"}`,
        borderRadius:5,color:active?color:"#3a6070",
        fontSize:8,padding:"5px 10px",cursor:"pointer",
        fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,
        transition:"all .15s"}}>
      {children}
    </button>
  );
}

function MBar({label,val,max=100,color="#64d2ff",tip=""}){
  return(
    <Tip text={tip||undefined}>
      <div style={{marginBottom:8,width:"100%"}}>
        <div style={{display:"flex",justifyContent:"space-between",
          fontSize:8,fontFamily:"'Share Tech Mono',monospace",marginBottom:3}}>
          <span style={{color:"#3a6070",letterSpacing:.8}}>{label}</span>
          <span style={{color}}>{val}%</span>
        </div>
        <div style={{height:3,background:"#0d1e2e",borderRadius:2,overflow:"hidden"}}>
          <div style={{height:"100%",width:`${(val/max)*100}%`,background:color,
            borderRadius:2,transition:"width .8s cubic-bezier(.4,0,.2,1)"}}/>
        </div>
      </div>
    </Tip>
  );
}

function Spark({data,color="#64d2ff",w=72,h=24,filled=false}){
  if(!data||data.length<2) return null;
  const mx=Math.max(...data), mn=Math.min(...data), rng=mx-mn||1;
  const pts=data.map((v,i)=>[i/(data.length-1)*w, h-((v-mn)/rng)*h]);
  const poly=pts.map(p=>p.join(",")).join(" ");
  const area=`M0,${h} `+pts.map(p=>`L${p[0]},${p[1]}`).join(" ")+` L${w},${h} Z`;
  const last=pts[pts.length-1];
  return(
    <svg width={w} height={h} style={{display:"block"}}>
      {filled&&<path d={area} fill={color} opacity=".1"/>}
      <polyline points={poly} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round"/>
      <circle cx={last[0]} cy={last[1]} r="2.5" fill={color}/>
    </svg>
  );
}

function ScoreRing({score,size=56}){
  const c=riskC(score), r=size/2-4, circ=2*Math.PI*r, dash=circ*(score/100);
  return(
    <div style={{position:"relative",width:size,height:size,flexShrink:0}}>
      <svg width={size} height={size} style={{transform:"rotate(-90deg)"}}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#0d1e2e" strokeWidth="3.5"/>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={c} strokeWidth="3.5"
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
          style={{transition:"stroke-dasharray .6s ease"}}/>
      </svg>
      <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",
        justifyContent:"center",fontFamily:"'Rajdhani',sans-serif",
        fontSize:size*.28,fontWeight:700,color:c}}>{score}</div>
    </div>
  );
}

function RocCurve({model,w=170,h=130}){
  const pts=[[0,0]];
  for(let i=1;i<=30;i++){
    const fpr=i/30;
    const tpr=Math.min(1,Math.pow(fpr,.14-(model.accuracy-80)/360));
    pts.push([fpr*w, h-tpr*h]);
  }
  pts.push([w,h]);
  const poly=pts.map(p=>p.join(",")).join(" ");
  const area="M0,"+h+" "+pts.slice(0,-1).map(p=>`L${p[0]},${p[1]}`).join(" ")+" L"+w+","+h+" Z";
  const auc=(0.5+model.accuracy/200).toFixed(3);
  return(
    <svg width={w} height={h}>
      <line x1={0} y1={h} x2={w} y2={0} stroke="#1a3448" strokeWidth="1" strokeDasharray="3,3"/>
      <path d={area} fill={model.color} opacity=".07"/>
      <polyline points={poly} fill="none" stroke={model.color} strokeWidth="2" strokeLinejoin="round"/>
      <rect x={w-58} y={2} width={56} height={16} rx={3} fill="#080f17" opacity=".9"/>
      <text x={w-4} y={13} textAnchor="end" fill={model.color} fontSize="9" fontFamily="'Share Tech Mono',monospace">AUC {auc}</text>
    </svg>
  );
}

function LossCurve({id,w=300,h=90,live=null}){
  const hist=TRAIN_HIST[id]; if(!hist) return null;
  const tr=live||hist.tr, vl=hist.vl.slice(0,tr.length);
  const all=[...tr,...vl], mx=Math.max(...all), mn=Math.min(...all), rng=mx-mn||1;
  const sy=v=>h-((v-mn)/rng)*h;
  const mk=arr=>arr.map((v,i)=>`${(i/Math.max(arr.length-1,1))*w},${sy(v)}`).join(" ");
  const m=ML_MODELS.find(x=>x.id===id);
  return(
    <svg width={w} height={h}>
      <defs>
        <linearGradient id={`lg${id}`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor={m?.color||"#64d2ff"} stopOpacity=".5"/>
          <stop offset="100%" stopColor={m?.color||"#64d2ff"} stopOpacity="1"/>
        </linearGradient>
      </defs>
      {tr.length>1&&<polyline points={mk(tr)} fill="none" stroke={`url(#lg${id})`} strokeWidth="2" strokeLinejoin="round"/>}
      {vl.length>1&&<polyline points={mk(vl)} fill="none" stroke="#ff9f0a" strokeWidth="1.5" strokeLinejoin="round" strokeDasharray="4,3"/>}
      <text x={4} y={10} fill={m?.color||"#64d2ff"} fontSize="7.5" fontFamily="'Share Tech Mono',monospace">Train</text>
      <text x={38} y={10} fill="#ff9f0a" fontSize="7.5" fontFamily="'Share Tech Mono',monospace">Val</text>
      {tr.length>0&&<circle cx={(tr.length-1)/Math.max(tr.length-1,1)*w} cy={sy(tr[tr.length-1])} r="3" fill={m?.color||"#64d2ff"}/>}
    </svg>
  );
}

function ConfMatrix({model}){
  const tp=Math.round(model.recall*820/100), fn=820-tp;
  const fp=Math.round(model.fpr*180/10),     tn=180-fp;
  return(
    <div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:4}}>
        {[["TP",tp,"#30d158","True Positive"],["FN",fn,"#ff9f0a","False Negative"],
          ["FP",fp,"#ff2d55","False Positive"],["TN",tn,"#64d2ff","True Negative"]].map(([l,v,c,d])=>(
          <Tip key={l} text={d}>
            <div style={{background:"#060e14",border:`1px solid ${c}33`,borderRadius:6,
              padding:"8px",textAlign:"center",cursor:"default",width:"100%"}}>
              <div style={{fontSize:7.5,color:"#3a6070",fontFamily:"'Share Tech Mono',monospace",marginBottom:3}}>{l}</div>
              <div style={{fontSize:20,fontFamily:"'Rajdhani',sans-serif",fontWeight:700,color:c}}>{v}</div>
            </div>
          </Tip>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// NETWORK GRAPH
// ═══════════════════════════════════════════════════════════════════════════════
function NetworkGraph({onNode,compact=false}){
  const [hov,setHov]=useState(null);
  const [sel,setSel]=useState(null);
  const [pulses,setPulses]=useState([]);
  const [zoom,setZoom]=useState(1);
  const [dragging,setDragging]=useState(null);
  const [nodes,setNodes]=useState(GRAPH_NODES.map(n=>({...n})));
  const svgRef=useRef();

  useEffect(()=>{
    const t=setInterval(()=>{
      const e=GRAPH_EDGES[rnd(0,GRAPH_EDGES.length-1)];
      const suspicious=e[2]>800000;
      setPulses(p=>[...p.slice(-8),{id:Date.now(),a:e[0],b:e[1],color:suspicious?"#ff2d55":"#64d2ff",size:suspicious?5:3.5}]);
    },1100);
    return()=>clearInterval(t);
  },[]);

  const handleNode=n=>{
    setSel(s=>s===n.id?null:n.id);
    onNode&&onNode(nodes.find(x=>x.id===n.id));
  };

  const vb=compact?`${(1-zoom)*360} ${(1-zoom)*220} ${810*zoom} ${500*zoom}`
                  :`${(1-zoom)*360} ${(1-zoom)*220} ${810*zoom} ${500*zoom}`;

  const nodeTypeIcon=t=>({entity:"◈",account:"○",broker:"◆",threat:"⚠",ngo:"✦",crypto:"₿"})[t]||"○";

  return(
    <div style={{position:"relative",width:"100%",height:"100%"}}>
      {/* zoom controls */}
      <div style={{position:"absolute",top:8,right:8,zIndex:10,display:"flex",gap:5}}>
        {[["＋",.2],[" − ",-.2]].map(([l,d])=>(
          <button key={l} onClick={()=>setZoom(z=>Math.max(.4,Math.min(2.2,z+d)))}
            style={{width:26,height:26,background:"#0a1820",border:"1px solid #1a3448",
              borderRadius:4,color:"#64d2ff",cursor:"pointer",fontSize:13,
              display:"flex",alignItems:"center",justifyContent:"center",fontFamily:"monospace"}}>
            {l}
          </button>
        ))}
        <button onClick={()=>setZoom(1)}
          style={{background:"#0a1820",border:"1px solid #1a3448",borderRadius:4,
            color:"#3a6070",fontSize:7.5,padding:"0 6px",cursor:"pointer",
            fontFamily:"'Share Tech Mono',monospace",height:26}}>
          RST
        </button>
      </div>

      <svg ref={svgRef} width="100%" height="100%" viewBox={vb}>
        <defs>
          <filter id="gf1"><feGaussianBlur stdDeviation="3" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
          <filter id="gf2"><feGaussianBlur stdDeviation="7" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
          {GRAPH_EDGES.map(([a,b,w],i)=>{
            const na=nodes.find(n=>n.id===a), nb=nodes.find(n=>n.id===b);
            if(!na||!nb) return null;
            return(
              <marker key={i} id={`arr${i}`} markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                <path d="M0,0 L6,3 L0,6 Z" fill={w>800000?"#ff2d5566":"#1a3448"}/>
              </marker>
            );
          })}
        </defs>

        {/* Edges */}
        {GRAPH_EDGES.map(([a,b,w],i)=>{
          const na=nodes.find(n=>n.id===a), nb=nodes.find(n=>n.id===b);
          if(!na||!nb) return null;
          const hot=hov===a||hov===b||sel===a||sel===b;
          const thick=w>800000;
          return(
            <line key={i} x1={na.x} y1={na.y} x2={nb.x} y2={nb.y}
              stroke={hot?(thick?"#ff2d5566":"#2a5070"):(thick?"#2a1a1a":"#0f2030")}
              strokeWidth={hot?2.5:thick?1.8:1.2}
              opacity={hot?1:.7}
              markerEnd={`url(#arr${i})`}
              style={{transition:"all .2s"}}/>
          );
        })}

        {/* Pulses */}
        {pulses.map(p=>{
          const na=nodes.find(n=>n.id===p.a), nb=nodes.find(n=>n.id===p.b);
          if(!na||!nb) return null;
          return(
            <circle key={p.id} r={p.size} fill={p.color} filter="url(#gf1)">
              <animateMotion dur="1.05s" fill="freeze" path={`M${na.x},${na.y} L${nb.x},${nb.y}`}/>
              <animate attributeName="opacity" values="1;.7;0" dur="1.05s" fill="freeze"/>
              <animate attributeName="r" values={`${p.size};${p.size*.6};2`} dur="1.05s" fill="freeze"/>
            </circle>
          );
        })}

        {/* Nodes */}
        {nodes.map(n=>{
          const c=riskC(n.risk), isH=hov===n.id, isSel=sel===n.id;
          return(
            <g key={n.id} onClick={()=>handleNode(n)}
              onMouseEnter={()=>setHov(n.id)} onMouseLeave={()=>setHov(null)}
              style={{cursor:"pointer"}}>
              {/* Ripple for high risk */}
              {n.risk>=85&&(
                <circle cx={n.x} cy={n.y} r="14" fill="none" stroke={c} strokeWidth="1.5" opacity=".3">
                  <animate attributeName="r" values="14;34" dur="2s" repeatCount="indefinite"/>
                  <animate attributeName="opacity" values=".4;0" dur="2s" repeatCount="indefinite"/>
                </circle>
              )}
              {(isH||isSel)&&<circle cx={n.x} cy={n.y} r="28" fill={c} opacity=".08" filter="url(#gf2)"/>}
              {isSel&&<circle cx={n.x} cy={n.y} r="21" fill="none" stroke={c} strokeWidth="1.5" opacity=".5" strokeDasharray="4,3"/>}
              <circle cx={n.x} cy={n.y} r="15" fill="#0b1c2c" stroke={c}
                strokeWidth={isSel?2.8:isH?2.2:1.6}
                filter={(isH||isSel)?"url(#gf1)":"none"}
                style={{transition:"all .2s"}}/>
              {/* Type icon */}
              <text x={n.x} y={n.y+4} textAnchor="middle" dominantBaseline="middle"
                fill={c} fontSize="9" fontFamily="monospace" opacity={isH?1:.7}>
                {nodeTypeIcon(n.type)}
              </text>
              <text x={n.x} y={n.y+28} textAnchor="middle"
                fill={isH?c:"#4a6a80"} fontSize="8.5" fontFamily="'Share Tech Mono',monospace"
                style={{transition:"fill .2s"}}>
                {n.label}
              </text>
              {isH&&(
                <>
                  <rect x={n.x-28} y={n.y+37} width={56} height={14} rx={3} fill="#080f17" opacity=".95"/>
                  <text x={n.x} y={n.y+47} textAnchor="middle" fill={c} fontSize="8" fontFamily="'Share Tech Mono',monospace">
                    RISK {n.risk} · {n.type.toUpperCase()}
                  </text>
                </>
              )}
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div style={{position:"absolute",bottom:10,left:10,background:"#060e1499",
        border:"1px solid #0f2030",borderRadius:7,padding:"8px 12px",
        fontSize:8,color:"#3a6070",fontFamily:"'Share Tech Mono',monospace",backdropFilter:"blur(4px)"}}>
        {[["#ff2d55","HIGH RISK (85+)"],["#ff9f0a","ELEVATED (70+)"],["#ffd60a","MODERATE (50+)"],["#30d158","LOW (<50)"]].map(([c,l])=>(
          <div key={l} style={{display:"flex",alignItems:"center",gap:5,marginBottom:3}}>
            <div style={{width:6,height:6,borderRadius:"50%",background:c,flexShrink:0}}/>
            <span>{l}</span>
          </div>
        ))}
        <div style={{borderTop:"1px solid #0f2030",marginTop:5,paddingTop:5}}>
          <div>● Red pulse = high-value flow (&gt;800K)</div>
          <div>● Blue pulse = standard flow</div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// TRAINING MODAL
// ═══════════════════════════════════════════════════════════════════════════════
function TrainModal({model,onClose}){
  const [phase,setPhase]=useState("idle");
  const [epoch,setEpoch]=useState(0);
  const [live,setLive]=useState([]);
  const [log,setLog]=useState([]);
  const [cfg,setCfg]=useState({epochs:30,lr:"3e-4",batch:4096,dropout:"0.2"});
  const logRef=useRef(), ivRef=useRef();
  const hist=TRAIN_HIST[model.id], total=parseInt(cfg.epochs)||30;

  const start=()=>{
    setPhase("running");setEpoch(0);setLive([]);setLog([]);
    ivRef.current=setInterval(()=>{
      setEpoch(e=>{
        const ne=e+1, idx=Math.min(ne-1,hist.tr.length-1);
        const tl=+(hist.tr[idx]+(Math.random()-.5)*.01).toFixed(4);
        const vl=+(hist.vl[idx]+(Math.random()-.5)*.012).toFixed(4);
        const acc=+(model.accuracy-(total-ne)/total*12+Math.random()*.4).toFixed(2);
        setLive(d=>[...d,tl]);
        setLog(l=>[...l,{ep:ne,tl,vl,acc,lr:(parseFloat(cfg.lr)*Math.pow(.98,ne)).toExponential(2)}]);
        if(ne>=total){clearInterval(ivRef.current);setPhase("done");}
        return ne;
      });
    },90);
  };
  const abort=()=>{clearInterval(ivRef.current);setPhase("idle");};
  useEffect(()=>{return()=>clearInterval(ivRef.current);},[]);
  useEffect(()=>{if(logRef.current)logRef.current.scrollTop=logRef.current.scrollHeight;},[log]);

  const pct=Math.min(100,Math.round((epoch/total)*100));

  return(
    <div style={{position:"fixed",inset:0,background:"#000c",zIndex:300,
      display:"flex",alignItems:"center",justifyContent:"center",animation:"fadeIn .2s"}}
      onClick={e=>e.target===e.currentTarget&&onClose()}>
      <div style={{background:"#080f17",border:`1px solid ${model.color}55`,borderRadius:14,
        width:600,maxHeight:"90vh",overflow:"hidden",display:"flex",flexDirection:"column",
        boxShadow:`0 0 80px ${model.color}22, 0 0 40px #0008`}}>

        {/* Header */}
        <div style={{padding:"15px 20px",borderBottom:"1px solid #0f2030",
          background:"#060e14",display:"flex",alignItems:"center",gap:10}}>
          <div style={{width:9,height:9,borderRadius:"50%",background:model.color,
            animation:phase==="running"?"pulse .7s infinite":"none"}}/>
          <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:18,fontWeight:700,color:"#c8dae8"}}>{model.name}</div>
          <div style={{fontSize:8.5,fontFamily:"'Share Tech Mono',monospace",color:"#2d5068",letterSpacing:1}}>TRAINING CONSOLE</div>
          <div style={{flex:1}}/>
          <span style={{fontSize:8.5,color:model.color,fontFamily:"'Share Tech Mono',monospace",
            border:`1px solid ${model.color}44`,padding:"2px 8px",borderRadius:4}}>{model.framework}</span>
          <button onClick={onClose} style={{background:"transparent",border:"none",color:"#3a6070",
            fontSize:22,cursor:"pointer",lineHeight:1,marginLeft:6}}>×</button>
        </div>

        <div style={{padding:20,overflowY:"auto",flex:1}}>
          {/* Hyperparams */}
          <div style={{marginBottom:16}}>
            <div style={{fontSize:8,color:"#3a6070",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:10}}>HYPERPARAMETERS</div>
            <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:8}}>
              {[["Epochs",cfg.epochs,"epochs"],["Learning Rate",cfg.lr,"lr"],
                ["Batch Size",cfg.batch,"batch"],["Dropout",cfg.dropout,"dropout"],
                ["Params",model.params,""],["Samples",model.samples.toLocaleString(),""]].map(([lbl,val,key])=>(
                <div key={lbl} style={{background:"#0a1820",borderRadius:8,padding:"8px 12px",border:"1px solid #0f2030"}}>
                  <div style={{fontSize:7.5,color:"#3a6070",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:4}}>{lbl}</div>
                  {key&&phase==="idle"
                    ?<input value={val} onChange={e=>setCfg(c=>({...c,[key]:e.target.value}))}
                        style={{background:"transparent",border:"none",outline:"none",
                          color:"#c8dae8",fontFamily:"'Share Tech Mono',monospace",fontSize:11,width:"100%"}}/>
                    :<div style={{fontSize:11,color:"#c8dae8",fontFamily:"'Share Tech Mono',monospace"}}>{val}</div>}
                </div>
              ))}
            </div>
          </div>

          {/* Progress */}
          {phase!=="idle"&&(
            <div style={{marginBottom:16}}>
              <div style={{display:"flex",justifyContent:"space-between",marginBottom:5}}>
                <span style={{fontSize:8.5,fontFamily:"'Share Tech Mono',monospace",color:"#3a6070"}}>EPOCH {epoch}/{total}</span>
                <span style={{fontSize:12,fontFamily:"'Rajdhani',sans-serif",fontWeight:700,color:model.color}}>{pct}%</span>
              </div>
              <div style={{height:6,background:"#0d1e2e",borderRadius:3,overflow:"hidden",position:"relative"}}>
                <div style={{height:"100%",width:`${pct}%`,borderRadius:3,transition:"width .09s",
                  background:`linear-gradient(90deg,${model.color}77,${model.color})`,position:"relative"}}>
                  {phase==="running"&&<div style={{position:"absolute",right:0,top:0,bottom:0,width:30,
                    background:"linear-gradient(90deg,transparent,#fff4)",animation:"scan .9s linear infinite"}}/>}
                </div>
              </div>
              {log.length>0&&(
                <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:6,marginTop:10}}>
                  {[["Train Loss",log[log.length-1].tl,model.color],
                    ["Val Loss",log[log.length-1].vl,"#ff9f0a"],
                    ["Accuracy",log[log.length-1].acc+"%","#30d158"],
                    ["LR",log[log.length-1].lr,"#bf5af2"]].map(([k,v,c])=>(
                    <div key={k} style={{background:"#060e14",borderRadius:6,padding:"6px 8px",textAlign:"center",border:"1px solid #0f2030"}}>
                      <div style={{fontSize:7,color:"#3a6070",fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,marginBottom:2}}>{k}</div>
                      <div style={{fontSize:13,fontFamily:"'Rajdhani',sans-serif",fontWeight:700,color:c}}>{v}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Live loss chart */}
          {live.length>1&&(
            <div style={{background:"#060e14",borderRadius:8,padding:"10px 12px",marginBottom:16,border:"1px solid #0f2030"}}>
              <div style={{fontSize:7.5,color:"#3a6070",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:7}}>LIVE LOSS</div>
              <LossCurve id={model.id} w={520} h={80} live={live}/>
            </div>
          )}

          {/* Log */}
          <div ref={logRef} style={{background:"#060e14",borderRadius:8,padding:"10px 14px",
            fontFamily:"'Share Tech Mono',monospace",fontSize:9,maxHeight:130,overflowY:"auto",
            border:"1px solid #0f2030",lineHeight:1.8}}>
            {log.length===0&&<div style={{color:"#1e3a4a"}}>{'>'} Awaiting training run…</div>}
            {log.slice(-28).map((l,i,a)=>(
              <div key={l.ep} style={{color:i===a.length-1?model.color:"#1e4a5a"}}>
                {'>'} [{String(l.ep).padStart(3,"0")}/{total}] loss={l.tl} val={l.vl} acc={l.acc}% lr={l.lr}
              </div>
            ))}
            {phase==="done"&&<div style={{color:"#30d158",marginTop:3}}>{'>'} ✓ Training complete — ready for deployment.</div>}
          </div>
        </div>

        {/* Footer */}
        <div style={{padding:"12px 20px",borderTop:"1px solid #0f2030",background:"#060e14",display:"flex",gap:8,alignItems:"center"}}>
          {phase==="idle"&&
            <button onClick={start} style={{background:model.color+"22",border:`1px solid ${model.color}`,
              borderRadius:6,color:model.color,padding:"8px 20px",fontFamily:"'Share Tech Mono',monospace",
              fontSize:10,cursor:"pointer",letterSpacing:.8,transition:"all .15s"}}>▶ START TRAINING</button>}
          {phase==="running"&&
            <button onClick={abort} style={{background:"#ff2d5522",border:"1px solid #ff2d55",
              borderRadius:6,color:"#ff2d55",padding:"8px 20px",fontFamily:"'Share Tech Mono',monospace",
              fontSize:10,cursor:"pointer",letterSpacing:.8}}>■ ABORT</button>}
          {phase==="done"&&
            <button onClick={onClose} style={{background:"#30d15822",border:"1px solid #30d158",
              borderRadius:6,color:"#30d158",padding:"8px 24px",fontFamily:"'Share Tech Mono',monospace",
              fontSize:10,cursor:"pointer",letterSpacing:.8,animation:"glow 2s infinite"}}>✓ DEPLOY MODEL</button>}
          <button onClick={onClose} style={{background:"transparent",border:"1px solid #1a3448",
            borderRadius:6,color:"#3a6070",padding:"8px 14px",fontFamily:"'Share Tech Mono',monospace",
            fontSize:10,cursor:"pointer"}}>CLOSE</button>
          {phase==="done"&&
            <div style={{marginLeft:"auto",fontSize:8.5,color:"#30d158",fontFamily:"'Share Tech Mono',monospace"}}>
              ✓ F1={model.f1}% Acc={model.accuracy}%
            </div>}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// ALERT TABLE
// ═══════════════════════════════════════════════════════════════════════════════
function AlertTable({alerts,onSelect,selId,maxH="55vh"}){
  return(
    <div style={{background:"#080f17",border:"1px solid #0d1e2e",borderRadius:10,overflow:"hidden"}}>
      <div style={{display:"grid",gridTemplateColumns:"96px 72px 144px 116px 188px 76px 52px 96px",
        padding:"8px 14px",background:"#060e14",borderBottom:"1px solid #0d1e2e",
        fontSize:7.5,fontFamily:"'Share Tech Mono',monospace",color:"#2d5068",letterSpacing:.8}}>
        {["ID","SEV","ROUTE","AMOUNT","TYPOLOGY","MODEL","SCORE","STATUS"].map(h=><div key={h}>{h}</div>)}
      </div>
      <div style={{overflowY:"auto",maxHeight:maxH}}>
        {alerts.map((a,i)=>(
          <div key={a.id} onClick={()=>onSelect(a)}
            style={{display:"grid",gridTemplateColumns:"96px 72px 144px 116px 188px 76px 52px 96px",
              padding:"8px 14px",borderBottom:"1px solid #090d18",cursor:"pointer",
              background:a.id===selId?"#0a2030":a.sev==="CRITICAL"?"#150808":i%2===0?"#080f17":"#060e14",
              animation:i===0?"fadeUp .2s ease":"none",transition:"background .1s"}}
            onMouseEnter={e=>a.id!==selId&&(e.currentTarget.style.background="#0c1e2c")}
            onMouseLeave={e=>a.id!==selId&&(e.currentTarget.style.background=a.id===selId?"#0a2030":a.sev==="CRITICAL"?"#150808":i%2===0?"#080f17":"#060e14")}>
            <div style={{fontFamily:"'Share Tech Mono',monospace",fontSize:9,color:"#64d2ff"}}>{a.id}</div>
            <div style={{display:"flex",alignItems:"center",gap:3}}>
              <div style={{width:4,height:4,borderRadius:"50%",background:sevC(a.sev),flexShrink:0}}/>
              <span style={{color:sevC(a.sev),fontSize:7.5,fontFamily:"'Share Tech Mono',monospace",fontWeight:700}}>{a.sev}</span>
            </div>
            <div style={{fontSize:9,color:"#6a8aaa"}}>{a.origin.slice(0,7)}→{a.dest.slice(0,7)}</div>
            <div style={{fontSize:9}}>{fmt(a.amount)} <span style={{fontSize:7,color:"#2d5068"}}>{a.currency}</span></div>
            <div style={{fontSize:9,color:"#4a7090"}}>{a.typology.split(" ").slice(0,3).join(" ")}</div>
            <div style={{fontSize:8,fontFamily:"'Share Tech Mono',monospace",color:a.modelColor||"#9b9fff"}}>{a.model}</div>
            <div style={{fontSize:11,fontFamily:"'Rajdhani',sans-serif",fontWeight:700,color:riskC(a.score)}}>{a.score}</div>
            <div style={{fontSize:8,fontFamily:"'Share Tech Mono',monospace",color:statC(a.status)}}>● {a.status}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN APP
// ═══════════════════════════════════════════════════════════════════════════════
export default function AquilaTrace(){
  const [tab,setTab]         = useState("dashboard");
  const [alerts,setAlerts]   = useState(INIT_ALERTS);
  const [selAlert,setSelAlert]= useState(null);
  const [selModel,setSelModel]= useState(null);
  const [trainMdl,setTrainMdl]= useState(null);
  const [live,setLive]       = useState(true);
  const [flash,setFlash]     = useState(false);
  const [cmpIds,setCmpIds]   = useState(["gnn","xgb","lstm"]);
  const [search,setSearch]   = useState("");
  const [fSev,setFSev]       = useState("ALL");
  const [fMod,setFMod]       = useState("ALL");
  const [fStat,setFStat]     = useState("ALL");
  const [selNode,setSelNode]  = useState(null);
  const spark = useRef(Array.from({length:28},()=>rnd(4,44)));

  useEffect(()=>{
    if(!live) return;
    const t=setInterval(()=>{
      if(Math.random()>.42){
        const a=mkAlert();
        setAlerts(p=>[a,...p.slice(0,99)]);
        setFlash(true); setTimeout(()=>setFlash(false),500);
      }
      spark.current=[...spark.current.slice(1),rnd(4,44)];
    },2600);
    return()=>clearInterval(t);
  },[live]);

  const filtered=alerts.filter(a=>{
    if(fSev!=="ALL"&&a.sev!==fSev) return false;
    if(fMod!=="ALL"&&a.model!==fMod) return false;
    if(fStat!=="ALL"&&a.status!==fStat) return false;
    if(search){
      const q=search.toLowerCase();
      if(!a.id.toLowerCase().includes(q)&&
         !a.origin.toLowerCase().includes(q)&&
         !a.typology.toLowerCase().includes(q)&&
         !a.network.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  const critical=alerts.filter(a=>a.sev==="CRITICAL").length;
  const high=alerts.filter(a=>a.sev==="HIGH").length;
  const frozen=alerts.filter(a=>a.status==="FROZEN").length;

  const NAV=[
    {id:"dashboard",icon:"⬡",lbl:"Dashboard"},
    {id:"models",   icon:"◈",lbl:"ML Models"},
    {id:"training", icon:"▲",lbl:"Training"},
    {id:"compare",  icon:"⇄",lbl:"Compare"},
    {id:"alerts",   icon:"◉",lbl:"Alerts"},
    {id:"network",  icon:"⬛",lbl:"Network"},
  ];

  return(
    <>
      <style>{CSS}</style>
      {trainMdl&&<TrainModal model={trainMdl} onClose={()=>setTrainMdl(null)}/>}

      <div style={{display:"flex",height:"100vh",background:"#050c12",
        overflow:"hidden",fontFamily:"'DM Sans',sans-serif",color:"#c8dae8"}}>

        {/* ── SIDEBAR ── */}
        <div style={{width:58,background:"#060e14",borderRight:"1px solid #0c1c28",
          display:"flex",flexDirection:"column",alignItems:"center",
          paddingTop:14,gap:3,flexShrink:0}}>
          <div style={{width:36,height:36,background:"linear-gradient(135deg,#0a3d5c,#0d6699)",
            borderRadius:9,display:"flex",alignItems:"center",justifyContent:"center",
            marginBottom:16,fontSize:17,boxShadow:"0 0 24px #0a3d5c99"}}>🦅</div>
          {NAV.map(n=>(
            <Tip key={n.id} text={n.lbl}>
              <button onClick={()=>setTab(n.id)}
                style={{width:40,height:40,background:tab===n.id?"#0d2535":"transparent",
                  border:"none",borderRadius:8,color:tab===n.id?"#64d2ff":"#2a4a60",
                  fontSize:14,cursor:"pointer",transition:"all .15s",
                  borderLeft:tab===n.id?"2px solid #64d2ff":"2px solid transparent"}}>
                {n.icon}
              </button>
            </Tip>
          ))}
          <div style={{flex:1}}/>
          <Tip text={live?"Live feed":"Paused"}>
            <div onClick={()=>setLive(l=>!l)}
              style={{width:7,height:7,borderRadius:"50%",
                background:live?"#30d158":"#2a4a60",marginBottom:14,
                animation:live?"pulse 2s infinite":"none",cursor:"pointer"}}/>
          </Tip>
        </div>

        {/* ── MAIN ── */}
        <div style={{flex:1,display:"flex",flexDirection:"column",overflow:"hidden"}}>

          {/* TOPBAR */}
          <div style={{height:50,background:"#060e14",borderBottom:"1px solid #0c1c28",
            display:"flex",alignItems:"center",padding:"0 18px",gap:14,flexShrink:0}}>
            <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:20,fontWeight:700,
              color:"#64d2ff",letterSpacing:3}}>AQUILA TRACE</div>
            <div style={{fontSize:8,fontFamily:"'Share Tech Mono',monospace",
              color:"#1a3a50",letterSpacing:2}}>ML INTELLIGENCE PLATFORM · v3.0</div>
            <div style={{flex:1}}/>
            {/* Model status pills */}
            <div style={{display:"flex",gap:4}}>
              {ML_MODELS.map(m=>(
                <Tip key={m.id} text={`${m.name} · ${m.status} · ${m.accuracy}% acc`}>
                  <div onClick={()=>{setSelModel(m);setTab("models");}}
                    style={{display:"flex",alignItems:"center",gap:4,
                      background:"#0a1820",border:`1px solid ${mstC(m.status)}33`,
                      borderRadius:5,padding:"3px 8px",cursor:"pointer",transition:"all .15s"}}
                    onMouseEnter={e=>e.currentTarget.style.borderColor=mstC(m.status)+"88"}
                    onMouseLeave={e=>e.currentTarget.style.borderColor=mstC(m.status)+"33"}>
                    <div style={{width:5,height:5,borderRadius:"50%",
                      background:mstC(m.status),
                      animation:m.status==="TRAINING"?"pulse .9s infinite":"none"}}/>
                    <span style={{fontSize:7.5,fontFamily:"'Share Tech Mono',monospace",color:"#3a6070"}}>{m.short}</span>
                  </div>
                </Tip>
              ))}
            </div>
            <div style={{width:1,height:22,background:"#0c1c28"}}/>
            <button onClick={()=>setLive(l=>!l)}
              style={{background:"transparent",border:`1px solid ${live?"#30d15866":"#1a3448"}`,
                borderRadius:6,color:live?"#30d158":"#3a6070",fontSize:8.5,
                fontFamily:"'Share Tech Mono',monospace",padding:"4px 12px",cursor:"pointer",
                letterSpacing:.8,transition:"all .2s"}}>
              {live?"● LIVE":"○ PAUSED"}
            </button>
            <div style={{fontSize:8.5,fontFamily:"'Share Tech Mono',monospace",color:"#1a3a50"}}>
              {new Date().toUTCString().slice(5,22)} UTC
            </div>
          </div>

          {/* CONTENT */}
          <div style={{flex:1,overflow:"auto",padding:18}}>

            {/* ══════════════ DASHBOARD ══════════════ */}
            {tab==="dashboard"&&(
              <div style={{display:"grid",gap:14}}>

                {/* KPIs */}
                <div style={{display:"grid",gridTemplateColumns:"repeat(5,1fr)",gap:10}}>
                  {[
                    {lbl:"ENSEMBLE ACC", val:`${ENSEMBLE.accuracy}%`,  color:"#64d2ff", sub:"6-model stack",    icon:"◈"},
                    {lbl:"CRITICAL",     val:critical,                  color:"#ff2d55", sub:"Active detections",icon:"◉", fl:flash},
                    {lbl:"HIGH RISK",    val:high,                      color:"#ff9f0a", sub:`${alerts.length} total`,icon:"◉"},
                    {lbl:"FROZEN",       val:frozen,                    color:"#5e5ce6", sub:"Accounts seized",  icon:"▣"},
                    {lbl:"FALSE POS",    val:`${ENSEMBLE.fpr}%`,        color:"#30d158", sub:"Ensemble avg",     icon:"▲"},
                  ].map((k,i)=>(
                    <div key={i} style={{background:"#080f17",border:"1px solid #0c1c28",
                      borderRadius:10,padding:"13px 16px",position:"relative",overflow:"hidden",
                      animation:k.fl?"flash .4s ease":"none",transition:"border-color .2s",cursor:"default"}}
                      onMouseEnter={e=>e.currentTarget.style.borderColor="#1a3448"}
                      onMouseLeave={e=>e.currentTarget.style.borderColor="#0c1c28"}>
                      <div style={{position:"absolute",top:0,left:0,right:0,height:2,
                        background:`linear-gradient(90deg,transparent,${k.color},transparent)`,opacity:.6}}/>
                      <div style={{fontSize:7.5,fontFamily:"'Share Tech Mono',monospace",
                        color:"#2a4860",letterSpacing:1.2,marginBottom:7}}>{k.icon} {k.lbl}</div>
                      <div style={{fontSize:32,fontWeight:700,fontFamily:"'Rajdhani',sans-serif",
                        color:k.color,lineHeight:1}}>{k.val}</div>
                      <div style={{fontSize:8.5,color:"#2a4860",marginTop:5}}>{k.sub}</div>
                    </div>
                  ))}
                </div>

                {/* Middle row */}
                <div style={{display:"grid",gridTemplateColumns:"2fr 1fr",gap:12}}>
                  {/* Graph preview */}
                  <div style={{background:"#080f17",border:"1px solid #0c1c28",borderRadius:10,padding:16,height:310}}>
                    <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:10}}>
                      <div style={{fontSize:8.5,fontFamily:"'Share Tech Mono',monospace",color:"#64d2ff",letterSpacing:1}}>GNN ENTITY CLUSTER</div>
                      <div style={{flex:1}}/>
                      <Spark data={spark.current} color="#64d2ff" h={18} w={56} filled/>
                      <button onClick={()=>setTab("network")}
                        style={{background:"transparent",border:"1px solid #1a3448",borderRadius:4,
                          color:"#3a6070",fontSize:8,padding:"2px 8px",cursor:"pointer",
                          fontFamily:"'Share Tech Mono',monospace"}}>EXPAND ↗</button>
                    </div>
                    <div style={{height:"calc(100% - 34px)"}}><NetworkGraph onNode={n=>{setSelNode(n);}} compact/></div>
                  </div>

                  {/* Right col */}
                  <div style={{display:"flex",flexDirection:"column",gap:10}}>
                    <div style={{background:"#080f17",border:"1px solid #64d2ff22",borderRadius:10,padding:16,flex:1}}>
                      <div style={{fontSize:8.5,fontFamily:"'Share Tech Mono',monospace",color:"#64d2ff",letterSpacing:1,marginBottom:12}}>ENSEMBLE PERFORMANCE</div>
                      <MBar label="ACCURACY"   val={ENSEMBLE.accuracy}  color="#64d2ff" tip="Correct classifications / total"/>
                      <MBar label="PRECISION"  val={ENSEMBLE.precision} color="#30d158" tip="TP / (TP+FP)"/>
                      <MBar label="RECALL"     val={ENSEMBLE.recall}    color="#5e5ce6" tip="TP / (TP+FN)"/>
                      <MBar label="F1 SCORE"   val={ENSEMBLE.f1}        color="#ff9f0a" tip="Harmonic mean precision & recall"/>
                      <MBar label="FALSE POS"  val={ENSEMBLE.fpr}       max={30} color="#ff2d55" tip="FP / (FP+TN)"/>
                    </div>
                    <div style={{background:"#080f17",border:"1px solid #0c1c28",borderRadius:10,padding:16,flex:1}}>
                      <div style={{fontSize:8.5,fontFamily:"'Share Tech Mono',monospace",color:"#64d2ff",letterSpacing:1,marginBottom:10}}>DETECTIONS / MODEL</div>
                      {ML_MODELS.map(m=>{
                        const cnt=alerts.filter(a=>a.model===m.short).length;
                        const pct=Math.round(cnt/Math.max(alerts.length,1)*100);
                        return(
                          <div key={m.id} style={{marginBottom:7}}>
                            <div style={{display:"flex",justifyContent:"space-between",
                              fontSize:7.5,fontFamily:"'Share Tech Mono',monospace",marginBottom:2}}>
                              <span style={{color:m.color}}>{m.short}</span>
                              <span style={{color:"#2a4860"}}>{cnt}</span>
                            </div>
                            <div style={{height:3,background:"#0d1e2e",borderRadius:2,overflow:"hidden"}}>
                              <div style={{height:"100%",width:`${pct}%`,background:m.color,
                                borderRadius:2,opacity:.8,transition:"width .6s"}}/>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* Recent alerts */}
                <div style={{background:"#080f17",border:"1px solid #0c1c28",borderRadius:10,padding:16}}>
                  <div style={{display:"flex",alignItems:"center",marginBottom:12}}>
                    <div style={{fontSize:8.5,fontFamily:"'Share Tech Mono',monospace",color:"#64d2ff",letterSpacing:1}}>RECENT DETECTIONS</div>
                    <div style={{marginLeft:8,width:6,height:6,borderRadius:"50%",background:"#ff2d55",
                      animation:flash?"pulse .4s":"none"}}/>
                    <div style={{flex:1}}/>
                    <button onClick={()=>setTab("alerts")}
                      style={{background:"transparent",border:"1px solid #1a3448",borderRadius:4,
                        color:"#3a6070",fontSize:8,padding:"3px 8px",cursor:"pointer",
                        fontFamily:"'Share Tech Mono',monospace"}}>VIEW ALL ↗</button>
                  </div>
                  <AlertTable alerts={alerts.slice(0,8)} onSelect={a=>{setSelAlert(a);setTab("alerts");}} selId={selAlert?.id} maxH="320px"/>
                </div>
              </div>
            )}

            {/* ══════════════ MODELS ══════════════ */}
            {tab==="models"&&(
              <div style={{display:"grid",gridTemplateColumns:selModel?"1fr 380px":"1fr",gap:14,alignItems:"start"}}>
                <div style={{display:"grid",gap:10}}>
                  {ML_MODELS.map(m=>(
                    <div key={m.id} onClick={()=>setSelModel(s=>s?.id===m.id?null:m)}
                      style={{background:"#080f17",border:`1px solid ${selModel?.id===m.id?m.color+"66":"#0c1c28"}`,
                        borderRadius:10,padding:18,cursor:"pointer",transition:"all .2s",
                        boxShadow:selModel?.id===m.id?`0 0 24px ${m.color}11`:"none"}}>
                      <div style={{display:"grid",gridTemplateColumns:"1fr auto",gap:12,alignItems:"start"}}>
                        <div>
                          <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:6,flexWrap:"wrap"}}>
                            <div style={{width:9,height:9,borderRadius:"50%",background:m.color,flexShrink:0}}/>
                            <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:17,fontWeight:700,color:"#c8dae8"}}>{m.name}</div>
                            <span style={{fontSize:7.5,fontFamily:"'Share Tech Mono',monospace",
                              color:mstC(m.status),border:`1px solid ${mstC(m.status)}44`,
                              padding:"1px 6px",borderRadius:3,letterSpacing:.8}}>{m.status}</span>
                            <span style={{fontSize:7.5,fontFamily:"'Share Tech Mono',monospace",color:"#2a4860"}}>{m.version}</span>
                            <div style={{flex:1}}/>
                            <span style={{fontSize:8,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace"}}>{m.latency}ms · {m.params}</span>
                          </div>
                          <div style={{fontSize:10.5,color:"#4a6a80",marginBottom:12,lineHeight:1.65}}>{m.desc}</div>
                          <div style={{display:"flex",gap:16,flexWrap:"wrap"}}>
                            {[["ACC",m.accuracy,"#64d2ff"],["PREC",m.precision,"#30d158"],
                              ["REC",m.recall,"#5e5ce6"],["F1",m.f1,"#ff9f0a"],["FPR",m.fpr,"#ff2d55"]].map(([k,v,c])=>(
                              <Tip key={k} text={k==="ACC"?"Accuracy":k==="PREC"?"Precision":k==="REC"?"Recall":k==="F1"?"F1 Score":"False Positive Rate"}>
                                <div style={{textAlign:"center",cursor:"default"}}>
                                  <div style={{fontSize:7,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8}}>{k}</div>
                                  <div style={{fontSize:16,fontFamily:"'Rajdhani',sans-serif",fontWeight:700,color:c}}>{v}%</div>
                                </div>
                              </Tip>
                            ))}
                          </div>
                        </div>
                        <div style={{display:"flex",flexDirection:"column",alignItems:"flex-end",gap:8}}>
                          <RocCurve model={m} w={158} h={118}/>
                          <button onClick={e=>{e.stopPropagation();setTrainMdl(m);}}
                            style={{background:m.color+"22",border:`1px solid ${m.color}88`,
                              borderRadius:6,color:m.color,fontSize:8.5,
                              fontFamily:"'Share Tech Mono',monospace",padding:"6px 14px",
                              cursor:"pointer",letterSpacing:.8,transition:"all .15s",width:"100%",textAlign:"center"}}
                            onMouseEnter={e=>e.currentTarget.style.background=m.color+"40"}
                            onMouseLeave={e=>e.currentTarget.style.background=m.color+"22"}>
                            ▶ RETRAIN
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Detail panel */}
                {selModel&&(
                  <div style={{background:"#080f17",border:`1px solid ${selModel.color}44`,
                    borderRadius:10,padding:20,position:"sticky",top:0,animation:"fadeUp .2s ease",
                    boxShadow:`0 0 32px ${selModel.color}11`}}>
                    <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:16}}>
                      <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:20,fontWeight:700,color:selModel.color}}>{selModel.short}</div>
                      <button onClick={()=>setSelModel(null)}
                        style={{background:"transparent",border:"none",color:"#3a6070",fontSize:22,cursor:"pointer",lineHeight:1}}>×</button>
                    </div>

                    <div style={{marginBottom:14}}>
                      <div style={{fontSize:7.5,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:8}}>LOSS CURVES</div>
                      <div style={{background:"#060e14",borderRadius:8,padding:10,border:"1px solid #0c1c28"}}>
                        <LossCurve id={selModel.id} w={308} h={80}/>
                      </div>
                    </div>

                    <div style={{marginBottom:14}}>
                      <div style={{fontSize:7.5,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:8}}>CONFUSION MATRIX</div>
                      <ConfMatrix model={selModel}/>
                    </div>

                    <div style={{marginBottom:14}}>
                      <div style={{fontSize:7.5,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:8}}>SHAP FEATURE IMPORTANCE</div>
                      {selModel.features.map(f=>(
                        <div key={f.f} style={{marginBottom:7}}>
                          <div style={{display:"flex",justifyContent:"space-between",fontSize:8.5,
                            fontFamily:"'Share Tech Mono',monospace",marginBottom:2}}>
                            <span style={{color:"#5a8aaa"}}>{f.f}</span>
                            <span style={{color:selModel.color}}>{f.v}</span>
                          </div>
                          <div style={{height:3,background:"#0d1e2e",borderRadius:2,overflow:"hidden"}}>
                            <div style={{height:"100%",width:`${f.v}%`,
                              background:`linear-gradient(90deg,${selModel.color}44,${selModel.color})`,borderRadius:2}}/>
                          </div>
                        </div>
                      ))}
                    </div>

                    {[["Framework",selModel.framework],["Parameters",selModel.params],
                      ["Training Samples",selModel.samples.toLocaleString()],
                      ["Last Trained",selModel.lastTrained],["Inference",selModel.latency+"ms"]].map(([k,v])=>(
                      <div key={k} style={{display:"flex",justifyContent:"space-between",
                        padding:"6px 0",borderBottom:"1px solid #0c1c28",fontSize:10}}>
                        <span style={{color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",fontSize:7.5,letterSpacing:.8}}>{k}</span>
                        <span style={{color:"#c8dae8"}}>{v}</span>
                      </div>
                    ))}

                    <button onClick={()=>setTrainMdl(selModel)}
                      style={{width:"100%",marginTop:14,background:selModel.color+"22",
                        border:`1px solid ${selModel.color}`,borderRadius:8,
                        color:selModel.color,padding:"10px",fontFamily:"'Share Tech Mono',monospace",
                        fontSize:9.5,cursor:"pointer",letterSpacing:.8,transition:"all .15s"}}
                      onMouseEnter={e=>e.currentTarget.style.background=selModel.color+"40"}
                      onMouseLeave={e=>e.currentTarget.style.background=selModel.color+"22"}>
                      ▶ LAUNCH TRAINING RUN
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* ══════════════ TRAINING ══════════════ */}
            {tab==="training"&&(
              <div style={{display:"grid",gap:14}}>
                <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12}}>
                  {ML_MODELS.map(m=>(
                    <div key={m.id} style={{background:"#080f17",border:"1px solid #0c1c28",borderRadius:10,padding:18}}>
                      <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:14}}>
                        <div style={{width:8,height:8,borderRadius:"50%",background:m.color,
                          animation:m.status==="TRAINING"?"pulse .8s infinite":"none"}}/>
                        <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:14,fontWeight:700,color:"#c8dae8"}}>{m.name}</div>
                        <div style={{flex:1}}/>
                        <span style={{fontSize:7,color:mstC(m.status),fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8}}>{m.status}</span>
                      </div>
                      <div style={{background:"#060e14",borderRadius:8,padding:"8px 10px",marginBottom:12,border:"1px solid #0c1c28"}}>
                        <div style={{fontSize:7.5,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,marginBottom:6}}>LOSS HISTORY</div>
                        <LossCurve id={m.id} w={238} h={62}/>
                      </div>
                      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:6,marginBottom:12}}>
                        {[["Samples",m.samples.toLocaleString()],["Last run",m.lastTrained],
                          ["Version",m.version],["Framework",m.framework.split(" ")[0]]].map(([k,v])=>(
                          <div key={k} style={{background:"#060e14",borderRadius:6,padding:"6px 8px",border:"1px solid #0c1c28"}}>
                            <div style={{fontSize:7,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,marginBottom:2}}>{k}</div>
                            <div style={{fontSize:9.5,color:"#6a8aaa",fontFamily:"'Share Tech Mono',monospace"}}>{v}</div>
                          </div>
                        ))}
                      </div>
                      <MBar label="F1" val={m.f1} color={m.color}/>
                      <button onClick={()=>setTrainMdl(m)}
                        style={{width:"100%",marginTop:8,background:m.color+"18",
                          border:`1px solid ${m.color}66`,borderRadius:6,color:m.color,
                          padding:"8px",fontFamily:"'Share Tech Mono',monospace",fontSize:8.5,
                          cursor:"pointer",letterSpacing:.8,transition:"all .15s"}}
                        onMouseEnter={e=>e.currentTarget.style.background=m.color+"33"}
                        onMouseLeave={e=>e.currentTarget.style.background=m.color+"18"}>
                        ▶ LAUNCH TRAINING
                      </button>
                    </div>
                  ))}
                </div>
                {/* Pipeline */}
                <div style={{background:"#080f17",border:"1px solid #0c1c28",borderRadius:10,padding:18}}>
                  <div style={{fontSize:8.5,fontFamily:"'Share Tech Mono',monospace",color:"#64d2ff",letterSpacing:1,marginBottom:14}}>ML PIPELINE</div>
                  <div style={{display:"flex",alignItems:"center",overflowX:"auto",gap:0}}>
                    {["Raw TXNs","Feature Eng.","Train/Val Split","Model Training","Evaluation","Ensemble Stack","Deployment","Live Inference"].map((s,i,arr)=>(
                      <div key={s} style={{display:"flex",alignItems:"center",flexShrink:0}}>
                        <div style={{background:"#0a1820",border:"1px solid #1a3448",borderRadius:7,
                          padding:"9px 13px",textAlign:"center",minWidth:96}}>
                          <div style={{fontSize:8,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",marginBottom:3,letterSpacing:.8}}>0{i+1}</div>
                          <div style={{fontSize:9.5,color:"#c8dae8"}}>{s}</div>
                        </div>
                        {i<arr.length-1&&(
                          <svg width="22" height="10" style={{flexShrink:0}}>
                            <line x1="0" y1="5" x2="16" y2="5" stroke="#1a3448" strokeWidth="1.5"/>
                            <polygon points="13,2 20,5 13,8" fill="#1a3448"/>
                          </svg>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ══════════════ COMPARE ══════════════ */}
            {tab==="compare"&&(
              <div style={{display:"grid",gap:14}}>
                <div style={{display:"flex",gap:8,alignItems:"center",flexWrap:"wrap"}}>
                  <div style={{fontSize:8.5,fontFamily:"'Share Tech Mono',monospace",color:"#64d2ff",letterSpacing:1}}>SELECT MODELS (max 3)</div>
                  {ML_MODELS.map(m=>(
                    <Pill key={m.id} color={m.color} active={cmpIds.includes(m.id)}
                      onClick={()=>setCmpIds(p=>p.includes(m.id)?p.filter(x=>x!==m.id):[...p,m.id].slice(-3))}>
                      {m.short}
                    </Pill>
                  ))}
                </div>
                {cmpIds.length>0&&(
                  <div style={{display:"grid",gridTemplateColumns:`repeat(${cmpIds.length},1fr)`,gap:12}}>
                    {cmpIds.map(id=>{
                      const m=ML_MODELS.find(x=>x.id===id);
                      const colW=cmpIds.length===1?460:cmpIds.length===2?240:160;
                      return(
                        <div key={id} style={{background:"#080f17",border:`1px solid ${m.color}44`,borderRadius:10,padding:20}}>
                          <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:14}}>
                            <div style={{width:8,height:8,borderRadius:"50%",background:m.color}}/>
                            <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:15,fontWeight:700,color:"#c8dae8"}}>{m.name}</div>
                          </div>
                          <MBar label="ACCURACY"  val={m.accuracy}  color={m.color}/>
                          <MBar label="PRECISION" val={m.precision} color={m.color} tip="TP/(TP+FP)"/>
                          <MBar label="RECALL"    val={m.recall}    color={m.color} tip="TP/(TP+FN)"/>
                          <MBar label="F1 SCORE"  val={m.f1}        color={m.color}/>
                          <MBar label="FPR"       val={m.fpr}       max={30} color="#ff2d55"/>
                          <div style={{marginTop:14}}>
                            <div style={{fontSize:7.5,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,marginBottom:7}}>ROC CURVE</div>
                            <div style={{background:"#060e14",borderRadius:7,padding:8,border:"1px solid #0c1c28",display:"inline-block"}}>
                              <RocCurve model={m} w={colW} h={110}/>
                            </div>
                          </div>
                          <div style={{marginTop:12}}>
                            <div style={{fontSize:7.5,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,marginBottom:7}}>CONFUSION MATRIX</div>
                            <ConfMatrix model={m}/>
                          </div>
                          <div style={{marginTop:12}}>
                            <div style={{fontSize:7.5,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,marginBottom:7}}>SHAP IMPORTANCE</div>
                            {m.features.map(f=>(
                              <div key={f.f} style={{marginBottom:5}}>
                                <div style={{display:"flex",justifyContent:"space-between",fontSize:8,fontFamily:"'Share Tech Mono',monospace",marginBottom:2}}>
                                  <span style={{color:"#4a6a80"}}>{f.f}</span><span style={{color:m.color}}>{f.v}</span>
                                </div>
                                <div style={{height:2.5,background:"#0d1e2e",borderRadius:2}}>
                                  <div style={{height:"100%",width:`${f.v}%`,background:m.color,opacity:.75,borderRadius:2}}/>
                                </div>
                              </div>
                            ))}
                          </div>
                          <div style={{marginTop:12,display:"grid",gridTemplateColumns:"1fr 1fr",gap:6}}>
                            {[["Latency",m.latency+"ms"],["Params",m.params],
                              ["Samples",m.samples.toLocaleString()],["Framework",m.framework.split(" ")[0]]].map(([k,v])=>(
                              <div key={k} style={{background:"#060e14",borderRadius:6,padding:"6px 8px",border:"1px solid #0c1c28"}}>
                                <div style={{fontSize:7,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,marginBottom:2}}>{k}</div>
                                <div style={{fontSize:10,fontFamily:"'Rajdhani',sans-serif",fontWeight:600,color:"#6a8aaa"}}>{v}</div>
                              </div>
                            ))}
                          </div>
                          <button onClick={()=>setTrainMdl(m)}
                            style={{width:"100%",marginTop:12,background:m.color+"18",border:`1px solid ${m.color}66`,
                              borderRadius:6,color:m.color,padding:"7px",fontFamily:"'Share Tech Mono',monospace",
                              fontSize:8,cursor:"pointer",letterSpacing:.8}}>▶ RETRAIN</button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* ══════════════ ALERTS ══════════════ */}
            {tab==="alerts"&&(
              <div style={{display:"grid",gridTemplateColumns:selAlert?"1fr 360px":"1fr",gap:14}}>
                <div>
                  {/* Filters */}
                  <div style={{display:"flex",gap:7,marginBottom:12,flexWrap:"wrap",alignItems:"center"}}>
                    <div style={{position:"relative",flex:1,minWidth:180}}>
                      <input value={search} onChange={e=>setSearch(e.target.value)}
                        placeholder="Search ID, country, typology, network…"
                        style={{width:"100%",background:"#0a1820",border:"1px solid #1a3448",
                          borderRadius:6,color:"#c8dae8",padding:"7px 12px 7px 28px",
                          fontSize:9.5,fontFamily:"'Share Tech Mono',monospace",outline:"none"}}/>
                      <div style={{position:"absolute",left:10,top:"50%",transform:"translateY(-50%)",color:"#3a6070",fontSize:11}}>⌕</div>
                    </div>
                    <div style={{display:"flex",gap:4}}>
                      {["ALL","CRITICAL","HIGH","MEDIUM","LOW"].map(s=>(
                        <Pill key={s} color={s==="ALL"?"#64d2ff":sevC(s)} active={fSev===s} onClick={()=>setFSev(s)}>{s}</Pill>
                      ))}
                    </div>
                    <div style={{display:"flex",gap:4}}>
                      {["ALL","OPEN","FROZEN","ESCALATED"].map(s=>(
                        <Pill key={s} color={statC(s)} active={fStat===s} onClick={()=>setFStat(s)}>{s}</Pill>
                      ))}
                    </div>
                    <div style={{display:"flex",gap:4}}>
                      {["ALL",...ML_MODELS.map(m=>m.short)].map(m=>{
                        const mdl=ML_MODELS.find(x=>x.short===m);
                        return <Pill key={m} color={mdl?.color||"#64d2ff"} active={fMod===m} onClick={()=>setFMod(m)}>{m}</Pill>;
                      })}
                    </div>
                    <div style={{fontSize:8.5,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",flexShrink:0}}>{filtered.length} results</div>
                  </div>
                  <AlertTable alerts={filtered} onSelect={setSelAlert} selId={selAlert?.id}/>
                </div>

                {/* Alert detail */}
                {selAlert&&(
                  <div style={{background:"#080f17",border:"1px solid #1a3448",borderRadius:10,
                    padding:20,alignSelf:"start",position:"sticky",top:0,animation:"fadeUp .2s ease"}}>
                    <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:14}}>
                      <div>
                        <div style={{fontFamily:"'Share Tech Mono',monospace",fontSize:13,color:"#64d2ff"}}>{selAlert.id}</div>
                        <div style={{fontSize:8.5,color:"#2a4860",marginTop:2}}>{new Date(selAlert.ts).toLocaleString()}</div>
                      </div>
                      <button onClick={()=>setSelAlert(null)}
                        style={{background:"transparent",border:"none",color:"#3a6070",fontSize:22,cursor:"pointer",lineHeight:1}}>×</button>
                    </div>

                    {/* Score + model */}
                    <div style={{display:"flex",gap:14,marginBottom:16,padding:13,
                      background:"#060e14",borderRadius:8,border:"1px solid #0c1c28"}}>
                      <ScoreRing score={selAlert.score} size={58}/>
                      <div>
                        <div style={{fontSize:7.5,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,marginBottom:3}}>RISK · {selAlert.sev}</div>
                        <div style={{fontSize:12,color:selAlert.modelColor||"#9b9fff",fontFamily:"'Share Tech Mono',monospace",marginBottom:2}}>◈ {selAlert.model}</div>
                        <div style={{fontSize:8.5,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace"}}>CONF {selAlert.conf}%</div>
                        <div style={{fontSize:8.5,color:statC(selAlert.status),fontFamily:"'Share Tech Mono',monospace",marginTop:3}}>● {selAlert.status}</div>
                      </div>
                    </div>

                    {[["TYPOLOGY",selAlert.typology],["NETWORK",selAlert.network],
                      ["ORIGIN",selAlert.origin],["DESTINATION",selAlert.dest],
                      ["CHANNEL",selAlert.channel],
                      ["AMOUNT",`${fmt(selAlert.amount)} ${selAlert.currency}`],
                      ["ENTITIES",selAlert.entities+" linked"],
                      ["ACCOUNTS",selAlert.accounts+" flagged"]].map(([k,v])=>(
                      <div key={k} style={{display:"flex",justifyContent:"space-between",
                        padding:"6px 0",borderBottom:"1px solid #0c1c28",fontSize:10}}>
                        <span style={{color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",fontSize:7.5,letterSpacing:.8}}>{k}</span>
                        <span style={{color:"#c8dae8"}}>{v}</span>
                      </div>
                    ))}

                    {/* ML Rationale */}
                    <div style={{marginTop:13,padding:11,background:"#060e14",borderRadius:8,border:"1px solid #1a3448"}}>
                      <div style={{fontSize:7.5,color:"#64d2ff",fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,marginBottom:5}}>◈ ML RATIONALE</div>
                      <div style={{fontSize:9.5,color:"#4a6a80",lineHeight:1.7}}>
                        {selAlert.model} flagged {selAlert.typology.toLowerCase()} indicators across {selAlert.accounts} accounts in the {selAlert.origin}→{selAlert.dest} corridor. Confidence {selAlert.conf}%. {selAlert.entities} co-located entities matched. Escalated to ensemble for secondary scoring.
                      </div>
                    </div>

                    {/* Actions */}
                    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:7,marginTop:13}}>
                      {[["FREEZE","#5e5ce6"],["ESCALATE","#ff2d55"],["ASSIGN","#64d2ff"],["EXPORT","#30d158"]].map(([l,c])=>(
                        <button key={l}
                          style={{background:c+"18",border:`1px solid ${c}66`,borderRadius:6,color:c,
                            fontSize:8,padding:"8px",cursor:"pointer",fontFamily:"'Share Tech Mono',monospace",
                            letterSpacing:.8,transition:"all .15s"}}
                          onMouseEnter={e=>e.currentTarget.style.background=c+"33"}
                          onMouseLeave={e=>e.currentTarget.style.background=c+"18"}>
                          {l}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ══════════════ NETWORK ══════════════ */}
            {tab==="network"&&(
              <div style={{display:"grid",gridTemplateColumns:selNode?"1fr 290px":"1fr",gap:14}}>
                <div style={{background:"#080f17",border:"1px solid #0c1c28",
                  borderRadius:10,padding:18,height:"calc(100vh - 120px)"}}>
                  <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:12}}>
                    <div style={{fontSize:8.5,fontFamily:"'Share Tech Mono',monospace",color:"#64d2ff",letterSpacing:1}}>
                      GNN ENTITY RELATIONSHIP GRAPH
                    </div>
                    <div style={{flex:1}}/>
                    {/* Node type legend */}
                    {[["◈","Entity"],["○","Account"],["◆","Broker"],["⚠","Threat"],["₿","Crypto"]].map(([icon,lbl])=>(
                      <div key={lbl} style={{display:"flex",alignItems:"center",gap:4,fontSize:8.5,color:"#3a6070"}}>
                        <span>{icon}</span><span style={{fontFamily:"'Share Tech Mono',monospace",fontSize:7.5}}>{lbl}</span>
                      </div>
                    ))}
                  </div>
                  <div style={{height:"calc(100% - 44px)",position:"relative"}}>
                    <NetworkGraph onNode={setSelNode}/>
                  </div>
                </div>

                {/* Node detail panel */}
                {selNode&&(
                  <div style={{background:"#080f17",border:`1px solid ${riskC(selNode.risk)}44`,
                    borderRadius:10,padding:20,alignSelf:"start",position:"sticky",top:0,animation:"fadeUp .2s ease"}}>
                    <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:14}}>
                      <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:17,fontWeight:700,color:riskC(selNode.risk)}}>{selNode.label}</div>
                      <button onClick={()=>setSelNode(null)}
                        style={{background:"transparent",border:"none",color:"#3a6070",fontSize:20,cursor:"pointer"}}>×</button>
                    </div>

                    <div style={{display:"flex",justifyContent:"center",marginBottom:14}}>
                      <ScoreRing score={selNode.risk} size={72}/>
                    </div>

                    {[["NODE TYPE",selNode.type.toUpperCase()],
                      ["RISK SCORE",selNode.risk],
                      ["CONNECTIONS",GRAPH_EDGES.filter(([a,b])=>a===selNode.id||b===selNode.id).length],
                      ["TOTAL FLOW","$"+fmt(GRAPH_EDGES.filter(([a,b])=>a===selNode.id||b===selNode.id).reduce((s,[,,w])=>s+w,0))],
                    ].map(([k,v])=>(
                      <div key={k} style={{display:"flex",justifyContent:"space-between",
                        padding:"7px 0",borderBottom:"1px solid #0c1c28",fontSize:10}}>
                        <span style={{color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",fontSize:7.5,letterSpacing:.8}}>{k}</span>
                        <span style={{color:"#c8dae8"}}>{v}</span>
                      </div>
                    ))}

                    {/* Neighbour list */}
                    <div style={{marginTop:12}}>
                      <div style={{fontSize:7.5,color:"#2a4860",fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,marginBottom:8}}>CONNECTED NODES</div>
                      <div style={{display:"flex",flexDirection:"column",gap:5}}>
                        {GRAPH_EDGES.filter(([a,b])=>a===selNode.id||b===selNode.id).map(([a,b,w],i)=>{
                          const otherId=a===selNode.id?b:a;
                          const other=GRAPH_NODES.find(n=>n.id===otherId);
                          if(!other) return null;
                          return(
                            <div key={i} style={{display:"flex",alignItems:"center",gap:8,
                              background:"#060e14",borderRadius:6,padding:"7px 10px",
                              border:`1px solid ${riskC(other.risk)}22`}}>
                              <div style={{width:6,height:6,borderRadius:"50%",background:riskC(other.risk),flexShrink:0}}/>
                              <div style={{flex:1}}>
                                <div style={{fontSize:9.5,color:"#c8dae8"}}>{other.label}</div>
                                <div style={{fontSize:8,color:"#3a6070",fontFamily:"'Share Tech Mono',monospace"}}>${fmt(w)}</div>
                              </div>
                              <div style={{fontSize:9,fontFamily:"'Rajdhani',sans-serif",fontWeight:700,color:riskC(other.risk)}}>{other.risk}</div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <div style={{marginTop:12,padding:10,background:"#060e14",borderRadius:8,
                      border:"1px solid #0c1c28",fontSize:9.5,color:"#4a6a80",lineHeight:1.7}}>
                      GCN propagation depth: {rnd(2,5)} hops. Classified as{" "}
                      <span style={{color:riskC(selNode.risk)}}>
                        {selNode.risk>=85?"HIGH RISK":selNode.risk>=70?"ELEVATED":selNode.risk>=50?"MODERATE":"LOW RISK"}
                      </span>{" "}by ensemble scoring.
                    </div>

                    <button onClick={()=>{setSelAlert(mkAlert());setTab("alerts");}}
                      style={{width:"100%",marginTop:12,background:"#ff2d5518",
                        border:"1px solid #ff2d5566",borderRadius:6,color:"#ff2d55",
                        padding:"8px",fontFamily:"'Share Tech Mono',monospace",fontSize:8.5,
                        cursor:"pointer",letterSpacing:.8}}>
                      VIEW LINKED ALERTS
                    </button>
                  </div>
                )}
              </div>
            )}

          </div>
        </div>
      </div>
    </>
  );
}

