import streamlit as st
from pathlib import Path

def apply_custom_css():
    """Injects custom dark glassmorphism CSS into Streamlit application."""
    css_path = Path(__file__).resolve().parent.parent / "static" / "css" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def render_page_header(title: str, subtitle: str = "", badge: str = None):
    """Renders a modern page header with optional status badge."""
    badge_html = f'<span class="nexus-badge badge-cyan">{badge}</span>' if badge else ""
    st.markdown(f"""
        <div style="margin-bottom: 1.75rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
                <h1 style="font-size: 2rem; font-weight: 800; margin: 0; background: linear-gradient(135deg, #F9FAFB 0%, #9CA3AF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {title}
                </h1>
                {badge_html}
            </div>
            <p style="color: #9CA3AF; margin-top: 0.35rem; font-size: 1rem;">
                {subtitle}
            </p>
        </div>
    """, unsafe_allow_html=True)

def render_card(content_html: str, title: str = None, badge: str = None, glow: bool = False):
    """Renders content enclosed in a glassmorphic card container."""
    glow_class = "nexus-card-glow" if glow else ""
    header_html = ""
    if title:
        badge_html = f'<span class="nexus-badge badge-emerald">{badge}</span>' if badge else ""
        header_html = f"""
            <div class="nexus-card-header">
                <div class="nexus-title">{title}</div>
                {badge_html}
            </div>
        """
    st.markdown(f"""
        <div class="nexus-card {glow_class}">
            {header_html}
            {content_html}
        </div>
    """, unsafe_allow_html=True)

def render_kpi(label: str, value: str, subtext: str = "", badge: str = "badge-cyan"):
    """Renders a single KPI tile."""
    sub_html = f'<div style="font-size: 0.75rem; color: #6B7280; margin-top: 0.25rem;">{subtext}</div>' if subtext else ""
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">{label}</div>
            <div class="kpi-val">{value}</div>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)

def render_skill_bar(skill_name: str, level_label: str, percentage: int, color: str = "emerald"):
    """Renders a custom styled skill progress bar."""
    fill_class = f"skill-fill-{color}"
    st.markdown(f"""
        <div class="skill-bar-wrap">
            <div class="skill-info">
                <span>{skill_name}</span>
                <span style="color: #9CA3AF; font-size: 0.8rem;">{level_label} ({percentage}%)</span>
            </div>
            <div class="skill-track">
                <div class="{fill_class}" style="width: {percentage}%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_callout(message: str, callout_type: str = "info", icon: str = "💡"):
    """Renders a styled alert or recommendation callout."""
    type_class = f"alert-{callout_type}"
    st.markdown(f"""
        <div class="nexus-alert {type_class}">
            <div style="font-size: 1.25rem;">{icon}</div>
            <div>{message}</div>
        </div>
    """, unsafe_allow_html=True)
