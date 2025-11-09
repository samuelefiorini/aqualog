"""
Database-backed authentication system for Aqualog.
Provides encrypted credential storage in DuckDB with role-based access control.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
from cryptography.fernet import Fernet
from loguru import logger
import base64
import os

from db import get_db_connection
from db.models import DashboardUser
from app.utils.config import get_config


class DatabaseAuthManager:
    """Database-backed authentication manager with encryption."""

    def __init__(self):
        """Initialize the database authentication manager."""
        self.db = get_db_connection()
        self.config = get_config()
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)

        # Initialize with default admin user if no users exist
        self._ensure_default_admin()

    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for password storage."""
        key_file = ".streamlit/encryption.key"

        # Try to get key from environment first
        env_key = os.getenv("AQUALOG_ENCRYPTION_KEY")
        if env_key:
            try:
                return base64.urlsafe_b64decode(env_key.encode())
            except Exception as e:
                logger.warning(f"Invalid encryption key in environment: {e}")

        # Try to load from file
        try:
            with open(key_file, "rb") as f:
                return f.read()
        except FileNotFoundError:
            # Generate new key
            key = Fernet.generate_key()

            # Save key to file
            try:
                os.makedirs(os.path.dirname(key_file), exist_ok=True)
                with open(key_file, "wb") as f:
                    f.write(key)
                logger.info(f"Generated new encryption key: {key_file}")
            except Exception as e:
                logger.error(f"Failed to save encryption key: {e}")

            return key

    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256."""
        return hashlib.sha256((password + salt).encode()).hexdigest()

    def _encrypt_password_hash(self, password_hash: str) -> str:
        """Encrypt password hash for database storage."""
        return self.cipher.encrypt(password_hash.encode()).decode()

    def _decrypt_password_hash(self, encrypted_hash: str) -> str:
        """Decrypt password hash from database."""
        return self.cipher.decrypt(encrypted_hash.encode()).decode()

    def _ensure_default_admin(self) -> None:
        """Ensure default admin user exists."""
        try:
            # Check if any users exist
            result = self.db.fetch_one("SELECT COUNT(*) FROM dashboard_users")
            if result and result[0] > 0:
                return

            # Create default admin user
            self.create_user(
                username="admin",
                password="aqualog2025",
                role="admin",
                full_name="System Administrator",
                email="admin@aqualog.local",
            )
            logger.info("Created default admin user (admin/aqualog2025)")

        except Exception as e:
            logger.error(f"Failed to create default admin user: {e}")

    def create_user(
        self,
        username: str,
        password: str,
        role: str = "user",
        full_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> int:
        """
        Create a new user with encrypted password.

        Args:
            username: Unique username
            password: Plain text password
            role: User role ('admin' or 'user')
            full_name: Optional full name
            email: Optional email address

        Returns:
            User ID of created user
        """
        if role not in ["admin", "user"]:
            raise ValueError("Role must be 'admin' or 'user'")

        # Generate salt and hash password
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        encrypted_hash = self._encrypt_password_hash(password_hash)

        # Get next ID
        max_id_result = self.db.fetch_one(
            "SELECT COALESCE(MAX(id), 0) + 1 FROM dashboard_users"
        )
        user_id = max_id_result[0]

        # Insert user
        query = """
        INSERT INTO dashboard_users (id, username, password_hash, salt, email, full_name, role, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        self.db.execute_query(
            query,
            (user_id, username, encrypted_hash, salt, email, full_name, role, True),
        )

        logger.info(f"Created user: {username} (role: {role})")
        return user_id

    def authenticate(self, username: str, password: str) -> Optional[DashboardUser]:
        """
        Authenticate user and return user object if successful.

        Args:
            username: Username to authenticate
            password: Plain text password

        Returns:
            DashboardUser object if authentication successful, None otherwise
        """
        try:
            # Get user from database
            query = """
            SELECT id, username, password_hash, salt, email, full_name, role, is_active,
                   created_at, last_login, login_attempts, locked_until
            FROM dashboard_users
            WHERE username = ? AND is_active = true
            """

            row = self.db.fetch_one(query, (username,))
            if not row:
                logger.warning(f"Authentication failed: user '{username}' not found")
                return None

            # Create user object
            user = DashboardUser(
                id=row[0],
                username=row[1],
                password_hash=row[2],
                salt=row[3],
                email=row[4],
                full_name=row[5],
                role=row[6],
                is_active=row[7],
                created_at=row[8],
                last_login=row[9],
                login_attempts=row[10],
                locked_until=row[11],
            )

            # Check if account is locked
            if user.is_locked:
                remaining_time = int(
                    (user.locked_until - datetime.now()).total_seconds() / 60
                )
                logger.warning(
                    f"Authentication failed: user '{username}' is locked for {remaining_time} minutes"
                )
                return None

            # Verify password
            decrypted_hash = self._decrypt_password_hash(user.password_hash)
            expected_hash = self._hash_password(password, user.salt)

            if decrypted_hash == expected_hash:
                # Successful authentication
                self._update_login_success(user.id)
                logger.info(f"User '{username}' authenticated successfully")
                return user
            else:
                # Failed authentication
                self._update_login_failure(user.id)
                logger.warning(
                    f"Authentication failed: invalid password for user '{username}'"
                )
                return None

        except Exception as e:
            logger.error(f"Authentication error for user '{username}': {e}")
            return None

    def _update_login_success(self, user_id: int) -> None:
        """Update user record after successful login."""
        query = """
        UPDATE dashboard_users 
        SET last_login = ?, login_attempts = 0, locked_until = NULL
        WHERE id = ?
        """
        self.db.execute_query(query, (datetime.now(), user_id))

    def _update_login_failure(self, user_id: int) -> None:
        """Update user record after failed login."""
        max_attempts = self.config.get_max_login_attempts()
        lockout_duration = self.config.get_lockout_duration()

        # Increment login attempts
        query = """
        UPDATE dashboard_users 
        SET login_attempts = login_attempts + 1
        WHERE id = ?
        """
        self.db.execute_query(query, (user_id,))

        # Check if user should be locked
        result = self.db.fetch_one(
            "SELECT login_attempts FROM dashboard_users WHERE id = ?", (user_id,)
        )
        if result and result[0] >= max_attempts:
            locked_until = datetime.now() + timedelta(minutes=lockout_duration)
            query = """
            UPDATE dashboard_users 
            SET locked_until = ?
            WHERE id = ?
            """
            self.db.execute_query(query, (locked_until, user_id))
            logger.warning(f"User ID {user_id} locked for {lockout_duration} minutes")

    def get_user_by_username(self, username: str) -> Optional[DashboardUser]:
        """Get user by username."""
        try:
            query = """
            SELECT id, username, password_hash, salt, email, full_name, role, is_active,
                   created_at, last_login, login_attempts, locked_until
            FROM dashboard_users
            WHERE username = ?
            """

            row = self.db.fetch_one(query, (username,))
            if not row:
                return None

            return DashboardUser(
                id=row[0],
                username=row[1],
                password_hash=row[2],
                salt=row[3],
                email=row[4],
                full_name=row[5],
                role=row[6],
                is_active=row[7],
                created_at=row[8],
                last_login=row[9],
                login_attempts=row[10],
                locked_until=row[11],
            )

        except Exception as e:
            logger.error(f"Error getting user '{username}': {e}")
            return None

    def get_all_users(self) -> List[DashboardUser]:
        """Get all users."""
        try:
            query = """
            SELECT id, username, password_hash, salt, email, full_name, role, is_active,
                   created_at, last_login, login_attempts, locked_until
            FROM dashboard_users
            ORDER BY username
            """

            rows = self.db.fetch_all(query)
            users = []

            for row in rows:
                user = DashboardUser(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    salt=row[3],
                    email=row[4],
                    full_name=row[5],
                    role=row[6],
                    is_active=row[7],
                    created_at=row[8],
                    last_login=row[9],
                    login_attempts=row[10],
                    locked_until=row[11],
                )
                users.append(user)

            return users

        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    def update_user_role(self, username: str, role: str) -> bool:
        """Update user role."""
        if role not in ["admin", "user"]:
            raise ValueError("Role must be 'admin' or 'user'")

        try:
            query = "UPDATE dashboard_users SET role = ? WHERE username = ?"
            self.db.execute_query(query, (role, username))
            logger.info(f"Updated user '{username}' role to '{role}'")
            return True
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            return False

    def deactivate_user(self, username: str) -> bool:
        """Deactivate user account."""
        try:
            query = "UPDATE dashboard_users SET is_active = false WHERE username = ?"
            self.db.execute_query(query, (username,))
            logger.info(f"Deactivated user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            return False

    def activate_user(self, username: str) -> bool:
        """Activate user account."""
        try:
            query = "UPDATE dashboard_users SET is_active = true WHERE username = ?"
            self.db.execute_query(query, (username,))
            logger.info(f"Activated user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error activating user: {e}")
            return False

    def change_password(self, username: str, new_password: str) -> bool:
        """Change user password."""
        try:
            # Generate new salt and hash
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(new_password, salt)
            encrypted_hash = self._encrypt_password_hash(password_hash)

            query = """
            UPDATE dashboard_users 
            SET password_hash = ?, salt = ?, login_attempts = 0, locked_until = NULL
            WHERE username = ?
            """
            self.db.execute_query(query, (encrypted_hash, salt, username))
            logger.info(f"Changed password for user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False

    def unlock_user(self, username: str) -> bool:
        """Unlock user account."""
        try:
            query = """
            UPDATE dashboard_users 
            SET login_attempts = 0, locked_until = NULL
            WHERE username = ?
            """
            self.db.execute_query(query, (username,))
            logger.info(f"Unlocked user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error unlocking user: {e}")
            return False

    def delete_user(self, username: str) -> bool:
        """Delete user account permanently."""
        if username == "admin":
            raise ValueError("Cannot delete the default admin user")

        try:
            query = "DELETE FROM dashboard_users WHERE username = ?"
            self.db.execute_query(query, (username,))
            logger.info(f"Deleted user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False


# Global database auth manager instance
_db_auth_manager = None


def get_db_auth_manager() -> DatabaseAuthManager:
    """Get the global database authentication manager instance."""
    global _db_auth_manager
    if _db_auth_manager is None:
        _db_auth_manager = DatabaseAuthManager()
    return _db_auth_manager
