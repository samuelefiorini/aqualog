"""
Indoor Trials page for Aqualog application.
Displays indoor trial data and performance analysis.
"""

import streamlit as st
from app.utils.auth import get_auth_manager


def show_indoor_trials_page():
    """Display the indoor trials analysis page."""

    # Get authentication manager and current user
    auth_manager = get_auth_manager()
    user = auth_manager.get_current_user()

    st.title("🏋️ Indoor Trials Analysis")
    st.markdown("---")

    # Placeholder content for now
    st.info(
        "🚧 Indoor Trials page is under construction. This will display indoor trial data and performance analysis."
    )

    # Show user permissions
    if user.is_admin:
        st.success(
            "👑 Administrator - You have full read/write access to indoor trial data"
        )
    else:
        st.info("👤 User - You have read-only access to indoor trial data")
