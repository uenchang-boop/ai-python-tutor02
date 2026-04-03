"""
分析函數之間的呼叫關係。

使用 ast.Name 和 ast.Call 節點掃描每個函數的 body，
找出它呼叫了哪些其他函數、被哪些函數呼叫。

輸出格式：
{
    "func_a": {
        "calls":     ["func_b", "func_c"],  # func_a 呼叫了這些
        "called_by": ["main"],              # 被這些函數呼叫
    }
}
"""
import ast


# ── Cyclomatic Complexity 計算 ────────────────────────

AST_BRANCH_NODES = (
    ast.If, ast.For, ast.While, ast.ExceptHandler,
    ast.With, ast.Assert, ast.comprehension,
)


def calc_cyclomatic_complexity(func_body: str) -> int:
    """
    計算 Cyclomatic Complexity（近似值）。
    基礎分 1，每個分支節點 +1，and/or 各 +1。
    """
    try:
        tree = ast.parse(func_body)
    except SyntaxError:
        return 1
    score = 1
    for node in ast.walk(tree):
        if isinstance(node, AST_BRANCH_NODES):
            score += 1
        if isinstance(node, ast.BoolOp):          # and / or
            score += len(node.values) - 1
    return score


def build_call_graph(functions: list[dict]) -> dict[str, dict]:
    """
    輸入：parse_functions() 回傳的 functions 列表
    輸出：call_graph dict

    演算法：
    1. 建立所有已知函數名稱集合
    2. 對每個函數解析其 body，找出所有 ast.Call 節點
    3. 若被呼叫的名稱在已知集合內，視為內部呼叫
    4. 反向建立 called_by 關係
    """
    known: set[str] = {f["name"] for f in functions}

    # 以函數原始碼重新 parse（body 是已 dedent 的字串）
    graph: dict[str, dict] = {
        f["name"]: {"calls": [], "called_by": []}
        for f in functions
    }

    for func in functions:
        fname  = func["name"]
        body   = func["body"]
        called = _extract_calls(body, known, fname)
        graph[fname]["calls"] = sorted(called)

    # 建立反向 called_by
    for fname, info in graph.items():
        for callee in info["calls"]:
            if callee in graph:
                if fname not in graph[callee]["called_by"]:
                    graph[callee]["called_by"].append(fname)

    return graph


def _extract_calls(source: str, known: set[str], self_name: str) -> list[str]:
    """
    解析一個函數的原始碼，回傳它所呼叫的已知函數列表（排除自身）。
    """
    found: set[str] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    for node in ast.walk(tree):
        # 直接呼叫：func_name(...)
        if isinstance(node, ast.Call):
            callee = _get_call_name(node.func)
            if callee and callee in known and callee != self_name:
                found.add(callee)

    return sorted(found)


def _get_call_name(node: ast.expr) -> str | None:
    """
    從 Call.func 節點取得函數名稱字串。
    支援：
    - Name:      func_name
    - Attribute: obj.method  → 回傳 method 部分
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None
