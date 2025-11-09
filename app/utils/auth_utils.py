"""
Authentication utilities for Streamlit pages.
Provides decorators and helper functions for page protection.
"""

import streamlit as st
from functools import wraps
from typing import Callable, Any
from app.utils.auth import get_auth_manager


def require_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication for a Streamlit page function.

    Usage:
        @require_auth
        def my_page():
            st.write("This page requires authentication")
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        auth_manager = get_auth_manager()

        if auth_manager.require_authentication():
            return func(*args, **kwargs)
        else:
            # Authentication form is shown, stop execution
            st.stop()

    return wrapper


def require_admin(func: Callable) -> Callable:
    """
    Decorator to require admin privileges for a Streamlit page function.

    Usage:
        @require_admin
        def admin_page():
            st.write("This page requires admin privileges")
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        auth_manager = get_auth_manager()

        if auth_manager.require_admin():
            return func(*args, **kwargs)
        else:
            # Access denied or login form is shown, stop execution
            st.stop()

    return wrapper


def require_write_access(func: Callable) -> Callable:
    """
    Decorator to require write access for a Streamlit page function.

    Usage:
        @require_write_access
        def edit_page():
            st.write("This page requires write access")
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        auth_manager = get_auth_manager()

        if auth_manager.require_write_access():
            return func(*args, **kwargs)
        else:
            # Access denied or login form is shown, stop execution
            st.stop()

    return wrapper


def check_auth() -> bool:
    """
    Check if user is authenticated.
    Returns True if authenticated, False otherwise.
    """
    auth_manager = get_auth_manager()
    return auth_manager.is_authenticated()


def get_user() -> str:
    """
    Get current authenticated user.
    Returns username if authenticated, None otherwise.
    """
    auth_manager = get_auth_manager()
    return auth_manager.get_current_username()


def is_admin() -> bool:
    """
    Check if current user has admin privileges.
    Returns True if admin, False otherwise.
    """
    auth_manager = get_auth_manager()
    return auth_manager.is_admin()


def can_write() -> bool:
    """
    Check if current user has write permissions.
    Returns True if write access, False otherwise.
    """
    auth_manager = get_auth_manager()
    return auth_manager.can_write()


def can_read() -> bool:
    """
    Check if current user has read permissions.
    Returns True if read access, False otherwise.
    """
    auth_manager = get_auth_manager()
    return auth_manager.can_read()


def show_auth_sidebar() -> None:
    """
    Show authentication status in sidebar.
    """
    auth_manager = get_auth_manager()

    if auth_manager.is_authenticated():
        with st.sidebar:
            st.divider()
            st.subheader("🔐 Authentication")
            st.success(f"Logged in as: **{auth_manager.get_current_user()}**")

            if st.button(":material/logout: Logout", key="sidebar_logout"):
                auth_manager.logout()
                st.rerun()


def show_auth_header() -> None:
    """
    Show authentication status in main area header.
    """
    auth_manager = get_auth_manager()

    if auth_manager.is_authenticated():
        col1, col2, col3 = st.columns([2, 1, 1])

        with col2:
            st.write(f":material/user:**{auth_manager.get_current_user()}**")

        with col3:
            if st.button(":material/logout: Logout", key="header_logout"):
                auth_manager.logout()
                st.rerun()


def protect_page(title: str = None, icon: str = ":material/pool:") -> bool:
    """
    Protect a page with authentication and set up basic layout.

    Args:
        title: Page title to display
        icon: Page icon

    Returns:
        True if authenticated and page should continue, False otherwise
    """
    auth_manager = get_auth_manager()

    # Check authentication
    if not auth_manager.require_authentication():
        return False

    # Set up page layout
    if title:
        st.title(f"{icon} {title}")

    # Show auth status in sidebar
    show_auth_sidebar()

    return True


class AuthenticatedPage:
    """
    Context manager for authenticated pages.

    Usage:
        with AuthenticatedPage("My Page Title"):
            st.write("Protected content here")
    """

    def __init__(self, title: str = None, icon: str = ":material/pool:"):
        self.title = title
        self.icon = icon
        self.auth_manager = get_auth_manager()

    def __enter__(self):
        if not self.auth_manager.require_authentication():
            st.stop()

        if self.title:
            st.title(f"{self.icon} {self.title}")

        show_auth_sidebar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
