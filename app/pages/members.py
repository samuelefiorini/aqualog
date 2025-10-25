"""
Members page for Aqualog application.
Displays the member registry with read-only access.
"""

import streamlit as st
from app.utils.auth import get_auth_manager


def show_members_page():
    """Display the members registry page."""

    # Get authentication manager and current user
    auth_manager = get_auth_manager()
    user = auth_manager.get_current_user()

    st.title("👥 Members Registry")
    st.markdown("---")

    # Placeholder content for now
    st.info(
        "🚧 Members page is under construction. This will display the member registry."
    )

    # Show user permissions
    if user.is_admin:
        st.success("👑 Administrator - You have full read/write access to member data")
    else:
        st.info("👤 User - You have read-only access to member data")
