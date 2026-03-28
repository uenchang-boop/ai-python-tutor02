# 🐍 AI Python Code Tutor v0.4.0

> 貼上程式碼 → 秒懂每個函數在做什麼  ·  由 AI 驅動

## 功能一覽

### 第 1 輪 — 核心解析 + UI 骨架
- ✅ AST 解析函數定義（參數、裝飾器、docstring、原始碼）
- ✅ 函數呼叫關係分析
- ✅ Claude 風格 UI（米白背景、琥珀色強調）
- ✅ 離線關鍵字模板解釋

### 第 2 輪 — AI 整合 + 快取
- ✅ Claude API / Gemini API 雙模式
- ✅ SHA256 快取機制（TTL 7 天）
- ✅ Token 費用追蹤與即時顯示
- ✅ API Key 設定側邊欄

### 第 3 輪 — Class 解析 + Import 百科
- ✅ 類別解析（繼承、方法、類別變數、裝飾器）
- ✅ 階層式 UI 顯示（類別 → 方法樹狀結構）
- ✅ Import 百科（50+ 常見套件內建說明）
- ✅ 未知套件 AI 線上查詢

### 第 4 輪 — 流程圖 + 新手引導
- ✅ **Mermaid.js 流程圖**
  - 🔗 函數呼叫流程圖（graph TD）
  - 🏛️ 類別繼承圖（classDiagram）
  - ⏱️ 執行順序圖（sequenceDiagram）
- ✅ **新手引導系統**（5 步驟互動引導）
- ✅ **圖示系統**（20+ 函數類型 emoji 對照）
- ✅ 雙範例按鈕（函數範例 / 類別範例）
- ✅ Mermaid 原始語法可展開查看

## 快速開始

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動應用
streamlit run app.py
```

## 專案結構

```
ai-python-tutor/
├── app.py                     # Streamlit 主程式
├── config.py                  # 全域設定
├── requirements.txt
├── README.md
│
├── parsers/                   # 程式碼解析
│   ├── function_parser.py     # 函數解析
│   ├── class_parser.py        # 類別解析
│   ├── import_parser.py       # Import 百科
│   └── call_graph.py          # 呼叫關係
│
├── ai/                        # AI 解釋
│   ├── explainer.py           # 雙模式 API
│   ├── prompts.py             # Prompt 模板
│   └── cache.py               # SHA256 快取
│
├── ui/                        # UI 元件
│   ├── theme.py               # Claude 風格 CSS
│   ├── components.py          # 函數/類別卡片
│   ├── sidebar.py             # 設定側邊欄
│   ├── onboarding.py          # 新手引導
│   └── icons.py               # 圖示系統
│
├── visualizer/                # 視覺化
│   └── mermaid_gen.py         # Mermaid 流程圖
│
└── cache/                     # 快取資料夾
```

## 支援的 API

| Provider | 模型 |
|----------|------|
| Claude   | claude-sonnet-4, claude-haiku-4.5, claude-opus-4 |
| Gemini   | gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro |
| 離線     | 內建關鍵字模板（無需 API Key） |

## 授權

MIT License
