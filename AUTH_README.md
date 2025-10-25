# Aqualog Authentication System

This document describes the database-backed authentication system implemented for the Aqualog freediving management application.

## Overview

The authentication system provides secure credential-based authentication using encrypted password storage in DuckDB. It includes:

- Database-backed user management with encrypted passwords
- Role-based access control (Admin/User)
- Session management with Streamlit session state
- Account lockout protection
- CLI-based user administration
- Page protection utilities with role checking

## Components

### Core Modules

1. **`auth.py`** - Main authentication manager (Streamlit integration)
2. **`db_auth.py`** - Database authentication backend with encryption
3. **`app_config.py`** - Configuration management
4. **`auth_utils.py`** - Utility functions and decorators
5. **`pages/login.py`** - Login page component

### Database Schema

- **`dashboard_users`** - User accounts with encrypted credentials
- **Encryption key** - Auto-generated and stored in `.streamlit/encryption.key`

### Configuration Files

- **`.streamlit/config.json`** - Application configuration
- **`.streamlit/encryption.key`** - Encryption key (auto-generated on first use)

## User Roles

### Administrator
- **Full access**: Read and write permissions
- **Can view**: All pages and data
- **Can modify**: System data and settings
- **CLI access**: User management commands

### User  
- **Read-only access**: View data and reports only
- **Cannot modify**: System data or settings
- **Limited pages**: Access to read-only pages only

## Default Credentials

**Username:** `admin`  
**Password:** `admin123`  
**Role:** Administrator

⚠️ **Important:** Change default credentials in production!

## Usage

### Basic Page Protection

```python
import streamlit as st
from app.utils.auth_utils import require_auth

@require_auth
def my_protected_page():
    st.title("Protected Content")
    st.write("This page requires authentication")

if __name__ == "__main__":
    my_protected_page()
```

### Admin-Only Pages

```python
from app.utils.auth_utils import require_admin

@require_admin
def admin_page():
    st.title("Admin Panel")
    st.write("This page requires admin privileges")
```

### Write-Protected Operations

```python
from app.utils.auth_utils import require_write_access

@require_write_access
def edit_data_page():
    st.title("Edit Data")
    st.write("This page requires write permissions")
```

### Role-Based Content

```python
from app.utils.auth_utils import is_admin, can_write

if is_admin():
    st.button("Admin Settings")

if can_write():
    st.button("Edit Data")
else:
    st.info("Read-only access")
```

### Using Context Manager

```python
from app.utils.auth_utils import AuthenticatedPage

with AuthenticatedPage("My Page Title"):
    st.write("Protected content here")
```

### Manual Authentication Check

```python
from app.utils.auth import require_authentication, get_current_user

if require_authentication():
    user = get_current_user()
    st.write(f"Welcome, {user.display_name}!")
    st.write(f"Role: {user.role}")
else:
    # Login form is automatically shown
    st.stop()
```

### Running the Application

```bash
# Start the main Streamlit application
streamlit run main.py

# Access login page directly
streamlit run app/pages/login.py
```

## User Management

### CLI Commands

Create a new user:
```bash
python scripts/cli.py create-user --username john --password secret123 --role user --name "John Doe" --email john@example.com
```

List all users:
```bash
python scripts/cli.py list-users
```

Change user password:
```bash
python scripts/cli.py change-password --username john --password newsecret123
```

Change user role:
```bash
python scripts/cli.py change-role --username john --role admin
```

Deactivate/activate user:
```bash
python scripts/cli.py deactivate-user --username john
python scripts/cli.py activate-user --username john
```

Unlock locked user:
```bash
python scripts/cli.py unlock-user --username john
```

Delete user:
```bash
python scripts/cli.py delete-user --username john
```

## Configuration

### Environment Variables

You can override configuration using environment variables:

- `AQUALOG_ENCRYPTION_KEY` - Base64-encoded encryption key
- `AQUALOG_SESSION_TIMEOUT` - Session timeout in minutes
- `AQUALOG_MAX_LOGIN_ATTEMPTS` - Maximum login attempts
- `AQUALOG_REQUIRE_AUTH` - Enable/disable authentication

### Configuration File

Edit `.streamlit/config.json` to customize settings:

```json
{
  "auth": {
    "session_timeout_minutes": 60,
    "max_login_attempts": 5,
    "lockout_duration_minutes": 15,
    "require_auth": true
  }
}
```

## Security Features

### Encryption

- **Password Storage**: Passwords are hashed with SHA-256 and unique salts
- **Database Encryption**: Password hashes are encrypted using Fernet (AES-128)
- **Key Management**: Encryption keys stored securely in `.streamlit/encryption.key`
- **Auto-Generation**: Encryption key is automatically created on first use
- **No Plaintext**: No plaintext passwords stored anywhere

#### Encryption Key Creation

The encryption key is automatically generated when the authentication system is first used:

1. **Environment Check**: Looks for `AQUALOG_ENCRYPTION_KEY` environment variable
2. **File Check**: Tries to load existing key from `.streamlit/encryption.key`
3. **Auto-Generate**: If not found, generates new Fernet key automatically
4. **Secure Storage**: Saves key to `.streamlit/encryption.key` with proper permissions
5. **Ready to Use**: System is ready for secure password storage

**Triggers for key creation:**
- First CLI user management command
- First login attempt via Streamlit
- Any database authentication operation

### Account Lockout

- Accounts are locked after 5 failed login attempts (configurable)
- Lockout duration is 15 minutes (configurable)
- Lockout status is displayed to users
- Admins can unlock accounts via CLI

### Session Management

- Sessions timeout after 60 minutes of inactivity (configurable)
- Session state is managed securely with Streamlit
- Logout clears all session data
- User object stored in session for role checking

### Role-Based Access Control

- **Admin Role**: Full read/write access to all features
- **User Role**: Read-only access to data and reports
- **Page Protection**: Decorators enforce role requirements
- **Operation Protection**: Write operations require admin role

## File Structure

```
main.py                  # Streamlit application entry point

app/                     # Main application code
├── __init__.py
├── pages/               # Streamlit pages
│   ├── __init__.py
│   └── login.py         # Login page component
├── utils/               # Application utilities
│   ├── __init__.py
│   ├── auth.py          # Main authentication manager
│   ├── auth_utils.py    # Authentication utilities
│   └── config.py        # Application configuration
└── auth/                # Authentication backend
    ├── __init__.py
    └── db_auth.py       # Database authentication backend

scripts/                 # CLI scripts and utilities
├── __init__.py
├── cli.py               # CLI tool for user management
└── data_generator.py    # Data generation utilities

db/                      # Database layer
├── schema.sql           # Database schema (includes dashboard_users)
├── models.py            # Data models (includes DashboardUser)
├── queries.py           # Database queries
├── utils.py             # Database utilities
└── connection.py        # Database connection management

.streamlit/              # Streamlit configuration
├── config.json          # Application configuration
└── encryption.key       # Encryption key (auto-generated on first use)
```

## API Reference

### AuthManager Class

- `authenticate(username, password)` - Authenticate user against database
- `logout()` - Log out current user
- `is_authenticated()` - Check authentication status
- `get_current_user()` - Get current DashboardUser object
- `get_current_username()` - Get current username
- `is_admin()` - Check if current user is admin
- `can_write()` - Check if current user has write permissions
- `can_read()` - Check if current user has read permissions
- `require_authentication()` - Show login form if not authenticated
- `require_admin()` - Require admin privileges
- `require_write_access()` - Require write permissions

### DatabaseAuthManager Class

- `create_user(username, password, role, ...)` - Create new user
- `authenticate(username, password)` - Authenticate against database
- `get_user_by_username(username)` - Get user by username
- `get_all_users()` - Get all users
- `update_user_role(username, role)` - Change user role
- `change_password(username, new_password)` - Change password
- `activate_user(username)` / `deactivate_user(username)` - Enable/disable user
- `unlock_user(username)` - Unlock locked account

### Utility Functions

- `require_auth(func)` - Decorator for authentication
- `require_admin(func)` - Decorator for admin-only pages
- `require_write_access(func)` - Decorator for write-protected pages
- `is_admin()` - Check admin status
- `can_write()` - Check write permissions
- `can_read()` - Check read permissions
- `get_user()` - Get current username
- `protect_page(title, icon)` - Protect page with layout setup

### DashboardUser Model

- `is_admin` - Property: True if user is admin
- `is_locked` - Property: True if account is locked
- `can_write` - Property: True if user has write permissions
- `can_read` - Property: True if user has read permissions
- `display_name` - Property: Full name or username

## Troubleshooting

### Common Issues

1. **Missing cryptography package**: Install with `uv pip install cryptography>=41.0.0`
2. **No encryption key**: Key is auto-generated on first use - try creating a user
3. **Import Errors**: Ensure all modules are in the Python path
4. **Permission Errors**: Check file permissions for `.streamlit/` directory
5. **Configuration Issues**: Verify JSON syntax in config files

### Encryption Key Issues

**Key not found error:**
```bash
# The key will be created automatically when you run:
python cli.py create-user --username admin --password newpassword --role admin
```

**Manual key creation (if needed):**
```python
from cryptography.fernet import Fernet
import os

# Generate key
key = Fernet.generate_key()

# Save to file
os.makedirs('.streamlit', exist_ok=True)
with open('.streamlit/encryption.key', 'wb') as f:
    f.write(key)
```

**Using environment variable:**
```bash
# Set encryption key via environment
export AQUALOG_ENCRYPTION_KEY="your-base64-encoded-key-here"
```

### Verification

**Test the system:**
```bash
# Initialize database
python scripts/cli.py init-db

# Create a test user
python scripts/cli.py create-user --username test --password test123 --role user

# List all users
python scripts/cli.py list-users

# Check that encryption key was created
ls -la .streamlit/encryption.key
```

**Expected results:**
- ✅ Encryption key automatically created in `.streamlit/encryption.key`
- ✅ Default admin user created (admin/admin123)
- ✅ Test user created with encrypted password
- ✅ Users listed with proper roles and status

### Logging

Authentication events are logged using loguru. Check `logs/aqualog.log` for:

- Login attempts (successful and failed)
- Account lockouts
- Configuration loading
- Session management events

## Development

### Testing Authentication

Run the authentication system tests:

```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from app_config import get_config, create_default_credentials
from auth import AuthManager

# Test configuration
config = get_config()
print(f'Config loaded: {config.get(\"app\", \"name\")}')

# Test credentials
create_default_credentials()
print('Credentials created')

# Test auth manager (requires mocking streamlit)
print('Authentication system ready!')
"
```

### Adding New Users

Edit `.streamlit/credentials.json`:

```json
{
  "credentials": {
    "admin": "hashed_password_here",
    "user2": "another_hashed_password"
  }
}
```

Generate password hashes:

```python
import hashlib
password = "your_password"
hash_value = hashlib.sha256(password.encode()).hexdigest()
print(hash_value)
```