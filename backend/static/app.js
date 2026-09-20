/* ============================================================
   RPHMS — shared frontend logic v2
   Plain JS, no build step. Uses fetch() against the FastAPI backend.
   ============================================================ */

const API_BASE = ""; // same origin - FastAPI serves both API and these static files

// ---------- Auth / session ----------

function getToken() {
  return localStorage.getItem("rphms_token");
}

function getUserName() {
  return localStorage.getItem("rphms_user") || "Provider";
}

function setSession(token, name) {
  localStorage.setItem("rphms_token", token);
  localStorage.setItem("rphms_user", name);
}

function clearSession() {
  localStorage.removeItem("rphms_token");
  localStorage.removeItem("rphms_user");
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = "/";
  }
}

function logout() {
  clearSession();
  window.location.href = "/";
}

// ---------- API helper ----------

async function apiRequest(path, options = {}) {
  const headers = options.headers || {};
  headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) headers["Authorization"] = "Bearer " + token;

  const response = await fetch(API_BASE + path, { ...options, headers });

  // A 401 on the login endpoint just means "wrong credentials" - let the
  // caller handle and display that. A 401 on any other endpoint means our
  // session token is invalid/expired, so force back to the login page.
  if (response.status === 401 && path !== "/api/login") {
    clearSession();
    window.location.href = "/";
    throw new Error("Session expired");
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message = (data && data.detail) ? data.detail : "Request failed";
    throw new Error(message);
  }

  return data;
}

// ---------- Formatting helpers ----------

function formatVital(value, unit) {
  if (value === null || value === undefined) {
    return `<span class="mono">—</span>`;
  }
  return `<span class="vital-value">${value}<span class="unit">${unit}</span></span>`;
}

function statusBadge(status) {
  const labels = { normal: "Normal", warning: "Warning", critical: "Critical" };
  const label = labels[status] || "Unknown";
  return `<span class="badge ${status}">${label}</span>`;
}

function deviceStatusHtml(isOnline) {
  return `<span class="device-status ${isOnline ? "online" : ""}">
    <span class="dot"></span>${isOnline ? "Online" : "Offline"}
  </span>`;
}

function timeAgo(isoString) {
  if (!isoString) return "No data yet";
  const then = new Date(isoString + (isoString.endsWith("Z") ? "" : "Z"));
  const seconds = Math.floor((Date.now() - then.getTime()) / 1000);
  if (seconds < 5) return "just now";
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return then.toLocaleDateString();
}

function formatDateTime(isoString) {
  if (!isoString) return "—";
  const d = new Date(isoString + (isoString.endsWith("Z") ? "" : "Z"));
  return d.toLocaleString(undefined, {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function initials(name) {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/);
  return (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
}

// ---------- Count-up animation for stat tiles ----------

function animateCount(el, target) {
  const start = parseInt(el.dataset.count || "0", 10);
  target = parseInt(target, 10) || 0;
  if (start === target) { el.textContent = target; return; }

  const duration = 450;
  const startTime = performance.now();

  function step(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = Math.round(start + (target - start) * eased);
    el.textContent = value;
    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      el.dataset.count = target;
    }
  }
  requestAnimationFrame(step);
}

// ---------- Icon set (inline SVG, no external icon font/library needed) ----------

const ICONS = {
  logo: `<svg viewBox="0 0 24 24" fill="none"><path d="M3 12h4l2-7 4 14 2-7h6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  dashboard: `<svg class="icon" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>`,
  alerts: `<svg class="icon" viewBox="0 0 24 24"><path d="M12 3v1M12 20v1M4.2 4.2l.7.7M19.1 19.1l.7.7M3 12h1M20 12h1M4.2 19.8l.7-.7M19.1 4.9l.7-.7"/><circle cx="12" cy="12" r="4"/></svg>`,
  users: `<svg class="icon" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" transform="translate(3 -1)"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
  wifi: `<svg class="icon" viewBox="0 0 24 24"><path d="M5 12.5a11 11 0 0 1 14 0"/><path d="M8.5 16a6 6 0 0 1 7 0"/><path d="M2 9a15.5 15.5 0 0 1 20 0"/><circle cx="12" cy="19" r="1" fill="currentColor" stroke="none"/></svg>`,
  check: `<svg class="icon" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>`,
  alertTriangle: `<svg class="icon" viewBox="0 0 24 24"><path d="M10.3 3.9L2 19h20L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>`,
  heart: `<svg class="icon" viewBox="0 0 24 24"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>`,
  droplet: `<svg class="icon" viewBox="0 0 24 24"><path d="M12 2s7 8 7 13a7 7 0 0 1-14 0c0-5 7-13 7-13z"/></svg>`,
  thermometer: `<svg class="icon" viewBox="0 0 24 24"><path d="M14 4a2 2 0 0 0-4 0v10.5a4 4 0 1 0 4 0V4z"/></svg>`,
  bell: `<svg class="icon" viewBox="0 0 24 24" fill="none"><path d="M6 8a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M9.5 18a2.5 2.5 0 0 0 5 0" stroke-width="1.8" stroke-linecap="round"/></svg>`,
  sparkles: `<svg class="icon" viewBox="0 0 24 24" fill="none"><path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z" stroke-width="1.6" stroke-linejoin="round"/><path d="M19 15l.7 2.1L22 18l-2.3.9L19 21l-.7-2.1L16 18l2.3-.9L19 15z" stroke-width="1.4" stroke-linejoin="round"/></svg>`,
  close: `<svg class="icon" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke-width="1.8" stroke-linecap="round"/></svg>`,
  send: `<svg class="icon" viewBox="0 0 24 24" fill="none"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  inbox: `<svg class="icon" viewBox="0 0 24 24" fill="none"><path d="M22 12h-6l-2 3h-4l-2-3H2" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M5.5 5h13l2.5 7v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-6l2.5-7z" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  info: `<svg class="icon" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke-width="1.6"/><path d="M12 16v-4M12 8h.01" stroke-width="1.8" stroke-linecap="round"/></svg>`,
};

function icon(name) {
  return ICONS[name] || "";
}

/* ============================================================
   ADVANCED UI HELPERS
   Theme, toasts, alert sound, small formatting utilities.
   ============================================================ */

// ---------- Theme (light / dark) ----------

function getTheme() {
  return localStorage.getItem("rphms_theme") || "light";
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("rphms_theme", theme);
  const btn = document.getElementById("themeToggle");
  if (btn) {
    btn.textContent = theme === "dark" ? "☀" : "☾";
    btn.title = theme === "dark" ? "Switch to light mode" : "Switch to dark mode";
  }
}

function toggleTheme() {
  applyTheme(getTheme() === "dark" ? "light" : "dark");
}

// Apply immediately so there's no flash of the wrong theme.
applyTheme(getTheme());

// ---------- Toasts ----------

function ensureToastHost() {
  let host = document.getElementById("toastHost");
  if (!host) {
    host = document.createElement("div");
    host.id = "toastHost";
    document.body.appendChild(host);
  }
  return host;
}

function showToast(message, type = "info", durationMs = 4000) {
  const host = ensureToastHost();
  const el = document.createElement("div");
  el.className = "toast " + type;
  el.textContent = message;
  host.appendChild(el);

  setTimeout(() => {
    el.classList.add("fading");
    setTimeout(() => el.remove(), 250);
  }, durationMs);
}

// ---------- Critical alert sound ----------
// Generated with the Web Audio API so there's no audio file to ship
// and nothing to load from the internet.

function isSoundEnabled() {
  return localStorage.getItem("rphms_sound") !== "off";
}

function toggleSound() {
  const next = isSoundEnabled() ? "off" : "on";
  localStorage.setItem("rphms_sound", next);
  const btn = document.getElementById("soundToggle");
  if (btn) {
    btn.textContent = next === "on" ? "🔔" : "🔕";
    btn.title = next === "on" ? "Alert sound on" : "Alert sound off";
  }
  showToast(next === "on" ? "Alert sound enabled" : "Alert sound muted", "info", 2000);
}

function playAlertTone() {
  if (!isSoundEnabled()) return;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    // Two short beeps - distinct enough to notice without being alarming.
    [0, 0.28].forEach((offset) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.value = 880;
      gain.gain.setValueAtTime(0.0001, ctx.currentTime + offset);
      gain.gain.exponentialRampToValueAtTime(0.18, ctx.currentTime + offset + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + offset + 0.2);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(ctx.currentTime + offset);
      osc.stop(ctx.currentTime + offset + 0.22);
    });
  } catch (err) {
    // Browsers block audio until the user has interacted with the page.
    // That's fine - the visual alert still shows.
    console.debug("Alert tone not played:", err);
  }
}

// ---------- Shared topbar controls ----------
// Adds theme + sound toggle buttons into any element with id="topbarActions".

function mountTopbarControls() {
  const host = document.getElementById("topbarActions");
  if (!host) return;

  const themeBtn = document.createElement("button");
  themeBtn.className = "icon-btn";
  themeBtn.id = "themeToggle";
  themeBtn.addEventListener("click", toggleTheme);

  const soundBtn = document.createElement("button");
  soundBtn.className = "icon-btn";
  soundBtn.id = "soundToggle";
  soundBtn.textContent = isSoundEnabled() ? "🔔" : "🔕";
  soundBtn.title = isSoundEnabled() ? "Alert sound on" : "Alert sound off";
  soundBtn.addEventListener("click", toggleSound);

  host.prepend(soundBtn);
  host.prepend(themeBtn);
  applyTheme(getTheme());
}

// ---------- Misc ----------

function downloadWithAuth(path, fallbackName) {
  // Files behind an auth header can't use a plain <a download>, so fetch
  // the bytes first, then hand the browser a temporary blob URL.
  apiRequestRaw(path)
    .then((blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fallbackName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      showToast("Download started", "success");
    })
    .catch((err) => showToast("Export failed: " + err.message, "error"));
}

async function apiRequestRaw(path) {
  const token = getToken();
  const response = await fetch(API_BASE + path, {
    headers: token ? { Authorization: "Bearer " + token } : {},
  });
  if (!response.ok) throw new Error("Request failed (" + response.status + ")");
  return response.blob();
}
