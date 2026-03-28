"""
新手引導系統 — 第 4 輪完整實作

首次使用者引導流程，存在 session_state 中追蹤進度。

引導步驟：
  1. 歡迎畫面 — 說明工具功能
  2. 互動教學 — 自動載入範例碼，引導按下分析
  3. 解讀結果 — 說明各區塊含義
  4. 完成 — 顯示進階功能提示

使用方式：
    from ui.onboarding import render_onboarding, should_show_onboarding
    if should_show_onboarding():
        render_onboarding()
"""

import streamlit as st


# ── Session State 管理 ────────────────────────────────

def should_show_onboarding() -> bool:
    """判斷是否需要顯示新手引導。"""
    if "onboarding_dismissed" not in st.session_state:
        st.session_state["onboarding_dismissed"] = False
    if "onboarding_step" not in st.session_state:
        st.session_state["onboarding_step"] = 0
    return not st.session_state["onboarding_dismissed"]


def dismiss_onboarding():
    """關閉新手引導。"""
    st.session_state["onboarding_dismissed"] = True
    st.session_state["onboarding_step"] = 0


def next_step():
    """進入下一步。"""
    st.session_state["onboarding_step"] = st.session_state.get("onboarding_step", 0) + 1


def prev_step():
    """回到上一步。"""
    step = st.session_state.get("onboarding_step", 0)
    if step > 0:
        st.session_state["onboarding_step"] = step - 1


# ── 引導內容 ──────────────────────────────────────────

_STEPS = [
    {
        "title": "歡迎使用 AI Python Code Tutor！",
        "icon": "👋",
        "content": (
            "這個工具可以幫你<b>秒懂 Python 程式碼</b>。\n"
            "無論你是程式新手，還是想快速理解別人的程式碼，\n"
            "只需要三個步驟就能得到清楚的解說。"
        ),
        "tip": "支援函數、類別、套件解析，還有流程圖視覺化！",
    },
    {
        "title": "第一步：貼上程式碼",
        "icon": "📋",
        "content": (
            "在左側的<b>程式碼輸入框</b>中，貼上你想要理解的 Python 程式碼。\n"
            "或者點擊「📋 載入範例程式碼」按鈕，先用範例試試看！"
        ),
        "tip": "支援任何合法的 Python 程式碼，包含函數、類別、套件引用等。",
    },
    {
        "title": "第二步：按下分析",
        "icon": "🔍",
        "content": (
            "點擊 <b>🔍 開始分析</b> 按鈕，工具就會：\n"
            "① 解析所有函數和類別\n"
            "② 分析呼叫關係\n"
            "③ 產生易懂的解說和流程圖"
        ),
        "tip": "設定 API Key 可啟用 AI 智慧解釋，離線模式也能使用！",
    },
    {
        "title": "第三步：閱讀解說",
        "icon": "💡",
        "content": (
            "分析結果包含：\n"
            "🎯 <b>功能說明</b> — 一句話講清楚函數在做什麼\n"
            "💡 <b>新手導讀</b> — 用生活化比喻幫助理解\n"
            "📊 <b>流程圖</b> — 視覺化呈現函數之間的關係\n"
            "📦 <b>Import 百科</b> — 認識用到的套件"
        ),
        "tip": "點擊「📋 查看原始碼」可以展開每個函數的程式碼。",
    },
    {
        "title": "🎉 你已經準備好了！",
        "icon": "🚀",
        "content": (
            "進階功能提示：\n"
            "🔑 在左側欄設定 <b>API Key</b> 啟用 AI 智慧解釋\n"
            "📊 切換不同的<b>流程圖類型</b>查看函數關係\n"
            "🏛️ 支援<b>類別解析</b>，顯示繼承和方法階層\n"
            "⚡ <b>快取機制</b>自動節省 API 費用"
        ),
        "tip": "開始探索吧！有任何問題都歡迎嘗試不同的程式碼。",
    },
]

TOTAL_STEPS = len(_STEPS)


# ── 渲染引導 UI ──────────────────────────────────────

def render_onboarding():
    """渲染新手引導浮動對話框。"""
    step = st.session_state.get("onboarding_step", 0)
    if step >= TOTAL_STEPS:
        dismiss_onboarding()
        return

    info = _STEPS[step]

    # 使用 st.container 和 markdown 模擬浮動提示框
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #FFFBF0 0%, #F5F3FF 100%);
        border: 2px solid #D97706;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        position: relative;
        box-shadow: 0 4px 24px rgba(217, 119, 6, 0.12);
    ">
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        ">
            <div>
                <span style="font-size: 32px; margin-right: 8px;">{info['icon']}</span>
                <span style="
                    font-family: 'Noto Sans TC', sans-serif;
                    font-size: 18px;
                    font-weight: 700;
                    color: #1A1A1A;
                ">{info['title']}</span>
            </div>
            <div style="
                font-size: 12px;
                color: #9B9B9B;
                background: #F0EFEB;
                padding: 3px 10px;
                border-radius: 12px;
                font-weight: 600;
            ">{step + 1} / {TOTAL_STEPS}</div>
        </div>

        <div style="
            font-size: 14px;
            color: #374151;
            line-height: 1.8;
            margin-bottom: 14px;
            white-space: pre-line;
        ">{info['content']}</div>

        <div style="
            font-size: 12px;
            color: #059669;
            background: #F0FDF4;
            padding: 8px 12px;
            border-radius: 8px;
            margin-bottom: 16px;
        ">💡 {info['tip']}</div>
    </div>
    """, unsafe_allow_html=True)

    # 導航按鈕
    cols = st.columns([1, 1, 1, 1])

    with cols[0]:
        if step > 0:
            st.button("← 上一步", on_click=prev_step, key="onb_prev",
                       use_container_width=True, type="secondary")

    with cols[1]:
        if step < TOTAL_STEPS - 1:
            st.button("下一步 →", on_click=next_step, key="onb_next",
                       use_container_width=True, type="primary")
        else:
            st.button("🎉 開始使用！", on_click=dismiss_onboarding, key="onb_done",
                       use_container_width=True, type="primary")

    with cols[3]:
        st.button("跳過引導", on_click=dismiss_onboarding, key="onb_skip",
                   use_container_width=True, type="secondary")


# ── 進度指示器 ────────────────────────────────────────

def render_step_indicator(current: int, total: int):
    """渲染步驟進度圓點。"""
    dots = []
    for i in range(total):
        if i == current:
            dots.append(
                '<span style="width:10px;height:10px;border-radius:50%;'
                'background:#D97706;display:inline-block;margin:0 3px;"></span>'
            )
        elif i < current:
            dots.append(
                '<span style="width:10px;height:10px;border-radius:50%;'
                'background:#059669;display:inline-block;margin:0 3px;"></span>'
            )
        else:
            dots.append(
                '<span style="width:10px;height:10px;border-radius:50%;'
                'background:#E8E5E0;display:inline-block;margin:0 3px;"></span>'
            )
    st.markdown(
        f'<div style="text-align:center;margin:8px 0;">{"".join(dots)}</div>',
        unsafe_allow_html=True,
    )
