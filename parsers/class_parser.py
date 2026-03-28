"""
使用 ast 模組解析 Python 程式碼中的類別定義。
第 3 輪完整實作。

ClassInfo = {
    "name": str,
    "bases": List[str],
    "docstring": str | None,
    "methods": List[FunctionInfo],
    "class_variables": List[{"name": str, "value": str}],
    "decorators": List[str],
    "line_start": int,
    "line_end": int,
    "body": str,
    "is_dataclass": bool,
    "is_abstract": bool,
    "is_exception": bool,
    "icon": str,
}
"""
import ast
import textwrap

from parsers.function_parser import _extract_function


# ── 圖示判斷 ──────────────────────────────────────────
def _get_class_icon(decorators: list, bases: list, name: str) -> str:
    dec_lower  = " ".join(decorators).lower()
    base_lower = " ".join(bases).lower()
    name_lower = name.lower()
    if "dataclass" in dec_lower:
        return "📋"
    if "abc" in base_lower or "abstractbase" in base_lower:
        return "🧩"
    if (
        "exception" in base_lower or "error" in base_lower
        or name_lower.endswith("error") or name_lower.endswith("exception")
    ):
        return "⚡"
    return "🏛️"


# ── 主解析器 ──────────────────────────────────────────
def parse_classes(source_code: str) -> list:
    """
    解析原始碼中的頂層 class 定義。
    回傳 List[ClassInfo]，語法錯誤時回傳空列表。
    """
    if not source_code.strip():
        return []
    try:
        tree = ast.parse(source_code)
    except Exception:
        return []

    source_lines = source_code.splitlines(keepends=True)
    total_lines  = len(source_lines)
    classes = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(_extract_class(node, source_lines, total_lines))
    return classes


# ── 單一類別提取 ──────────────────────────────────────
def _extract_class(node, source_lines: list, total_lines: int) -> dict:
    """從 AST ClassDef 節點提取 ClassInfo dict。"""

    # 基類
    bases = []
    for b in node.bases:
        try:
            bases.append(ast.unparse(b))
        except Exception:
            bases.append("?")

    # 裝飾器
    decorators = []
    for d in node.decorator_list:
        try:
            decorators.append("@" + ast.unparse(d))
        except Exception:
            pass

    # Docstring
    docstring = ast.get_docstring(node)

    # 行號
    line_start = node.lineno
    line_end   = getattr(node, "end_lineno", total_lines)

    # 原始碼（含 decorator 行）
    deco_start = node.decorator_list[0].lineno if node.decorator_list else line_start
    raw_body   = "".join(source_lines[deco_start - 1 : line_end])
    body       = textwrap.dedent(raw_body).rstrip()

    # 方法（直接子節點的 FunctionDef）
    methods = []
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fi = _extract_function(item, source_lines, total_lines)
            fi["parent_class"] = node.name
            methods.append(fi)

    # 類別變數（直接子節點的 Assign / AnnAssign）
    class_variables = []
    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            try:
                ann = ast.unparse(item.annotation)
                val = ast.unparse(item.value) if item.value else None
            except Exception:
                ann, val = "?", None
            class_variables.append({
                "name":  item.target.id,
                "value": f": {ann}" + (f" = {val}" if val else ""),
            })
        elif isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    try:
                        val = ast.unparse(item.value)
                    except Exception:
                        val = "..."
                    class_variables.append({"name": target.id, "value": f"= {val}"})

    # 型別旗標
    is_dataclass = any("dataclass" in d.lower() for d in decorators)
    is_abstract  = any("abc" in b.lower() for b in bases)
    is_exception = (
        any("exception" in b.lower() or "error" in b.lower() for b in bases)
        or node.name.lower().endswith(("error", "exception"))
    )
    icon = _get_class_icon(decorators, bases, node.name)

    return {
        "name":            node.name,
        "bases":           bases,
        "docstring":       docstring,
        "methods":         methods,
        "class_variables": class_variables,
        "decorators":      decorators,
        "line_start":      line_start,
        "line_end":        line_end,
        "body":            body,
        "is_dataclass":    is_dataclass,
        "is_abstract":     is_abstract,
        "is_exception":    is_exception,
        "icon":            icon,
    }
