
import { useState, useEffect, useRef, useCallback } from "react";

// ═══════════════════════════════════════════════════════════
// CONSTANTS & DATA
// ═══════════════════════════════════════════════════════════
const COUNTRIES=["Nigeria","Kenya","Senegal","Ghana","Ethiopia","Tanzania","Cameroon","Mali","Niger","Somalia","Sudan","DRC","Uganda","Chad","Mozambique"];
const CURRENCIES=["KES","NGN","XOF","ETB","TZS","GHS","USD","XAF"];
const CHANNELS=["Mobile Money","Bank Wire","Crypto","Hawala","Cash","Trade Finance","Remittance"];
const TYPOLOGIES=["Mobile Money Smurfing","Hawala Network","Shell Company Layering","Trade Misinvoicing","Cryptocurrency Mixing","NGO Abuse","Commodity Laundering","Cross-Border Structuring"];
const NETWORKS=["Al-Shabaab","Boko Haram","JNIM","ISIS-Sahel","Wagner-Linked","Unknown Affiliate","Suspected Cell"];

const MODELS=[
  {id:"gnn",name:"Graph Neural Network",short:"GNN",color:"#64d2ff",fw:"PyTorch Geometric",acc:94.2,prec:91.8,rec:96.1,f1:93.9,fpr:4.3,lat:38,params:"47M",status:"DEPLOYED",ver:"v3.1.2",samples:2840000,
   features:[{f:"Degree centrality",v:88},{f:"Betweenness",v:74},{f:"Edge velocity",v:69},{f:"Cluster coeff.",v:61},{f:"Node embedding",v:55}]},
  {id:"xgb",name:"XGBoost Ensemble",short:"XGB",color:"#30d158",fw:"XGBoost 2.0",acc:91.5,prec:89.3,rec:92.4,f1:90.8,fpr:7.1,lat:12,params:"2.1M trees",status:"DEPLOYED",ver:"v5.0.1",samples:6100000,
   features:[{f:"Txn velocity",v:92},{f:"Amount delta",v:83},{f:"Time-of-day",v:71},{f:"Cross-border",v:68},{f:"Account age",v:52}]},
  {id:"lstm",name:"LSTM Sequence",short:"LSTM",color:"#ff9f0a",fw:"TensorFlow 2.15",acc:89.7,prec:87.1,rec:91.9,f1:89.4,fpr:9.2,lat:61,params:"18M",status:"DEPLOYED",ver:"v2.4.0",samples:1920000,
   features:[{f:"Seq entropy",v:86},{f:"Burst pattern",v:79},{f:"Dormancy",v:73},{f:"Recip. pattern",v:64},{f:"Hour variance",v:48}]},
  {id:"iso",name:"Isolation Forest",short:"iForest",color:"#bf5af2",fw:"scikit-learn 1.4",acc:82.3,prec:78.6,rec:86.0,f1:82.1,fpr:14.8,lat:8,params:"500 trees",status:"DEPLOYED",ver:"v1.9.3",samples:9200000,
   features:[{f:"Isolation depth",v:95},{f:"Path length",v:81},{f:"Feature outlier",v:70},{f:"Sparse region",v:58},{f:"Contam. score",v:44}]},
  {id:"bert",name:"FinBERT NLP",short:"BERT",color:"#ff6b6b",fw:"HuggingFace 4.38",acc:88.1,prec:85.4,rec:90.7,f1:87.9,fpr:11.3,lat:145,params:"110M",status:"STAGING",ver:"v1.2.0-β",samples:840000,
   features:[{f:"Memo keywords",v:90},{f:"Entity NER",v:82},{f:"Language model",v:75},{f:"Semantic sim.",v:67},{f:"Token anomaly",v:53}]},
  {id:"gcn",name:"GCN Propagator",short:"GCN",color:"#ffd60a",fw:"DGL + PyTorch",acc:90.4,prec:88.2,rec:92.8,f1:90.4,fpr:8.6,lat:52,params:"23M",status:"TRAINING",ver:"v0.8-rc",samples:3400000,
   features:[{f:"Prop depth",v:89},{f:"Seed risk",v:84},{f:"Edge weight",v:72},{f:"Hop attenuation",v:60},{f:"Community",v:49}]},
];
const ENSEMBLE={acc:96.8,prec:94.9,rec:97.3,f1:96.1,fpr:2.4};

// Graph topology
const GNODES=[
  {id:1,x:420,y:200,risk:91,label:"Shell Co. A",type:"entity"},
  {id:2,x:220,y:90,risk:78,label:"ACC-NGA01",type:"account"},
  {id:3,x:620,y:90,risk:85,label:"ACC-KEN07",type:"account"},
  {id:4,x:160,y:300,risk:62,label:"Hawala Node",type:"broker"},
  {id:5,x:680,y:300,risk:93,label:"JNIM Cell",type:"entity"},
  {id:6,x:420,y:370,risk:74,label:"ACC-MLI04",type:"account"},
  {id:7,x:270,y:220,risk:55,label:"ACC-SEN02",type:"account"},
  {id:8,x:570,y:220,risk:88,label:"ACC-ETH09",type:"account"},
  {id:9,x:90,y:180,risk:44,label:"NGO-FRNT",type:"ngo"},
  {id:10,x:340,y:120,risk:67,label:"ACC-GHA03",type:"account"},
  {id:11,x:520,y:360,risk:79,label:"Crypto Wallet",type:"crypto"},
  {id:12,x:760,y:200,risk:71,label:"ACC-SDN05",type:"account"},
];
const GEDGES=[[1,2],[1,3],[2,4],[3,5],[4,6],[5,6],[7,1],[1,8],[8,5],[9,4],[7,4],[3,8],[10,1],[11,5],[6,11],[2,10],[5,12],[12,3]];

// Training histories
function genCurve(n,s,e,noise=0.02){
  return Array.from({length:n},(_,i)=>{
    const t=i/(n-1);
    return +(s+(e-s)*(1-Math.exp(-4*t))+(Math.random()-.5)*noise*2).toFixed(4);
  });
}
const HISTORIES={
  gnn:{train:genCurve(40,1.42,.18),val:genCurve(40,1.55,.23)},
  xgb:{train:genCurve(30,1.31,.24),val:genCurve(30,1.38,.28)},
  lstm:{train:genCurve(50,1.60,.29),val:genCurve(50,1.74,.35)},
  iso:{train:genCurve(20,.98,.42),val:genCurve(20,1.05,.48)},
  bert:{train:genCurve(35,1.85,.31),val:genCurve(35,1.98,.39)},
  gcn:{train:genCurve(45,1.51,.21),val:genCurve(45,1.63,.27)},
};

// ═══════════════════════════════════════════════════════════
// UTILS
// ═══════════════════════════════════════════════════════════
const rnd=(a,b)=>Math.floor(Math.random()*(b-a+1))+a;
const pick=a=>a[rnd(0,a.length-1)];
const uid=()=>Math.random().toString(36).slice(2,8).toUpperCase();
const fmt=n=>parseFloat(n).toLocaleString(undefined,{maximumFractionDigits:0});

function mkAlert(){
  const score=rnd(38,99);
  const m=pick(MODELS.filter(m=>m.status==="DEPLOYED"));
  return{
    id:`AQT-${uid()}`,ts:Date.now()-rnd(0,86400)*1000,
    origin:pick(COUNTRIES),dest:pick(COUNTRIES),
    amount:(Math.random()*980000+20000).toFixed(2),
    currency:pick(CURRENCIES),channel:pick(CHANNELS),
    typology:pick(TYPOLOGIES),network:pick(NETWORKS),
    score,sev:score>=85?"CRITICAL":score>=70?"HIGH":score>=55?"MEDIUM":"LOW",
    status:pick(["OPEN","UNDER REVIEW","ESCALATED","FROZEN"]),
    entities:rnd(2,9),accounts:rnd(3,18),
    model:m.short,mColor:m.color,conf:rnd(70,99),
  };
}
const ALERTS0=Array.from({length:50},mkAlert);

const sevColor=s=>s==="CRITICAL"?"#ff2d55":s==="HIGH"?"#ff9f0a":s==="MEDIUM"?"#ffd60a":"#30d158";
const riskColor=r=>r>=85?"#ff2d55":r>=70?"#ff9f0a":r>=50?"#ffd60a":"#30d158";
const statusColor=s=>s==="FROZEN"?"#5e5ce6":s==="ESCALATED"?"#ff2d55":s==="UNDER REVIEW"?"#ff9f0a":"#64d2ff";
const mStatusColor=s=>s==="DEPLOYED"?"#30d158":s==="STAGING"?"#ff9f0a":"#5e5ce6";

// ═══════════════════════════════════════════════════════════
// GLOBAL STYLES
// ═══════════════════════════════════════════════════════════
const CSS=`
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&family=DM+Sans:wght@300;400;500&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#05080f;color:#c0d4e8;font-family:'DM Sans',sans-serif;}
::-webkit-scrollbar{width:3px;height:3px;}
::-webkit-scrollbar-track{background:#080e18;}
::-webkit-scrollbar-thumb{background:#1a3348;border-radius:2px;}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}
@keyframes fadeIn{from{opacity:0;}to{opacity:1;}}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:.25;}}
@keyframes flash{0%{background:#ff2d5528;}100%{background:transparent;}}
@keyframes scan{0%{left:-40%;}100%{left:110%;}}
@keyframes flowDash{0%{stroke-dashoffset:20;}100%{stroke-dashoffset:0;}}
@keyframes glow{0%,100%{box-shadow:0 0 8px #64d2ff22;}50%{box-shadow:0 0 22px #64d2ff66;}}
@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
`;

// ═══════════════════════════════════════════════════════════
// MICRO COMPONENTS
// ═══════════════════════════════════════════════════════════
function Mono({children,color="#64d2ff",size=9}){
  return <span style={{fontFamily:"'Share Tech Mono',monospace",fontSize:size,color,letterSpacing:.8}}>{children}</span>;
}
function Label({children,color="#2a4f6a",sz=8}){
  return <div style={{fontSize:sz,fontFamily:"'Share Tech Mono',monospace",color,letterSpacing:1.5,marginBottom:8,textTransform:"uppercase"}}>{children}</div>;
}
function Card({children,style={},border="#0d1e2e",glow=false}){
  return(
    <div style={{background:"#080f1a",border:`1px solid ${border}`,borderRadius:10,
      boxShadow:glow?"0 0 30px #64d2ff0a":"none",...style}}>
      {children}
    </div>
  );
}
function Pill({children,color,size=8}){
  return(
    <span style={{background:color+"1a",border:`1px solid ${color}44`,borderRadius:4,
      color,fontSize:size,fontFamily:"'Share Tech Mono',monospace",padding:"2px 7px",letterSpacing:.8,display:"inline-block"}}>
      {children}
    </span>
  );
}
function Bar({v,max=100,color="#64d2ff",h=3}){
  return(
    <div style={{height:h,background:"#0d1e2e",borderRadius:h,overflow:"hidden"}}>
      <div style={{height:"100%",width:`${(v/max)*100}%`,background:color,borderRadius:h,transition:"width .7s cubic-bezier(.4,0,.2,1)"}}/>
    </div>
  );
}
function MetRow({label,value,max=100,color="#64d2ff",unit="%"}){
  return(
    <div style={{marginBottom:9}}>
      <div style={{display:"flex",justifyContent:"space-between",marginBottom:3}}>
        <Mono color="#2a4f6a" size={8}>{label}</Mono>
        <Mono color={color} size={9}>{value}{unit}</Mono>
      </div>
      <Bar v={value} max={max} color={color}/>
    </div>
  );
}
function ScoreRing({score,size=56}){
  const c=riskColor(score);
  const r=size/2-4,circ=2*Math.PI*r,dash=circ*(score/100);
  return(
    <div style={{position:"relative",width:size,height:size,flexShrink:0}}>
      <svg width={size} height={size} style={{transform:"rotate(-90deg)"}}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#0d1e2e" strokeWidth={3}/>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={c} strokeWidth={3}
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
          style={{transition:"stroke-dasharray .6s ease"}}/>
      </svg>
      <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",
        fontFamily:"'Rajdhani',sans-serif",fontSize:size*.3,fontWeight:700,color:c}}>{score}</div>
    </div>
  );
}
function Sparkline({data,color="#64d2ff",w=70,h=24,filled=false}){
  if(!data||data.length<2)return null;
  const mx=Math.max(...data),mn=Math.min(...data);
  const pts=data.map((v,i)=>[i/(data.length-1)*w, h-((v-mn)/(mx-mn||1))*h]);
  const poly=pts.map(p=>p.join(",")).join(" ");
  const area=`M0,${h} `+pts.map(p=>`L${p[0]},${p[1]}`).join(" ")+` L${w},${h} Z`;
  return(
    <svg width={w} height={h} style={{display:"block"}}>
      {filled&&<path d={area} fill={color} opacity=".1"/>}
      <polyline points={poly} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round"/>
      <circle cx={pts[pts.length-1][0]} cy={pts[pts.length-1][1]} r="2.5" fill={color}/>
    </svg>
  );
}
function LossCurve({id,w=280,h=80,live=null}){
  const hist=HISTORIES[id];if(!hist)return null;
  const train=live||hist.train;
  const val=hist.val.slice(0,train.length);
  const all=[...train,...val];
  const mx=Math.max(...all),mn=Math.min(...all);
  const sy=v=>h-((v-mn)/(mx-mn||1))*h;
  const mkPts=arr=>arr.map((v,i)=>`${(i/Math.max(arr.length-1,1))*w},${sy(v)}`).join(" ");
  return(
    <svg width={w} height={h}>
      <defs>
        <linearGradient id={`lg${id}`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#64d2ff" stopOpacity=".5"/>
          <stop offset="100%" stopColor="#64d2ff"/>
        </linearGradient>
      </defs>
      {train.length>1&&<polyline points={mkPts(train)} fill="none" stroke={`url(#lg${id})`} strokeWidth="2" strokeLinejoin="round"/>}
      {val.length>1&&<polyline points={mkPts(val)} fill="none" stroke="#ff9f0a" strokeWidth="1.5" strokeLinejoin="round" strokeDasharray="4,3"/>}
      <text x={4} y={10} fill="#64d2ff" fontSize="7.5" fontFamily="'Share Tech Mono',monospace">Train</text>
      <text x={38} y={10} fill="#ff9f0a" fontSize="7.5" fontFamily="'Share Tech Mono',monospace">Val</text>
      {train.length>0&&<circle cx={(train.length-1)/Math.max(train.length-1,1)*w} cy={sy(train[train.length-1])} r="3" fill="#64d2ff"/>}
    </svg>
  );
}
function RocCurve({model,w=160,h=120}){
  const pts=[[0,0]];
  for(let i=1;i<=30;i++){const fpr=i/30;const tpr=Math.min(1,Math.pow(fpr,.14-(model.acc-80)/360));pts.push([fpr*w,h-tpr*h]);}
  pts.push([w,h]);
  const poly=pts.map(p=>p.join(",")).join(" ");
  const area="M0,"+h+" "+pts.slice(0,-1).map(p=>`L${p[0]},${p[1]}`).join(" ")+" L"+w+","+h+" Z";
  const auc=(0.5+model.acc/200).toFixed(3);
  return(
    <svg width={w} height={h}>
      <line x1={0} y1={h} x2={w} y2={0} stroke="#1a3348" strokeWidth={1} strokeDasharray="4,3"/>
      <path d={area} fill={model.color} opacity=".07"/>
      <polyline points={poly} fill="none" stroke={model.color} strokeWidth="2" strokeLinejoin="round"/>
      <rect x={w-54} y={2} width={52} height={14} rx={3} fill="#05080f" opacity=".9"/>
      <text x={w-4} y={12} textAnchor="end" fill={model.color} fontSize="8.5" fontFamily="'Share Tech Mono',monospace">AUC {auc}</text>
    </svg>
  );
}
function ConfMatrix({model}){
  const tp=Math.round(model.rec*820/100),fn=820-tp;
  const fp=Math.round(model.fpr*180/10),tn=180-fp;
  const cells=[{l:"TP",v:tp,c:"#30d158"},{l:"FN",v:fn,c:"#ff9f0a"},{l:"FP",v:fp,c:"#ff2d55"},{l:"TN",v:tn,c:"#64d2ff"}];
  return(
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:4}}>
      {cells.map(c=>(
        <div key={c.l} style={{background:"#05080f",border:`1px solid ${c.c}22`,borderRadius:6,padding:"7px",textAlign:"center"}}>
          <Label color={c.c} sz={7}>{c.l}</Label>
          <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:18,fontWeight:700,color:c.c}}>{c.v}</div>
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// TRAINING MODAL
// ═══════════════════════════════════════════════════════════
function TrainingModal({model,onClose}){
  const [phase,setPhase]=useState("idle");
  const [epoch,setEpoch]=useState(0);
  const [liveData,setLiveData]=useState([]);
  const [log,setLog]=useState([]);
  const [cfg,setCfg]=useState({epochs:30,lr:"3e-4",batch:4096,dropout:"0.2",wd:"1e-4"});
  const logRef=useRef(null);
  const iv=useRef(null);
  const hist=HISTORIES[model.id];
  const total=+cfg.epochs||30;

  const start=()=>{
    setPhase("running");setEpoch(0);setLiveData([]);setLog([]);
    iv.current=setInterval(()=>{
      setEpoch(e=>{
        const ne=e+1;
        const idx=Math.min(ne-1,hist.train.length-1);
        const tl=+(hist.train[idx]+(Math.random()-.5)*.012).toFixed(4);
        const vl=+(hist.val[idx]+(Math.random()-.5)*.015).toFixed(4);
        const ac=+(model.acc-(total-ne)/total*12+Math.random()*.5).toFixed(2);
        setLiveData(d=>[...d,tl]);
        setLog(l=>[...l,{ep:ne,tl,vl,ac,lr:(parseFloat(cfg.lr)*Math.pow(.98,ne)).toExponential(2)}]);
        if(ne>=total){clearInterval(iv.current);setPhase("done");}
        return ne;
      });
    },90);
  };
  const stop=()=>{clearInterval(iv.current);setPhase("idle");};
  useEffect(()=>()=>clearInterval(iv.current),[]);
  useEffect(()=>{if(logRef.current)logRef.current.scrollTop=logRef.current.scrollHeight;},[log]);
  const pct=Math.min(100,Math.round((epoch/total)*100));

  return(
    <div style={{position:"fixed",inset:0,background:"#000000d0",zIndex:300,display:"flex",alignItems:"center",justifyContent:"center",animation:"fadeIn .2s"}}
      onClick={e=>e.target===e.currentTarget&&onClose()}>
      <div style={{background:"#080f1a",border:`1px solid ${model.color}44`,borderRadius:14,width:600,maxHeight:"88vh",
        overflow:"hidden",display:"flex",flexDirection:"column",boxShadow:`0 0 80px ${model.color}18`}}>
        {/* Header */}
        <div style={{padding:"14px 20px",borderBottom:"1px solid #0d1e2e",background:"#05080f",display:"flex",alignItems:"center",gap:10}}>
          <div style={{width:9,height:9,borderRadius:"50%",background:model.color,animation:phase==="running"?"pulse .8s infinite":"none"}}/>
          <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:17,fontWeight:700,color:"#d0e4f4"}}>{model.name}</div>
          <Mono color="#1a3348" size={9}>TRAINING CONSOLE</Mono>
          <div style={{flex:1}}/>
          <Pill color={model.color}>{model.fw}</Pill>
          <button onClick={onClose} style={{background:"transparent",border:"none",color:"#2a4f6a",fontSize:22,cursor:"pointer",lineHeight:1}}>×</button>
        </div>
        <div style={{padding:20,overflowY:"auto",flex:1}}>
          {/* Hyperparams */}
          <Label color="#2a4f6a">HYPERPARAMETERS</Label>
          <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:8,marginBottom:16}}>
            {[["Epochs",cfg.epochs,"epochs"],["Learning Rate",cfg.lr,"lr"],["Batch Size",cfg.batch,"batch"],
              ["Dropout",cfg.dropout,"dropout"],["Weight Decay",cfg.wd,"wd"],["Parameters",model.params,""]].map(([lbl,val,key])=>(
              <div key={lbl} style={{background:"#05080f",borderRadius:8,padding:"9px 12px",border:"1px solid #0d1e2e"}}>
                <Label color="#1a3348" sz={7}>{lbl}</Label>
                {key&&phase==="idle"
                  ?<input value={val} onChange={e=>setCfg(c=>({...c,[key]:e.target.value}))}
                      style={{background:"transparent",border:"none",outline:"none",color:"#c0d4e8",fontFamily:"'Share Tech Mono',monospace",fontSize:11,width:"100%"}}/>
                  :<Mono color="#c0d4e8" size={11}>{val}</Mono>
                }
              </div>
            ))}
          </div>
          {/* Progress */}
          {phase!=="idle"&&(
            <div style={{marginBottom:16}}>
              <div style={{display:"flex",justifyContent:"space-between",marginBottom:5}}>
                <Mono color="#2a4f6a" size={8}>EPOCH {epoch}/{total}</Mono>
                <span style={{fontFamily:"'Rajdhani',sans-serif",fontSize:13,fontWeight:700,color:model.color}}>{pct}%</span>
              </div>
              <div style={{height:6,background:"#0d1e2e",borderRadius:3,overflow:"hidden",position:"relative"}}>
                <div style={{height:"100%",width:`${pct}%`,background:`linear-gradient(90deg,${model.color}88,${model.color})`,borderRadius:3,transition:"width .09s",position:"relative"}}>
                  <div style={{position:"absolute",right:0,top:0,bottom:0,width:24,background:"linear-gradient(90deg,transparent,#fff3)",animation:phase==="running"?"scan .9s linear infinite":"none"}}/>
                </div>
              </div>
              {log.length>0&&(
                <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:6,marginTop:10}}>
                  {[["Train Loss",log[log.length-1].tl,model.color],["Val Loss",log[log.length-1].vl,"#ff9f0a"],
                    ["Accuracy",log[log.length-1].ac+"%","#30d158"],["LR",log[log.length-1].lr,"#bf5af2"]].map(([k,v,c])=>(
                    <div key={k} style={{background:"#05080f",borderRadius:6,padding:"7px",textAlign:"center",border:"1px solid #0d1e2e"}}>
                      <Label color="#1a3348" sz={7}>{k}</Label>
                      <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:13,fontWeight:700,color:c}}>{v}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          {/* Live loss */}
          {liveData.length>1&&(
            <div style={{background:"#05080f",borderRadius:8,padding:12,marginBottom:14,border:"1px solid #0d1e2e"}}>
              <Label color="#1a3348" sz={7}>LIVE LOSS CURVE</Label>
              <LossCurve id={model.id} w={520} h={80} live={liveData}/>
            </div>
          )}
          {/* Log */}
          <div ref={logRef} style={{background:"#05080f",borderRadius:8,padding:12,fontFamily:"'Share Tech Mono',monospace",
            fontSize:9,maxHeight:130,overflowY:"auto",border:"1px solid #0d1e2e",lineHeight:1.8}}>
            {log.length===0&&<div style={{color:"#1a3348"}}>{'>'} Awaiting training run…</div>}
            {log.slice(-30).map((l,i)=>(
              <div key={l.ep} style={{color:i===log.slice(-30).length-1?model.color:"#1e4a6a"}}>
                {'>'} [{String(l.ep).padStart(3,"0")}/{total}] loss={l.tl}  val={l.vl}  acc={l.ac}%  lr={l.lr}
              </div>
            ))}
            {phase==="done"&&<div style={{color:"#30d158",marginTop:4}}>{'>'} ✓ Training complete — model ready for deployment.</div>}
          </div>
        </div>
        {/* Footer */}
        <div style={{padding:"12px 20px",borderTop:"1px solid #0d1e2e",background:"#05080f",display:"flex",gap:8,alignItems:"center"}}>
          {phase==="idle"&&<button onClick={start}
            style={{background:model.color+"1a",border:`1px solid ${model.color}`,borderRadius:6,color:model.color,
              padding:"8px 20px",fontFamily:"'Share Tech Mono',monospace",fontSize:9.5,cursor:"pointer",letterSpacing:.8}}>
            ▶ START TRAINING</button>}
          {phase==="running"&&<button onClick={stop}
            style={{background:"#ff2d551a",border:"1px solid #ff2d55",borderRadius:6,color:"#ff2d55",
              padding:"8px 20px",fontFamily:"'Share Tech Mono',monospace",fontSize:9.5,cursor:"pointer",letterSpacing:.8}}>
            ■ ABORT</button>}
          {phase==="done"&&<button onClick={onClose}
            style={{background:"#30d1581a",border:"1px solid #30d158",borderRadius:6,color:"#30d158",
              padding:"8px 24px",fontFamily:"'Share Tech Mono',monospace",fontSize:9.5,cursor:"pointer",letterSpacing:.8,animation:"glow 2s infinite"}}>
            ✓ DEPLOY MODEL</button>}
          <button onClick={onClose}
            style={{background:"transparent",border:"1px solid #1a3348",borderRadius:6,color:"#2a4f6a",
              padding:"8px 14px",fontFamily:"'Share Tech Mono',monospace",fontSize:9.5,cursor:"pointer"}}>CLOSE</button>
          {phase==="done"&&<div style={{marginLeft:"auto",fontSize:9,color:"#30d158",fontFamily:"'Share Tech Mono',monospace"}}>
            F1={model.f1}%  Acc={model.acc}%</div>}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// NETWORK GRAPH
// ═══════════════════════════════════════════════════════════
function NetworkGraph({onNodeClick,compact=false}){
  const [hover,setHover]=useState(null);
  const [sel,setSel]=useState(null);
  const [pulses,setPulses]=useState([]);
  const [zoom,setZoom]=useState(1);
  const W=compact?580:860,H=compact?320:480;

  useEffect(()=>{
    const t=setInterval(()=>{
      const e=GEDGES[rnd(0,GEDGES.length-1)];
      setPulses(p=>[...p.slice(-8),{id:Date.now(),from:e[0],to:e[1],c:Math.random()>.7?"#ff2d55":"#64d2ff"}]);
    },1200);
    return()=>clearInterval(t);
  },[]);

  const handleNode=n=>{
    setSel(s=>s===n.id?null:n.id);
    onNodeClick&&onNodeClick(n);
  };

  // Scale nodes to viewport
  const scaleX=x=>(x/860)*W;
  const scaleY=y=>(y/480)*H;

  return(
    <div style={{position:"relative",width:"100%",height:"100%"}}>
      {!compact&&(
        <div style={{position:"absolute",top:8,right:8,display:"flex",gap:5,zIndex:10}}>
          {["+","-"].map(z=>(
            <button key={z} onClick={()=>setZoom(s=>Math.max(.5,Math.min(2.2,s+(z==="+"?.25:-.25))))}
              style={{background:"#080f1a",border:"1px solid #1a3348",borderRadius:4,color:"#64d2ff",
                width:26,height:26,cursor:"pointer",fontSize:15,display:"flex",alignItems:"center",justifyContent:"center"}}>
              {z}
            </button>
          ))}
          <button onClick={()=>setZoom(1)}
            style={{background:"#080f1a",border:"1px solid #1a3348",borderRadius:4,color:"#2a4f6a",
              fontSize:8,padding:"0 7px",cursor:"pointer",fontFamily:"'Share Tech Mono',monospace"}}>RST</button>
        </div>
      )}
      <svg width="100%" height="100%"
        viewBox={`${(1-zoom)*W/2} ${(1-zoom)*H/2} ${W*zoom} ${H*zoom}`}>
        <defs>
          <filter id="fg1"><feGaussianBlur stdDeviation="3" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
          <filter id="fg2"><feGaussianBlur stdDeviation="6" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
          <filter id="fg3"><feGaussianBlur stdDeviation="1.5" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        {/* Background grid */}
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#0a1628" strokeWidth=".5"/>
          </pattern>
        </defs>
        <rect width={W} height={H} fill="url(#grid)" opacity=".5"/>
        {/* Edges */}
        {GEDGES.map(([a,b],i)=>{
          const na=GNODES.find(n=>n.id===a),nb=GNODES.find(n=>n.id===b);
          const hot=hover===a||hover===b||sel===a||sel===b;
          return(
            <g key={i}>
              <line x1={scaleX(na.x)} y1={scaleY(na.y)} x2={scaleX(nb.x)} y2={scaleY(nb.y)}
                stroke={hot?"#1e4a70":"#0c1e30"} strokeWidth={hot?2:1} style={{transition:"all .2s"}}/>
              <line x1={scaleX(na.x)} y1={scaleY(na.y)} x2={scaleX(nb.x)} y2={scaleY(nb.y)}
                stroke="#64d2ff" strokeWidth=".6" opacity=".15"
                strokeDasharray="6,6" style={{animation:"flowDash 2s linear infinite"}}/>
            </g>
          );
        })}
        {/* Pulses */}
        {pulses.map(p=>{
          const na=GNODES.find(n=>n.id===p.from),nb=GNODES.find(n=>n.id===p.to);
          if(!na||!nb)return null;
          return(
            <circle key={p.id} r="4.5" fill={p.c} filter="url(#fg1)">
              <animateMotion dur="1.1s" fill="freeze"
                path={`M${scaleX(na.x)},${scaleY(na.y)} L${scaleX(nb.x)},${scaleY(nb.y)}`}/>
              <animate attributeName="opacity" values="1;.7;0" dur="1.1s" fill="freeze"/>
              <animate attributeName="r" values="4.5;3;1.5" dur="1.1s" fill="freeze"/>
            </circle>
          );
        })}
        {/* Nodes */}
        {GNODES.map(n=>{
          const c=riskColor(n.risk);
          const isH=hover===n.id,isS=sel===n.id;
          const nx=scaleX(n.x),ny=scaleY(n.y);
          return(
            <g key={n.id} onClick={()=>handleNode(n)}
              onMouseEnter={()=>setHover(n.id)} onMouseLeave={()=>setHover(null)}
              style={{cursor:"pointer"}}>
              {(isH||isS)&&<circle cx={nx} cy={ny} r="28" fill={c} opacity=".07" filter="url(#fg2)"/>}
              {isS&&<circle cx={nx} cy={ny} r="20" fill="none" stroke={c} strokeWidth="1.5" opacity=".4" strokeDasharray="5,3"/>}
              {/* Node glow ring */}
              <circle cx={nx} cy={ny} r="16" fill="#0a1628" stroke={c} strokeWidth={isS?2.5:isH?2:1.5}
                filter={isH||isS?"url(#fg1)":"url(#fg3)"} style={{transition:"all .2s"}}/>
              {/* Inner dot */}
              <circle cx={nx} cy={ny} r="6" fill={c} opacity={isH?1:.7}/>
              {/* Type indicator */}
              <text x={nx} y={ny+1} textAnchor="middle" dominantBaseline="middle"
                fill="#05080f" fontSize="7" fontFamily="'Share Tech Mono',monospace">
                {n.type==="entity"?"E":n.type==="broker"?"B":n.type==="crypto"?"₿":n.type==="ngo"?"N":"A"}
              </text>
              {/* Label */}
              <text x={nx} y={ny+30} textAnchor="middle"
                fill={isH?c:"#3a6080"} fontSize="8.5" fontFamily="'Share Tech Mono',monospace"
                style={{transition:"fill .2s"}}>{n.label}</text>
              {/* Risk score on hover */}
              {isH&&<text x={nx} y={ny+41} textAnchor="middle" fill={c} fontSize="7.5"
                fontFamily="'Share Tech Mono',monospace">RISK {n.risk}</text>}
            </g>
          );
        })}
      </svg>
      {/* Legend */}
      <div style={{position:"absolute",bottom:10,left:10,background:"#05080fcc",border:"1px solid #0d1e2e",
        borderRadius:6,padding:"8px 10px",display:"flex",gap:12}}>
        {[{c:"#ff2d55",l:"Critical"},{c:"#ff9f0a",l:"High"},{c:"#ffd60a",l:"Medium"},{c:"#30d158",l:"Low"}].map(x=>(
          <div key={x.l} style={{display:"flex",alignItems:"center",gap:5}}>
            <div style={{width:7,height:7,borderRadius:"50%",background:x.c}}/>
            <Mono color="#3a6080" size={8}>{x.l}</Mono>
          </div>
        ))}
        <div style={{width:1,background:"#0d1e2e"}}/>
        {[{l:"E=Entity"},{l:"A=Account"},{l:"B=Broker"},{l:"₿=Crypto"},{l:"N=NGO"}].map(x=>(
          <Mono key={x.l} color="#2a4060" size={7.5}>{x.l}</Mono>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// ALERT TABLE
// ═══════════════════════════════════════════════════════════
function AlertTable({alerts,onSelect,selId}){
  const cols=["ID","SEV","ROUTE","AMOUNT","TYPOLOGY","MODEL","SCORE","STATUS"];
  return(
    <Card>
      <div style={{display:"grid",gridTemplateColumns:"100px 76px 145px 115px 185px 75px 52px 100px",
        padding:"8px 14px",background:"#05080f",borderBottom:"1px solid #0d1e2e"}}>
        {cols.map(c=><Mono key={c} color="#1a3348" size={7.5}>{c}</Mono>)}
      </div>
      <div style={{overflowY:"auto",maxHeight:"52vh"}}>
        {alerts.map((a,i)=>(
          <div key={a.id} onClick={()=>onSelect(a)}
            style={{display:"grid",gridTemplateColumns:"100px 76px 145px 115px 185px 75px 52px 100px",
              padding:"8px 14px",borderBottom:"1px solid #080e18",cursor:"pointer",fontSize:10,
              background:a.id===selId?"#0a2035":a.sev==="CRITICAL"?"#160509":i%2===0?"#080f1a":"#05080f",
              animation:i===0?"fadeUp .3s ease":"none",transition:"background .1s"}}
            onMouseEnter={e=>a.id!==selId&&(e.currentTarget.style.background="#0c1a28")}
            onMouseLeave={e=>a.id!==selId&&(e.currentTarget.style.background=a.id===selId?"#0a2035":a.sev==="CRITICAL"?"#160509":i%2===0?"#080f1a":"#05080f")}>
            <Mono color="#64d2ff" size={9}>{a.id}</Mono>
            <div style={{display:"flex",alignItems:"center",gap:4}}>
              <div style={{width:5,height:5,borderRadius:"50%",background:sevColor(a.sev),flexShrink:0}}/>
              <Mono color={sevColor(a.sev)} size={7.5}>{a.sev}</Mono>
            </div>
            <div style={{color:"#5a8090",fontSize:9}}>{a.origin.slice(0,7)}→{a.dest.slice(0,7)}</div>
            <div style={{fontSize:9}}>{fmt(a.amount)} <Mono color="#1a3348" size={7.5}>{a.currency}</Mono></div>
            <div style={{fontSize:9,color:"#4a7090"}}>{a.typology.split(" ").slice(0,3).join(" ")}</div>
            <Mono color={a.mColor} size={8}>{a.model}</Mono>
            <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:13,fontWeight:700,color:riskColor(a.score)}}>{a.score}</div>
            <Mono color={statusColor(a.status)} size={8}>● {a.status}</Mono>
          </div>
        ))}
      </div>
    </Card>
  );
}

// ═══════════════════════════════════════════════════════════
// MAIN APP
// ═══════════════════════════════════════════════════════════
const NAV=[
  {id:"dash",icon:"⬡",lbl:"Dashboard"},
  {id:"network",icon:"◎",lbl:"Network Graph"},
  {id:"models",icon:"◈",lbl:"ML Models"},
  {id:"training",icon:"▲",lbl:"Training"},
  {id:"compare",icon:"⇄",lbl:"Compare"},
  {id:"alerts",icon:"◉",lbl:"Alerts"},
];

export default function App(){
  const [tab,setTab]=useState("dash");
  const [alerts,setAlerts]=useState(ALERTS0);
  const [selAlert,setSelAlert]=useState(null);
  const [selModel,setSelModel]=useState(null);
  const [trainModel,setTrainModel]=useState(null);
  const [selNode,setSelNode]=useState(null);
  const [live,setLive]=useState(true);
  const [flash,setFlash]=useState(false);
  const [cmpIds,setCmpIds]=useState(["gnn","xgb","lstm"]);
  const [search,setSearch]=useState("");
  const [fSev,setFSev]=useState("ALL");
  const [fMod,setFMod]=useState("ALL");
  const spark=useRef(Array.from({length:24},()=>rnd(5,45)));

  useEffect(()=>{
    if(!live)return;
    const t=setInterval(()=>{
      if(Math.random()>.4){
        setAlerts(p=>[mkAlert(),...p.slice(0,79)]);
        setFlash(true);setTimeout(()=>setFlash(false),500);
      }
      spark.current=[...spark.current.slice(1),rnd(5,45)];
    },2600);
    return()=>clearInterval(t);
  },[live]);

  const filtered=alerts.filter(a=>{
    if(fSev!=="ALL"&&a.sev!==fSev)return false;
    if(fMod!=="ALL"&&a.model!==fMod)return false;
    if(search&&!a.id.includes(search.toUpperCase())
      &&!a.origin.toLowerCase().includes(search.toLowerCase())
      &&!a.typology.toLowerCase().includes(search.toLowerCase())
      &&!a.network.toLowerCase().includes(search.toLowerCase()))return false;
    return true;
  });

  const critical=alerts.filter(a=>a.sev==="CRITICAL").length;
  const high=alerts.filter(a=>a.sev==="HIGH").length;
  const frozen=alerts.filter(a=>a.status==="FROZEN").length;

  return(
    <>
      <style>{CSS}</style>
      {trainModel&&<TrainingModal model={trainModel} onClose={()=>setTrainModel(null)}/>}
      <div style={{display:"flex",height:"100vh",background:"#05080f",overflow:"hidden"}}>

        {/* ── SIDEBAR ── */}
        <div style={{width:58,background:"#05080f",borderRight:"1px solid #0a1628",
          display:"flex",flexDirection:"column",alignItems:"center",paddingTop:12,gap:2,flexShrink:0}}>
          {/* Logo */}
          <div style={{width:36,height:36,background:"linear-gradient(135deg,#0a3050,#0d5a8a)",
            borderRadius:9,display:"flex",alignItems:"center",justifyContent:"center",
            marginBottom:16,fontSize:17,boxShadow:"0 0 24px #0a305088"}}>🦅</div>
          {NAV.map(n=>(
            <button key={n.id} onClick={()=>setTab(n.id)} title={n.lbl}
              style={{width:42,height:42,background:tab===n.id?"#0c1e30":"transparent",
                border:"none",borderRadius:8,color:tab===n.id?"#64d2ff":"#1e3a52",
                fontSize:15,cursor:"pointer",transition:"all .15s",
                borderLeft:tab===n.id?"2px solid #64d2ff":"2px solid transparent"}}>
              {n.icon}
            </button>
          ))}
          <div style={{flex:1}}/>
          {/* Live dot */}
          <div style={{width:7,height:7,borderRadius:"50%",
            background:live?"#30d158":"#1e3a52",marginBottom:12,
            animation:live?"pulse 2s infinite":"none",cursor:"pointer"}}
            onClick={()=>setLive(l=>!l)} title={live?"Live":"Paused"}/>
        </div>

        {/* ── MAIN ── */}
        <div style={{flex:1,display:"flex",flexDirection:"column",overflow:"hidden"}}>

          {/* ── TOPBAR ── */}
          <div style={{height:48,background:"#05080f",borderBottom:"1px solid #0a1628",
            display:"flex",alignItems:"center",padding:"0 16px",gap:12,flexShrink:0}}>
            <span style={{fontFamily:"'Rajdhani',sans-serif",fontSize:18,fontWeight:700,
              color:"#64d2ff",letterSpacing:3}}>AQUILA TRACE</span>
            <Mono color="#0e2840" size={8}>ML INTELLIGENCE · v3.0</Mono>
            <div style={{flex:1}}/>
            {/* Model status strip */}
            {MODELS.map(m=>(
              <div key={m.id} onClick={()=>{setSelModel(m);setTab("models");}}
                style={{display:"flex",alignItems:"center",gap:4,background:"#080f1a",
                  border:`1px solid ${mStatusColor(m.status)}22`,borderRadius:4,
                  padding:"3px 7px",cursor:"pointer",transition:"border-color .15s"}}
                onMouseEnter={e=>e.currentTarget.style.borderColor=mStatusColor(m.status)+"66"}
                onMouseLeave={e=>e.currentTarget.style.borderColor=mStatusColor(m.status)+"22"}>
                <div style={{width:5,height:5,borderRadius:"50%",background:mStatusColor(m.status),
                  animation:m.status==="TRAINING"?"pulse .9s infinite":"none"}}/>
                <Mono color="#2a4060" size={7.5}>{m.short}</Mono>
              </div>
            ))}
            <div style={{width:1,height:20,background:"#0a1628"}}/>
            <button onClick={()=>setLive(l=>!l)}
              style={{background:"transparent",border:`1px solid ${live?"#30d15855":"#1a3348"}`,
                borderRadius:5,color:live?"#30d158":"#2a4060",fontSize:8.5,
                fontFamily:"'Share Tech Mono',monospace",padding:"4px 11px",cursor:"pointer",letterSpacing:.8}}>
              {live?"● LIVE":"○ PAUSED"}
            </button>
            <Mono color="#0e2840" size={8}>{new Date().toUTCString().slice(5,22)} UTC</Mono>
          </div>

          {/* ── CONTENT ── */}
          <div style={{flex:1,overflow:"auto",padding:16}}>

            {/* ════════ DASHBOARD ════════ */}
            {tab==="dash"&&(
              <div style={{display:"grid",gap:14,animation:"fadeUp .3s ease"}}>
                {/* KPIs */}
                <div style={{display:"grid",gridTemplateColumns:"repeat(5,1fr)",gap:10}}>
                  {[
                    {lbl:"ENSEMBLE ACC",val:`${ENSEMBLE.acc}%`,color:"#64d2ff",sub:"6-model stack",flash:false},
                    {lbl:"CRITICAL",val:critical,color:"#ff2d55",sub:"Active alerts",flash},
                    {lbl:"HIGH RISK",val:high,color:"#ff9f0a",sub:`${alerts.length} total`},
                    {lbl:"FROZEN",val:frozen,color:"#5e5ce6",sub:"Accounts seized"},
                    {lbl:"FALSE POS RATE",val:`${ENSEMBLE.fpr}%`,color:"#30d158",sub:"Ensemble avg"},
                  ].map((k,i)=>(
                    <Card key={i} style={{padding:"13px 15px",position:"relative",overflow:"hidden",
                      animation:k.flash?"flash .4s ease":"none"}}
                      border={k.flash?"#ff2d5544":"#0d1e2e"}>
                      <div style={{position:"absolute",top:0,left:0,right:0,height:2,
                        background:`linear-gradient(90deg,transparent,${k.color},transparent)`,opacity:.5}}/>
                      <Mono color="#1a3348" size={7.5}>{k.lbl}</Mono>
                      <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:30,fontWeight:700,
                        color:k.color,lineHeight:1,marginTop:4}}>{k.val}</div>
                      <div style={{fontSize:9,color:"#1e3a52",marginTop:4}}>{k.sub}</div>
                    </Card>
                  ))}
                </div>

                {/* Middle row */}
                <div style={{display:"grid",gridTemplateColumns:"5fr 2fr",gap:12}}>
                  {/* Network preview */}
                  <Card style={{padding:14,height:320}}>
                    <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:10}}>
                      <Label color="#1a3348">GNN ENTITY CLUSTER — LIVE</Label>
                      <div style={{flex:1}}/>
                      <Sparkline data={spark.current} color="#64d2ff" w={60} h={18} filled/>
                      <button onClick={()=>setTab("network")}
                        style={{background:"transparent",border:"1px solid #1a3348",borderRadius:4,
                          color:"#2a4060",fontSize:7.5,padding:"2px 8px",cursor:"pointer",
                          fontFamily:"'Share Tech Mono',monospace"}}>EXPAND ↗</button>
                    </div>
                    <div style={{height:"calc(100% - 36px)"}}>
                      <NetworkGraph onNodeClick={n=>{setSelNode(n);}} compact={true}/>
                    </div>
                  </Card>

                  {/* Ensemble metrics */}
                  <div style={{display:"flex",flexDirection:"column",gap:10}}>
                    <Card style={{padding:14,flex:1}} border="#64d2ff22">
                      <Label color="#1a4060">ENSEMBLE METRICS</Label>
                      <MetRow label="ACCURACY" value={ENSEMBLE.acc} color="#64d2ff"/>
                      <MetRow label="PRECISION" value={ENSEMBLE.prec} color="#30d158"/>
                      <MetRow label="RECALL" value={ENSEMBLE.rec} color="#5e5ce6"/>
                      <MetRow label="F1 SCORE" value={ENSEMBLE.f1} color="#ff9f0a"/>
                      <MetRow label="FALSE POS RATE" value={ENSEMBLE.fpr} max={30} color="#ff2d55"/>
                    </Card>
                    <Card style={{padding:14,flex:1}}>
                      <Label color="#1a3348">DETECTIONS / MODEL</Label>
                      {MODELS.map(m=>{
                        const cnt=alerts.filter(a=>a.model===m.short).length;
                        const pct=Math.round(cnt/Math.max(alerts.length,1)*100);
                        return(
                          <div key={m.id} style={{marginBottom:7}}>
                            <div style={{display:"flex",justifyContent:"space-between",marginBottom:2}}>
                              <Mono color={m.color} size={8}>{m.short}</Mono>
                              <Mono color="#1a3348" size={8}>{cnt}</Mono>
                            </div>
                            <Bar v={pct} color={m.color} h={3}/>
                          </div>
                        );
                      })}
                    </Card>
                  </div>
                </div>

                {/* Recent alerts */}
                <Card style={{padding:14}}>
                  <div style={{display:"flex",alignItems:"center",marginBottom:10}}>
                    <Label color="#1a3348">RECENT DETECTIONS</Label>
                    <div style={{marginLeft:8,width:6,height:6,borderRadius:"50%",background:"#ff2d55",
                      animation:flash?"pulse .5s":"none"}}/>
                    <div style={{flex:1}}/>
                    <button onClick={()=>setTab("alerts")}
                      style={{background:"transparent",border:"1px solid #1a3348",borderRadius:4,
                        color:"#2a4060",fontSize:7.5,padding:"2px 8px",cursor:"pointer",
                        fontFamily:"'Share Tech Mono',monospace"}}>VIEW ALL ↗</button>
                  </div>
                  <AlertTable alerts={alerts.slice(0,8)} onSelect={a=>{setSelAlert(a);setTab("alerts");}} selId={selAlert?.id}/>
                </Card>
              </div>
            )}

            {/* ════════ NETWORK GRAPH ════════ */}
            {tab==="network"&&(
              <div style={{display:"grid",gridTemplateColumns:selNode?"1fr 270px":"1fr",gap:14,animation:"fadeUp .3s ease"}}>
                <Card style={{padding:16,height:"calc(100vh - 110px)"}}>
                  <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:12}}>
                    <Label color="#1a4060">GNN ENTITY RELATIONSHIP NETWORK</Label>
                    <div style={{flex:1}}/>
                    <Mono color="#1a3348" size={8}>{GNODES.length} NODES · {GEDGES.length} EDGES · 3 CLUSTERS</Mono>
                  </div>
                  <div style={{height:"calc(100% - 40px)",position:"relative"}}>
                    <NetworkGraph onNodeClick={setSelNode}/>
                    <div style={{position:"absolute",top:10,left:10,background:"#05080fcc",
                      border:"1px solid #0d1e2e",borderRadius:6,padding:"8px 10px"}}>
                      <div style={{display:"flex",flexDirection:"column",gap:5}}>
                        {[
                          {color:"#ff2d55",cnt:GNODES.filter(n=>n.risk>=85).length,lbl:"Critical risk nodes"},
                          {color:"#ff9f0a",cnt:GNODES.filter(n=>n.risk>=70&&n.risk<85).length,lbl:"High risk nodes"},
                          {color:"#ffd60a",cnt:GNODES.filter(n=>n.risk>=50&&n.risk<70).length,lbl:"Medium risk"},
                          {color:"#30d158",cnt:GNODES.filter(n=>n.risk<50).length,lbl:"Low risk"},
                        ].map(x=>(
                          <div key={x.lbl} style={{display:"flex",alignItems:"center",gap:7}}>
                            <div style={{width:7,height:7,borderRadius:"50%",background:x.color}}/>
                            <Mono color="#2a4060" size={8}>{x.cnt} {x.lbl}</Mono>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </Card>
                {selNode&&(
                  <div style={{animation:"fadeUp .2s ease"}}>
                    <Card style={{padding:18}} border={`${riskColor(selNode.risk)}44`}>
                      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:14}}>
                        <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:17,fontWeight:700,
                          color:riskColor(selNode.risk)}}>{selNode.label}</div>
                        <button onClick={()=>setSelNode(null)}
                          style={{background:"transparent",border:"none",color:"#2a4060",fontSize:20,cursor:"pointer"}}>×</button>
                      </div>
                      <div style={{display:"flex",justifyContent:"center",marginBottom:14}}>
                        <ScoreRing score={selNode.risk} size={72}/>
                      </div>
                      {[["Node Type",selNode.type.toUpperCase()],
                        ["Risk Score",selNode.risk+"/100"],
                        ["Connections",GEDGES.filter(([a,b])=>a===selNode.id||b===selNode.id).length+" edges"],
                        ["GCN Hops",rnd(2,5)+" propagation hops"],
                        ["Classification",selNode.risk>=85?"HIGH RISK":selNode.risk>=70?"ELEVATED":selNode.risk>=50?"MODERATE":"LOW RISK"],
                      ].map(([k,v])=>(
                        <div key={k} style={{display:"flex",justifyContent:"space-between",
                          padding:"6px 0",borderBottom:"1px solid #0a1628",fontSize:10}}>
                          <Mono color="#1a3348" size={8}>{k}</Mono>
                          <span style={{color:"#c0d4e8"}}>{v}</span>
                        </div>
                      ))}
                      <div style={{marginTop:12,padding:10,background:"#05080f",borderRadius:7,
                        border:"1px solid #0d1e2e",fontSize:10,color:"#3a6080",lineHeight:1.7}}>
                        GCN risk propagation: node flagged at depth {rnd(1,4)}. Connected to{" "}
                        <span style={{color:riskColor(selNode.risk)}}>
                          {GEDGES.filter(([a,b])=>a===selNode.id||b===selNode.id).length} entities
                        </span>{" "}in current cluster.
                      </div>
                      <button onClick={()=>{setSelAlert(mkAlert());setTab("alerts");}}
                        style={{width:"100%",marginTop:12,background:"#ff2d551a",border:"1px solid #ff2d5544",
                          borderRadius:6,color:"#ff2d55",padding:"8px",fontFamily:"'Share Tech Mono',monospace",
                          fontSize:8.5,cursor:"pointer",letterSpacing:.8}}>VIEW LINKED ALERTS →</button>
                    </Card>
                  </div>
                )}
              </div>
            )}

            {/* ════════ ML MODELS ════════ */}
            {tab==="models"&&(
              <div style={{display:"grid",gridTemplateColumns:selModel?"1fr 360px":"1fr",gap:14,animation:"fadeUp .3s ease"}}>
                <div style={{display:"grid",gap:10}}>
                  {MODELS.map(m=>(
                    <Card key={m.id} style={{padding:18,cursor:"pointer",transition:"all .2s",
                      borderColor:selModel?.id===m.id?m.color+"55":"#0d1e2e",
                      boxShadow:selModel?.id===m.id?`0 0 24px ${m.color}0f`:"none"}}
                      onClick={()=>setSelModel(s=>s?.id===m.id?null:m)}>
                      <div style={{display:"grid",gridTemplateColumns:"1fr auto",gap:14,alignItems:"start"}}>
                        <div>
                          <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:5}}>
                            <div style={{width:9,height:9,borderRadius:"50%",background:m.color}}/>
                            <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:16,fontWeight:700,color:"#d0e4f4"}}>{m.name}</div>
                            <Pill color={mStatusColor(m.status)} size={7}>{m.status}</Pill>
                            <Mono color="#1a3348" size={7.5}>{m.ver}</Mono>
                            <div style={{flex:1}}/>
                            <Mono color="#1a3348" size={8}>{m.lat}ms · {m.params}</Mono>
                          </div>
                          <div style={{display:"flex",gap:14,marginTop:4}}>
                            {[["ACC",m.acc,"#64d2ff"],["PREC",m.prec,"#30d158"],
                              ["REC",m.rec,"#5e5ce6"],["F1",m.f1,"#ff9f0a"],["FPR",m.fpr,"#ff2d55"]].map(([k,v,c])=>(
                              <div key={k} style={{textAlign:"center"}}>
                                <Mono color="#1a3348" size={7}>{k}</Mono>
                                <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:15,fontWeight:700,color:c,marginTop:1}}>{v}%</div>
                              </div>
                            ))}
                          </div>
                          {/* SHAP */}
                          <div style={{marginTop:10}}>
                            {m.features.map(f=>(
                              <div key={f.f} style={{display:"flex",alignItems:"center",gap:8,marginBottom:4}}>
                                <Mono color="#2a4060" size={8} style={{width:120,flexShrink:0}}>{f.f}</Mono>
                                <div style={{flex:1,height:2.5,background:"#0d1e2e",borderRadius:2,overflow:"hidden"}}>
                                  <div style={{height:"100%",width:`${f.v}%`,background:`linear-gradient(90deg,${m.color}55,${m.color})`,borderRadius:2}}/>
                                </div>
                                <Mono color={m.color} size={8}>{f.v}</Mono>
                              </div>
                            ))}
                          </div>
                        </div>
                        <div style={{display:"flex",flexDirection:"column",gap:8,alignItems:"flex-end"}}>
                          <RocCurve model={m} w={155} h={115}/>
                          <button onClick={e=>{e.stopPropagation();setTrainModel(m);}}
                            style={{background:m.color+"1a",border:`1px solid ${m.color}77`,borderRadius:6,
                              color:m.color,fontSize:8.5,fontFamily:"'Share Tech Mono',monospace",
                              padding:"6px 14px",cursor:"pointer",letterSpacing:.8,width:"100%",
                              transition:"background .15s"}}
                            onMouseEnter={e=>e.currentTarget.style.background=m.color+"33"}
                            onMouseLeave={e=>e.currentTarget.style.background=m.color+"1a"}>
                            ▶ RETRAIN
                          </button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>

                {/* Model detail panel */}
                {selModel&&(
                  <Card style={{padding:20,position:"sticky",top:0,alignSelf:"start",
                    animation:"fadeUp .2s ease"}} border={`${selModel.color}44`}
                    glow={true}>
                    <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:14}}>
                      <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:19,fontWeight:700,color:selModel.color}}>
                        {selModel.short}
                      </div>
                      <button onClick={()=>setSelModel(null)}
                        style={{background:"transparent",border:"none",color:"#2a4060",fontSize:22,cursor:"pointer",lineHeight:1}}>×</button>
                    </div>
                    <Label color="#1a3348">LOSS CURVES</Label>
                    <div style={{background:"#05080f",borderRadius:7,padding:"8px 10px",marginBottom:14,border:"1px solid #0d1e2e"}}>
                      <LossCurve id={selModel.id} w={290} h={75}/>
                    </div>
                    <Label color="#1a3348">CONFUSION MATRIX</Label>
                    <div style={{marginBottom:14}}>
                      <ConfMatrix model={selModel}/>
                    </div>
                    <Label color="#1a3348">ROC CURVE</Label>
                    <div style={{background:"#05080f",borderRadius:7,padding:"8px 10px",marginBottom:14,border:"1px solid #0d1e2e",display:"inline-block"}}>
                      <RocCurve model={selModel} w={290} h={140}/>
                    </div>
                    <Label color="#1a3348">FEATURE IMPORTANCE (SHAP)</Label>
                    {selModel.features.map(f=>(
                      <div key={f.f} style={{marginBottom:7}}>
                        <div style={{display:"flex",justifyContent:"space-between",marginBottom:2}}>
                          <Mono color="#3a6080" size={8.5}>{f.f}</Mono>
                          <Mono color={selModel.color} size={8.5}>{f.v}</Mono>
                        </div>
                        <div style={{height:3,background:"#0d1e2e",borderRadius:2,overflow:"hidden"}}>
                          <div style={{height:"100%",width:`${f.v}%`,background:`linear-gradient(90deg,${selModel.color}44,${selModel.color})`,borderRadius:2}}/>
                        </div>
                      </div>
                    ))}
                    <div style={{marginTop:14}}>
                      {[["Framework",selModel.fw],["Parameters",selModel.params],
                        ["Training Samples",selModel.samples.toLocaleString()],
                        ["Last Trained","2025-02-"+rnd(10,23)],
                        ["Inference",selModel.lat+"ms"]].map(([k,v])=>(
                        <div key={k} style={{display:"flex",justifyContent:"space-between",
                          padding:"5px 0",borderBottom:"1px solid #0a1628",fontSize:10}}>
                          <Mono color="#1a3348" size={8}>{k}</Mono>
                          <span style={{color:"#c0d4e8"}}>{v}</span>
                        </div>
                      ))}
                    </div>
                    <button onClick={()=>setTrainModel(selModel)}
                      style={{width:"100%",marginTop:14,background:selModel.color+"1a",
                        border:`1px solid ${selModel.color}`,borderRadius:7,color:selModel.color,
                        padding:"10px",fontFamily:"'Share Tech Mono',monospace",fontSize:9.5,
                        cursor:"pointer",letterSpacing:.8,transition:"background .15s"}}
                      onMouseEnter={e=>e.currentTarget.style.background=selModel.color+"33"}
                      onMouseLeave={e=>e.currentTarget.style.background=selModel.color+"1a"}>
                      ▶ LAUNCH TRAINING RUN
                    </button>
                  </Card>
                )}
              </div>
            )}

            {/* ════════ TRAINING ════════ */}
            {tab==="training"&&(
              <div style={{animation:"fadeUp .3s ease"}}>
                <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12,marginBottom:14}}>
                  {MODELS.map(m=>(
                    <Card key={m.id} style={{padding:16}}>
                      <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:12}}>
                        <div style={{width:8,height:8,borderRadius:"50%",background:m.color,
                          animation:m.status==="TRAINING"?"pulse .9s infinite":"none"}}/>
                        <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:13,fontWeight:700,color:"#d0e4f4"}}>{m.name}</div>
                        <div style={{flex:1}}/>
                        <Mono color={mStatusColor(m.status)} size={7}>{m.status}</Mono>
                      </div>
                      <div style={{background:"#05080f",borderRadius:7,padding:"8px 10px",
                        marginBottom:10,border:"1px solid #0a1628"}}>
                        <Label color="#1a3348" sz={7}>LOSS HISTORY</Label>
                        <LossCurve id={m.id} w={230} h={60}/>
                      </div>
                      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:6,marginBottom:10}}>
                        {[["Samples",m.samples.toLocaleString()],["Framework",m.fw.split(" ")[0]],
                          ["Version",m.ver],["F1",m.f1+"%"]].map(([k,v])=>(
                          <div key={k} style={{background:"#05080f",borderRadius:5,padding:"6px 8px",border:"1px solid #0a1628"}}>
                            <Label color="#1a3348" sz={7}>{k}</Label>
                            <Mono color="#8ab0c8" size={10}>{v}</Mono>
                          </div>
                        ))}
                      </div>
                      <MetRow label="F1" value={m.f1} color={m.color}/>
                      <button onClick={()=>setTrainModel(m)}
                        style={{width:"100%",marginTop:6,background:m.color+"14",
                          border:`1px solid ${m.color}55`,borderRadius:6,color:m.color,
                          padding:"8px",fontFamily:"'Share Tech Mono',monospace",fontSize:8.5,
                          cursor:"pointer",letterSpacing:.8,transition:"background .15s"}}
                        onMouseEnter={e=>e.currentTarget.style.background=m.color+"2a"}
                        onMouseLeave={e=>e.currentTarget.style.background=m.color+"14"}>
                        ▶ LAUNCH TRAINING
                      </button>
                    </Card>
                  ))}
                </div>
                {/* Pipeline */}
                <Card style={{padding:16}}>
                  <Label color="#1a4060">ML PIPELINE — 8 STAGES</Label>
                  <div style={{display:"flex",alignItems:"center",overflowX:"auto",gap:0,paddingBottom:4}}>
                    {["Raw TXNs","Feature Eng.","Train/Val Split","GNN Training","XGB Training","LSTM Training","Ensemble Stack","Deployment"].map((s,i,arr)=>(
                      <div key={s} style={{display:"flex",alignItems:"center",flexShrink:0}}>
                        <div style={{background:"#080f1a",border:"1px solid #1a3348",borderRadius:7,
                          padding:"9px 13px",textAlign:"center",minWidth:96}}>
                          <Mono color="#1a3348" size={7}>{String(i+1).padStart(2,"0")}</Mono>
                          <div style={{fontSize:9.5,color:"#8ab0c8",marginTop:3}}>{s}</div>
                        </div>
                        {i<arr.length-1&&(
                          <div style={{width:18,flexShrink:0,position:"relative",display:"flex",alignItems:"center",justifyContent:"center"}}>
                            <div style={{height:1,width:12,background:"#1a3348"}}/>
                            <div style={{color:"#1a3348",fontSize:9,position:"absolute",right:-1}}>▶</div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            )}

            {/* ════════ COMPARE ════════ */}
            {tab==="compare"&&(
              <div style={{animation:"fadeUp .3s ease"}}>
                <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:14,flexWrap:"wrap"}}>
                  <Mono color="#1a4060" size={9}>SELECT MODELS (max 3)</Mono>
                  {MODELS.map(m=>(
                    <button key={m.id}
                      onClick={()=>setCmpIds(p=>p.includes(m.id)?p.filter(x=>x!==m.id):[...p,m.id].slice(-3))}
                      style={{background:cmpIds.includes(m.id)?m.color+"1a":"transparent",
                        border:`1px solid ${cmpIds.includes(m.id)?m.color+"77":"#1a3348"}`,
                        borderRadius:5,color:cmpIds.includes(m.id)?m.color:"#2a4060",
                        fontSize:8.5,padding:"5px 12px",cursor:"pointer",
                        fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,transition:"all .15s"}}>
                      {m.short}
                    </button>
                  ))}
                </div>
                {cmpIds.length>0&&(
                  <div style={{display:"grid",gridTemplateColumns:`repeat(${cmpIds.length},1fr)`,gap:12}}>
                    {cmpIds.map(id=>{
                      const m=MODELS.find(x=>x.id===id);
                      return(
                        <Card key={id} style={{padding:18}} border={`${m.color}33`}>
                          <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:14}}>
                            <div style={{width:8,height:8,borderRadius:"50%",background:m.color}}/>
                            <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:14,fontWeight:700,color:"#d0e4f4"}}>{m.name}</div>
                          </div>
                          <MetRow label="ACCURACY" value={m.acc} color={m.color}/>
                          <MetRow label="PRECISION" value={m.prec} color={m.color}/>
                          <MetRow label="RECALL" value={m.rec} color={m.color}/>
                          <MetRow label="F1 SCORE" value={m.f1} color={m.color}/>
                          <MetRow label="FALSE POS RATE" value={m.fpr} max={30} color="#ff2d55"/>
                          <div style={{marginTop:12}}>
                            <Label color="#1a3348" sz={7}>ROC CURVE</Label>
                            <div style={{background:"#05080f",borderRadius:6,padding:"8px",border:"1px solid #0a1628",display:"inline-block"}}>
                              <RocCurve model={m} w={cmpIds.length===1?360:cmpIds.length===2?200:145} h={100}/>
                            </div>
                          </div>
                          <div style={{marginTop:10}}>
                            <Label color="#1a3348" sz={7}>CONFUSION MATRIX</Label>
                            <ConfMatrix model={m}/>
                          </div>
                          <div style={{marginTop:10}}>
                            <Label color="#1a3348" sz={7}>SHAP IMPORTANCE</Label>
                            {m.features.map(f=>(
                              <div key={f.f} style={{marginBottom:5}}>
                                <div style={{display:"flex",justifyContent:"space-between",marginBottom:2}}>
                                  <Mono color="#2a4060" size={8}>{f.f}</Mono>
                                  <Mono color={m.color} size={8}>{f.v}</Mono>
                                </div>
                                <Bar v={f.v} color={m.color} h={2.5}/>
                              </div>
                            ))}
                          </div>
                          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:6,marginTop:10}}>
                            {[["Latency",m.lat+"ms"],["Params",m.params],
                              ["Samples",m.samples.toLocaleString()],["Framework",m.fw.split(" ")[0]]].map(([k,v])=>(
                              <div key={k} style={{background:"#05080f",borderRadius:5,padding:"6px 8px",border:"1px solid #0a1628"}}>
                                <Label color="#1a3348" sz={7}>{k}</Label>
                                <Mono color="#8ab0c8" size={9.5}>{v}</Mono>
                              </div>
                            ))}
                          </div>
                          <button onClick={()=>setTrainModel(m)}
                            style={{width:"100%",marginTop:10,background:m.color+"14",
                              border:`1px solid ${m.color}55`,borderRadius:6,color:m.color,
                              padding:"7px",fontFamily:"'Share Tech Mono',monospace",fontSize:8,
                              cursor:"pointer",letterSpacing:.8}}>▶ RETRAIN</button>
                        </Card>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* ════════ ALERTS ════════ */}
            {tab==="alerts"&&(
              <div style={{display:"grid",gridTemplateColumns:selAlert?"1fr 350px":"1fr",gap:14,animation:"fadeUp .3s ease"}}>
                <div>
                  {/* Filters */}
                  <div style={{display:"flex",gap:8,marginBottom:12,flexWrap:"wrap",alignItems:"center"}}>
                    <div style={{position:"relative",flex:1,minWidth:180}}>
                      <input value={search} onChange={e=>setSearch(e.target.value)}
                        placeholder="Search ID, country, typology, network…"
                        style={{width:"100%",background:"#080f1a",border:"1px solid #1a3348",borderRadius:6,
                          color:"#c0d4e8",padding:"7px 12px 7px 28px",fontSize:9.5,
                          fontFamily:"'Share Tech Mono',monospace",outline:"none"}}/>
                      <div style={{position:"absolute",left:9,top:"50%",transform:"translateY(-50%)",
                        color:"#2a4060",fontSize:12}}>⌕</div>
                    </div>
                    <div style={{display:"flex",gap:4}}>
                      {["ALL","CRITICAL","HIGH","MEDIUM","LOW"].map(s=>(
                        <button key={s} onClick={()=>setFSev(s)}
                          style={{background:fSev===s?sevColor(s==="ALL"?"null":s)+"1a":"transparent",
                            border:`1px solid ${fSev===s?sevColor(s==="ALL"?"null":s)+"55":"#1a3348"}`,
                            borderRadius:5,color:fSev===s?(s==="ALL"?"#64d2ff":sevColor(s)):"#2a4060",
                            fontSize:7.5,padding:"5px 9px",cursor:"pointer",
                            fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8}}>
                          {s}
                        </button>
                      ))}
                    </div>
                    <div style={{display:"flex",gap:4,flexWrap:"wrap"}}>
                      {["ALL",...MODELS.map(m=>m.short)].map(m=>{
                        const mdl=MODELS.find(x=>x.short===m);
                        const c=mdl?.color||"#64d2ff";
                        return(
                          <button key={m} onClick={()=>setFMod(m)}
                            style={{background:fMod===m?c+"1a":"transparent",
                              border:`1px solid ${fMod===m?c+"55":"#1a3348"}`,
                              borderRadius:5,color:fMod===m?c:"#2a4060",
                              fontSize:7.5,padding:"5px 9px",cursor:"pointer",
                              fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8}}>
                            {m}
                          </button>
                        );
                      })}
                    </div>
                    <Mono color="#1a3348" size={8}>{filtered.length} results</Mono>
                  </div>
                  <AlertTable alerts={filtered} onSelect={setSelAlert} selId={selAlert?.id}/>
                </div>

                {/* Alert detail */}
                {selAlert&&(
                  <Card style={{padding:18,alignSelf:"start",position:"sticky",top:0,
                    animation:"fadeUp .2s ease"}} border="#1e3a52">
                    <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:12}}>
                      <div>
                        <Mono color="#64d2ff" size={13}>{selAlert.id}</Mono>
                        <div style={{fontSize:9,color:"#1a3348",marginTop:3}}>{new Date(selAlert.ts).toLocaleString()}</div>
                      </div>
                      <button onClick={()=>setSelAlert(null)}
                        style={{background:"transparent",border:"none",color:"#2a4060",fontSize:22,cursor:"pointer",lineHeight:1}}>×</button>
                    </div>
                    <div style={{display:"flex",gap:12,marginBottom:14,padding:12,
                      background:"#05080f",borderRadius:8,border:"1px solid #0a1628"}}>
                      <ScoreRing score={selAlert.score} size={56}/>
                      <div>
                        <Mono color="#1a3348" size={8}>RISK · <span style={{color:sevColor(selAlert.sev)}}>{selAlert.sev}</span></Mono>
                        <div style={{fontSize:11,color:selAlert.mColor,fontFamily:"'Share Tech Mono',monospace",margin:"4px 0 2px"}}>◈ {selAlert.model}</div>
                        <Mono color="#1a3348" size={8.5}>CONF {selAlert.conf}%</Mono>
                        <div style={{marginTop:4}}><Mono color={statusColor(selAlert.status)} size={8.5}>● {selAlert.status}</Mono></div>
                      </div>
                    </div>
                    {[["TYPOLOGY",selAlert.typology],["NETWORK",selAlert.network],
                      ["ORIGIN",selAlert.origin],["DESTINATION",selAlert.dest],
                      ["CHANNEL",selAlert.channel],
                      ["AMOUNT",`${fmt(selAlert.amount)} ${selAlert.currency}`],
                      ["ENTITIES",selAlert.entities+" linked"],
                      ["ACCOUNTS",selAlert.accounts+" flagged"]].map(([k,v])=>(
                      <div key={k} style={{display:"flex",justifyContent:"space-between",
                        padding:"5px 0",borderBottom:"1px solid #0a1628",fontSize:10}}>
                        <Mono color="#1a3348" size={8}>{k}</Mono>
                        <span style={{color:"#c0d4e8",textAlign:"right",maxWidth:200}}>{v}</span>
                      </div>
                    ))}
                    <div style={{marginTop:12,padding:10,background:"#05080f",borderRadius:7,border:"1px solid #1a3348"}}>
                      <Mono color="#1a4060" size={8}>◈ ML RATIONALE</Mono>
                      <div style={{fontSize:10,color:"#3a6080",lineHeight:1.7,marginTop:6}}>
                        {selAlert.model} flagged {selAlert.typology.toLowerCase()} pattern across {selAlert.accounts} accounts
                        in the {selAlert.origin}→{selAlert.dest} corridor. Confidence: {selAlert.conf}%.
                        {selAlert.entities} co-located entities matched. Ensemble confirmed at RISK {selAlert.score}.
                      </div>
                    </div>
                    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:7,marginTop:12}}>
                      {[["FREEZE","#5e5ce6"],["ESCALATE","#ff2d55"],["ASSIGN","#64d2ff"],["EXPORT","#30d158"]].map(([l,c])=>(
                        <button key={l}
                          style={{background:c+"14",border:`1px solid ${c}55`,borderRadius:6,
                            color:c,fontSize:8,padding:"8px",cursor:"pointer",
                            fontFamily:"'Share Tech Mono',monospace",letterSpacing:.8,transition:"all .15s"}}
                          onMouseEnter={e=>e.currentTarget.style.background=c+"2a"}
                          onMouseLeave={e=>e.currentTarget.style.background=c+"14"}>
                          {l}
                        </button>
                      ))}
                    </div>
                  </Card>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}


