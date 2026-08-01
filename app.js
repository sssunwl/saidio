// SAIDIO 統一素材庫
// 資訊架構:每個頁籤回答一個不重複的問題。
//   今天 = 我今天要生什麼   產線 = 這條線的規則與歷史
//   歸檔 = 某一天生了什麼   策略 = 整體在推什麼
// 同一份 brief 只在「今天」與「歸檔」各出現一次,語意不同(待辦 vs 紀錄)。
//
// 顯示原則(2026-07-26):同一組 prompt 之間逐字重複的段落只顯示一次(共用段),
// 卡片只印各自的差異 —— 但**複製永遠是完整版**,因為 SS 的用法是單獨複製一條直接貼工具。

const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const fmt = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

const STREAMS = {
  obcar:      { label: "OBcar",       icon: "◇", color: "var(--obcar)",      file: "data/obcar.json",      desc: "23 款車的 360°定點航拍與沖繩海邊跟拍。v2 三層 Prompt：一張定錨圖＋三段接力，每車每比例 10 條。", tool: "https://labs.google/fx/tools/flow" },
  capychill: { label: "CapyChill",   icon: "◍", color: "var(--capychill)", file: "data/capychill.json", desc: "Lo-fi 水豚長片:每日專輯音樂、概念圖與低風險微動畫。", tool: "https://labs.google/fx/tools/flow" },
  carousel:  { label: "IG Carousel", icon: "▤", color: "var(--carousel)",  file: "data/carousel.json",  desc: "一天一個可販售產品:母圖 → 分割 → Canva 上字。", tool: "https://www.canva.com" },
  music:     { label: "音樂",        icon: "♪", color: "var(--music)",     file: "data/dashboard.json", desc: "每日 10 條可重複使用的配樂 prompt,供各頻道剪輯取用。", tool: "https://aistudio.google.com" },
  suntravel: { label: "旅遊",        icon: "▷", color: "var(--suntravel)", file: "data/suntravel.json", desc: "沖繩海島到城市街景的 B-roll 與 Flow 影片 prompt。", tool: "https://labs.google/fx/tools/flow" },
  voiceover: { label: "旁白",        icon: "◗", color: "var(--voiceover)", file: "data/voiceover.json", desc: "投資解說、旅遊導覽、冥想引導與睡眠故事的腳本與聲線。", tool: "https://aistudio.google.com" },
};
// OBcar 是目前要逐車驗證的客戶製作線,排最前面。
const ORDER = ["obcar", "capychill", "carousel", "music", "suntravel", "voiceover"];

// 一條 brief 內的項目先分到三個橫排(圖 / 微動畫 / 音樂),剩下的落到「文字」。
// 陣列順序 = 比對優先序(「影片」不能被「圖」搶走);顯示順序另外由 LANE_ORDER 決定。
const LANES = [
  { key: "audio",  label: "音樂",   re: /音樂|music|track|配樂|音效|sfx|環境音|lyria|bgm/i },
  { key: "motion", label: "微動畫", re: /影片|video|動畫|微動|b-?roll|flow|veo|reels|shorts/i },
  { key: "image",  label: "圖",     re: /圖|image|imagen|card|卡|canva|封面|插畫|分割|split|拆件/i },
  { key: "text",   label: "文字",   re: /.*/ },
];
const LANE_ORDER = ["image", "motion", "audio", "text"];

const state = { briefs: [], dashboard: null, streamData: {}, filter: "all", obcarAspect: "16:9", month: new Date(), selected: null };

/* ── 正規化:把兩種 schema 收斂成同一個形狀 ───────────────── */
function normItem(raw, stream) {
  if (typeof raw === "string") return { type: "Prompt", purpose: "", engine: "", text: raw, stream };
  if (raw && typeof raw === "object") {
    if (raw.text) return {
      type: raw.type || "Prompt", purpose: raw.purpose || "", engine: raw.engine || "",
      text: raw.text, generation: raw.generation || null, aspect: raw.aspect || "", stream,
    };
    // 音樂線的結構化 prompt 物件 → 攤平成可讀文字
    const skip = new Set(["id", "type"]);
    const body = Object.entries(raw)
      .filter(([k, v]) => !skip.has(k) && v != null && v !== "")
      .map(([k, v]) => `${k.replace(/_/g, " ")}: ${Array.isArray(v) ? v.join(", ") : v}`)
      .join("\n");
    return { type: raw.type || `Track ${raw.id || ""}`.trim(), purpose: raw.duration || "", engine: "", text: body, stream };
  }
  return { type: "Prompt", purpose: "", engine: "", text: String(raw), stream };
}

function normBrief(b, stream) {
  const rawItems = Array.isArray(b.items) ? b.items : Array.isArray(b.prompts) ? b.prompts : [];
  return {
    stream, date: b.date, title: b.title || "", focus: b.focus || "",
    summary: b.summary || "", meta: typeof b.meta === "string" ? b.meta : "",
    items: rawItems.map(r => normItem(r, stream)),
  };
}

async function load() {
  const results = await Promise.all(Object.entries(STREAMS).map(async ([key, cfg]) => {
    try {
      const res = await fetch(cfg.file, { cache: "no-store" });
      if (!res.ok) throw new Error(res.status);
      const json = await res.json();
      state.streamData[key] = json;
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

/* ── 去重:同一家族的 prompt 有大量逐字相同的段落 ─────────── */

// 把 prompt 切成可比對的最小單位:【區塊標題】底下的每一行,長段落再依句切開。
// 切句只在「句點後面接空白」時發生,所以 4.5:1、1080×1440 不會被切壞。
function splitUnits(text) {
  const units = [];
  let section = "";
  for (const rawLine of String(text).split("\n")) {
    const line = rawLine.trim();
    if (!line) continue;
    if (/^【.*】$/.test(line)) { section = line; continue; }
    if (line.length > 90) {
      for (const s of sentences(line)) units.push({ section, text: s });
    } else {
      units.push({ section, text: line });
    }
  }
  return units;
}

function sentences(paragraph) {
  const out = [];
  let buf = "";
  for (let i = 0; i < paragraph.length; i++) {
    const ch = paragraph[i];
    buf += ch;
    if (/[.!?。！？]/.test(ch)) {
      const next = paragraph[i + 1];
      if (next === undefined || /\s/.test(next)) { out.push(buf.trim()); buf = ""; }
    }
  }
  if (buf.trim()) out.push(buf.trim());
  return out;
}

const uKey = u => `${u.section} ${u.text}`;

// shared = 在這個家族「每一條」prompt 裡都逐字出現的單位。
function familyAnalysis(items) {
  const parsed = items.map(it => splitUnits(it.text));
  if (items.length < 2) return { shared: [], uniques: parsed, useShared: false };

  const count = new Map();
  for (const units of parsed) {
    for (const k of new Set(units.map(uKey))) count.set(k, (count.get(k) || 0) + 1);
  }
  const isShared = k => count.get(k) === items.length;

  const shared = [], seen = new Set();
  for (const u of parsed[0]) {
    const k = uKey(u);
    if (isShared(k) && !seen.has(k)) { seen.add(k); shared.push(u); }
  }
  const uniques = parsed.map(units => units.filter(u => !isShared(uKey(u))));

  // 共用段太少就不值得多一層面板。
  const sharedChars = shared.reduce((n, u) => n + u.text.length, 0);
  const avg = items.reduce((n, it) => n + it.text.length, 0) / items.length;
  return { shared, uniques, useShared: sharedChars > Math.max(160, avg * 0.22) };
}

// 「IG 圖組・第 1 張」「母圖・warm-neutral」→ 家族名,同家族才互相比對。
function familyKey(type) {
  let s = String(type || "").split("・")[0].trim();
  s = s.replace(/\s*第\s*\d+\s*張\s*$/, "").replace(/\s+\d+(\s*\/\s*\d+)?\s*$/, "").trim();
  return s || "Prompt";
}

function laneKey(it) {
  const hay = `${it.type} ${it.purpose} ${it.engine}`;
  for (const L of LANES) if (L.re.test(hay)) return L.key;
  return "text";
}

// 音樂線的 prompt 是純字串,type 一律 "Prompt",光靠字面分不出來 → 用產線補。
function laneOf(it) {
  const k = laneKey(it);
  if (k === "text" && it.stream === "music") return "audio";
  return k;
}

/* ── 複製登錄簿:避免把幾萬字塞進 data- 屬性 ───────────────── */
const CLIP = [];
const clip = text => (CLIP.push(text), CLIP.length - 1);

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
    .map(b => groupHTML(b, true)).join("") || `<div class="glass panel"><div class="empty">這條產線今天沒有素材。</div></div>`;
  wire();
}

/* ── 一組 brief 的版面 ───────────────────────────────────
   group(整批) → lane(圖 / 微動畫 / 音樂 / 文字) → family(同型 prompt)
                 → 共用段(只印一次) + 差異小卡格
------------------------------------------------------- */
function groupHTML(b, open = true) {
  const c = STREAMS[b.stream];
  const joinedText = items => items.map(it => `【${it.type}】\n${it.text}`).join("\n\n──────────────────\n\n");
  const allText = joinedText(b.items);
  const landscapeItems = b.items.filter(it => it.aspect === "16:9");
  const verticalItems = b.items.filter(it => it.aspect === "9:16");
  const obCopyAttrs = landscapeItems.length && verticalItems.length
    ? ` data-ob-copy-landscape="${clip(joinedText(landscapeItems))}" data-ob-copy-vertical="${clip(joinedText(verticalItems))}"`
    : "";
  const lanes = LANE_ORDER
    .map(k => LANES.find(L => L.key === k))
    .map(L => ({ L, items: b.items.filter(it => laneOf(it) === L.key) }))
    .filter(x => x.items.length);

  return `<section class="glass group ${open ? "" : "collapsed"}" style="--c:${c.color}">
    <div class="group-head">
      <span class="group-badge"></span>
      <h3>${esc(c.label)}</h3>
      <span class="group-title">${esc(b.title)}${b.focus ? ` — ${esc(b.focus)}` : ""}</span>
      <span class="group-count">${b.items.length} PROMPT</span>
      <button class="copy-btn copy-all" data-copy="${clip(allText)}"${obCopyAttrs}>複製全部</button>
      <span class="caret">▾</span>
    </div>
    <div class="group-body">
      ${b.meta ? `<p class="group-focus">${esc(b.meta)}</p>` : ""}
      ${lanes.map(x => laneHTML(x.L, x.items)).join("")}
    </div>
  </section>`;
}

function laneHTML(L, items) {
  const fams = [];
  for (const it of items) {
    const key = familyKey(it.type);
    const hit = fams.find(f => f.key === key);
    if (hit) hit.items.push(it); else fams.push({ key, items: [it] });
  }
  return `<div class="lane" data-lane="${L.key}">
    <div class="lane-head"><span class="lane-tag">${L.label}</span>
      <span class="lane-count">${items.length} 條</span></div>
    ${fams.map(famHTML).join("")}
  </div>`;
}

function famHTML(f) {
  const { shared, uniques, useShared } = familyAnalysis(f.items);
  const bodies = useShared ? uniques : f.items.map(it => splitUnits(it.text));
  const sharedText = shared.map(u => u.text).join("\n");
  return `<div class="fam">
    ${f.items.length > 1 ? `<div class="fam-head">${esc(f.key)} × ${f.items.length}</div>` : ""}
    ${useShared ? `<div class="shared collapsed">
      <div class="shared-head">
        <span class="caret">▾</span>
        <strong>本組共用段</strong>
        <span class="shared-note">這 ${f.items.length} 條逐字相同的 ${shared.length} 句收在這裡,卡片只印差異。單條「複製」仍是完整 prompt。</span>
        <button class="copy-btn" data-copy="${clip(sharedText)}">複製共用段</button>
      </div>
      <div class="shared-body">${unitsHTML(shared)}</div>
    </div>` : ""}
    <div class="pgrid">${f.items.map((it, i) => cardHTML(it, bodies[i], i)).join("")}</div>
  </div>`;
}

function unitsHTML(units) {
  let html = "", cur = null;
  for (const u of units) {
    if (u.section !== cur) {
      cur = u.section;
      if (cur) html += `<h5 class="sec">${esc(cur)}</h5>`;
    }
    html += `<p>${esc(u.text)}</p>`;
  }
  return html;
}

const GEN_LABEL = { ready: "已生成", running: "生成中", failed: "失敗", queued: "排隊中" };

function genHTML(it) {
  const g = it.generation;
  if (!g || !g.status) return "";
  const link = g.assetUrl
    ? `<a class="media-link" href="${esc(g.assetUrl)}" target="_blank" rel="noopener">▶</a>`
    : "";
  return `<span class="gen gen-${esc(g.status)}" title="${esc(g.error || "")}">${esc(GEN_LABEL[g.status] || g.status)}</span>${link}`;
}

// 同型 prompt 的 type 會一模一樣(例如 10 條「專輯音樂」),取開頭一段當標題才分得出誰是誰。
function itemLabel(it) {
  const lines = it.text.split("\n").map(l => l.trim()).filter(l => l && !l.startsWith("【"));
  const first = lines.find(l => !/^(duration|bpm)\s*:/i.test(l)) || lines[0] || "";
  const m = first.match(/^(?:Track\s*\d+\/?\d*\s*[—–-]\s*)?["“”]?([^"“”\n.]{4,48})/);
  let label = (m ? m[1] : first).trim().replace(/[.,;:]$/, "");
  if (/^mood\s*:/i.test(label)) label = label.replace(/^mood\s*:\s*/i, "");
  return label && label.length >= 4 ? label : "";
}

function cardHTML(it, units, i) {
  const generic = !it.type || it.type === "Prompt";
  const title = generic ? (itemLabel(it) || "Prompt") : it.type;
  return `<div class="pcell" data-aspect="${esc(it.aspect || "")}"><article class="pcard">
    <div class="pc-head">
      <span class="pc-no">${String(i + 1).padStart(2, "0")}</span>
      <span class="pc-type" title="${esc(title)}">${esc(title)}</span>
      ${genHTML(it)}
      <button class="copy-btn" data-copy="${clip(it.text)}">複製</button>
    </div>
    <div class="pc-body">${units.length ? unitsHTML(units)
      : `<p class="pc-same">這條與「本組共用段」完全相同。</p>`}</div>
    <span class="pc-hint">滑上去展開 · 點一下釘住</span>
  </article></div>`;
}

/* ── 互動 ─────────────────────────────────────────────── */
function wire() {
  $$(".copy-btn").forEach(b => b.onclick = async e => {
    e.stopPropagation();
    const text = CLIP[Number(b.dataset.copy)] ?? "";
    try { await navigator.clipboard.writeText(text); toast(`已複製 ${text.length.toLocaleString()} 字`); }
    catch { toast("複製失敗,請手動選取"); }
  });
  $$(".group-head").forEach(h => h.onclick = e => {
    if (e.target.closest(".copy-btn")) return;
    h.parentElement.classList.toggle("collapsed");
  });
  $$(".shared-head").forEach(h => h.onclick = e => {
    if (e.target.closest(".copy-btn")) return;
    h.parentElement.classList.toggle("collapsed");
  });
  $$(".pcard").forEach(card => card.onclick = e => {
    if (e.target.closest(".copy-btn") || e.target.closest("a")) return;
    const on = card.classList.contains("pinned");
    $$(".pcard.pinned").forEach(o => o.classList.remove("pinned"));
    card.classList.toggle("pinned", !on);
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
  // 歷史批次預設收起,只展開最新一批 —— 否則一條線幾百個 prompt 會全部攤開。
  detail.innerHTML = `<div class="glass panel" style="--c:${c.color}">
      <p class="eyebrow" style="color:${c.color}">${esc(c.label)}</p>
      <p class="muted">${esc(c.desc)}</p>
      <p class="muted small">工具:<a href="${c.tool}" target="_blank" rel="noopener" style="color:${c.color}">${esc(c.tool)}</a></p>
    </div>` + (key === "obcar" ? obcarTrackerHTML(state.streamData.obcar?.tracker) + obcarPromptFilterHTML() : "") + (list.length
      ? list.map((b, i) => `<p class="batch-date">${esc(b.date)}</p>${groupHTML(b, i === 0)}`).join("")
      : `<div class="glass panel"><div class="empty">這條線還沒有紀錄。</div></div>`);
  wire();
  if (key === "obcar") wireObcarAspect();
}

const OBCAR_STATUS = {
  todo: ["待做", "·"], doing: ["製作中", "◌"], review: ["待檢查", "?"],
  done: ["完成", "✓"], blocked: ["卡住", "!"], na: ["不適用", "—"],
};

function obcarRatioSwitchHTML(label) {
  return `<div class="ob-ratio-control">
    ${label ? `<span>${esc(label)}</span>` : ""}
    <div class="ob-ratio-switch" role="group" aria-label="OBcar畫面比例">
      <button data-ob-aspect="16:9">16:9 橫式</button><button data-ob-aspect="9:16">9:16 直式 · 4:5安全區</button>
    </div>
  </div>`;
}

function obcarPromptFilterHTML() {
  return `<section class="glass panel ob-prompt-filter">
    <div><p class="eyebrow">PROMPT 顯示</p><h3>只顯示目前選擇的比例</h3></div>
    ${obcarRatioSwitchHTML("切換 Prompt")}
    <strong class="ob-prompt-count" data-ob-prompt-count>14 PROMPT</strong>
  </section>`;
}

function obcarStatusCell(value) {
  const key = OBCAR_STATUS[value] ? value : "todo";
  const [label, mark] = OBCAR_STATUS[key];
  return `<td><span class="ob-status ob-${key}" title="${label}" aria-label="${label}">${mark}</span></td>`;
}

function obcarTrackerHTML(tracker) {
  if (!tracker?.vehicles?.length) return "";
  const fields169 = ["anchor169", "orbitClips169", "orbitMaster169", "coastStills169", "coastClips169", "coastMaster169"];
  const fields916 = ["anchor916", "orbitClips916", "orbitMaster916", "coastStills916", "coastClips916", "coastMaster916"];
  const allFields = ["spec", "references", ...fields169, ...fields916, "finalQa"];
  const total = tracker.vehicles.length * allFields.length;
  const tasksOf = v => ({ ...(tracker.defaultTasks || {}), ...(v.tasks || {}) });
  const done = tracker.vehicles.reduce((n, v) => n + allFields.filter(f => tasksOf(v)[f] === "done").length, 0);
  const table = (aspect, fields) => {
    const rows = tracker.vehicles.map(v => {
      const tasks = tasksOf(v);
      return `<tr><th scope="row"><span class="ob-id">${esc(v.id)}</span><strong>${esc(v.name)}</strong><small>${esc(v.seats)}座 · ${esc(v.note || "")}</small></th>
        ${obcarStatusCell(tasks.spec)}${obcarStatusCell(tasks.references)}${fields.map(f => obcarStatusCell(tasks[f])).join("")}${obcarStatusCell(tasks.finalQa)}</tr>`;
    }).join("");
    return `<div class="ob-table-wrap" data-ob-table="${aspect}"><table class="ob-table ob-table-ratio">
      <thead><tr><th rowspan="2">車款</th><th colspan="2">準備</th><th colspan="3">360° · ${aspect}</th><th colspan="3">海邊 · ${aspect}</th><th rowspan="2">總 QA</th></tr>
      <tr><th>規格</th><th>實車照</th><th>定錨</th><th>3段接力</th><th>成片</th><th>3定格</th><th>3×10秒</th><th>成片</th></tr></thead>
      <tbody>${rows}</tbody></table></div>`;
  };
  return `<section class="glass panel ob-tracker" style="--c:var(--obcar)">
    <div class="ob-track-head"><div><p class="eyebrow">逐車完成表</p><h3>23 車款 × 兩種影片 × 兩種比例</h3></div>
      <div class="ob-total"><strong>${done}/${total}</strong><span>步驟完成</span></div></div>
    <p class="muted small">✓ 完成　◌ 製作中　? 待檢查　! 卡住　· 待做。先把 16:9 做完批准，9:16 再用批准的 16:9 當場景參考原生重生；直式的車與重要物件全程留在中央4:5安全區。</p>
    ${obcarRatioSwitchHTML("切換完成表")}
    ${table("16:9", fields169)}${table("9:16", fields916)}
  </section>`;
}

function wireObcarAspect() {
  const apply = () => {
    $$('[data-ob-aspect]').forEach(b => b.classList.toggle("active", b.dataset.obAspect === state.obcarAspect));
    $$('[data-ob-table]').forEach(t => t.hidden = t.dataset.obTable !== state.obcarAspect);
    let visibleCount = 0;
    $$('#line-detail .pcell[data-aspect]').forEach(c => {
      const aspect = c.dataset.aspect;
      c.hidden = Boolean(aspect && aspect !== state.obcarAspect);
      if (aspect && !c.hidden) visibleCount += 1;
    });
    $$('#line-detail .fam').forEach(f => {
      const cards = [...f.querySelectorAll('.pcell[data-aspect]')];
      f.hidden = Boolean(cards.length && cards.every(c => c.hidden));
    });
    $$('#line-detail .lane').forEach(lane => {
      const cards = [...lane.querySelectorAll('.pcell[data-aspect]')];
      const shown = cards.filter(c => !c.hidden).length;
      if (cards.some(c => c.dataset.aspect)) {
        lane.hidden = shown === 0;
        const count = lane.querySelector('.lane-count');
        if (count) count.textContent = `${shown} 條`;
      }
    });
    $$('#line-detail .group').forEach(group => {
      const cards = [...group.querySelectorAll('.pcell[data-aspect]')];
      if (!cards.some(c => c.dataset.aspect)) return;
      const shown = cards.filter(c => !c.hidden).length;
      const count = group.querySelector('.group-count');
      if (count) count.textContent = `${shown} PROMPT`;
      const copyAll = group.querySelector('.copy-all[data-ob-copy-landscape]');
      if (copyAll) {
        copyAll.dataset.copy = state.obcarAspect === "9:16" ? copyAll.dataset.obCopyVertical : copyAll.dataset.obCopyLandscape;
        copyAll.textContent = `複製${state.obcarAspect}全部`;
      }
    });
    $$('[data-ob-prompt-count]').forEach(x => x.textContent = `${visibleCount} PROMPT`);
  };
  $$('[data-ob-aspect]').forEach(b => b.onclick = () => { state.obcarAspect = b.dataset.obAspect; apply(); });
  apply();
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
  const list = ORDER.flatMap(k => state.briefs.filter(b => b.date === state.selected && b.stream === k));
  $("#archive-detail").innerHTML = list.length
    ? `<p class="eyebrow">${state.selected}</p>` + list.map((b, i) => groupHTML(b, i === 0)).join("")
    : `<div class="empty">${state.selected} 沒有素材紀錄。</div>`;
  wire();
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
      <div class="progress"><i style="width:${Number(p.progress) || 0}%"></i></div>
      ${p.href ? `<a class="project-link" href="${esc(p.href)}" target="_blank" rel="noopener">查看製作清單 →</a>` : ""}</article>`;
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
// 釘住的卡片點空白處收掉
document.addEventListener("click", e => {
  if (!e.target.closest(".pcard")) $$(".pcard.pinned").forEach(c => c.classList.remove("pinned"));
});

load();
