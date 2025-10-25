"""
Dashboard page for Aqualog application.
Main landing page with KPIs and navigation.
"""

import streamlit as st
from app.utils.auth import get_auth_manager


def show_dashboard_page():
    """Display the main dashboard page."""

    # Get authentication manager and current user
    auth_manager = get_auth_manager()
    user = auth_manager.get_current_user()

    # Welcome message with navigation hints
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.success(f"🌊 Welcome back, **{user.display_name}**!")
        if user.is_admin:
            st.info("👑 Administrator - Full Access")
            st.caption(
                "💡 You can manage members, view analytics, and access admin settings"
            )
        else:
            st.info("👤 User - Read-only Access")
            st.caption("💡 You can browse member data and view performance analytics")

    with col2:
        # Add a refresh button for the dashboard
        if st.button("refresh Refresh Data", help="Reload dashboard statistics"):
            st.cache_data.clear()
            st.rerun()

    with col3:
        st.write("")  # Empty space for layout

    # Main content
    st.markdown("---")

    # Dashboard content
    st.header("📊 Dashboard")

    # Get database stats with caching
    @st.cache_data(ttl=60)  # Cache for 60 seconds
    def load_dashboard_stats():
        """Load database statistics with caching for better performance."""
        from db import get_database_stats

        return get_database_stats()

    try:
        stats = load_dashboard_stats()

        # Display KPIs with simple metrics
        st.subheader("📈 Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("👥 Members", stats.total_members)

        with col2:
            st.metric("⏱️ Cooper Tests", stats.total_cooper_tests)

        with col3:
            st.metric("🏋️ Indoor Trials", stats.total_indoor_trials)

        with col4:
            st.metric("💾 Database", f"{stats.database_size_mb:.1f} MB")

        # Additional dashboard insights
        st.markdown("---")
        st.subheader("💡 Quick Insights")

        insight_col1, insight_col2, insight_col3 = st.columns(3)

        with insight_col1:
            if stats.total_members > 0:
                avg_tests_per_member = stats.total_cooper_tests / stats.total_members
                st.metric(
                    label="Avg Cooper Tests per Member",
                    value=f"{avg_tests_per_member:.1f}",
                    help="Average number of Cooper tests per registered member",
                )
            else:
                st.metric(label="Avg Cooper Tests per Member", value="--")

        with insight_col2:
            if stats.total_members > 0:
                avg_trials_per_member = stats.total_indoor_trials / stats.total_members
                st.metric(
                    label="Avg Indoor Trials per Member",
                    value=f"{avg_trials_per_member:.1f}",
                    help="Average number of indoor trials per registered member",
                )
            else:
                st.metric(label="Avg Indoor Trials per Member", value="--")

        with insight_col3:
            total_activities = stats.total_cooper_tests + stats.total_indoor_trials
            st.metric(
                label="Total Activities",
                value=f"{total_activities}",
                help="Combined total of Cooper tests and indoor trials",
            )

    except Exception as e:
        st.error("⚠️ Unable to load dashboard statistics")
        st.info(
            "This might be due to database connectivity issues or missing data. Please try refreshing the page or contact your administrator."
        )

        # Show a fallback dashboard with placeholder values
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("👥 Members", "--")

        with col2:
            st.metric("⏱️ Cooper Tests", "--")

        with col3:
            st.metric("🏋️ Indoor Trials", "--")

        with col4:
            st.metric("💾 Database", "-- MB")

        # Log the error for debugging
        import logging

        logging.error(f"Dashboard data loading error: {e}")

    # Navigation section
    st.markdown("---")
    st.subheader("🧭 Quick Navigation")
    st.caption(
        "Use the sidebar navigation to access different sections of the application"
    )

    # Show available pages based on user role
    if user.is_admin:
        st.info("""
        **Available Pages:**
        - 👥 **Members** - View and manage the society member registry
        - ⏱️ **Cooper Tests** - Cooper tests and performance analysis  
        - 🏋️ **Indoor Trials** - Indoor trial data and trends
        - ⚙️ **Admin Panel** - User management and system configuration
        """)
    else:
        st.info("""
        **Available Pages:**
        - 👥 **Members** - Browse the society member registry (read-only)
        - ⏱️ **Cooper Tests** - View Cooper test data and analysis (read-only)
        - 🏋️ **Indoor Trials** - View indoor trial data (read-only)
        """)

    st.caption("💡 Navigate using the sidebar menu")
