"""
Graphviz 呼叫圖產生器 — CC 顏色分級版

依 Cyclomatic Complexity 上色節點：
  CC ≤  5  → 淡綠  (簡單，新手可讀)
  CC 6-10  → 黃    (中等，需留意)
  CC > 10  → 紅粗框 (複雜，重點學習)
"""
import graphviz

from parsers.call_graph import calc_cyclomatic_complexity


def build_call_graph_dot(functions: list[dict], call_graph: dict) -> str:
    """
    functions:  parse_functions() 回傳的 list
    call_graph: build_call_graph() 回傳的 dict（含 "calls" key）
    回傳 Graphviz DOT 語法字串，可直接傳給 st.graphviz_chart()。
    """
    dot = graphviz.Digraph(comment="Call Graph")
    dot.attr(rankdir="LR", bgcolor="transparent")
    dot.attr("node", fontname="Arial", fontsize="12",
             style="filled", shape="box")

    standalone = [f for f in functions if not f.get("parent_class")]
    if not standalone:
        return ""

    for func in standalone:
        name = func["name"]
        cc   = calc_cyclomatic_complexity(func.get("body", ""))
        if cc <= 5:
            fill, pw, color = "#90EE90", "1",   "#2d6a2d"
        elif cc <= 10:
            fill, pw, color = "#FFD700", "1.5", "#7a6000"
        else:
            fill, pw, color = "#FF6B6B", "3",   "#7a0000"
        dot.node(
            name,
            label=f"{name}\\nCC={cc}",
            fillcolor=fill,
            penwidth=pw,
            color=color,
        )

    known = {f["name"] for f in standalone}
    for caller, info in call_graph.items():
        if caller not in known:
            continue
        for callee in info.get("calls", []):
            if callee in known:
                dot.edge(caller, callee)

    return dot.source


def get_highest_cc_index(functions: list[dict]) -> int:
    """回傳 CC 最高的獨立函數在列表中的索引（供 radio 預設選取）。"""
    standalone = [f for f in functions if not f.get("parent_class")]
    if not standalone:
        return 0
    ccs = [calc_cyclomatic_complexity(f.get("body", "")) for f in standalone]
    return ccs.index(max(ccs))
