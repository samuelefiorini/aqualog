"""
Indoor Trials page for Aqualog application.
Displays indoor trial data and performance analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from loguru import logger

from db.queries import get_all_indoor_trials, get_all_members


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_indoor_trials_data():
    """Load indoor trials data with caching for optimal performance."""
    try:
        trials = get_all_indoor_trials()
        members = get_all_members()
        logger.info(
            f"Successfully loaded {len(trials)} indoor trials and {len(members)} members"
        )
        return trials, members
    except Exception as e:
        logger.error(f"Failed to load indoor trials data: {e}")
        raise


def process_indoor_trials_data(trials, members):
    """Convert indoor trials list to formatted pandas DataFrame."""
    if not trials:
        return pd.DataFrame()

    # Create member lookup
    member_lookup = {m.id: f"{m.name} {m.surname}" for m in members}

    # Convert to list of dictionaries for DataFrame
    trials_data = []
    for trial in trials:
        # Calculate speed if time is available
        speed_mps = None
        if trial.time_seconds and trial.time_seconds > 0:
            speed_mps = trial.distance_meters / trial.time_seconds

        trials_data.append(
            {
                "trial_id": trial.id,
                "member_id": trial.member_id,
                "member_name": member_lookup.get(
                    trial.member_id, f"Member {trial.member_id}"
                ),
                "trial_date": trial.trial_date,
                "location": trial.location or "Unknown",
                "distance_meters": trial.distance_meters,
                "time_seconds": trial.time_seconds,
                "speed_mps": speed_mps,
                "pool_length_meters": trial.pool_length_meters,
                "created_at": trial.created_at,
            }
        )

    return pd.DataFrame(trials_data)


def create_distance_vs_time_chart(df):
    """Create distance vs time scatter plot."""
    if df.empty:
        return None

    # Filter out trials without time data for this chart
    df_with_time = df[df["time_seconds"].notna() & (df["time_seconds"] > 0)]

    if df_with_time.empty:
        return None

    fig = px.scatter(
        df_with_time,
        x="time_seconds",
        y="distance_meters",
        color="member_name",
        size="speed_mps",
        hover_data=["trial_date", "location", "pool_length_meters"],
        labels={
            "time_seconds": "Time (seconds)",
            "distance_meters": "Distance (meters)",
            "member_name": "Member",
            "speed_mps": "Speed (m/s)",
        },
    )

    # Calculate linear regression statistics for all data
    import numpy as np
    from scipy import stats

    x = df_with_time["time_seconds"].values
    y = df_with_time["distance_meters"].values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # Add regression line for all data
    x_range = np.array([x.min(), x.max()])
    y_pred = slope * x_range + intercept

    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_pred,
            mode="lines",
            name="Linear Regression",
            line=dict(color="grey", width=2, dash="dash"),
            showlegend=True,
        )
    )

    # Add annotation with regression info
    fig.add_annotation(
        text=f"Linear Regression<br>Slope: {slope:.2f} m/s<br>R²: {r_value**2:.3f}",
        xref="paper",
        yref="paper",
        x=0.02,
        y=0.98,
        showarrow=False,
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="gray",
        borderwidth=1,
        font=dict(size=10),
        align="left",
        xanchor="left",
        yanchor="top",
    )

    fig.update_layout(
        height=650,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(b=100),
    )
    return fig


def create_performance_trends_chart(df):
    """Create performance trends over time chart."""
    if df.empty:
        return None

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Distance Over Time",
            "Speed Over Time (with time data)",
            "Distance by Pool Length",
            "Performance by Location",
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
        ],
    )

    # Distance over time
    for member_name in df["member_name"].unique():
        member_data = df[df["member_name"] == member_name].sort_values("trial_date")

        fig.add_trace(
            go.Scatter(
                x=member_data["trial_date"],
                y=member_data["distance_meters"],
                mode="lines+markers",
                name=f"{member_name} - Distance",
                line=dict(width=2),
                showlegend=True,
            ),
            row=1,
            col=1,
        )

    # Speed over time (only for trials with time data)
    df_with_time = df[df["speed_mps"].notna()]
    for member_name in df_with_time["member_name"].unique():
        member_data = df_with_time[
            df_with_time["member_name"] == member_name
        ].sort_values("trial_date")

        if not member_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=member_data["trial_date"],
                    y=member_data["speed_mps"],
                    mode="lines+markers",
                    name=f"{member_name} - Speed",
                    line=dict(width=2),
                    showlegend=False,
                ),
                row=1,
                col=2,
            )

    # Distance by pool length
    pool_lengths = df["pool_length_meters"].unique()
    for pool_length in pool_lengths:
        pool_data = df[df["pool_length_meters"] == pool_length]

        fig.add_trace(
            go.Box(
                y=pool_data["distance_meters"],
                name=f"{pool_length}m pool",
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    # Performance by location (top locations only)
    location_counts = df["location"].value_counts()
    top_locations = location_counts.head(5).index

    for location in top_locations:
        location_data = df[df["location"] == location]

        fig.add_trace(
            go.Box(
                y=location_data["distance_meters"],
                name=location[:20] + "..." if len(location) > 20 else location,
                showlegend=False,
            ),
            row=2,
            col=2,
        )

    # Update layout
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=2)
    fig.update_xaxes(title_text="Pool Length", row=2, col=1)
    fig.update_xaxes(title_text="Location", row=2, col=2)

    fig.update_yaxes(title_text="Distance (m)", row=1, col=1)
    fig.update_yaxes(title_text="Speed (m/s)", row=1, col=2)
    fig.update_yaxes(title_text="Distance (m)", row=2, col=1)
    fig.update_yaxes(title_text="Distance (m)", row=2, col=2)

    fig.update_layout(
        height=1000,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        margin=dict(b=120),
    )

    return fig


def create_speed_distance_distribution_chart(df, selected_member=None):
    """Create speed and distance distribution plots for all athletes with optional member highlight."""
    df_with_speed = df[df["speed_mps"].notna()]

    if df_with_speed.empty:
        return None

    # Create subplots with 2 rows
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(
            "Speed Distribution",
            "Distance Distribution",
        ),
        vertical_spacing=0.25,
    )

    # Speed distribution (top row) - all athletes combined
    fig.add_trace(
        go.Histogram(
            x=df_with_speed["speed_mps"],
            name="All Athletes",
            opacity=0.7,
            marker=dict(color="lightblue"),
            showlegend=False,
            nbinsx=30,
        ),
        row=1,
        col=1,
    )

    # Distance distribution (bottom row) - all athletes combined
    fig.add_trace(
        go.Histogram(
            x=df["distance_meters"],
            name="All Athletes",
            opacity=0.7,
            marker=dict(color="lightgreen"),
            showlegend=False,
            nbinsx=30,
        ),
        row=2,
        col=1,
    )

    # Add vertical lines for selected member's median values
    if selected_member and selected_member != "All Members":
        member_data = df[df["member_name"] == selected_member]
        member_speed_data = member_data[member_data["speed_mps"].notna()]

        if not member_speed_data.empty:
            median_speed = member_speed_data["speed_mps"].median()
            fig.add_vline(
                x=median_speed,
                line_dash="dot",
                line_color="red",
                line_width=2,
                annotation_text=f"{selected_member}<br>Median: {median_speed:.2f} m/s",
                annotation_position="bottom right",
                row=1,
                col=1,
            )

        if not member_data.empty:
            median_distance = member_data["distance_meters"].median()
            fig.add_vline(
                x=median_distance,
                line_dash="dot",
                line_color="red",
                line_width=2,
                annotation_text=f"{selected_member}<br>Median: {median_distance:.0f}m",
                annotation_position="bottom right",
                row=2,
                col=1,
            )

    # Update axes labels
    fig.update_xaxes(title_text="Speed (m/s)", row=1, col=1)
    fig.update_xaxes(title_text="Distance (m)", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)

    # Update layout
    fig.update_layout(
        height=700,
        showlegend=False,
    )

    return fig


def show_indoor_trials_statistics(df):
    """Display indoor trials statistics."""
    if df.empty:
        return

    st.subheader(":material/analytics: Indoor Trials Statistics")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Trials", len(df))

    with col2:
        unique_members = df["member_name"].nunique()
        st.metric("Active Members", unique_members)

    with col3:
        median_distance = df["distance_meters"].median()
        st.metric("Median Distance", f"{median_distance:.0f}m")

    with col4:
        trials_with_time = df["time_seconds"].notna().sum()
        time_percentage = (trials_with_time / len(df)) * 100
        st.metric("Trials with Time", f"{trials_with_time} ({time_percentage:.0f}%)")

    with col5:
        df_with_speed = df[df["speed_mps"].notna()]
        if not df_with_speed.empty:
            median_speed = df_with_speed["speed_mps"].median()
            st.metric("Median Speed", f"{median_speed:.2f} m/s")
        else:
            st.metric("Median Speed", "N/A")


def show_empty_state():
    """Display empty state when no indoor trials are found."""
    st.info(":material/inbox: No indoor trials found in the database")

    st.markdown("""
    **Possible reasons:**
    - No indoor trials have been recorded yet
    - Database connection issues
    - Data has not been populated
    
    **What you can do:**
    - Contact your administrator to add indoor trial data
    - Check if the database is properly initialized
    - Try refreshing the page
    """)


def show_error_fallback():
    """Display fallback content when data loading fails."""
    st.error("⚠️ Unable to load indoor trials data")

    st.markdown("""
    **Possible causes:**
    - Database connection issues
    - Missing or corrupted indoor trial data
    - System maintenance in progress
    
    **What you can do:**
    - Try refreshing the page
    - Check your internet connection
    - Contact your system administrator if the problem persists
    """)


def show_indoor_trials_page():
    """Display the indoor trials analysis page."""
    st.title(":material/aq_indoor: Indoor Trials Analysis")
    st.divider()

    try:
        # Load data with caching
        trials, members = load_indoor_trials_data()

        if not trials:
            show_empty_state()
            return

        # Process data for visualization
        df = process_indoor_trials_data(trials, members)

        if df.empty:
            show_empty_state()
            return

        # Show statistics
        show_indoor_trials_statistics(df)

        st.divider()

        # Filtering and member selection
        st.subheader(":material/search: Filters & Selection")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            # Member selection
            all_members = ["All Members"] + sorted(df["member_name"].unique().tolist())
            selected_member = st.selectbox(
                "Select Member",
                options=all_members,
                help="Choose a specific member or view all members",
            )

        with col2:
            # Date range filter
            min_date = df["trial_date"].min()
            max_date = df["trial_date"].max()

            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help="Filter trials by date range",
            )

        with col3:
            # Pool length filter
            pool_lengths = sorted(df["pool_length_meters"].unique())
            selected_pool_length = st.selectbox(
                "Pool Length",
                options=["All"] + [f"{length}m" for length in pool_lengths],
                help="Filter by pool length",
            )

        # Apply filters
        filtered_df = df.copy()

        if selected_member != "All Members":
            filtered_df = filtered_df[filtered_df["member_name"] == selected_member]

        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df["trial_date"] >= start_date)
                & (filtered_df["trial_date"] <= end_date)
            ]

        if selected_pool_length != "All":
            pool_length_value = int(selected_pool_length.replace("m", ""))
            filtered_df = filtered_df[
                filtered_df["pool_length_meters"] == pool_length_value
            ]

        if filtered_df.empty:
            st.warning("No indoor trials match the selected filters.")
            return

        st.caption(f"Showing {len(filtered_df)} trial(s) matching your filters")

        # Performance trends visualization
        st.divider()
        st.subheader(":material/bid_landscape: Indoor Trials Performance Analysis")

        trends_chart = create_performance_trends_chart(filtered_df)
        if trends_chart:
            st.plotly_chart(trends_chart)

        # Distance vs Time relationship (only for trials with time data)
        st.divider()
        st.subheader(":material/timer: Distance vs Time Performance")

        trials_with_time = filtered_df["time_seconds"].notna().sum()
        if trials_with_time > 0:
            distance_time_chart = create_distance_vs_time_chart(filtered_df)
            if distance_time_chart:
                st.plotly_chart(distance_time_chart)
                st.caption(
                    f"Showing {trials_with_time} trials with time data. Bubble size represents speed."
                )

            # Speed and distance distributions
            st.divider()
            st.subheader(":material/analytics: Speed & Distance Distributions")
            speed_dist_chart = create_speed_distance_distribution_chart(
                filtered_df, selected_member
            )
            if speed_dist_chart:
                st.plotly_chart(speed_dist_chart)
        else:
            st.info("No trials with time data available for distance vs time analysis.")

        # Data table
        st.divider()
        st.subheader(":material/data_exploration: Indoor Trials Data")

        # Prepare display dataframe
        display_df = filtered_df[
            [
                "member_name",
                "trial_date",
                "distance_meters",
                "time_seconds",
                "speed_mps",
                "location",
                "pool_length_meters",
            ]
        ].copy()

        display_df.columns = [
            "Member",
            "Date",
            "Distance (m)",
            "Time (s)",
            "Speed (m/s)",
            "Location",
            "Pool Length (m)",
        ]

        # Round numeric columns
        numeric_cols = ["Speed (m/s)"]
        for col in numeric_cols:
            display_df[col] = display_df[col].round(2)

        # Configure column display
        column_config = {
            "Member": st.column_config.TextColumn("Member", width="medium"),
            "Date": st.column_config.DateColumn("Date", width="medium"),
            "Distance (m)": st.column_config.NumberColumn(
                "Distance (m)", width="small"
            ),
            "Time (s)": st.column_config.NumberColumn("Time (s)", width="small"),
            "Speed (m/s)": st.column_config.NumberColumn(
                "Speed (m/s)", width="small", format="%.2f"
            ),
            "Location": st.column_config.TextColumn("Location", width="large"),
            "Pool Length (m)": st.column_config.NumberColumn(
                "Pool Length (m)", width="small"
            ),
        }

        st.dataframe(
            display_df,
            column_config=column_config,
            hide_index=True,
            width="stretch",
            height=400,
        )

        # Additional actions
        st.divider()

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button(
                ":material/refresh: Refresh Data",
                help="Reload indoor trials data from database",
            ):
                st.cache_data.clear()
                st.rerun()

        with col2:
            st.button(
                ":material/download: Export CSV",
                disabled=True,
                help="Export functionality coming soon",
            )

        with col3:
            st.caption(
                ":material/lightbulb: Use filters to focus on specific members, dates, or pool lengths"
            )

    except Exception as e:
        logger.error(f"Indoor trials page error: {e}")
        show_error_fallback()
