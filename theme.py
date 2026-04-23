"""
Dynamic theme management for dark/light mode toggle
Generates CSS on-the-fly based on selected theme
"""

import streamlit as st
from config import THEMES


def get_theme():
    """Get current theme from session state"""
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    return st.session_state.theme


def set_theme(theme_name):
    """Set theme and save to session state"""
    if theme_name in THEMES:
        st.session_state.theme = theme_name


def get_colors():
    """Get color dict for current theme"""
    return THEMES[get_theme()]


def apply_theme_css():
    """Generate and apply CSS for current theme"""
    colors = get_colors()
    
    css = f"""
    <style>
    /* ============ GLOBAL ============ */
    .stApp {{
        background: {colors['bg_primary']};
        color: {colors['text_primary']};
    }}
    
    section[data-testid="stSidebar"] {{
        background: {colors['bg_secondary']};
    }}
    
    /* ============ TYPOGRAPHY ============ */
    .title {{
        font-size: 44px;
        font-weight: 800;
        color: {colors['accent']};
        line-height: 1.05;
    }}
    
    .subtitle {{
        color: {colors['text_secondary']};
        letter-spacing: 2px;
        font-size: 12px;
        text-transform: uppercase;
    }}
    
    .section {{
        font-size: 22px;
        font-weight: 700;
        color: {colors['text_primary']};
        margin: 24px 0 16px;
        border-bottom: 2px solid {colors['border_color']};
        padding-bottom: 8px;
    }}
    
    /* ============ CARDS & CONTAINERS ============ */
    .card {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border_color']};
        border-radius: 8px;
        padding: 18px;
        color: {colors['text_primary']};
    }}
    
    .card.buy {{
        border-color: rgba(110, 231, 183, 0.65);
        color: {colors['green']};
    }}
    
    .card.sell {{
        border-color: rgba(252, 165, 165, 0.65);
        color: {colors['red']};
    }}
    
    .card.hold {{
        border-color: rgba(252, 211, 77, 0.65);
        color: {colors['yellow']};
    }}
    
    /* ============ SIGNAL DISPLAY ============ */
    .signal {{
        font-size: 44px;
        font-weight: 800;
        margin: 8px 0;
    }}
    
    /* ============ TEXT UTILITIES ============ */
    .small-note {{
        color: {colors['text_secondary']};
        font-size: 13px;
    }}
    
    /* ============ NEWS BOX ============ */
    .news-box {{
        background: {colors['bg_card']};
        border-left: 3px solid;
        padding: 14px;
        margin: 10px 0;
        border-radius: 8px;
        color: {colors['text_primary']};
    }}
    
    /* ============ BUTTONS ============ */
    .stButton > button {{
        background: linear-gradient(135deg, {colors['accent']}, #8b5cf6) !important;
        color: white !important;
        border: none !important;
    }}
    
    .stButton > button:hover {{
        opacity: 0.85 !important;
    }}
    
    /* ============ INPUTS & SELECTS ============ */
    .stSelectbox {{
        color: {colors['text_primary']};
    }}
    
    .stTextInput input {{
        background: {colors['bg_secondary']};
        color: {colors['text_primary']};
        border: 1px solid {colors['border_color']} !important;
    }}
    
    .stTextArea textarea {{
        background: {colors['bg_secondary']};
        color: {colors['text_primary']};
        border: 1px solid {colors['border_color']} !important;
    }}
    
    /* ============ METRICS ============ */
    .stMetric {{
        background: {colors['bg_card']};
        border-radius: 8px;
    }}
    
    /* ============ INFO/WARNING/ERROR BOXES ============ */
    .stAlert {{
        border-radius: 8px;
    }}
    
    /* ============ PLOTLY CHARTS ============ */
    .plot-container {{
        background: transparent;
    }}
    
    /* ============ DIVIDER ============ */
    hr {{
        border-color: {colors['border_color']} !important;
    }}
    
    /* ============ FOOTER ============ */
    .footer {{
        text-align: center;
        color: {colors['text_secondary']};
        font-size: 10px;
        margin-top: 20px;
    }}
    
    /* ============ THEME TOGGLE BUTTON ============ */
    .theme-toggle {{
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 999;
    }}
    
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def theme_toggle_button():
    """
    Display theme toggle button in sidebar.
    Should be called in sidebar context.
    """
    current = get_theme()
    new_theme = "light" if current == "dark" else "dark"
    
    if st.button(f"🌓 {new_theme.capitalize()} Mode", width="stretch"):
        set_theme(new_theme)
        st.rerun()
