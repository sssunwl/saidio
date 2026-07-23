// SAIDIO 統一素材庫 — 各創作專案與每日素材合併瀏覽
const $ = s => document.querySelector(s);
const fmt = d => d.toISOString().slice(0, 10);

const STREAMS = {
  music:     { label: "音樂", emoji: "🎵", cls: "s-music" },
  voiceover: { label: "旁白", emoji: "🗣️", cls: "s-voiceover" },
  suntravel: { label: "旅遊", emoji: "🎬", cls: "s-suntravel" },
  capychill: { label: "CapyChill", emoji: "🦫", cls: "s-capychill" },
  carousel:  { label: "IG Carousel", emoji: "📚", cls: "s-carousel" },
};

let meta = null, projects = [], radar = [], updatedAt = "";
let briefs = [];                 // 合併後、依日期排序的所有 brief
let activeStream = "all";        // all | music | voiceover | suntravel
let viewed = new Date();
const expanded = new Set();      // 展開中的 brief id

// 把音樂舊格式（prompts 是字串陣列）normalize 成統一的 items 結構
function normalize(brief, stream) {
  brief.stream = brief.stream || stream;
  if (!brief.items) {
    brief.items = (brief.prompts || []).map(text => ({
      type: "音樂 prompt", purpose: brief.focus, engine: "Lyria", status: "prompt", text,
    }));
  }
  brief.id = `${brief.stream}-${brief.date}`;
  return brief;
}

async function loadStream(file, stream) {
  try {
    const d = await fetch(file).then(r => r.ok ? r.json() : null);
    if (!d) return [];
    if (stream === "music") { meta = d; projects = d.projects || []; radar = d.radar || []; }
    if (d.updatedAt > updatedAt) updatedAt = d.updatedAt;
    return (d.briefs || []).map(b => normalize(b, stream));
  } catch (e) { return []; }
}

async function boot() {
  const parts = await Promise.all([
    loadStream("data/dashboard.json", "music"),
    loadStream("data/voiceover.json", "voiceover"),
    loadStream("data/suntravel.json", "suntravel"),
    loadStream("data/capychill.json", "capychill"),
    loadStream("data/carousel.json", "carousel"),
  ]);
  briefs = parts.flat().sort((a, b) => a.date.localeCompare(b.date));
  render();
}

function visible() {
  return activeStream === "all" ? briefs : briefs.filter(b => b.stream === activeStream);
}

function currentBatchDate(list) {
  const today = fmt(new Date());
  return list.filter(b => b.date <= today).at(-1)?.date || list.at(0)?.date || null;
}

function render() {
  const vis = visible();
  const batchDate = currentBatchDate(vis);
  const latest = vis.findLast(b => b.date === batchDate);
  $("#today-focus").textContent = latest ? latest.title : "尚無素材";
  $("#today-meta").textContent = latest ? latest.meta : "";
  $("#updated-at").textContent = updatedAt ? `更新於 ${new Date(updatedAt).toLocaleString("zh-Hant-TW")}` : "";

  // metrics（沿用音樂 dashboard 的，補一個素材總數）
  const m = (meta && meta.metrics ? [...meta.metrics] : []);
  m.unshift({ label: "素材批次總數", value: String(briefs.length).padStart(2, "0") });
  $("#metrics").innerHTML = m.slice(0, 4).map(x => `<div class="metric"><span>${x.label}</span><strong>${x.value}</strong></div>`).join("");

  renderChips();
  renderTodayCards();
  renderNotifications();
  $("#projects-grid").innerHTML = projects.map(p => `<article class="project"><div class="project-top"><span class="tag ${p.state === "進行中" ? "active" : p.state === "暫緩" ? "hold" : ""}">${p.state}</span><span class="muted">${p.progress}%</span></div><h3>${p.name}</h3><p>${p.summary}</p><div class="progress"><i style="width:${p.progress}%"></i></div></article>`).join("");
  $("#radar-list").innerHTML = radar.map(r => `<div class="signal"><time>${r.date}</time><div><strong>${r.title}</strong><p>${r.detail}</p></div><span class="tag">${r.tag}</span></div>`).join("");
  renderCalendar();
}

function renderChips() {
  const counts = { all: briefs.length };
  for (const k of Object.keys(STREAMS)) counts[k] = briefs.filter(b => b.stream === k).length;
  const chip = (key, label) => `<button class="chip ${activeStream === key ? "on" : ""} ${STREAMS[key] ? STREAMS[key].cls : ""}" data-stream="${key}">${label} <b>${counts[key] || 0}</b></button>`;
  let html = chip("all", "全部");
  for (const [k, v] of Object.entries(STREAMS)) html += chip(k, `${v.emoji} ${v.label}`);
  $("#stream-chips").innerHTML = html;
  document.querySelectorAll(".chip").forEach(c => c.onclick = () => { activeStream = c.dataset.stream; render(); });
}

function itemCard(it) {
  const generation = it.generation || {};
  const labels = { ready: "已生成", running: "生成中", failed: "失敗", queued: "排隊中" };
  const media = generation.assetUrl
    ? `<a class="media-link" href="${generation.assetUrl}" target="_blank" rel="noopener">▶ 開啟成品</a>`
    : "";
  const state = generation.status
    ? `<span class="gen-status gen-${generation.status}" title="${generation.error || ""}">${labels[generation.status] || generation.status}</span>`
    : `<span class="gen-status gen-prompt">提示詞</span>`;
  return `<div class="prompt"><div class="prompt-head"><span class="ptag">${it.type} · ${it.voice || it.engine}</span>${state}${media}</div>${it.text}</div>`;
}

function briefBlock(b) {
  const s = STREAMS[b.stream];
  const open = expanded.has(b.id);
  return `<article class="stream-card ${s.cls}" data-id="${b.id}">
    <div class="sc-head">
      <span class="sc-badge">${s.emoji} ${s.label}</span>
      <div class="sc-title"><strong>${b.title}</strong><span>${b.focus} · ${b.date}</span></div>
      <div class="sc-actions">
        <button class="mini" data-copy="${b.id}">複製</button>
        <button class="mini" data-toggle="${b.id}">${open ? "收起" : `展開 ${b.items.length}`}</button>
      </div>
    </div>
    <div class="sc-body" ${open ? "" : "hidden"}>
      <p class="sc-summary">${b.summary || ""}</p>
      ${b.items.map(itemCard).join("")}
    </div>
  </article>`;
}

function renderTodayCards() {
  const vis = visible();
  const latestDate = currentBatchDate(vis);
  const todays = vis.filter(b => b.date === latestDate);
  $("#briefs-eyebrow").textContent = latestDate ? `最新一批素材 · ${latestDate}` : "尚無素材";
  $("#today-cards").innerHTML = todays.length ? todays.map(briefBlock).join("") : `<p class="muted">此分類目前沒有素材。</p>`;
  wireCards();
}

function wireCards() {
  document.querySelectorAll("[data-toggle]").forEach(btn => btn.onclick = () => {
    const id = btn.dataset.toggle; expanded.has(id) ? expanded.delete(id) : expanded.add(id);
    renderTodayCards(); renderArchiveDetail();
  });
  document.querySelectorAll("[data-copy]").forEach(btn => btn.onclick = async () => {
    const b = briefs.find(x => x.id === btn.dataset.copy);
    await navigator.clipboard.writeText(b.items.map(i => i.text).join("\n\n"));
    btn.textContent = "已複製"; setTimeout(() => btn.textContent = "複製", 1200);
  });
}

function renderNotifications() {
  $("#notifications").innerHTML = [...visible()].reverse().slice(0, 6).map(b => {
    const s = STREAMS[b.stream];
    return `<div class="notification"><time>${b.date}</time><p><span class="dot ${s.cls}"></span><strong>${b.title}</strong><br>${b.focus}</p></div>`;
  }).join("") || `<p class="muted">尚無通知。</p>`;
}

function renderCalendar() {
  const y = viewed.getFullYear(), mo = viewed.getMonth();
  const first = new Date(y, mo, 1), offset = (first.getDay() + 6) % 7, days = new Date(y, mo + 1, 0).getDate(), today = fmt(new Date());
  $("#month-label").textContent = first.toLocaleString("zh-Hant-TW", { month: "long", year: "numeric" });
  const vis = visible();
  let html = "";
  for (let i = 0; i < offset; i++) html += '<div class="day empty"></div>';
  for (let d = 1; d <= days; d++) {
    const key = `${y}-${String(mo + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    const dayBriefs = vis.filter(b => b.date === key);
    const dots = dayBriefs.map(b => `<i class="${STREAMS[b.stream].cls}"></i>`).join("");
    html += `<button class="day ${dayBriefs.length ? "has-brief" : ""} ${key === today ? "today" : ""}" ${dayBriefs.length ? `data-date="${key}"` : ""}><span class="day-num">${d}</span><span class="dots">${dots}</span></button>`;
  }
  $("#calendar-grid").innerHTML = html;
  document.querySelectorAll(".day[data-date]").forEach(x => x.onclick = () => {
    document.querySelectorAll(".day").forEach(d => d.classList.remove("selected"));
    x.classList.add("selected");
    renderArchiveDetail(x.dataset.date);
  });
}

let selectedDate = null;
function renderArchiveDetail(date) {
  if (date) selectedDate = date;
  if (!selectedDate) return;
  const dayBriefs = visible().filter(b => b.date === selectedDate);
  $("#archive-detail").innerHTML = `<strong>${selectedDate} · 當日素材</strong>` + dayBriefs.map(briefBlock).join("");
  wireCards();
}

$("#prev-month").onclick = () => { viewed.setMonth(viewed.getMonth() - 1); renderCalendar(); };
$("#next-month").onclick = () => { viewed.setMonth(viewed.getMonth() + 1); renderCalendar(); };
boot();
