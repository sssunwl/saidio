# SAIDIO 多線素材工廠 — 交接檔

> 給接手的 AI:這是 SAIDIO「每日 prompt 工廠 + 統一素材庫網站」。本檔記錄現狀、路徑、待辦。
> 更新日:2026-07-21。

## 一句話
GitHub Actions 每天用 Gemini(免費文字額度)生成三條線的 prompt/腳本 → commit 進 repo + POST 到 Discord → 人手動去各工具生成媒體、存本機 `resource/`。網站是可標籤/年曆瀏覽的統一素材庫。

## 路徑
- **GitHub repo（雲端排程 + 網站文字的真相來源）**：`sssunwl/saidio`（`gh repo clone sssunwl/saidio`）
- **線上網站**：https://sssunwl.github.io/saidio/
- **本機工作夾**：`/Users/sws/Sun/Claude/saidio/`
  - `geminimusic/` — 音樂媒體庫（`YYYYMMDD<n>.mp4` + INDEX.md，人手動存）
  - `resource/voiceover/` — 旁白 mp3 / 音效（人手動存）
  - `resource/suntravel/` — B-roll / Flow 片 / 字卡圖（人手動存）
  - `VOICES.md` — 語音人物聖經（與 repo 同步一份）
- **本機夾非 git**；repo 只存「文字」不存媒體（避免 repo 脹大，Footage 教訓）。

## 本機媒體備份／同步策略
- `geminimusic/` 與 `resource/` 是媒體本體的唯一工作副本，**不進 Git**；每次新增或整理完素材後，至少同步到一個工作區外的雲端硬碟或外接硬碟。
- 建議以 `YYYYMMDD` 日期資料夾／檔名為單位增量備份，保留 `geminimusic/INDEX.md`，並一併備份 `resource/` 的目錄結構；不要只備份檔案而遺失分類。
- `VOICES.md` 以 repo 版本為文字真相來源；本機副本修改後，須同步回 repo。媒體若要跨電腦使用，從備份還原到同一路徑即可。
- 接手前先確認：今天新增的媒體已備份、`INDEX.md` 已更新、`VOICES.md` 本機與 repo 版本一致。

## repo 內關鍵檔
- `.github/workflows/daily-brief.yml`（🎵 音樂，00:12 UTC，既有）
- `.github/workflows/daily-voiceover.yml`（🗣️ 旁白，00:18 UTC，新）
- `.github/workflows/daily-suntravel.yml`（🎬 旅遊，00:24 UTC，新）
- `scripts/generate_daily_brief.py`（音樂）/ `generate_voiceover_brief.py` / `generate_suntravel_brief.py`
- `data/dashboard.json`（音樂+metrics+projects+radar）/ `data/voiceover.json` / `data/suntravel.json`
- `index.html` + `app.js` + `styles.css`（統一素材庫前端，vanilla JS 無 build）
- `VOICES.md`（聲線/角色唯一真相來源）

## 機制重點
- **Secrets**（已存在，兩支新 workflow 共用）：`GEMINI_API_KEY`、`DISCORD_WEBHOOK_URL`。無新增費用。
- **模式**：只有「文字」全自動（免費）。媒體（音樂/B-roll/Flow/字卡圖/配音）都是給 prompt、人手動生成（Veo/Imagen/Lyria 要錢，用戶決定維持 prompt 模式）。
- **輪播主題**：voiceover=投資解說/旅遊導覽/冥想引導/睡眠故事；suntravel=沖繩海島/城市街景/美食特寫/交通移動/飯店房景/日出日落/雨天室內（`ROTATION` 在各 script 頂部，依 `date.toordinal()%len` 輪）。
- **資料 schema**：新線 brief 有 `items[]`（`{type,purpose,engine,voice?,status,text}`）；音樂舊線是 `prompts[]` 字串，前端 `normalize()` 兼容兩者。
- **一致性**：靠 `VOICES.md` 每個聲線的 `🔒 鎖定聲線` 欄填固定 voice 名稱（AI Studio 或 ElevenLabs），之後永遠用同一個。

## 已驗證（2026-07-21）
- 三支 workflow 手動 dispatch 全 success；今天真資料已生成（旁白=V-CALM 冥想包、旅遊=美食特寫）；Discord 已收；Pages 已服務新 data。
- 前端 console 無錯、三線合併、標籤過濾/年曆互動正常。

## 待辦（需用戶輸入才能做）
1. **鎖定聲線**：用戶到 AI Studio 試聽，把 voice 名稱填進 `VOICES.md` 的 5 個 `🔒` 空欄。V-TRAVEL 可雙人（[F]/[M]）。
2. **AI 角色劇**：`VOICES.md` C 段是待填模板；用戶給世界觀+角色（或沿用 Suniverse「S 家族」）後，再開 `daily-drama` workflow（複製 voiceover 那套即可）。
3. **睡眠 Channel**：全球通用兒童睡前 channel；可加「無語言助眠 playlist」一條**音樂線**排程（no vocals、可循環、3–5 分串 30–60 分）。命名/視覺/頻率未定。
4. 用戶看實物後可能要調：各線**數量**、輪播**主題**、**時間**、工具列**連結**（現 B-roll/Flow 指 labs.google/fx/tools/flow，音樂/旁白指 aistudio.google.com）。

## 怎麼改（給接手 AI）
- 改數量/主題 → 編 `scripts/generate_*_brief.py` 的 prompt 與 `ROTATION`，並同步改 workflow 內對 items 長度的 assert。
- 改網站 → 編 `index.html`/`app.js`/`styles.css`，本機 `python3 -m http.server` 起靜態站驗證（fetch 需 http）。
- 部署 → push 到 `main` 即觸發 Pages（repo 慣例是 bot 直接 commit main）。
- 測試單支 → `gh workflow run daily-voiceover.yml -R sssunwl/saidio`（注意：若當天 data 已有今日 brief 會跳過生成，只重貼；要強制可在 script 靠 `FORCE_REGENERATE=1`）。
