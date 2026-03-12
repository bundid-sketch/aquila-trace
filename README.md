!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>AquilaTrace 3.1 — Secure Login</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
:root{
  --bg:#050c1a;--panel:#0a1628;--border:#1a2d4a;--sky:#38bdf8;--purple:#818cf8;
  --green:#34d399;--red:#ef4444;--orange:#fb923c;--yellow:#fbbf24;--text:#e2e8f0;--muted:#4b6080;--card:#0d1f38;
}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden;}

/* BACKGROUND GRID */
body::before{content:'';position:fixed;inset:0;background:
  linear-gradient(rgba(56,189,248,.03) 1px,transparent 1px),
  linear-gradient(90deg,rgba(56,189,248,.03) 1px,transparent 1px);
  background-size:40px 40px;pointer-events:none;z-index:0;}
body::after{content:'';position:fixed;inset:0;background:radial-gradient(ellipse at 50% 50%,rgba(14,165,233,.06) 0%,transparent 70%);pointer-events:none;z-index:0;}

/* SCAN LINES */
.scanline{position:fixed;top:0;left:0;width:100%;height:2px;background:linear-gradient(90deg,transparent,rgba(56,189,248,.4),transparent);animation:scan 4s linear infinite;z-index:1;pointer-events:none;}
@keyframes scan{0%{top:0;}100%{top:100vh;}}

.wrap{position:relative;z-index:10;width:100%;max-width:440px;padding:20px;}

/* LOGO AREA */
.logo-area{text-align:center;margin-bottom:28px;}
.logo-ring{width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,#0ea5e9,#6366f1);display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:22px;font-weight:900;box-shadow:0 0 30px rgba(14,165,233,.35);position:relative;}
.logo-ring::after{content:'';position:absolute;inset:-4px;border-radius:50%;border:1px solid rgba(56,189,248,.3);animation:ringPulse 2s ease-in-out infinite;}
@keyframes ringPulse{0%,100%{transform:scale(1);opacity:.6;}50%{transform:scale(1.08);opacity:1;}}
.logo-title{font-size:22px;font-weight:800;letter-spacing:3px;}
.logo-title .a{color:var(--sky);}.logo-title .b{color:#fff;}
.logo-sub{font-size:11px;color:var(--muted);margin-top:4px;letter-spacing:1px;}
.classif{display:inline-block;font-size:9px;font-weight:700;letter-spacing:2px;color:#f87171;background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);padding:2px 10px;border-radius:3px;margin-top:8px;}

/* CARD */
.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:28px;box-shadow:0 20px 60px rgba(0,0,0,.5);}
.step{display:none;}.step.active{display:block;}
.step-title{font-size:13px;font-weight:700;color:var(--sky);margin-bottom:4px;}
.step-sub{font-size:11px;color:var(--muted);margin-bottom:20px;line-height:1.5;}

/* PROGRESS */
.progress-bar{display:flex;gap:6px;margin-bottom:24px;}
.pb-step{flex:1;height:3px;border-radius:2px;background:var(--border);transition:.4s;}
.pb-step.done{background:var(--green);}
.pb-step.active{background:var(--sky);}

/* INPUTS */
.field{margin-bottom:14px;}
.field label{display:block;font-size:10px;font-weight:600;color:var(--muted);margin-bottom:5px;letter-spacing:.5px;text-transform:uppercase;}
.field input,.field select{width:100%;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 14px;color:var(--text);font-size:13px;outline:none;transition:.2s;}
.field input:focus,.field select:focus{border-color:var(--sky);box-shadow:0 0 0 2px rgba(56,189,248,.1);}
.field input.err{border-color:var(--red);}
.field input.ok{border-color:var(--green);}
.field .hint{font-size:10px;color:var(--muted);margin-top:4px;}
.field .err-msg{font-size:10px;color:#f87171;margin-top:4px;display:none;}
.field .err-msg.show{display:block;}

/* PASSWORD STRENGTH */
.pw-strength{height:3px;border-radius:2px;margin-top:6px;background:var(--border);transition:.4s;}
.pw-strength-fill{height:3px;border-radius:2px;transition:.4s;}
.pw-label{font-size:10px;margin-top:3px;}

/* OTP BOX */
.otp-grid{display:flex;gap:8px;justify-content:center;margin:16px 0;}
.otp-grid input{width:44px;height:52px;text-align:center;font-size:20px;font-weight:700;background:var(--panel);border:1px solid var(--border);border-radius:8px;color:var(--sky);outline:none;transition:.2s;}
.otp-grid input:focus{border-color:var(--sky);box-shadow:0 0 0 2px rgba(56,189,248,.15);}
.otp-grid input.filled{border-color:var(--green);}

/* BIOMETRIC */
.bio-ring{width:90px;height:90px;border-radius:50%;border:2px solid var(--border);display:flex;align-items:center;justify-content:center;margin:16px auto;font-size:36px;cursor:pointer;transition:.3s;position:relative;}
.bio-ring:hover{border-color:var(--sky);box-shadow:0 0 20px rgba(56,189,248,.2);}
.bio-ring.scanning{border-color:var(--sky);animation:bioScan 1.5s ease-in-out infinite;}
.bio-ring.success{border-color:var(--green);box-shadow:0 0 20px rgba(52,211,153,.3);}
.bio-ring.fail{border-color:var(--red);animation:shake .4s ease;}
@keyframes bioScan{0%,100%{box-shadow:0 0 0 0 rgba(56,189,248,.4);}50%{box-shadow:0 0 0 12px rgba(56,189,248,.0);}}
@keyframes shake{0%,100%{transform:translateX(0);}25%{transform:translateX(-6px);}75%{transform:translateX(6px);}}
.bio-progress{height:3px;background:var(--border);border-radius:2px;margin:8px 0;overflow:hidden;}
.bio-progress-fill{height:3px;background:linear-gradient(90deg,var(--sky),var(--purple));border-radius:2px;width:0%;transition:width .1s linear;}

/* DEVICE TRUST */
.device-card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:12px 14px;margin-bottom:8px;display:flex;align-items:center;gap:12px;cursor:pointer;transition:.2s;}
.device-card:hover{border-color:var(--sky);}
.device-card.selected{border-color:var(--green);background:rgba(52,211,153,.05);}
.device-icon{font-size:22px;flex-shrink:0;}
.device-info{flex:1;}
.device-name{font-size:12px;font-weight:600;}
.device-sub{font-size:10px;color:var(--muted);}
.device-check{width:18px;height:18px;border-radius:50%;border:1.5px solid var(--border);display:flex;align-items:center;justify-content:center;font-size:10px;flex-shrink:0;transition:.2s;}
.device-card.selected .device-check{background:var(--green);border-color:var(--green);}

/* BUTTONS */
.btn-primary{width:100%;padding:11px;border-radius:9px;font-size:13px;font-weight:700;cursor:pointer;border:none;background:linear-gradient(135deg,#0ea5e9,#6366f1);color:#fff;transition:.2s;letter-spacing:.3px;}
.btn-primary:hover{opacity:.9;transform:translateY(-1px);}
.btn-primary:disabled{opacity:.4;cursor:not-allowed;transform:none;}
.btn-ghost{width:100%;padding:9px;border-radius:9px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid var(--border);background:none;color:var(--muted);transition:.2s;margin-top:8px;}
.btn-ghost:hover{border-color:var(--sky);color:var(--sky);}

/* STATUS / ALERTS */
.status-bar{display:flex;align-items:center;gap:8px;padding:9px 12px;border-radius:8px;margin-bottom:14px;font-size:11px;}
.status-info{background:rgba(56,189,248,.08);border:1px solid rgba(56,189,248,.2);color:var(--sky);}
.status-warn{background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.2);color:var(--yellow);}
.status-err{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.25);color:#f87171;}
.status-ok{background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.2);color:var(--green);}

/* SECURITY BADGE */
.sec-badges{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-top:16px;}
.sec-badge{font-size:9px;padding:3px 8px;border-radius:10px;font-weight:600;background:rgba(56,189,248,.08);border:1px solid rgba(56,189,248,.15);color:var(--muted);}

/* AUDIT TICKER */
.audit-ticker{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:7px 12px;margin-top:14px;font-size:10px;color:var(--muted);font-family:monospace;overflow:hidden;white-space:nowrap;}
.audit-inner{display:inline-block;animation:ticker 18s linear infinite;}
@keyframes ticker{0%{transform:translateX(100%);}100%{transform:translateX(-100%);}}

/* ROLE BADGE */
.role-pill{display:inline-flex;align-items:center;gap:5px;font-size:10px;padding:3px 10px;border-radius:20px;font-weight:600;}

/* SUCCESS SCREEN */
.success-icon{font-size:48px;text-align:center;margin:10px 0;}
.access-granted{font-size:16px;font-weight:800;color:var(--green);text-align:center;letter-spacing:2px;margin-bottom:4px;}
.user-profile{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:14px;margin:14px 0;}
.up-row{display:flex;justify-content:space-between;font-size:11px;margin-bottom:6px;color:var(--muted);}
.up-row span:last-child{color:var(--text);font-weight:600;}

/* LOADING SPINNER */
.spinner{display:inline-block;width:16px;height:16px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin .7s linear infinite;vertical-align:middle;margin-right:6px;}
@keyframes spin{to{transform:rotate(360deg);}}

/* ATTEMPTS */
.attempts-left{font-size:10px;color:var(--orange);text-align:center;margin-top:6px;}
.countdown{font-size:11px;color:#f87171;text-align:center;margin-top:6px;font-weight:600;}

/* DIVIDER */
.divider{display:flex;align-items:center;gap:10px;margin:14px 0;color:var(--muted);font-size:10px;}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:var(--border);}
</style>
</head>
<body>
<div class="scanline"></div>

<div class="wrap">
  <!-- LOGO -->
  <div class="logo-area">
    <div class="logo-ring">AQ</div>
    <div class="logo-title"><span class="a">AQUILA</span><span class="b">TRACE</span></div>
    <div class="logo-sub">COUNTER-TERRORISM FINANCING PLATFORM · v3.1</div>
    <div class="classif">⬛ RESTRICTED ACCESS — AUTHORIZED PERSONNEL ONLY</div>
  </div>

  <!-- AUTH CARD -->
  <div class="card">
    <!-- Progress Steps -->
    <div class="progress-bar">
      <div class="pb-step active"  id="pb1"></div>
      <div class="pb-step"         id="pb2"></div>
      <div class="pb-step"         id="pb3"></div>
      <div class="pb-step"         id="pb4"></div>
      <div class="pb-step"         id="pb5"></div>
    </div>

    <!-- ── STEP 1: CREDENTIALS ── -->
    <div class="step active" id="step1">
      <div class="step-title">Step 1 of 5 — Identity Verification</div>
      <div class="step-sub">Enter your AquilaTrace operator credentials. All access attempts are logged and audited.</div>

      <div id="cred-status"></div>

      <div class="field">
        <label>Operator ID / Badge Number</label>
        <input type="text" id="username" placeholder="e.g. DCI-KE-0042 or OP-NAIROBI-7" autocomplete="off"/>
        <div class="hint">Format: AGENCY-COUNTRY-NUMBER</div>
        <div class="err-msg" id="username-err">Operator ID is required</div>
      </div>
      <div class="field">
        <label>Password</label>
        <input type="password" id="password" placeholder="Enter secure password" oninput="checkPwStrength(this.value)"/>
        <div class="pw-strength"><div class="pw-strength-fill" id="pwFill"></div></div>
        <div class="pw-label" id="pwLabel" style="color:var(--muted);font-size:10px;"></div>
        <div class="err-msg" id="password-err">Password must be at least 8 characters</div>
      </div>
      <div class="field">
        <label>Clearance Level</label>
        <select id="clearance">
          <option value="">— Select clearance level —</option>
          <option value="L1">Level 1 — Analyst (Read only)</option>
          <option value="L2">Level 2 — Investigator</option>
          <option value="L3">Level 3 — Senior Analyst</option>
          <option value="L4">Level 4 — Operations Commander</option>
          <option value="L5">Level 5 — Director / INTERPOL Liaison</option>
        </select>
        <div class="err-msg" id="clearance-err">Clearance level required</div>
      </div>
      <div id="lockout-msg" class="attempts-left" style="display:none;"></div>
      <button class="btn-primary" id="btn1" onclick="submitCredentials()">Verify Credentials →</button>
    </div>

    <!-- ── STEP 2: OTP ── -->
    <div class="step" id="step2">
      <div class="step-title">Step 2 of 5 — One-Time Passcode (OTP)</div>
      <div class="step-sub">A 6-digit OTP has been sent to your registered secure channel. Enter it below.<br><span style="color:var(--yellow)">Demo: use code <strong>847291</strong></span></div>

      <div id="otp-status"></div>
      <div class="otp-grid" id="otpGrid">
        <input type="text" maxlength="1" oninput="otpInput(this,0)" onkeydown="otpKey(event,0)"/>
        <input type="text" maxlength="1" oninput="otpInput(this,1)" onkeydown="otpKey(event,1)"/>
        <input type="text" maxlength="1" oninput="otpInput(this,2)" onkeydown="otpKey(event,2)"/>
        <input type="text" maxlength="1" oninput="otpInput(this,3)" onkeydown="otpKey(event,3)"/>
        <input type="text" maxlength="1" oninput="otpInput(this,4)" onkeydown="otpKey(event,4)"/>
        <input type="text" maxlength="1" oninput="otpInput(this,5)" onkeydown="otpKey(event,5)"/>
      </div>
      <div id="otp-timer" class="countdown"></div>
      <button class="btn-primary" id="btn2" onclick="submitOTP()" disabled>Verify OTP →</button>
      <button class="btn-ghost" onclick="resendOTP()">Resend OTP</button>
    </div>

    <!-- ── STEP 3: TOTP / AUTHENTICATOR ── -->
    <div class="step" id="step3">
      <div class="step-title">Step 3 of 5 — Authenticator App (TOTP)</div>
      <div class="step-sub">Enter the 6-digit code from your AquilaTrace Authenticator or Google Authenticator app.<br><span style="color:var(--yellow)">Demo: use code <strong>391047</strong></span></div>

      <div id="totp-status"></div>
      <div class="field" style="margin-top:14px;">
        <label>TOTP Code</label>
        <input type="text" id="totpInput" maxlength="6" placeholder="000000" style="font-size:20px;text-align:center;letter-spacing:8px;font-weight:700;" oninput="this.value=this.value.replace(/\D/g,'');if(this.value.length===6)submitTOTP()"/>
      </div>
      <div id="totp-timer" class="countdown"></div>
      <button class="btn-primary" id="btn3" onclick="submitTOTP()">Verify TOTP →</button>
    </div>

    <!-- ── STEP 4: BIOMETRIC ── -->
    <div class="step" id="step4">
      <div class="step-title">Step 4 of 5 — Biometric Verification</div>
      <div class="step-sub">Place your finger on the biometric scanner or use face recognition to proceed.</div>

      <div id="bio-status"></div>
      <div class="bio-ring" id="bioRing" onclick="startBiometric()">
        <span id="bioIcon">👆</span>
      </div>
      <div style="text-align:center;font-size:11px;color:var(--muted);margin-bottom:8px;" id="bioLabel">Tap to scan fingerprint / face</div>
      <div class="bio-progress"><div class="bio-progress-fill" id="bioFill"></div></div>
      <div style="text-align:center;font-size:10px;color:var(--muted);margin-top:4px;" id="bioPercent"></div>
      <button class="btn-primary" id="btn4" onclick="submitBiometric()" disabled style="margin-top:14px;">Confirm Biometric →</button>
      <button class="btn-ghost" onclick="skipBiometric()">Use backup PIN instead</button>

      <!-- BACKUP PIN -->
      <div id="backupPinWrap" style="display:none;margin-top:10px;">
        <div class="divider">Backup PIN</div>
        <div class="field">
          <label>6-Digit Backup PIN</label>
          <input type="password" id="backupPin" maxlength="6" placeholder="••••••" style="text-align:center;font-size:18px;letter-spacing:6px;"/>
          <div class="hint">Demo: use PIN <strong>112358</strong></div>
        </div>
        <button class="btn-primary" onclick="submitBackupPin()">Verify PIN →</button>
      </div>
    </div>

    <!-- ── STEP 5: DEVICE TRUST ── -->
    <div class="step" id="step5">
      <div class="step-title">Step 5 of 5 — Device & Session Trust</div>
      <div class="step-sub">Select this device's trust profile and confirm your active session context.</div>

      <div id="device-status"></div>

      <div style="font-size:10px;color:var(--muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px;">Recognized Devices</div>
      <div class="device-card selected" id="dev0" onclick="selectDevice(0)">
        <div class="device-icon">💻</div>
        <div class="device-info">
          <div class="device-name">This Device — Nairobi Ops Terminal</div>
          <div class="device-sub">Last used: Today 08:42 · Trusted · AES-256</div>
        </div>
        <div class="device-check">✓</div>
      </div>
      <div class="device-card" id="dev1" onclick="selectDevice(1)">
        <div class="device-icon">📱</div>
        <div class="device-info">
          <div class="device-name">Mobile — DCI Field Unit Phone</div>
          <div class="device-sub">Last used: Yesterday · Trusted</div>
        </div>
        <div class="device-check"></div>
      </div>
      <div class="device-card" id="dev2" onclick="selectDevice(2)">
        <div class="device-icon">🖥</div>
        <div class="device-info">
          <div class="device-name">INTERPOL NCB Terminal — Nairobi</div>
          <div class="device-sub">Last used: 3 days ago · Trusted</div>
        </div>
        <div class="device-check"></div>
      </div>

      <div class="field" style="margin-top:14px;">
        <label>Session Purpose (Audit Log)</label>
        <select id="sessionPurpose">
          <option value="">— Select session purpose —</option>
          <option>Routine monitoring</option>
          <option>Active investigation</option>
          <option>Joint operation — INTERPOL</option>
          <option>Joint operation — AFRIPOL</option>
          <option>Executive briefing</option>
          <option>System maintenance</option>
        </select>
      </div>
      <button class="btn-primary" id="btn5" onclick="submitDevice()">Establish Secure Session →</button>
    </div>

    <!-- ── SUCCESS ── -->
    <div class="step" id="stepSuccess">
      <div class="success-icon">🛡</div>
      <div class="access-granted">ACCESS GRANTED</div>
      <div style="text-align:center;font-size:11px;color:var(--muted);margin-bottom:14px;">All 5 authentication factors verified</div>

      <div class="user-profile">
        <div class="up-row"><span>Operator</span><span id="su-name">—</span></div>
        <div class="up-row"><span>Clearance</span><span id="su-clearance">—</span></div>
        <div class="up-row"><span>Device</span><span id="su-device">—</span></div>
        <div class="up-row"><span>Session ID</span><span id="su-session" style="font-family:monospace;font-size:10px;">—</span></div>
        <div class="up-row"><span>Session Purpose</span><span id="su-purpose">—</span></div>
        <div class="up-row"><span>Auth Time</span><span id="su-time">—</span></div>
        <div class="up-row" style="margin-bottom:0;"><span>Session Expires</span><span style="color:var(--yellow)" id="su-expires">—</span></div>
      </div>

      <div id="su-factor-list" style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px;"></div>

      <button class="btn-primary" onclick="launchPlatform()">
        🚀 Launch AquilaTrace Platform
      </button>
      <button class="btn-ghost" onclick="resetAuth()">← Sign in as different user</button>
    </div>

  </div><!-- /card -->

  <!-- SECURITY BADGES -->
  <div class="sec-badges">
    <span class="sec-badge">🔒 TLS 1.3</span>
    <span class="sec-badge">🛡 AES-256</span>
    <span class="sec-badge">🔑 FIDO2</span>
    <span class="sec-badge">📋 ISO 27001</span>
    <span class="sec-badge">🌐 INTERPOL SECURE</span>
    <span class="sec-badge">🇰🇪 CBK COMPLIANT</span>
  </div>

  <!-- AUDIT TICKER -->
  <div class="audit-ticker">
    <span class="audit-inner">
      [08:41:02] AUTH_OK — OP-NBI-044 · L4 · Nairobi Terminal &nbsp;·&nbsp;
      [08:38:17] AUTH_FAIL — Unknown badge · 3 attempts · IP locked &nbsp;·&nbsp;
      [08:35:55] SESSION_EXPIRED — OP-MSA-011 · timeout &nbsp;·&nbsp;
      [08:31:40] MFA_OTP_RESEND — OP-MDE-003 &nbsp;·&nbsp;
      [08:29:12] AUTH_OK — OP-LMU-007 · L2 · Mobile device &nbsp;·&nbsp;
      [08:22:08] BIOMETRIC_FAIL — OP-KSM-009 · backup PIN used &nbsp;·&nbsp;
      [08:18:44] SESSION_START — OP-NBI-039 · Joint Op INTERPOL &nbsp;·&nbsp;
    </span>
  </div>

</div><!-- /wrap -->

<script>
/* ══════════════════════════════════════════
   AQUILATRACE MFA ENGINE
   ══════════════════════════════════════════ */

// ── STATE ──
const AUTH = {
  step: 1,
  username: '', clearance: '', clearanceLabel: '',
  device: 0, purpose: '',
  otpAttempts: 0, totpAttempts: 0, credAttempts: 0,
  bioVerified: false,
  sessionId: '',
  factors: [],
  otpExpiry: 0, totpExpiry: 0,
  locked: false, lockUntil: 0,
};

// Demo credentials
const DEMO_USERS = {
  'DCI-KE-0042': { pw: 'Aquila@2024!', name: 'Insp. J. Kamau', role: 'DCI Kenya' },
  'OP-NAIROBI-7': { pw: 'Trace#Secure9', name: 'Analyst A. Wanjiku', role: 'AFRIPOL Liaison' },
  'INTERPOL-NCB-01': { pw: 'InterpolKE!23', name: 'Supt. H. Otieno', role: 'INTERPOL NCB' },
  'admin': { pw: 'admin', name: 'System Administrator', role: 'Platform Admin' },
};
const DEMO_OTP  = '847291';
const DEMO_TOTP = '391047';
const DEMO_PIN  = '112358';

const CLEARANCE_LABELS = {
  L1:'Level 1 — Analyst', L2:'Level 2 — Investigator',
  L3:'Level 3 — Senior Analyst', L4:'Level 4 — Operations Commander',
  L5:'Level 5 — Director'
};
const DEVICES = ['Nairobi Ops Terminal','DCI Field Unit Phone','INTERPOL NCB Terminal'];

// ── PROGRESS ──
function setProgress(step){
  for(let i=1;i<=5;i++){
    const el=document.getElementById('pb'+i);
    el.className='pb-step'+(i<step?' done':i===step?' active':'');
  }
}

// ── STATUS MESSAGES ──
function setStatus(containerId, type, msg){
  const el=document.getElementById(containerId);
  if(!el) return;
  el.innerHTML=msg?`<div class="status-bar status-${type}"><span>${msg}</span></div>`:'';
}

// ── PASSWORD STRENGTH ──
function checkPwStrength(pw){
  let score=0;
  if(pw.length>=8)  score++;
  if(pw.length>=12) score++;
  if(/[A-Z]/.test(pw)) score++;
  if(/[0-9]/.test(pw)) score++;
  if(/[^A-Za-z0-9]/.test(pw)) score++;
  const fill=document.getElementById('pwFill');
  const label=document.getElementById('pwLabel');
  const colors=['#ef4444','#fb923c','#fbbf24','#34d399','#38bdf8'];
  const labels=['Very Weak','Weak','Fair','Strong','Very Strong'];
  fill.style.width=(score/5*100)+'%';
  fill.style.background=colors[score-1]||'var(--border)';
  label.textContent=pw.length?labels[score-1]||'':'';
  label.style.color=colors[score-1]||'var(--muted)';
}

// ── STEP 1: CREDENTIALS ──
function submitCredentials(){
  if(AUTH.locked && Date.now()<AUTH.lockUntil){ showLockout(); return; }
  const u=document.getElementById('username').value.trim();
  const p=document.getElementById('password').value;
  const c=document.getElementById('clearance').value;
  let valid=true;

  document.getElementById('username-err').classList.remove('show');
  document.getElementById('password-err').classList.remove('show');
  document.getElementById('clearance-err').classList.remove('show');

  if(!u){ document.getElementById('username-err').classList.add('show'); valid=false; }
  if(p.length<4){ document.getElementById('password-err').classList.add('show'); valid=false; }
  if(!c){ document.getElementById('clearance-err').classList.add('show'); valid=false; }
  if(!valid) return;

  const btn=document.getElementById('btn1');
  btn.innerHTML='<span class="spinner"></span>Verifying...'; btn.disabled=true;

  setTimeout(()=>{
    // Accept demo credentials OR any non-empty credentials (for demo flexibility)
    const user=DEMO_USERS[u];
    const pwOk=user?user.pw===p:p.length>=4;

    if(pwOk){
      AUTH.username=u; AUTH.clearance=c; AUTH.clearanceLabel=CLEARANCE_LABELS[c];
      AUTH.credAttempts=0;
      AUTH.factors.push({label:'Credentials',icon:'🔑',ok:true});
      addAuditLog(`CRED_OK — ${u} · ${c}`);
      goStep(2);
      startOTPTimer();
    } else {
      AUTH.credAttempts++;
      const left=3-AUTH.credAttempts;
      if(AUTH.credAttempts>=3){
        AUTH.locked=true; AUTH.lockUntil=Date.now()+30000;
        setStatus('cred-status','err','🔒 Account temporarily locked. Try again in 30 seconds.');
        startLockCountdown();
      } else {
        setStatus('cred-status','err',`❌ Invalid credentials. ${left} attempt${left!==1?'s':''} remaining.`);
        document.getElementById('lockout-msg').style.display='block';
        document.getElementById('lockout-msg').textContent=`${left} attempt${left!==1?'s':''} remaining before lockout`;
      }
      addAuditLog(`CRED_FAIL — ${u} · attempt ${AUTH.credAttempts}`);
    }
    btn.innerHTML='Verify Credentials →'; btn.disabled=false;
  }, 1400);
}

// ── STEP 2: OTP ──
let otpTimerInterval=null;
function startOTPTimer(){
  AUTH.otpExpiry=Date.now()+120000; // 2 min
  clearInterval(otpTimerInterval);
  otpTimerInterval=setInterval(()=>{
    const left=Math.max(0,Math.ceil((AUTH.otpExpiry-Date.now())/1000));
    const el=document.getElementById('otp-timer');
    if(el) el.textContent=left>0?`OTP expires in ${left}s`:'OTP expired — please resend';
    if(left===0){ clearInterval(otpTimerInterval); setStatus('otp-status','warn','⚠ OTP has expired. Click Resend OTP.'); }
  },1000);
}

function otpInput(inp,idx){
  inp.value=inp.value.replace(/\D/g,'');
  if(inp.value) inp.classList.add('filled');
  else inp.classList.remove('filled');
  const inputs=document.querySelectorAll('#otpGrid input');
  if(inp.value && idx<5) inputs[idx+1].focus();
  const code=[...inputs].map(i=>i.value).join('');
  document.getElementById('btn2').disabled=code.length<6;
  if(code.length===6) submitOTP();
}
function otpKey(e,idx){
  if(e.key==='Backspace'){
    const inputs=document.querySelectorAll('#otpGrid input');
    if(!inputs[idx].value && idx>0){ inputs[idx-1].focus(); inputs[idx-1].value=''; inputs[idx-1].classList.remove('filled'); }
  }
}

function submitOTP(){
  const inputs=document.querySelectorAll('#otpGrid input');
  const code=[...inputs].map(i=>i.value).join('');
  if(code.length<6) return;
  if(Date.now()>AUTH.otpExpiry){ setStatus('otp-status','err','❌ OTP expired. Please resend.'); return; }

  const btn=document.getElementById('btn2');
  btn.innerHTML='<span class="spinner"></span>Verifying...'; btn.disabled=true;
  setTimeout(()=>{
    if(code===DEMO_OTP){
      clearInterval(otpTimerInterval);
      AUTH.factors.push({label:'OTP (SMS/Email)',icon:'📨',ok:true});
      addAuditLog(`OTP_OK — ${AUTH.username}`);
      goStep(3); startTOTPTimer();
    } else {
      AUTH.otpAttempts++;
      if(AUTH.otpAttempts>=3){
        setStatus('otp-status','err','🔒 Too many failed OTP attempts. Session terminated.');
        setTimeout(resetAuth,3000);
      } else {
        setStatus('otp-status','err',`❌ Incorrect OTP. ${3-AUTH.otpAttempts} attempt(s) left.`);
      }
      addAuditLog(`OTP_FAIL — ${AUTH.username} · attempt ${AUTH.otpAttempts}`);
      btn.innerHTML='Verify OTP →'; btn.disabled=false;
    }
  },900);
}

function resendOTP(){
  document.querySelectorAll('#otpGrid input').forEach(i=>{i.value='';i.classList.remove('filled');});
  document.getElementById('btn2').disabled=true;
  setStatus('otp-status','info','📨 New OTP sent to your registered secure channel.');
  startOTPTimer();
}

// ── STEP 3: TOTP ──
let totpTimerInterval=null;
function startTOTPTimer(){
  const cycle=30;
  clearInterval(totpTimerInterval);
  totpTimerInterval=setInterval(()=>{
    const s=cycle-(Math.floor(Date.now()/1000)%cycle);
    const el=document.getElementById('totp-timer');
    if(el) el.textContent=`Code refreshes in ${s}s`;
  },1000);
}

function submitTOTP(){
  const code=document.getElementById('totpInput').value.trim();
  if(code.length<6) return;
  const btn=document.getElementById('btn3');
  btn.innerHTML='<span class="spinner"></span>Verifying...'; btn.disabled=true;
  setTimeout(()=>{
    if(code===DEMO_TOTP){
      clearInterval(totpTimerInterval);
      AUTH.factors.push({label:'TOTP Authenticator',icon:'📱',ok:true});
      addAuditLog(`TOTP_OK — ${AUTH.username}`);
      goStep(4);
    } else {
      AUTH.totpAttempts++;
      if(AUTH.totpAttempts>=3){
        setStatus('totp-status','err','🔒 Too many failed TOTP attempts. Session terminated.');
        setTimeout(resetAuth,3000);
      } else {
        setStatus('totp-status','err',`❌ Incorrect TOTP. ${3-AUTH.totpAttempts} attempt(s) left.`);
      }
      addAuditLog(`TOTP_FAIL — ${AUTH.username}`);
      btn.innerHTML='Verify TOTP →'; btn.disabled=false;
    }
  },800);
}

// ── STEP 4: BIOMETRIC ──
let bioInterval=null, bioProgress=0;
function startBiometric(){
  const ring=document.getElementById('bioRing');
  const icon=document.getElementById('bioIcon');
  const fill=document.getElementById('bioFill');
  const label=document.getElementById('bioLabel');
  const pct=document.getElementById('bioPercent');
  if(ring.classList.contains('scanning')) return;
  ring.classList.add('scanning'); icon.textContent='🔍';
  label.textContent='Scanning... hold still';
  bioProgress=0; clearInterval(bioInterval);
  bioInterval=setInterval(()=>{
    bioProgress+=Math.random()*8+4;
    if(bioProgress>=100){ bioProgress=100; clearInterval(bioInterval);
      const success=Math.random()>.15; // 85% success rate
      if(success){
        ring.classList.remove('scanning'); ring.classList.add('success');
        icon.textContent='✅'; label.textContent='Biometric verified successfully';
        fill.style.width='100%'; pct.textContent='100% — Match confirmed';
        fill.style.background='var(--green)';
        AUTH.bioVerified=true;
        document.getElementById('btn4').disabled=false;
        setStatus('bio-status','ok','✅ Fingerprint/Face matched — 98.7% confidence');
        AUTH.factors.push({label:'Biometric',icon:'🧬',ok:true});
        addAuditLog(`BIO_OK — ${AUTH.username}`);
      } else {
        ring.classList.remove('scanning'); ring.classList.add('fail');
        icon.textContent='❌'; label.textContent='Biometric failed — try again';
        fill.style.background='var(--red)';
        setStatus('bio-status','err','❌ Biometric match failed. Try again or use backup PIN.');
        addAuditLog(`BIO_FAIL — ${AUTH.username}`);
        setTimeout(()=>{ ring.classList.remove('fail'); icon.textContent='👆'; label.textContent='Tap to scan fingerprint / face'; fill.style.width='0%'; pct.textContent=''; }, 2000);
      }
    }
    fill.style.width=Math.min(bioProgress,100)+'%';
    pct.textContent=Math.floor(Math.min(bioProgress,100))+'% — '+( bioProgress<50?'Acquiring...':bioProgress<80?'Processing...':'Matching...');
  },80);
}

function submitBiometric(){
  if(!AUTH.bioVerified){ setStatus('bio-status','warn','⚠ Please complete biometric scan first.'); return; }
  goStep(5);
}

function skipBiometric(){
  document.getElementById('backupPinWrap').style.display='block';
  document.getElementById('btn4').style.display='none';
  setStatus('bio-status','info','ℹ Enter your 6-digit backup PIN to proceed.');
}

function submitBackupPin(){
  const pin=document.getElementById('backupPin').value.trim();
  if(pin===DEMO_PIN){
    AUTH.factors.push({label:'Backup PIN',icon:'🔢',ok:true});
    addAuditLog(`BACKUP_PIN_OK — ${AUTH.username}`);
    goStep(5);
  } else {
    setStatus('bio-status','err','❌ Incorrect backup PIN.');
    addAuditLog(`BACKUP_PIN_FAIL — ${AUTH.username}`);
  }
}

// ── STEP 5: DEVICE TRUST ──
function selectDevice(idx){
  document.querySelectorAll('.device-card').forEach((d,i)=>{
    d.classList.toggle('selected',i===idx);
    d.querySelector('.device-check').textContent=i===idx?'✓':'';
  });
  AUTH.device=idx;
}

function submitDevice(){
  const purpose=document.getElementById('sessionPurpose').value;
  if(!purpose){ setStatus('device-status','warn','⚠ Please select a session purpose for the audit log.'); return; }
  AUTH.purpose=purpose;
  const btn=document.getElementById('btn5');
  btn.innerHTML='<span class="spinner"></span>Establishing secure session...'; btn.disabled=true;
  setTimeout(()=>{
    AUTH.factors.push({label:'Device Trust',icon:'💻',ok:true});
    AUTH.sessionId='SES-'+Math.random().toString(36).slice(2,8).toUpperCase()+'-'+Date.now().toString(36).toUpperCase();
    addAuditLog(`SESSION_START — ${AUTH.username} · ${AUTH.sessionId} · ${purpose}`);
    showSuccess();
  },1600);
}

// ── SUCCESS ──
function showSuccess(){
  const user=DEMO_USERS[AUTH.username]||{name:AUTH.username,role:'Operator'};
  document.getElementById('su-name').textContent=`${user.name} (${user.role})`;
  document.getElementById('su-clearance').textContent=AUTH.clearanceLabel;
  document.getElementById('su-device').textContent=DEVICES[AUTH.device];
  document.getElementById('su-session').textContent=AUTH.sessionId;
  document.getElementById('su-purpose').textContent=AUTH.purpose;
  document.getElementById('su-time').textContent=new Date().toLocaleTimeString();
  document.getElementById('su-expires').textContent=new Date(Date.now()+28800000).toLocaleTimeString()+' (8h)';
  document.getElementById('su-factor-list').innerHTML=AUTH.factors.map(f=>`
    <span style="display:inline-flex;align-items:center;gap:4px;font-size:10px;padding:3px 9px;border-radius:10px;background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.2);color:var(--green);">
      ${f.icon} ${f.label} ✓
    </span>`).join('');
  goStep('Success');
  setProgress(6);
}

function launchPlatform(){
  const btn=event.target;
  btn.innerHTML='<span class="spinner"></span>Loading AquilaTrace...'; btn.disabled=true;
  setTimeout(()=>{
    // In production this would redirect to the main platform
    // For demo: show a confirmation
    btn.innerHTML='✅ Platform Launched — See main AquilaTrace tab';
    btn.style.background='linear-gradient(135deg,#059669,#0d9488)';
  },2000);
}

// ── HELPERS ──
function goStep(n){
  document.querySelectorAll('.step').forEach(s=>s.classList.remove('active'));
  document.getElementById('step'+(typeof n==='number'?n:n)).classList.add('active');
  if(typeof n==='number'){ AUTH.step=n; setProgress(n); }
}

function resetAuth(){
  Object.assign(AUTH,{step:1,username:'',clearance:'',clearanceLabel:'',device:0,purpose:'',
    otpAttempts:0,totpAttempts:0,credAttempts:0,bioVerified:false,sessionId:'',factors:[],
    otpExpiry:0,totpExpiry:0,locked:false,lockUntil:0});
  clearInterval(otpTimerInterval); clearInterval(totpTimerInterval); clearInterval(bioInterval);
  document.getElementById('username').value='';
  document.getElementById('password').value='';
  document.getElementById('clearance').value='';
  document.getElementById('pwFill').style.width='0';
  document.getElementById('pwLabel').textContent='';
  document.querySelectorAll('#otpGrid input').forEach(i=>{i.value='';i.classList.remove('filled');});
  document.getElementById('totpInput').value='';
  document.getElementById('backupPin').value='';
  document.getElementById('backupPinWrap').style.display='none';
  document.getElementById('btn4').style.display='block';
  document.getElementById('bioRing').className='bio-ring';
  document.getElementById('bioIcon').textContent='👆';
  document.getElementById('bioFill').style.width='0';
  document.getElementById('bioLabel').textContent='Tap to scan fingerprint / face';
  document.getElementById('bioPercent').textContent='';
  document.getElementById('lockout-msg').style.display='none';
  ['cred-status','otp-status','totp-status','bio-status','device-status'].forEach(id=>{
    const el=document.getElementById(id); if(el) el.innerHTML='';
  });
  goStep(1); setProgress(1);
}

function startLockCountdown(){
  const btn=document.getElementById('btn1');
  const msg=document.getElementById('lockout-msg');
  msg.style.display='block';
  const interval=setInterval(()=>{
    const left=Math.max(0,Math.ceil((AUTH.lockUntil-Date.now())/1000));
    msg.textContent=left>0?`Locked — ${left}s remaining`:'Lockout lifted — try again';
    btn.innerHTML=left>0?`🔒 Locked (${left}s)`:'Verify Credentials →';
    btn.disabled=left>0;
    if(left===0){ clearInterval(interval); AUTH.locked=false; }
  },1000);
}

function showLockout(){
  const left=Math.ceil((AUTH.lockUntil-Date.now())/1000);
  setStatus('cred-status','err',`🔒 Account locked. Try again in ${left} seconds.`);
}

// Audit log (appended to ticker visually)
const auditLogs=[];
function addAuditLog(msg){
  const t=new Date().toTimeString().slice(0,8);
  auditLogs.unshift(`[${t}] ${msg}`);
  const ticker=document.querySelector('.audit-inner');
  if(ticker) ticker.textContent=auditLogs.slice(0,12).join(' · ') + ' · ';
}
</script>
</body>
</html>
