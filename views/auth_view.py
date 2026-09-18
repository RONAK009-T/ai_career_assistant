import streamlit as st
from utils.auth import login_user, register_user, reset_password
from utils.validators import validate_email, validate_username, validate_password_strength
from utils.ui_components import render_card, render_callout

def render_auth_page():
    """Renders authentication page with tabs for Login, Register, and Forgot Password."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem; margin-top: 1rem;">
                <h1 style="font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, #10B981 0%, #06B6D4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    🤖 NexusAI Career Assistant
                </h1>
                <p style="color: #9CA3AF; font-size: 1rem;">
                    Accelerate your career, optimize your productivity, and master new skills.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_register, tab_forgot = st.tabs(["🔑 Log In", "✨ Create Account", "🔒 Reset Password"])
        
        with tab_login:
            st.markdown("### Welcome Back")
            with st.form("login_form"):
                username_or_email = st.text_input("Username or Email", placeholder="alex or alex@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Log In to Dashboard", use_container_width=True)
                
                if submitted:
                    if not username_or_email or not password:
                        st.error("Please fill in both fields.")
                    else:
                        success, message = login_user(username_or_email, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                            
        with tab_register:
            st.markdown("### Create New Account")
            with st.form("register_form"):
                full_name = st.text_input("Full Name", placeholder="Alex Johnson")
                username = st.text_input("Username", placeholder="alex_dev")
                email = st.text_input("Email Address", placeholder="alex@example.com")
                target_role = st.selectbox("Target Career / Role", [
                    "Full Stack Developer",
                    "Python Developer",
                    "Backend Engineer",
                    "Frontend Engineer",
                    "Data Scientist",
                    "Data Analyst",
                    "AI / Machine Learning Engineer",
                    "DevOps / Cloud Engineer",
                    "Cybersecurity Analyst",
                    "Product / Project Manager",
                    "Other"
                ])
                password = st.text_input("Create Password", type="password", placeholder="At least 6 characters")
                password_confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                
                submitted = st.form_submit_button("Create My Account", use_container_width=True)
                
                if submitted:
                    if not full_name or not username or not email or not password:
                        st.error("Please complete all required fields.")
                    elif password != password_confirm:
                        st.error("Passwords do not match.")
                    elif not validate_email(email):
                        st.error("Please enter a valid email address.")
                    else:
                        u_valid, u_msg = validate_username(username)
                        if not u_valid:
                            st.error(u_msg)
                        else:
                            p_valid, p_msg = validate_password_strength(password)
                            if not p_valid:
                                st.error(p_msg)
                            else:
                                success, message = register_user(username, email, password, full_name, target_role)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)

        with tab_forgot:
            st.markdown("### Reset Password")
            st.info("Enter your registered email address to set a new password.")
            with st.form("forgot_password_form"):
                reset_email = st.text_input("Registered Email", placeholder="alex@example.com")
                new_pwd = st.text_input("New Password", type="password", placeholder="••••••••")
                new_pwd_confirm = st.text_input("Confirm New Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Update Password", use_container_width=True)
                
                if submitted:
                    if not reset_email or not new_pwd:
                        st.error("Please enter email and new password.")
                    elif new_pwd != new_pwd_confirm:
                        st.error("Passwords do not match.")
                    elif len(new_pwd) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        success, message = reset_password(reset_email, new_pwd)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
