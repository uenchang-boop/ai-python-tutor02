"""
Prompt 模板 — AI Python Code Tutor 第 2 輪

包含：
  FUNCTION_EXPLAIN_PROMPT  — 函數解釋（主要）
  CLASS_EXPLAIN_PROMPT     — 類別解釋（第 3 輪用）
  IMPORT_EXPLAIN_PROMPT    — 套件解釋（第 3 輪用）
"""

# ── 函數解釋 Prompt ───────────────────────────────────
FUNCTION_EXPLAIN_PROMPT = """你是一位 Python 程式教育專家，專門幫助完全沒有程式背景的新手理解程式碼。

請分析以下 Python 函數，並回傳 JSON 格式的解釋：

```python
{code_snippet}
```

請嚴格按照以下 JSON 格式回傳（不要加任何 markdown 標記、不要加 ```json、純文字 JSON）：
{{
    "definition": "用一句話說明這個函數的功能（15字以內，繁體中文）",
    "guide": "用生活化的比喻解釋這個函數在做什麼（30-50字，想像你在跟完全不懂程式的朋友解釋，繁體中文）",
    "icon": "一個最能代表這個函數功能的 emoji（只給一個）",
    "params_explain": [
        {{"name": "參數名稱", "explain": "這個參數代表什麼（10字以內，繁體中文）"}}
    ],
    "return_explain": "回傳值是什麼（10字以內，繁體中文；如果沒有回傳值就寫 無）",
    "complexity": "simple"
}}

complexity 的值只能是：simple（10行以內）、medium（10-30行）、complex（30行以上）。
params_explain 如果函數沒有參數（或只有 self），給空陣列 []。
只回傳 JSON，不要有任何其他文字。"""


# ── 類別解釋 Prompt（第 3 輪使用）────────────────────
CLASS_EXPLAIN_PROMPT = """你是一位 Python 程式教育專家，專門幫助新手理解物件導向程式設計。

請分析以下 Python 類別，並回傳 JSON 格式的解釋：

```python
{code_snippet}
```

請嚴格按照以下 JSON 格式回傳（純文字 JSON，不要加 markdown 標記）：
{{
    "definition": "用一句話說明這個類別的功能（20字以內，繁體中文）",
    "guide": "用生活化的比喻解釋這個類別代表什麼（30-50字，繁體中文）",
    "icon": "一個最能代表此類別功能的 emoji（只給一個）",
    "purpose": "這個類別在程式中扮演什麼角色（20字以內，繁體中文）"
}}

只回傳 JSON，不要有任何其他文字。"""


# ── 套件解釋 Prompt（第 3 輪使用）────────────────────
IMPORT_EXPLAIN_PROMPT = """你是一位 Python 教育專家，請用繁體中文、新手能懂的方式解釋這個 Python 套件。

套件名稱：{package_name}

請嚴格按照以下 JSON 格式回傳（純文字 JSON，不要加 markdown 標記）：
{{
    "description": "一句話說明這個套件的用途（15字以內，繁體中文）",
    "guide": "用生活化的比喻解釋這個套件做什麼（30字以內，繁體中文）",
    "category": "套件類型（如：資料處理、網路請求、視覺化、測試、Web框架 等）",
    "icon": "最能代表此套件的 emoji（只給一個）"
}}

只回傳 JSON，不要有任何其他文字。"""


# ── 逐行中文注解 Prompt ───────────────────────────────
LINE_ANNOTATE_PROMPT = """你是一位 Python 程式教育專家，專門幫助完全沒有程式背景的新手。

請對以下每一行 Python 程式碼加上繁體中文注解（使用 # 符號），規則如下：
1. 注解加在該行右側，以 # 開頭
2. 每條注解 15 字以內，用新手也能懂的白話文
3. 空行不需要注解
4. 保留原始縮排，不要更動程式碼本身
5. def 行也要注解（說明這個函式做什麼）
6. 只回傳加注解後的完整程式碼，不要任何其他說明文字

程式碼如下：
{code}"""
