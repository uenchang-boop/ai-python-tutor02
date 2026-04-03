"""
AI 解釋產生器 — 雙模式：Claude API + Gemini API

切換方式：在 ui/sidebar.py 選擇 API 提供者，
init_ai(api_key, model, provider) 會自動切換。

token 費用追蹤：每次 API 呼叫後累計到 session，
供 UI 顯示「本次查詢消耗費用」。
"""

import json
import re

from ai.cache import ExplanationCache
from ai.prompts import FUNCTION_EXPLAIN_PROMPT
from config import COST_PER_1K

# ── 全域狀態 ──────────────────────────────────────────
_cache:          ExplanationCache | None = None
_claude_client                           = None   # anthropic.Anthropic
_gemini_model                            = None   # genai.GenerativeModel
_current_model:  str                     = "claude-sonnet-4-20250514"
_current_provider: str                   = "claude"   # "claude" | "gemini"
_api_ready:      bool                    = False
_last_error:     str                     = ""

# ── 費用累計（本次 session）────────────────────────────
_session_cost = {
    "input_tokens":  0,
    "output_tokens": 0,
    "total_usd":     0.0,
    "api_calls":     0,
}


# ── 初始化 ────────────────────────────────────────────

def init_ai(api_key: str, model: str, provider: str = "claude") -> bool:
    """
    初始化 AI 客戶端。
    provider: "claude" | "gemini"
    回傳 True=成功。
    """
    global _cache, _claude_client, _gemini_model
    global _current_model, _current_provider, _api_ready, _last_error

    if _cache is None:
        _cache = ExplanationCache()

    _current_model    = model
    _current_provider = provider

    if not api_key or not api_key.strip():
        _api_ready  = False
        _last_error = "未輸入 API Key"
        return False

    # ── Claude ──────────────────────────────────────
    if provider == "claude":
        try:
            import anthropic
            _claude_client = anthropic.Anthropic(api_key=api_key.strip())
            _api_ready     = True
            _last_error    = ""
            return True
        except ImportError:
            _api_ready  = False
            _last_error = "請安裝套件：pip install anthropic"
            return False
        except Exception as e:
            _api_ready  = False
            _last_error = str(e)
            return False

    # ── Gemini ──────────────────────────────────────
    if provider == "gemini":
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key.strip())
            _gemini_model = genai.GenerativeModel(model)
            _api_ready    = True
            _last_error   = ""
            return True
        except ImportError:
            _api_ready  = False
            _last_error = "請安裝套件：pip install google-generativeai"
            return False
        except Exception as e:
            _api_ready  = False
            _last_error = str(e)
            return False

    _api_ready  = False
    _last_error = f"未知 provider: {provider}"
    return False


def get_cache() -> ExplanationCache:
    global _cache
    if _cache is None:
        _cache = ExplanationCache()
    return _cache


def is_api_ready() -> bool:
    return _api_ready


def get_last_error() -> str:
    return _last_error


def get_session_cost() -> dict:
    """回傳本次 session 的 token 費用統計。"""
    return dict(_session_cost)


def reset_session_cost() -> None:
    """重設費用計數器（每次重新分析時呼叫）。"""
    global _session_cost
    _session_cost = {
        "input_tokens":  0,
        "output_tokens": 0,
        "total_usd":     0.0,
        "api_calls":     0,
    }


# ── 主要 API ──────────────────────────────────────────

def generate_explanation(func_info: dict) -> dict:
    """
    產生函數解釋，回傳 dict：
      definition, guide, icon, params_explain,
      return_explain, complexity, source,
      token_cost(選填), error_msg(選填)
    """
    global _last_error

    cache = get_cache()
    code  = func_info.get("body", "")

    # 1. 查快取
    cached = cache.get(code)
    if cached:
        result           = dict(cached)
        result["source"] = "cache"
        return result

    # 2. 呼叫 AI API
    if _api_ready:
        try:
            if _current_provider == "claude":
                result = _call_claude(func_info, code)
            else:
                result = _call_gemini(func_info, code)

            cache.set(
                code,
                func_info.get("name", "unknown"),
                result,
                api_model=_current_model,
            )
            result["source"] = _current_provider
            return result

        except Exception as e:
            _last_error = f"{type(e).__name__}: {e}"

    # 3. 離線 fallback
    result               = _offline_template(func_info)
    result["source"]     = "template"
    result["error_msg"]  = _last_error
    return result


# ── Claude API 呼叫 ───────────────────────────────────

def _call_claude(func_info: dict, code: str) -> dict:
    """呼叫 Claude API，追蹤 token 用量。"""
    global _session_cost

    # 用 replace 避免 { } 被 .format() 誤判
    prompt = FUNCTION_EXPLAIN_PROMPT.replace("{code_snippet}", code)

    response = _claude_client.messages.create(
        model=_current_model,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    # ── 追蹤費用 ──────────────────────────────────
    usage        = response.usage
    in_tok       = getattr(usage, "input_tokens",  0)
    out_tok      = getattr(usage, "output_tokens", 0)
    cost_table   = COST_PER_1K.get(_current_model, {"input": 0, "output": 0})
    usd          = (in_tok / 1000 * cost_table["input"]
                  + out_tok / 1000 * cost_table["output"])

    _session_cost["input_tokens"]  += in_tok
    _session_cost["output_tokens"] += out_tok
    _session_cost["total_usd"]     += usd
    _session_cost["api_calls"]     += 1

    raw_text = response.content[0].text.strip()
    return _parse_ai_response(raw_text)


# ── Gemini API 呼叫 ───────────────────────────────────

def _call_gemini(func_info: dict, code: str) -> dict:
    """呼叫 Gemini API，追蹤 token 用量（估算）。"""
    global _session_cost

    import google.generativeai as genai

    prompt = FUNCTION_EXPLAIN_PROMPT.replace("{code_snippet}", code)

    generation_config = genai.GenerationConfig(
        temperature=0.3,
        max_output_tokens=800,
    )

    response = _gemini_model.generate_content(
        prompt,
        generation_config=generation_config,
    )

    # Gemini 費用估算（字元數 / 4 ≈ tokens）
    in_tok     = len(prompt) // 4
    out_tok    = len(response.text) // 4
    cost_table = COST_PER_1K.get(_current_model, {"input": 0, "output": 0})
    usd        = (in_tok / 1000 * cost_table["input"]
                + out_tok / 1000 * cost_table["output"])

    _session_cost["input_tokens"]  += in_tok
    _session_cost["output_tokens"] += out_tok
    _session_cost["total_usd"]     += usd
    _session_cost["api_calls"]     += 1

    return _parse_ai_response(response.text.strip())


# ── 共用 JSON 解析 ────────────────────────────────────

def _parse_ai_response(raw_text: str) -> dict:
    """清理並解析 AI 回傳的 JSON。"""
    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$",          "", raw_text.strip())

    data = json.loads(raw_text)
    data.setdefault("definition",     "執行特定任務邏輯")
    data.setdefault("guide",          "像一個專門工具，負責處理某件具體的事")
    data.setdefault("icon",           "🔧")
    data.setdefault("params_explain", [])
    data.setdefault("return_explain", "無")
    data.setdefault("complexity",     "simple")
    return data


# ── 離線關鍵字模板 ────────────────────────────────────

_TEMPLATES: list[tuple[str, dict]] = [
    (r"_get|request|query|api|twse|finmind|fetch",
     {"icon": "🌐", "definition": "向外部 API 發送查詢請求",
      "guide": "像外送員，帶著訂單去遠端服務取資料再帶回來"}),
    (r"safe|parse_int|parse_float|to_int|to_float|cast",
     {"icon": "🛡️", "definition": "安全轉換資料型別，避免程式崩潰",
      "guide": "像翻譯官，把可能有雜訊的字串穩穩轉成數字；遇到空值也不會出錯"}),
    (r"date|time|trading_date|recent|schedule|calendar",
     {"icon": "📅", "definition": "計算或取得特定日期",
      "guide": "像日曆助理，根據規則算出你需要的那天，例如跳過假日找最近交易日"}),
    (r"read|load|open",
     {"icon": "📥", "definition": "從外部來源讀取資料",
      "guide": "像圖書館員，把指定的書從書架搬到你桌上"}),
    (r"clean|filter|strip|trim",
     {"icon": "🧹", "definition": "清洗或過濾不需要的資料",
      "guide": "像洗菜，把爛葉子和泥土去掉，只留下乾淨能用的部分"}),
    (r"process|transform|convert|calc|compute|calculate",
     {"icon": "⚙️", "definition": "對資料進行加工或計算",
      "guide": "像工廠生產線，原料進去，加工後的成品出來"}),
    (r"save|write|export|store|dump|output",
     {"icon": "💾", "definition": "將結果儲存到檔案或資料庫",
      "guide": "像把作業存進資料夾，確保結果不會消失"}),
    (r"plot|draw|chart|visual|show|display|render",
     {"icon": "📊", "definition": "將資料轉成視覺化圖表",
      "guide": "像把枯燥的數字表格變成一眼就懂的折線圖或長條圖"}),
    (r"init|setup|config|prepare|__init__|build|create",
     {"icon": "🏗️", "definition": "初始化物件或設定環境",
      "guide": "像開店前準備：開燈、擺好桌椅、確認庫存，一切就緒才開始營業"}),
    (r"^main$|^run$|^start$|^execute$",
     {"icon": "🎬", "definition": "主程式入口，串連所有步驟",
      "guide": "像導演，決定各個演員（函數）依序上場的時機和順序"}),
    (r"test|assert|check|validate|verify|ensure",
     {"icon": "✅", "definition": "驗證資料或邏輯是否正確",
      "guide": "像品管員，在成品出廠前逐一檢查有沒有瑕疵"}),
    (r"send|post|notify|push|publish|emit",
     {"icon": "📮", "definition": "向外部發送資料或通知",
      "guide": "像寄信，把訊息傳給遠端對方，然後等待回應"}),
    (r"analyze|analyse|parse|extract|split|tokenize",
     {"icon": "🔬", "definition": "解析或拆解資料結構",
      "guide": "像把大報告拆成各章節，逐段仔細閱讀分析"}),
    (r"summary|stats|count|mean|avg|sum|aggregate|report",
     {"icon": "🔢", "definition": "計算統計摘要或彙整數據",
      "guide": "像期末成績單，把一學期分數濃縮成平均、最高、最低三個數字"}),
    (r"signal|judge|decision|detect|flag|alert|warn|generate_signal",
     {"icon": "🚨", "definition": "根據條件產生判斷訊號",
      "guide": "像警報系統，持續監測數值，一旦超標就亮紅燈警告"}),
    (r"auth|login|token|session|credential|permission",
     {"icon": "🔐", "definition": "處理身份驗證或權限確認",
      "guide": "像門衛核對通行證，確認你有資格才放行"}),
    (r"handle|catch|error|exception|retry|fallback|recover",
     {"icon": "🛡️", "definition": "處理例外狀況，防止程式崩潰",
      "guide": "像緊急出口，平時不用，但出意外時確保安全離開"}),
    (r"loop|iterate|batch|each|foreach|bulk",
     {"icon": "🔄", "definition": "對多筆資料依序重複處理",
      "guide": "像輸送帶，每件商品都跑過同樣流程，一個接一個處理完"}),
    (r"delete|remove|clear|reset|purge",
     {"icon": "🗑️", "definition": "刪除或清除不需要的資料",
      "guide": "像清垃圾桶，把過期無用的資料清掉，騰出空間"}),
    (r"search|find|lookup|scan|seek|locate",
     {"icon": "🔍", "definition": "在資料集中搜尋符合條件的項目",
      "guide": "像偵探辦案，在一堆線索中找出符合特徵的那一個"}),
    (r"log|print|debug|trace|verbose",
     {"icon": "📝", "definition": "輸出或記錄程式執行狀態",
      "guide": "像飛機黑盒子，把每個重要事件都記錄下來，出事時可查閱"}),
    (r"trend|direction|momentum",
     {"icon": "📈", "definition": "判斷數值的趨勢方向",
      "guide": "像看折線圖，判斷現在是往上升、往下跌、還是持平"}),
    (r"print_report|format|render_",
     {"icon": "🖨️", "definition": "格式化並輸出報告",
      "guide": "像印表機，把整理好的資料以整齊格式呈現給人看"}),
]

_DEFAULT: dict = {
    "icon":       "🔧",
    "definition": "執行特定的輔助任務",
    "guide":      "像一個專門工具，負責處理某件具體的事，讓其他函數可以直接呼叫使用",
}

_PARAM_MAP: dict = {
    "val": "要轉換的原始值",        "value": "輸入值",
    "default": "失敗時的預設值",     "data": "要處理的資料",
    "df": "DataFrame 資料表",        "stock_id": "股票代號（如 2330）",
    "code": "程式碼字串",             "path": "檔案路徑",
    "url": "網址",                    "key": "查詢鍵值",
    "name": "名稱",                   "id": "識別碼",
    "result": "結果資料",             "config": "設定參數",
    "days": "天數",                   "limit": "數量上限",
    "start": "起始位置或日期",        "end": "結束位置或日期",
    "dataset": "資料集名稱",          "params": "查詢參數字典",
    "endpoint": "API 端點路徑",       "days_back": "往前幾天",
    "s": "輸入字串",                  "n": "數字",
    "x": "X 軸資料",                  "y": "Y 軸資料",
    "msg": "訊息文字",                "text": "文字內容",
}

_RETURN_MAP: dict = {
    "int": "整數數值",           "float": "浮點數值",
    "str": "文字字串",           "bool": "True / False",
    "list": "資料列表",          "dict": "字典資料",
    "Dict": "字典資料",          "List[dict]": "多筆資料列表",
    "Optional[dict]": "字典或 None（可能查無資料）",
    "None": "無回傳值",          "": "視函數邏輯而定",
}


def _offline_template(func_info: dict) -> dict:
    name      = func_info.get("name", "").lower()
    docstring = (func_info.get("docstring") or "").strip()
    params    = func_info.get("params", [])
    body      = func_info.get("body", "")

    line_count = body.count("\n") + 1
    complexity = "simple" if line_count <= 10 else ("medium" if line_count <= 30 else "complex")

    matched = None
    for pattern, tmpl in _TEMPLATES:
        if re.search(pattern, name):
            matched = dict(tmpl)
            break
    if matched is None:
        matched = dict(_DEFAULT)

    if docstring:
        matched["definition"] = docstring.split("\n")[0].strip()[:60]

    visible = [p for p in params if p not in ("self", "cls")]
    matched["params_explain"] = [
        {"name": p, "explain": _PARAM_MAP.get(p.split(":")[0].strip(), "輸入參數")}
        for p in visible
    ]

    ret = func_info.get("return_annotation") or ""
    matched["return_explain"] = _RETURN_MAP.get(ret.strip(), f"回傳 {ret}" if ret else "視函數邏輯而定")
    matched["complexity"]     = complexity
    return matched


# ═══════════════════════════════════════════════════
#  第 3 輪新增：類別解釋 & Import 解釋
# ═══════════════════════════════════════════════════

from ai.prompts import CLASS_EXPLAIN_PROMPT, IMPORT_EXPLAIN_PROMPT, LINE_ANNOTATE_PROMPT


def generate_class_explanation(class_info: dict) -> dict:
    """
    產生類別解釋。
    優先查快取（以 class body 為 key），否則呼叫 AI 或離線模板。

    回傳：
    {
        "definition": str,
        "guide": str,
        "icon": str,
        "purpose": str,
        "source": str,  # "cache" | "claude" | "gemini" | "template"
    }
    """
    global _last_error

    cache = get_cache()
    body  = class_info.get("body", "")

    # 1. 查快取（快取 key 加前綴 CLASS: 避免與函數衝突）
    cache_key = "CLASS:" + body
    cached = cache.get(cache_key)
    if cached:
        result = dict(cached)
        result["source"] = "cache"
        return result

    # 2. 呼叫 AI API
    if _api_ready:
        try:
            prompt = CLASS_EXPLAIN_PROMPT.replace("{code_snippet}", body)
            if _current_provider == "claude":
                result = _call_claude_raw(prompt)
            else:
                result = _call_gemini_raw(prompt)

            result.setdefault("definition", f"{class_info.get('name', '?')} 類別")
            result.setdefault("guide", "像一個藍圖，定義了物件的屬性和行為")
            result.setdefault("icon", class_info.get("icon", "🏛️"))
            result.setdefault("purpose", "提供可重複使用的物件範本")

            cache.set(cache_key, class_info.get("name", "class"), result, api_model=_current_model)
            result["source"] = _current_provider
            return result

        except Exception as e:
            _last_error = f"{type(e).__name__}: {e}"

    # 3. 離線模板
    return _offline_class_template(class_info)


def generate_import_explanation(package_name: str) -> dict:
    """
    為未知套件呼叫 AI 解釋（線上模式），或回傳通用模板。

    回傳：
    {
        "description": str,
        "guide": str,
        "category": str,
        "icon": str,
        "source": str,
    }
    """
    global _last_error

    cache = get_cache()
    cache_key = "PKG:" + package_name

    cached = cache.get(cache_key)
    if cached:
        result = dict(cached)
        result["source"] = "cache"
        return result

    if _api_ready:
        try:
            prompt = IMPORT_EXPLAIN_PROMPT.replace("{package_name}", package_name)
            if _current_provider == "claude":
                result = _call_claude_raw(prompt)
            else:
                result = _call_gemini_raw(prompt)

            result.setdefault("description", f"{package_name} 套件")
            result.setdefault("guide", "提供特定功能的 Python 套件")
            result.setdefault("category", "第三方套件")
            result.setdefault("icon", "📦")

            cache.set(cache_key, package_name, result, api_model=_current_model)
            result["source"] = _current_provider
            return result

        except Exception as e:
            _last_error = f"{type(e).__name__}: {e}"

    return {
        "description": f"{package_name} 套件",
        "guide":       "這個套件提供特定的 Python 功能模組",
        "category":    "第三方套件",
        "icon":        "📦",
        "source":      "template",
    }


# ── 共用：不解析 JSON 的 raw API 呼叫 ─────────────────

def _call_claude_raw(prompt: str) -> dict:
    """呼叫 Claude API，追蹤 token，回傳解析後 dict。"""
    global _session_cost

    response = _claude_client.messages.create(
        model=_current_model,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    usage      = response.usage
    in_tok     = getattr(usage, "input_tokens",  0)
    out_tok    = getattr(usage, "output_tokens", 0)
    cost_table = COST_PER_1K.get(_current_model, {"input": 0, "output": 0})
    usd        = in_tok / 1000 * cost_table["input"] + out_tok / 1000 * cost_table["output"]

    _session_cost["input_tokens"]  += in_tok
    _session_cost["output_tokens"] += out_tok
    _session_cost["total_usd"]     += usd
    _session_cost["api_calls"]     += 1

    return _parse_ai_response(response.content[0].text.strip())


def _call_gemini_raw(prompt: str) -> dict:
    """呼叫 Gemini API，追蹤 token（估算），回傳解析後 dict。"""
    global _session_cost

    import google.generativeai as genai
    generation_config = genai.GenerationConfig(temperature=0.3, max_output_tokens=600)
    response = _gemini_model.generate_content(prompt, generation_config=generation_config)

    in_tok     = len(prompt) // 4
    out_tok    = len(response.text) // 4
    cost_table = COST_PER_1K.get(_current_model, {"input": 0, "output": 0})
    usd        = in_tok / 1000 * cost_table["input"] + out_tok / 1000 * cost_table["output"]

    _session_cost["input_tokens"]  += in_tok
    _session_cost["output_tokens"] += out_tok
    _session_cost["total_usd"]     += usd
    _session_cost["api_calls"]     += 1

    return _parse_ai_response(response.text.strip())


# ── 逐行中文注解 ──────────────────────────────────────

def generate_line_annotation(func_info: dict) -> str:
    """
    為函式逐行加上繁體中文注解。
    回傳帶注解的完整程式碼字串（可直接用 st.code() 顯示）。
    失敗時回傳原始程式碼（不崩潰）。
    """
    global _last_error

    cache  = get_cache()
    code   = func_info.get("body", "")
    cache_key = "ANNOTATE:" + code   # 與函式解釋用不同前綴

    # 1. 查快取
    cached = cache.get(cache_key)
    if cached:
        return cached.get("annotated_code", code)

    # 2. 呼叫 AI
    if _api_ready:
        try:
            prompt = LINE_ANNOTATE_PROMPT.replace("{code}", code)

            if _current_provider == "claude":
                response = _claude_client.messages.create(
                    model=_current_model,
                    max_tokens=1200,
                    messages=[{"role": "user", "content": prompt}],
                )
                annotated = response.content[0].text.strip()
                usage      = response.usage
                in_tok     = getattr(usage, "input_tokens",  0)
                out_tok    = getattr(usage, "output_tokens", 0)
                cost_table = COST_PER_1K.get(_current_model, {"input": 0, "output": 0})
                usd        = in_tok / 1000 * cost_table["input"] + out_tok / 1000 * cost_table["output"]
                _session_cost["input_tokens"]  += in_tok
                _session_cost["output_tokens"] += out_tok
                _session_cost["total_usd"]     += usd
                _session_cost["api_calls"]     += 1
            else:
                import google.generativeai as genai
                cfg  = genai.GenerationConfig(temperature=0.2, max_output_tokens=1200)
                resp = _gemini_model.generate_content(prompt, generation_config=cfg)
                annotated = resp.text.strip()
                in_tok     = len(prompt) // 4
                out_tok    = len(annotated) // 4
                cost_table = COST_PER_1K.get(_current_model, {"input": 0, "output": 0})
                usd        = in_tok / 1000 * cost_table["input"] + out_tok / 1000 * cost_table["output"]
                _session_cost["input_tokens"]  += in_tok
                _session_cost["output_tokens"] += out_tok
                _session_cost["total_usd"]     += usd
                _session_cost["api_calls"]     += 1

            # 存快取
            cache.set(cache_key, func_info.get("name", "?"),
                      {"annotated_code": annotated}, api_model=_current_model)
            return annotated

        except Exception as e:
            _last_error = str(e)

    # 3. Fallback：回傳原始程式碼
    return code


# ── 類別離線模板 ──────────────────────────────────────

_CLASS_TEMPLATES = [
    (r"processor|handler|manager|controller|service",
     {"icon": "⚙️", "definition": "負責協調和管理特定業務流程",
      "guide": "像一個部門主管，統籌旗下所有操作，確保流程順暢執行",
      "purpose": "封裝相關功能，提供統一的操作介面"}),
    (r"model|entity|schema|record|data",
     {"icon": "📋", "definition": "定義資料的結構與屬性",
      "guide": "像一份表單範本，規定每筆資料要填哪些欄位、什麼格式",
      "purpose": "標準化資料結構，讓資料傳遞更安全可靠"}),
    (r"parser|reader|loader|importer|extractor",
     {"icon": "🔬", "definition": "解析並提取特定格式的資料",
      "guide": "像翻譯官，把外部格式（XML、JSON、CSV）翻成 Python 能理解的物件",
      "purpose": "統一資料輸入流程，隱藏格式解析細節"}),
    (r"writer|exporter|formatter|serializer|renderer",
     {"icon": "💾", "definition": "將資料轉換並輸出成特定格式",
      "guide": "像出版社的排版師，把內容按照規定格式整理輸出",
      "purpose": "統一資料輸出流程，確保格式一致性"}),
    (r"client|connector|adapter|gateway|proxy",
     {"icon": "🌐", "definition": "負責與外部系統溝通的橋樑",
      "guide": "像大使館，代表你的程式與外部 API 或服務進行溝通",
      "purpose": "封裝外部依賴，讓換掉外部服務時不影響核心邏輯"}),
    (r"test|spec|case|scenario",
     {"icon": "🧪", "definition": "包含自動化測試用例的測試類別",
      "guide": "像品質檢驗員的工作手冊，列出所有要驗證的情境和預期結果",
      "purpose": "確保程式碼修改後不會破壞原有功能"}),
    (r"exception|error",
     {"icon": "⚡", "definition": "自訂的例外錯誤類型",
      "guide": "像程式的自訂警報，當特定錯誤發生時發出清楚識別的訊號",
      "purpose": "提供更精確的錯誤識別，讓例外處理更有針對性"}),
    (r"config|setting|option|preference",
     {"icon": "⚙️", "definition": "集中管理應用程式設定",
      "guide": "像遙控器的設定面板，把所有可調參數集中在一個地方管理",
      "purpose": "集中設定管理，避免魔術數字散落在程式各處"}),
    (r"view|page|screen|widget|component",
     {"icon": "🖼️", "definition": "負責使用者介面的呈現邏輯",
      "guide": "像網頁的版面設計師，決定資料要如何展示給使用者看",
      "purpose": "分離顯示邏輯與業務邏輯，讓 UI 更容易維護"}),
]

_CLASS_DEFAULT = {
    "icon":       "🏛️",
    "definition": "提供可重複使用的物件藍圖",
    "guide":      "像一個設計好的模具，可以批量製造相同結構的物件，每個物件都有自己的資料",
    "purpose":    "封裝相關屬性和方法，提高程式的可維護性",
}


def _offline_class_template(class_info: dict) -> dict:
    name      = class_info.get("name", "").lower()
    docstring = (class_info.get("docstring") or "").strip()

    matched = None
    for pattern, tmpl in _CLASS_TEMPLATES:
        if re.search(pattern, name):
            matched = dict(tmpl)
            break
    if matched is None:
        matched = dict(_CLASS_DEFAULT)

    # 有 docstring 則用第一行
    if docstring:
        matched["definition"] = docstring.split("\n")[0].strip()[:60]

    matched["source"] = "template"
    return matched
