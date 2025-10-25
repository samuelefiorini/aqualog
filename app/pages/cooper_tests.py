"""
Cooper Tests page for Aqualog application.
Displays Cooper test data and visualizations.
"""

import streamlit as st
from app.utils.auth import get_auth_manager


def show_cooper_tests_page():
    """Display the Cooper tests analysis page."""

    # Get authentication manager and current user
    auth_manager = get_auth_manager()
    user = auth_manager.get_current_user()

    st.title("⏱️ Cooper Tests Analysis")
    st.markdown("---")

    # Placeholder content for now
    st.info(
        "🚧 Cooper Tests page is under construction. This will display Cooper test data and visualizations."
    )

    # Show user permissions
    if user.is_admin:
        st.success(
            "👑 Administrator - You have full read/write access to Cooper test data"
        )
    else:
        st.info("👤 User - You have read-only access to Cooper test data")
