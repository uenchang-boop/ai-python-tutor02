"""
圖示系統 — 第 4 輪完整實作

提供統一的 emoji 圖示對照，供 AI 離線模板、
Mermaid 流程圖節點、卡片標題等共用。

使用方式：
    from ui.icons import get_func_icon, get_class_icon
    icon = get_func_icon("load_data")   # → "📥"
    icon = get_class_icon("DataProcessor", decorators=[], bases=[])  # → "🏛️"
"""

import re

# ── 函數圖示對照表 ────────────────────────────────────
_FUNC_ICONS: list[tuple[str, str]] = [
    (r"read|load|fetch|get|open",                       "📥"),
    (r"clean|filter|remove|drop|strip",                 "🧹"),
    (r"process|transform|convert|calc|compute",         "⚙️"),
    (r"save|write|export|store|dump",                   "💾"),
    (r"plot|draw|chart|visual|show|display|render",     "📊"),
    (r"init|setup|config|prepare|__init__|build|create","🏗️"),
    (r"^main$|^run$|^start$|^execute$|^app$",           "🎬"),
    (r"test|assert|check|validate|verify",              "✅"),
    (r"send|post|request|api|call|notify",              "📮"),
    (r"parse|extract|split|tokenize|analyze",           "🔬"),
    (r"loop|iterate|batch|each|foreach",                "🔄"),
    (r"handle|catch|error|exception|retry",             "🛡️"),
    (r"auth|login|token|session|credential",            "🔐"),
    (r"log|print|debug|trace|verbose",                  "📝"),
    (r"search|find|lookup|scan|seek|locate",            "🔍"),
    (r"delete|clear|reset|purge",                       "🗑️"),
    (r"summary|stats|count|mean|avg|aggregate|report",  "🔢"),
    (r"date|time|schedule|calendar",                    "📅"),
    (r"signal|detect|flag|alert|warn",                  "🚨"),
    (r"trend|direction|momentum",                       "📈"),
    (r"format|render_|print_report",                    "🖨️"),
]

_FUNC_DEFAULT_ICON = "🔧"


def get_func_icon(func_name: str) -> str:
    """根據函數名稱回傳對應 emoji 圖示。"""
    name_lower = func_name.lower()
    for pattern, icon in _FUNC_ICONS:
        if re.search(pattern, name_lower):
            return icon
    return _FUNC_DEFAULT_ICON


# ── 類別圖示對照表 ────────────────────────────────────
def get_class_icon(
    class_name: str,
    decorators: list[str] | None = None,
    bases: list[str] | None = None,
) -> str:
    """
    根據類別資訊回傳對應 emoji：
      📋  dataclass
      🧩  抽象類別 (ABC)
      ⚡  例外類別 (Exception / Error)
      🏛️  一般類別
    """
    decs  = " ".join(decorators or []).lower()
    bases_ = " ".join(bases or []).lower()
    name  = class_name.lower()

    if "dataclass" in decs:
        return "📋"
    if "abc" in bases_ or "abstractbase" in bases_:
        return "🧩"
    if (
        "exception" in bases_ or "error" in bases_
        or name.endswith("error") or name.endswith("exception")
    ):
        return "⚡"
    return "🏛️"
