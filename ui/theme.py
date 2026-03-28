"""
Claude 風格主題 — CSS 注入與配色常數。
"""

COLORS = {
    "bg_main":        "#FAF9F7",
    "bg_card":        "#FFFFFF",
    "bg_code":        "#F5F3EF",
    "bg_sidebar":     "#F0EFEB",
    "text_primary":   "#1A1A1A",
    "text_secondary": "#6B6B6B",
    "text_muted":     "#9B9B9B",
    "accent_primary": "#D97706",
    "accent_blue":    "#2563EB",
    "accent_green":   "#059669",
    "accent_purple":  "#7C3AED",
    "border_light":   "#E8E5E0",
    "border_focus":   "#D97706",
}

FONTS = {
    "heading": "'Noto Sans TC', 'SF Pro Display', sans-serif",
    "body":    "'Noto Sans TC', 'SF Pro Text', sans-serif",
    "code":    "'JetBrains Mono', 'Fira Code', 'Source Code Pro', monospace",
}


def inject_theme():
    """將 Claude 風格 CSS 注入 Streamlit 頁面。"""
    import streamlit as st

    st.markdown("""
    <style>
    /* ── Google Fonts ─────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    /* ── 全域背景 ─────────────────────────────────── */
    .stApp { background-color: #FAF9F7 !important; }
    .stApp > header { background: transparent !important; }

    /* ── 隱藏 Streamlit 預設元素 ─────────────────── */
    #MainMenu, footer, .stDeployButton { visibility: hidden; }

    /* ── 主內容區域 ───────────────────────────────── */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px !important;
    }

    /* ── 標題區 ───────────────────────────────────── */
    .tutor-header {
        font-family: 'Noto Sans TC', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: #1A1A1A;
        margin-bottom: 2px;
        letter-spacing: -0.3px;
    }
    .tutor-subtitle {
        font-size: 15px;
        color: #6B6B6B;
        margin-bottom: 0;
        font-weight: 400;
    }
    .tutor-version {
        font-size: 11px;
        color: #9B9B9B;
        background: #F0EFEB;
        padding: 2px 8px;
        border-radius: 10px;
        margin-left: 8px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── 函數卡片 ─────────────────────────────────── */
    .func-card {
        background: #FFFFFF;
        border: 1px solid #E8E5E0;
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 14px;
        transition: box-shadow 0.2s, border-color 0.2s;
    }
    .func-card:hover {
        box-shadow: 0 2px 14px rgba(0,0,0,0.07);
        border-color: #D5D2CC;
    }
    .func-card-async {
        border-left: 3px solid #2563EB;
    }

    /* ── 函數名稱 Badge ───────────────────────────── */
    .func-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #FEF3C7;
        color: #D97706;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 7px;
        margin-bottom: 12px;
    }
    .func-badge-async {
        background: #DBEAFE;
        color: #1D4ED8;
    }
    .func-badge-method {
        background: #EDE9FE;
        color: #6D28D9;
    }

    /* ── 參數列 ───────────────────────────────────── */
    .func-params {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #6B6B6B;
        background: #F5F3EF;
        padding: 5px 12px;
        border-radius: 6px;
        margin-bottom: 12px;
        display: inline-block;
    }
    .func-params .param-default {
        color: #059669;
    }

    /* ── 解釋區塊 ─────────────────────────────────── */
    .explain-block {
        background: #FFFBF0;
        border-left: 3px solid #D97706;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 8px 0;
        font-size: 14px;
        color: #1A1A1A;
        line-height: 1.6;
    }
    .guide-block {
        background: #F0FDF4;
        border-left-color: #059669;
        color: #064E3B;
    }
    .explain-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 4px;
        display: block;
    }
    .label-def  { color: #D97706; }
    .label-guide { color: #059669; }

    /* ── 回傳型別 ─────────────────────────────────── */
    .return-badge {
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;
        color: #7C3AED;
        background: #F5F3FF;
        padding: 2px 8px;
        border-radius: 4px;
    }

    /* ── 呼叫關係 ─────────────────────────────────── */
    .call-relation {
        font-size: 12px;
        color: #5B21B6;
        background: #F5F3FF;
        padding: 6px 12px;
        border-radius: 6px;
        margin-top: 10px;
        line-height: 1.8;
    }
    /* FINDING-001: 移除 called_by 的 inline style（# 字元被誤判為 Markdown heading） */
    .call-relation-calledby {
        font-size: 12px;
        color: #C2410C;
        background: #FFF7ED;
        padding: 6px 12px;
        border-radius: 6px;
        margin-top: 6px;
        line-height: 1.8;
    }
    .call-chip {
        display: inline-block;
        background: #EDE9FE;
        color: #6D28D9;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        padding: 1px 7px;
        border-radius: 4px;
        margin: 1px 3px;
    }
    /* FINDING-001b: 移除 return_explain 的 inline style，同理避免 # 誤判 */
    .return-explain {
        margin: 8px 0 0;
        font-size: 12px;
        color: #6B6B6B;
    }
    .return-explain-label {
        font-weight: 600;
    }

    /* ── 摘要標籤列 ───────────────────────────────── */
    .summary-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 18px;
        align-items: center;
    }
    .summary-tag {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        font-weight: 500;
        padding: 5px 12px;
        border-radius: 20px;
    }
    .tag-func   { background: #FEF3C7; color: #92400E; }
    .tag-import { background: #EDE9FE; color: #5B21B6; }
    .tag-lines  { background: #E0F2FE; color: #0C4A6E; }
    .tag-top    { background: #FCE7F3; color: #9D174D; }

    /* ── Import 標籤 ──────────────────────────────── */
    .import-section {
        margin-bottom: 18px;
    }
    .import-badge {
        display: inline-block;
        background: #F0EFEB;
        color: #374151;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        padding: 3px 9px;
        border-radius: 5px;
        margin: 2px 4px 2px 0;
        border: 1px solid #E8E5E0;
    }

    /* ── 頂層程式碼 ───────────────────────────────── */
    .toplevel-card {
        background: #FFFAF0;
        border: 1px solid #FDE68A;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 14px;
    }
    .toplevel-label {
        font-size: 12px;
        font-weight: 700;
        color: #D97706;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    /* ── 歡迎畫面 ─────────────────────────────────── */
    .welcome-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px 20px;
        text-align: center;
        color: #6B6B6B;
    }
    .welcome-emoji {
        font-size: 64px;
        margin-bottom: 16px;
    }
    .welcome-title {
        font-size: 22px;
        font-weight: 700;
        color: #1A1A1A;
        margin-bottom: 8px;
    }
    .welcome-desc {
        font-size: 15px;
        color: #6B6B6B;
        margin-bottom: 32px;
        max-width: 400px;
        line-height: 1.6;
    }
    .steps-row {
        display: flex;
        gap: 24px;
        justify-content: center;
        flex-wrap: wrap;
    }
    .step-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        width: 120px;
    }
    .step-num {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #FEF3C7;
        color: #D97706;
        font-weight: 700;
        font-size: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .step-text {
        font-size: 13px;
        color: #6B6B6B;
        text-align: center;
    }

    /* ── 按鈕 ─────────────────────────────────────── */
    .stButton > button {
        background: #D97706 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        font-size: 15px !important;
        font-family: 'Noto Sans TC', sans-serif !important;
        transition: background 0.2s !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: #B45309 !important;
    }
    .stButton > button:disabled {
        background: #D5D2CC !important;
        color: #9B9B9B !important;
        cursor: not-allowed !important;
    }

    /* ── 次要按鈕（載入範例）────────────────────────── */
    .stButton > button[kind="secondary"] {
        background: #F5F3EF !important;
        color: #1A1A1A !important;
        border: 1px solid #E8E5E0 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #ECEAE6 !important;
    }

    /* ── TextArea ─────────────────────────────────── */
    .stTextArea textarea {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
        border-radius: 10px !important;
        border-color: #E8E5E0 !important;
        background: #FFFFFF !important;
        color: #1A1A1A !important;
    }
    .stTextArea textarea:focus {
        border-color: #D97706 !important;
        box-shadow: 0 0 0 2px rgba(217,119,6,0.15) !important;
    }

    /* ── Expander ─────────────────────────────────── */
    .streamlit-expanderHeader {
        font-size: 13px !important;
        color: #6B6B6B !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ── 分隔線 ───────────────────────────────────── */
    hr { border-color: #E8E5E0 !important; margin: 20px 0 !important; }

    /* ── Caption ─────────────────────────────────── */
    .stCaption { color: #9B9B9B !important; font-size: 12px !important; }

    /* ── Quick Win 1: 行動版提示（≤768px 顯示）─────── */
    @media (max-width: 768px) {
        .mobile-hint {
            display: block !important;
            background: #FEF3C7;
            color: #92400E;
            font-size: 13px;
            padding: 10px 14px;
            border-radius: 8px;
            margin-top: 12px;
            text-align: center;
        }
    }

    /* ── Quick Win 3: st.subheader 樣式對齊設計系統 ── */
    [data-testid="stHeadingWithActionElements"] h2,
    .stSubheader h2 {
        font-family: 'Noto Sans TC', sans-serif !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #6B6B6B !important;
        letter-spacing: 0.4px !important;
        margin-bottom: 10px !important;
    }

    /* ── 類別卡片（Round 3）──────────────────────── */
    .class-card {
        background: #FDFCFF;
        border: 2px solid #7C3AED;
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 20px;
        position: relative;
    }
    .class-card:hover {
        box-shadow: 0 4px 20px rgba(124,58,237,0.12);
    }
    .class-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
    }
    .class-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #EDE9FE;
        color: #5B21B6;
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 8px;
    }
    .class-bases {
        font-size: 12px;
        color: #7C3AED;
        background: #F5F3FF;
        padding: 4px 10px;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        margin-left: 4px;
    }
    .class-docstring {
        font-size: 13px;
        color: #4B5563;
        background: #F5F3FF;
        border-left: 3px solid #7C3AED;
        border-radius: 0 8px 8px 0;
        padding: 8px 14px;
        margin: 8px 0 14px 0;
        line-height: 1.6;
    }
    .class-vars-section {
        margin-bottom: 12px;
    }
    .class-var-badge {
        display: inline-block;
        background: #F3F0FF;
        color: #6D28D9;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 4px;
        margin: 2px 3px 2px 0;
        border: 1px solid #DDD6FE;
    }
    .method-tree {
        margin-left: 16px;
        border-left: 2px solid #DDD6FE;
        padding-left: 16px;
    }
    .method-connector {
        font-size: 11px;
        color: #A78BFA;
        font-family: 'JetBrains Mono', monospace;
        margin: 6px 0 4px 0;
    }
    .class-type-tag {
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 10px;
        font-weight: 600;
    }
    .tag-dataclass  { background: #E0F2FE; color: #0369A1; }
    .tag-abstract   { background: #FEF9C3; color: #854D0E; }
    .tag-exception  { background: #FEE2E2; color: #991B1B; }

    /* ── Import 百科（Round 3）──────────────────── */
    .import-encyclopedia {
        margin-bottom: 24px;
    }
    .import-pkg-card {
        background: #FFFFFF;
        border: 1px solid #E8E5E0;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .import-pkg-icon {
        font-size: 24px;
        flex-shrink: 0;
        line-height: 1;
        margin-top: 2px;
    }
    .import-pkg-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 700;
        color: #374151;
        margin-bottom: 2px;
    }
    .import-pkg-desc {
        font-size: 13px;
        color: #1A1A1A;
        margin-bottom: 4px;
        line-height: 1.5;
    }
    .import-pkg-guide {
        font-size: 12px;
        color: #059669;
        line-height: 1.5;
    }
    .import-pkg-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 6px;
        flex-wrap: wrap;
    }
    .import-cat-badge {
        font-size: 11px;
        background: #F0EFEB;
        color: #6B6B6B;
        padding: 2px 8px;
        border-radius: 10px;
        font-weight: 500;
    }
    .import-stdlib-badge {
        font-size: 11px;
        background: #DCFCE7;
        color: #166534;
        padding: 2px 8px;
        border-radius: 10px;
        font-weight: 600;
    }
    .import-unknown-card {
        background: #FFFBF0;
        border: 1px dashed #FCD34D;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 13px;
        color: #92400E;
    }

    /* ── Mermaid 流程圖區（Round 4）──────────────── */
    .mermaid-section {
        margin-top: 24px;
    }
    .mermaid-container {
        background: #FDFCFF;
        border: 1px solid #E8E5E0;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 16px;
    }

    /* ── 新手引導（Round 4）──────────────────────── */
    .onboarding-overlay {
        position: relative;
        z-index: 100;
    }

    /* ── Radio 按鈕 (流程圖選擇器) ─────────────────── */
    [data-testid="stHorizontalBlock"] .stRadio > div {
        gap: 8px !important;
    }
    .stRadio > div > label {
        font-size: 13px !important;
        padding: 6px 14px !important;
        border-radius: 8px !important;
        border: 1px solid #E8E5E0 !important;
        background: #FFFFFF !important;
        transition: all 0.2s !important;
    }
    .stRadio > div > label:hover {
        border-color: #D97706 !important;
        background: #FFFBF0 !important;
    }
    .stRadio > div > label[data-checked="true"] {
        background: #FEF3C7 !important;
        border-color: #D97706 !important;
        color: #92400E !important;
        font-weight: 600 !important;
    }

    </style>
    """, unsafe_allow_html=True)
