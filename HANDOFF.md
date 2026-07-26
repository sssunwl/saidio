# SAIDIO 多線素材工廠 — 交接檔

> 給接手的 AI:這是 SAIDIO「每日 prompt 工廠 + 統一素材庫網站」。本檔記錄現狀、路徑、待辦。
> 更新日:2026-07-22。

## 2026-07-22：媒體 API 一步到位
- 新增 `.github/workflows/daily-production.yml`，每天 09:12 JST 一次產生三條 brief，並可接續生成 1 份 TTS、1 份 Lyria 音樂、1 份 Veo 直式 B-roll。
- 實際媒體排程有安全鎖：repo variable `SAIDIO_MEDIA_ENABLED=true` 才會啟用；手動 dispatch 可選 all/music/voiceover/video。
- 生成程式為 `scripts/generate_media.py`，單項保存 ready/failed 狀態，可重跑且已完成項目不重複扣額度。
- 大型媒體不進 Git，發布到每月 GitHub Release `media-YYYY-MM`；網站顯示狀態及成品連結。這些 Release 資產是公開的，不得放機密客戶素材。
- 原本三支 daily workflow 保留作手動復原，但已移除 schedule，避免同時寫檔與重複生成。

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

## 2026-07-25：Prompt 一律自帶 NEGATIVE + RULES，網站換上 v2

**為什麼**：SS 平常是「單獨複製一條 prompt」就直接貼到工具，規則若只寫在別的檔案或腦袋裡，實作時一定會漏。所以規則現在跟著 prompt 走。

- 新檔 `scripts/prompt_blocks.py` 是這些區塊的唯一真相來源：`bundle()` 把每條 prompt 組成
  `【PROMPT】/【NEGATIVE PROMPT｜禁止項】/【RULES｜產出規則】` 三段，音樂、概念圖、影片各有一組。改規則只改這裡。
- **音樂線**（`generate_daily_brief.py`）：Gemini 只負責寫製作方向那一段（明寫時長、BPM、樂器、編排、剪接點、哪段可循環、怎麼收尾），
  不再自己寫 negative；negative 與 rules 由程式接上。AI 角色劇那天允許「明確標示的角色人聲」，其餘一律無人聲。
  Gemini 有時回字串、有時回物件，`flatten_prompt()` 統一攤平成字串（`generate_media.py` 本來就只吃字串）。
- **CapyChill**（`generate_capychill_briefs.py`）：概念圖 prompt 加了 `PAW CONSTRUCTION` —— 手掌必須畫出分開的腳趾與指節、
  不可畫成圓團 mitten、不可被毛或道具蓋住。這是「動畫階段手不會動」的**源頭病**：模型讀不出解剖的部位就不動它。
  影片 prompt 的 negative 明列 `frozen scene / static rain / stiff paws`，rules 要求手掌「輕微 shift and re-grip」，
  並寫進 Flow「帧」模式（首尾同一張圖）與後製 delogo/xfade 參數。
- **回填**：今天（7/25）的音樂 brief 已就地補上三段式；更早的歷史批次維持原樣。旅遊／旁白／IG Carousel 尚未套用，之後要就照同一套加。
## 2026-07-25（第二輪）：三段式套到全部產線，locks 改成只鎖已完成的音樂

用戶要求「全部 Prompt 都更新，除了 CapyChill 7/23–7/25 的音樂」（其餘媒體他會重新生成）。

- **`prompt_blocks.py` 補完四組區塊**：`VOICE_*`（旁白腳本）、`SFX_*`（環境音）、`BROLL_*`（旅遊 Flow 片）、
  `CARD_*`（IG 圖卡）。新增 `blocks_for(stream, item_type)` 當唯一對照表，生成器與 backfill 共用，不會各自漂移。
- **旁白／旅遊生成器**：Gemini 只寫腳本或分鏡本身，程式再接上 negative + rules；並明確叫 Gemini
  **不要自己寫 negative／rules**（兩份規則貼在一起會互相矛盾）。今天的 brief 若是舊格式，
  不呼叫 API 也會就地補上區塊。
- **IG Carousel**：每張圖卡改成完整三段式；`LOCKED_DATES` 清空（全部重寫）；
  尺寸抽成 `CARD_WIDTH/CARD_HEIGHT/CARD_RATIO` 常數，方便日後從 4:5 換 3:4。
- **CapyChill 鎖的粒度改了**：舊版整天鎖死 → 現在 `MUSIC_LOCKED_DATES = {7/23, 7/24, 7/25}`
  只鎖**音樂 prompt**（專輯已產出，不該誘發重跑），概念圖與微動畫照現行規則重寫。
  見 `keep_published_music()`。
- **新腳本 `scripts/backfill_prompt_blocks.py`**：不需要 API key，把歷史檔案裡沒有三段式的 prompt
  就地補上（本輪補了 125 條）。改完 `prompt_blocks.py` 就可以再跑一次。
- **測試**：`python3 -m unittest discover -s tests`，20 項全過（新增 4 項：圖卡三段式、
  旁白與環境音吃到不同規則、重複 bundle 不會疊套、鎖定日保留音樂但換掉影片規則）。
- **修掉 CapyChill 7/24 的手寫 Flow prompt**：`CapyChill/DailyPrompt/20260724/character_raw/Flow_prompts.md`
  舊版六條全寫「雨凍住、環境完全凍結、手不動」，正是僵硬的兩個病因。已改為**由生成器輸出**
  （內容等同 `data/capychill.json` 的 7/24 影片項），舊版移到同層 `.archived/`。
- **新腳本 `CapyChill/scripts/upscale_master.py`**：母圖貼進 Flow 前的 Lanczos 放大（+ 輕微 unsharp），
  `--portrait --focus <THEMES 的 focus_x>` 可一併切出 9:16 走廊。已在 7/24 母圖實測。
## 2026-07-26：IG Carousel 改成「一天一個可販售產品」

用戶決定：尺寸改 3:4、百搭先上且行業包也要、行業研究現在跑。三件都做完了。

- **架構換掉**：舊版是「九天磨一個品牌、每張獨立生成」。新版是
  **一張無文字連續背景母圖 → 分割成 N 張 → Canva 上字**。
  原因是算數：9 張並排要 9720px 寬，模型長邊只給約 1536px，切完每格剩 ~170px 再放大——
  背景撐得住，**文字和人臉一定爛**。所以能切的只有沒有文字的那一層。
- **兩個階段**：`UNIVERSAL_EPOCH`(7/26)–7/30 是**百搭 Kit** 五套結構型
  （列表／前後對比／教學步驟／金句／誤解破除）× 3 配色；`INDUSTRY_EPOCH`(7/31) 之後是
  **行業包，一天一個行業**（`industry_index = delta % 9`，家族用 `(industry_index + round_index) % 9`
  錯開，所以同一個行業下一輪不會長得一樣）。
- **張數可變 6–12**，由結構決定（金句 6、對比與誤解破除 8、清單與步驟 9）。
  預設 9 是有依據的：互動在第 3 張後掉、第 8 張後回升，8–10 張最好。
- **`scripts/split_carousel.py`（新）**：母圖 → N 張 1080×1440 + `_seam_preview.png`。
  preview 會畫出每個切點左右 80px 禁區，發文前先看它。
  `--fit stretch` 只適用抽象紋理母圖；有可辨識結構就改 `--fit cover`。
- **`PLATE_NEGATIVE / PLATE_RULES`（新）**：母圖專用，第一條就是 NO TEXT OF ANY KIND。
- **`INDUSTRIES` 換成買家導向**（商業教練／房仲／攝影師／課程創作者…）。研究發現：
  咖啡店、餐廳、牙醫是**內容題材**，不是**模板買家**。
- **文件**：`CAROUSEL_RULES.md` 改寫為 v2；`CAROUSEL_RESEARCH.md`（新，市場數據 + 來源）；
  `CAROUSEL_V2_DESIGN.md`（架構與販售流程，已標註哪幾節被研究推翻）。
- **測試 23 項全過**。舊架構的 7/23–7/25 三天保留在 data 裡當歸檔，不再重寫。
- **還沒做**：LICENSE.md 草稿、Gumroad 產品頁文案、Canva 動態頁流程。

- **網站**：`index.html`/`app.js`/`styles.css` 換成玻璃感 v2（今天／產線／歸檔／策略四頁籤），
  單條「複製」複製的就是完整三段式。v2 補回了 `generation.status` 徽章與成品連結，媒體排程的結果照樣看得到。
  本機開發版在 `/Users/sws/Sun/Claude/saidio/web_v2/`，改完要兩邊同步。
