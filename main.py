"""
Aqualog - Freediving Society Management System

Main entry point for the Streamlit application.
"""

import streamlit as st
from app.utils.auth import get_auth_manager

# Add Material Icons CSS
st.markdown(
    """
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<style>
    .material-icons {
        vertical-align: middle;
        margin-right: 8px;
    }
    
    .main-header {
        background: linear-gradient(90deg, #1f77b4 0%, #17a2b8 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    
    .nav-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    
    .nav-card:hover {
        background: #e9ecef;
        transition: background-color 0.3s;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Configure page
st.set_page_config(
    page_title="Aqualog - Freediving Management",
    page_icon="🏊‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/aqualog",
        "Report a bug": "https://github.com/your-repo/aqualog/issues",
        "About": "Aqualog - Freediving Society Management System v1.0",
    },
)


def main():
    """Main application function."""

    # Get authentication manager
    auth_manager = get_auth_manager()

    # Check authentication
    if not auth_manager.require_authentication():
        # Authentication form is shown, stop execution
        return

    # User is authenticated, show main content
    st.markdown(
        """
    <div class="main-header">
        <h1><i class="material-icons">pool</i>Aqualog - Freediving Management System</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Get current user
    user = auth_manager.get_current_user()

    # Welcome message
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.success(f"🌊 Welcome, **{user.display_name}**!")
        if user.is_admin:
            st.info("👑 Administrator - Full Access")
        else:
            st.info("👤 User - Read-only Access")

    with col3:
        st.write("")  # Empty space for layout

    # Main content
    st.markdown("---")

    # Dashboard content
    st.markdown("## 📊 Dashboard")

    # Get database stats
    try:
        from db import get_database_stats

        stats = get_database_stats()

        # Display KPIs with enhanced styling
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
            <div class="metric-card">
                <h3><i class="material-icons">group</i>Members</h3>
                <h2 style="color: #1f77b4; margin: 0;">{stats.total_members}</h2>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
            <div class="metric-card">
                <h3><i class="material-icons">timer</i>Cooper Tests</h3>
                <h2 style="color: #17a2b8; margin: 0;">{stats.total_cooper_tests}</h2>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
            <div class="metric-card">
                <h3><i class="material-icons">fitness_center</i>Indoor Trials</h3>
                <h2 style="color: #28a745; margin: 0;">{stats.total_indoor_trials}</h2>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                f"""
            <div class="metric-card">
                <h3><i class="material-icons">storage</i>Database</h3>
                <h2 style="color: #ffc107; margin: 0;">{stats.database_size_mb:.1f} MB</h2>
            </div>
            """,
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")

    # Navigation section
    st.markdown("---")
    st.markdown("## 🧭 Quick Navigation")

    # Create navigation cards
    if user.is_admin:
        nav_cols = st.columns(3)

        with nav_cols[0]:
            st.markdown(
                """
            <div class="nav-card">
                <h4><i class="material-icons">group</i>Member Management</h4>
                <p>View and manage the society member registry</p>
                <small>✅ Read and write access</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with nav_cols[1]:
            st.markdown(
                """
            <div class="nav-card">
                <h4><i class="material-icons">assessment</i>Performance Analysis</h4>
                <p>Cooper tests and indoor trials with charts and trends</p>
                <small>✅ Read and write access</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with nav_cols[2]:
            st.markdown(
                """
            <div class="nav-card">
                <h4><i class="material-icons">admin_panel_settings</i>Admin Panel</h4>
                <p>User management, backups and system configuration</p>
                <small>👑 Administrators only</small>
            </div>
            """,
                unsafe_allow_html=True,
            )
    else:
        nav_cols = st.columns(2)

        with nav_cols[0]:
            st.markdown(
                """
            <div class="nav-card">
                <h4><i class="material-icons">group</i>View Members</h4>
                <p>Browse the society member registry</p>
                <small>👁️ Read-only access</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with nav_cols[1]:
            st.markdown(
                """
            <div class="nav-card">
                <h4><i class="material-icons">assessment</i>Performance Analysis</h4>
                <p>View Cooper tests and indoor trials</p>
                <small>👁️ Read-only access</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Sidebar with system info
    with st.sidebar:
        st.markdown("### 🏊‍♂️ Aqualog")
        st.markdown("---")

        # User info
        st.markdown("**👤 Current User**")
        st.write(f"**{user.display_name}**")
        st.write(f"Role: {user.role}")

        st.markdown("---")

        # Quick stats
        st.markdown("**📊 Quick Stats**")
        try:
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

        # Logout button in sidebar
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            auth_manager.logout()
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
        "<i class='material-icons' style='font-size: 16px;'>pool</i>"
        "Aqualog - Freediving Society Management System | "
        f"Logged in as {user.username}"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
