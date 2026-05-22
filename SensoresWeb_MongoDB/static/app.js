/* ==========================================================
   Sistema Riego — app.js
   Helpers compartidos: theme toggle, fetch, formato
   ========================================================== */

(function () {
  // ---- Theme ----
  const THEME_KEY = "riego.theme";
  const root = document.documentElement;

  function applyTheme(t) {
    root.setAttribute("data-theme", t);
    const btn = document.querySelector("[data-theme-toggle]");
    if (btn) btn.setAttribute("aria-pressed", t === "dark");
  }

  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    const prefers = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    applyTheme(saved || prefers);
  }

  function toggleTheme() {
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
  }

  // ---- Formatters ----
  const fmt = {
    num(v, d = 1) {
      if (v == null || v === "") return "—";
      const n = Number(v);
      return isNaN(n) ? "—" : n.toFixed(d);
    },
    int(v) {
      if (v == null || v === "") return "—";
      const n = Number(v);
      return isNaN(n) ? "—" : Math.round(n).toString();
    },
    fecha(v) {
      if (!v) return "—";
      try {
        const d = new Date(v);
        if (isNaN(d.getTime())) return v;
        return d.toLocaleString("es-CO", {
          day: "2-digit", month: "2-digit",
          hour: "2-digit", minute: "2-digit",
        });
      } catch { return v; }
    },
  };

  // ---- Fetch helper ----
  async function getJSON(url) {
    const res = await fetch(url, { headers: { "Accept": "application/json" } });
    if (!res.ok) throw new Error(`${res.status} ${url}`);
    return res.json();
  }

  // ---- Auto-refresh ----
  function autoRefresh(fn, intervalMs = 5000) {
    fn();
    return setInterval(fn, intervalMs);
  }

  // ---- Live timestamp ----
  function updateLastUpdate(el) {
    if (!el) return;
    el.textContent = new Date().toLocaleTimeString("es-CO", {
      hour: "2-digit", minute: "2-digit", second: "2-digit",
    });
  }

  // ---- Init on load ----
  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    document.addEventListener("click", function (e) {
      const t = e.target.closest("[data-theme-toggle]");
      if (t) { e.preventDefault(); toggleTheme(); }
    });
  });

  window.Riego = { applyTheme, toggleTheme, fmt, getJSON, autoRefresh, updateLastUpdate };
})();

/* ===== Chart.js theme defaults (called from pages that load Chart.js) ===== */
window.RiegoCharts = (function () {
  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }
  function applyDefaults() {
    if (typeof Chart === "undefined") return;
    Chart.defaults.font.family = "Manrope, ui-sans-serif, system-ui, sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = cssVar("--muted");
    Chart.defaults.borderColor = cssVar("--border");
    Chart.defaults.plugins.legend.labels.boxWidth = 10;
    Chart.defaults.plugins.legend.labels.boxHeight = 10;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
  }
  function palette() {
    return {
      temp:   cssVar("--terra"),
      hum:    cssVar("--sky"),
      pres:   cssVar("--ink-2"),
      luz:    cssVar("--warn"),
      green:  cssVar("--green"),
      border: cssVar("--border"),
      muted:  cssVar("--muted"),
    };
  }
  function gradient(ctx, color) {
    const c = ctx.chart.ctx;
    const g = c.createLinearGradient(0, 0, 0, 240);
    g.addColorStop(0, color + "55");
    g.addColorStop(1, color + "00");
    return g;
  }
  return { applyDefaults, palette, gradient };
})();
