CUSTOM_CSS = """
    <style>
    .stApp { background-color: #0b1220; }
    .block-container { padding-top: 1.4rem; max-width: 1340px; }

    .hero {
        background-color: #1a2236;
        border: 1px solid #2a334d;
        border-radius: 18px;
        padding: 1.7rem 1.9rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }
    .hero h1 { color: #f1f5f9; margin-bottom: 0.6rem; }
    .hero p { color: #cbd5e1; line-height: 1.65; font-size: 1.02rem; margin: 0; }

    div[data-testid="stExpander"] {
        background-color: #1a2236;
        border: 1px solid #2a334d;
        border-radius: 14px;
    }
    div[data-testid="stExpander"] p,
    div[data-testid="stExpander"] li { color: #cbd5e1; }

    .small-note { font-size: 0.92rem; color: #8b9bb4; }

    div[data-testid="stMetric"] { background: transparent; border: none; padding: 0; }
    div[data-testid="stMetric"] label { color: #8b9bb4 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #f1f5f9 !important; }

    [data-testid="stSidebar"] { background-color: #161e30; }
    [data-testid="stSidebar"] * { color: #cbd5e1 !important; }

    .stButton button {
        background-color: #3b82f6; color: white;
        border: none; border-radius: 10px;
    }

    div[data-testid="stTabs"] button {
        color: #cbd5e1; background-color: transparent; border: none;
        font-size: 1.05rem; font-weight: 500;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 2px solid #3b82f6; color: #f1f5f9;
    }

    code {
        background-color: #2a334d; padding: 2px 6px;
        border-radius: 6px; color: #fbbf24;
    }
    a { color: #60a5fa; }

    h1, h2, h3, h4 { color: #f1f5f9; }

    /* блок-формулы: подсветка, чтобы выделялись в длинных текстах */
    .katex-display {
        margin: 1.2rem 0 !important;
        padding: 0.9rem 1rem;
        background-color: rgba(59,130,246,0.07);
        border-left: 3px solid #3b82f6;
        border-radius: 6px;
        overflow-x: auto;
    }
    .katex { color: #f1f5f9 !important; font-size: 1.08em; }

    /* инфо/успех/ворнинг блоки темнее */
    div[data-testid="stAlert"] {
        background-color: #1a2236 !important;
        border: 1px solid #2a334d;
        border-radius: 12px;
    }
    div[data-testid="stAlert"] * { color: #cbd5e1 !important; }
    </style>
    """
