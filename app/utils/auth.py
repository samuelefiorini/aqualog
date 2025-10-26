"""
Database-backed authentication module for Aqualog.
Provides authentication using encrypted credentials stored in DuckDB.
"""

import streamlit as st
import time
from typing import Optional
from loguru import logger
from app.auth.db_auth import get_db_auth_manager
from db.models import DashboardUser


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""

    pass


class AuthManager:
    """Manages authentication for the Aqualog application using database backend."""

    def __init__(self):
        """Initialize the authentication manager."""
        self.db_auth = get_db_auth_manager()

        # Initialize session state
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user" not in st.session_state:
            st.session_state.user = None
        if "username" not in st.session_state:
            st.session_state.username = None

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate user with username and password.

        Args:
            username: The username to authenticate
            password: The password to authenticate

        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            user = self.db_auth.authenticate(username, password)

            if user:
                # Successful authentication
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.username = user.username

                logger.info(
                    f"User '{username}' authenticated successfully (role: {user.role})"
                )
                return True
            else:
                # Failed authentication
                logger.warning(f"Failed login attempt for user '{username}'")
                return False

        except Exception as e:
            logger.error(f"Authentication error for user '{username}': {e}")
            return False

    def logout(self) -> None:
        """Log out the current user."""
        username = st.session_state.get("username", "Unknown")

        # Clear session state
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.username = None

        logger.info(f"User '{username}' logged out")

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return st.session_state.get("authenticated", False)

    def get_current_user(self) -> Optional[DashboardUser]:
        """Get the current authenticated user object."""
        if self.is_authenticated():
            return st.session_state.get("user")
        return None

    def get_current_username(self) -> Optional[str]:
        """Get the current authenticated username."""
        if self.is_authenticated():
            return st.session_state.get("username")
        return None

    def is_admin(self) -> bool:
        """Check if current user has admin privileges."""
        user = self.get_current_user()
        return user is not None and user.is_admin

    def can_write(self) -> bool:
        """Check if current user has write permissions."""
        user = self.get_current_user()
        return user is not None and user.can_write

    def can_read(self) -> bool:
        """Check if current user has read permissions."""
        user = self.get_current_user()
        return user is not None and user.can_read

    def require_authentication(self) -> bool:
        """
        Require authentication for the current page.
        Shows login form if not authenticated.

        Returns:
            bool: True if authenticated, False if login form is shown
        """
        if not self.is_authenticated():
            self.show_login_form()
            return False
        return True

    def require_admin(self) -> bool:
        """
        Require admin privileges for the current page.
        Shows access denied if not admin.

        Returns:
            bool: True if admin, False if access denied
        """
        if not self.require_authentication():
            return False

        if not self.is_admin():
            st.error("🚫 Access Denied: Administrator privileges required")
            st.info("Contact your administrator to access this page.")
            st.stop()

        return True

    def require_write_access(self) -> bool:
        """
        Require write permissions for the current operation.
        Shows access denied if no write access.

        Returns:
            bool: True if write access, False if access denied
        """
        if not self.require_authentication():
            return False

        if not self.can_write():
            st.error("🚫 Access Denied: Write permissions required")
            st.info(
                "You have read-only access. Contact your administrator for write permissions."
            )
            return False

        return True

    def show_login_form(self) -> None:
        """Display the login form."""
        st.title("🏊‍♂️ Aqualog - Login")
        st.markdown("---")

        # Login form
        with st.form("login_form"):
            st.subheader("Login to use Aqualog")

            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input(
                "Password", type="password", placeholder="Enter your password"
            )

            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                login_button = st.form_submit_button("🔑 Login")

            if login_button:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    if self.authenticate(username, password):
                        st.success(f"Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        # Information section
        st.markdown("---")

        # User roles information
        with st.expander("👥 User Roles"):
            st.info("""
            **Administrator:**
            - Full read and write access
            - Can view all pages and data
            - Can modify system settings
            
            **User:**
            - Read-only access
            - Can view data and reports
            - Cannot modify data
            """)

        # Footer
        st.markdown("---")
        st.caption("Aqualog - Freediving Society Management System")


# Global authentication manager instance
auth_manager = AuthManager()


def get_auth_manager() -> AuthManager:
    """Get the global authentication manager instance."""
    return auth_manager


def require_authentication() -> bool:
    """Convenience function to require authentication."""
    return auth_manager.require_authentication()


def require_admin() -> bool:
    """Convenience function to require admin privileges."""
    return auth_manager.require_admin()


def require_write_access() -> bool:
    """Convenience function to require write access."""
    return auth_manager.require_write_access()


def is_authenticated() -> bool:
    """Convenience function to check authentication status."""
    return auth_manager.is_authenticated()


def is_admin() -> bool:
    """Convenience function to check admin status."""
    return auth_manager.is_admin()


def can_write() -> bool:
    """Convenience function to check write permissions."""
    return auth_manager.can_write()


def can_read() -> bool:
    """Convenience function to check read permissions."""
    return auth_manager.can_read()


def get_current_user() -> Optional[DashboardUser]:
    """Convenience function to get current user."""
    return auth_manager.get_current_user()


def get_current_username() -> Optional[str]:
    """Convenience function to get current username."""
    return auth_manager.get_current_username()


def logout() -> None:
    """Convenience function to logout."""
    auth_manager.logout()
