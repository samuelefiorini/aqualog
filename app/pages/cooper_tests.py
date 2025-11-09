"""
Cooper Tests page for Aqualog application.
Displays Cooper test data and visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, time
from loguru import logger

from db.queries import get_all_cooper_tests, get_all_members


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_cooper_tests_data():
    """Load Cooper tests data with caching for optimal performance."""
    try:
        tests = get_all_cooper_tests()
        members = get_all_members()
        logger.info(
            f"Successfully loaded {len(tests)} Cooper tests and {len(members)} members"
        )
        return tests, members
    except Exception as e:
        logger.error(f"Failed to load Cooper tests data: {e}")
        raise


def time_to_seconds(time_obj):
    """Convert time object to total seconds."""
    if not time_obj:
        return 0
    return (
        time_obj.hour * 3600
        + time_obj.minute * 60
        + time_obj.second
        + time_obj.microsecond / 1_000_000
    )


def calculate_distance_per_cycle(diving_time_seconds, pool_length):
    """Calculate estimated distance per diving cycle."""
    # Rough estimation: assume swimmer covers pool length multiple times during dive
    # This is a simplified calculation - in reality it would depend on swimming speed
    if diving_time_seconds <= 0:
        return 0

    # Assume average swimming speed of ~1.5 m/s during diving phase
    estimated_speed = 1.5  # meters per second
    return diving_time_seconds * estimated_speed


def process_cooper_test_data(tests, members):
    """Process Cooper test data for visualization."""
    if not tests:
        return pd.DataFrame()

    # Create member lookup
    member_lookup = {m.id: f"{m.name} {m.surname}" for m in members}

    processed_data = []

    for test in tests:
        member_name = member_lookup.get(test.member_id, f"Member {test.member_id}")

        # Calculate metrics for each cycle
        diving_times = test.diving_times or []
        surface_times = test.surface_times or []

        total_diving_seconds = sum(time_to_seconds(t) for t in diving_times)
        total_surface_seconds = sum(time_to_seconds(t) for t in surface_times)
        total_cycles = min(len(diving_times), len(surface_times))

        # Calculate average distance (estimation)
        avg_distance_per_cycle = 0
        if total_cycles > 0:
            avg_diving_time = total_diving_seconds / total_cycles
            avg_distance_per_cycle = calculate_distance_per_cycle(
                avg_diving_time, test.pool_length_meters
            )

        processed_data.append(
            {
                "test_id": test.id,
                "member_id": test.member_id,
                "member_name": member_name,
                "test_date": test.test_date,
                "total_diving_seconds": total_diving_seconds,
                "total_surface_seconds": total_surface_seconds,
                "total_cycles": total_cycles,
                "avg_diving_time": total_diving_seconds / total_cycles
                if total_cycles > 0
                else 0,
                "avg_surface_time": total_surface_seconds / total_cycles
                if total_cycles > 0
                else 0,
                "avg_distance_per_cycle": avg_distance_per_cycle,
                "pool_length": test.pool_length_meters,
                "diving_times": diving_times,
                "surface_times": surface_times,
            }
        )

    return pd.DataFrame(processed_data)


def create_performance_trends_chart(df):
    """Create performance trends over time chart."""
    if df.empty:
        return None

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Average Diving Time Over Time",
            "Average Surface Time Over Time",
            "Total Cycles Over Time",
            "Estimated Distance per Cycle",
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
        ],
    )

    # Group by member for different colored lines
    for member_name in df["member_name"].unique():
        member_data = df[df["member_name"] == member_name].sort_values("test_date")

        # Average diving time
        fig.add_trace(
            go.Scatter(
                x=member_data["test_date"],
                y=member_data["avg_diving_time"],
                mode="lines+markers",
                name=f"{member_name} - Diving",
                line=dict(width=2),
                showlegend=True,
            ),
            row=1,
            col=1,
        )

        # Average surface time
        fig.add_trace(
            go.Scatter(
                x=member_data["test_date"],
                y=member_data["avg_surface_time"],
                mode="lines+markers",
                name=f"{member_name} - Surface",
                line=dict(width=2),
                showlegend=False,
            ),
            row=1,
            col=2,
        )

        # Total cycles
        fig.add_trace(
            go.Scatter(
                x=member_data["test_date"],
                y=member_data["total_cycles"],
                mode="lines+markers",
                name=f"{member_name} - Cycles",
                line=dict(width=2),
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        # Estimated distance
        fig.add_trace(
            go.Scatter(
                x=member_data["test_date"],
                y=member_data["avg_distance_per_cycle"],
                mode="lines+markers",
                name=f"{member_name} - Distance",
                line=dict(width=2),
                showlegend=False,
            ),
            row=2,
            col=2,
        )

    # Update layout
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=2)
    fig.update_yaxes(title_text="Seconds", row=1, col=1)
    fig.update_yaxes(title_text="Seconds", row=1, col=2)
    fig.update_yaxes(title_text="Number of Cycles", row=2, col=1)
    fig.update_yaxes(title_text="Meters", row=2, col=2)

    fig.update_layout(
        height=700,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
        margin=dict(b=100),
    )

    return fig


def create_parallel_coordinates_chart(df, time_type="diving"):
    """Create parallel coordinates chart showing cycle times across test dates."""
    if df.empty:
        return None

    try:
        # Filter to single member data for parallel coordinates
        if len(df["member_name"].unique()) > 1:
            # If multiple members, take the first one or return None
            return None

        member_data = df.sort_values("test_date")

        if len(member_data) < 2:
            # Need at least 2 tests for parallel coordinates
            return None

        # Prepare data for parallel coordinates
        parallel_data = []
        test_dates = []

        # Get the maximum number of cycles across all tests
        max_cycles = 0
        for _, test in member_data.iterrows():
            if time_type == "diving":
                times = test["diving_times"]
            else:
                times = test["surface_times"]

            if times and len(times) > max_cycles:
                max_cycles = len(times)

        if max_cycles == 0:
            return None

        # Build parallel coordinates data
        for cycle_idx in range(max_cycles):
            cycle_data = {"cycle": f"Cycle {cycle_idx + 1}"}

            for _, test in member_data.iterrows():
                test_date_str = test["test_date"].strftime("%Y-%m-%d")

                if time_type == "diving":
                    times = test["diving_times"]
                else:
                    times = test["surface_times"]

                if times and cycle_idx < len(times):
                    cycle_data[test_date_str] = time_to_seconds(times[cycle_idx])
                else:
                    cycle_data[test_date_str] = None

            parallel_data.append(cycle_data)

        # Convert to DataFrame
        parallel_df = pd.DataFrame(parallel_data)

        # Get test date columns (exclude 'cycle' column)
        date_columns = [col for col in parallel_df.columns if col != "cycle"]

        if len(date_columns) < 2:
            return None

        # Create parallel coordinates plot
        fig = go.Figure()

        # Use continuous colormap for ordered cycles
        import plotly.colors as pc

        # Generate colors from a continuous colormap (viridis is good for ordered data)
        num_cycles = len(parallel_df)
        if num_cycles > 1:
            # Create color scale from early cycles (purple/blue) to late cycles (yellow/green)
            colorscale_values = [i / (num_cycles - 1) for i in range(num_cycles)]
            colors = [
                pc.sample_colorscale("viridis", val)[0] for val in colorscale_values
            ]
        else:
            colors = ["#440154"]  # Single color if only one cycle

        # Add a line for each cycle
        for idx, (_, row) in enumerate(parallel_df.iterrows()):
            y_values = []
            x_positions = list(range(len(date_columns)))

            for col in date_columns:
                y_values.append(row[col])

            # Only plot if we have at least 2 non-null values
            non_null_count = sum(1 for v in y_values if v is not None)
            if non_null_count >= 2:
                fig.add_trace(
                    go.Scatter(
                        x=x_positions,
                        y=y_values,
                        mode="lines+markers",
                        name=row["cycle"],
                        line=dict(width=2, color=colors[idx]),
                        marker=dict(size=8, color=colors[idx]),
                        connectgaps=False,  # Don't connect across missing data
                    )
                )

        # Update layout
        time_label = "Diving Time" if time_type == "diving" else "Surface Time"

        fig.update_layout(
            title=f"Cycle-by-Cycle {time_label} Progression Across Tests",
            xaxis=dict(
                title="Test Date",
                tickmode="array",
                tickvals=list(range(len(date_columns))),
                ticktext=date_columns,
                tickangle=45,
            ),
            yaxis=dict(title=f"{time_label} (seconds)"),
            height=500,
            showlegend=True,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
            margin=dict(r=150),  # Make room for legend
        )

        return fig

    except Exception as e:
        logger.error(f"Error creating parallel coordinates chart: {e}")
        return None


def create_diving_vs_surface_chart(df):
    """Create diving time vs surface time relationship chart."""
    if df.empty:
        return None

    fig = px.scatter(
        df,
        x="avg_diving_time",
        y="avg_surface_time",
        color="member_name",
        size="total_cycles",
        hover_data=["test_date", "total_cycles", "pool_length"],
        labels={
            "avg_diving_time": "Average Diving Time (seconds)",
            "avg_surface_time": "Average Surface Time (seconds)",
            "member_name": "Member",
        },
    )

    # Calculate linear regression statistics for all data
    import numpy as np
    from scipy import stats
    import plotly.graph_objects as go

    x = df["avg_diving_time"].values
    y = df["avg_surface_time"].values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # Add regression line for all data
    x_range = np.array([x.min(), x.max()])
    y_pred = slope * x_range + intercept

    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_pred,
            mode="lines",
            name="Linear Regression (All Athletes)",
            line=dict(color="black", width=2, dash="dash"),
            showlegend=True,
        )
    )

    # Add annotation with regression info
    fig.add_annotation(
        text=f"Linear Regression<br>Slope: {slope:.2f}<br>R²: {r_value**2:.3f}",
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
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
        margin=dict(b=100),
    )
    return fig


def create_cycle_patterns_chart(test_data):
    """Create chart showing dive/surface patterns within a single test session."""
    try:
        # Handle both dictionary and pandas Series
        if hasattr(test_data, "get"):
            # Dictionary-like access
            diving_times = test_data.get("diving_times")
            surface_times = test_data.get("surface_times")
            member_name = test_data.get("member_name", "Unknown")
            test_date = test_data.get("test_date", "Unknown")
        else:
            # Pandas Series access
            diving_times = (
                test_data["diving_times"] if "diving_times" in test_data else None
            )
            surface_times = (
                test_data["surface_times"] if "surface_times" in test_data else None
            )
            member_name = (
                test_data["member_name"] if "member_name" in test_data else "Unknown"
            )
            test_date = (
                test_data["test_date"] if "test_date" in test_data else "Unknown"
            )

        if not diving_times or not surface_times:
            return None

        diving_times_seconds = [time_to_seconds(t) for t in diving_times]
        surface_times_seconds = [time_to_seconds(t) for t in surface_times]

        cycles = list(
            range(1, min(len(diving_times_seconds), len(surface_times_seconds)) + 1)
        )

        if not cycles:
            return None

        fig = go.Figure()

        # Diving times
        fig.add_trace(
            go.Scatter(
                x=cycles,
                y=diving_times_seconds[: len(cycles)],
                mode="lines+markers",
                name="Diving Time",
                line=dict(color="blue", width=3),
                marker=dict(size=8),
            )
        )

        # Surface times
        fig.add_trace(
            go.Scatter(
                x=cycles,
                y=surface_times_seconds[: len(cycles)],
                mode="lines+markers",
                name="Surface Time",
                line=dict(color="red", width=3),
                marker=dict(size=8),
            )
        )

        fig.update_layout(
            title=f"Dive/Surface Pattern - {member_name} ({test_date})",
            xaxis_title="Cycle Number",
            yaxis_title="Time (seconds)",
            height=400,
            showlegend=True,
        )

        return fig

    except Exception as e:
        logger.error(f"Error creating cycle patterns chart: {e}")
        return None


def show_cooper_tests_statistics(df):
    """Display Cooper tests statistics."""
    if df.empty:
        return

    st.subheader(":material/analytics: Cooper Tests Statistics")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Tests", len(df))

    with col2:
        unique_members = df["member_name"].nunique()
        st.metric("Active Members", unique_members)

    with col3:
        median_cycles = df["total_cycles"].median()
        st.metric("Median Cycles per Test", f"{median_cycles:.0f}")

    with col4:
        median_diving_time = df["avg_diving_time"].median()
        st.metric("Median Diving Time", f"{median_diving_time:.1f}s")

    with col5:
        median_surface_time = df["avg_surface_time"].median()
        st.metric("Median Surface Time", f"{median_surface_time:.1f}s")


def show_empty_state():
    """Display empty state when no Cooper tests are found."""
    st.info(":material/inbox: No Cooper tests found in the database")

    st.markdown("""
    **Possible reasons:**
    - No Cooper tests have been recorded yet
    - Database connection issues
    - Data has not been populated
    
    **What you can do:**
    - Contact your administrator to add Cooper test data
    - Check if the database is properly initialized
    - Try refreshing the page
    """)


def show_error_fallback():
    """Display fallback content when data loading fails."""
    st.error("⚠️ Unable to load Cooper tests data")

    st.markdown("""
    **Possible causes:**
    - Database connection issues
    - Missing or corrupted Cooper test data
    - System maintenance in progress
    
    **What you can do:**
    - Try refreshing the page
    - Check your internet connection
    - Contact your system administrator if the problem persists
    """)


def show_cooper_tests_page():
    """Display the Cooper tests analysis page."""
    st.title(":material/timer: Cooper Tests Analysis")
    st.divider()

    try:
        # Load data with caching
        tests, members = load_cooper_tests_data()

        if not tests:
            show_empty_state()
            return

        # Process data for visualization
        df = process_cooper_test_data(tests, members)

        if df.empty:
            show_empty_state()
            return

        # Show statistics
        show_cooper_tests_statistics(df)

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
            min_date = df["test_date"].min()
            max_date = df["test_date"].max()

            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help="Filter tests by date range",
            )

        with col3:
            # Pool length filter
            pool_lengths = sorted(df["pool_length"].unique())
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
                (filtered_df["test_date"] >= start_date)
                & (filtered_df["test_date"] <= end_date)
            ]

        if selected_pool_length != "All":
            pool_length_value = int(selected_pool_length.replace("m", ""))
            filtered_df = filtered_df[filtered_df["pool_length"] == pool_length_value]

        if filtered_df.empty:
            st.warning("No Cooper tests match the selected filters.")
            return

        st.caption(f"Showing {len(filtered_df)} test(s) matching your filters")

        # Performance trends visualization
        st.divider()
        st.subheader(":material/bid_landscape: Performance Trends Over Time")

        trends_chart = create_performance_trends_chart(filtered_df)
        if trends_chart:
            st.plotly_chart(trends_chart)

        # Parallel coordinates chart for cycle-by-cycle analysis
        if selected_member != "All Members":
            st.markdown("### 🔗 Cycle-by-Cycle Performance Progression")

            # Time type selector
            time_type = st.selectbox(
                "Select Time Type",
                options=["diving", "surface"],
                format_func=lambda x: "Diving Time"
                if x == "diving"
                else "Surface Time",
                help="Choose whether to display diving times or surface times across test dates",
            )

            member_data = filtered_df[filtered_df["member_name"] == selected_member]

            # Show parallel coordinates chart
            parallel_chart = create_parallel_coordinates_chart(member_data, time_type)

            if parallel_chart:
                st.plotly_chart(parallel_chart)
                st.caption(
                    f"Each line represents a cycle number, showing how {time_type} times change across test dates. "
                    "This helps identify which cycles improve or decline over time."
                )
            else:
                st.info(
                    "Parallel coordinates chart requires at least 2 test sessions for the selected member."
                )

            # Show improvement KPIs below the chart if there are at least 2 tests
            if len(member_data) >= 2:
                st.markdown(
                    "#### :material/bid_landscape: Performance Improvement (Last Two Tests)"
                )

                # Sort by test date to get the most recent tests
                member_data_sorted = member_data.sort_values("test_date")
                latest_test = member_data_sorted.iloc[-1]
                previous_test = member_data_sorted.iloc[-2]

                # Calculate median times for each test
                latest_diving_median = pd.Series(
                    [time_to_seconds(t) for t in latest_test["diving_times"]]
                ).median()
                previous_diving_median = pd.Series(
                    [time_to_seconds(t) for t in previous_test["diving_times"]]
                ).median()

                latest_surface_median = pd.Series(
                    [time_to_seconds(t) for t in latest_test["surface_times"]]
                ).median()
                previous_surface_median = pd.Series(
                    [time_to_seconds(t) for t in previous_test["surface_times"]]
                ).median()

                # Calculate deltas
                diving_delta = latest_diving_median - previous_diving_median
                surface_delta = latest_surface_median - previous_surface_median

                # Display improvement metrics
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        label=":material/head_mounted_device: Median Diving Time",
                        value=f"{latest_diving_median:.1f}s",
                        delta=f"{diving_delta:+.1f}s",
                        delta_color="inverse",  # Lower diving time is better, so inverse colors
                        help="Median diving time in the most recent test vs. previous test. Lower is better.",
                    )

                with col2:
                    st.metric(
                        label=":material/pulmonology: Median Surface Time",
                        value=f"{latest_surface_median:.1f}s",
                        delta=f"{surface_delta:+.1f}s",
                        delta_color="inverse",  # Lower surface time is better (faster recovery)
                        help="Median surface time in the most recent test vs. previous test. Lower indicates better recovery.",
                    )

                # Add interpretation
                if abs(diving_delta) < 1 and abs(surface_delta) < 1:
                    st.info(
                        ":material/lightbulb: Performance is stable - minimal changes between tests."
                    )
                elif diving_delta < -1 or surface_delta < -1:
                    st.success(
                        ":material/celebration: Great improvement! Times have decreased, indicating better performance."
                    )
                elif diving_delta > 1 or surface_delta > 1:
                    st.warning(
                        ":material/warning: Performance may have declined. Consider reviewing training approach."
                    )

        # Diving vs Surface time relationship
        st.divider()
        st.subheader(":material/refresh: Diving vs Surface Time Relationship")

        relationship_chart = create_diving_vs_surface_chart(filtered_df)
        if relationship_chart:
            st.plotly_chart(relationship_chart)

        # Individual test session analysis
        if selected_member != "All Members":
            st.divider()
            st.subheader(":material/target: Individual Test Session Analysis")

            member_tests = filtered_df[filtered_df["member_name"] == selected_member]

            if not member_tests.empty:
                # Select specific test session
                test_options = []
                for _, test in member_tests.iterrows():
                    test_options.append(
                        f"{test['test_date']} - {test['total_cycles']} cycles"
                    )

                selected_test_idx = st.selectbox(
                    "Select Test Session",
                    options=range(len(test_options)),
                    format_func=lambda x: test_options[x],
                    help="Choose a specific test session to analyze cycle patterns",
                )

                selected_test_data = member_tests.iloc[selected_test_idx]

                # Show cycle patterns
                cycle_chart = create_cycle_patterns_chart(selected_test_data)
                if cycle_chart:
                    st.plotly_chart(cycle_chart)

                # Show detailed metrics for selected test
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Total Diving Time",
                        f"{selected_test_data['total_diving_seconds']:.1f}s",
                    )
                    st.metric(
                        "Average Diving Time",
                        f"{selected_test_data['avg_diving_time']:.1f}s",
                    )

                with col2:
                    st.metric(
                        "Total Surface Time",
                        f"{selected_test_data['total_surface_seconds']:.1f}s",
                    )
                    st.metric(
                        "Average Surface Time",
                        f"{selected_test_data['avg_surface_time']:.1f}s",
                    )

                with col3:
                    st.metric("Total Cycles", int(selected_test_data["total_cycles"]))
                    st.metric("Pool Length", f"{selected_test_data['pool_length']}m")

        # Data table
        st.divider()
        st.subheader(":material/data_exploration: Cooper Tests Data")

        # Prepare display dataframe
        display_df = filtered_df[
            [
                "member_name",
                "test_date",
                "total_cycles",
                "avg_diving_time",
                "avg_surface_time",
                "total_diving_seconds",
                "total_surface_seconds",
                "pool_length",
            ]
        ].copy()

        display_df.columns = [
            "Member",
            "Date",
            "Cycles",
            "Avg Diving (s)",
            "Avg Surface (s)",
            "Total Diving (s)",
            "Total Surface (s)",
            "Pool Length (m)",
        ]

        # Round numeric columns
        numeric_cols = [
            "Avg Diving (s)",
            "Avg Surface (s)",
            "Total Diving (s)",
            "Total Surface (s)",
        ]
        for col in numeric_cols:
            display_df[col] = display_df[col].round(1)

        st.dataframe(display_df, hide_index=True, height=300)

        # Additional actions
        st.divider()

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button(
                ":material/refresh: Refresh Data",
                help="Reload Cooper tests data from database",
            ):
                st.cache_data.clear()
                st.rerun()

        with col2:
            st.button(
                ":material/download: Export Data",
                disabled=True,
                help="Export functionality coming soon",
            )

        with col3:
            st.caption(
                ":material/lightbulb: Use filters to focus on specific members or time periods"
            )

    except Exception as e:
        logger.error(f"Cooper tests page error: {e}")
        show_error_fallback()
