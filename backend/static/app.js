/* ============================================================
   RPHMS — shared frontend logic
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
