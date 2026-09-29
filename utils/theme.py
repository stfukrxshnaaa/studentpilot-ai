"""
Theme and custom styling manager for StudyPilot AI.
Provides clean modern CSS for Dark and Light modes, responsive cards, badge pills, and glassmorphism.
"""

def get_custom_css(theme_mode: str = "dark") -> str:
    """Returns custom CSS styles optimized for StudyPilot AI."""
    is_dark = (theme_mode.lower() == "dark")
    
    bg_primary = "#0f172a" if is_dark else "#f8fafc"
    bg_card = "#1e293b" if is_dark else "#ffffff"
    bg_card_hover = "#24344d" if is_dark else "#f1f5f9"
    border_color = "#334155" if is_dark else "#e2e8f0"
    text_primary = "#f8fafc" if is_dark else "#0f172a"
    text_secondary = "#94a3b8" if is_dark else "#64748b"
    accent_indigo = "#6366f1"
    accent_purple = "#8b5cf6"
    accent_emerald = "#10b981"
    
    css = f"""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    
    code, pre {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    /* Global Metric Cards */
    .metric-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 14px 0 rgba(0, 0, 0, {0.25 if is_dark else 0.05});
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px 0 rgba(99, 102, 241, 0.15);
    }}
    .metric-label {{
        font-size: 13px;
        font-weight: 600;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }}
    .metric-value {{
        font-size: 28px;
        font-weight: 800;
        color: {text_primary};
        line-height: 1.2;
    }}
    .metric-sub {{
        font-size: 12px;
        color: {accent_emerald};
        margin-top: 6px;
        font-weight: 500;
    }}

    /* Hero / Banner Header */
    .hero-banner {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }}
    .hero-title {{
        font-size: 26px;
        font-weight: 800;
        color: {text_primary};
        margin: 0;
    }}
    .hero-subtitle {{
        font-size: 14px;
        color: {text_secondary};
        margin-top: 6px;
    }}

    /* Badges & Pills */
    .badge-pill {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }}
    .badge-easy {{ background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }}
    .badge-medium {{ background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .badge-hard {{ background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }}

    .badge-mastered {{ background: rgba(16, 185, 129, 0.2); color: #10b981; }}
    .badge-progress {{ background: rgba(59, 130, 246, 0.2); color: #3b82f6; }}
    .badge-notstarted {{ background: rgba(148, 163, 184, 0.2); color: #94a3b8; }}

    /* Flashcard Modern Flip Card Container */
    .flashcard-box {{
        background: {bg_card};
        border: 2px solid {accent_indigo};
        border-radius: 18px;
        padding: 36px 28px;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
        margin: 15px 0;
    }}

    /* Pomodoro Timer Display */
    .timer-display {{
        background: {bg_card};
        border: 2px solid rgba(99, 102, 241, 0.4);
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        max-width: 420px;
        margin: 0 auto;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
    }}
    .timer-digits {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 64px;
        font-weight: 800;
        color: {accent_indigo};
        letter-spacing: 2px;
        margin: 15px 0;
    }}

    /* Custom Streamlit Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: {bg_card} !important;
        border-right: 1px solid {border_color};
    }}
    
    /* Clean Buttons */
    .stButton>button {{
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }}
    </style>
    """
    return css
