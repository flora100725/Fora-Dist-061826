M-ARCH-0616 TFDA Compliance Hub（v2.5.0-WOW-AI-ExpansionPack）
技術規格書（更新版：納入「Symmetric Medical Supply Chain & UDI Ledger Auditing Ecosystem」能力）
文件語言：繁體中文（預設）
部署目標：Hugging Face Spaces（Streamlit）為主，企業版可延伸至 Node.js/React 全端
整合 API：Gemini / OpenAI / Anthropic / XAI（多供應商可切換，支援無金鑰備援規則引擎）
核心檔案：app.py、agents.yaml、SKILL.md、使用者上傳資料（CSV/JSON/PDF/圖片/文字）
法規對齊：TFDA 醫療器材管理法、TUDID、（可選）FDA 21 CFR Part 801.20 UDI

1. 執行摘要與法規框架（Executive Summary & Regulatory Framework）
1.1 計畫目標（Programmatic Objective）
本系統為「高風險、生命攸關」醫療器材（例如植入式心律調節器、人工關節、植入式幫浦等）打造一套零信任（Zero-Trust）、雙向對帳（Symmetric Reconciliation）、**證據級（Evidence-Grade）**的供應鏈稽核與召回作業平台。其核心價值不是單純的資料儀表板，而是將下列工作一體化：

供應鏈全生命週期可視化：從經銷商出貨申報 → 醫院驗收/入庫 →（可選）臨床使用/植入前盤點 → 退貨/回收
雙向對帳（Symmetric Ledger）：同一設備（以 UDI-PI / SN 為核心）在「出貨帳」與「驗收帳」必須可互相驗證
合規驗證與異常偵測：過期許可證、序號重複（疑似一物二賣/灰市注入/偽造）、時間倒置（收貨早於出貨）、單位/數量不一致、地理圍籬漂移
證據鏈與可重現 AI：所有 AI 生成內容具備可追溯的 AI Trace、所有證據檔案具備 SHA-256 指紋與版本化
召回與應變（ROPG）：將偵測結果轉成可執行的召回劇本（playbook）、任務清單與結案標準
關鍵設計哲學：
「資料不可信」是常態（噪音、後修、編碼後綴、欄位漂移），因此系統必須以雙向對帳 + 證據鏈 + 人在回路（Human-in-the-loop）保證行政處分與召回決策的可辯護性。

1.2 合規矩陣（TFDA / FDA UDI Requirements）
系統將每筆流向紀錄與證據解析統一落在 UDI 的結構化定義上：

UDI-DI（Device Identifier）：靜態、對應製造商/型號/品牌（例如 GTIN 或其他 DI）
UDI-PI（Production Identifier）：動態生命週期參數
序號（SN / Serial）：單品追蹤的核心
批號/批次（Lot/Batch）
有效期限（EXP）
製造日期（MFG）
系統的稽核引擎會以 UDI 觀念將「出貨帳」與「驗收帳」進行對稱驗證，並將結果映射到法規與行政流程的輸出（稽核報告、函文草案、召回作業指引）。

2. 全域架構（Global Architecture）：Symmetric Ledger + AI Compliance Hood
2.1 核心方塊圖（平台級）
+--------------------------------------------------------------------------------------------------+
|                             Symmetric Medical Supply Chain & UDI Auditing Ecosystem              |
|                                                                                                  |
|  [Distributor Ledger] --(UDI-DI/UDI-PI/Permit/Date/Qty checks)--+                                 |
|                                                                v                                 |
|                                +-------------------------------+------------------------------+  |
|                                |         Symmetric Audit Engine (Zero-Trust Reconciliation)   |  |
|                                |  - Matched Pairs / Unmatched Inflow / Unmatched Outflow       |  |
|                                |  - Duplicate Serial / Timeline Inversion / Expired Permit     |  |
|                                |  - Qty/Unit Mismatch / UDI Structure checks                    |  |
|                                +-------------------------------+------------------------------+  |
|                                                                |                                 |
|                                                                v                                 |
|    [Clinical Intake Ledger] --(UDI-DI/UDI-PI/Permit/Date/Qty checks)--+                           |
|                                                                                                  |
|  +------------------+  +--------------------+  +--------------------+  +---------------------+   |
|  | GIS & Geofencing |  | Simulation & NPDO  |  | Evidence Graph EGEL |  | Recall Console ROPG |   |
|  +------------------+  +--------------------+  +--------------------+  +---------------------+   |
|               \                |                      |                      /                   |
|                \               v                      v                     /                    |
|                 +----------------------- AI Compliance Hood ----------------+                     |
|                 | Multi-Provider LLM + Fallback Rules + AI Trace (AIET)     |                     |
|                 +-----------------------------------------------------------+                     |
+--------------------------------------------------------------------------------------------------+
2.2 部署型態：Streamlit（Spaces）為主、企業全端可擴展
A. HF Spaces / Streamlit 版本（本次交付核心）

單一 app.py 提供 UI、資料上傳、異常偵測、代理人工作台、證據/召回模組
以 session_state 管理狀態；無 API Key 時以規則/模板備援
適用：快速稽核、示範、內部專案協作、低成本部署
B. 企業版 Node.js/React 參考架構（對齊你提供的 Symmetric 規格）

React/Vite 前端：資料分頁、useMemo、虛擬化列表
Express API Proxy：保護金鑰、串流輸出、長任務排程（OCR/影像）
適用：大量資料（10^5～10^6 行）、多使用者、RBAC、不可否認稽核
本技術規格書採「平台能力一致、部署形式可替換」原則：資料模型、稽核邏輯、證據鏈、AI Trace、召回劇本在兩種部署應保持一致。

3. WOW UI 與前端呈現層（Presentation Layer）
3.1 WOW UI：主題、語言、Pantone 風格、Jackpot
系統提供：

亮/暗主題（Sleek Light / Sleek Dark）
語言切換：英文 / 繁體中文（預設）
Pantone 風格 10 套（近似配色），並支援 Jackpot 隨機套用
所有核心視覺元件（按鈕、面板、徽章、警示）以 CSS Token 化，避免不同模組各自配色造成稽核疲勞
3.2 WOW 可視化：LLM 執行流程、互動指示器、Live Log、互動儀表板
互動指示器（Interactive Indicator）：代理人逐步執行的進度、狀態（Running/Complete/Fallback）
Live Log：上傳證據、異常偵測、召回模擬、AI 呼叫均有時間戳記
AI Trace（AIET）面板：每次呼叫的 provider/model、延遲、prompt/輸出指紋、錯誤回退原因（不含金鑰）
4. 核心資料型態與擴充模型（Data Modalities & Schema）
4.1 雙帳本資料（Distributor / Clinical Intake）
延續既有 M-ARCH 資料結構（DistributionItem / PurchaseItem），並吸收 Symmetric 規格的欄位觀念（udi_di、serial_no、batch_no）。系統內部將欄位統一映射成標準欄位集：

交易識別：no / id、reporter/declarant、target/customer/supplier
時間欄位：deliveryDate / receiveDate（均正規化為 YYYYMMDD 或 ISO）
合規欄位：permitNo/license_no、udiDi/udid（DI/完整碼）、modelNo
生命週期欄位：serialNo、batchNo、mfgDate、expDate、quantity、unit
4.2 證據與鑑識資料（Artifacts / CGFS）
為支援 CGFS 與 EGEL，新增統一證據檔案模型（Artifact）：

artifact_id（UUID）
檔名、MIME、大小、sha256
tags：可包含 anomaly_id、serial_norm、permitNo
狀態：UPLOADED / EXTRACTED / REVIEWED / EXPORTED
解析結果（可選）：OCR 文字、欄位候選、信號分數卡
4.3 證據圖譜（EGEL）與 AI Trace（AIET）
EGEL Graph Snapshot：node/edge 清單（可輕量在 Streamlit 顯示）
AIET：每次 AI 任務的最小可稽核欄位
provider / model / latency
prompt_fingerprint / output_fingerprint
status（OK / FALLBACK_NO_KEY / FALLBACK_ERROR）
可選：artifact_id / anomaly_id 參照
5. 資料匯入、清洗與正規化管線（CSV / JSON / PDF / 影像）
5.1 結構化資料（CSV/JSON）匯入管線
吸收 Symmetric 規格的「Header Mapper + Standardization Engine」概念，系統的匯入流程分為：

檔案解析：CSV/JSON 讀取，處理編碼與引號
欄位映射：將「序號/編號/ID」→ id/no；「交貨日期/收貨日期」→ deliveryDate/receiveDate
資料標準化
日期：2026-06-18、20260618、民國年（可選）→ YYYYMMDD
數值：quantity 轉整數；缺失值標記 N/A
識別碼正規化（Serial Normalization）
去除斜線段、空白、符號、院內後綴碼
產生 serial_norm 作為對帳核心鍵
5.2 非結構化證據（PDF/文字/圖片）
PDF：抽取文字（pypdf），並對前 N 頁設上限以避免記憶體爆掉
文字：直接輸入/上傳（txt/md）
圖片：本版可先保存為 Artifact；若未啟用 OCR，則提供「需安裝 OCR 依賴」提示（企業版可接 CV-ULA）
6. 雙向對帳稽核引擎（Bi-Directional Symmetric Reconciliation Audit Engine）
6.1 對帳核心：Matched / Unmatched Inflow / Unmatched Outflow
以 serial_norm 為主鍵（可擴展到 serial+UDI-DI+batch 多欄比對），產生三種集合：

Matched Pair（對稱匹配）：出貨與驗收互相找到對應
Unmatched Inflow（灰市注入疑慮）：醫院驗收存在，但授權出貨帳無對應
Unmatched Outflow（轉運/遺失/未登錄）：出貨存在，但醫院未驗收/未登錄
同時檢查：

quantity/unit 不一致（部分出貨、拆箱、或資料錯誤）
permitNo 在時間窗口內是否過期
時間倒置（receive < delivery）
6.2 異常類型（Minimum Set）
保留既有並擴充至 Symmetric 的稽核語意：

DUPLICATE_SERIAL（序號重複）
TIMELINE_INVERSION（時間倒置）
EXPIRED_PERMIT（過期許可證）
UNIT_MISMATCH / QTY_MISMATCH（單位/數量）
ORPHAN_SERIAL（孤兒序號：單邊存在）
GEOFENCE_DRIFT（地理圍籬漂移，企業版/可選）
BIO_ANOMALY（數位孿生/遙測異常，企業版/可選）
6.3 合規分數（Deterministic Compliance Score）
沿用「未解決異常扣分」機制，並建議加入「證據強度修正」：

Severity penalty：CRITICAL/HIGH/WARNING
Evidence modifier：Strong/Moderate/Weak（由 EGEL/CGFS 綜合）
目的：避免僅靠資料噪音造成過度扣分；也避免在證據不足下直接行政處置
7. GIS 地理投影與物流視覺化（Geospatial System）
7.1 兩種呈現路徑：Leaflet/地圖瓦片 vs SVG 投影
**Streamlit 版本（本次）：**以 pydeck scatter layer 近似呈現站點與活躍度
**React/SVG 企業版（Symmetric 規格）：**採線性插值投影至 SVG viewport，具備低成本、免外部地圖 key 的優勢
7.2 動態連線與物流動畫（企業版能力）
沿用 Symmetric 規格中的 <animateMotion> 概念，將「出貨→收貨」或「調撥→目的地」以虛線與動點顯示，支援：

依頻率/數量調整線寬與顏色
與 ROPG 召回範圍疊加顯示
與 Dynamic Rebalancer 的路徑建議疊加
8. 離散事件模擬與壓力引擎（Simulation & Stress Engine）+ NPDO
8.1 基礎庫存演算（Deterministic）
維持既有「每日流入/流出」模型，用於推估何時低於安全庫存線，並可觸發：

風險警示（LOW STOCK / CRITICAL_ALERT）
進一步觸發 MAIS 協商式調撥（企業版）或 AI 行動建議
8.2 NPDO：神經需求預測編排（Proposed Upgrade）
新增 NPDO 作為模擬輸入的升級來源：

融合手術排程、季節/天候、公共衛生指標
輸出 30/60/90 天需求曲線與信賴區間
在 UI 上以雙線（基準 vs NPDO）比較，並標註異常峰值的原因（riskFactor_reason）
9. AI 能力層（AI Compliance Hood）：多供應商、可重現、可回退
9.1 模型路由與工作型態
快速結構化/解析：flash/mini 類
深度推理/報告：pro/sonnet 類
規格要求：任何 AI 輸出若解析失敗或金鑰不存在，必須回退到可重現模板，以維持系統可用性與稽核一致性
9.2 API Key 策略（符合你的要求）
若環境變數已有金鑰：UI 不顯示、不要求輸入、不回顯
若環境無金鑰：提供頁面 password 欄位輸入，僅存 session，不記錄到 log/trace 明文
9.3 代理人工作台（Agentic Workbench）
執行代理人可在執行前修改 prompt、max_tokens（預設 12000）、模型
代理人逐一執行：每步輸出可切換 Markdown/Text
輸出可編輯後作為下一代理人的輸入（Human-in-the-loop chaining）
agents.yaml 在 App 內可貼上/上傳/下載/標準化再匯入（避免欄位錯誤造成崩潰）
10. WOW 模組整合（新增 + 既有）：EGEL、CGFS、ROPG + MAIS、CV-ULA + 既有三大進階
本版同時包含你先前的進階模組（6.1～6.3）與新增（6.4～6.6），並吸收 Symmetric 規格提出的三項擴展（NPDO/MAIS/CV-ULA）。

10.1 6.1 法規修正監測與函文生成（Law Watchdog）
定期抓取 TFDA/WHO 公告（RSS/XML）
將新規範轉為可比對條件（permit 範圍、品項類別、時效）
產出：政策警示、函文草案（可編輯）、自動掛載到 EGEL 作為證據節點
10.2 6.2 數位孿生遙測風險（Digital Twin Predictor）
解析裝置遙測（阻抗、閾值、電壓）
產出 BIO_ANOMALY，但不提供病患個人醫療建議
作用：將「物流稽核」與「設備完整性」風險連結到召回門檻與隔離策略
10.3 6.3 動態補貨與地理圍籬（Dynamic Rebalancer）
將 GIS 路徑與庫存預測結合，提供調撥方案
可輸出路徑向量與檢查點（geofence checkpoints）
10.4 6.4 EGEL：證據圖譜與可解釋帳（Evidence Graph & Explainability Ledger）
**目的：**讓「為何判定異常」具備可視化證據鏈與可稽核解釋。
能力：

節點：異常、序號、許可證、機構、交易、Artifact、AI 輸出、人工處置
邊：SUPPORTS / REFERS_TO / CONFLICTS_WITH
產出：可引用的「證據備忘錄（Evidence Memo）」與「Evidence Pack 匯出」
人因設計：
所有自動連結必須標記信心等級（High/Med/Low），預設需要人工確認才能成為「已驗證」證據。

10.5 6.5 CGFS：灰市/偽造鑑識工作室（Counterfeit & Grey-Market Forensics Studio）
**目的：**將稽核從表格延伸到文件/標籤/包裝。
**輸入：**PDF 發票、出貨單、證明文件、（可選）包裝照片
輸出：「信號分解式」鑑識卡（不下定論，僅提供可驗證的可疑信號）：

permit/日期/序號候選欄位抽取
文字異常：可疑間距、斜線拼接、同形異字
文件模板重複線索（多份不同供應商文件版式高度相似）
與帳冊對照不一致（permit mismatch / serial collision / date mismatch）
所有結果可回寫到 EGEL 作為 evidence nodes，並可被 ROPG 召回範圍引用。

10.6 6.6 ROPG：召回控制台與作戰劇本（Recall Orchestrator & Playbook Generator）
**目的：**把偵測結果轉成「可執行的召回行動」。
流程：

定義範圍（serial-only / permit-based / batch-based / 地理擴張）
決定性（deterministic）影響評估：受影響機構、筆數、序號清單
生成 playbook（AI 可選）：分階段任務、函文草案、結案標準
追蹤執行：任務狀態、稽核軌跡、Evidence Pack 匯出
硬性規格：
影響範圍計算必須 deterministic；AI 只能提供敘述與替代情境（需明確標註）。

10.7 MAIS：多代理人互動協商與自動調撥契約（Proposed）
當模擬引擎偵測某院低於安全庫存線，觸發協商代理人：

Broker 代理人負責召集周邊機構供需資訊
產出調撥路由與「結構化調撥協議草案」
並更新 GIS 路徑動畫與庫存推估
10.8 CV-ULA：電腦視覺輔助 UDI/標籤稽核（Proposed）
於驗收端用手機/掃描器拍照上傳
多模態模型進行 OCR + 標籤/包裝完整性檢查
與帳冊與（可選）外部 UDI 資料庫比對
輸出結構化 JSON：抽取的 udi_di、serial、exp、lot、包裝是否破損與建議措施
在本次 Streamlit 版本可先以「Artifact 保存 + 待 OCR 啟用」方式落地
11. AI Note Keeper（保留原功能並強化）
使用者可貼文字/Markdown 或上傳 PDF/txt/md
系統可轉成結構化 Markdown
關鍵字上色：預設珊瑚色（coral），並支援自選顏色與自定關鍵字（AI Keywords）
提供 6 個 AI Magics（整理、摘要、待辦、卡片、稽核語氣、翻譯）
加上 3 個 WOW Magics（EGEL Memo / CGFS Signals / ROPG Playbook）
12. 安全、治理、可稽核（Security, Governance, Auditability）
12.1 Zero-Trust 與證據鏈（Chain-of-Custody）
Artifact 必須有 SHA-256，任何修改視為新版本
匯出 Evidence Pack 時必須包含 manifest（artifact_id → sha256 → timestamp → tags）
AIET（AI Trace）必須可匯出，用於重現模型呼叫的指紋級證據
12.2 Prompt Injection 防護
上傳文字視為不可信資料，只能作為引用/摘要，不可當作指令
代理人 System Prompt 必須把「不執行未授權指令」寫入 guardrails
對外匯出預設啟用敏感資訊遮罩（PII/PHI）
12.3 金鑰與資料外洩防護
金鑰只存在環境變數或 session password 欄位
Live log / trace 嚴禁輸出金鑰明文
若未配置 key：系統仍可完整跑完對帳、異常、召回 deterministic 計算
13. 效能、擴充與取捨（Performance, Scaling, Trade-offs）
13.1 前端效能（企業版/React 對齊 Symmetric 規格）
useMemo、分頁、虛擬化列表（react-window）
GIS 路徑多於 5,000 時改 Canvas 渲染
Tab 動態掛載以避免不必要的 re-render
13.2 Streamlit（Spaces）效能策略
上傳檔案大小上限與頁數上限
對 DataFrame 展示採 head(n) 與欄位篩選
長任務採 status/progress 呈現；失敗可回退
14. 匯出與交付物標準（Exports & Deliverables）
14.1 必要匯出
note.md（AI Note Keeper）
agents.yaml（標準化後）與 SKILL.md
Evidence Memo / Recall Playbook（Markdown）
Evidence Pack（建議企業版以 zip + manifest 落地）
14.2 報告格式要求（稽核級）
必須區分：已確認事實 / 不一致 / 假說 / 待補證據
必須包含引用：anomaly_id、artifact_id、sha256、serial_norm、permitNo
必須提供結案標準（Closure Criteria）與復原分數條件
15. 更新後的系統模組清單（整合視圖）
Dataset Manager：CSV/JSON 匯入、欄位映射、正規化
Symmetric Audit Engine：雙向對帳、異常、合規分數
GIS / Geofencing：站點、活躍度、（可選）路徑動畫與圍籬
Simulation & NPDO：庫存壓力、需求預測
Agentic Workbench：30 代理人、逐步執行、可編輯串接
AI Note Keeper：整理筆記、關鍵字上色、WOW Magics
CGFS：鑑識信號、欄位抽取、與帳冊對照
EGEL：證據圖譜、解釋備忘錄、Evidence Pack
ROPG：召回模擬、劇本、任務、匯出
Config Editor：agents.yaml / SKILL.md 貼上/上傳/下載/標準化
AIET + Live Log：可重現、可追溯、可稽核
16. 20 個全面性的後續追問（工程 / 法規 / 產品驗收）
Symmetric 對帳規則：在你們的實務流程中，對帳主鍵是「serial_norm」即可，還是必須升級為「serial_norm + UDI-DI + lot/batch + expDate」的多鍵匹配才合規？
欄位漂移治理：不同醫院/經銷商 CSV 欄名變化很大時，Header Mapper 的對照表由誰維護、如何版本化與回溯？
民國年/多格式日期：是否要求全面支援民國年（如 115/06/18）轉西元？若支援，法規稽核輸出採哪一種格式為主？
Unmatched Inflow 的處置門檻：出現「醫院驗收有、出貨帳無」時，是否直接列為高風險（灰市），還是需要滿足特定證據強度才升級？
數量/單位不一致：若醫院拆箱把 1 box 變成多個序號零件登錄，對帳引擎應如何定義合法拆分規則與例外處理？
合規分數校準：目前扣分權重是否需要依你們內規或 TFDA 稽核慣例調整？是否要加入「證據強度」加權以降低噪音誤判？
證據鏈要求：你們是否需要「不可否認」等級的匯出（例如 hash-chained audit log 或數位簽章），以便行政處分或訴訟舉證？
Artifact 保留策略：在 HF Spaces（短暫容器）下，是否要強制使用者在關閉前匯出 Evidence Pack？企業版是否需要長期保管與自動歸檔？
CV-ULA 落地優先序：你們最需要的是「OCR 抽取 UDI/序號」還是「包裝破損偵測」？對於誤判率可接受門檻為何？
OCR/影像依賴：是否允許安裝 tesseract/opencv 等系統依賴？若不允許，是否改採外部 OCR API（但會增加資料外傳風險）？
EGEL 圖譜互動：你們希望證據圖譜是輕量 JSON 檢視即可，還是必須做成可點擊、可篩選、可拖曳的力導向圖（需較多前端工程）？
CGFS 信號定義：哪些「可疑信號」被你們視為強信號（High），哪些只能是提醒（Warning）？是否需要可配置的信號規則庫？
MAIS 自動化界線：多代理人協商調撥是否可以「自動生成協議草案」但仍需人工批准？是否允許自動更新庫存/路徑（通常不建議）？
ROPG 召回範圍擴張：召回擴張規則（permit-based / batch-based / 地理半徑）在你們作業準則中哪些是允許的？誰有權限啟用？
召回劇本的任務系統：ROPG 任務是否需要匯出成 CSV 對接 Jira/ServiceNow，或必須與你們既有內控系統整合？
法規引用正確性：是否需要一份「可引用法規條文白名單」以降低模型幻覺？法規更新由誰審核後才能進入 Law Watchdog？
多供應商模型治理：案件進行中是否允許切換 provider/model？若允許，是否要在 AIET 中強制記錄並在報告中揭露？
Prompt Injection 稽核：是否需要在每次證據摘要前先跑「注入風險掃描」代理人（例如你 30 agents 中的安全角色）作為強制關卡？
資料量級目標：你們的實際資料量（每月交易行數、證據檔數）上限是多少？這將決定是否必須採用資料庫、索引與背景任務佇列。
驗收測試（UAT）：你們是否能提供「黃金資料集」（含已知重複序號、過期許可、時間倒置、灰市注入樣例）用於建立可重現的回歸測試與交付驗收標準？
