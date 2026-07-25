// SAIDIO 統一素材庫
// 資訊架構:每個頁籤回答一個不重複的問題。
//   今天 = 我今天要生什麼   產線 = 這條線的規則與歷史
//   歸檔 = 某一天生了什麼   策略 = 整體在推什麼
// 同一份 brief 只在「今天」與「歸檔」各出現一次,語意不同(待辦 vs 紀錄)。

const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const fmt = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

const STREAMS = {
  music:     { label: "音樂",        icon: "♪", color: "var(--music)",     file: "data/dashboard.json", desc: "每日 10 條可重複使用的配樂 prompt,供各頻道剪輯取用。", tool: "https://aistudio.google.com" },
  voiceover: { label: "旁白",        icon: "◗", color: "var(--voiceover)", file: "data/voiceover.json", desc: "投資解說、旅遊導覽、冥想引導與睡眠故事的腳本與聲線。", tool: "https://aistudio.google.com" },
  suntravel: { label: "旅遊",        icon: "▷", color: "var(--suntravel)", file: "data/suntravel.json", desc: "沖繩海島到城市街景的 B-roll 與 Flow 影片 prompt。", tool: "https://labs.google/fx/tools/flow" },
  capychill: { label: "CapyChill",   icon: "◍", color: "var(--capychill)", file: "data/capychill.json", desc: "Lo-fi 水豚長片:每日專輯音樂、概念圖與低風險微動畫。", tool: "https://labs.google/fx/tools/flow" },
  carousel:  { label: "IG Carousel", icon: "▤", color: "var(--carousel)",  file: "data/carousel.json",  desc: "九日九套 Template Family,每張 4:5 獨立輸出。", tool: "https://www.canva.com" },
};
const ORDER = ["capychill", "music", "suntravel", "voiceover", "carousel"];

const state = { briefs: [], dashboard: null, filter: "all", month: new Date(), selected: null };

/* ── 正規化:把兩種 schema 收斂成同一個形狀 ───────────────── */
function normItem(raw, stream) {
  if (typeof raw === "string") return { type: "Prompt", purpose: "", text: raw };
  if (raw && typeof raw === "object") {
    if (raw.text) return { type: raw.type || "Prompt", purpose: raw.purpose || raw.engine || "", text: raw.text, generation: raw.generation || null };
    // 音樂線的結構化 prompt 物件 → 攤平成可讀文字
    const skip = new Set(["id", "type"]);
    const body = Object.entries(raw)
      .filter(([k, v]) => !skip.has(k) && v != null && v !== "")
      .map(([k, v]) => `${k.replace(/_/g, " ")}: ${Array.isArray(v) ? v.join(", ") : v}`)
      .join("\n");
    return { type: raw.type || `Track ${raw.id || ""}`.trim(), purpose: raw.duration || "", text: body };
  }
  return { type: "Prompt", purpose: "", text: String(raw) };
}

function normBrief(b, stream) {
  const rawItems = Array.isArray(b.items) ? b.items : Array.isArray(b.prompts) ? b.prompts : [];
  return {
    stream, date: b.date, title: b.title || "", focus: b.focus || "",
    summary: b.summary || "", meta: b.meta || "",
    items: rawItems.map(r => normItem(r, stream)),
  };
}

async function load() {
  const results = await Promise.all(Object.entries(STREAMS).map(async ([key, cfg]) => {
    try {
      const res = await fetch(cfg.file, { cache: "no-store" });
      if (!res.ok) throw new Error(res.status);
      const json = await res.json();
      if (key === "music") state.dashboard = json;
      return (json.briefs || []).map(b => normBrief(b, key));
    } catch (e) { console.warn(`[saidio] ${key} 載入失敗`, e); return []; }
  }));
  state.briefs = results.flat().filter(b => b.date).sort((a, b) => b.date.localeCompare(a.date));

  const stamp = state.dashboard?.updatedAt?.slice(0, 16).replace("T", " ") || "—";
  $("#updated-at").textContent = `更新 ${stamp}`;
  $("#footer-updated").textContent = `最後更新 ${stamp}`;

  renderToday(); renderLines(); renderCalendar(); renderStrategy();
}

/* ── 今天 ─────────────────────────────────────────────── */
function latestDate() {
  const today = fmt(new Date());
  return state.briefs.some(b => b.date === today) ? today : (state.briefs[0]?.date || today);
}

function renderToday() {
  const date = latestDate();
  const todays = state.briefs.filter(b => b.date === date);
  const isToday = date === fmt(new Date());

  $("#today-date").textContent = isToday ? "今天要生的素材" : `最新一批 · ${date}`;
  $("#today-summary").textContent = todays.length
    ? `${date} · ${todays.length} 條產線 · 共 ${todays.reduce((n, b) => n + b.items.length, 0)} 個 prompt`
    : "今天還沒有素材,排程會在每天早上自動生成。";

  $("#today-stats").innerHTML = [
    { n: todays.length, l: "產線" },
    { n: todays.reduce((s, b) => s + b.items.length, 0), l: "PROMPT" },
    { n: state.briefs.length, l: "歷史批次" },
  ].map(s => `<div class="stat"><b>${String(s.n).padStart(2, "0")}</b><span>${s.l}</span></div>`).join("");

  // 過濾 chip
  const chips = [`<button class="chip ${state.filter === "all" ? "active" : ""}" data-f="all">全部</button>`]
    .concat(ORDER.filter(k => todays.some(b => b.stream === k)).map(k => {
      const c = STREAMS[k];
      return `<button class="chip ${state.filter === k ? "active" : ""}" data-f="${k}" style="--c:${c.color}"><i></i>${c.label}</button>`;
    }));
  $("#today-filter").innerHTML = chips.join("");
  $$("#today-filter .chip").forEach(el => el.onclick = () => { state.filter = el.dataset.f; renderToday(); });

  const shown = state.filter === "all" ? todays : todays.filter(b => b.stream === state.filter);
  $("#today-groups").innerHTML = ORDER
    .map(k => shown.find(b => b.stream === k)).filter(Boolean)
    .map(groupHTML).join("") || `<div class="glass panel"><div class="empty">這條產線今天沒有素材。</div></div>`;
  wireItems();
}

function groupHTML(b) {
  const c = STREAMS[b.stream];
  return `<section class="glass group" style="--c:${c.color}">
    <div class="group-head"><span class="group-badge"></span><h3>${esc(c.label)}</h3>
      <span class="group-count">${b.items.length} PROMPT</span></div>
    <p class="group-focus">${esc(b.title)}${b.focus ? ` — ${esc(b.focus)}` : ""}</p>
    ${b.items.map(itemHTML).join("")}
  </section>`;
}

// 同一產線的 prompt 常常同型別(例如 10 首「專輯音樂」),
// 取開頭一段當標籤才分得出誰是誰。
function itemLabel(it) {
  // 跳過區塊標題(【PROMPT】/【NEGATIVE…】/【RULES…】)與只是重複右側標籤的欄位
  const lines = it.text.split("\n").map(l => l.trim())
    .filter(l => l && !l.startsWith("【"));
  const first = lines.find(l => !/^(duration|bpm)\s*:/i.test(l)) || lines[0] || "";
  const m = first.match(/^(?:Track\s*\d+\/?\d*\s*[—–-]\s*)?["“”]?([^"“”\n.]{4,56})/);
  let label = (m ? m[1] : first).trim().replace(/[.,;:]$/, "");
  if (/^mood\s*:/i.test(label)) label = label.replace(/^mood\s*:\s*/i, "");
  if (!label || label.length < 4 || label === it.purpose) return "";
  return label;
}

// 媒體排程(generate_media.py)會回寫 generation.status/assetUrl,
// 沒有這兩個徽章就看不出哪些 prompt 已經真的生成過。
const GEN_LABEL = { ready: "已生成", running: "生成中", failed: "失敗", queued: "排隊中" };

function genHTML(it) {
  const g = it.generation;
  if (!g || !g.status) return "";
  const link = g.assetUrl
    ? `<a class="media-link" href="${esc(g.assetUrl)}" target="_blank" rel="noopener">▶ 成品</a>`
    : "";
  return `<span class="gen gen-${esc(g.status)}" title="${esc(g.error || "")}">${esc(GEN_LABEL[g.status] || g.status)}</span>${link}`;
}

function itemHTML(it, i) {
  const label = itemLabel(it);
  return `<article class="item">
    <div class="item-head">
      <span class="item-type">${esc(it.type)}</span>
      ${label ? `<span class="item-label">${esc(label)}</span>` : ""}
      ${it.purpose ? `<span class="item-purpose">${esc(it.purpose)}</span>` : ""}
      <span class="item-actions">
        ${genHTML(it)}
        <button class="copy-btn" data-copy="${encodeURIComponent(it.text)}">複製</button>
        <span class="caret">▶</span>
      </span>
    </div>
    <div class="item-body"><pre class="prompt-text">${esc(it.text)}</pre></div>
  </article>`;
}

function wireItems() {
  $$(".item-head").forEach(h => h.onclick = e => {
    if (e.target.closest(".copy-btn")) return;
    h.parentElement.classList.toggle("open");
  });
  $$(".copy-btn").forEach(b => b.onclick = async () => {
    const text = decodeURIComponent(b.dataset.copy);
    try { await navigator.clipboard.writeText(text); toast("已複製 Prompt"); }
    catch { toast("複製失敗,請手動選取"); }
  });
}

/* ── 產線 ─────────────────────────────────────────────── */
function renderLines() {
  $("#line-grid").innerHTML = ORDER.map(k => {
    const c = STREAMS[k];
    const list = state.briefs.filter(b => b.stream === k);
    const total = list.reduce((n, b) => n + b.items.length, 0);
    return `<article class="glass line-card" data-line="${k}" style="--c:${c.color}">
      <div class="line-icon">${c.icon}</div>
      <h3>${esc(c.label)}</h3>
      <p>${esc(c.desc)}</p>
      <div class="line-meta"><span>${list.length} 批次</span><span>${total} PROMPT</span></div>
    </article>`;
  }).join("");
  $$(".line-card").forEach(el => el.onclick = () => openLine(el.dataset.line));
  $("#lines-back").onclick = () => {
    $("#line-grid").hidden = false; $("#line-detail").hidden = true; $("#lines-back").hidden = true;
  };
}

function openLine(key) {
  const c = STREAMS[key];
  const list = state.briefs.filter(b => b.stream === key);
  $("#line-grid").hidden = true; $("#lines-back").hidden = false;
  const detail = $("#line-detail");
  detail.hidden = false;
  detail.innerHTML = `<div class="glass panel" style="--c:${c.color}">
      <p class="eyebrow" style="color:${c.color}">${esc(c.label)}</p>
      <p class="muted">${esc(c.desc)}</p>
      <p class="muted small">工具:<a href="${c.tool}" target="_blank" rel="noopener" style="color:${c.color}">${esc(c.tool)}</a></p>
    </div>` + (list.length
      ? list.map(groupHTML).join("")
      : `<div class="glass panel"><div class="empty">這條線還沒有紀錄。</div></div>`);
  wireItems();
}

/* ── 歸檔 ─────────────────────────────────────────────── */
function renderCalendar() {
  const y = state.month.getFullYear(), m = state.month.getMonth();
  $("#month-label").textContent = `${y}.${String(m + 1).padStart(2, "0")}`;
  const first = new Date(y, m, 1), last = new Date(y, m + 1, 0);
  const lead = (first.getDay() + 6) % 7; // 週一起始
  const today = fmt(new Date());

  let html = "";
  for (let i = 0; i < lead; i++) html += `<div class="day empty"></div>`;
  for (let d = 1; d <= last.getDate(); d++) {
    const iso = fmt(new Date(y, m, d));
    const on = state.briefs.filter(b => b.date === iso);
    html += `<div class="day ${iso === today ? "today" : ""} ${iso === state.selected ? "selected" : ""}" data-date="${iso}">
      <span class="day-num">${d}</span>
      <span class="dots">${ORDER.filter(k => on.some(b => b.stream === k))
        .map(k => `<i style="background:${STREAMS[k].color}"></i>`).join("")}</span>
    </div>`;
  }
  $("#calendar-grid").innerHTML = html;
  $$(".day[data-date]").forEach(el => el.onclick = () => { state.selected = el.dataset.date; renderCalendar(); renderArchive(); });

  $("#calendar-legend").innerHTML = ORDER
    .map(k => `<span><i style="background:${STREAMS[k].color}"></i>${STREAMS[k].label}</span>`).join("");
  $("#prev-month").onclick = () => { state.month = new Date(y, m - 1, 1); renderCalendar(); };
  $("#next-month").onclick = () => { state.month = new Date(y, m + 1, 1); renderCalendar(); };
}

function renderArchive() {
  const list = state.briefs.filter(b => b.date === state.selected);
  $("#archive-detail").innerHTML = list.length
    ? `<p class="eyebrow">${state.selected}</p>` + list.map(b => {
        const c = STREAMS[b.stream];
        return `<div style="--c:${c.color};margin-bottom:14px">
          <div class="group-head"><span class="group-badge"></span><h3>${esc(c.label)}</h3>
            <span class="group-count">${b.items.length} PROMPT</span></div>
          <p class="group-focus">${esc(b.title)}</p>
          ${b.items.map(itemHTML).join("")}</div>`;
      }).join("")
    : `<div class="empty">${state.selected} 沒有素材紀錄。</div>`;
  wireItems();
}

/* ── 策略 ─────────────────────────────────────────────── */
function renderStrategy() {
  const d = state.dashboard;
  if (!d) return;
  $("#metrics").innerHTML = (d.metrics || [])
    .map(m => `<div class="glass metric"><span>${esc(m.label)}</span><strong>${esc(m.value)}</strong></div>`).join("");
  $("#projects-grid").innerHTML = (d.projects || []).map(p => {
    const cls = p.state === "進行中" ? "active" : p.state === "暫停" ? "hold" : "";
    return `<article class="project"><span class="tag ${cls}">${esc(p.state)}</span>
      <h3>${esc(p.name)}</h3><p>${esc(p.summary)}</p>
      <div class="progress"><i style="width:${Number(p.progress) || 0}%"></i></div></article>`;
  }).join("");
  $("#radar-list").innerHTML = (d.radar || []).map(r =>
    `<div class="signal"><time>${esc(r.date)}</time><strong>${esc(r.title)}</strong><p>${esc(r.detail)}</p></div>`).join("");
}

/* ── 共用 ─────────────────────────────────────────────── */
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, ch =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}
let toastTimer;
function toast(msg) {
  const t = $("#toast");
  t.textContent = msg; t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), 1900);
}

$$(".tab").forEach(tab => tab.onclick = () => {
  $$(".tab").forEach(t => t.classList.toggle("active", t === tab));
  $$(".view").forEach(v => v.classList.toggle("active", v.id === `view-${tab.dataset.view}`));
});

load();
