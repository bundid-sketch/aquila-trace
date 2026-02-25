import { useState } from "react";

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=DM+Sans:wght@300;400;500&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#060e14;font-family:'DM Sans',sans-serif;}
  ::-webkit-scrollbar{width:4px;height:4px;}
  ::-webkit-scrollbar-track{background:#0a1820;}
  ::-webkit-scrollbar-thumb{background:#1e3a4a;border-radius:2px;}
  @keyframes fadeSlide{from{opacity:0;transform:translateY(-6px);}to{opacity:1;transform:translateY(0);}}
  @keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.3;}}
  @keyframes flowRight{0%{stroke-dashoffset:20;}100%{stroke-dashoffset:0;}}
  @keyframes glow{0%,100%{opacity:0.4;}50%{opacity:1;}}
`;

// ── Data ──────────────────────────────────────────────────────────────────────

const TABS = ["Architecture","Model Rationale","Data Schema","Tech Stack","Team & Roles","Checklist"];

const ARCH_LAYERS = [
  {
    id:"ui", label:"PRESENTATION LAYER", color:"#64d2ff", y:0,
    components:["React Dashboard","Alert Feed","Network Graph Viz","Training Console","Comparison View"],
    desc:"Analyst-facing interface. Renders live alerts, model metrics, entity graphs and training state.",
  },
  {
    id:"api", label:"API LAYER", color:"#30d158", y:1,
    components:["REST API (FastAPI)","WebSocket Feed","Auth Middleware","Rate Limiter","Alert Router"],
    desc:"Stateless API gateway. Routes analyst actions to backend services and streams live events.",
  },
  {
    id:"ml", label:"ML PIPELINE LAYER", color:"#ff9f0a", y:2,
    components:["GNN Detector","XGBoost Scorer","LSTM Sequencer","Isolation Forest","FinBERT NLP","GCN Propagator","Ensemble Meta-Learner"],
    desc:"Six specialist models feeding a stacked ensemble. Each model scores independently; meta-learner produces final risk score.",
  },
  {
    id:"data", label:"DATA LAYER", color:"#bf5af2", y:3,
    components:["Transaction Store","Entity Graph DB","Feature Store","Model Registry","Alert Store","Audit Log"],
    desc:"Persistent storage for transactions, graph topology, engineered features, trained model artefacts and alert history.",
  },
  {
    id:"ingest", label:"INGESTION LAYER", color:"#ff6b6b", y:4,
    components:["Mobile Money Feed","Bank Wire Stream","Crypto Chain Monitor","Hawala Reports","Trade Finance Docs","Batch Importer"],
    desc:"Connects to raw financial data sources. Normalises heterogeneous formats into a unified transaction schema.",
  },
];

const ARCH_FLOWS = [
  {from:"ingest",to:"data",label:"normalised txns"},
  {from:"data",to:"ml",label:"feature vectors"},
  {from:"ml",to:"api",label:"risk scores"},
  {from:"api",to:"ui",label:"alerts + events"},
  {from:"ui",to:"api",label:"analyst actions"},
];

const MODEL_RATIONALE = [
  {
    id:"gnn", name:"Graph Neural Network", short:"GNN", color:"#64d2ff", framework:"PyTorch Geometric",
    why:"Financial crime rarely lives in a single transaction — it hides in the relationships between accounts, entities, and brokers. GNNs natively operate on graph-structured data, enabling multi-hop detection across entity clusters that rule-based systems and tabular models miss entirely.",
    alternatives:[{name:"Rule-based graph heuristics",reason:"Cannot generalise to novel network topologies or adapt to adversarial structuring."},{name:"Standard MLP on graph features",reason:"Loses structural context — treating degree centrality as a scalar discards the full neighbourhood signal."}],
    strengths:["Captures N-hop relationships","Learns structural patterns across different typologies","Propagates suspicion through connected subgraphs"],
    tradeoffs:["Higher inference latency (38ms)","Requires graph construction preprocessing","Needs substantial labelled graph data"],
  },
  {
    id:"xgb", name:"XGBoost Ensemble", short:"XGB", color:"#30d158", framework:"XGBoost 2.0",
    why:"Individual transaction features (velocity, amount delta, time-of-day, cross-border flags) are tabular by nature. XGBoost is the gold standard for tabular ML — fast, interpretable, robust to missing values, and highly competitive with deep learning on structured data.",
    alternatives:[{name:"Random Forest",reason:"Lower predictive accuracy and no built-in regularisation for imbalanced fraud datasets."},{name:"Logistic Regression",reason:"Insufficient to capture non-linear interactions between velocity, amount, and geography."}],
    strengths:["Sub-15ms inference — fastest deployed model","Highly interpretable via SHAP","Handles class imbalance well with scale_pos_weight"],
    tradeoffs:["Cannot model sequential behaviour","Blind to graph structure","Feature engineering-heavy"],
  },
  {
    id:"lstm", name:"Bidirectional LSTM", short:"LSTM", color:"#ff9f0a", framework:"TensorFlow 2.15",
    why:"Account behaviour is inherently sequential. Smurfing, dormancy breaks, and burst patterns only emerge when transactions are viewed as a time-ordered sequence. BiLSTM reads both forward and backward context across 90-day rolling windows, catching temporal anomalies invisible to stateless models.",
    alternatives:[{name:"1D CNN on sequences",reason:"Captures local patterns but misses long-range temporal dependencies critical for dormancy detection."},{name:"Transformer (BERT-style on sequences)",reason:"Significantly higher compute cost for marginal gain on sequences under 200 steps."}],
    strengths:["Detects dormancy breaks and burst cycles","Bidirectional context improves recall","90-day window captures slow-burn structuring"],
    tradeoffs:["61ms inference — slowest tabular model","Requires sequence padding/truncation","Sensitive to concept drift in behaviour patterns"],
  },
  {
    id:"iso", name:"Isolation Forest", short:"iForest", color:"#bf5af2", framework:"scikit-learn 1.4",
    why:"Labelled examples of novel terrorist financing schemes do not exist until they are discovered. Isolation Forest requires no labels — it isolates anomalies by their statistical rarity in feature space, acting as a zero-day detector for typologies the supervised models have never seen.",
    alternatives:[{name:"One-Class SVM",reason:"Scales poorly to millions of daily transactions and is sensitive to kernel choice."},{name:"Autoencoder anomaly detection",reason:"Higher complexity with marginal gain on low-dimensional tabular features; harder to explain to compliance teams."}],
    strengths:["Fully unsupervised — no labels required","Extremely fast (8ms inference)","Robust to high-dimensional sparse features"],
    tradeoffs:["Highest false positive rate (14.8%)","No semantic understanding of why a transaction is anomalous","Contamination parameter requires careful tuning"],
  },
  {
    id:"bert", name:"FinBERT NLP Engine", short:"BERT", color:"#ff6b6b", framework:"HuggingFace 4.38",
    why:"Memo lines, entity names, and narrative fields in wire transfers carry rich semantic signals that numeric models ignore. Fine-tuned on financial crime corpora, FinBERT classifies free-text fields for suspicious keywords, entity name patterns, and semantic similarity to known terrorist financing narratives.",
    alternatives:[{name:"TF-IDF + Logistic Regression",reason:"Bag-of-words loses semantic context — 'humanitarian relief' and 'relief funds for fighters' look similar to TF-IDF."},{name:"GPT-based classifier",reason:"10–100x inference cost with no meaningful accuracy improvement on short financial text fields."}],
    strengths:["Understands semantic context of financial language","NER identifies suspicious entity name patterns","Catches obfuscated language TF-IDF misses"],
    tradeoffs:["145ms inference — highest latency","110M parameters — largest model","Requires domain-specific fine-tuning data"],
  },
  {
    id:"gcn", name:"GCN Risk Propagator", short:"GCN", color:"#ffd60a", framework:"DGL + PyTorch",
    why:"Once a seed node is flagged as high-risk, that risk should flow to connected entities — just as investigators follow the money through a network. GCN propagates risk scores from confirmed high-risk nodes through graph convolutions, elevating the scores of previously-unseen accounts connected to known bad actors.",
    alternatives:[{name:"Manual analyst expansion",reason:"Cannot scale — an analyst expanding a network of 10,000 nodes is infeasible in real time."},{name:"Simple neighbour averaging",reason:"No learnable weights — treats all edge types and distances equally, missing directional risk flow."}],
    strengths:["Automatically surfaces unknown connected accounts","Learnable edge weights reflect transaction direction and size","Complements GNN detection with continuous risk propagation"],
    tradeoffs:["52ms inference","Still in TRAINING — v0.8.0-rc","Propagation depth tuning is non-trivial"],
  },
];

const SCHEMA = {
  Transaction:{
    color:"#64d2ff",
    fields:[
      {name:"txn_id",type:"UUID",pk:true,desc:"Unique transaction identifier"},
      {name:"timestamp",type:"DATETIME",desc:"UTC transaction timestamp"},
      {name:"origin_account_id",type:"UUID FK",desc:"Sending account reference"},
      {name:"destination_account_id",type:"UUID FK",desc:"Receiving account reference"},
      {name:"amount",type:"DECIMAL(18,4)",desc:"Transaction amount"},
      {name:"currency",type:"VARCHAR(3)",desc:"ISO 4217 currency code"},
      {name:"channel",type:"ENUM",desc:"Mobile Money | Bank Wire | Crypto | Hawala | Cash | Trade | Remittance"},
      {name:"origin_country",type:"VARCHAR(2)",desc:"ISO 3166-1 alpha-2 origin country"},
      {name:"dest_country",type:"VARCHAR(2)",desc:"ISO 3166-1 alpha-2 destination country"},
      {name:"memo",type:"TEXT",desc:"Free-text narrative / memo field"},
      {name:"is_cross_border",type:"BOOLEAN",desc:"Derived: origin ≠ destination country"},
      {name:"created_at",type:"DATETIME",desc:"Record ingestion timestamp"},
    ]
  },
  Account:{
    color:"#30d158",
    fields:[
      {name:"account_id",type:"UUID",pk:true,desc:"Unique account identifier"},
      {name:"entity_id",type:"UUID FK",desc:"Owning entity reference"},
      {name:"account_type",type:"ENUM",desc:"Personal | Business | NGO | Broker | Crypto"},
      {name:"country",type:"VARCHAR(2)",desc:"Account registration country"},
      {name:"opened_at",type:"DATE",desc:"Account opening date"},
      {name:"status",type:"ENUM",desc:"ACTIVE | FROZEN | CLOSED | MONITORED"},
      {name:"risk_score",type:"FLOAT",desc:"Current ensemble risk score (0–100)"},
      {name:"last_txn_at",type:"DATETIME",desc:"Timestamp of most recent transaction"},
      {name:"txn_count_30d",type:"INTEGER",desc:"Transaction count rolling 30 days"},
      {name:"total_volume_30d",type:"DECIMAL",desc:"Total transaction volume rolling 30 days"},
    ]
  },
  Entity:{
    color:"#ff9f0a",
    fields:[
      {name:"entity_id",type:"UUID",pk:true,desc:"Unique entity identifier"},
      {name:"entity_type",type:"ENUM",desc:"Individual | Company | NGO | Broker | State Actor"},
      {name:"name",type:"VARCHAR(255)",desc:"Registered entity name"},
      {name:"country",type:"VARCHAR(2)",desc:"Registration country"},
      {name:"risk_score",type:"FLOAT",desc:"GCN-propagated risk score"},
      {name:"network_affiliation",type:"VARCHAR(100)",desc:"Suspected network link if any"},
      {name:"sanctions_listed",type:"BOOLEAN",desc:"Appears on any sanctions list"},
      {name:"created_at",type:"DATETIME",desc:"Record creation timestamp"},
    ]
  },
  Alert:{
    color:"#bf5af2",
    fields:[
      {name:"alert_id",type:"VARCHAR(12)",pk:true,desc:"Human-readable alert ID e.g. AQT-XXXX"},
      {name:"txn_id",type:"UUID FK",desc:"Triggering transaction"},
      {name:"risk_score",type:"FLOAT",desc:"Ensemble risk score 0–100"},
      {name:"severity",type:"ENUM",desc:"CRITICAL | HIGH | MEDIUM | LOW"},
      {name:"typology",type:"VARCHAR(100)",desc:"Detected financing typology"},
      {name:"detected_by",type:"VARCHAR(20)",desc:"Primary detecting model shortname"},
      {name:"model_confidence",type:"FLOAT",desc:"Detecting model confidence 0–100"},
      {name:"status",type:"ENUM",desc:"OPEN | UNDER REVIEW | ESCALATED | FROZEN"},
      {name:"network",type:"VARCHAR(100)",desc:"Suspected threat network"},
      {name:"analyst_id",type:"UUID FK",desc:"Assigned analyst (nullable)"},
      {name:"created_at",type:"DATETIME",desc:"Alert generation timestamp"},
      {name:"resolved_at",type:"DATETIME",desc:"Resolution timestamp (nullable)"},
    ]
  },
  FeatureVector:{
    color:"#ff6b6b",
    fields:[
      {name:"fv_id",type:"UUID",pk:true,desc:"Feature vector record ID"},
      {name:"txn_id",type:"UUID FK",desc:"Source transaction"},
      {name:"txn_velocity_1h",type:"FLOAT",desc:"Transactions from account in last 1 hour"},
      {name:"txn_velocity_24h",type:"FLOAT",desc:"Transactions from account in last 24 hours"},
      {name:"amount_delta_pct",type:"FLOAT",desc:"% change from account rolling average"},
      {name:"hour_of_day",type:"INTEGER",desc:"Transaction hour (0–23)"},
      {name:"is_dormancy_break",type:"BOOLEAN",desc:"First txn after 30+ day inactivity"},
      {name:"sequence_entropy",type:"FLOAT",desc:"Shannon entropy of 90-day txn sequence"},
      {name:"degree_centrality",type:"FLOAT",desc:"Graph node degree centrality"},
      {name:"betweenness",type:"FLOAT",desc:"Graph betweenness centrality"},
      {name:"cluster_coeff",type:"FLOAT",desc:"Local clustering coefficient"},
      {name:"memo_risk_score",type:"FLOAT",desc:"FinBERT NLP risk score on memo text"},
      {name:"computed_at",type:"DATETIME",desc:"Feature computation timestamp"},
    ]
  },
};

const TECH_STACK = [
  {
    layer:"Frontend", color:"#64d2ff",
    items:[
      {name:"React 18",role:"UI framework",why:"Component model ideal for real-time dashboards"},
      {name:"D3.js",role:"Network graph visualisation",why:"Full SVG control for entity relationship graphs"},
      {name:"Recharts",role:"ML metric charts",why:"Declarative charting for ROC, loss, confusion matrix"},
      {name:"Tailwind CSS",role:"Styling",why:"Utility-first — rapid iteration during hackathon"},
      {name:"WebSocket (native)",role:"Live alert stream",why:"Sub-second alert delivery without polling"},
    ]
  },
  {
    layer:"API", color:"#30d158",
    items:[
      {name:"FastAPI",role:"REST + WebSocket API",why:"Async Python — handles concurrent analyst sessions and ML inference calls"},
      {name:"Pydantic v2",role:"Schema validation",why:"Auto-validates request/response shapes, generates OpenAPI docs"},
      {name:"JWT + OAuth2",role:"Authentication",why:"Stateless auth for analyst sessions"},
      {name:"Redis",role:"Alert queue + caching",why:"Sub-millisecond feature cache and pub/sub for live alert stream"},
    ]
  },
  {
    layer:"ML Pipeline", color:"#ff9f0a",
    items:[
      {name:"PyTorch Geometric",role:"GNN model",why:"State-of-the-art graph ML library with message-passing primitives"},
      {name:"DGL + PyTorch",role:"GCN Risk Propagator",why:"Efficient sparse graph convolutions at scale"},
      {name:"TensorFlow 2.15",role:"BiLSTM Sequence Model",why:"Mature seq2seq APIs and TFX for production deployment"},
      {name:"XGBoost 2.0",role:"Ensemble scorer",why:"Best-in-class tabular ML with native SHAP support"},
      {name:"scikit-learn 1.4",role:"Isolation Forest + preprocessing",why:"Production-stable unsupervised anomaly detection"},
      {name:"HuggingFace Transformers",role:"FinBERT NLP",why:"Pre-trained financial BERT with fine-tuning pipeline"},
      {name:"SHAP",role:"Model explainability",why:"Unified explainability across all model types"},
    ]
  },
  {
    layer:"Data", color:"#bf5af2",
    items:[
      {name:"PostgreSQL 16",role:"Transaction + alert store",why:"ACID-compliant relational store for financial records"},
      {name:"Neo4j",role:"Entity graph database",why:"Native graph DB for entity relationship queries"},
      {name:"Apache Parquet + S3",role:"Feature store",why:"Columnar format for fast ML training reads"},
      {name:"MLflow",role:"Model registry",why:"Tracks experiments, versions, and deployment artefacts"},
      {name:"Apache Kafka",role:"Transaction stream",why:"Durable event log for real-time ingestion pipeline"},
    ]
  },
  {
    layer:"Infrastructure", color:"#ff6b6b",
    items:[
      {name:"Docker + Compose",role:"Containerisation",why:"Reproducible local dev environment for entire stack"},
      {name:"GitHub Actions",role:"CI/CD",why:"Automated test, lint, and build pipeline"},
      {name:"Pytest",role:"Testing",why:"Unit and integration test coverage across pipeline"},
      {name:"Prometheus + Grafana",role:"Monitoring",why:"Model drift and inference latency tracking"},
    ]
  },
];

const TEAM_ROLES = [
  {role:"ML Engineer",color:"#ff9f0a",owner:"Team Member A",responsibilities:["GNN + GCN model development","Feature engineering pipeline","Ensemble stacking and evaluation","SHAP explainability integration"]},
  {role:"Backend Engineer",color:"#30d158",owner:"Team Member B",responsibilities:["FastAPI service development","Kafka ingestion pipeline","PostgreSQL + Neo4j schema","Redis caching and WebSocket feed"]},
  {role:"Frontend Engineer",color:"#64d2ff",owner:"Team Member C",responsibilities:["React dashboard implementation","D3 network graph visualisation","Training console UI","Alert management interface"]},
  {role:"Data Engineer",color:"#bf5af2",owner:"Team Member D",responsibilities:["Synthetic dataset generation","Feature store build","Train/val/test split strategy","Data quality validation"]},
  {role:"Product / Presenter",color:"#ff6b6b",owner:"Team Member E",responsibilities:["Pitch deck and demo script","Typology library documentation","SAR report templates","Hackathon submission packaging"]},
];

const CHECKLIST = [
  {section:"Architecture",color:"#64d2ff",items:[
    "System architecture diagram with all 5 layers and data flows",
    "Architecture reviewed and signed off by full team",
    "Diagram understandable in <2 min without verbal explanation",
    "All inter-layer interfaces (APIs, schemas) explicitly labelled",
  ]},
  {section:"Model Rationale",color:"#ff9f0a",items:[
    "Each of 6 models justified with at least 2 alternatives considered",
    "Accuracy/latency tradeoffs documented per model",
    "Model-to-typology mapping completed",
    "Ensemble strategy explained with expected accuracy target",
  ]},
  {section:"Data Schema",color:"#30d158",items:[
    "5 core entities defined: Transaction, Account, Entity, Alert, FeatureVector",
    "All foreign key relationships mapped",
    "Feature catalogue complete — every ML feature derivable from raw schema",
    "Zero ambiguous field names — all types and constraints specified",
  ]},
  {section:"Tech Stack",color:"#bf5af2",items:[
    "Full stack documented across 5 layers",
    "Alternatives considered and ruled out for key choices",
    "All dependencies version-pinned in requirements.txt",
    "Local dev environment boots in <10 minutes from README",
  ]},
  {section:"Repository",color:"#ff6b6b",items:[
    "Monorepo created with /frontend /backend /ml /data /docs structure",
    "CI/CD pipeline runs lint + tests on every PR",
    "README includes architecture diagram and quickstart guide",
    "Environment variables templated in .env.example",
    "Branch protection on main — no direct pushes",
  ]},
  {section:"Team",color:"#ffd60a",items:[
    "All 5 roles assigned with no gaps",
    "Sprint plan created — each milestone has a named owner",
    "Daily standup time agreed",
    "Definition of Done documented for each milestone",
  ]},
];

// ── Components ────────────────────────────────────────────────────────────────

function TabBar({tabs,active,onSelect}){
  return(
    <div style={{display:"flex",gap:4,marginBottom:20,flexWrap:"wrap"}}>
      {tabs.map(t=>(
        <button key={t} onClick={()=>onSelect(t)}
          style={{background:active===t?"#0a3d5c":"#080f17",border:`1px solid ${active===t?"#64d2ff66":"#0c1e2c"}`,
            borderRadius:6,color:active===t?"#64d2ff":"#3d6680",fontSize:9,padding:"6px 14px",
            cursor:"pointer",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,transition:"all 0.15s"}}>
          {t.toUpperCase()}
        </button>
      ))}
    </div>
  );
}

function SectionLabel({children,color="#64d2ff"}){
  return(
    <div style={{fontSize:8,fontFamily:"'Share Tech Mono',monospace",color,letterSpacing:2,marginBottom:10}}>
      {children}
    </div>
  );
}

function Tag({children,color}){
  return(
    <span style={{background:color+"18",border:`1px solid ${color}44`,borderRadius:4,
      color,fontSize:8,fontFamily:"'Share Tech Mono',monospace",padding:"2px 7px",letterSpacing:1}}>
      {children}
    </span>
  );
}

// ── Architecture View ──────────────────────────────────────────────────────────
function ArchitectureView(){
  const [sel,setSel]=useState(null);
  const selected=sel?ARCH_LAYERS.find(l=>l.id===sel):null;
  return(
    <div style={{display:"grid",gridTemplateColumns:"1fr 340px",gap:16,animation:"fadeSlide 0.2s ease"}}>
      <div>
        <SectionLabel>SYSTEM ARCHITECTURE — 5-LAYER MODEL</SectionLabel>
        <div style={{background:"#080f17",border:"1px solid #0c1e2c",borderRadius:10,padding:20}}>
          {/* Flow arrows between layers */}
          <svg width="100%" height={ARCH_LAYERS.length*96+40} style={{display:"block",marginBottom:-((ARCH_LAYERS.length*96+40))}}>
            {ARCH_LAYERS.slice(0,-1).map((_,i)=>(
              <g key={i}>
                <line x1="50%" y1={i*96+72} x2="50%" y2={i*96+88}
                  stroke="#1e3a4a" strokeWidth="1.5" strokeDasharray="4,3"
                  style={{animation:"glow 2s infinite"}}/>
                <polygon points={`calc(50% - 4),${i*96+86} calc(50% + 4),${i*96+86} 50%,${i*96+92}`}
                  fill="#1e3a4a"/>
              </g>
            ))}
          </svg>
          <div style={{display:"flex",flexDirection:"column",gap:8,position:"relative",zIndex:1}}>
            {ARCH_LAYERS.map(l=>(
              <div key={l.id} onClick={()=>setSel(s=>s===l.id?null:l.id)}
                style={{background:sel===l.id?l.color+"18":"#060e14",border:`1px solid ${sel===l.id?l.color+"66":"#0c1e2c"}`,
                  borderRadius:8,padding:"12px 16px",cursor:"pointer",transition:"all 0.2s",
                  borderLeft:`3px solid ${l.color}`}}>
                <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:8}}>
                  <div style={{fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:l.color,letterSpacing:1.5,fontWeight:700}}>{l.label}</div>
                  <div style={{flex:1}}/>
                  <div style={{fontSize:8,color:"#2d5068",fontFamily:"'Share Tech Mono',monospace"}}>↓ click to inspect</div>
                </div>
                <div style={{display:"flex",gap:6,flexWrap:"wrap"}}>
                  {l.components.map(c=>(
                    <Tag key={c} color={l.color}>{c}</Tag>
                  ))}
                </div>
              </div>
            ))}
          </div>
          {/* Data flow legend */}
          <div style={{marginTop:16,padding:"10px 14px",background:"#060e14",borderRadius:8,border:"1px solid #0c1e2c"}}>
            <div style={{fontSize:8,color:"#2d5068",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:8}}>DATA FLOWS</div>
            <div style={{display:"flex",gap:16,flexWrap:"wrap"}}>
              {ARCH_FLOWS.map(f=>(
                <div key={f.label} style={{display:"flex",alignItems:"center",gap:6,fontSize:9,color:"#4a7090"}}>
                  <span style={{fontFamily:"'Share Tech Mono',monospace",color:ARCH_LAYERS.find(l=>l.id===f.from)?.color,fontSize:8}}>{f.from.toUpperCase()}</span>
                  <span style={{color:"#1e3a4a"}}>──▶</span>
                  <span style={{fontFamily:"'Share Tech Mono',monospace",color:ARCH_LAYERS.find(l=>l.id===f.to)?.color,fontSize:8}}>{f.to.toUpperCase()}</span>
                  <span style={{color:"#2d5068",fontSize:8}}>({f.label})</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      {/* Detail panel */}
      <div>
        <SectionLabel>LAYER DETAIL</SectionLabel>
        {selected?(
          <div style={{background:"#080f17",border:`1px solid ${selected.color}44`,borderRadius:10,padding:20,animation:"fadeSlide 0.2s ease"}}>
            <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:20,fontWeight:700,color:selected.color,marginBottom:8}}>{selected.label}</div>
            <div style={{fontSize:11,color:"#5a8090",lineHeight:1.7,marginBottom:16}}>{selected.desc}</div>
            <SectionLabel color={selected.color}>COMPONENTS</SectionLabel>
            <div style={{display:"flex",flexDirection:"column",gap:6}}>
              {selected.components.map(c=>(
                <div key={c} style={{display:"flex",alignItems:"center",gap:8,padding:"7px 10px",background:"#060e14",borderRadius:6,border:"1px solid #0c1e2c"}}>
                  <div style={{width:5,height:5,borderRadius:"50%",background:selected.color,flexShrink:0}}/>
                  <div style={{fontSize:10,color:"#c8dae8"}}>{c}</div>
                </div>
              ))}
            </div>
          </div>
        ):(
          <div style={{background:"#080f17",border:"1px solid #0c1e2c",borderRadius:10,padding:20,color:"#2d5068",fontSize:10,fontFamily:"'Share Tech Mono',monospace",textAlign:"center",paddingTop:40}}>
            ← Click a layer to inspect its components
          </div>
        )}
      </div>
    </div>
  );
}

// ── Model Rationale View ───────────────────────────────────────────────────────
function ModelRationaleView(){
  const [sel,setSel]=useState(MODEL_RATIONALE[0]);
  return(
    <div style={{display:"grid",gridTemplateColumns:"220px 1fr",gap:16,animation:"fadeSlide 0.2s ease"}}>
      <div style={{display:"flex",flexDirection:"column",gap:6}}>
        <SectionLabel>SELECT MODEL</SectionLabel>
        {MODEL_RATIONALE.map(m=>(
          <div key={m.id} onClick={()=>setSel(m)}
            style={{background:sel.id===m.id?m.color+"18":"#080f17",border:`1px solid ${sel.id===m.id?m.color+"66":"#0c1e2c"}`,
              borderRadius:8,padding:"10px 14px",cursor:"pointer",transition:"all 0.15s"}}>
            <div style={{display:"flex",alignItems:"center",gap:8}}>
              <div style={{width:7,height:7,borderRadius:"50%",background:m.color,flexShrink:0}}/>
              <div style={{fontSize:11,fontFamily:"'Rajdhani',sans-serif",fontWeight:600,color:"#c8dae8"}}>{m.name}</div>
            </div>
            <div style={{fontSize:8,color:"#3d6680",fontFamily:"'Share Tech Mono',monospace",marginTop:4}}>{m.framework}</div>
          </div>
        ))}
      </div>
      <div style={{animation:"fadeSlide 0.2s ease"}}>
        <SectionLabel color={sel.color}>{sel.name.toUpperCase()} — SELECTION RATIONALE</SectionLabel>
        <div style={{display:"grid",gap:12}}>
          {/* Why */}
          <div style={{background:"#080f17",border:`1px solid ${sel.color}33`,borderRadius:10,padding:16}}>
            <div style={{fontSize:8,color:sel.color,fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:8}}>WHY THIS MODEL</div>
            <div style={{fontSize:11,color:"#7a9bb5",lineHeight:1.8}}>{sel.why}</div>
          </div>
          {/* Alternatives ruled out */}
          <div style={{background:"#080f17",border:"1px solid #0c1e2c",borderRadius:10,padding:16}}>
            <div style={{fontSize:8,color:"#ff2d55",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:10}}>ALTERNATIVES CONSIDERED & RULED OUT</div>
            {sel.alternatives.map(a=>(
              <div key={a.name} style={{marginBottom:10,padding:"10px 12px",background:"#060e14",borderRadius:8,border:"1px solid #1a0a0a"}}>
                <div style={{display:"flex",alignItems:"center",gap:6,marginBottom:4}}>
                  <span style={{color:"#ff2d55",fontSize:10}}>✕</span>
                  <span style={{fontSize:11,fontFamily:"'Rajdhani',sans-serif",fontWeight:600,color:"#c8dae8"}}>{a.name}</span>
                </div>
                <div style={{fontSize:10,color:"#5a6a70",lineHeight:1.6}}>{a.reason}</div>
              </div>
            ))}
          </div>
          {/* Strengths + Tradeoffs */}
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
            <div style={{background:"#080f17",border:`1px solid ${sel.color}33`,borderRadius:10,padding:14}}>
              <div style={{fontSize:8,color:"#30d158",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:8}}>STRENGTHS</div>
              {sel.strengths.map(s=>(
                <div key={s} style={{display:"flex",gap:7,marginBottom:7,fontSize:10,color:"#7a9bb5",alignItems:"flex-start"}}>
                  <span style={{color:"#30d158",flexShrink:0,marginTop:1}}>✓</span>{s}
                </div>
              ))}
            </div>
            <div style={{background:"#080f17",border:"1px solid #0c1e2c",borderRadius:10,padding:14}}>
              <div style={{fontSize:8,color:"#ff9f0a",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:8}}>TRADEOFFS</div>
              {sel.tradeoffs.map(t=>(
                <div key={t} style={{display:"flex",gap:7,marginBottom:7,fontSize:10,color:"#7a9bb5",alignItems:"flex-start"}}>
                  <span style={{color:"#ff9f0a",flexShrink:0,marginTop:1}}>⚠</span>{t}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Data Schema View ───────────────────────────────────────────────────────────
function DataSchemaView(){
  const [sel,setSel]=useState("Transaction");
  const entity=SCHEMA[sel];
  return(
    <div style={{display:"grid",gridTemplateColumns:"160px 1fr",gap:16,animation:"fadeSlide 0.2s ease"}}>
      <div style={{display:"flex",flexDirection:"column",gap:6}}>
        <SectionLabel>ENTITIES</SectionLabel>
        {Object.keys(SCHEMA).map(k=>(
          <div key={k} onClick={()=>setSel(k)}
            style={{background:sel===k?SCHEMA[k].color+"18":"#080f17",border:`1px solid ${sel===k?SCHEMA[k].color+"66":"#0c1e2c"}`,
              borderRadius:7,padding:"8px 12px",cursor:"pointer",transition:"all 0.15s"}}>
            <div style={{display:"flex",alignItems:"center",gap:7}}>
              <div style={{width:6,height:6,borderRadius:"50%",background:SCHEMA[k].color}}/>
              <div style={{fontSize:11,color:"#c8dae8",fontFamily:"'Rajdhani',sans-serif",fontWeight:600}}>{k}</div>
            </div>
            <div style={{fontSize:8,color:"#2d5068",fontFamily:"'Share Tech Mono',monospace",marginTop:3}}>{SCHEMA[k].fields.length} fields</div>
          </div>
        ))}
        {/* Relationships */}
        <div style={{background:"#080f17",border:"1px solid #0c1e2c",borderRadius:7,padding:"10px 12px",marginTop:6}}>
          <div style={{fontSize:7,color:"#2d5068",fontFamily:"'Share Tech Mono',monospace",letterSpacing:1,marginBottom:8}}>FK RELATIONSHIPS</div>
          {[["Account","→","Entity"],["Transaction","→","Account (×2)"],["Alert","→","Transaction"],["FeatureVector","→","Transaction"],["Alert","→","Account"]].map(([a,b,c])=>(
            <div key={a+c} style={{fontSize:8,fontFamily:"'Share Tech Mono',monospace",color:"#4a7090",marginBottom:4}}>
              <span style={{color:SCHEMA[a]?.color||"#64d2ff"}}>{a}</span>
              <span style={{color:"#1e3a4a"}}> {b} </span>
              <span style={{color:SCHEMA[c?.split(" ")[0]]?.color||"#64d2ff"}}>{c}</span>
            </div>
          ))}
        </div>
      </div>
      <div style={{animation:"fadeSlide 0.2s ease"}}>
        <SectionLabel color={entity.color}>{sel.toUpperCase()} SCHEMA</SectionLabel>
        <div style={{background:"#080f17",border:`1px solid ${entity.color}33`,borderRadius:10,overflow:"hidden"}}>
          <div style={{display:"grid",gridTemplateColumns:"160px 140px 1fr",padding:"8px 16px",background:"#060e14",borderBottom:"1px solid #0c1e2c",
            fontSize:8,fontFamily:"'Share Tech Mono',monospace",color:"#2d5068",letterSpacing:1}}>
            <div>FIELD</div><div>TYPE</div><div>DESCRIPTION</div>
          </div>
          {entity.fields.map((f,i)=>(
            <div key={f.name} style={{display:"grid",gridTemplateColumns:"160px 140px 1fr",padding:"9px 16px",
              borderBottom:"1px solid #0a1820",background:i%2===0?"#080f17":"#060e14",
              transition:"background 0.1s"}}
              onMouseEnter={e=>e.currentTarget.style.background="#0d1f2e"}
              onMouseLeave={e=>e.currentTarget.style.background=i%2===0?"#080f17":"#060e14"}>
              <div style={{fontFamily:"'Share Tech Mono',monospace",fontSize:9.5,color:f.pk?entity.color:"#c8dae8",display:"flex",alignItems:"center",gap:5}}>
                {f.pk&&<span style={{fontSize:7,color:entity.color}}>🔑</span>}
                {f.name}
              </div>
              <div style={{fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:f.type.includes("FK")?"#bf5af2":f.type.includes("ENUM")?"#ff9f0a":"#4a8aaa"}}>{f.type}</div>
              <div style={{fontSize:9.5,color:"#5a7090"}}>{f.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Tech Stack View ────────────────────────────────────────────────────────────
function TechStackView(){
  const [sel,setSel]=useState(null);
  return(
    <div style={{animation:"fadeSlide 0.2s ease"}}>
      <SectionLabel>TECHNOLOGY STACK — 5 LAYERS</SectionLabel>
      <div style={{display:"grid",gap:12}}>
        {TECH_STACK.map(layer=>(
          <div key={layer.layer} style={{background:"#080f17",border:"1px solid #0c1e2c",borderRadius:10,padding:16}}>
            <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:12}}>
              <div style={{width:8,height:8,borderRadius:"50%",background:layer.color}}/>
              <div style={{fontSize:10,fontFamily:"'Share Tech Mono',monospace",color:layer.color,letterSpacing:1}}>{layer.layer.toUpperCase()} LAYER</div>
            </div>
            <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(220px,1fr))",gap:8}}>
              {layer.items.map(item=>(
                <div key={item.name} onClick={()=>setSel(s=>s?.name===item.name?null:item)}
                  style={{background:sel?.name===item.name?layer.color+"18":"#060e14",border:`1px solid ${sel?.name===item.name?layer.color+"66":"#0c1e2c"}`,
                    borderRadius:8,padding:"10px 12px",cursor:"pointer",transition:"all 0.15s"}}>
                  <div style={{display:"flex",alignItems:"center",gap:7,marginBottom:4}}>
                    <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:13,fontWeight:700,color:layer.color}}>{item.name}</div>
                    <Tag color={layer.color}>{item.role}</Tag>
                  </div>
                  <div style={{fontSize:9.5,color:"#4a7090",lineHeight:1.5}}>{item.why}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Team View ──────────────────────────────────────────────────────────────────
function TeamView(){
  return(
    <div style={{animation:"fadeSlide 0.2s ease"}}>
      <SectionLabel>TEAM ROLES & RESPONSIBILITIES</SectionLabel>
      <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(260px,1fr))",gap:12,marginBottom:20}}>
        {TEAM_ROLES.map(r=>(
          <div key={r.role} style={{background:"#080f17",border:`1px solid ${r.color}44`,borderRadius:10,padding:18,borderTop:`2px solid ${r.color}`}}>
            <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:16,fontWeight:700,color:r.color,marginBottom:2}}>{r.role}</div>
            <div style={{fontSize:9,color:"#2d5068",fontFamily:"'Share Tech Mono',monospace",marginBottom:12}}>{r.owner}</div>
            {r.responsibilities.map(resp=>(
              <div key={resp} style={{display:"flex",gap:7,marginBottom:6,fontSize:10,color:"#7a9bb5",alignItems:"flex-start"}}>
                <span style={{color:r.color,flexShrink:0,fontSize:9,marginTop:1}}>▸</span>{resp}
              </div>
            ))}
          </div>
        ))}
      </div>
      {/* Sprint plan */}
      <div style={{background:"#080f17",border:"1px solid #0c1e2c",borderRadius:10,padding:20}}>
        <SectionLabel>SPRINT OVERVIEW — 15 DAYS</SectionLabel>
        <div style={{display:"flex",gap:0,overflowX:"auto"}}>
          {[
            {days:"1–2",label:"M1\nFoundation",color:"#64d2ff"},
            {days:"3–4",label:"M2\nData Pipeline",color:"#30d158"},
            {days:"5–7",label:"M3\nML Models",color:"#ff9f0a"},
            {days:"8",label:"M4\nEnsemble",color:"#bf5af2"},
            {days:"9–10",label:"M5\nDashboard",color:"#ff6b6b"},
            {days:"11",label:"M6\nAlerts",color:"#64d2ff"},
            {days:"12",label:"M7\nTypologies",color:"#30d158"},
            {days:"13",label:"M8\nReporting",color:"#ff9f0a"},
            {days:"14",label:"M9\nTesting",color:"#bf5af2"},
            {days:"15",label:"M10\nSubmission",color:"#ffd60a"},
          ].map((m,i,arr)=>(
            <div key={m.days} style={{display:"flex",alignItems:"center",flexShrink:0}}>
              <div style={{background:i===0?m.color+"22":"#060e14",border:`1px solid ${i===0?m.color:"#1e3a4a"}`,borderRadius:8,padding:"10px 14px",textAlign:"center",minWidth:90}}>
                <div style={{fontSize:8,color:m.color,fontFamily:"'Share Tech Mono',monospace",marginBottom:4}}>DAY {m.days}</div>
                <div style={{fontSize:10,color:"#c8dae8",whiteSpace:"pre-line",lineHeight:1.4}}>{m.label}</div>
              </div>
              {i<arr.length-1&&<div style={{width:16,height:1,background:"#1e3a4a",flexShrink:0}}><div style={{color:"#1e3a4a",fontSize:9,marginLeft:8,marginTop:-6}}>▶</div></div>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Checklist View ─────────────────────────────────────────────────────────────
function ChecklistView(){
  const total=CHECKLIST.reduce((s,c)=>s+c.items.length,0);
  const [checked,setChecked]=useState({});
  const done=Object.values(checked).filter(Boolean).length;
  const pct=Math.round((done/total)*100);
  const toggle=(sec,i)=>setChecked(p=>({...p,[sec+i]:!p[sec+i]}));
  return(
    <div style={{animation:"fadeSlide 0.2s ease"}}>
      <div style={{display:"flex",alignItems:"center",gap:14,marginBottom:16}}>
        <SectionLabel>MILESTONE 1 COMPLETION CHECKLIST</SectionLabel>
        <div style={{flex:1}}/>
        <div style={{fontSize:11,fontFamily:"'Rajdhani',sans-serif",fontWeight:700,color:pct===100?"#30d158":"#64d2ff"}}>{done}/{total} DONE</div>
        <div style={{width:120,height:6,background:"#0f2030",borderRadius:3,overflow:"hidden"}}>
          <div style={{height:"100%",width:`${pct}%`,background:pct===100?"#30d158":"#64d2ff",borderRadius:3,transition:"width 0.4s"}}/>
        </div>
        <div style={{fontSize:10,color:pct===100?"#30d158":"#3d6680",fontFamily:"'Share Tech Mono',monospace"}}>{pct}%</div>
      </div>
      <div style={{display:"grid",gap:12}}>
        {CHECKLIST.map(sec=>{
          const secDone=sec.items.filter((_,i)=>checked[sec.section+i]).length;
          return(
            <div key={sec.section} style={{background:"#080f17",border:`1px solid ${sec.color}33`,borderRadius:10,padding:16}}>
              <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:12}}>
                <div style={{fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:sec.color,letterSpacing:1}}>{sec.section.toUpperCase()}</div>
                <div style={{flex:1}}/>
                <div style={{fontSize:9,color:secDone===sec.items.length?"#30d158":"#2d5068",fontFamily:"'Share Tech Mono',monospace"}}>{secDone}/{sec.items.length}</div>
                <div style={{width:60,height:3,background:"#0f2030",borderRadius:2,overflow:"hidden"}}>
                  <div style={{height:"100%",width:`${(secDone/sec.items.length)*100}%`,background:sec.color,borderRadius:2,transition:"width 0.3s"}}/>
                </div>
              </div>
              {sec.items.map((item,i)=>{
                const isChecked=!!checked[sec.section+i];
                return(
                  <div key={i} onClick={()=>toggle(sec.section,i)}
                    style={{display:"flex",alignItems:"flex-start",gap:10,padding:"8px 10px",marginBottom:4,
                      background:isChecked?sec.color+"11":"#060e14",border:`1px solid ${isChecked?sec.color+"44":"#0c1e2c"}`,
                      borderRadius:6,cursor:"pointer",transition:"all 0.15s"}}>
                    <div style={{width:14,height:14,borderRadius:3,border:`1.5px solid ${isChecked?sec.color:"#2d5068"}`,
                      background:isChecked?sec.color:"transparent",flexShrink:0,marginTop:1,
                      display:"flex",alignItems:"center",justifyContent:"center",transition:"all 0.15s"}}>
                      {isChecked&&<span style={{color:"#060e14",fontSize:9,fontWeight:700,lineHeight:1}}>✓</span>}
                    </div>
                    <div style={{fontSize:10,color:isChecked?"#7a9bb5":"#c8dae8",textDecoration:isChecked?"line-through":"none",lineHeight:1.5,transition:"all 0.15s"}}>
                      {item}
                    </div>
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
      {done===total&&(
        <div style={{marginTop:16,padding:16,background:"#0a2a0a",border:"1px solid #30d158",borderRadius:10,textAlign:"center",animation:"fadeSlide 0.3s ease"}}>
          <div style={{fontFamily:"'Rajdhani',sans-serif",fontSize:18,fontWeight:700,color:"#30d158"}}>✓ MILESTONE 1 COMPLETE</div>
          <div style={{fontSize:10,color:"#4a8a4a",marginTop:4,fontFamily:"'Share Tech Mono',monospace"}}>Ready to proceed to Milestone 2 — Data Pipeline & Feature Engineering</div>
        </div>
      )}
    </div>
  );
}

// ── App ────────────────────────────────────────────────────────────────────────
export default function Milestone1(){
  const [tab,setTab]=useState("Architecture");
  return(
    <>
      <style>{CSS}</style>
      <div style={{minHeight:"100vh",background:"#060e14",color:"#c8dae8",fontFamily:"'DM Sans',sans-serif",padding:20}}>
        {/* Header */}
        <div style={{marginBottom:20,paddingBottom:16,borderBottom:"1px solid #0c1e2c"}}>
          <div style={{display:"flex",alignItems:"center",gap:12}}>
            <div style={{fontSize:22,fontFamily:"'Rajdhani',sans-serif",fontWeight:700,color:"#64d2ff",letterSpacing:3}}>🦅 AQUILA TRACE</div>
            <div style={{background:"#64d2ff22",border:"1px solid #64d2ff44",borderRadius:5,padding:"2px 10px",fontSize:8,fontFamily:"'Share Tech Mono',monospace",color:"#64d2ff",letterSpacing:1}}>MILESTONE 1</div>
            <div style={{fontSize:9,fontFamily:"'Share Tech Mono',monospace",color:"#2d5068"}}>PROJECT FOUNDATION & ARCHITECTURE DESIGN</div>
            <div style={{flex:1}}/>
            <div style={{fontSize:8,fontFamily:"'Share Tech Mono',monospace",color:"#1e4060"}}>NIRU HACKATHON · DAYS 1–2</div>
          </div>
        </div>
        <TabBar tabs={TABS} active={tab} onSelect={setTab}/>
        {tab==="Architecture"&&<ArchitectureView/>}
        {tab==="Model Rationale"&&<ModelRationaleView/>}
        {tab==="Data Schema"&&<DataSchemaView/>}
        {tab==="Tech Stack"&&<TechStackView/>}
        {tab==="Team & Roles"&&<TeamView/>}
        {tab==="Checklist"&&<ChecklistView/>}
      </div>
    </>
  );
}




