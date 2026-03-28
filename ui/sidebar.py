"""
側邊欄設定介面 — 雙 API 模式
支援 Claude API / Gemini API / 離線模式切換
"""
import html as _html
import streamlit as st

from config import CLAUDE_MODELS, GEMINI_MODELS, DEFAULT_MODEL, APP_VERSION
from ai.explainer import init_ai, get_cache, is_api_ready, get_last_error


def render_sidebar() -> dict:
    """
    渲染側邊欄，回傳：
    { "api_key", "model", "provider", "mode" }
    """
    with st.sidebar:
        # ── 標題 ─────────────────────────────────────
        st.markdown("""
        <div style="padding:4px 0 16px;">
            <div style="font-size:18px;font-weight:700;color:#1A1A1A;">⚙️ 設定</div>
            <div style="font-size:12px;color:#9B9B9B;margin-top:2px;">AI Python Code Tutor</div>
        </div>
        """, unsafe_allow_html=True)

        # ── API 提供者選擇 ─────────────────────────────
        st.markdown(
            '<div style="font-size:13px;font-weight:600;color:#1A1A1A;margin-bottom:6px;">'
            '🔀 API 提供者</div>',
            unsafe_allow_html=True,
        )
        provider_options = ["🤖 Claude API", "✨ Gemini API", "⛔ 離線模式"]
        saved_provider   = st.session_state.get("provider_choice", "🤖 Claude API")
        try:
            prov_idx = provider_options.index(saved_provider)
        except ValueError:
            prov_idx = 0

        provider_choice = st.radio(
            label="provider_radio",
            options=provider_options,
            index=prov_idx,
            label_visibility="collapsed",
            horizontal=True,
        )
        st.session_state["provider_choice"] = provider_choice

        offline_mode = provider_choice.startswith("⛔")
        provider     = "gemini" if "Gemini" in provider_choice else "claude"

        st.markdown('<div style="margin-top:14px;"></div>', unsafe_allow_html=True)

        # ── API Key ───────────────────────────────────
        if not offline_mode:
            key_label = "Anthropic API Key" if provider == "claude" else "Google Gemini API Key"
            key_placeholder = "sk-ant-..." if provider == "claude" else "AIzaSy..."
            key_link  = ("https://console.anthropic.com/settings/keys"
                         if provider == "claude"
                         else "https://aistudio.google.com/app/apikey")
            key_link_text = "Anthropic Console" if provider == "claude" else "Google AI Studio"

            st.markdown(
                f'<div style="font-size:13px;font-weight:600;color:#1A1A1A;margin-bottom:6px;">'
                f'🔑 {key_label}</div>',
                unsafe_allow_html=True,
            )

            # 不同 provider 用不同 session key 儲存
            sess_key = f"api_key_{provider}"
            api_key  = st.text_input(
                label="api_key_input",
                type="password",
                placeholder=key_placeholder,
                value=st.session_state.get(sess_key, ""),
                label_visibility="collapsed",
            )
            if api_key != st.session_state.get(sess_key, ""):
                st.session_state[sess_key] = api_key

            st.markdown(
                f'<div style="font-size:11px;color:#9B9B9B;margin-top:4px;">'
                f'還沒有 Key？→ '
                f'<a href="{key_link}" target="_blank" '
                f'style="color:#2563EB;padding:6px 0;display:inline-block;">'
                f'{key_link_text}</a>'
                f' 取得</div>',
                unsafe_allow_html=True,
            )
        else:
            api_key = ""

        # ── 模型選擇 ───────────────────────────────────
        st.markdown('<div style="margin-top:14px;"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:13px;font-weight:600;color:#1A1A1A;margin-bottom:6px;">'
            '🧠 模型</div>',
            unsafe_allow_html=True,
        )

        if offline_mode:
            model_options = ["（離線，不使用 AI）"]
        elif provider == "claude":
            model_options = CLAUDE_MODELS
        else:
            model_options = GEMINI_MODELS

        saved_model = st.session_state.get(f"model_{provider}", model_options[0])
        try:
            model_idx = model_options.index(saved_model)
        except ValueError:
            model_idx = 0

        selected_model = st.selectbox(
            label="model_select",
            options=model_options,
            index=model_idx,
            label_visibility="collapsed",
        )
        st.session_state[f"model_{provider}"] = selected_model

        # ── 初始化 AI ──────────────────────────────────
        if offline_mode:
            st.info("📖 離線模式：使用內建關鍵字模板", icon=None)
            mode = "offline"
        elif api_key:
            success = init_ai(api_key, selected_model, provider)
            if success:
                icon = "🤖" if provider == "claude" else "✨"
                st.success(f"{icon} {provider.capitalize()} API 已連線", icon=None)
            else:
                err = get_last_error()
                st.error(f"❌ {err or 'API Key 有誤'}", icon=None)
            mode = provider
        else:
            # FINDING-003: st.warning() 黃色框視覺重量過重，改為小字 caption
            st.caption("💡 輸入 API Key 啟用 AI 解釋")
            mode = "offline"

        # API 呼叫錯誤提示
        last_err = get_last_error()
        if last_err and not offline_mode and api_key and is_api_ready():
            st.markdown(
                f'<div style="font-size:11px;color:#DC2626;background:#FEF2F2;'
                f'padding:8px 10px;border-radius:6px;margin-top:6px;word-break:break-all;">'
                f'⚠️ 最後錯誤：{_html.escape(last_err)}</div>',
                unsafe_allow_html=True,
            )

        # ── 快取統計 ───────────────────────────────────
        st.markdown("---")
        st.markdown(
            '<div style="font-size:13px;font-weight:600;color:#1A1A1A;margin-bottom:10px;">'
            '📊 快取統計</div>',
            unsafe_allow_html=True,
        )

        cache = get_cache()
        stats = cache.stats()
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("快取總數", stats["total_cached"])
        with col_b:
            hit_pct = int(stats["hit_rate"] * 100)
            st.metric("命中率", f"{hit_pct}%")

        if stats["hits"] + stats["misses"] > 0:
            st.markdown(
                f'<div style="font-size:11px;color:#6B6B6B;margin-top:4px;">'
                f'本次：命中 {stats["hits"]} 次 / 呼叫 {stats["misses"]} 次</div>',
                unsafe_allow_html=True,
            )

        if st.button("🗑️ 清除所有快取", use_container_width=True):
            count = cache.clear()
            st.success(f"已清除 {count} 筆快取")
            st.rerun()

        # ── 新手引導重設 ──────────────────────────────────
        if st.button("🎓 重新顯示新手引導", use_container_width=True):
            st.session_state["onboarding_dismissed"] = False
            st.session_state["onboarding_step"] = 0
            st.rerun()

        # ── 版本資訊 ───────────────────────────────────
        st.markdown("---")
        _ver = APP_VERSION.split("-")[0]   # "0.4.0-round4" → "0.4.0"
        st.markdown(
            f'<div style="font-size:11px;color:#9B9B9B;text-align:center;">'
            f'AI Python Code Tutor v{_ver}<br>'
            f'流程圖 · 類別解析 · Import 百科 · 新手引導</div>',
            unsafe_allow_html=True,
        )

    return {
        "api_key":  api_key,
        "model":    selected_model,
        "provider": provider,
        "mode":     mode,
    }
