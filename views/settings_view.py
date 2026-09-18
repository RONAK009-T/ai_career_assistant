import os
import streamlit as st
from utils.auth import get_current_user
from utils.ui_components import render_page_header
from database.models import update_user_profile

def render_settings():
    """Renders User Profile and Gemini API Key configuration settings."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="⚙️ Settings & Profile Configuration",
        subtitle="Manage your personal profile, target career track, and Gemini AI credentials.",
        badge="System"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👤 Profile Details")
        with st.form("profile_form"):
            full_name = st.text_input("Full Name", value=user.get('full_name', ''))
            target_role = st.text_input("Target Career Role", value=user.get('target_role', 'Software Engineer'))
            bio = st.text_area("Professional Bio", value=user.get('bio', ''), height=100)
            submitted = st.form_submit_button("Update Profile", use_container_width=True)
            if submitted:
                update_user_profile(user['id'], full_name, target_role, bio)
                st.success("Profile updated successfully!")
                st.rerun()

    with col2:
        st.markdown("### 🔑 Gemini AI Configuration")
        st.info("Get a free Gemini API Key at [Google AI Studio](https://aistudio.google.com).")
        
        current_key = os.getenv("GEMINI_API_KEY", "")
        masked_key = f"{current_key[:4]}••••••••{current_key[-4:]}" if len(current_key) > 8 else "Not configured"
        st.markdown(f"**Current API Key Status:** `{masked_key}`")

        with st.form("api_key_form"):
            new_key = st.text_input("Set / Override Gemini API Key", type="password", placeholder="AIzaSy...")
            submitted_key = st.form_submit_button("Save API Key to Session", use_container_width=True)
            if submitted_key:
                if new_key:
                    os.environ["GEMINI_API_KEY"] = new_key.strip()
                    st.success("API Key updated for current session!")
                else:
                    st.error("Please enter a valid key.")
