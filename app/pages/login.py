"""
Login page for Aqualog application.
Handles user authentication and redirects to main application.
"""

import streamlit as st
from app.utils.auth import get_auth_manager


def main():
    """Main login page function."""
    # Configure page
    st.set_page_config(
        page_title="Aqualog - Login",
        page_icon=":material/pool:",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    # Get authentication manager
    auth_manager = get_auth_manager()

    # If already authenticated, show status
    if auth_manager.is_authenticated():
        st.success(f"✅ Already logged in as **{auth_manager.get_current_user()}**")
        st.info(
            "🏠 Navigate to the main application pages using the sidebar or navigation."
        )

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚪 Logout", type="secondary", width="stretch"):
                auth_manager.logout()
                st.rerun()

        # Show available pages
        st.markdown("---")
        st.subheader("📄 Available Pages")
        st.markdown("""
        - **Dashboard** - View system statistics and overview
        - **Members** - Browse the member registry
        - **Cooper Tests** - View Cooper test results and trends
        - **Indoor Trials** - Analyze indoor training data
        """)

        return

    # Show login form
    auth_manager.show_login_form()


if __name__ == "__main__":
    main()
