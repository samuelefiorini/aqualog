"""
Aqualog - Freediving Society Management System

Main entry point for the Streamlit application using modern st.navigation.
"""

import streamlit as st
from app.utils.auth import get_auth_manager
from app.pages.dashboard import show_dashboard_page
from app.pages.members import show_members_page
from app.pages.cooper_tests import show_cooper_tests_page
from app.pages.indoor_trials import show_indoor_trials_page
from app.pages.admin_panel import show_admin_panel_page

# Simple page configuration without custom CSS

# Configure page
st.set_page_config(
    page_title="Aqualog - Freediving Management",
    page_icon=":material/pool:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/aqualog",
        "Report a bug": "https://github.com/your-repo/aqualog/issues",
        "About": "Aqualog - Freediving Society Management System v1.0",
    },
)


def main():
    """Main application function with navigation."""

    # Get authentication manager
    auth_manager = get_auth_manager()

    # Check authentication
    if not auth_manager.require_authentication():
        # Authentication form is shown, stop execution
        return

    # Get current user
    user = auth_manager.get_current_user()

    # Define pages based on user role
    if user.is_admin:
        pages = {
            "Main": [
                st.Page(
                    show_dashboard_page, title="Dashboard", icon=":material/dashboard:"
                ),
            ],
            "Data Management": [
                st.Page(show_members_page, title="Members", icon=":material/group:"),
                st.Page(
                    show_cooper_tests_page,
                    title="Cooper Tests",
                    icon=":material/timer:",
                ),
                st.Page(
                    show_indoor_trials_page,
                    title="Indoor Trials",
                    icon=":material/fitness_center:",
                ),
            ],
            "Administration": [
                st.Page(
                    show_admin_panel_page,
                    title="Admin Panel",
                    icon=":material/admin_panel_settings:",
                ),
            ],
        }
    else:
        pages = {
            "Main": [
                st.Page(
                    show_dashboard_page, title="Dashboard", icon=":material/dashboard:"
                ),
            ],
            "Data Views": [
                st.Page(show_members_page, title="Members", icon=":material/group:"),
                st.Page(
                    show_cooper_tests_page,
                    title="Cooper Tests",
                    icon=":material/timer:",
                ),
                st.Page(
                    show_indoor_trials_page,
                    title="Indoor Trials",
                    icon=":material/fitness_center:",
                ),
            ],
        }

    # Create navigation
    pg = st.navigation(pages)

    # Add header with user info and logout
    st.title("🏊‍♂️ Aqualog - Freediving Management System")

    # Sidebar with user info and logout
    with st.sidebar:
        st.markdown("---")

        # User info
        st.markdown("**👤 Current User**")
        st.write(f"**{user.display_name}**")
        st.write(f"Role: {user.role}")

        st.markdown("---")

        # Quick stats
        st.markdown("**📊 Quick Stats**")
        try:
            from db import get_database_stats

            stats = get_database_stats()
            st.write(f"Members: {stats.total_members}")
            st.write(f"Cooper Tests: {stats.total_cooper_tests}")
            st.write(f"Indoor Trials: {stats.total_indoor_trials}")
        except Exception:
            st.write("Data not available")

        st.markdown("---")

        # System info
        st.markdown("**ℹ️ System**")
        st.write("Version: 1.0.0")
        st.write("Database: DuckDB")

        st.markdown("---")

        # Logout button in sidebar
        if st.button("🚪 Logout", width="stretch", type="secondary"):
            auth_manager.logout()
            st.rerun()

    # Run the selected page
    pg.run()

    # Footer
    st.markdown("---")
    st.caption(
        f"🏊‍♂️ Aqualog - Freediving Society Management System | Logged in as {user.username}"
    )


if __name__ == "__main__":
    main()
