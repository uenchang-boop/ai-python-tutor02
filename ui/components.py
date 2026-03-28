"""
可重複使用的 UI 元件模組 — 第 3 輪更新
新增：Class 解析卡片、Import 百科、版本號改從 config 讀取
"""
import html as _html
import streamlit as st

from config import APP_VERSION   # ← Bug 001 fix: 改從 config 讀版本號


# ── 標題 ─────────────────────────────────────────────
def render_header():
    # Bug 001 fix: 版本號改讀 config.APP_VERSION，不再硬編碼
    ver = APP_VERSION.split("-")[0]   # "0.3.0-round3" → "0.3.0"
    st.markdown(f"""
    <div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid #E8E5E0;">
        <div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;">
            <h1 class="tutor-header">🐍 AI Python Code Tutor</h1>
            <span class="tutor-version">v{ver}</span>
        </div>
        <p class="tutor-subtitle">貼上程式碼 → 秒懂每個函數在做什麼 &nbsp;·&nbsp; 由 AI 驅動服務</p>
    </div>
    """, unsafe_allow_html=True)


# ── 歡迎畫面 ──────────────────────────────────────────
def render_welcome():
    st.markdown("""
    <div class="welcome-wrap">
        <div class="welcome-emoji">🔍</div>
        <div class="welcome-title">準備好了嗎？</div>
        <div class="welcome-desc">
            把你的 Python 程式碼貼到左側，<br>
            我會幫你逐一解說每個函數在做什麼。
        </div>
        <div class="steps-row">
            <div class="step-item">
                <div class="step-num">1</div>
                <div class="step-text">📋 貼上<br>Python 程式碼</div>
            </div>
            <div class="step-item">
                <div class="step-num" style="color:#1A1A1A;background:#E0F2FE;">→</div>
                <div class="step-text" style="visibility:hidden;">x</div>
            </div>
            <div class="step-item">
                <div class="step-num">2</div>
                <div class="step-text">🔍 按下<br>開始分析</div>
            </div>
            <div class="step-item">
                <div class="step-num" style="color:#1A1A1A;background:#E0F2FE;">→</div>
                <div class="step-text" style="visibility:hidden;">x</div>
            </div>
            <div class="step-item">
                <div class="step-num">3</div>
                <div class="step-text">💡 閱讀<br>AI 解說</div>
            </div>
        </div>
        <div style="margin-top:28px;font-size:12px;color:#9B9B9B;line-height:1.7;">
            💡 在左側欄輸入 API Key 啟用 AI 智慧解釋<br>
            📊 分析結果含流程圖、類別繼承圖、執行順序圖<br>
            📖 無 Key 時自動使用離線關鍵字模板
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── 摘要標籤列 ────────────────────────────────────────
def render_summary_bar(result: dict):
    func_count   = len(result.get("functions", []))
    import_count = len(result.get("imports", []))
    toplevel     = result.get("top_level_code", [])

    tags = [f'<span class="summary-tag tag-func">🔧 {func_count} 個函數</span>']
    if import_count:
        tags.append(f'<span class="summary-tag tag-import">📦 {import_count} 個套件</span>')
    if toplevel:
        tags.append(f'<span class="summary-tag tag-top">📄 {len(toplevel)} 段頂層程式碼</span>')

    st.markdown(
        f'<div class="summary-bar">{"".join(tags)}</div>',
        unsafe_allow_html=True,
    )


# ── Import 標籤列 ─────────────────────────────────────
def render_import_tags(imports: list[str]):
    if not imports:
        return
    badges = []
    for imp in imports:
        parts = imp.replace("from ", "").replace("import ", "").strip().split()[0]
        safe  = _html.escape(parts)
        full  = _html.escape(imp)
        badges.append(f'<span class="import-badge" title="{full}">{safe}</span>')

    st.markdown(f"""
    <div class="import-section">
        <div style="font-size:12px;color:#9B9B9B;margin-bottom:6px;
                    font-weight:600;letter-spacing:0.5px;">📦 使用的套件</div>
        {"".join(badges)}
    </div>
    """, unsafe_allow_html=True)


# ── Source & Complexity Badges ────────────────────────
def _source_badge(source: str) -> str:
    MAP = {
        "cache":    '<span style="font-size:11px;background:#D1FAE5;color:#065F46;padding:2px 8px;border-radius:10px;font-weight:600;">⚡ 快取</span>',
        "gemini":   '<span style="font-size:11px;background:#DBEAFE;color:#1E40AF;padding:2px 8px;border-radius:10px;font-weight:600;">🤖 Gemini</span>',
        "template": '<span style="font-size:11px;background:#F0EFEB;color:#6B6B6B;padding:2px 8px;border-radius:10px;font-weight:600;">📖 離線</span>',
    }
    return MAP.get(source, "")


def _complexity_badge(complexity: str) -> str:
    MAP = {
        "simple":  '<span style="font-size:11px;background:#D1FAE5;color:#065F46;padding:2px 8px;border-radius:10px;">🟢 簡單</span>',
        "medium":  '<span style="font-size:11px;background:#FEF3C7;color:#92400E;padding:2px 8px;border-radius:10px;">🟡 中等</span>',
        "complex": '<span style="font-size:11px;background:#FEE2E2;color:#991B1B;padding:2px 8px;border-radius:10px;">🔴 複雜</span>',
    }
    return MAP.get(complexity, "")


# ── 函數卡片 ──────────────────────────────────────────
def render_function_card(func: dict, explanation: dict, relations: dict):
    name       = func["name"]
    params     = func.get("params", [])
    is_async   = func.get("is_async", False)
    parent     = func.get("parent_class")
    ret_ann    = func.get("return_annotation")
    body       = func.get("body", "")

    icon       = explanation.get("icon", "🔧")
    definition = _html.escape(explanation.get("definition", ""))
    guide      = _html.escape(explanation.get("guide", ""))
    source     = explanation.get("source", "template")
    complexity = explanation.get("complexity", "simple")
    params_xp  = explanation.get("params_explain", [])
    return_xp  = explanation.get("return_explain", "")

    badge_class = "func-badge"
    card_class  = "func-card"
    if is_async:
        badge_class += " func-badge-async"
        card_class  += " func-card-async"
    elif parent:
        badge_class += " func-badge-method"

    title_parts = []
    if parent:
        title_parts.append(
            f'<span style="color:#9B9B9B;font-size:11px;font-weight:400;">'
            f'{_html.escape(parent)}.</span>'
        )
    title_parts.append(f'<span>{_html.escape(name)}</span>')
    if is_async:
        title_parts.append(
            '<span style="font-size:10px;background:#BFDBFE;color:#1E40AF;'
            'padding:1px 6px;border-radius:4px;font-family:\'JetBrains Mono\',monospace;">async</span>'
        )
    badge_html = f'<span class="{badge_class}">{icon} {"".join(title_parts)}</span>'

    # ── ChatGPT 跳轉按鈕 ──────────────────────────────────────────────────────
    # 建立引導提示詞：含函數名稱 + 程式碼段落（最多 800 字元避免 URL 過長）
    _body_snippet = (body[:800] + "...") if len(body) > 800 else body
    _func_display = f"{parent}.{name}" if parent else name
    _chatgpt_prompt = (
        f"您是一位程式語言的老師，請解釋 {_func_display}() 函數，"
        f"及說明目前引用的段落，讓一位初學程式設計的人有所了解：\n\n"
        f"```python\n{_body_snippet}\n```"
    )
    import urllib.parse as _up
    _encoded_prompt = _up.quote(_chatgpt_prompt)
    _chatgpt_url    = f"https://chatgpt.com/?q={_encoded_prompt}"
    chatgpt_btn_html = (
        f'<a href="{_chatgpt_url}" target="_blank" rel="noopener noreferrer" '
        f'title="在 ChatGPT 詢問此函數的說明" '
        f'style="display:inline-flex;align-items:center;gap:4px;'
        f'padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;'
        f'background:linear-gradient(135deg,#10a37f,#1a7f64);color:#fff;'
        f'text-decoration:none;border:none;cursor:pointer;'
        f'box-shadow:0 1px 4px rgba(16,163,127,0.3);'
        f'transition:opacity 0.15s;">'
        f'<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">'
        f'<path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 '
        f'6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 '
        f'6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 '
        f'6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 '
        f'5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z"/>'
        f'</svg>'
        f'問 ChatGPT</a>'
    )
    # ─────────────────────────────────────────────────────────────────────────

    params_html = (
        f'<div class="func-params">({"  ,  ".join(_html.escape(p) for p in params)})</div>'
        if params else '<div class="func-params">()</div>'
    )

    ret_html = f'<span class="return-badge">→ {_html.escape(ret_ann)}</span>' if ret_ann else ""

    # 參數解釋表
    visible_params = [p for p in params_xp if p.get("name") != "self"]
    params_explain_html = ""
    if visible_params:
        rows = "".join(
            f'<tr>'
            f'<td style="font-family:\'JetBrains Mono\',monospace;font-size:12px;'
            f'color:#7C3AED;padding:3px 8px 3px 0;white-space:nowrap;">'
            f'{_html.escape(p.get("name",""))}</td>'
            f'<td style="font-size:12px;color:#1A1A1A;padding:3px 0;">'
            f'{_html.escape(p.get("explain",""))}</td>'
            f'</tr>'
            for p in visible_params
        )
        params_explain_html = (
            f'<div style="margin:8px 0 0;background:#F5F3EF;border-radius:8px;padding:10px 14px;">'
            f'<div style="font-size:11px;font-weight:700;color:#9B9B9B;'
            f'letter-spacing:0.8px;margin-bottom:6px;">📌 參數說明</div>'
            f'<table style="border-collapse:collapse;width:100%;">{rows}</table></div>'
        )

    # 回傳說明 — FINDING-001b: 改用 .return-explain 類別，移除含 # 的 inline style
    return_explain_html = ""
    if return_xp and return_xp.strip() not in ("", "無", "none", "None"):
        return_explain_html = (
            f'<div class="return-explain">'
            f'<span class="return-explain-label">↩ 回傳：</span>{_html.escape(return_xp)}'
            f'</div>'
        )

    # 呼叫關係 — FINDING-001: called_by 改用 .call-relation-calledby 類別，
    # 移除 style="background:#FFF7ED;color:#C2410C;" 中的 # 字元，
    # 避免被 Streamlit Markdown 解析器誤判為 heading。
    calls_html     = ""
    called_by_html = ""
    calls          = relations.get("calls", [])
    called_by      = relations.get("called_by", [])
    if calls:
        chips      = " ".join(f'<span class="call-chip">{_html.escape(c)}</span>' for c in calls)
        calls_html = f'<div class="call-relation">📤 呼叫了：{chips}</div>'
    if called_by:
        chips          = " ".join(f'<span class="call-chip">{_html.escape(c)}</span>' for c in called_by)
        called_by_html = f'<div class="call-relation-calledby">📥 被呼叫：{chips}</div>'

    src_badge  = _source_badge(source)
    comp_badge = _complexity_badge(complexity)

    # Bug 002 fix ─────────────────────────────────────────────────────────────
    # 原本用多行 f-string，當 params_explain_html / return_explain_html 為空串時
    # 會產生連續空行，導致 Streamlit 的 Markdown 解析器將後面的 <div> 當純文字輸出。
    # 改用列表組合，只加入非空的區塊，徹底避免空行問題。
    # ─────────────────────────────────────────────────────────────────────────
    header_row = (
        f'<div style="display:flex;justify-content:space-between;'
        f'align-items:flex-start;flex-wrap:wrap;gap:6px;margin-bottom:4px;">'
        f'<div>{badge_html}</div>'
        f'<div style="display:flex;gap:6px;align-items:center;">'
        f'{chatgpt_btn_html} {comp_badge} {src_badge} {ret_html}'
        f'</div>'
        f'</div>'
    )
    explain_def   = (
        f'<div class="explain-block">'
        f'<span class="explain-label label-def">🎯 功能說明</span>{definition}'
        f'</div>'
    )
    explain_guide = (
        f'<div class="explain-block guide-block">'
        f'<span class="explain-label label-guide">💡 新手導讀</span>{guide}'
        f'</div>'
    )
    # 只收集非空區塊，join 時不產生任何空行
    inner_blocks = [
        header_row,
        params_html,
        explain_def,
        explain_guide,
    ]
    for blk in (params_explain_html, return_explain_html, calls_html, called_by_html):
        if blk:
            inner_blocks.append(blk)

    card_html = f'<div class="{card_class}">{"".join(inner_blocks)}</div>'
    st.markdown(card_html, unsafe_allow_html=True)

    if body:
        with st.expander(f"📋 查看原始碼 — {name}()", expanded=False):
            st.code(body, language="python")


# ── 頂層程式碼 ────────────────────────────────────────
def render_top_level_code(top_level: list[dict]):
    if not top_level:
        return
    st.markdown("""
    <div style="margin-top:24px;">
        <div style="font-size:13px;font-weight:700;color:#D97706;
                    letter-spacing:0.5px;margin-bottom:10px;">📄 頂層程式碼</div>
    </div>
    """, unsafe_allow_html=True)
    for item in top_level:
        line = item.get("line", "?")
        code = item.get("code", "")
        with st.expander(f"第 {line} 行起的頂層程式碼", expanded=len(code) < 200):
            st.code(code, language="python")


# ── 側邊欄 stub（向後相容）────────────────────────────
def render_sidebar():
    from ui.sidebar import render_sidebar as _real
    return _real()


# ═══════════════════════════════════════════════════
#  第 3 輪新增：類別卡片 & Import 百科
# ═══════════════════════════════════════════════════

def render_class_card(
    class_info: dict,
    class_explanation: dict,
    method_explanations: dict,   # {method_name: explanation_dict}
    call_graph: dict,
):
    """
    渲染類別卡片（階層式：類別 header → 方法列表）。

    class_info:          ClassInfo dict
    class_explanation:   generate_class_explanation() 回傳
    method_explanations: {name: generate_explanation() 回傳}
    call_graph:          build_call_graph() 回傳
    """
    name       = class_info["name"]
    bases      = class_info.get("bases", [])
    docstring  = class_info.get("docstring") or ""
    methods    = class_info.get("methods", [])
    class_vars = class_info.get("class_variables", [])
    decorators = class_info.get("decorators", [])
    icon       = class_info.get("icon", "🏛️")
    body       = class_info.get("body", "")

    cex_def    = _html.escape(class_explanation.get("definition", ""))
    cex_guide  = _html.escape(class_explanation.get("guide", ""))
    cex_src    = class_explanation.get("source", "template")

    # 繼承標籤
    bases_html = ""
    if bases:
        bases_safe = ", ".join(_html.escape(b) for b in bases)
        bases_html = f'<span class="class-bases">繼承自：{bases_safe}</span>'

    # 型別旗標
    type_tags = ""
    if class_info.get("is_dataclass"):
        type_tags += '<span class="class-type-tag tag-dataclass">📋 dataclass</span> '
    if class_info.get("is_abstract"):
        type_tags += '<span class="class-type-tag tag-abstract">🧩 抽象類別</span> '
    if class_info.get("is_exception"):
        type_tags += '<span class="class-type-tag tag-exception">⚡ 例外類別</span> '

    # 裝飾器列表
    deco_html = ""
    if decorators:
        deco_safe  = "  ".join(_html.escape(d) for d in decorators)
        deco_html  = (
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
            f'color:#7C3AED;margin-bottom:4px;">{deco_safe}</div>'
        )

    # Docstring
    doc_html = ""
    if docstring:
        doc_first = docstring.split("\n")[0].strip()
        doc_html  = (
            f'<div class="class-docstring">💬 {_html.escape(doc_first)}</div>'
        )

    # 類別變數
    vars_html = ""
    if class_vars:
        var_badges = "".join(
            f'<span class="class-var-badge">'
            f'{_html.escape(v["name"])} '
            f'<span style="color:#A78BFA;">{_html.escape(v["value"][:30])}</span>'
            f'</span>'
            for v in class_vars[:8]
        )
        vars_html = (
            f'<div class="class-vars-section">'
            f'<div style="font-size:11px;font-weight:700;color:#A78BFA;'
            f'letter-spacing:0.8px;margin-bottom:6px;">📌 類別屬性</div>'
            f'{var_badges}'
            f'</div>'
        )

    # 解釋來源 badge
    src_badge = _source_badge(cex_src)

    header_html = f"""
    <div class="class-card">
        <div class="class-header">
            <div>
                {deco_html}
                <span class="class-badge">{icon} class {_html.escape(name)}</span>
                {bases_html}
            </div>
            <div style="display:flex;gap:6px;align-items:center;">{type_tags}{src_badge}</div>
        </div>
        {doc_html}
        <div class="explain-block" style="border-left-color:#7C3AED;background:#F5F3FF;">
            <span class="explain-label" style="color:#7C3AED;">🎯 類別說明</span>{cex_def}
        </div>
        <div class="explain-block guide-block">
            <span class="explain-label label-guide">💡 新手導讀</span>{cex_guide}
        </div>
        {vars_html}
    """

    st.markdown(header_html, unsafe_allow_html=True)

    # ── 方法列表（樹狀顯示）──────────────────────────
    if methods:
        method_count = len(methods)
        st.markdown(
            f'<div class="method-tree">'
            f'<div style="font-size:12px;font-weight:700;color:#7C3AED;'
            f'letter-spacing:0.5px;margin-bottom:12px;">'
            f'⚡ {method_count} 個方法</div>',
            unsafe_allow_html=True,
        )

        for i, method in enumerate(methods):
            is_last   = (i == method_count - 1)
            connector = "└──" if is_last else "├──"
            mname     = method["name"]
            mexpl     = method_explanations.get(mname, {})
            relations = call_graph.get(mname, {})
            micon     = mexpl.get("icon", "🔧")

            st.markdown(
                f'<div class="method-connector">{connector} {micon} '
                f'<span style="color:#6D28D9;font-family:\'JetBrains Mono\',monospace;">'
                f'{_html.escape(mname)}()</span></div>',
                unsafe_allow_html=True,
            )
            render_function_card(method, mexpl, relations)

        st.markdown("</div>", unsafe_allow_html=True)

    # 關閉 class-card div
    st.markdown("</div>", unsafe_allow_html=True)

    # 查看完整類別原始碼
    if body:
        with st.expander(f"📋 查看完整類別原始碼 — class {name}", expanded=False):
            st.code(body, language="python")


def render_import_encyclopedia(import_details: list, ai_explain_fn=None):
    """
    渲染 Import 百科區塊。

    import_details:  parse_imports_detail() 回傳的 List[ImportInfo]
    ai_explain_fn:   generate_import_explanation 函式（有 API Key 時傳入）
    """
    if not import_details:
        return

    st.markdown(
        '<div style="font-size:13px;font-weight:700;color:#6B6B6B;'
        'letter-spacing:0.5px;margin-bottom:12px;margin-top:8px;">'
        '📦 Import 百科</div>',
        unsafe_allow_html=True,
    )

    known    = [pkg for pkg in import_details if pkg.get("info")]
    unknown  = [pkg for pkg in import_details if not pkg.get("info")]

    # ── 已知套件：可展開的卡片 ─────────────────────────
    for pkg in known:
        info      = pkg["info"]
        pkg_name  = pkg["display_name"]
        icon      = info.get("icon", "📦")
        desc      = info.get("description", "")
        guide     = info.get("guide", "")
        category  = info.get("category", "")
        url       = info.get("url", "")
        is_stdlib = pkg.get("is_stdlib", False)

        stdlib_badge = (
            '<span class="import-stdlib-badge">✅ 標準函式庫</span>'
            if is_stdlib else ""
        )
        cat_badge = (
            f'<span class="import-cat-badge">{_html.escape(category)}</span>'
            if category else ""
        )
        url_link = (
            f'<a href="{_html.escape(url)}" target="_blank" '
            f'style="font-size:11px;color:#2563EB;text-decoration:none;">📖 官方文件</a>'
            if url else ""
        )

        with st.expander(f"{icon} {pkg_name}", expanded=False):
            st.markdown(
                f'<div class="import-pkg-card">'
                f'<div class="import-pkg-icon">{icon}</div>'
                f'<div style="flex:1;">'
                f'<div class="import-pkg-name">{_html.escape(pkg_name)}</div>'
                f'<div class="import-pkg-desc">{_html.escape(desc)}</div>'
                f'<div class="import-pkg-guide">{_html.escape(guide)}</div>'
                f'<div class="import-pkg-meta">'
                f'{stdlib_badge}{cat_badge}{url_link}'
                f'</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            # 顯示原始 import 語句
            st.code(pkg.get("raw", f"import {pkg_name}"), language="python")

    # ── 未知套件 ───────────────────────────────────────
    if unknown:
        st.markdown(
            '<div style="font-size:12px;font-weight:600;color:#D97706;'
            'margin-top:8px;margin-bottom:8px;">❓ 資料庫中未收錄的套件</div>',
            unsafe_allow_html=True,
        )
        for pkg in unknown:
            pkg_name = pkg["display_name"]

            # 如果有 AI API，嘗試線上解釋
            if ai_explain_fn:
                with st.expander(f"📦 {pkg_name}（AI 解釋中...）", expanded=False):
                    with st.spinner(f"🤖 正在詢問 AI 關於 {pkg_name}..."):
                        result = ai_explain_fn(pkg_name)
                    icon  = result.get("icon", "📦")
                    desc  = result.get("description", "")
                    guide = result.get("guide", "")
                    cat   = result.get("category", "")
                    src   = result.get("source", "template")
                    src_b = _source_badge(src)
                    st.markdown(
                        f'<div class="import-pkg-card">'
                        f'<div class="import-pkg-icon">{icon}</div>'
                        f'<div style="flex:1;">'
                        f'<div class="import-pkg-name">{_html.escape(pkg_name)}</div>'
                        f'<div class="import-pkg-desc">{_html.escape(desc)}</div>'
                        f'<div class="import-pkg-guide">{_html.escape(guide)}</div>'
                        f'<div class="import-pkg-meta">'
                        f'<span class="import-cat-badge">{_html.escape(cat)}</span>{src_b}'
                        f'</div>'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    st.code(pkg.get("raw", f"import {pkg_name}"), language="python")
            else:
                st.markdown(
                    f'<div class="import-unknown-card">'
                    f'📦 <code style="font-family:JetBrains Mono,monospace;">{_html.escape(pkg_name)}</code>'
                    f' &nbsp;—&nbsp; 資料庫未收錄。'
                    f'<span style="color:#9B9B9B;font-size:11px;">'
                    f' 輸入 API Key 啟用線上解釋</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
