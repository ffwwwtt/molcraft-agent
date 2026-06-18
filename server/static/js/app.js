
"use strict";

// ── GSAP ScrollTrigger registration ──
if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

// ═══════════════════════════════════════════
//  SVG Icons — 24x24, stroke="currentColor", stroke-width="1.5"
// ═══════════════════════════════════════════
var ICONS = {
  chat:     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>',
  chatActive:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/><circle cx="9" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="15" cy="12" r="1" fill="currentColor" stroke="none"/></svg>',
  more:     '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/></svg>',
  edit:     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.8 2.8 0 113.9 4L9 19l-4 1 1-4z"/></svg>',
  refresh:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 4v6h6M23 20v-6h-6"/><path d="M20.5 9A9 9 0 005.6 16M3.5 15A9 9 0 0018.4 8"/></svg>',
  trash:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6M10 11v6M14 11v6"/></svg>',
  clipboard:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><path d="M9 14h6M9 18h6"/></svg>',
  chart:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>',
  folder:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2v11z"/></svg>',
  gear:     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 00.3 1.8l.1.1a2 2 0 01-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.8-.3 1.7 1.7 0 00-1 1.6v.3a2 2 0 01-4 0v-.3a1.7 1.7 0 00-1.3-1.6 1.7 1.7 0 00-1.8.3l-.1.1a2 2 0 01-2.8-2.8l.1-.1a1.7 1.7 0 00.3-1.8 1.7 1.7 0 00-1.6-1H3a2 2 0 010-4h.3a1.7 1.7 0 001.6-1.3 1.7 1.7 0 00-.3-1.8l-.1-.1a2 2 0 012.8-2.8l.1.1a1.7 1.7 0 001.8.3 1.7 1.7 0 001-1v-.3a2 2 0 014 0v.3a1.7 1.7 0 001 1.6 1.7 1.7 0 001.8-.3l.1-.1a2 2 0 012.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.8 1.7 1.7 0 001.6 1H21a2 2 0 010 4h-.3a1.7 1.7 0 00-1.3.9z"/></svg>',
  download: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>',
  upload:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>',
  save:     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><path d="M17 21v-8H7v8M7 3v5h8"/></svg>',
  plug:     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7 2v5M17 2v5M7 7h10a3 3 0 013 3v3a3 3 0 01-3 3h-1v4H8v-4H7a3 3 0 01-3-3v-3a3 3 0 013-3z"/><path d="M10 14h4"/></svg>',
  dollar:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>',
  palette:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 010 20"/><circle cx="8.5" cy="9" r="1.5" fill="currentColor" stroke="none"/><circle cx="15.5" cy="14" r="1.5" fill="currentColor" stroke="none"/><circle cx="16.5" cy="8" r="1" fill="currentColor" stroke="none"/></svg>',
  bot:      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="8" width="18" height="13" rx="2"/><path d="M9 3h6M12 3v5"/><circle cx="9" cy="14" r="1.2" fill="currentColor" stroke="none"/><circle cx="15" cy="14" r="1.2" fill="currentColor" stroke="none"/></svg>',
  check:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
  xmark:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18M6 6l12 12"/></svg>',
  flask:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6M10 3v6l-5 11a2 2 0 001.7 3h10.6a2 2 0 001.7-3L14 9V3"/></svg>',
  file:     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>',
  code:     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 18l6-6-6-6M8 6l-6 6 6 6"/></svg>',
  image:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" stroke="none"/><path d="M21 15l-5-5L5 21"/></svg>',
  stop:     '<svg viewBox="0 0 20 20" fill="currentColor"><rect x="4" y="4" width="12" height="12" rx="1"/></svg>',
  spinner:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" opacity="0.25"/><path d="M12 2a10 10 0 019.9 9" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/></path></svg>',
  logo:     '<svg viewBox="0 0 48 48" fill="none"><polygon points="24,4 41.3,14 41.3,34 24,44 6.7,34 6.7,14" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/><line x1="24" y1="4" x2="41.3" y2="34" stroke="currentColor" stroke-width="1" stroke-linecap="round" opacity="0.5"/><line x1="24" y1="4" x2="6.7" y2="34" stroke="currentColor" stroke-width="1" stroke-linecap="round" opacity="0.5"/><line x1="6.7" y1="14" x2="41.3" y2="14" stroke="currentColor" stroke-width="1" stroke-linecap="round" opacity="0.5"/><circle cx="24" cy="24" r="3" fill="currentColor"/><circle cx="24" cy="10" r="1.3" fill="currentColor" opacity="0.7"/><circle cx="38" cy="18" r="1.3" fill="currentColor" opacity="0.7"/><circle cx="38" cy="30" r="1.3" fill="currentColor" opacity="0.7"/><circle cx="24" cy="38" r="1.3" fill="currentColor" opacity="0.7"/><circle cx="10" cy="30" r="1.3" fill="currentColor" opacity="0.7"/><circle cx="10" cy="18" r="1.3" fill="currentColor" opacity="0.7"/></svg>',
  plus:     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
  pdf:      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h4"/></svg>',
  spreadsheet:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/></svg>',
  doc:      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8M8 17h5"/></svg>',
  audio:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
  archive:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8v13a2 2 0 01-2 2H5a2 2 0 01-2-2V8"/><path d="M1 3a2 2 0 012-2h18a2 2 0 012 2v4H1V3z"/><path d="M10 13h4"/></svg>',
  notebook: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/><path d="M8 7h8M8 11h6"/></svg>',
  presentation:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M8 20l4-4 4 4M12 16v4"/></svg>',
  database: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg>',
};

// ── Map file extension to icon ──
function fileIcon(name) {
  var ext = (name || '').split('.').pop().toLowerCase();
  var map = {
    pdf:  ICONS.pdf,  doc: ICONS.doc,  docx: ICONS.doc,
    ppt:  ICONS.presentation, pptx: ICONS.presentation,
    xls:  ICONS.spreadsheet, xlsx: ICONS.spreadsheet, csv: ICONS.spreadsheet,
    png:  ICONS.image, jpg: ICONS.image, jpeg: ICONS.image,
    gif:  ICONS.image, bmp: ICONS.image, webp: ICONS.image, svg: ICONS.image, tiff: ICONS.image,
    mp3:  ICONS.audio, wav: ICONS.audio, m4a: ICONS.audio,
    ogg:  ICONS.audio, flac: ICONS.audio, wma: ICONS.audio, aac: ICONS.audio,
    zip:  ICONS.archive, rar: ICONS.archive, '7z': ICONS.archive, gz: ICONS.archive, tar: ICONS.archive,
    py:   ICONS.code, js: ICONS.code, ts: ICONS.code, java: ICONS.code,
    c:    ICONS.code, cpp: ICONS.code, h: ICONS.code, rs: ICONS.code, go: ICONS.code,
    html: ICONS.code, htm: ICONS.code, css: ICONS.code,
    json: ICONS.code, xml: ICONS.code, yaml: ICONS.code, yml: ICONS.code, toml: ICONS.code,
    ipynb: ICONS.notebook,
    md:   ICONS.doc, txt: ICONS.doc, log: ICONS.doc,
    epub: ICONS.notebook,
    db:   ICONS.database, sqlite: ICONS.database,
  };
  return map[ext] || ICONS.file;
}

// ═══════════════════════════════════════════
//  Auth — token management, login/register
// ═══════════════════════════════════════════

var AUTH = { token: null, user: null };

function loadAuth() {
  var raw = localStorage.getItem('molcraft-auth');
  if (raw) { try { AUTH = JSON.parse(raw); } catch(e) { AUTH = {token:null,user:null}; } }
}
loadAuth();

function saveAuth() {
  localStorage.setItem('molcraft-auth', JSON.stringify(AUTH));
}

function clearAuth() {
  AUTH = { token: null, user: null };
  localStorage.removeItem('molcraft-auth');
}

// API fetch wrapper — adds Authorization header, handles 401
async function apiFetch(url, opts) {
  opts = opts || {};
  if (!opts.headers) opts.headers = {};
  if (AUTH.token) opts.headers['Authorization'] = 'Bearer ' + AUTH.token;
  var r = await fetch(url, opts);
  if (r.status === 401 && AUTH.token) {
    // Token expired — try refresh
    var ref = await fetch('/api/auth/refresh', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: localStorage.getItem('molcraft-refresh') || '' })
    });
    if (ref.ok) {
      var data = await ref.json();
      AUTH.token = data.access_token;
      localStorage.setItem('molcraft-refresh', data.refresh_token);
      saveAuth();
      opts.headers['Authorization'] = 'Bearer ' + AUTH.token;
      return fetch(url, opts);
    } else {
      clearAuth();
      showAuth();
      throw new Error('Session expired');
    }
  }
  if (r.status === 401) { showAuth(); throw new Error('Not authenticated'); }
  return r;
}

function isLoggedIn() { return !!AUTH.token; }

function showAuth(mode) {
  mode = mode || 'login';
  document.getElementById('loading-screen').classList.add('hidden');
  var landing = document.getElementById('landing-page');
  var app = document.getElementById('app');
  var ap = document.getElementById('auth-page');

  // Hide landing/app
  if (landing) landing.style.display = 'none';
  if (app) app.style.display = 'none';

  // Fade in auth page
  ap.classList.add('active');
  ap.style.display = 'flex';
  ap.style.opacity = '0';
  ap.offsetHeight;
  ap.style.transition = 'opacity 0.3s ease';
  ap.style.opacity = '1';
  setTimeout(function() {
    ap.style.transition = '';
    ap.style.opacity = '';
  }, 350);
  toggleAuth(mode);
}

function hideAuth() {
  var ap = document.getElementById('auth-page');
  ap.style.transition = 'opacity 0.2s ease';
  ap.style.opacity = '0';
  document.getElementById('auth-error').style.display = 'none';
  setTimeout(function() {
    ap.classList.remove('active');
    ap.style.display = 'none';
    ap.style.opacity = '';
    ap.style.transition = '';
  }, 200);
}

function toggleAuth(mode) {
  if (!mode) {
    var regVisible = document.getElementById('register-form').style.display === 'block';
    mode = regVisible ? 'login' : 'register';
  }
  var isLogin = (mode === 'login');
  var loginForm = document.getElementById('login-form');
  var registerForm = document.getElementById('register-form');
  var showingForm = isLogin ? loginForm : registerForm;
  var hidingForm = isLogin ? registerForm : loginForm;

  document.getElementById('auth-title').textContent = isLogin ? '欢迎回来' : '创建账户';
  document.getElementById('auth-sub').textContent = isLogin ? '登录你的 MolCraft 账户' : '开始你的科研之旅';
  document.getElementById('toggle-text').textContent = isLogin ? '还没有账户？' : '已有账户？';
  document.getElementById('toggle-link').textContent = isLogin ? '立即注册' : '去登录';
  document.getElementById('auth-error').style.display = 'none';

  // Sequential fade: hide old → show new (no overlap)
  if (hidingForm) {
    hidingForm.style.transition = 'opacity 0.15s ease';
    hidingForm.style.opacity = '0';
  }

  setTimeout(function() {
    if (hidingForm) {
      hidingForm.style.display = 'none';
      hidingForm.style.opacity = '';
      hidingForm.style.transition = '';
    }
    if (showingForm) {
      showingForm.style.display = 'block';
      showingForm.style.opacity = '0';
      showingForm.offsetHeight;
      showingForm.style.transition = 'opacity 0.2s ease';
      showingForm.style.opacity = '1';
      setTimeout(function() {
        showingForm.style.transition = '';
        showingForm.style.opacity = '';
      }, 250);
    }
  }, 150);
}

async function handleLogin(e) {
  e.preventDefault();
  var btn = document.getElementById('login-btn');
  var errEl = document.getElementById('auth-error');
  btn.disabled = true; btn.textContent = '登录中...'; errEl.style.display = 'none';
  try {
    var r = await fetch('/api/auth/login', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        email: document.getElementById('login-email').value,
        password: document.getElementById('login-password').value
      })
    });
    if (!r.ok) {
      var detail = (await r.json()).detail || '登录失败';
      throw new Error(detail);
    }
    var data = await r.json();
    AUTH.token = data.access_token;
    AUTH.user = data.user;
    localStorage.setItem('molcraft-refresh', data.refresh_token);
    saveAuth();
    hideAuth();
    showLanding();
    loadSettings();
    loadDashboard();
    loadConversations();
    syncAgentStatus();
    connectWebSocket();
  } catch(ex) {
    errEl.textContent = ex.message;
    errEl.style.display = 'block';
  } finally {
    btn.disabled = false; btn.textContent = '登录';
  }
}

async function handleRegister(e) {
  e.preventDefault();
  var btn = document.getElementById('reg-btn');
  var errEl = document.getElementById('auth-error');
  var email = document.getElementById('reg-email').value.trim();

  // Client-side email validation
  email = email.toLowerCase().trim();
  if (email.length > 254) {
    errEl.textContent = '邮箱地址过长，最多254个字符';
    errEl.style.display = 'block';
    return;
  }
  if (email.indexOf('..') >= 0) {
    errEl.textContent = '邮箱格式不正确，不能包含连续的点';
    errEl.style.display = 'block';
    return;
  }
  var atPos = email.indexOf('@');
  if (atPos < 1) {
    errEl.textContent = '邮箱格式不正确，缺少@符号';
    errEl.style.display = 'block';
    return;
  }
  var localPart = email.substring(0, atPos);
  var domain = email.substring(atPos + 1);
  if (!domain || domain.indexOf('.') < 0) {
    errEl.textContent = '邮箱域名格式不正确，缺少顶级域名';
    errEl.style.display = 'block';
    return;
  }
  var emailRe = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;
  if (!emailRe.test(email)) {
    errEl.textContent = '邮箱格式不正确，请输入有效的邮箱地址';
    errEl.style.display = 'block';
    return;
  }
  if (localPart.length > 64) {
    errEl.textContent = '邮箱前缀过长，最多64个字符';
    errEl.style.display = 'block';
    return;
  }
  if (localPart.length < 3) {
    errEl.textContent = '邮箱前缀太短，至少需要3个字符';
    errEl.style.display = 'block';
    return;
  }
  if (localPart.charAt(0) === '.' || localPart.charAt(localPart.length-1) === '.') {
    errEl.textContent = '邮箱前缀不能以点号开头或结尾';
    errEl.style.display = 'block';
    return;
  }
  // Common provider typo hints
  var typos = {
    'gmial.com':'gmail.com','gmail.co':'gmail.com','gmai.com':'gmail.com',
    'gmal.com':'gmail.com','hotmai.com':'hotmail.com','hotmal.com':'hotmail.com',
    'outlook.co':'outlook.com','outlok.com':'outlook.com',
    'yahooo.com':'yahoo.com','yaho.com':'yahoo.com',
    'qq.con':'qq.com','qq.co':'qq.com',
    '163.con':'163.com','163.co':'163.com'
  };
  if (typos[domain]) {
    errEl.textContent = '邮箱域名可能拼写错误，您是否想输入 @' + typos[domain] + '？';
    errEl.style.display = 'block';
    return;
  }

  btn.disabled = true; btn.textContent = '注册中...'; errEl.style.display = 'none';
  try {
    var r = await fetch('/api/auth/register', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        email: email,
        password: document.getElementById('reg-password').value,
        display_name: document.getElementById('reg-name').value
      })
    });
    if (!r.ok) {
      var detail = (await r.json()).detail || '注册失败';
      if (r.status === 409) {
        // Email already exists — offer quick switch to login
        errEl.innerHTML = detail + '<br><a onclick="toggleAuth(\'login\');document.getElementById(\'login-email\').value=document.getElementById(\'reg-email\').value" style="color:var(--accent);cursor:pointer;text-decoration:underline">点击此处直接登录</a>';
        errEl.style.display = 'block';
        btn.disabled = false; btn.textContent = '注册';
        return;
      }
      throw new Error(detail);
    }
    var data = await r.json();
    AUTH.token = data.access_token;
    AUTH.user = data.user;
    localStorage.setItem('molcraft-refresh', data.refresh_token);
    saveAuth();
    hideAuth();
    showLanding();
    loadSettings();
    loadDashboard();
    loadConversations();
    syncAgentStatus();
    connectWebSocket();
  } catch(ex) {
    errEl.textContent = ex.message;
    errEl.style.display = 'block';
  } finally {
    btn.disabled = false; btn.textContent = '注册';
  }
}

function logout() {
  clearAuth();
  localStorage.removeItem('molcraft-refresh');
  // Stop background polling
  if (window._dashInterval) { clearInterval(window._dashInterval); window._dashInterval = null; }
  if (window._logPollInterval) { clearInterval(window._logPollInterval); window._logPollInterval = null; }
  // Disconnect WebSocket
  if (ws) { try { ws.close(); } catch(e) {} ws = null; }
  _apiSettingsCache = { base_url: '', api_key: '', model: '' };
  // Clear settings input fields so old values don't persist across logout/login
  var bs = document.getElementById('setting-base-url'); if (bs) bs.value = '';
  var ak = document.getElementById('setting-api-key'); if (ak) { ak.value = ''; ak.dataset.masked = '0'; }
  var md = document.getElementById('setting-model'); if (md) md.value = '';
  // Clear app state — prevent previous user's data leaking into next login
  activeConvId = null;
  STATE = { currentPage: 'studio', agentRunning: false, logLines: [], experiments: [], charts: [], files: [] };
  // Clear conversation list in sidebar
  var convList = document.getElementById('conversation-list');
  if (convList) convList.innerHTML = '';
  // Clear log display
  var logContainer = getLogContainer();
  if (logContainer) logContainer.innerHTML = '';
  // Clear research goal
  var goalEl = document.getElementById('studio-goal');
  if (goalEl) goalEl.value = '';
  // Clear studio stats
  var statExps = document.getElementById('stat-experiments'); if (statExps) statExps.textContent = '0';
  var statConfirmed = document.getElementById('stat-confirmed'); if (statConfirmed) statConfirmed.textContent = '0';
  var statRejected = document.getElementById('stat-rejected'); if (statRejected) statRejected.textContent = '0';
  var statCharts = document.getElementById('stat-charts'); if (statCharts) statCharts.textContent = '0';
  // Clear charts/experiments containers
  var chartsGrid = document.getElementById('charts-grid'); if (chartsGrid) chartsGrid.innerHTML = '';
  var papersContainer = document.getElementById('papers-container'); if (papersContainer) papersContainer.innerHTML = '';
  var filesContainer = document.getElementById('files-container'); if (filesContainer) filesContainer.innerHTML = '';
  // Update chart badge
  var badge = document.getElementById('chart-badge'); if (badge) badge.textContent = '0';
  if (ws) { ws.close(); ws = null; }
  document.getElementById('app').style.display = 'none';
  document.getElementById('landing-page').style.display = 'none';
  showAuth('login');
}

// ═══════════════════════════════════════════

var STATE = { currentPage: 'studio', agentRunning: false, logLines: [], experiments: [], charts: [], files: [] };
var activeConvId = null;

// ── API URL → 模型映射 (2026年6月更新) ──
var URL_MODELS = {
  'openai.com':          ['gpt-5.5', 'gpt-5.4-mini', 'gpt-5.4', 'gpt-4.1', 'gpt-4.1-mini', 'gpt-4o', 'gpt-4o-mini', 'o4-mini', 'o3-mini'],
  'siliconflow.cn':      ['deepseek-ai/DeepSeek-V4-Pro', 'deepseek-ai/DeepSeek-V4-Flash', 'deepseek-ai/DeepSeek-V3.2', 'deepseek-ai/DeepSeek-R1', 'Qwen/Qwen3.6-35B-A3B', 'Qwen/Qwen2.5-72B-Instruct', 'Pro/zai-org/GLM-5.1', 'Pro/moonshotai/Kimi-K2.6'],
  'deepseek.com':        ['deepseek-v4-flash', 'deepseek-v4-pro', 'deepseek-chat', 'deepseek-reasoner'],
  'aliyuncs.com':        ['qwen3.7-max', 'qwen3.6-plus', 'qwen3.6-flash', 'qwen-plus', 'qwen-max', 'qwen-flash'],
  'moonshot.ai':         ['kimi-k2.6', 'moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
  'bigmodel.cn':         ['glm-5.1', 'glm-5', 'glm-4.7', 'glm-4-plus', 'glm-4-flash'],
};
var ws = null;
var wsReconnectTimer = null;
var _inToolOutput = false;  // tracks whether current line is tool output
var _thinkingActive = false;  // thinking bubble is visible
var _thinkingText = '';       // accumulated thinking text
var _thinkingEl = null;       // DOM element for thinking bubble
var _toolCallActive = false;  // streaming tool call card is visible
var _toolCallName = '';       // current streaming tool name
var _toolCallText = '';       // accumulated streaming tool args
var _toolCallEl = null;       // DOM element for streaming tool card
var _lastToolName = '';       // last [TOOL] name for output context
var _debounceTimer = null;
var _renderingSaved = false;  // true while rendering logs loaded from conversation file
// In-memory cache for API settings — persists across page nav, cleared on refresh/logout
var _apiSettingsCache = { base_url: '', api_key: '', model: '' };

document.addEventListener('DOMContentLoaded', async function() {
  setTimeout(function() {
    var ls = document.getElementById('loading-screen');
    if (ls) ls.classList.add('hidden');
  }, 600);

  window.addEventListener('hashchange', handleRoute);

  // ── Keyboard shortcuts ──
  document.addEventListener('keydown', function(e) {
    // Ctrl+Shift+L → clear current conversation logs
    if (e.ctrlKey && e.shiftKey && e.key === 'L') {
      e.preventDefault();
      if (STATE.currentPage === 'studio' && activeConvId && !STATE.agentRunning) {
        clearLog();
      }
    }
    // Ctrl+Shift+N → new conversation
    if (e.ctrlKey && e.shiftKey && e.key === 'N') {
      e.preventDefault();
      if (!STATE.agentRunning) {
        navigateTo('studio');
        var goalInput = document.getElementById('studio-goal');
        if (goalInput) { goalInput.value = ''; goalInput.focus(); }
        var container = getLogContainer();
        if (container) container.innerHTML = '';
        activeConvId = null;
        _lastLogSeq = -1;
      }
    }
  });

  document.querySelectorAll('.nav-item').forEach(function(el) {
    el.addEventListener('click', function(e) { e.preventDefault(); navigateTo(el.dataset.page); });
  });

  var tempSlider = document.getElementById('setting-temperature');
  if (tempSlider) tempSlider.addEventListener('input', function() {
    var tv = document.getElementById('temp-value'); if (tv) tv.textContent = tempSlider.value;
    autoSaveSettings();
  });

  // ── Auto-resize chat textarea ──
  var chatTextarea = document.getElementById('studio-goal');
  if (chatTextarea) {
    chatTextarea.addEventListener('input', function() {
      this.style.height = 'auto';
      var newH = Math.min(this.scrollHeight, window.innerHeight * 0.5);
      this.style.height = newH + 'px';
    });
  }

  // ── File filter tabs (with GSAP fade transition) ──
  document.querySelectorAll('.file-filter-tab').forEach(function(tab) {
    tab.addEventListener('click', function() {
      var alreadyActive = tab.classList.contains('active');
      if (alreadyActive) return;
      document.querySelectorAll('.file-filter-tab').forEach(function(t) { t.classList.remove('active'); });
      tab.classList.add('active');
      switchFileTab();
    });
  });

  function switchFileTab() {
    var container = document.getElementById('files-container');
    if (!container) { renderFiles(); return; }

    if (typeof gsap !== 'undefined') {
      gsap.timeline()
        .to(container, { opacity: 0, duration: 0.1, ease: 'power2.in' })
        .call(function() { renderFiles(); })
        .fromTo(container, { opacity: 0, y: 6 }, { opacity: 1, y: 0, duration: 0.2, ease: 'power2.out' });
    } else {
      renderFiles();
    }
  }

  // Theme dropdown — handled by selectTheme() below

  // Auto-save settings on any field change (debounced)
  ['setting-base-url','setting-api-key','setting-model','setting-prompt',
   'iterations-input','minutes-input','write-paper-toggle'].forEach(function(id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener('input', autoSaveSettings);
    if (el) el.addEventListener('change', autoSaveSettings);
  });

  // Auto-save research goal to conversation (debounced)
  var studioGoal = document.getElementById('studio-goal');
  if (studioGoal) {
    studioGoal.addEventListener('input', function() {
      clearTimeout(_goalSaveTimer);
      _goalSaveTimer = setTimeout(saveGoalSilent, 800);
    });
  }

  // API Key show/hide toggle + focus clear mask
  var toggleApiKey = document.getElementById('toggle-api-key');
  var apiKeyInput = document.getElementById('setting-api-key');
  if (toggleApiKey && apiKeyInput) {
    toggleApiKey.addEventListener('click', function() {
      if (apiKeyInput.dataset.masked === '1') {
        apiKeyInput.dataset.masked = '0';
        apiKeyInput.value = '';
        apiKeyInput.style.webkitTextSecurity = 'none';
        toggleApiKey.textContent = '隐藏';
        return;
      }
      if (apiKeyInput.style.webkitTextSecurity === 'disc') {
        apiKeyInput.style.webkitTextSecurity = 'none';
        toggleApiKey.textContent = '隐藏';
      } else {
        apiKeyInput.style.webkitTextSecurity = 'disc';
        toggleApiKey.textContent = '显示';
      }
    });
    // Clear masked placeholder when user focuses to type a new key
    apiKeyInput.addEventListener('focus', function() {
      if (apiKeyInput.dataset.masked === '1') {
        apiKeyInput.dataset.masked = '0';
        apiKeyInput.value = '';
        apiKeyInput.style.webkitTextSecurity = 'none';
      }
    });
  }

  // ── Dropdown click-outside close ──
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.dropdown-input')) {
      document.querySelectorAll('.dropdown-list.open').forEach(function(el) { el.classList.remove('open'); });
    }
  });

  // ── API URL → 模型联动 ──
  var urlInput = document.getElementById('setting-base-url');
  if (urlInput) {
    urlInput.addEventListener('input', updateModelDropdown);
  }
  updateModelDropdown();  // init model list

  // ── Auth: check if logged in ──
  if (!isLoggedIn()) {
    showAuth('login');
    return;
  }

  // Show UI for logged-in users
  var userDiv = document.querySelector('.sidebar-user');
  var userEl = document.getElementById('sidebar-username');
  if (userEl && AUTH.user) userEl.textContent = AUTH.user.email || AUTH.user.display_name || 'User';
  if (userDiv) userDiv.style.display = '';

  await loadSettings();
  await loadDashboard();
  await loadConversations();
  await syncAgentStatus();
  initTokenDisplay();

  var goalInput = document.getElementById('studio-goal');
  if (goalInput) goalInput.addEventListener('input', function() {
    var convId = activeConvId;
    if (!convId) return;
    clearTimeout(_debounceTimer);
    _debounceTimer = setTimeout(function() {
      var g = goalInput.value.trim();
      var title = g ? g.slice(0, 60) : 'New Conversation';
      apiFetch('/api/conversations/' + convId, {
        method: 'PUT', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({goal: g, title: title})
      }).then(function(){ loadConversations(); }).catch(function(){});
    }, 500);
  });

  // Auto-enter app for already-logged-in users
  showLanding();
  initScrollAnimations();
  handleRoute();
  connectWebSocket();
  window._dashInterval = setInterval(loadDashboard, 5000);
  window._logPollInterval = setInterval(pollAgentLogs, 2000);
  initConvResizer();
  initSidebarResizer();
  initStudioResizer();
  initDropZone();
  initLogScrollDetection();
  initLogFilters();
});


// ===== WEBSOCKET =====
function connectWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) return;
  if (!AUTH.token) return;
  var protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  // Pass auth token as query param for WebSocket
  var wsUrl = protocol + '//' + window.location.host + '/ws?token=' + encodeURIComponent(AUTH.token);
  try {
    ws = new WebSocket(wsUrl);
    ws.onopen = function() { if (wsReconnectTimer) { clearTimeout(wsReconnectTimer); wsReconnectTimer = null; } syncAgentStatus(); };
    ws.onmessage = function(event) { try { handleWSMessage(JSON.parse(event.data)); } catch(e) {} };
    ws.onclose = function() { if (!wsReconnectTimer) wsReconnectTimer = setTimeout(connectWebSocket, 3000); };
    ws.onerror = function() { ws.close(); };
  } catch(e) { wsReconnectTimer = setTimeout(connectWebSocket, 5000); }
}

function handleWSMessage(msg) {
  switch (msg.type) {
    case 'log':
      if (msg.conv_id && activeConvId && msg.conv_id !== activeConvId) break;
      // Dedup: skip logs already loaded from DB (race between WS broadcast and selectConv)
      if (msg.seq >= 0 && msg.seq <= _lastLogSeq) break;
      addLogLine(msg.data);
      if (msg.seq >= 0) _lastLogSeq = Math.max(_lastLogSeq, msg.seq);
      break;
    case 'status': updateStatus(msg.data); break;
    case 'charts_update': STATE.charts = msg.data || []; renderCharts(); updateChartBadge(); break;
    case 'experiments_update': loadExperiments(); break;
    case 'thinking':
      if (msg.conv_id && activeConvId && msg.conv_id !== activeConvId) break;
      handleThinking(msg.data);
      break;
    case 'tool_call_chunk':
      if (msg.conv_id && activeConvId && msg.conv_id !== activeConvId) break;
      handleToolCallChunk(msg.tool, msg.data);
      break;
    case 'usage':
      updateTokenUsage(msg.data);
      break;
    case 'pong': break;
  }
}

setInterval(function() { if (ws && ws.readyState === WebSocket.OPEN) ws.send('ping'); }, 30000);

// ===== ROUTING =====
function handleRoute() { navigateTo(window.location.hash.slice(1) || 'studio'); }

function navigateTo(page) {
  if (STATE.currentPage === page) return;
  // Auto-save settings when leaving settings page
  if (STATE.currentPage === 'settings' && page !== 'settings') {
    saveSettingsSilent();
  }
  var oldTarget = document.getElementById('page-' + STATE.currentPage);
  STATE.currentPage = page;
  // Update top nav items
  document.querySelectorAll('.top-nav-item[data-page]').forEach(function(el) { el.classList.toggle('active', el.dataset.page === page); });
  // Preload new page content
  if (page === 'experiments') loadExperiments();
  if (page === 'charts') renderCharts();
  if (page === 'files') loadFiles();
  if (page === 'settings') loadSettings();

  var target = document.getElementById('page-' + page);
  if (!target) return;

  // Hide old page instantly
  if (oldTarget && oldTarget !== target) {
    oldTarget.classList.remove('active');
    oldTarget.style.display = 'none';
  }
  // Show new page and fade it in
  target.style.display = 'flex';
  target.style.flexDirection = 'column';
  target.style.opacity = '0';
  target.offsetHeight;
  target.classList.add('active');
  target.style.transition = 'opacity 0.2s ease';
  target.style.opacity = '1';
  setTimeout(function() {
    target.style.transition = '';
    target.style.opacity = '';
  }, 250);

  // Reset chat scroll when entering studio
  if (page === 'studio') {
    var chatMsgs = document.getElementById('chat-messages');
    if (chatMsgs) chatMsgs.scrollTop = chatMsgs.scrollHeight;
  }
}

// ── Top nav auto-hide ──
(function() {
  var trigger = document.getElementById('top-nav-trigger');
  var nav = document.getElementById('top-nav');
  var hideTimer = null;
  function showNav() {
    if (nav) nav.classList.add('show');
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
  }
  function hideNavSoon() {
    hideTimer = setTimeout(function() {
      if (nav) nav.classList.remove('show');
    }, 400);
  }
  if (trigger) {
    trigger.addEventListener('mouseenter', showNav);
  }
  if (nav) {
    nav.addEventListener('mouseenter', showNav);
    nav.addEventListener('mouseleave', hideNavSoon);
  }
})();

// ── Collapsible conversation panel ──
function toggleConvPanel() {
  var panel = document.getElementById('conv-panel');
  if (!panel) return;
  panel.classList.toggle('collapsed');
  var collapsed = panel.classList.contains('collapsed');
  localStorage.setItem('molcraft-conv-collapsed', collapsed);
  // Toggle expand button in top nav
  var expandBtn = document.getElementById('top-expand-conv');
  if (expandBtn) expandBtn.style.display = collapsed ? '' : 'none';
}

// ===== API =====
async function api(url, options) {
  options = options || {};
  var resp = await apiFetch(url, { headers: {'Content-Type': 'application/json'}, ...options });
  if (!resp.ok) { var err = await resp.json().catch(function(){return{}}); throw new Error(err.detail || 'HTTP ' + resp.status); }
  return await resp.json();
}

function toast(message, type) {
  type = type || 'info';
  var container = document.getElementById('toast-container');
  if (!container) return;
  var el = document.createElement('div');
  el.className = 'toast ' + type;
  el.innerHTML = '<span>' + ({success:'OK',error:'ERR',info:'i'}[type]||'i') + '</span> ' + escapeHtml(message);
  container.appendChild(el);
  setTimeout(function() { el.style.opacity = '0'; setTimeout(function(){ el.remove(); }, 300); }, 3000);
}

// ===== STATUS =====
function updateStatus(data) {
  STATE.agentRunning = data.running;
  var dot = document.getElementById('status-indicator');
  var txt = document.getElementById('status-text');
  var ds = document.getElementById('dash-start-btn'), dd = document.getElementById('dash-stop-btn');
  var ss = document.getElementById('studio-start-btn'), sd = document.getElementById('studio-stop-btn');

  if (data.running) {
    if (dot) dot.className = 'status-dot running';
    if (txt) txt.textContent = 'Running (' + data.current_iteration + '/' + data.total_iterations + ')';
    updateAgentStatus('executing');
    if (ds) ds.style.display = 'none'; if (dd) { dd.style.display = ''; dd.disabled = false; dd.innerHTML = ICONS.stop; }
    if (ss) ss.style.display = 'none'; if (sd) { sd.style.display = ''; sd.disabled = false; sd.innerHTML = ICONS.stop; }
  } else {
    if (dot) dot.className = 'status-dot idle';
    if (txt) txt.textContent = '就绪';
    if (ds) ds.style.display = ''; if (dd) { dd.style.display = 'none'; dd.disabled = false; dd.innerHTML = ICONS.stop; }
    if (ss) ss.style.display = ''; if (sd) { sd.style.display = 'none'; sd.disabled = false; sd.innerHTML = ICONS.stop; }
    updateAgentStatus('done');
  }
}

async function syncAgentStatus() {
  try {
    var resp = await api('/api/status');
    updateStatus(resp);
  } catch(e) {}
}

// ===== LOG =====
// ===== LOG STATE =====
var LOG_AUTO_SCROLL = true;
var LOG_ACTIVE_FILTER = 'all';
var LOG_TOTAL_LINES = 0;
var LOG_FILTERED_COUNT = 0;

// ===== TOOL NAME CHINESE MAPPING =====
var TOOL_CN = {
  'read_file': '读取文件',
  'write_file': '写入文件',
  'execute_code': '执行代码',
  'search_literature': '文献搜索',
  'analyze_data': '数据分析',
  'generate_chart': '生成图表',
  'record_experiment': '记录实验',
  'report_iteration': '迭代报告',
  'write_paper': '撰写论文',
  'delete_file': '删除文件',
  'fetch_url': '抓取网页',
  'deep_research': '深度调研',
  'output': '工具输出'
};
function toolNameCN(name) {
  return TOOL_CN[name] || name;
}

function getLogContainer() {
  // Return chat-messages when on studio page, fallback to log-container
  var chat = document.getElementById('chat-messages');
  if (chat && STATE.currentPage === 'studio') return chat;
  return document.getElementById('log-container');
}

function addLogLine(line) {
  // Finalize any active thinking bubble when a real log entry arrives
  if (_thinkingActive) { finalizeThinking(); }

  var container = getLogContainer();
  if (!container) return;
  var inChat = container.id === 'chat-messages';
  var welcome = container.querySelector('.log-welcome, .chat-welcome');
  if (welcome) welcome.remove();

  LOG_TOTAL_LINES++;

  // Determine level and whether this is a tool call
  var level = 'info';
  var isTool = false;
  var isSeparator = false;
  var toolInfo = null;
  var sepLabel = '';

  // Check for iteration separators
  var iterMatch = line.match(/={10,}/);
  var iterLabel = line.match(/Iteration\s+(\d+)\/(\d+)\s+start/i);
  if (iterMatch && iterLabel) {
    isSeparator = true;
    sepLabel = '第 ' + iterLabel[1] + ' / ' + iterLabel[2] + ' 轮迭代';
  }

  // Extract timestamp first (needed for endToolOutput detection below)
  var tsMatch = line.match(/\[(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}[^\]]*)\]/);
  var timestamp = tsMatch ? tsMatch[1] : '';
  var message = tsMatch ? line.slice(tsMatch[0].length).trim() : line;

  // ── Tool output tracking ──
  // Once we see [TOOL] or [ERROR] tool_name, subsequent lines are tool output
  // until a separator or structured log entry appears.  This prevents tool
  // output that happens to contain "Error", "===", etc. from leaking into
  // the wrong filter categories.
  // End tool output only on explicit structured log markers.
  // Use `message` (timestamp stripped) because engine stdout lines carry timestamps.
  var endToolOutput = /^(?:\[(?:compress|resume|warmup|API)\]|No more tool calls|Iteration \d+ done|✓ Experiment complete|✓ \{|✗ Iteration|Starting research agent|Goal:|Fatal error:|Experiment stopped|⏰ Time limit reached|Sending request to model)/.test(message);
  if (isSeparator || endToolOutput) {
    _inToolOutput = false;
  }

  var _toolCardUpgraded = false; // set when streaming card already upgraded to formal card

  // Tool call detection — handle both English and Chinese tool names
  var toolMatch = message.match(/\[TOOL\]\s+(\S+?)\s*\|\s*(\{.*\})/);
  if (!toolMatch) {
    toolMatch = message.match(/\[TOOL\]\s+(.+?)\s*\|\s*(.+)/);
  }
  // Tool error: [ERROR] tool_name: ...  →  belongs under 工具, not 错误
  var toolErrorMatch = message.match(/\[ERROR\]\s+(\S+)/);
  if (toolMatch) {
    var matchedName = toolMatch[1].trim();
    var matchedArgs = toolMatch[2].trim();
    _lastToolName = matchedName; // track for output context
    // If we have an active streaming card for the SAME tool, upgrade it in-place
    if (_toolCallActive && _toolCallName === matchedName) {
      upgradeStreamCard();
      // Update the just-upgraded card with the real [TOOL] line for persistence
      var _upgraded = container.querySelector('.log-tool-card[data-saved="0"]');
      if (_upgraded) {
        _upgraded.dataset.raw = line;
        // Update args preview in header
        var _argsSpan = _upgraded.querySelector('.log-tool-args');
        if (_argsSpan) _argsSpan.textContent = matchedArgs.slice(0, 80);
      }
      _inToolOutput = true;
      isTool = true; level = 'tool';
      toolInfo = { name: matchedName, args: matchedArgs };
      _toolCardUpgraded = true; // skip creating a duplicate card
    } else if (_toolCallActive) {
      // Different tool — finalize old streaming card first
      upgradeStreamCard();
      _inToolOutput = true;
      isTool = true; level = 'tool';
      toolInfo = { name: matchedName, args: matchedArgs };
    } else {
      _inToolOutput = true;
      isTool = true; level = 'tool';
      toolInfo = { name: matchedName, args: matchedArgs };
    }
  } else if (toolErrorMatch) {
    _inToolOutput = true;
    isTool = true; level = 'tool';
    toolInfo = { name: toolErrorMatch[1].trim(), args: line, isError: true };
  } else if (_inToolOutput && message.trim()) {
    // Text lines between tool calls are tool output — keep under 工具
    isTool = true; level = 'tool';
    toolInfo = { name: _lastToolName || 'output', args: message, isOutput: true };
  }

  // Thinking card detection: [THINKING] full text (restored from saved conversation)
  // Use [\s\S]* instead of .* so multi-line thinking text is fully captured
  var thinkingMatch = message.match(/\[THINKING\]\s+([\s\S]*)/);
  if (thinkingMatch) {
    isTool = true; level = 'info';
    toolInfo = { name: 'thinking', args: thinkingMatch[1].trim(), isThinking: true };
  }

  // If streaming card was already upgraded to a formal card, don't create
  // a duplicate [TOOL] card — the upgraded card is already in the DOM.
  if (_toolCardUpgraded) {
    updateLogCount();
    if (LOG_AUTO_SCROLL) scrollLogToBottom();
    return;
  }

  // Level detection (only for lines that are NOT tool cards or separators)
  var lower = message.toLowerCase();
  if (!isTool && !isSeparator) {
    if (/\[error\]|traceback|exception|error:|fatal/i.test(message)) level = 'error';
    else if (/\[warn\]|warning/i.test(message)) level = 'warn';
    else if (/\[success\]|completed|done|finished/i.test(message)) level = 'success';
    // Only match explicit markers at line-start (after optional timestamp),
    // not embedded === or --- in tool output / data tables
    else if (/^(?:\[[^\]]*\]\s*)?(?:===|---)/.test(message) || /agent started|agent finished/i.test(message)) level = 'highlight';
  }

  // Shorten timestamp for display
  var shortTime = '';
  if (timestamp) {
    var tParts = timestamp.match(/(\d{2}:\d{2}:\d{2})/);
    shortTime = tParts ? tParts[1] : timestamp.slice(0, 8);
  }

  // ── Build DOM ──
  var el;

  if (isSeparator) {
    // Iteration separator
    el = document.createElement('div');
    el.className = 'log-separator';
    el.dataset.filter = 'highlight';
    el.innerHTML = '<div class="log-separator-line"></div>' +
      '<span class="log-separator-label">' + escapeHtml(sepLabel) + '</span>' +
      '<div class="log-separator-line"></div>';
  } else if (isTool && toolInfo && !_toolCardUpgraded) {
    // Tool call card (or thinking card)
    if (toolInfo.isThinking) {
      // Restored thinking card — amber-themed, expanded by default
      el = document.createElement('div');
      el.className = 'log-tool-card thinking-card expanded';
      el.dataset.filter = 'info';
      el.dataset.saved = '1';  // Mark as already saved — skip in saveCurrentThinking
      el.innerHTML =
        '<div class="log-tool-header thinking-card-header" onclick="this.parentElement.classList.toggle(\'expanded\')">' +
          '<span class="log-tool-icon">&#x1f4ad;</span>' +
          '<span class="log-tool-name thinking-name">Agent 思考</span>' +
          '<span class="log-tool-eng-name">' + escapeHtml(String(toolInfo.args.length)) + ' chars</span>' +
          (shortTime ? '<span class="log-tool-time">' + escapeHtml(shortTime) + '</span>' : '') +
          '<span class="log-tool-chevron">&#x25b6;</span>' +
        '</div>' +
        '<div class="log-tool-body">' +
          '<div class="log-tool-result thinking-result">' + escapeHtml(toolInfo.args) + '</div>' +
        '</div>';
    } else {
      var isToolErr = toolInfo.isError;
      var isOutput = toolInfo.isOutput;
      var cnName;
      if (isOutput) {
        var parentCN = toolNameCN(toolInfo.name);
        cnName = (parentCN && parentCN !== toolInfo.name) ? parentCN + ' 输出' : '工具输出';
      } else {
        cnName = toolNameCN(toolInfo.name);
      }

      // Extract clean content from JSON args/output for display (not just raw JSON)
      var isCodeTool = false;
      var bodyContent = toolInfo.args;
      var argsPreview = toolInfo.args.slice(0, 80);

      if (!isToolErr && toolInfo.args && toolInfo.args.charAt(0) === '{') {
        var cleaned = _cleanToolData(toolInfo.name, toolInfo.args, isOutput);
        if (cleaned) {
          bodyContent = cleaned.text;
          isCodeTool = cleaned.isCode;
          argsPreview = cleaned.text.replace(/\n/g, ' ').substring(0, 80);
        }
      }

      el = document.createElement('div');
      el.className = 'log-tool-card' + (isToolErr ? ' log-tool-error' : '');
      el.dataset.filter = 'tool';
      el.innerHTML =
        '<div class="log-tool-header" onclick="this.parentElement.classList.toggle(\'expanded\')">' +
          '<span class="log-tool-icon">' + (isToolErr ? '&#x26a0;' : '&#x1f527;') + '</span>' +
          '<span class="log-tool-name">' + escapeHtml(cnName) + '</span>' +
          '<span class="log-tool-eng-name">' + escapeHtml(toolInfo.name) + '</span>' +
          '<span class="log-tool-args">' + escapeHtml(argsPreview) + '</span>' +
          (shortTime ? '<span class="log-tool-time">' + escapeHtml(shortTime) + '</span>' : '') +
          '<span class="log-tool-chevron">&#x25b6;</span>' +
        '</div>' +
        '<div class="log-tool-body">' +
          '<div class="log-tool-result">' + (isCodeTool ? '<pre>' + escapeHtml(bodyContent) + '</pre>' : escapeHtml(bodyContent)) + '</div>' +
        '</div>';
    }
  } else {
    // Regular log line
    el = document.createElement('div');
    el.className = 'log-entry';
    el.dataset.filter = level === 'info' ? 'info' : level;

    var dotClass = 'lvl-' + level;
    var msgClass = 'msg-' + level;

    el.innerHTML =
      '<span class="log-level ' + dotClass + '"></span>' +
      '<span class="log-body">' +
        '<span class="log-msg ' + msgClass + '">' + escapeHtml(message) + '</span>' +
      '</span>' +
      (shortTime ? '<span class="log-time">' + escapeHtml(shortTime) + '</span>' : '');
  }

  container.appendChild(el);

  // Store the raw log line so saveCurrentLogs can save the EXACT same text
  // the backend persisted.  Reconstructing from DOM elements loses the
  // full timestamp format, which breaks server-side deduplication.
  el.dataset.raw = line;

  // Mark WS-received entries so saveCurrentLogs knows the backend
  // already persists them — avoids duplicate log entries on switch.
  if (!_renderingSaved) el.dataset.fromWs = '1';

  // Apply active filter
  if (LOG_ACTIVE_FILTER !== 'all') applyLogFilter(el);

  // Trim old entries
  while (container.children.length > 3000) container.removeChild(container.firstChild);

  updateLogCount();
  if (LOG_AUTO_SCROLL) scrollLogToBottom();
}

// ── Thinking bubble (live streaming thought display) ──
function handleThinking(text) {
  // Sentinel: end of thinking stream
  if (text === '__END__') {
    finalizeThinking();
    return;
  }

  var container = getLogContainer();
  if (!container) return;
  var welcome = container.querySelector('.log-welcome, .chat-welcome');
  if (welcome) welcome.remove();

  if (!_thinkingActive) updateAgentStatus('thinking');

  _thinkingText += text;
  _thinkingActive = true;

  if (!_thinkingEl) {
    _thinkingEl = document.createElement('div');
    _thinkingEl.className = 'thinking-bubble';
    _thinkingEl.innerHTML =
      '<div class="thinking-header">' +
        '<span class="thinking-dot"></span>' +
        '<span class="thinking-label">Thinking...</span>' +
      '</div>' +
      '<div class="thinking-body"></div>';
    container.appendChild(_thinkingEl);
  }

  // Update the body text live
  var body = _thinkingEl.querySelector('.thinking-body');
  if (body) body.textContent = _thinkingText;

  if (LOG_AUTO_SCROLL) scrollLogToBottom();
}

// ── Streaming tool call display (like thinking bubble but for code/args) ──
// Upgraded: clean content extraction for ALL tools, stream card upgrades to formal log card

var _toolLabels = {
  'execute_code': 'Executing Code',
  'write_file': 'Writing File',
  'write_paper': 'Writing Paper',
  'search_literature': 'Searching Literature',
  'analyze_data': 'Analyzing Data',
  'generate_chart': 'Generating Chart',
  'record_experiment': 'Recording Experiment',
  'report_iteration': 'Reporting Iteration',
  'read_file': 'Reading File',
  'delete_file': 'Deleting File',
  'fetch_url': 'Fetching URL',
  'deep_research': 'Deep Research'
};

// Priority display keys per tool — extract these fields from streaming JSON for clean display
var _toolContentKeys = {
  'execute_code':      ['code'],
  'write_file':        ['content', 'file_path'],
  'write_paper':       ['title', 'abstract', 'sections'],
  'search_literature': ['query'],
  'analyze_data':      ['file_path'],
  'generate_chart':    ['title', 'chart_type', 'x_column', 'y_columns'],
  'record_experiment': ['hypothesis', 'conclusion', 'round_num'],
  'report_iteration':  ['summary', 'hypothesis_id', 'round_num'],
  'read_file':         ['file_path'],
  'delete_file':       ['file_path', 'reason'],
  'fetch_url':         ['url'],
  'deep_research':     ['topic'],
};

// ── Clean tool output/args: extract human-readable content from JSON or Python repr ──
function _cleanToolData(toolName, rawText, isOutput) {
  if (!rawText || rawText.charAt(0) !== '{') return null;

  // Try JSON first (new format)
  var data = null;
  try { data = JSON.parse(rawText); } catch(e) {}

  if (data) {
    return _extractCleanFields(toolName, data, rawText, isOutput);
  }

  // Fallback: Python repr format (old data, single quotes)
  return _extractPythonRepr(toolName, rawText, isOutput);
}

// Extract from parsed JSON object
function _extractCleanFields(toolName, data, rawText, isOutput) {
  var text = '', isCode = false;

  if (isOutput) {
    // Tool results — prioritize the "main content" field
    if (data.stdout)           { text = data.stdout; isCode = true; }
    else if (data.content)     { text = data.content; }
    else if (data.text)        { text = data.text; }
    else if (data.results)     { text = data.results.map(function(r){return r.title||r.snippet||r.url||'';}).filter(Boolean).join('\n'); }
    else if (data.message)     { text = data.message; }
    else if (data.error)       { text = 'Error: ' + data.error; }
    else {
      // Generic: show key status fields
      text = _formatStatusFields(data);
    }
  } else {
    // Tool args — extract code/content/sections
    var clean = _extractStreamContent(toolName, rawText);
    if (clean) { text = clean; isCode = (toolName === 'execute_code' || toolName === 'write_file' || toolName === 'write_paper'); }
  }

  return text ? {text: text, isCode: isCode} : null;
}

// Extract from Python repr format (old data: {'key': 'value', ...})
function _extractPythonRepr(toolName, rawText, isOutput) {
  var text = '', isCode = false;

  // Primary content fields to try (ordered by priority)
  var primaryKeys = isOutput
    ? ['stdout', 'content', 'text', 'message', 'error', 'title', 'summary', 'hypothesis', 'conclusion', 'query', 'topic']
    : ['code', 'content', 'sections', 'query', 'title', 'hypothesis', 'summary'];

  for (var i = 0; i < primaryKeys.length; i++) {
    var k = primaryKeys[i];
    var val = _extractPythonField(rawText, k);
    if (val !== null) {
      text = val;
      isCode = (isOutput && k === 'stdout') || (!isOutput && (k === 'code' || k === 'content' || k === 'sections'));
      break;
    }
  }

  // If no primary field found, show status summary for output
  if (!text && isOutput) {
    text = _formatStatusFields(null); // can't parse Python repr generically, show placeholder
  }

  // Fallback: strip the dict wrapper
  if (!text) {
    text = rawText.replace(/^\{'?/, '').replace(/'?\}$/, '').replace(/\\n/g, '\n');
  }

  return text ? {text: text, isCode: isCode} : null;
}

// Extract a single field value from Python repr string: 'key': 'value'
function _extractPythonField(rawText, key) {
  var re = new RegExp("'" + key + "':\\s*'((?:[^'\\\\]|\\\\.)*)'");
  var m = rawText.match(re);
  if (m) {
    return m[1].replace(/\\n/g, '\n').replace(/\\t/g, '\t').replace(/\\r/g, '').replace(/\\'/g, "'").replace(/\\\\/g, '\\');
  }
  return null;
}

// Format status/auxiliary fields
function _formatStatusFields(data) {
  var fields = [];
  // Walk known keys in display order
  var knownKeys = ['status','file_path','paper_path','docx_path','chart_path','chart_type',
                   'title','count','row_count','record_count','round_num','round',
                   'format','sources_found','fetched_count','images_embedded','exit_code'];
  if (data) {
    for (var i = 0; i < knownKeys.length; i++) {
      var k = knownKeys[i];
      var v = data[k];
      if (v !== undefined && v !== null) {
        var label = k.replace(/_/g, ' ');
        if (typeof v === 'number') fields.push(label + ': ' + v);
        else if (typeof v === 'string') fields.push(label + ': ' + (v.length > 100 ? v.substring(0,100)+'...' : v));
        else fields.push(label + ': ' + JSON.stringify(v).substring(0, 80));
      }
    }
  }
  return fields.length > 0 ? fields.join('\n') : (data ? JSON.stringify(data).substring(0, 500) : '');
}

function _extractStreamContent(toolName, rawText) {
  // Extract clean human-readable content from streaming partial JSON.
  // Uses a "find the opening quote" approach — much more robust than
  // regex matching on partial/incomplete JSON strings.
  var keys = _toolContentKeys[toolName];
  if (!keys) {
    // Unknown tool — just strip JSON noise and show raw text
    return rawText.replace(/^[{"'\s]+/, '').replace(/\\n/g, '\n').substring(0, 2000);
  }

  var primaryKey = keys[0];
  // Look for the JSON key opening:  "key": "
  var openPattern = '"' + primaryKey + '": "';
  var startIdx = rawText.indexOf(openPattern);

  if (startIdx !== -1) {
    // Extract everything after the opening marker
    var inner = rawText.substring(startIdx + openPattern.length);
    // Apply JSON unescaping as we go (supports streaming display)
    inner = inner.replace(/\\n/g, '\n').replace(/\\t/g, '\t')
                 .replace(/\\r/g, '\r').replace(/\\"/g, '"')
                 .replace(/\\\\/g, '\\');
    // Trim trailing JSON closers that may have arrived
    // (during streaming these are partial; after streaming they're complete)
    inner = inner.replace(/"?\s*\}?\s*$/, '');
    var limit = (primaryKey === 'code' || primaryKey === 'content' || primaryKey === 'sections') ? 10000 : 2000;
    return inner.substring(0, limit);
  }

  // Key not found yet (JSON hasn't opened that field) —
  // show a minimal version stripped of JSON punctuation
  var cleaned = rawText.replace(/^[{"'\s]+/, '').replace(/\\n/g, '\n');
  return cleaned.substring(0, 2000);
}

// Tool name → Chinese display name
var _toolNameCN = {
  'execute_code': '执行代码',       'write_file': '写入文件',
  'write_paper': '撰写论文',        'search_literature': '搜索文献',
  'analyze_data': '分析数据',       'generate_chart': '生成图表',
  'record_experiment': '记录实验',  'report_iteration': '报告迭代',
  'read_file': '读取文件',          'delete_file': '删除文件',
  'fetch_url': '抓取网页',          'deep_research': '深度研究',
  'thinking': 'Agent 思考'
};

function handleToolCallChunk(toolName, chunk) {
  // If switching to a different tool, finalize previous
  if (_toolCallActive && _toolCallName !== toolName) {
    upgradeStreamCard();
  }

  var container = getLogContainer();
  if (!container) return;
  var welcome = container.querySelector('.log-welcome, .chat-welcome');
  if (welcome) welcome.remove();

  updateAgentStatus('executing', toolName);

  if (!_toolCallActive) {
    _toolCallActive = true;
    _toolCallName = toolName;
    _toolCallText = '';
    _toolCallEl = document.createElement('div');
    _toolCallEl.className = 'toolcall-stream';
    var label = _toolLabels[toolName] || toolName;
    _toolCallEl.innerHTML =
      '<div class="toolcall-header">' +
        '<span class="toolcall-spin"></span>' +
        '<span class="toolcall-label">' + escapeHtml(label) + '</span>' +
      '</div>' +
      '<div class="toolcall-body"><pre></pre></div>';
    container.appendChild(_toolCallEl);
  }

  _toolCallText += chunk;
  var body = _toolCallEl.querySelector('.toolcall-body pre');
  if (body) {
    body.textContent = _extractStreamContent(toolName, _toolCallText);
  }

  if (LOG_AUTO_SCROLL) scrollLogToBottom();
}

// ── Upgrade streaming card → formal log card (NEW) ──
function upgradeStreamCard() {
  if (!_toolCallActive || !_toolCallEl) return;
  _toolCallActive = false;
  var toolName = _toolCallName;
  var streamText = _toolCallText;
  _toolCallName = '';
  _toolCallText = '';
  var el = _toolCallEl;
  _toolCallEl = null;

  if (!streamText.trim()) { el.remove(); return; }

  // Try to parse the final accumulated JSON for a clean args string
  var argsStr = '';
  var contentPreview = '';
  try {
    var parsed = JSON.parse(streamText);
    // Build a short args preview from key fields
    var previewParts = [];
    var keys = _toolContentKeys[toolName] || [];
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      var v = parsed[k];
      if (v !== undefined && v !== null) {
        if (typeof v === 'string') {
          previewParts.push(k + '=' + (v.length > 60 ? v.substring(0, 60) + '...' : v));
        } else if (typeof v === 'object') {
          previewParts.push(k + '={...}');
        } else {
          previewParts.push(k + '=' + v);
        }
      }
    }
    argsStr = previewParts.join(', ') || JSON.stringify(parsed).substring(0, 120);
    contentPreview = _extractStreamContent(toolName, streamText);
  } catch(e) {
    argsStr = streamText.substring(0, 120);
    contentPreview = _extractStreamContent(toolName, streamText);
  }

  var now = new Date();
  var shortTime = ('0' + now.getHours()).slice(-2) + ':' +
                  ('0' + now.getMinutes()).slice(-2) + ':' +
                  ('0' + now.getSeconds()).slice(-2);
  var cnName = _toolNameCN[toolName] || toolName;

  // Transform the streaming card into a formal log-tool-card IN PLACE
  el.className = 'log-tool-card';
  el.dataset.filter = 'tool';
  el.dataset.saved = '0'; // mark for upgrade-search (below)
  el.dataset.fromWs = '1';  // backend already persists via _on_tool_start — skip in saveCurrentLogs
  el.dataset.raw = '[' + shortTime + '] [TOOL] ' + toolName + ' | ' + argsStr;
  el.innerHTML =
    '<div class="log-tool-header" onclick="this.parentElement.classList.toggle(\'expanded\')">' +
      '<span class="log-tool-icon">&#x1f527;</span>' +
      '<span class="log-tool-name">' + escapeHtml(cnName) + '</span>' +
      '<span class="log-tool-eng-name">' + escapeHtml(toolName) + '</span>' +
      '<span class="log-tool-args">' + escapeHtml(argsStr) + '</span>' +
      '<span class="log-tool-time">' + shortTime + '</span>' +
      '<span class="log-tool-chevron">&#x25b6;</span>' +
    '</div>' +
    '<div class="log-tool-body">' +
      '<div class="log-tool-result"><pre>' + escapeHtml(contentPreview) + '</pre></div>' +
    '</div>';

  updateLogCount();
  if (LOG_AUTO_SCROLL) scrollLogToBottom();
}

// Keep finalizeToolCallCard as a simple alias for backward compat
function finalizeToolCallCard() {
  upgradeStreamCard();
}

// ── Agent status indicator ──
function updateAgentStatus(status, toolName) {
  var dot = document.getElementById('status-indicator');
  var text = document.getElementById('status-text');
  if (!dot || !text) return;

  dot.className = 'status-dot ' + status;
  switch (status) {
    case 'thinking':
      text.textContent = '思考中...';
      break;
    case 'executing':
      var label = _toolLabels[toolName] || toolName;
      text.textContent = label + '...';
      break;
    case 'idle':
      dot.className = 'status-dot idle';
      text.textContent = '就绪';
      break;
    case 'done':
      dot.className = 'status-dot done';
      text.textContent = '完成';
      break;
    default:
      text.textContent = status;
  }
}

function finalizeThinking() {
  if (!_thinkingActive || !_thinkingEl) return;
  _thinkingActive = false;

  var text = _thinkingText.trim();
  _thinkingText = '';
  var el = _thinkingEl;
  _thinkingEl = null;

  if (!text) { el.remove(); return; }

  // Convert to a collapsible thinking card
  el.className = 'log-tool-card thinking-card expanded';
  el.dataset.filter = 'info';
  el.dataset.fromWs = '1';  // backend now persists thinking to DB — skip in saveCurrentLogs
  el.innerHTML =
    '<div class="log-tool-header thinking-card-header" onclick="this.parentElement.classList.toggle(\'expanded\')">' +
      '<span class="log-tool-icon">&#x1f4ad;</span>' +
      '<span class="log-tool-name thinking-name">Agent 思考</span>' +
      '<span class="log-tool-eng-name">' + text.length + ' chars</span>' +
      '<span class="log-tool-chevron">&#x25b6;</span>' +
    '</div>' +
    '<div class="log-tool-body">' +
      '<div class="log-tool-result thinking-result">' + escapeHtml(text) + '</div>' +
    '</div>';

  // Apply active filter
  if (LOG_ACTIVE_FILTER !== 'all') applyLogFilter(el);
  updateLogCount();
}

// ── Token usage display ──
function initTokenDisplay() {
  var logActions = document.querySelector('.log-actions');
  if (!logActions) return;
  var el = document.getElementById('token-usage-display');
  if (!el) {
    el = document.createElement('div');
    el.id = 'token-usage-display';
    el.className = 'token-usage-display';
    logActions.appendChild(el);
  }
  el.innerHTML = '<span class="token-item token-placeholder">TOKEN --</span>';
}

function updateTokenUsage(data) {
  var el = document.getElementById('token-usage-display');
  if (!el) return;

  var promptK = (data.prompt_tokens / 1000).toFixed(1);
  var compK = (data.completion_tokens / 1000).toFixed(1);
  var totalK = (data.total_tokens / 1000).toFixed(1);

  var html = '';
  html += '<span class="token-item" title="输入 Token"><span class="token-label">IN</span>' + promptK + 'K</span>';
  html += '<span class="token-item" title="输出 Token"><span class="token-label">OUT</span>' + compK + 'K</span>';
  html += '<span class="token-item" title="总计 Token"><span class="token-label">合计</span>' + totalK + 'K</span>';
  el.innerHTML = html;
}

function scrollLogToBottom() {
  var container = getLogContainer();
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

function updateLogCount() {
  var container = getLogContainer();
  var countEl = document.getElementById('log-line-count');
  if (countEl && container) {
    var visible = container.querySelectorAll('.log-entry:not(.filtered-hidden), .log-tool-card:not(.filtered-hidden), .log-separator:not(.filtered-hidden)').length;
    countEl.textContent = visible + ' / ' + LOG_TOTAL_LINES + ' 行';
  }
}

// ── Filtering ──
function applyLogFilter(el) {
  if (LOG_ACTIVE_FILTER === 'all') {
    el.classList.remove('filtered-hidden');
  } else {
    var f = el.dataset.filter;
    if (f === LOG_ACTIVE_FILTER || (LOG_ACTIVE_FILTER === 'highlight' && f === 'highlight')) {
      el.classList.remove('filtered-hidden');
    } else {
      el.classList.add('filtered-hidden');
    }
  }
}

function setLogFilter(filter) {
  LOG_ACTIVE_FILTER = filter;
  var container = getLogContainer();
  if (!container) return;

  // Update filter button states
  document.querySelectorAll('.log-filter-btn').forEach(function(btn) {
    btn.classList.toggle('active', btn.dataset.filter === filter);
  });

  // Apply filter to all entries
  var entries = container.querySelectorAll('.log-entry, .log-tool-card, .log-separator, .thinking-bubble');
  for (var i = 0; i < entries.length; i++) {
    applyLogFilter(entries[i]);
  }
  updateLogCount();
}

// ── Auto-scroll ──
function toggleAutoScroll() {
  LOG_AUTO_SCROLL = !LOG_AUTO_SCROLL;
  var btn = document.getElementById('log-autoscroll-btn');
  if (btn) {
    btn.classList.toggle('active', LOG_AUTO_SCROLL);
    btn.title = LOG_AUTO_SCROLL ? '自动滚动: 开' : '自动滚动: 关';
  }
  if (LOG_AUTO_SCROLL) scrollLogToBottom();
}

// ── Pause auto-scroll on manual scroll up ──
function initLogScrollDetection() {
  var container = getLogContainer();
  if (!container) return;
  container.addEventListener('scroll', function() {
    var atBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 40;
    if (!atBottom && LOG_AUTO_SCROLL) {
      LOG_AUTO_SCROLL = false;
      var btn = document.getElementById('log-autoscroll-btn');
      if (btn) { btn.classList.remove('active'); btn.title = '自动滚动: 关'; }
    } else if (atBottom && !LOG_AUTO_SCROLL) {
      LOG_AUTO_SCROLL = true;
      var btn = document.getElementById('log-autoscroll-btn');
      if (btn) { btn.classList.add('active'); btn.title = '自动滚动: 开'; }
    }
  });
}

function initLogFilters() {
  document.querySelectorAll('.log-filter-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      setLogFilter(btn.dataset.filter);
    });
  });
}

async function clearLog() {
  if (!await showConfirm('清空日志', '确定要清空当前所有日志吗？', '确定清空', false)) return;
  var container = getLogContainer();
  if (container) {
    container.innerHTML = '<div class="log-welcome"><div class="log-welcome-icon">' + ICONS.logo + '</div><div class="log-welcome-text">MolCraft Research Agent Ready</div><div class="log-welcome-hint">Enter a research goal and click Start</div></div>';
  }
  _inToolOutput = false;
  _thinkingActive = false; _thinkingText = ''; _thinkingEl = null;
  _toolCallActive = false; _toolCallName = ''; _toolCallText = ''; _toolCallEl = null;
  _lastToolName = '';
  updateAgentStatus('idle');
  LOG_TOTAL_LINES = 0;
  updateLogCount();
  if (activeConvId) {
    api('/api/conversations/' + activeConvId, { method: 'PUT', body: JSON.stringify({clear_logs: true}) }).catch(function(){});
  }
}


// ===== CONVERSATIONS =====
async function loadConversations() {
  try {
    var data = await api('/api/conversations');
    var list = document.getElementById('conv-list');
    if (!list) return;

    var html = '';
    var convs = Array.isArray(data) ? data : (data.conversations || []);
    for (var i = 0; i < convs.length; i++) {
      var c = convs[i];
      var isActive = c.id === activeConvId && STATE.currentPage === 'studio';
      var title = escapeHtml(c.title || c.id);
      var count = c.log_count || 0;
      var time = c.updated_at ? timeAgo(c.updated_at) : '';
      html += '<div class="conv-item' + (isActive ? ' active' : '') + '" onclick="selectConv(\'' + c.id + '\')">';
      html += '<span class="conv-icon">' + (isActive ? ICONS.chatActive : ICONS.chat) + '</span>';
      html += '<div class="conv-info"><div class="conv-title" title="' + title + '">' + title + '</div>';
      html += '<div class="conv-meta">' + time + (time && count > 0 ? ' \u00b7 ' : '') + (count > 0 ? count + ' \u6761\u6d88\u606f' : '') + '</div></div>';
      html += '<button class="conv-menu-btn" onclick="event.stopPropagation();toggleConvMenu(event,\'' + c.id + '\',\'' + escHtml(title) + '\')" title="\u66f4\u591a">' + ICONS.more + '</button>';
      html += '<div class="conv-dropdown" id="conv-menu-' + c.id + '">';
      html += '<div class="conv-dropdown-item" onclick="event.stopPropagation();renameConv(\'' + c.id + '\')">' + ICONS.edit + ' \u7f16\u8f91\u540d\u79f0</div>';
      html += '<div class="conv-dropdown-item" onclick="event.stopPropagation();clearConvLogs(\'' + c.id + '\')">' + ICONS.refresh + ' \u6e05\u7a7a\u5185\u5bb9</div>';
      html += '<div class="conv-dropdown-item conv-dropdown-danger" onclick="event.stopPropagation();delConv(\'' + c.id + '\')">' + ICONS.trash + ' \u5220\u9664\u5bf9\u8bdd</div>';
      html += '</div>';
      html += '</div>';
    }
    list.innerHTML = html || '<div class="empty-state" style="padding:16px;text-align:center;color:var(--text-muted);font-size:0.8rem;">No conversations</div>';
  } catch(e) { console.error('loadConversations:', e); }
}

async function newConversation() {
  try {
    var data = await api('/api/conversations', { method: 'POST', body: JSON.stringify({goal:'',title:'New Conversation'}) });
    await loadConversations();
    await selectConv(data.id);
  } catch(e) { toast('Failed: ' + e.message, 'error'); }
}

async function selectConv(convId) {
  if (convId === activeConvId && STATE.currentPage === 'studio') return;
  // Finalize active thinking bubble, then persist DOM entries to server.
  // saveCurrentLogs uses append (not PUT) so it won't overwrite server logs.
  if (_thinkingActive) finalizeThinking();
  await saveCurrentLogs();
  navigateTo('studio');
  try {
    var conv = await api('/api/conversations/' + convId);
    activeConvId = convId;
    var goalInput = document.getElementById('studio-goal');
    if (goalInput) goalInput.value = conv.goal || '';
    var dashGoal = document.getElementById('dash-goal');
    if (dashGoal) dashGoal.value = conv.goal || '';

    var container = getLogContainer();
    if (container) {
      // Fade out
      container.classList.add('fading');
      await new Promise(function(r) { setTimeout(r, 200); });
      _inToolOutput = false;
      _thinkingActive = false; _thinkingText = ''; _thinkingEl = null;
      LOG_TOTAL_LINES = 0;
      LOG_ACTIVE_FILTER = 'all';
      document.querySelectorAll('.log-filter-btn').forEach(function(b) {
        b.classList.toggle('active', b.dataset.filter === 'all');
      });

      // Start with welcome; addLogLine will remove it when logs arrive
      container.innerHTML = '<div class="log-welcome"><div class="log-welcome-icon">' + ICONS.logo + '</div><div class="log-welcome-text">MolCraft Research Agent Ready</div><div class="log-welcome-hint">Enter a research goal and click Start</div></div>';
      var logs = conv.logs || [];
      var start = Math.max(0, logs.length - 500);
      // Batch render: set flag so addLogLine won't mark these as WS entries
      var wasAutoScroll = LOG_AUTO_SCROLL;
      LOG_AUTO_SCROLL = false;
      _renderingSaved = true;
      var maxSeq = -1;
      var _seenContent = {};
      for (var i = start; i < logs.length; i++) {
        var logItem = logs[i];
        var content = typeof logItem === 'string' ? logItem : (logItem.content || '');
        // Skip duplicates (from saveCurrentLogs race with _db_log or duplicate writes)
        // Use a hash map — more robust than consecutive-only dedup
        if (_seenContent[content]) continue;
        _seenContent[content] = true;
        var seq = logItem.seq || 0;
        if (seq > maxSeq) maxSeq = seq;
        addLogLine(content);
      }
      _lastLogSeq = maxSeq;  // prevent polling from re-adding loaded logs
      _renderingSaved = false;
      LOG_AUTO_SCROLL = wasAutoScroll;
      // Mark all loaded entries as already saved to prevent duplicate appends later
      var allEntries = container.querySelectorAll('.log-entry, .log-tool-card, .log-separator');
      for (var j = 0; j < allEntries.length; j++) {
        allEntries[j].dataset.saved = '1';
      }
      updateLogCount();
      if (LOG_AUTO_SCROLL) scrollLogToBottom();
      // Fade back in
      container.classList.remove('fading');
    }
    // Restore saved token usage
    if (conv.token_usage && conv.token_usage.total_tokens > 0) {
      updateTokenUsage(conv.token_usage);
    } else {
      initTokenDisplay();
    }
    await loadConversations();
    STATE.logLines = [];
  } catch(e) { toast('Load failed: ' + e.message, 'error'); }
}

// Save ALL DOM entries in their natural display order (tool cards, thinking cards,
// separators, and regular log lines all interleaved).  Uses append_log per entry
// so the server-side array preserves the same chronological order.
async function saveCurrentLogs() {
  if (!activeConvId) return;
  var container = getLogContainer();
  if (!container) return;

  var entries = container.querySelectorAll('.log-entry, .log-tool-card, .log-separator');
  for (var i = 0; i < entries.length; i++) {
    var el = entries[i];
    // Already persisted (loaded from DB, or arrived via WS which writes to DB)
    if (el.dataset.saved === '1' || el.dataset.fromWs === '1') continue;
    var isThinkingCard = el.classList.contains('thinking-card');

    // Use the raw log text if available (matches backend format exactly,
    // making server-side deduplication effective).  Fall back to DOM
    // reconstruction for entries without raw text (e.g. thinking cards).
    var text = el.dataset.raw || '';
    if (!text) {
      if (el.classList.contains('log-tool-card')) {
        if (isThinkingCard) {
          var thinkResult = el.querySelector('.thinking-result');
          if (thinkResult) {
            var thinkText = thinkResult.textContent.trim();
            if (thinkText) text = '[THINKING] ' + thinkText;
          }
        } else {
          var engName = el.querySelector('.log-tool-eng-name');
          var args = el.querySelector('.log-tool-args');
          var time = el.querySelector('.log-tool-time');
          text = '[TOOL] ' + (engName ? engName.textContent.trim() : '?') + ' | ' + (args ? args.textContent.trim() : '');
          if (time) text = '[' + time.textContent.trim() + '] ' + text;
        }
      } else if (el.classList.contains('log-separator')) {
        var label = el.querySelector('.log-separator-label');
        text = '========== ' + (label ? label.textContent.trim() : '') + ' ==========';
      } else {
        var time = el.querySelector('.log-time');
        var msg = el.querySelector('.log-msg');
        text = (time ? '[' + time.textContent.trim() + '] ' : '') + (msg ? msg.textContent.trim() : el.textContent.trim());
      }
    }

    if (!text.trim()) continue;

    try {
      await api('/api/conversations/' + activeConvId + '/append_log', {
        method: 'POST',
        body: JSON.stringify({ log: text })
      });
      el.dataset.saved = '1';
    } catch(e) { /* non-critical */ }
  }
}

function escHtml(s) {
  return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function showConfirm(title, message, confirmLabel, isDanger) {
  return new Promise(function(resolve) {
    var overlay = document.createElement('div');
    overlay.className = 'confirm-overlay';
    overlay.innerHTML =
      '<div class="confirm-dialog">' +
      '<h3>' + title + '</h3>' +
      '<p>' + message + '</p>' +
      '<div class="confirm-dialog-btns">' +
      '<button class="confirm-dialog-btn" id="confirm-cancel">取消</button>' +
      '<button class="confirm-dialog-btn' + (isDanger ? ' danger' : ' primary') + '" id="confirm-ok">' + confirmLabel + '</button>' +
      '</div></div>';
    document.body.appendChild(overlay);

    function cleanup() { overlay.remove(); }

    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) { cleanup(); resolve(false); }
    });
    overlay.querySelector('#confirm-cancel').addEventListener('click', function() {
      cleanup(); resolve(false);
    });
    overlay.querySelector('#confirm-ok').addEventListener('click', function() {
      cleanup(); resolve(true);
    });
    // Auto-focus confirm button
    setTimeout(function() {
      var okBtn = overlay.querySelector('#confirm-ok');
      if (okBtn) okBtn.focus();
    }, 50);
  });
}

function toggleConvMenu(e, convId, title) {
  var menu = document.getElementById('conv-menu-' + convId);
  if (!menu) return;
  var isOpen = menu.classList.contains('open');
  // Close all other open menus
  document.querySelectorAll('.conv-dropdown.open').forEach(function(m) {
    m.classList.remove('open');
  });
  if (!isOpen) {
    menu.classList.add('open');
    var btn = e.target.closest('.conv-menu-btn');
    var rect = btn.getBoundingClientRect();
    menu.style.top = (rect.top - 4) + 'px';
    menu.style.left = (rect.right + 6) + 'px';
  }
}

function startInlineEdit(convId, titleEl) {
  var input = document.createElement('input');
  input.type = 'text';
  input.className = 'conv-title-input';
  input.value = titleEl.textContent;
  var titleDiv = titleEl;
  titleEl.replaceWith(input);
  input.focus();
  input.select();

  var saving = false;
  async function save() {
    if (saving) return; saving = true;
    var name = input.value.trim();
    if (!name) name = 'Untitled';
    input.replaceWith(titleDiv);
    titleDiv.textContent = name;
    try {
      await api('/api/conversations/' + convId, { method: 'PUT', body: JSON.stringify({title: name}) });
      toast('已重命名', 'success');
    } catch(e) { toast('重命名失败: ' + e.message, 'error'); }
  }
  function cancel() {
    input.replaceWith(titleDiv);
  }
  input.addEventListener('blur', save);
  input.addEventListener('keydown', function(ev) {
    if (ev.key === 'Enter') { ev.preventDefault(); input.blur(); }
    if (ev.key === 'Escape') { ev.preventDefault(); cancel(); }
  });
}

async function renameConv(convId) {
  // Find the conv-item containing this dropdown
  var menu = document.getElementById('conv-menu-' + convId);
  if (!menu) return;
  var convItem = menu.closest('.conv-item');
  // Close all dropdowns
  document.querySelectorAll('.conv-dropdown.open').forEach(function(m) { m.classList.remove('open'); });
  if (!convItem) return;
  var titleEl = convItem.querySelector('.conv-title');
  if (!titleEl) return;
  startInlineEdit(convId, titleEl);
}

async function clearConvLogs(convId) {
  var ok = await showConfirm('清空对话内容', '将删除该对话的所有日志和消息，此操作不可撤销。', '确定清空', false);
  if (!ok) return;
  try {
    await api('/api/conversations/' + convId, { method: 'PUT', body: JSON.stringify({clear_logs: true}) });
    if (activeConvId === convId) {
      var container = getLogContainer();
      if (container) container.innerHTML = '<div class="log-welcome"><div class="log-welcome-icon">' + ICONS.logo + '</div><div class="log-welcome-text">MolCraft Research Agent Ready</div><div class="log-welcome-hint">Enter a research goal and click Start</div></div>';
      var countEl = document.getElementById('log-line-count'); if (countEl) countEl.textContent = '0 lines';
    }
    await loadConversations();
    toast('已清空', 'success');
  } catch(e) { toast('清空失败: ' + e.message, 'error'); }
}

async function delConv(convId) {
  var ok = await showConfirm('删除对话', '确定要删除该对话吗？删除后无法恢复。', '确定删除', true);
  if (!ok) return;
  try {
    await api('/api/conversations/' + convId, { method: 'DELETE' });
    if (activeConvId === convId) {
      activeConvId = null;
      var container = getLogContainer();
      if (container) container.innerHTML = '<div class="log-welcome"><div class="log-welcome-icon">' + ICONS.logo + '</div><div class="log-welcome-text">MolCraft Research Agent Ready</div><div class="log-welcome-hint">Enter a research goal and click Start</div></div>';
      var goalInput = document.getElementById('studio-goal'); if (goalInput) goalInput.value = '';
      var dashGoal = document.getElementById('dash-goal'); if (dashGoal) dashGoal.value = '';
      var countEl = document.getElementById('log-line-count'); if (countEl) countEl.textContent = '0 lines';
    }
    await loadConversations();
    toast('Deleted', 'success');
  } catch(e) { toast('Delete failed: ' + e.message, 'error'); }
}

// ===== DASHBOARD =====
async function loadDashboard() {
  if (!isLoggedIn()) return;
  try {
    var expData = await api('/api/experiments');
    var chartData = await api('/api/charts');
    var records = expData.records || [];
    var summary = expData.summary || {};
    var charts = Array.isArray(chartData) ? chartData : (chartData.charts || []);

    var se = document.getElementById('stat-experiments'); if (se) se.textContent = records.length;
    var sc = document.getElementById('stat-confirmed'); if (sc) sc.textContent = summary.confirmed || 0;
    var sr = document.getElementById('stat-rejected'); if (sr) sr.textContent = summary.rejected || 0;
    var sch = document.getElementById('stat-charts'); if (sch) sch.textContent = charts.length;

    var recentEl = document.getElementById('recent-activity');
    if (recentEl) {
      if (records.length === 0) {
        recentEl.innerHTML = '<div class="empty-state">No activity</div>';
      } else {
        var html = '';
        var recent = records.slice(-5).reverse();
        for (var i = 0; i < recent.length; i++) {
          var r = recent[i];
          html += '<div class="activity-item"><span class="activity-icon">' + (r.confirmed ? '\u2705' : '\u23f3') + '</span>';
          html += '<div class="activity-info"><div class="activity-title">' + escapeHtml(r.goal || r.iteration || '') + '</div>';
          html += '<div class="activity-meta">' + (r.timestamp ? timeAgo(r.timestamp) : '') + '</div></div></div>';
        }
        recentEl.innerHTML = html;
      }
    }

    STATE.experiments = records;
    STATE.charts = charts;
    updateExpBadge(records.length);
    updateChartBadge();
  } catch(e) { console.error('loadDashboard:', e); }
}

async function startAgentFromDash() {
  var goalEl = document.getElementById('dash-goal');
  if (goalEl) {
    navigateTo('studio');
    var sg = document.getElementById('studio-goal');
    if (sg && goalEl.value.trim()) sg.value = goalEl.value.trim();
  }
  await startAgent();
}

// ===== AGENT START / STOP =====
async function startAgent() {
  var baseUrl = document.getElementById('setting-base-url');
  var apiKey = document.getElementById('setting-api-key');
  var model = document.getElementById('setting-model');
  var goalEl = document.getElementById('studio-goal');

  var url = baseUrl ? baseUrl.value.trim() : '';
  var key = apiKey ? apiKey.value.trim() : '';
  var mdl = model ? model.value.trim() : '';
  var goal = goalEl ? goalEl.value.trim() : '';

  // key may be empty because it's stored encrypted on server — check config
  var keyConfigured = (document.getElementById('api-key-configured')||{}).value === '1';
  var missing = [];
  if (!url) missing.push('API Base URL');
  if (!key && !keyConfigured) missing.push('API Key');
  if (!mdl) missing.push('Model');
  if (!goal) missing.push('Research Goal');
  if (missing.length > 0) { toast('Missing: ' + missing.join(', '), 'error'); return; }

  // Let the backend own conversation creation — avoids frontend/backend
  // race conditions that produce duplicate conversation files.
  // Pass activeConvId so the backend can reuse an existing conversation;
  // if none is active, the backend creates one and returns its ID.

  var iterations = parseInt(document.getElementById('iterations-input').value) || 3;
  var minutes = parseInt(document.getElementById('minutes-input').value) || 90;
  var writePaper = document.getElementById('write-paper-toggle');
  var wp = writePaper ? writePaper.checked : false;

  var container = getLogContainer();
  if (container) {
    var welcome = container.querySelector('.log-welcome, .chat-welcome');
    if (welcome) welcome.remove();
  }

  // Ensure settings are persisted before starting (system_prompt especially)
  await saveSettingsSilent();

  var systemPrompt = (document.getElementById('setting-prompt') || {}).value || '';

  try {
    var resp = await api('/api/agent/start', {
      method: 'POST',
      body: JSON.stringify({
        api_key: key, base_url: url, model: mdl, goal: goal,
        max_iterations: iterations, max_minutes: minutes,
        write_paper: wp, conv_id: activeConvId || null,
        system_prompt: systemPrompt
      })
    });
    // Sync conversation ID from backend
    if (resp.conversation_id) {
      if (resp.conversation_id !== activeConvId) {
        activeConvId = resp.conversation_id;
        await loadConversations();
      }
    }
    // Update UI immediately
    STATE.agentRunning = true;
    _lastLogSeq = -1;  // reset log polling for new run
    updateStatus({running: true, current_iteration: 0, total_iterations: iterations});
    // Reset token usage display
    var tokenEl = document.getElementById('token-usage-display');
    if (tokenEl) tokenEl.innerHTML = '<span class="token-item" style="color:var(--text-muted)">' + ICONS.spinner + ' 统计中...</span>';
    toast('Experiment started', 'success');
  } catch(e) { toast('Start failed: ' + e.message, 'error'); }
}

var _stopFallbackTimer = null;
var _lastLogSeq = -1;  // track last seen log sequence number for polling

async function pollAgentLogs() {
  if (!isLoggedIn()) return;
  if (!STATE.agentRunning || !activeConvId) return;
  try {
    var resp = await apiFetch('/api/conversations/' + activeConvId);
    if (!resp.ok) return;
    var conv = await resp.json();
    var logs = conv.logs || [];
    if (logs.length === 0) return;

    // Only add new logs (beyond _lastLogSeq)
    var container = getLogContainer();
    if (!container) return;

    for (var i = 0; i < logs.length; i++) {
      if (logs[i].seq > _lastLogSeq) {
        _lastLogSeq = logs[i].seq;
        var line = typeof logs[i] === 'string' ? logs[i] : (logs[i].content || '');
        addLogLine(line);
      }
    }
  } catch(e) {}
}

async function stopAgent() {
  try {
    await api('/api/agent/stop', { method: 'POST' });
    // Show "stopping" state — button will be restored when WS status arrives
    var sd = document.getElementById('studio-stop-btn');
    if (sd) { sd.disabled = true; sd.innerHTML = ICONS.spinner; }
    var dd = document.getElementById('dash-stop-btn');
    if (dd) { dd.disabled = true; dd.innerHTML = ICONS.spinner; }
    // Fallback: force button restore if WS status doesn't arrive in 15s
    clearTimeout(_stopFallbackTimer);
    _stopFallbackTimer = setTimeout(function() {
      if (STATE.agentRunning) {
        STATE.agentRunning = false;
        updateStatus({running: false, current_iteration: 0, total_iterations: 0});
      }
    }, 15000);
  } catch(e) { toast('Stop failed: ' + e.message, 'error'); }
}

function clearStudioGoal() {
  var el = document.getElementById('studio-goal');
  if (el) el.value = '';
}


// ===== EXPERIMENTS =====
async function loadExperiments() {
  try {
    var data = await api('/api/experiments');
    var records = data.records || [];
    STATE.experiments = records;
    renderExperiments(records);
    updateExpBadge(records.length);
  } catch(e) { console.error('loadExperiments:', e); }
}

function renderExperiments(records) {
  var container = document.getElementById('experiments-list');
  if (!container) return;
  // Update summary
  var summaryEl = document.getElementById('experiments-summary');
  if (summaryEl) {
    var len = records ? records.length : 0;
    var conf = records ? records.filter(function(r){return r.confirmed;}).length : 0;
    summaryEl.innerHTML = '<div class="stat-card"><div class="stat-icon">' + ICONS.flask + '</div><div class="stat-info"><span class="stat-value">' + len + '</span><span class="stat-label">\u5b9e\u9a8c\u8f6e\u6b21</span></div></div>' +
      '<div class="stat-card"><div class="stat-icon">' + ICONS.check + '</div><div class="stat-info"><span class="stat-value">' + conf + '</span><span class="stat-label">\u9a8c\u8bc1\u901a\u8fc7</span></div></div>' +
      '<div class="stat-card"><div class="stat-icon">' + ICONS.xmark + '</div><div class="stat-info"><span class="stat-value">' + (len - conf) + '</span><span class="stat-label">\u9a8c\u8bc1\u9a73\u56de</span></div></div>';
  }
  if (!records || records.length === 0) {
    container.innerHTML = '<div class="empty-state" style="text-align:center;padding:40px;color:var(--text-muted);">\u6682\u65e0\u5b9e\u9a8c\u8bb0\u5f55</div>';
    return;
  }
  var html = '';
  for (var i = 0; i < records.length; i++) {
    var r = records[i];
    var isConfirmed = r.confirmed;
    var metrics = r.metrics || {};
    var metricKeys = Object.keys(metrics);
    html += '<div class="exp-item"><div class="exp-header" onclick="toggleExp(this)">';
    html += '<span class="exp-status ' + (isConfirmed ? 'confirmed' : 'rejected') + '"></span>';
    html += '<span class="exp-title">' + escapeHtml(r.hypothesis || r.goal || r.iteration || '\u7b2c ' + (i+1) + ' \u8f6e\u5b9e\u9a8c') + '</span>';
    if (metricKeys.length > 0) {
      html += '<span class="exp-metric-tag">' + escapeHtml(metricKeys[0]) + '<span class="val">' + escapeHtml(String(metrics[metricKeys[0]])) + '</span></span>';
    }
    html += '<span class="exp-round">#' + (r.round || i + 1) + '</span>';
    html += '<span class="exp-chevron">&#x25b6;</span></div>';
    html += '<div class="exp-body">';
    html += '<div class="exp-body-grid">';
    html += '<div class="exp-field"><div class="exp-field-label">\u72b6\u6001</div><div class="exp-field-value">' + (isConfirmed ? '\u2705 \u9a8c\u8bc1\u901a\u8fc7' : '\u274c \u9a8c\u8bc1\u9a73\u56de') + '</div></div>';
    html += '<div class="exp-field"><div class="exp-field-label">\u8fed\u4ee3</div><div class="exp-field-value">' + escapeHtml(r.iteration || '\u7b2c ' + (i+1) + ' \u8f6e') + '</div></div>';
    if (r.timestamp) html += '<div class="exp-field"><div class="exp-field-label">\u65f6\u95f4</div><div class="exp-field-value">' + escapeHtml(r.timestamp) + '</div></div>';
    html += '</div>';
    if (metricKeys.length > 0) {
      html += '<div class="exp-field-label" style="margin-bottom:6px;">\u6307\u6807</div><div class="exp-metrics-row">';
      for (var k = 0; k < metricKeys.length; k++) {
        var mk = metricKeys[k];
        html += '<span class="exp-metric-tag">' + escapeHtml(mk) + '<span class="val">' + escapeHtml(String(metrics[mk])) + '</span></span>';
      }
      html += '</div>';
    }
    if (r.conclusion || r.summary) {
      html += '<div class="exp-field-label" style="margin-top:10px;margin-bottom:4px;">\u7ed3\u8bba</div>';
      html += '<div class="exp-field-value">' + escapeHtml(r.conclusion || r.summary || '') + '</div>';
    }
    html += '</div></div>';
  }
  container.innerHTML = html;
  // Update badges
  updateExpBadge(records.length);
}

function toggleExp(el) {
  el.parentElement.classList.toggle('open');
}

function updateExpBadge(count) {
  ['exp-badge', 'exp-badge-top'].forEach(function(id) {
    var b = document.getElementById(id);
    if (b) { b.textContent = count > 99 ? '99+' : count; b.style.display = count ? '' : 'none'; }
  });
}

async function exportExperiments() {
  try {
    var data = await api('/api/experiments/export');
    var blob = new Blob([data.markdown], {type: 'text/markdown'});
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'experiments_report.md'; a.click(); URL.revokeObjectURL(a.href);
    toast('Exported', 'success');
  } catch(e) { toast('No experiments to export', 'info'); }
}

async function clearExperiments() {
  if (!await showConfirm('清空实验记录', '确定要清空所有实验记录吗？此操作不可撤销。', '确定清空', false)) return;
  try {
    await api('/api/experiments/clear', { method: 'POST' });
    STATE.experiments = [];
    renderExperiments([]);
    updateExpBadge(0);
    toast('Cleared', 'success');
  } catch(e) { toast('Clear failed: ' + e.message, 'error'); }
}

// ===== CHARTS =====
function renderCharts() {
  var grid = document.getElementById('charts-grid');
  if (!grid) return;
  var charts = STATE.charts || [];
  if (charts.length === 0) {
    grid.innerHTML = '<div class="empty-state">No charts generated yet</div>';
    return;
  }
  var html = '';
  for (var i = 0; i < charts.length; i++) {
    var c = charts[i];
    html += '<div class="chart-card">';
    var tokenParam = AUTH.token ? '?token=' + AUTH.token : '';
    html += '<img class="chart-image" src="/api/charts/' + encodeURIComponent(c.name) + tokenParam + '" alt="' + escapeHtml(c.name) + '" onclick="viewChart(\'' + escapeHtml(c.name) + '\')" style="max-height:200px;width:100%;object-fit:contain;cursor:pointer;" loading="lazy" />';
    html += '<div class="chart-info"><span class="chart-name">' + escapeHtml(c.name) + '</span>';
    html += '<div class="chart-actions">';
    html += '<button class="btn btn-small btn-secondary" onclick="downloadFile(\'charts\',\'' + escapeHtml(c.name) + '\')">Download</button>';
    html += '<button class="btn btn-small btn-danger-outline" onclick="deleteFile(\'charts\',\'' + escapeHtml(c.name) + '\')">Delete</button>';
    html += '</div></div></div>';
  }
  grid.innerHTML = html;
}

function viewChart(name) {
  var modal = document.getElementById('modal-overlay');
  var body = document.getElementById('modal-body');
  if (!modal || !body) return;
  var tokenParam = AUTH.token ? '?token=' + AUTH.token : '';
  body.innerHTML = '<img src="/api/charts/' + encodeURIComponent(name) + tokenParam + '" style="max-width:100%;max-height:80vh;" />';
  modal.style.display = 'flex';
}

function updateChartBadge() {
  var count = STATE.charts ? STATE.charts.length : 0;
  ['chart-badge', 'chart-badge-top'].forEach(function(id) {
    var b = document.getElementById(id);
    if (b) { b.textContent = count > 99 ? '99+' : count; b.style.display = count ? '' : 'none'; }
  });
}

// ===== FILES =====
async function loadFiles() {
  try {
    var data = await api('/api/files');
    STATE.files = Array.isArray(data) ? data : (data.files || []);
    renderFiles();
  } catch(e) { console.error('loadFiles:', e); }
}

function renderFiles() {
  var filesCont = document.getElementById('files-container');
  var papersCont = document.getElementById('papers-container');
  var files = STATE.files || [];

  // Count files per category for tab labels + nav badge
  var counts = { all: 0, data: 0, scripts: 0, papers: 0 };
  files.forEach(function(f) { if (f.type !== 'charts') { counts.all++; counts[f.type] = (counts[f.type] || 0) + 1; } });
  var fb = document.getElementById('file-badge-top');
  if (fb) { fb.textContent = counts.all > 99 ? '99+' : counts.all; fb.style.display = counts.all > 0 ? '' : 'none'; }

  // Update tab labels with counts
  var tabs = document.querySelectorAll('.file-filter-tab');
  tabs.forEach(function(t) {
    var cat = t.dataset.cat;
    var count = counts[cat] || 0;
    // Remove old count span if exists, then append new one
    var old = t.querySelector('.tab-count');
    if (old) old.remove();
    var span = document.createElement('span');
    span.className = 'tab-count';
    span.textContent = ' ' + (count > 99 ? '99+' : count);
    t.appendChild(span);
  });

  // Get active filter
  var activeTab = document.querySelector('.file-filter-tab.active');
  var activeCat = activeTab ? activeTab.dataset.cat : 'all';
  var searchQuery = (document.getElementById('file-search-input') || {}).value || '';

  // Filter by category (exclude charts — they have their own page)
  var filtered = files.filter(function(f) {
    if (f.type === 'charts') return false;
    if (activeCat === 'all') return true;
    if (activeCat === 'data') return f.type === 'data';
    if (activeCat === 'scripts') return f.type === 'scripts';
    if (activeCat === 'papers') return f.type === 'papers';
    return true;
  });

  // Filter by search
  if (searchQuery) {
    var q = searchQuery.toLowerCase();
    filtered = filtered.filter(function(f) { return f.name.toLowerCase().indexOf(q) >= 0; });
  }

  if (filesCont) {
    if (filtered.length === 0) {
      filesCont.innerHTML = '<div class="empty-state" style="text-align:center;padding:40px;color:var(--text-muted);">' +
        (searchQuery ? '\u6ca1\u6709\u5339\u914d "' + escapeHtml(searchQuery) + '" \u7684\u6587\u4ef6' : '\u6682\u65e0\u6587\u4ef6') + '</div>';
    } else {
      var html = '';
      html += '<div class="batch-bar" id="batch-bar">';
      html += '<span id="batch-count">\u5df2\u9009 0 \u9879</span>';
      html += '<button class="btn btn-small btn-danger-outline" onclick="batchDeleteFiles()">\u6279\u91cf\u5220\u9664</button>';
      html += '<button class="btn btn-small btn-secondary" onclick="clearFileSelection()">\u53d6\u6d88\u9009\u62e9</button>';
      html += '</div>';
      for (var j = 0; j < filtered.length; j++) {
        var f = filtered[j];
        var typeIcon = fileIcon(f.name);
        var typeLabel = f.type === 'charts' ? '\u56fe\u8868' : f.type === 'scripts' ? '\u811a\u672c' : f.type === 'papers' ? '\u8bba\u6587' : '\u6570\u636e';
        html += '<div class="file-item" id="file-item-' + j + '">';
        html += '<label class="file-check"><input type="checkbox" onchange="onFileCheck()" data-idx="' + j + '" data-type="' + f.type + '" data-name="' + escapeHtml(f.name) + '" /></label>';
        html += '<span class="file-type-icon">' + typeIcon + '</span>';
        html += '<div class="file-info"><span class="file-name">' + escapeHtml(f.name) + '</span>';
        html += '<span class="file-meta"><span class="file-type-tag">' + typeLabel + '</span>' + (f.size ? ' \u00b7 ' + formatSize(f.size) : '') + (f.modified ? ' \u00b7 ' + timeAgo(f.modified) : '') + '</span></div>';
        html += '<div class="file-actions">';
        if (f.type !== 'papers') html += '<button class="btn btn-small btn-secondary" onclick="viewFile(\'' + f.type + '\',\'' + escapeHtml(f.name) + '\')">\u67e5\u770b</button>';
        html += '<button class="btn btn-small btn-secondary" onclick="downloadFile(\'' + f.type + '\',\'' + escapeHtml(f.name) + '\')">\u4e0b\u8f7d</button>';
        html += '<button class="btn btn-small btn-danger-outline" onclick="deleteFile(\'' + f.type + '\',\'' + escapeHtml(f.name) + '\')">\u5220\u9664</button>';
        html += '</div></div>';
      }
      filesCont.innerHTML = html;
    }
  }
}

function viewFile(type, name) {
  var modal = document.getElementById('modal-overlay');
  var body = document.getElementById('modal-body');
  if (!modal || !body) return;

  var tokenParam = AUTH.token ? '?token=' + AUTH.token : '';
  var ext = name.split('.').pop().toLowerCase();
  if (['png','jpg','jpeg','gif','svg','webp'].indexOf(ext) >= 0) {
    body.innerHTML = '<img src="/api/files/' + type + '/' + name + tokenParam + '" style="max-width:100%;max-height:80vh;" />';
  } else if (['pdf'].indexOf(ext) >= 0) {
    body.innerHTML = '<iframe src="/api/files/' + type + '/' + name + tokenParam + '" style="width:100%;height:80vh;border:none;"></iframe>';
  } else {
    apiFetch('/api/files/' + type + '/' + name)
      .then(function(r){ return r.text(); })
      .then(function(txt){
        body.innerHTML = '<pre style="max-height:80vh;overflow:auto;padding:16px;background:var(--bg-input);border-radius:8px;font-family:var(--font-mono);font-size:0.85rem;white-space:pre-wrap;">' + escapeHtml(txt) + '</pre>';
      })
      .catch(function(){ body.innerHTML = '<p>Failed to load file</p>'; });
  }
  modal.style.display = 'flex';
}

function closeModal() {
  var modal = document.getElementById('modal-overlay');
  if (modal) modal.style.display = 'none';
}

async function downloadFile(type, name) {
  try {
    var resp = await apiFetch('/api/files/' + type + '/' + name + '/download');
    var blob = await resp.blob();
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; a.click(); URL.revokeObjectURL(a.href);
  } catch(e) { toast('Download failed', 'error'); }
}

function onFileCheck() {
  var checked = document.querySelectorAll('.file-check input:checked');
  var bar = document.getElementById('batch-bar');
  var countEl = document.getElementById('batch-count');
  if (bar) bar.classList.toggle('show', checked.length > 0);
  if (countEl) countEl.textContent = '已选 ' + checked.length + ' 项';
}

function clearFileSelection() {
  document.querySelectorAll('.file-check input').forEach(function(cb) { cb.checked = false; });
  onFileCheck();
}

async function batchDeleteFiles() {
  var checked = document.querySelectorAll('.file-check input:checked');
  if (checked.length === 0) return;
  if (!await showConfirm('批量删除', '确定要删除选中的 ' + checked.length + ' 个文件吗？此操作不可撤销。', '确定删除', true)) return;
  var total = checked.length;
  var done = 0;
  for (var i = 0; i < checked.length; i++) {
    var cb = checked[i];
    try {
      await api('/api/files/' + cb.dataset.type + '/' + cb.dataset.name, { method: 'DELETE' });
      done++;
    } catch(e) { /* skip failed */ }
  }
  await loadFiles();
  toast('已删除 ' + done + '/' + total + ' 个文件', done === total ? 'success' : 'error');
}

async function deleteFile(type, name) {
  if (!await showConfirm('删除文件', '确定要删除 "' + name + '" 吗？', '确定删除', true)) return;
  try {
    await api('/api/files/' + type + '/' + name, { method: 'DELETE' });
    await loadFiles();
    if (type === 'charts') {
      var data = await api('/api/charts');
      STATE.charts = Array.isArray(data) ? data : (data.charts || []);
      renderCharts();
    }
    toast('Deleted', 'success');
  } catch(e) { toast('Delete failed', 'error'); }
}

// ===== FILE UPLOAD =====
function initDropZone() {
  var dropZone = document.getElementById('drop-zone');
  if (!dropZone) return;

  ['dragenter','dragover'].forEach(function(evt){
    dropZone.addEventListener(evt, function(e){
      e.preventDefault(); e.stopPropagation();
      dropZone.classList.add('drag-over');
    });
  });

  ['dragleave','drop'].forEach(function(evt){
    dropZone.addEventListener(evt, function(e){
      e.preventDefault(); e.stopPropagation();
      dropZone.classList.remove('drag-over');
    });
  });

  dropZone.addEventListener('drop', function(e){
    var files = e.dataTransfer.files;
    if (files.length > 0) uploadFilesDirect(files);
  });
}

function uploadFiles(input) {
  if (input.files && input.files.length > 0) uploadFilesDirect(input.files);
}

function uploadChatFiles(input) {
  uploadFiles(input);
  input.value = '';
}

async function uploadFilesDirect(fileList) {
  var dropZone = document.getElementById('drop-zone');
  var total = fileList.length;
  var done = 0;

  for (var i = 0; i < total; i++) {
    var file = fileList[i];
    if (dropZone) {
      dropZone.classList.add('drop-zone-uploading');
      dropZone.querySelector('.drop-zone-text').textContent = 'Uploading ' + file.name + ' (' + (i+1) + '/' + total + ')...';
    }
    try {
      var formData = new FormData();
      formData.append('file', file);
      await apiFetch('/api/files/upload', { method: 'POST', body: formData });
      done++;
    } catch(e) {
      toast('Upload failed: ' + file.name, 'error');
    }
  }

  if (dropZone) {
    dropZone.classList.remove('drop-zone-uploading');
    dropZone.querySelector('.drop-zone-text').textContent = 'Drag files here to upload';
  }
  toast('Uploaded ' + done + '/' + total + ' files', done === total ? 'success' : 'error');
  await loadFiles();
}

// ===== SETTINGS =====
async function loadSettings() {
  try {
    var config = await api('/api/config');
    // API fields: server returns empty, use in-memory cache to survive page switches
    var bs = document.getElementById('setting-base-url');
    if (bs) bs.value = bs.value.trim() || _apiSettingsCache.base_url || '';
    var ak = document.getElementById('setting-api-key');
    if (ak) {
      if (!ak.value.trim()) { ak.value = _apiSettingsCache.api_key || ''; ak.dataset.masked = '0'; }
    }
    var akc = document.getElementById('api-key-configured'); if (akc) akc.value = '0';
    var md = document.getElementById('setting-model');
    if (md) md.value = md.value.trim() || _apiSettingsCache.model || '';
    // Non-API fields always load from server
    var tp = document.getElementById('setting-temperature');
    if (tp) { tp.value = config.temperature || 0.3; var tv = document.getElementById('temp-value'); if (tv) tv.textContent = config.temperature || 0.3; }
    var sp = document.getElementById('setting-prompt'); if (sp) sp.value = config.system_prompt || '';
    var it = document.getElementById('iterations-input'); if (it) it.value = config.max_iterations || 3;
    var mm = document.getElementById('minutes-input'); if (mm) mm.value = config.max_minutes || 90;
    var th = document.getElementById('setting-theme');
    if (th) { var t = localStorage.getItem('molcraft-theme') || 'codex'; if (t === 'codex') { document.documentElement.removeAttribute('data-theme'); } else { document.documentElement.setAttribute('data-theme', t); } th.value = t === 'clean' ? '极简白' : 'Codex 暗色 (默认)'; }
  } catch(e) {}
}

async function saveSettings() {
  try {
    await doSaveSettings();
    toast('Settings saved', 'success');
  } catch(e) { toast('Save failed: ' + e.message, 'error'); }
}

async function saveSettingsSilent() {
  try { await doSaveSettings(); } catch(e) {}
}

async function doSaveSettings() {
  var apiKeyInput = document.getElementById('setting-api-key');
  // If key is masked placeholder (already configured), don't overwrite with dummy text
  var apiKeyValue = (apiKeyInput && apiKeyInput.dataset.masked === '1') ? '' : (apiKeyInput ? apiKeyInput.value.trim() : '');
  var config = {
    base_url: document.getElementById('setting-base-url').value.trim(),
    api_key: apiKeyValue,
    model: document.getElementById('setting-model').value.trim(),
    temperature: parseFloat(document.getElementById('setting-temperature').value),
    system_prompt: document.getElementById('setting-prompt').value.trim(),
    max_iterations: parseInt(document.getElementById('iterations-input').value),
    max_minutes: parseInt(document.getElementById('minutes-input').value)
  };
  // Update in-memory cache so values survive page switches
  _apiSettingsCache.base_url = config.base_url;
  _apiSettingsCache.api_key = config.api_key;
  _apiSettingsCache.model = config.model;
  await api('/api/config', { method: 'POST', body: JSON.stringify(config) });
}

var _settingsSaveTimer = null;
function autoSaveSettings() {
  clearTimeout(_settingsSaveTimer);
  _settingsSaveTimer = setTimeout(saveSettingsSilent, 600);
}

// Auto-save research goal to existing conversation (debounced 800ms)
var _goalSaveTimer = null;
async function saveGoalSilent() {
  if (!activeConvId) return;
  var goalEl = document.getElementById('studio-goal');
  if (!goalEl) return;
  var goal = goalEl.value.trim();
  if (!goal) return;
  try {
    await api('/api/conversations/' + activeConvId, {
      method: 'PUT',
      body: JSON.stringify({ goal: goal, title: goal.substring(0, 100) })
    });
  } catch(e) {}
}

// ===== RESIZERS =====
function initSidebarResizer() {
  var resizer = document.getElementById('sidebar-resizer');
  var sidebar = document.getElementById('sidebar');
  if (!resizer || !sidebar) return;
  var startX, startW;
  function onMove(e) { var w = startW + (e.clientX - startX); if (w < 180) w = 180; if (w > 500) w = 500; sidebar.style.width = w + 'px'; }
  function onUp() {
    resizer.classList.remove('active'); document.body.style.cursor = ''; document.body.style.userSelect = '';
    document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp);
    try { localStorage.setItem('molcraft_sw', sidebar.style.width); } catch(e) {}
  }
  resizer.addEventListener('mousedown', function(e) {
    e.preventDefault(); startX = e.clientX; startW = sidebar.offsetWidth;
    resizer.classList.add('active'); document.body.style.cursor = 'ew-resize'; document.body.style.userSelect = 'none';
    document.addEventListener('mousemove', onMove); document.addEventListener('mouseup', onUp);
  });
  try { var s = localStorage.getItem('molcraft_sw'); if (s) sidebar.style.width = s; } catch(e) {}
}

function initConvResizer() {
  var resizer = document.getElementById('conv-resizer');
  var convList = document.getElementById('conv-list');
  if (!resizer || !convList) return;
  var startY, startH;
  function onMove(e) { var h = startH + (startY - e.clientY); if (h < 60) h = 60; if (h > window.innerHeight - 150) h = window.innerHeight - 150; convList.style.maxHeight = h + 'px'; convList.style.height = h + 'px'; }
  function onUp() {
    resizer.classList.remove('active'); document.body.style.cursor = ''; document.body.style.userSelect = '';
    document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp);
    try { localStorage.setItem('molcraft_ch', convList.style.height); } catch(e) {}
  }
  resizer.addEventListener('mousedown', function(e) {
    e.preventDefault(); startY = e.clientY; startH = convList.offsetHeight;
    resizer.classList.add('active'); document.body.style.cursor = 'ns-resize'; document.body.style.userSelect = 'none';
    document.addEventListener('mousemove', onMove); document.addEventListener('mouseup', onUp);
  });
  try { var s = localStorage.getItem('molcraft_ch'); if (s) { convList.style.maxHeight = s; convList.style.height = s; } } catch(e) {}
}

function initStudioResizer() {
  var resizer = document.getElementById('studio-resizer');
  var studioInput = document.querySelector('.studio-input');
  var studioLog = document.querySelector('.studio-log');
  if (!resizer || !studioInput || !studioLog) return;
  var startY, startH;
  function onMove(e) { var h = startH + (e.clientY - startY); if (h < 100) h = 100; if (h > window.innerHeight - 250) h = window.innerHeight - 250; studioInput.style.flex = 'none'; studioInput.style.height = h + 'px'; }
  function onUp() {
    resizer.classList.remove('active'); document.body.style.cursor = ''; document.body.style.userSelect = '';
    document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp);
    try { localStorage.setItem('molcraft_studio_h', studioInput.style.height); } catch(e) {}
  }
  resizer.addEventListener('mousedown', function(e) {
    e.preventDefault(); startY = e.clientY; startH = studioInput.offsetHeight;
    resizer.classList.add('active'); document.body.style.cursor = 'ns-resize'; document.body.style.userSelect = 'none';
    document.addEventListener('mousemove', onMove); document.addEventListener('mouseup', onUp);
  });
  try { var s = localStorage.getItem('molcraft_studio_h'); if (s) { studioInput.style.flex = 'none'; studioInput.style.height = s; } } catch(e) {}
}

// ===== UTILITIES =====
function escapeHtml(text) {
  var d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

function timeAgo(isoStr) {
  try {
    if (!isoStr) return '';
    // Normalize: replace space with T, append Z if no timezone
    var normalized = isoStr.replace(' ', 'T');
    if (!/[+-]\d{2}:\d{2}$/.test(normalized) && !normalized.endsWith('Z')) {
      normalized += 'Z';
    }
    var diff = Date.now() - new Date(normalized).getTime();
    if (isNaN(diff) || diff < 0) return '';
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前';
    if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前';
    if (diff < 604800000) return Math.floor(diff / 86400000) + '天前';
    // Older than 7 days: show date
    var d = new Date(normalized);
    return (d.getMonth() + 1) + '/' + d.getDate();
  } catch(e) { return ''; }
}

function formatSize(bytes) {
  if (!bytes) return '';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1048576).toFixed(1) + ' MB';
}

// ===== LANDING / APP TRANSITIONS =====
// ═══════════════════════════════════════════
//  GSAP Scroll-Driven Landing Animations
// ═══════════════════════════════════════════
function initScrollAnimations() {
  // Fallback: show cards if GSAP not available
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
    document.querySelectorAll('.bento-card, .process-card, .cta-card').forEach(function(el) {
      el.style.visibility = 'visible';
    });
    return;
  }

  // Mobile: cards visible immediately, no animations
  if (window.innerWidth <= 768) {
    document.querySelectorAll('.bento-card, .process-card, .cta-card').forEach(function(el) {
      el.classList.add('gsap-ready');
    });
    return;
  }

  // Mark all cards visible so GSAP can animate them
  document.querySelectorAll('.bento-card, .process-card, .cta-card').forEach(function(el) {
    el.classList.add('gsap-ready');
  });

  // ══════════════════════════════════════
  //  SECTION 1: Bento Cards — center burst
  // ══════════════════════════════════════
  var bentoCards = gsap.utils.toArray('.bento-card');
  var mainCard = document.querySelector('.bento-main');

  if (bentoCards.length && mainCard) {
    var nonMainCards = bentoCards.filter(function(c) { return !c.classList.contains('bento-main'); });

    // All cards start invisible & scaled down
    gsap.set(bentoCards, { opacity: 0, scale: 0.6 });

    var tlBento = gsap.timeline({
      scrollTrigger: {
        trigger: '#features',
        start: 'top 80%',
        scroller: '#landing-page',
        once: true
      }
    });

    // Phase 1: Main card scales up first
    tlBento.to(mainCard, {
      opacity: 1, scale: 1, duration: 0.5,
      ease: 'back.out(1.4)'
    }, 0);

    // Phase 2: Child cards burst out with stagger
    tlBento.to(nonMainCards, {
      opacity: 1, scale: 1, duration: 0.55,
      ease: 'back.out(1.4)',
      stagger: 0.07
    }, 0.15);

    // Phase 3: Main card glow pulse
    tlBento.to(mainCard, {
      animation: 'bentoGlowPulse 1.5s ease-out forwards',
      duration: 1.5
    }, 0.3);

    // Phase 4: Icon bounce stagger
    var icons = document.querySelectorAll('.bento-card .bento-icon');
    tlBento.to(icons, {
      scale: 1.18, duration: 0.22, ease: 'back.out(2)',
      stagger: 0.04
    }, 0.5);
    tlBento.to(icons, {
      scale: 1, duration: 0.35, ease: 'power2.in',
      stagger: 0.04
    }, 0.72);
  }

  // ══════════════════════════════════════
  //  SECTION 2: Process Cards — circuit chain
  // ══════════════════════════════════════
  var processCards = gsap.utils.toArray('.process-card');
  var processArrows = document.querySelectorAll('.process-arrow');

  if (processCards.length >= 3) {
    gsap.set(processCards, { opacity: 0 });
    gsap.set(processArrows, { opacity: 0, scaleX: 0, transformOrigin: 'center center' });

    var tlProcess = gsap.timeline({
      scrollTrigger: {
        trigger: '#process',
        start: 'top 75%',
        scroller: '#landing-page',
        once: true
      }
    });

    // Card 1 — slide in from left
    gsap.set(processCards[0], { x: -30 });
    tlProcess.to(processCards[0], {
      opacity: 1, x: 0, duration: 0.5, ease: 'power3.out'
    }, 0);

    // Arrow 1 — expand
    if (processArrows[0]) {
      tlProcess.to(processArrows[0], {
        opacity: 1, scaleX: 1, duration: 0.35, ease: 'power2.inOut'
      }, 0.15);
    }

    // Card 2 — pop up from below
    gsap.set(processCards[1], { y: 30 });
    tlProcess.to(processCards[1], {
      opacity: 1, y: 0, duration: 0.5, ease: 'power3.out'
    }, 0.25);

    // Number color shift on card 2
    var num2 = processCards[1] ? processCards[1].querySelector('.process-num') : null;
    if (num2) {
      tlProcess.to(num2, { color: 'var(--laccent)', duration: 0.5, ease: 'power2.out' }, 0.3);
    }

    // Arrow 2 — expand
    if (processArrows[1]) {
      tlProcess.to(processArrows[1], {
        opacity: 1, scaleX: 1, duration: 0.35, ease: 'power2.inOut'
      }, 0.4);
    }

    // Card 3 — slide in from right
    gsap.set(processCards[2], { x: 30 });
    tlProcess.to(processCards[2], {
      opacity: 1, x: 0, duration: 0.5, ease: 'power3.out'
    }, 0.5);
  }

  // ══════════════════════════════════════
  //  SECTION 3: CTA — envelope reveal
  // ══════════════════════════════════════
  var ctaCard = document.querySelector('.cta-card');
  var ctaButtons = document.querySelectorAll('.cta-btn-primary, .cta-btn-ghost');

  if (ctaCard) {
    gsap.set(ctaCard, { opacity: 0, scale: 0.92 });

    var tlCta = gsap.timeline({
      scrollTrigger: {
        trigger: '#cta',
        start: 'top 85%',
        scroller: '#landing-page',
        once: true
      }
    });

    // Card reveal
    tlCta.to(ctaCard, {
      opacity: 1, scale: 1, duration: 0.6, ease: 'power2.out'
    }, 0);

    // Buttons float up
    if (ctaButtons.length) {
      gsap.set(ctaButtons, { y: 10, opacity: 0 });
      tlCta.to(ctaButtons, {
        y: 0, opacity: 1, duration: 0.4, ease: 'power2.out',
        stagger: 0.1
      }, 0.25);
    }

    // Glow bar scan
    var glowBar = document.createElement('div');
    glowBar.className = 'cta-glow-bar';
    ctaCard.appendChild(glowBar);
    tlCta.to(glowBar, {
      left: '200%', duration: 0.8, ease: 'power2.inOut',
      onComplete: function() { glowBar.remove(); }
    }, 0.45);
  }

  // Refresh ScrollTrigger after all timelines created
  ScrollTrigger.refresh();
}

function showLanding() {
  if (!isLoggedIn()) { showAuth('login'); return; }
  var landing = document.getElementById('landing-page');
  var app = document.getElementById('app');
  if (landing) { landing.style.display = ''; landing.scrollTop = 0; landing.style.opacity = '1'; }
  if (app) { app.style.display = 'none'; app.classList.remove('fading'); }
}

function enterApp() {
  if (!isLoggedIn()) { showAuth('login'); return; }
  // Prevent duplicate setup
  if (window._dashInterval) clearInterval(window._dashInterval);
  if (window._logPollInterval) clearInterval(window._logPollInterval);
  if (ws) { try { ws.close(); } catch(e) {} ws = null; }
  var landing = document.getElementById('landing-page');
  var app = document.getElementById('app');
  // Fade out landing
  if (landing) {
    landing.style.transition = 'opacity 0.35s ease';
    landing.style.opacity = '0';
    setTimeout(function() { landing.style.display = 'none'; landing.style.opacity = '1'; }, 350);
  }
  // Show app with fade in, page content delayed 0.2s
  if (app) {
    app.style.display = 'flex';
    app.classList.add('fading');
    var studioPage = document.getElementById('page-studio');
    if (studioPage) { studioPage.style.opacity = '0'; studioPage.style.transition = 'opacity 0.35s ease'; }
    requestAnimationFrame(function() {
      requestAnimationFrame(function() {
        app.classList.remove('fading');
        setTimeout(function() {
          if (studioPage) {
            studioPage.style.opacity = '1';
            setTimeout(function() { studioPage.style.transition = ''; studioPage.style.opacity = ''; }, 400);
          }
        }, 200);
      });
    });
    var activePage = document.querySelector('.page.active');
    if (activePage) {
      activePage.style.animation = 'none';
      activePage.offsetHeight;
      activePage.style.animation = '';
    }
  }
  // Always start at studio on login
  window.location.hash = 'studio';
  navigateTo('studio');
  loadDashboard();
  loadConversations();
  initConvResizer();
  initSidebarResizer();
  initStudioResizer();
  initLogFilters();
  initLogScrollDetection();
  connectWebSocket();
  window._dashInterval = setInterval(loadDashboard, 5000);
  window._logPollInterval = setInterval(pollAgentLogs, 2000);
}

function returnToLanding() {
  var landing = document.getElementById('landing-page');
  var app = document.getElementById('app');
  saveCurrentLogs();
  // Fade out entire app (including top nav, conv panel, etc.)
  if (app) {
    app.classList.add('fading');
    setTimeout(function() {
      app.style.display = 'none';
      app.classList.remove('fading');
    }, 400);
  }
  // Show landing at top, fade in
  if (landing) {
    landing.scrollTop = 0;
    landing.style.display = '';
    landing.style.opacity = '0';
    landing.style.transition = 'opacity 0.5s ease';
    requestAnimationFrame(function() {
      requestAnimationFrame(function() {
        landing.style.opacity = '1';
      });
    });
  }
}

// ===== MODAL & DROPDOWN CLICK-OUTSIDE =====
document.addEventListener('click', function(e) {
  var modal = document.getElementById('modal-overlay');
  if (modal && e.target === modal) closeModal();
  // Close conv dropdown menus when clicking outside
  if (!e.target.closest('.conv-menu-btn') && !e.target.closest('.conv-dropdown')) {
    document.querySelectorAll('.conv-dropdown.open').forEach(function(m) { m.classList.remove('open'); });
  }
});

// ===== CUSTOM DROPDOWN =====
function toggleDropdown(id) {
  var list = document.getElementById(id);
  if (!list) return;
  var isOpen = list.classList.contains('open');

  // Close all dropdowns first (with caret reset)
  document.querySelectorAll('.dropdown-list.open').forEach(function(el) {
    el.classList.remove('open');
    var caret = el.parentElement.querySelector('.dd-caret');
    if (caret) {
      if (typeof gsap !== 'undefined') gsap.to(caret, { rotate: 0, duration: 0.2, ease: 'power2.out' });
      else caret.style.transform = '';
    }
  });

  if (isOpen) return;

  // Position the dropdown below the input element
  var input = list.parentElement.querySelector('input');
  if (input) {
    var rect = input.getBoundingClientRect();
    list.style.top = (rect.bottom + 2) + 'px';
    list.style.left = rect.left + 'px';
    list.style.width = rect.width + 'px';
  }
  list.classList.add('open');

  // Animate caret rotation
  var caret = list.parentElement.querySelector('.dd-caret');
  if (caret) {
    if (typeof gsap !== 'undefined') gsap.to(caret, { rotate: 180, duration: 0.2, ease: 'power2.out' });
    else caret.style.transform = 'rotate(180deg)';
  }
}

function selectDropdown(inputId, li) {
  var input = document.getElementById(inputId);
  if (input) {
    input.value = li.dataset.value;
    input.dispatchEvent(new Event('input'));
  }
  var list = li.parentElement;
  list.classList.remove('open');
  // Reset caret
  var caret = list.parentElement.querySelector('.dd-caret');
  if (caret) {
    if (typeof gsap !== 'undefined') gsap.to(caret, { rotate: 0, duration: 0.2, ease: 'power2.out' });
    else caret.style.transform = '';
  }
}

function selectTheme(li) {
  var value = li.dataset.value;
  var input = document.getElementById('setting-theme');
  var themeLabels = { codex: 'Codex 暗色 (默认)', clean: '极简白' };

  // Update input display
  if (input) input.value = themeLabels[value] || value;

  // Apply theme
  if (value === 'codex') {
    document.documentElement.removeAttribute('data-theme');
  } else {
    document.documentElement.setAttribute('data-theme', value);
  }
  localStorage.setItem('molcraft-theme', value);

  // Close dropdown
  li.parentElement.classList.remove('open');
  // Reset caret via toggleDropdown logic
  var caret = li.parentElement.parentElement.querySelector('.dd-caret');
  if (caret) {
    if (typeof gsap !== 'undefined') gsap.to(caret, { rotate: 0, duration: 0.2, ease: 'power2.out' });
    else caret.style.transform = '';
  }
}

function updateModelDropdown() {
  var urlInput = document.getElementById('setting-base-url');
  var modelList = document.getElementById('model-dropdown');
  if (!urlInput || !modelList) return;

  var url = urlInput.value.toLowerCase();
  var matched = null;
  for (var domain in URL_MODELS) {
    if (url.indexOf(domain) >= 0) { matched = URL_MODELS[domain]; break; }
  }

  modelList.innerHTML = '';
  var models = matched || [];
  if (!matched) {
    for (var d in URL_MODELS) { models = models.concat(URL_MODELS[d]); }
  }
  for (var i = 0; i < models.length; i++) {
    var li = document.createElement('li');
    li.dataset.value = models[i];
    li.setAttribute('onclick', "selectDropdown('setting-model', this)");
    li.textContent = models[i];
    modelList.appendChild(li);
  }
}

