"""
Members page for Aqualog application.
Displays the member registry with read-only access.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from loguru import logger

from db.queries import get_all_members


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_members_data():
    """Load members data with caching for optimal performance."""
    try:
        members = get_all_members()
        logger.info(f"Successfully loaded {len(members)} members for registry page")
        return members
    except Exception as e:
        logger.error(f"Failed to load members data: {e}")
        raise


def format_members_dataframe(members):
    """Convert members list to formatted pandas DataFrame."""
    if not members:
        return pd.DataFrame()

    # Convert to list of dictionaries for DataFrame
    members_data = []
    for member in members:
        members_data.append(
            {
                "ID": member.id,
                "Name": member.name,
                "Surname": member.surname,
                "Date of Birth": member.date_of_birth.strftime("%Y-%m-%d")
                if member.date_of_birth
                else "N/A",
                "Age": calculate_age(member.date_of_birth)
                if member.date_of_birth
                else "N/A",
                "Contact Info": member.contact_info or "N/A",
                "Membership Start": member.membership_start_date.strftime("%Y-%m-%d")
                if member.membership_start_date
                else "N/A",
                "Member Since": calculate_membership_duration(
                    member.membership_start_date
                )
                if member.membership_start_date
                else "N/A",
                "Created": member.created_at.strftime("%Y-%m-%d %H:%M")
                if member.created_at
                else "N/A",
            }
        )

    return pd.DataFrame(members_data)


def calculate_age(birth_date):
    """Calculate age from birth date."""
    if not birth_date:
        return "N/A"

    today = datetime.now().date()
    age = today.year - birth_date.year

    # Adjust if birthday hasn't occurred this year
    if today < birth_date.replace(year=today.year):
        age -= 1

    return age


def calculate_membership_duration(membership_date):
    """Calculate membership duration in years and months."""
    if not membership_date:
        return "N/A"

    today = datetime.now().date()
    years = today.year - membership_date.year
    months = today.month - membership_date.month

    # Adjust for negative months
    if months < 0:
        years -= 1
        months += 12

    if years > 0:
        return f"{years}y {months}m"
    else:
        return f"{months}m"


def show_members_statistics(members):
    """Display member statistics."""
    if not members:
        return

    st.subheader(":material/analytics: Registry Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Members", len(members))

    with col2:
        # Calculate average age
        ages = [calculate_age(m.date_of_birth) for m in members if m.date_of_birth]
        valid_ages = [age for age in ages if isinstance(age, int)]
        avg_age = sum(valid_ages) / len(valid_ages) if valid_ages else 0
        st.metric("Average Age", f"{avg_age:.1f}" if avg_age > 0 else "N/A")

    with col3:
        # Count members with contact info
        with_contact = sum(1 for m in members if m.contact_info)
        st.metric("With Contact Info", f"{with_contact}/{len(members)}")

    with col4:
        # Find newest member
        if members:
            newest = max(
                members, key=lambda m: m.membership_start_date or datetime.min.date()
            )
            newest_duration = calculate_membership_duration(
                newest.membership_start_date
            )
            st.metric("Newest Member", newest_duration)


def show_empty_state():
    """Display empty state when no members are found."""
    st.info(":material/inbox: No members found in the registry")

    st.markdown("""
    **Possible reasons:**
    - The database is empty
    - No members have been added yet
    - Database connection issues
    
    **What you can do:**
    - Contact your administrator to add members
    - Check if the database is properly initialized
    - Try refreshing the page
    """)


def show_error_fallback():
    """Display fallback content when data loading fails."""
    st.error("⚠️ Unable to load members registry")

    st.markdown("""
    **Possible causes:**
    - Database connection issues
    - Missing or corrupted member data
    - System maintenance in progress
    
    **What you can do:**
    - Try refreshing the page
    - Check your internet connection
    - Contact your system administrator if the problem persists
    """)


def show_members_page():
    """Display the members registry page."""
    st.title(":material/group: Members Registry")
    st.divider()

    try:
        # Load members data with caching
        members = load_members_data()

        if not members:
            show_empty_state()
            return

        # Show statistics
        show_members_statistics(members)

        st.divider()

        # Convert to DataFrame for display
        df = format_members_dataframe(members)

        if df.empty:
            show_empty_state()
            return

        # Search and filter controls
        st.subheader(":material/search: Member Search & Filter")

        col1, col2 = st.columns([2, 1])

        with col1:
            search_term = st.text_input(
                "Search members",
                placeholder="Search by name, surname, or contact info...",
                help="Enter any text to search across member names and contact information",
            )

        with col2:
            # Sort options
            sort_options = {
                "Surname (A-Z)": ("Surname", True),
                "Surname (Z-A)": ("Surname", False),
                "Name (A-Z)": ("Name", True),
                "Name (Z-A)": ("Name", False),
                "Age (Youngest)": ("Age", True),
                "Age (Oldest)": ("Age", False),
                "Membership (Newest)": ("Membership Start", False),
                "Membership (Oldest)": ("Membership Start", True),
            }

            sort_choice = st.selectbox(
                "Sort by", options=list(sort_options.keys()), index=0
            )

        # Apply search filter
        filtered_df = df.copy()

        if search_term:
            search_mask = (
                filtered_df["Name"].str.contains(search_term, case=False, na=False)
                | filtered_df["Surname"].str.contains(search_term, case=False, na=False)
                | filtered_df["Contact Info"].str.contains(
                    search_term, case=False, na=False
                )
            )
            filtered_df = filtered_df[search_mask]

        # Apply sorting
        sort_column, ascending = sort_options[sort_choice]
        if sort_column in filtered_df.columns:
            # Handle special sorting for Age column (convert N/A to 0 for sorting)
            if sort_column == "Age":
                filtered_df["Age_Sort"] = filtered_df["Age"].apply(
                    lambda x: 0 if x == "N/A" else x
                )
                filtered_df = filtered_df.sort_values("Age_Sort", ascending=ascending)
                filtered_df = filtered_df.drop("Age_Sort", axis=1)
            else:
                filtered_df = filtered_df.sort_values(sort_column, ascending=ascending)

        # Display results count
        if search_term:
            st.caption(f"Found {len(filtered_df)} member(s) matching '{search_term}'")
        else:
            st.caption(f"Showing all {len(filtered_df)} members")

        # Display the members table
        st.subheader(":material/data_exploration: Member Registry")

        if filtered_df.empty:
            st.info(f"No members found matching '{search_term}'")
        else:
            # Configure column display
            column_config = {
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Surname": st.column_config.TextColumn("Surname", width="medium"),
                "Date of Birth": st.column_config.DateColumn(
                    "Date of Birth", width="medium"
                ),
                "Age": st.column_config.NumberColumn("Age", width="small"),
                "Contact Info": st.column_config.TextColumn(
                    "Contact Info", width="large"
                ),
                "Membership Start": st.column_config.DateColumn(
                    "Membership Start", width="medium"
                ),
                "Member Since": st.column_config.TextColumn(
                    "Member Since", width="small"
                ),
                "Created": st.column_config.DatetimeColumn("Created", width="medium"),
            }

            # Display the dataframe with custom configuration
            st.dataframe(
                filtered_df,
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
                help="Reload member data from database",
            ):
                st.cache_data.clear()
                st.rerun()

        with col2:
            # Export functionality (placeholder for future implementation)
            st.button(
                ":material/download: Export CSV",
                disabled=True,
                help="Export functionality coming soon",
            )

        with col3:
            st.caption(
                ":material/lightbulb: Use the search box to quickly find specific members"
            )

    except Exception as e:
        logger.error(f"Members page error: {e}")
        show_error_fallback()
