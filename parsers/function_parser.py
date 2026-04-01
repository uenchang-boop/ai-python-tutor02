"""
使用 ast 模組解析 Python 程式碼中的函數定義。

輸入：Python 原始碼字串
輸出：dict  {
    "functions":       List[FunctionInfo],
    "top_level_code":  List[{"code": str, "line": int}],
    "imports":         List[str],
    "errors":          List[str],
}

FunctionInfo = {
    "name":              str,
    "params":            List[str],
    "defaults":          List[str],
    "decorators":        List[str],
    "docstring":         str | None,
    "body":              str,           # 含 def 行的原始碼
    "line_start":        int,
    "line_end":          int,
    "return_annotation": str | None,
    "is_async":          bool,
    "parent_class":      str | None,    # 第 3 輪實作
}
"""
import ast
import textwrap
from typing import Any


# ── 輔助：取得 annotation 字串 ──────────────────────────
def _annotation_str(node: ast.expr | None) -> str | None:
    if node is None:
        return None
    return ast.unparse(node)


# ── 輔助：從原始碼切出指定行範圍 ────────────────────────
def _extract_lines(source_lines: list[str], start: int, end: int) -> str:
    """start / end 為 1-based 行號（含頭含尾）"""
    return "".join(source_lines[start - 1 : end])


# ── 輔助：取得函數最後一行 ──────────────────────────────
def _func_end_line(node: ast.FunctionDef | ast.AsyncFunctionDef,
                   total_lines: int) -> int:
    """
    ast.FunctionDef 本身有 end_lineno（Python 3.8+），直接使用。
    """
    return getattr(node, "end_lineno", total_lines)


# ── 輔助：移除包含錯誤行的頂層區塊 ────────────────────────
def _remove_bad_block(source_code: str, error_line: int) -> str:
    """
    移除包含 error_line 的頂層區塊（def / class / 其他 indent=0 的段落）。
    回傳去掉該區塊後的程式碼字串。
    """
    lines = source_code.splitlines()
    n = len(lines)
    if n == 0:
        return ""

    err_idx = min(error_line - 1, n - 1)  # 0-based

    # 向前找到含錯誤行的頂層起始行（indent == 0 的非空行）
    start = 0
    for i in range(err_idx, -1, -1):
        stripped = lines[i].lstrip()
        if stripped and len(lines[i]) - len(stripped) == 0:
            start = i
            break

    # 向後找到下一個頂層起始行（即本區塊的結束位置）
    end = n  # exclusive
    for i in range(start + 1, n):
        stripped = lines[i].lstrip()
        if stripped and len(lines[i]) - len(stripped) == 0:
            end = i
            break

    return "\n".join(lines[:start] + lines[end:])


# ── 主解析器 ────────────────────────────────────────────
def parse_functions(source_code: str) -> dict:
    """
    解析原始碼，回傳結構化結果。
    有語法錯誤時自動跳過壞區塊，繼續解析其餘有效部分。
    """
    result: dict[str, Any] = {
        "functions":      [],
        "top_level_code": [],
        "imports":        [],
        "errors":         [],
        "clean_code":     source_code,   # 去除語法錯誤區塊後的程式碼
    }

    if not source_code.strip():
        return result

    # 1. 嘗試解析（最多容忍 10 個壞區塊）
    working = source_code
    for _ in range(10):
        try:
            ast.parse(working)
            result["clean_code"] = working
            break                          # 解析成功
        except SyntaxError as e:
            result["errors"].append(f"第 {e.lineno} 行有語法錯誤：{e.msg}")
            cleaned = _remove_bad_block(working, e.lineno)
            if cleaned == working or not cleaned.strip():
                result["clean_code"] = ""
                return result              # 無法繼續，放棄
            working = cleaned
        except Exception as e:
            result["errors"].append(f"解析失敗：{e}")
            return result
    else:
        return result                      # 超過重試上限

    # 2. 用清理後的程式碼正式解析
    try:
        tree = ast.parse(working)
    except Exception as e:
        result["errors"].append(f"解析失敗：{e}")
        return result

    source_lines = source_code.splitlines(keepends=True)
    total_lines  = len(source_lines)

    # 2. 收集所有頂層節點類型（用來偵測「頂層程式碼」）
    TOP_IGNORE = (
        ast.FunctionDef, ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.Import, ast.ImportFrom,
        ast.Expr,       # 含 module docstring；後面單獨判斷
    )

    # 3. 走訪頂層節點
    for node in ast.iter_child_nodes(tree):

        # ── Import ──
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            result["imports"].append(ast.unparse(node))

        # ── 頂層函數 ──
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["functions"].append(_extract_function(node, source_lines, total_lines))

        # ── 頂層 Class 方法（第 3 輪完整實作，這裡先收集 class body 內函數） ──
        elif isinstance(node, ast.ClassDef):
            for item in ast.walk(node):
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    fi = _extract_function(item, source_lines, total_lines)
                    fi["parent_class"] = node.name
                    result["functions"].append(fi)

        # ── 頂層非函數/匯入的可執行程式碼 ──
        else:
            # 排除純 docstring（module-level Expr(Constant)）
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue
            if hasattr(node, "lineno"):
                end = getattr(node, "end_lineno", node.lineno)
                code_snippet = _extract_lines(source_lines, node.lineno, end).strip()
                if code_snippet:
                    result["top_level_code"].append({
                        "code": code_snippet,
                        "line": node.lineno,
                    })

    return result


def _extract_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    source_lines: list[str],
    total_lines: int,
) -> dict:
    """從 AST 節點提取 FunctionInfo dict"""

    # 參數
    args = node.args
    params: list[str] = []
    defaults_map: dict[str, str] = {}

    # positional + keyword-only
    all_args = args.posonlyargs + args.args + args.kwonlyargs
    # 預設值對齊（從右側對齊）
    pos_defaults = args.defaults
    kw_defaults  = [d for d in args.kw_defaults if d is not None]

    for arg in all_args:
        params.append(
            arg.arg + (f": {_annotation_str(arg.annotation)}" if arg.annotation else "")
        )
    if args.vararg:
        params.append(f"*{args.vararg.arg}")
    if args.kwarg:
        params.append(f"**{args.kwarg.arg}")

    # 預設值（簡化：只取 positional 的預設值）
    defaults_raw: list[str] = []
    offset = len(args.args) - len(pos_defaults)
    for i, d in enumerate(pos_defaults):
        if offset + i < len(args.args):
            param_name = args.args[offset + i].arg
            defaults_raw.append(f"{param_name}={ast.unparse(d)}")

    # 裝飾器
    decorators: list[str] = [
        "@" + ast.unparse(d) for d in node.decorator_list
    ]

    # Docstring
    docstring: str | None = ast.get_docstring(node)

    # 行號
    line_start = node.lineno
    line_end   = _func_end_line(node, total_lines)

    # 原始碼（含 decorator 行）
    deco_start = node.decorator_list[0].lineno if node.decorator_list else line_start
    body_code  = _extract_lines(source_lines, deco_start, line_end)
    # dedent 確保不多餘縮排
    body_code  = textwrap.dedent(body_code).rstrip()

    return {
        "name":              node.name,
        "params":            params,
        "defaults":          defaults_raw,
        "decorators":        decorators,
        "docstring":         docstring,
        "body":              body_code,
        "line_start":        line_start,
        "line_end":          line_end,
        "return_annotation": _annotation_str(node.returns),
        "is_async":          isinstance(node, ast.AsyncFunctionDef),
        "parent_class":      None,   # 由 parse_functions 填入
    }
