"""
Mermaid.js 流程圖產生器 — 第 4 輪完整實作

三種圖表類型：
  1. 函數呼叫流程圖（call graph）       — graph TD
  2. 類別繼承圖（class hierarchy）       — classDiagram
  3. 執行順序圖（sequence diagram）      — sequenceDiagram

Streamlit 整合方式：
  使用 st.components.v1.html() 嵌入 mermaid CDN 渲染。
"""

import html as _html
import re

from ui.icons import get_func_icon, get_class_icon


def _safe_id(name: str) -> str:
    """將函數/類別名稱轉成 Mermaid 合法 ID（只保留英數底線）。"""
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)


def _safe_label(name: str) -> str:
    """為 Mermaid label 做跳脫。"""
    return name.replace('"', "'")


# ═══════════════════════════════════════════════════
#  1. 函數呼叫流程圖
# ═══════════════════════════════════════════════════

def generate_call_graph(functions: list[dict], call_graph: dict) -> str:
    """
    產生函數呼叫流程圖的 Mermaid 語法。

    functions:  parse_functions() 回傳的 functions list
    call_graph: build_call_graph() 回傳的 dict
    """
    if not functions or not call_graph:
        return ""

    lines = ["graph TD"]

    # 節點定義（帶 icon）
    defined = set()
    for func in functions:
        name = func["name"]
        if func.get("parent_class"):
            continue  # 只處理獨立函數
        sid  = _safe_id(name)
        icon = get_func_icon(name)
        lines.append(f'    {sid}["{icon} {_safe_label(name)}"]')
        defined.add(name)

    # 邊（呼叫關係）
    for caller, info in call_graph.items():
        if caller not in defined:
            continue
        for callee in info.get("calls", []):
            if callee in defined:
                lines.append(f"    {_safe_id(caller)} --> {_safe_id(callee)}")

    # 上色
    for func in functions:
        if func.get("parent_class"):
            continue
        name = func["name"]
        name_lower = name.lower()
        sid = _safe_id(name)
        if name_lower in ("main", "run", "start", "execute", "app"):
            lines.append(f"    style {sid} fill:#FEF3C7,stroke:#D97706,stroke-width:2px")
        elif re.search(r"read|load|fetch|get|open", name_lower):
            lines.append(f"    style {sid} fill:#DBEAFE,stroke:#2563EB")
        elif re.search(r"save|write|export|store", name_lower):
            lines.append(f"    style {sid} fill:#D1FAE5,stroke:#059669")
        elif re.search(r"plot|draw|chart|visual", name_lower):
            lines.append(f"    style {sid} fill:#EDE9FE,stroke:#7C3AED")

    if len(lines) <= 1:
        return ""
    return "\n".join(lines)


# ═══════════════════════════════════════════════════
#  2. 類別繼承圖
# ═══════════════════════════════════════════════════

def generate_class_diagram(classes: list[dict]) -> str:
    """產生類別繼承圖的 Mermaid classDiagram 語法。"""
    if not classes:
        return ""

    lines = ["classDiagram"]

    for cls in classes:
        name    = _safe_id(cls["name"])
        methods = cls.get("methods", [])
        cvars   = cls.get("class_variables", [])

        # 繼承關係
        for base in cls.get("bases", []):
            base_id = _safe_id(base)
            lines.append(f"    {base_id} <|-- {name}")

        # 類別屬性
        for v in cvars:
            vname = _safe_label(v["name"])
            lines.append(f"    {name} : {vname}")

        # 方法
        for m in methods:
            mname = m["name"]
            vis = "-" if mname.startswith("_") and not mname.startswith("__") else "+"
            if mname.startswith("__") and mname.endswith("__"):
                vis = "+"
            params_short = ", ".join(
                p.split(":")[0].strip() for p in m.get("params", []) if p != "self"
            )
            lines.append(f"    {name} : {vis}{mname}({params_short})")

    if len(lines) <= 1:
        return ""
    return "\n".join(lines)


# ═══════════════════════════════════════════════════
#  3. 執行順序圖
# ═══════════════════════════════════════════════════

def generate_sequence_diagram(functions: list[dict], call_graph: dict) -> str:
    """
    產生執行順序圖的 Mermaid sequenceDiagram 語法。
    以 main/run/start 為起點，依序展開呼叫鏈。
    """
    if not functions or not call_graph:
        return ""

    standalone = [f for f in functions if not f.get("parent_class")]
    if not standalone:
        return ""

    func_names = {f["name"] for f in standalone}
    entry_points = []
    for f in standalone:
        name = f["name"]
        if name.lower() in ("main", "run", "start", "execute", "app"):
            entry_points.append(name)

    if not entry_points:
        for name in func_names:
            info = call_graph.get(name, {})
            if not info.get("called_by"):
                entry_points.append(name)

    if not entry_points:
        entry_points = [standalone[0]["name"]]

    lines = ["sequenceDiagram"]

    added_participants = []
    added = set()
    visited_edges = set()

    def _ensure_participant(name):
        if name not in added:
            icon = get_func_icon(name)
            added_participants.append(
                f"    participant {_safe_id(name)} as {icon} {_safe_label(name)}"
            )
            added.add(name)

    for entry in entry_points:
        _ensure_participant(entry)

    interactions = []

    def _expand(caller: str, depth: int = 0):
        if depth > 6:
            return
        info = call_graph.get(caller, {})
        for callee in info.get("calls", []):
            if callee not in func_names:
                continue
            edge = (caller, callee)
            if edge in visited_edges:
                continue
            visited_edges.add(edge)
            _ensure_participant(callee)
            interactions.append(f"    {_safe_id(caller)}->>+{_safe_id(callee)}: 呼叫")
            interactions.append(f"    {_safe_id(callee)}-->>-{_safe_id(caller)}: 回傳")
            _expand(callee, depth + 1)

    for entry in entry_points:
        _expand(entry)

    if not interactions:
        return ""

    return "\n".join(lines + added_participants + interactions)


# ═══════════════════════════════════════════════════
#  渲染工具
# ═══════════════════════════════════════════════════

def render_mermaid_html(mermaid_code: str, height: int = 420) -> str:
    """
    產生嵌入式 HTML，使用 mermaid CDN 渲染圖表。
    回傳可直接用 st.components.v1.html() 顯示的 HTML 字串。
    """
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 16px;
            background: #FDFCFF;
            display: flex;
            justify-content: center;
            overflow: auto;
            font-family: 'Noto Sans TC', sans-serif;
        }}
        .mermaid {{
            max-width: 100%;
        }}
        .mermaid .nodeLabel {{
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="mermaid">
{mermaid_code}
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'base',
            themeVariables: {{
                primaryColor: '#FEF3C7',
                primaryBorderColor: '#D97706',
                primaryTextColor: '#1A1A1A',
                secondaryColor: '#EDE9FE',
                lineColor: '#9B9B9B',
                fontFamily: '"Noto Sans TC", "JetBrains Mono", sans-serif',
                fontSize: '13px',
            }},
            flowchart: {{
                curve: 'basis',
                padding: 20,
            }},
            sequence: {{
                actorMargin: 40,
                messageFontSize: 12,
            }},
        }});
    </script>
</body>
</html>"""
