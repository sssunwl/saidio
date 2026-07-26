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

## 2026-07-26:網站改「共用段抽出 + 小格卡」,並補上 LICENSE / Gumroad 文案

**為什麼**:SS 反映一組 prompt 在頁面上「整組全部展開、每條佔一整行」太長,而且同組之間
大量文字是逐字重複的(NEGATIVE 與 RULES 一字不差,PROMPT 也有八成相同)。

前端(`app.js`/`styles.css`,本機開發版 `saidio/web_v2/` 要兩邊同步):

- **共用段抽出**:`familyAnalysis()` 把同家族(`familyKey()`,例:「圖卡文字・第 N 張」→「圖卡文字」)
  的 prompt 切成句子單位(`splitUnits()`/`sentences()`,只在句點後接空白處斷句,所以 `4.5:1`、
  `1080×1440` 不會被切壞),**在每一條都逐字出現**的句子收進「本組共用段」面板只印一次,
  卡片只印各自的差異。實測 IG 圖卡文字從每張 2,870 字降到 253 字。
- ⚠️ **去重只影響顯示,複製永遠是完整 prompt**。SS 的用法是單獨複製一條直接貼工具,
  規則必須跟著 prompt 走(見 2026-07-25 那節)。改前端時別把 `CLIP` 換成畫面上的文字。
- **三個橫排**:每批 brief 先分到 圖 / 微動畫 / 音樂 / 文字 四個 lane(`LANES` 是比對優先序,
  `LANE_ORDER` 是顯示順序;「影片」必須比「圖」先比對,否則會被搶走)。音樂線的 prompt 是純字串、
  type 一律 `Prompt`,靠 `laneOf()` 用 stream 補分類。
- **小格卡**:`.pgrid` 一行 5 格(1280px),滑鼠移上去或點一下(`.pinned`)才展開蓋住鄰居;
  手機兩格。整組可收合,「複製全部」在標題列。
- **產線**:順序改成 CapyChill → IG Carousel → 音樂 → 旅遊 → 旁白;歷史批次預設收合,只展開最新一批
  (carousel 有 17 批,全展開會有幾萬字)。

已用 http-server 8649 實測:四頁籤、年曆、複製、1280 與 375px 皆無橫向溢出、console 無錯。

產品文件(IG Carousel 可販售線):

- `LICENSE.md` —— 買家可用於自己與客戶的社群貼文與廣告、可商用不需標註;不可轉售或轉送模板本身。
  字體只用 OFL 開源字體,**不碰 Canva Pro 專屬字體**(否則買家不能外發給客戶)。
- `GUMROAD_LISTING.md` —— 四層定價的產品頁文案(免費導流 / US$19 百搭 Kit / US$49 行業包 /
  US$99 代理授權)、標題關鍵字、視覺素材清單、上架後導流與驗證門檻。所有 `〔〕` 是上架前要填的欄位。

## 2026-07-26(下午):行業包排前面 + 五個維度打散「長得都一樣」

SS:「不要寫太單一的輪播圖 Prompt,我想做出很多不同款又好看的。」另外要求**行業包先跑**
(教練/房仲/攝影師/課程創作者才是掏錢的買家)。

`scripts/generate_carousel_briefs.py`:

- **排程改成 14 天一循環**:9 天行業包 → 5 天百搭 Kit。`EPOCH=2026-07-26`、`CYCLE_DAYS=14`;
  `INDUSTRY_EPOCH=EPOCH`、`UNIVERSAL_EPOCH=EPOCH+9`(名字留著,值對調了)。
  `main()` 的 `start` 也要跟著用 `EPOCH`,不然會從百搭那天才開始寫。
- **五個正交維度**,各用互質步長輪替(`pick()`):
  20 `VISUAL_FAMILIES` × 10 `COLOURWAYS` × 6 `TYPE_PAIRINGS` × 5 `SURFACES` × 7 `STORY_STRUCTURES`。
  視覺語法(怎麼長)與故事結構(怎麼講)是**正交**的:`industry_brief()` 把兩者組成一個 `look` 再餵給
  既有的 prompt builder,所以 `plate_prompt()`/`card_prompt()` 不用改介面。
- ⚠️ **7 種結構會被 14 天整除**。單用日次會讓同一個行業每輪都拿到同一個結構(共振),
  所以結構的 index 是 `day_index + round_index`。改 `CYCLE_DAYS` 或結構數時,
  一定要重跑 `test_no_two_days_ever_look_the_same`(檢查 140 天內零重複組合)。
- **頁數跟著結構走**(金句 6 / 客戶疑慮 7 / 對比與誤解破除 8 / 清單、步驟、案例 9),不再硬湊九張。
  賣的時候標題的頁數要跟實際檔案一致。
- 百搭 Kit 的三個配色也隨輪次前進,第二輪的列表款不會跟第一輪同色。

`data/carousel.json` 已重生(7/26 → 8/8);7/23–7/25 三筆舊格式維持鎖定不動。
25 個測試全過。

**產品決定**:動態頁(Canva 頁面動畫)**改走代做服務**,不放進模板包 —— 買家自己做的成功率太低,
賣他做不出來的檔案會變客訴。服務文案在 `GUMROAD_LISTING.md`。

## 2026-07-26(晚):Canva 連接器實測 —— 端到端跑完 7/26 商業教練那組

SS 已授權 Canva 連接器(可用;帳號下有 4 個 brand kit:OkinawaSunDays / TT / Seasee / OKIPLAYGROUND,
本次**刻意不套**,因為這是要賣的模板,必須品牌中性)。

**成品**:9 張 1080×1440 的「商業教練｜品牌定位｜列表款 × 靜謐拱窗編輯誌」。
Canva design id `DAHQdxXsoZ0`;PNG 存 `resource/carousel/20260726-coach-list-quietarch/`(不進 git)。

### 實測結論:Canva 的 AI 生成做不出「照規格的一整組輪播」

`generate-design` 四個候選沒有一個能用:一個幾乎全空、一個是不相干的實景照片版型、
一個**直接生成九宮格 contact sheet**(正是 `CAROUSEL_RULES.md` 明令禁止的)、一個是單張裝飾封面。
而且 `instagram_post` preset 是 1080×1350(4:5),要再 `resize-design` 成 custom 1080×1440。

→ **可行路徑是程式化組版**:`read-design(open_transaction)` → `edit-design` 的
`add_page` / `add_text` / `insert_shape` / `format_text` / `position_element` → `commit`。
完全可控:邊界、字級、顏色、角色分工都照 `CAROUSEL_RULES.md` 落地。

### 三個要記住的 API 限制

1. **`format_text` 沒有字型家族參數**。設得了級數/顏色/字重/行高,**設不了 serif↔grotesk**。
   所以 `TYPE_PAIRINGS` 這個維度目前只能靠人在 Canva 裡手動換字型。生成器照樣要寫,
   因為那是給人看的規格,但別以為 API 會自動套。
2. **`add_text` 一律以 16px 黑字落地**,必須第二趟 `format_text`。也就是每頁最少兩次呼叫
   (加元素一次、排版一次),因為 format 需要的 element_id 只有加完才拿得到。
3. **`resize-design` 會產生新的 design id**,不是原地改。舊 id 要丟掉。

### 這一組還沒做完的三件事

- **母圖還沒接**:SS 還沒生連續背景帶。第 1 張沿用 AI 給的奶油色拱窗紙紋當背景,第 2–9 張是純色。
  母圖生好之後把切片放到每張的最底層即可。
- **autofill 還沒 tag**:目前是一份普通 design,不是 Brand Template。要用
  `edit-design` 的 `update_autofill_field` 幫每個文字框掛欄位名(p1_headline、p2_body…),
  再 `publish-brand-template`。**沒做這步,明天的房仲包還是要重來一次同樣的組版流程。**
- 字型配對(serif-led)未套用,見限制 1。

⚠️ 先前估的「autofill 之後每組上字 ~5 分鐘」**尚未驗證**。第一份模板是手工組出來的,花了約二十趟 API。
tag + publish 之後才知道真實速度。

## 2026-07-26(續):autofill 已 tag 並發成 Brand Template

**Brand Template `EAHQd4F-edo`**(「Sophisticated Brand Positioning Instagram Carousel」),
dataset 21 個欄位全部生效,`search-brand-templates(dataset:"non_empty")` 查得到:

```
card1_kicker / card1_number / card1_headline / card1_logo
card2_kicker / card2_body   … card5_kicker / card5_body
card6_pause
card7_kicker / card7_body
card8_kicker / card8_takeaway
card9_logo / card9_cta / card9_secondary / card9_hashtags
```
頁碼與封面滑動提示**刻意不 tag**(每組都一樣,tag 了只是增加填表負擔)。

### 三件實測出來的事

1. **`publish-brand-template` 會回錯誤但其實已經成功。** 訊息是
   `Not allowed to access brand template with id 'EAHQd4F-edo'` —— 那是發佈後「回讀」的權限問題,
   模板本身已建立、dataset 也正確。**不要因為看到這個錯誤就重跑發佈**,先用
   `search-brand-templates(dataset:"any")` 確認。
2. **這個 connector 沒有 `autofill-design` 工具。** 其他工具的說明文字有提到它,但實際可用清單裡沒有。
   所以「餵一列資料 → 自動產一份設計」目前**不能全程由程式跑完**。兩條替代路:
   (a) SS 在 Canva 介面用 Bulk Create + CSV(dataset 已經在,這條可用);
   (b) 我用 `create-design-from-brand-template` 複製九頁,再逐頁 `replace_text`
       —— 省掉全部排版工,約 10 趟 API(從零組版是約 20 趟),但不是一鍵。
3. ⚠️ **一個結構一個母模板,不是一個行業一個。** dataset 綁在版面上,
   `列表款×靜謐拱窗編輯誌` 是 9 頁,7/27 的 `金句款×模組方格` 是 6 頁、版面也不同 —— **套不進去**。
   → 正確的量產計畫是:**先做 7 個母模板(一個 STORY_STRUCTURE 一個)**,
   之後九個行業就只是換資料。做完 7 個,行業包才真的變便宜。

## 2026-07-26(深夜):第一組完整成品做完 —— 商業教練 9 張,背景+文字都到位

**設計**:`DAHQeQnrU7M`(從 Brand Template `EAHQd4F-edo` 複製出的工作副本)。
**Brand Template 已更新**:`EAHQfHucRM8`(21 欄位 dataset 生效,`get-brand-template-dataset` 驗證過)。
成品 PNG 存 `SonaSNS-Platform/IGcarousell/Template/20260726-coach-list-quietarch/final_cards/`。

### 圖片託管:公開 URL 只吃得動一種格式

Canva 的 `upload-asset-from-url` **只接受直接回 200 的 URL,不能是簽名重導向**:
- GitHub Release 附件的下載連結是 302 轉址到 Azure blob 簽名 URL —— `curl` 抓得到、Canva 抓不到,
  9 次全部 `fetch_failed`(即使簽名 URL 本身立即用 curl 驗證仍是 200)。懷疑是 Canva 的抓取器
  不跟 redirect,或不接受 `Content-Type: application/octet-stream`。
- 改用 **`raw.githubusercontent.com`**(plain 200、`Content-Type: image/png`)全部成功。
→ **以後餵圖給 Canva,一律用 raw.githubusercontent.com,不要用簽名轉址連結。**

新建了一個**專用的暫存 repo**:`sssunwl/canva-scratch-assets`(public)——不放進 `saidio` 本身,
因為 `saidio` 有「repo 只存文字不存媒體」的規則(Footage 教訓)。這個 scratch repo 就是給
Canva 連接器抓公開圖用的丟棄式空間,以後每個行業包都可以往這丟,定期清空即可。

### 一個真的會炸的坑:editing transaction 會過期,而且過期不會告訴你

開一個 `read-design(open_transaction:true)` 之後,如果中間插了太多其他呼叫(對話被中斷、
工具暫時不可用之類),**transaction 會悄悄過期**,之後的 `edit-design` 全部回
`Editing transaction ... not found`。更糟的是:**過期前已經做的所有 insert/layer 都不會保留**,
因為從頭到尾沒有呼叫 `commit`——回頭 `read-design` 會發現設計整個打回原形。
這次因此把 4 頁的背景插入工作重做了一次。

→ **教訓:每處理完 2–3 頁就呼叫一次 `commit`**,不要囤到最後一次性 commit。
`layer_element` 需要 `insert_fill` 回傳的 element_id,所以每頁至少要兩次 `edit-design` 呼叫
(插入一次、疊層一次),抓緊時機盡快 commit。

### 產品邏輯的坑:CTA 卡不能自己選深色底

原始手工版第 9 頁(CTA)是我自己選的深咖啡實色底 + 淺色字,但母圖系統的整條 strip
只有**一個色票**(這正是「同一組必然統一」的設計初衷)。貼上母圖切片後,CTA 卡背景
從深咖啡變成跟其他 8 張一樣的暖米色,淺色字整個讀不出來。
**修法**:CTA 卡文字改用跟其他卡一樣的深墨色(`#5C4433`/`#8F6342`/`#A89078`),
不再假設 CTA 卡背景會不一樣。**以後手工組模板,CTA 卡不要另外挑背景色**,
要嘛在母圖規則裡明講「最後一張要深色」,要嘛就跟其他卡同色——目前選了後者。

### Canva `publish-brand-template` 這次不是同一種假錯誤

之前(7/26 稍早)發佈完的「無法存取」錯誤是假警報,`search-brand-templates` 馬上就查得到。
**這次不一樣**:發佈後回的錯誤裡新 id 是 `EAHQfHucRM8`,但 `search-brand-templates` 完全不列出它、
只列出舊的 `EAHQd4F-edo`(內容還是最初沒背景的版本)。用 `get-brand-template-dataset(EAHQfHucRM8)`
直接查才確認新版真的存在、21 欄位都在——**search 的索引比實際建立慢,不能只憑 search 判斷發佈成功與否**,
要用 `get-brand-template-dataset` 直接戳 id 才準。

## 2026-07-26(再晚):線稿類母圖改成 Canva 原生向量畫,不再外部生圖

SS 兩個回饋都是對的,而且指向同一個結論:
①「三個風格背景都長一樣」——生圖工具收斂成同一種調性,換 prompt 文字沒有真的換出風格差異;
②「你能操控 Canva,為什麼不直接在裡面做」——問得對。

**改用 `insert_shape` 直接畫向量拱門**,不再靠 ChatGPT Images/Imagen 生背景圖再貼進 Canva。
拱門是一條 SVG path(`M0 H L0 r A r r 0 0 1 W r L W H`,r=width/2 畫出正圓弧),
`insert_shape` 支援 M/L/A 指令,半圓拱門一次到位、線條保證銳利(向量,不是點陣放大)。

**好處是三個問題一次解決**:
- 不會糊(向量沒有「放大倍率」這回事)
- 不會漂移(座標自己算,要多準有多準)
- 不用託管(不用建 scratch repo、不用簽名網址、不用煩惱 Canva 抓不抓得到)

**「每張都一樣很難賣」也是對的**——第一次只做了一張範例就急著問方向,等於自己也犯了同一個錯。
補救:9 張全部重做,同一套語言(線色 `#B8996F`、同一排版)但構圖各自不同——
大拱門/單拱門(左右各一次,鏡射)/雙拱門/小拱門/無拱門(視覺停頓卡故意留白)/窄長拱門/
置中小拱門(收束卡)/實心色塊(CTA 卡,唯一填滿的一張,標記收尾)。
位置用「清空區」原則手算(避開既有文字的 bounding box),不是憑感覺亂擺。

**這對系統的結論**:線稿/幾何類視覺語言(這款、瑞士方格、展間掛牌都算——這三款母圖規則本來就
只有線條沒有照片)**以後直接向量畫,不進 `segment_plate_prompt()` 那條外部生圖的路**。
分段生成/seam report/scratch repo 那整套仍然保留,但只留給**真的需要照片質感或複雜紋理**的
未來款式——目前九個買家行業裡還沒有一個非得靠外部生圖不可,所以短期內這條路可能都用不到。

新設計 id `DAHQgWZnzi8`(從 Brand Template `EAHQfHucRM8` 複製出的最新工作副本)。
成品 PNG 存 `SonaSNS-Platform/IGcarousell/Template/20260726-coach-list-quietarch/vector_final/`。

⚠️ **這個 design id 之後大概率也會在下次 publish 後失效**(第三次遇到同樣模式:
publish-brand-template 之後,原本的工作 design 就讀不到了)。下次要接著改,
先用 `create-design-from-brand-template(最新模板id)` 生一份新副本再開始,
不要嘗試回頭改舊的 design id。
