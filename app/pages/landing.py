"""
Landing page for Aqualog application.
Displays key performance indicators and provides navigation guidance.
"""

import streamlit as st
from loguru import logger

from db.queries import get_database_stats


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_database_statistics():
    """Load database statistics with caching for optimal performance."""
    try:
        stats = get_database_stats()
        logger.info("Successfully loaded database statistics for landing page")
        return stats
    except Exception as e:
        logger.error(f"Failed to load database statistics: {e}")
        raise


def create_kpi_display(stats):
    """Create KPI display with metrics."""
    st.subheader(":material/analytics: Key Performance Indicators")

    # Main KPI metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label=":material/group: Total Members",
            value=stats.total_members,
            help="Total number of registered society members",
        )

    with col2:
        st.metric(
            label=":material/timer: Cooper Tests",
            value=stats.total_cooper_tests,
            help="Total number of Cooper test sessions recorded",
        )

    with col3:
        st.metric(
            label=":material/aq_indoor: Indoor Trials",
            value=stats.total_indoor_trials,
            help="Total number of indoor training trials recorded",
        )

    with col4:
        st.metric(
            label=":material/save: Database Size",
            value=f"{stats.database_size_mb:.1f} MB",
            help="Current size of the database file",
        )


def show_welcome_message():
    """Display friendly welcome message and navigation hints."""
    st.title(":material/analytics: Aqualog Dashboard")

    # Navigation hints
    st.info("""
    **:material/explore: Navigation Guide:**
    - Use the **sidebar menu** to navigate between different sections
    - **Members** - View the complete registry of society members
    - **Cooper Tests** - Analyze performance trends and diving patterns
    - **Indoor Trials** - Track training progress and distance achievements
    """)


def show_error_fallback():
    """Display fallback content when data loading fails."""
    st.error("⚠️ Unable to load dashboard statistics")

    st.markdown("""
    **Possible causes:**
    - Database connection issues
    - Missing or corrupted data
    - System maintenance in progress
    
    **What you can do:**
    - Try refreshing the page
    - Check your internet connection
    - Contact your system administrator if the problem persists
    """)

    # Show placeholder metrics
    st.subheader(":material/analytics: Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(":material/group: Total Members", "--")

    with col2:
        st.metric(":material/timer: Cooper Tests", "--")

    with col3:
        st.metric(":material/aq_indoor: Indoor Trials", "--")

    with col4:
        st.metric(":material/save: Database Size", "-- MB")


def show_landing_page():
    """Main landing page function."""
    # Welcome message and navigation hints
    show_welcome_message()

    st.divider()

    try:
        # Load data with caching
        stats = load_database_statistics()

        # Display KPIs
        create_kpi_display(stats)

        # Additional insights
        st.divider()
        st.subheader(":material/lightbulb: Quick Insights")

        col1, col2 = st.columns(2)

        with col1:
            if stats.total_members > 0:
                avg_tests = stats.total_cooper_tests / stats.total_members

                st.metric(
                    ":material/bid_landscape: Avg Tests per Member",
                    f"{avg_tests:.1f}",
                    help="Average Cooper tests per registered member",
                )
            else:
                st.metric(":material/bid_landscape: Avg Tests per Member", "--")

        with col2:
            if stats.total_members > 0:
                avg_trials = stats.total_indoor_trials / stats.total_members

                st.metric(
                    ":material/target: Avg Trials per Member",
                    f"{avg_trials:.1f}",
                    help="Average indoor trials per registered member",
                )
            else:
                st.metric(":material/target: Avg Trials per Member", "--")

        # Total activities summary
        total_activities = stats.total_cooper_tests + stats.total_indoor_trials
        st.metric(
            ":material/trophy: Total Activities",
            total_activities,
            help="Combined Cooper tests and indoor trials",
        )

    except Exception as e:
        logger.error(f"Landing page data loading error: {e}")
        show_error_fallback()
