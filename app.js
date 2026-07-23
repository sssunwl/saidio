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
let activeView = "briefs";
let selectedDate = null;
let selectedArchiveStream = null;
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
  renderProjects();
  $("#radar-list").innerHTML = radar.map(r => `<div class="signal"><time>${r.date}</time><div><strong>${r.title}</strong><p>${r.detail}</p></div><span class="tag">${r.tag}</span></div>`).join("");
  renderCalendar();
  showView(location.hash.slice(1) || activeView, false);
}

function showView(name, updateHash = true) {
  if (!["briefs", "calendar", "projects", "radar"].includes(name)) name = "briefs";
  activeView = name;
  document.querySelectorAll("[data-view]").forEach(x => x.classList.toggle("active", x.dataset.view === name));
  document.querySelectorAll("[data-view-link]").forEach(x => x.classList.toggle("active", x.dataset.viewLink === name));
  if (updateHash && location.hash !== `#${name}`) history.pushState(null, "", `#${name}`);
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

function groupName(stream, it) {
  if (stream === "capychill") {
    if (it.type === "專輯音樂") return "🎵 專輯音樂";
    if (it.type === "專輯概念圖") return "🖼️ 專輯概念圖";
    return "🎬 影片版本";
  }
  if (stream === "carousel") return it.type.startsWith("IG 圖組") ? "🖼️ 9 張獨立圖卡" : "🧩 Canva 拆件";
  return it.type;
}

function itemTitle(it, index) {
  const track = it.text.match(/Track \d+\/\d+ — "([^"]+)"/)?.[1];
  return track ? `${index + 1}. ${track}` : it.type;
}

function itemCard(it, b, index) {
  const generation = it.generation || {};
  const labels = { ready: "已生成", running: "生成中", failed: "失敗", queued: "排隊中" };
  const media = generation.assetUrl ? `<a class="media-link" href="${generation.assetUrl}" target="_blank" rel="noopener">▶ 開啟成品</a>` : "";
  const state = generation.status
    ? `<span class="gen-status gen-${generation.status}" title="${generation.error || ""}">${labels[generation.status] || generation.status}</span>`
    : `<span class="gen-status gen-prompt">提示詞</span>`;
  return `<article class="prompt-item">
    <div class="prompt-item-head">
      <div><span class="ptag">${it.voice || it.engine}</span><strong>${itemTitle(it, index)}</strong><small>${it.purpose || ""}</small></div>
      <div class="prompt-item-actions">${state}${media}<button class="mini" data-copy-item="${b.id}" data-item-index="${index}">單獨複製</button><button class="mini" data-item-toggle>查看</button></div>
    </div>
    <div class="prompt" hidden>${it.text}</div>
  </article>`;
}

function groupedItems(b) {
  const groups = new Map();
  b.items.forEach((it, index) => {
    const name = groupName(b.stream, it);
    if (!groups.has(name)) groups.set(name, []);
    groups.get(name).push({ it, index });
  });
  const tabs = [...groups.entries()].map(([name, items], groupIndex) =>
    `<button class="group-tab" data-group-toggle="${b.id}-${groupIndex}">${name}<b>${items.length}</b></button>`
  ).join("");
  const panels = [...groups.entries()].map(([name, items], groupIndex) =>
    `<section class="item-group" id="group-${b.id}-${groupIndex}" hidden><div class="item-group-title"><strong>${name}</strong><span>選一項查看或複製</span></div>${items.map(({ it, index }) => itemCard(it, b, index)).join("")}</section>`
  ).join("");
  return `<div class="group-browser"><nav class="group-tabs">${tabs}</nav><div class="group-content"><div class="group-placeholder">先選擇一個製作分類</div>${panels}</div></div>`;
}

function briefBlock(b) {
  const s = STREAMS[b.stream];
  const open = expanded.has(b.id);
  return `<article class="stream-card ${s.cls}" data-id="${b.id}">
    <div class="sc-head">
      <span class="sc-badge">${s.emoji} ${s.label}</span>
      <div class="sc-title"><strong>${b.title}</strong><span>${b.focus} · ${b.date}</span></div>
      <div class="sc-actions"><button class="mini" data-toggle="${b.id}">${open ? "收起" : `開啟 ${b.items.length}`}</button></div>
    </div>
    <div class="sc-body" ${open ? "" : "hidden"}>
      <p class="sc-summary">${b.summary || ""}</p>
      ${groupedItems(b)}
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
    const id = btn.dataset.toggle;
    const body = btn.closest(".stream-card").querySelector(".sc-body");
    body.hidden = !body.hidden;
    body.hidden ? expanded.delete(id) : expanded.add(id);
    btn.textContent = body.hidden ? `開啟 ${briefs.find(b => b.id === id)?.items.length || ""}` : "收起";
  });
  document.querySelectorAll("[data-group-toggle]").forEach(btn => btn.onclick = () => {
    const browser = btn.closest(".group-browser");
    browser.querySelectorAll(".group-tab").forEach(x => x.classList.toggle("on", x === btn));
    browser.querySelectorAll(".item-group").forEach(x => x.hidden = x.id !== `group-${btn.dataset.groupToggle}`);
    browser.querySelector(".group-placeholder").hidden = true;
  });
  document.querySelectorAll("[data-item-toggle]").forEach(btn => btn.onclick = () => {
    const prompt = btn.closest(".prompt-item").querySelector(".prompt");
    prompt.hidden = !prompt.hidden;
    btn.textContent = prompt.hidden ? "查看" : "收起";
  });
  document.querySelectorAll("[data-copy-item]").forEach(btn => btn.onclick = async () => {
    const b = briefs.find(x => x.id === btn.dataset.copyItem);
    const it = b.items[Number(btn.dataset.itemIndex)];
    const copy = `日期：${b.date}\n當天主題：${b.title}\n主題重點：${b.focus}\n項目：${it.type}\n用途：${it.purpose || ""}\n使用工具：${it.voice || it.engine || ""}\n\nPROMPT：\n${it.text}`;
    await navigator.clipboard.writeText(copy);
    btn.textContent = "已複製"; setTimeout(() => btn.textContent = "單獨複製", 1200);
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
  const vis = briefs;
  let html = "";
  for (let i = 0; i < offset; i++) html += '<div class="day empty"></div>';
  for (let d = 1; d <= days; d++) {
    const key = `${y}-${String(mo + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    const dayBriefs = vis.filter(b => b.date === key);
    const dots = [...new Set(dayBriefs.map(b => b.stream))].map(k => `<i class="${STREAMS[k].cls}"></i>`).join("");
    html += `<button class="day ${dayBriefs.length ? "has-brief" : ""} ${key === today ? "today" : ""}" ${dayBriefs.length ? `data-date="${key}"` : ""}><span class="day-num">${d}</span><span class="dots">${dots}</span></button>`;
  }
  $("#calendar-grid").innerHTML = html;
  document.querySelectorAll(".day[data-date]").forEach(x => x.onclick = () => {
    document.querySelectorAll(".day").forEach(d => d.classList.remove("selected"));
    x.classList.add("selected");
    selectedDate = x.dataset.date;
    selectedArchiveStream = null;
    renderArchiveFolders();
  });
  $("#calendar-legend").innerHTML = Object.entries(STREAMS).map(([k, s]) => `<span><i class="${s.cls}"></i>${s.label}</span>`).join("");
  if (selectedDate) renderArchiveFolders();
}

function renderArchiveFolders() {
  $("#folder-date").textContent = selectedDate || "先在年曆選日期";
  const dayBriefs = selectedDate ? briefs.filter(b => b.date === selectedDate) : [];
  $("#archive-folders").innerHTML = dayBriefs.map(b => {
    const s = STREAMS[b.stream];
    return `<button class="folder ${selectedArchiveStream === b.stream ? "on" : ""}" data-folder="${b.stream}"><span>▸ ${s.emoji} ${s.label}</span><b>${b.items.length}</b></button>`;
  }).join("") || (selectedDate ? `<p class="muted">當日沒有 Prompt。</p>` : "");
  document.querySelectorAll("[data-folder]").forEach(btn => btn.onclick = () => {
    selectedArchiveStream = btn.dataset.folder;
    renderArchiveFolders();
    renderArchiveDetail();
  });
  if (!selectedArchiveStream) $("#archive-detail").innerHTML = `<div class="empty-state">${selectedDate ? "請從左側資料夾選擇一個分類。" : "選擇左側日期，再選一個資料夾查看 Prompt。"}</div>`;
}

function renderArchiveDetail() {
  if (!selectedDate || !selectedArchiveStream) return;
  const dayBriefs = briefs.filter(b => b.date === selectedDate && b.stream === selectedArchiveStream);
  $("#archive-detail").innerHTML = dayBriefs.map(briefBlock).join("");
  wireCards();
}

function renderProjects() {
  $("#projects-grid").innerHTML = projects.map((p, i) => `<button class="project" data-project="${i}"><div class="project-top"><span class="tag ${p.state === "進行中" ? "active" : p.state === "暫緩" ? "hold" : ""}">${p.state}</span><span class="muted">${p.progress}%</span></div><h3>${p.name}</h3><p>${p.summary}</p><div class="progress"><i style="width:${p.progress}%"></i></div><span class="project-open">開啟專案 →</span></button>`).join("");
  document.querySelectorAll("[data-project]").forEach(btn => btn.onclick = () => openProject(projects[Number(btn.dataset.project)]));
}

function openProject(project) {
  const stream = project.name.includes("CapyChill") ? "capychill" : project.name.includes("Carousel") ? "carousel" : null;
  if (!stream) return;
  const list = briefs.filter(b => b.stream === stream);
  $("#projects-grid").hidden = true;
  $("#project-detail").hidden = false;
  $("#projects-back").hidden = false;
  $("#projects-title").textContent = project.name;
  $("#project-detail").innerHTML = `<div class="project-summary"><span class="tag active">${project.state}</span><strong>${project.progress}%</strong><p>${project.summary}</p></div><div class="project-days">${list.map(b => {
    const ready = b.items.filter(i => i.generation?.status === "ready").length;
    return `<article class="project-day"><div><time>${b.date}</time><h3>${b.title}</h3><p>${b.focus}</p></div><div class="day-progress"><strong>${ready}/${b.items.length}</strong><span>已完成</span></div><button class="mini" data-project-day="${b.id}">查看每日內容</button><div class="project-day-body" id="project-day-${b.id}" hidden>${briefBlock(b)}</div></article>`;
  }).join("")}</div>`;
  document.querySelectorAll("[data-project-day]").forEach(btn => btn.onclick = () => {
    const body = document.getElementById(`project-day-${btn.dataset.projectDay}`);
    body.hidden = !body.hidden;
    btn.textContent = body.hidden ? "查看每日內容" : "收起";
  });
  wireCards();
}

$("#projects-back").onclick = () => {
  $("#projects-grid").hidden = false;
  $("#project-detail").hidden = true;
  $("#projects-back").hidden = true;
  $("#projects-title").textContent = "進行中的專案";
};

$("#prev-month").onclick = () => { viewed.setMonth(viewed.getMonth() - 1); renderCalendar(); };
$("#next-month").onclick = () => { viewed.setMonth(viewed.getMonth() + 1); renderCalendar(); };
document.querySelectorAll("[data-view-link]").forEach(link => link.onclick = e => { e.preventDefault(); showView(link.dataset.viewLink); });
window.addEventListener("hashchange", () => showView(location.hash.slice(1), false));
boot();
