"""
Admin Panel page for Aqualog application.
Administrative functions and system management.
"""

import streamlit as st
from app.utils.auth import get_auth_manager


def show_admin_panel_page():
    """Display the admin panel page."""

    # Get authentication manager and require admin privileges
    auth_manager = get_auth_manager()

    # Check if user is admin (this will show error if not)
    if not auth_manager.is_admin():
        st.error("🚫 Access Denied: Administrator privileges required")
        st.info("Contact your administrator to access this page.")
        return

    user = auth_manager.get_current_user()

    st.title("⚙️ Admin Panel")
    st.markdown("---")

    # Placeholder content for now
    st.info(
        "🚧 Admin Panel is under construction. This will provide user management, backups, and system configuration."
    )
