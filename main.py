"""
Aqualog - Freediving Society Management System

Main entry point for the Streamlit application using modern st.navigation.
"""

import streamlit as st
from app.utils.auth import get_auth_manager
from app.pages.landing import show_landing_page
from app.pages.members import show_members_page
from app.pages.cooper_tests import show_cooper_tests_page
from app.pages.indoor_trials import show_indoor_trials_page
from app.pages.admin_panel import show_admin_panel_page


from app.utils.config import TITLE


# Simple page configuration without custom CSS

# Configure page
st.set_page_config(
    page_title="Aqualog - Freediving Management",
    page_icon=":material/head_mounted_device:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/samuelefiorini/aqualog?tab=readme-ov-file#%E2%80%8D%EF%B8%8F-aqualog---freediving-society-management-system",
        "Report a bug": "https://github.com/samuelefiorini/aqualog/issues",
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
                    show_landing_page, title="Dashboard", icon=":material/dashboard:"
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
                    show_landing_page, title="Dashboard", icon=":material/dashboard:"
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
    st.title(TITLE)

    # Sidebar with user info and logout
    with st.sidebar:
        st.divider()

        # Enhanced user info with proper emoji and styling
        if user.is_admin:
            st.markdown("### :material/crown: Administrator")
            st.markdown(f"**{user.display_name}**")
            st.caption("Full system access")
        else:
            st.markdown("### :material/account_box: User")
            st.markdown(f"**{user.display_name}**")
            st.caption("Read-only access")

        st.divider()

        # Logout button in sidebar
        if st.button(":material/logout: Logout", type="secondary"):
            auth_manager.logout()
            st.rerun()

    # Run the selected page
    pg.run()

    # Footer
    st.divider()
    st.caption(f"{TITLE} | Logged in as {user.username}")


if __name__ == "__main__":
    main()
