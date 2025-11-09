"""
Configuration module for Aqualog application.
Manages application settings, authentication, and environment variables.
"""

import os
from pathlib import Path
from typing import Dict, Any
import json
from loguru import logger


TITLE = ":material/head_mounted_device: Aqualog"
FOOTER = ":material/head_mounted_device: Aqualog | Project repository: [link](https://github.com/samuelefiorini/aqualog)"


class Config:
    """Application configuration manager."""

    def __init__(self, config_file: str = ".streamlit/config.json"):
        """Initialize configuration manager."""
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment variables."""
        config = self._get_default_config()

        # Load from config file if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    file_config = json.load(f)
                    config.update(file_config)
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")

        # Override with environment variables
        self._load_env_overrides(config)

        # Create config file if it doesn't exist
        if not self.config_file.exists():
            self._create_config_file(config)

        return config

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "app": {
                "name": "Aqualog",
                "version": "1.0.0",
                "description": "Freediving Society Management System",
                "debug": False,
            },
            "database": {
                "path": "data/aqualog.duckdb",
                "backup_dir": "backups",
                "auto_backup": True,
                "backup_retention_days": 30,
            },
            "auth": {
                "session_timeout_minutes": 60,
                "max_login_attempts": 5,
                "lockout_duration_minutes": 15,
                "require_auth": True,
                "credentials_file": ".streamlit/credentials.json",
            },
            "ui": {
                "theme": "light",
                "sidebar_expanded": True,
                "show_footer": True,
                "items_per_page": 50,
            },
            "logging": {
                "level": "INFO",
                "file": "logs/aqualog.log",
                "max_size_mb": 10,
                "backup_count": 5,
            },
        }

    def _load_env_overrides(self, config: Dict[str, Any]) -> None:
        """Load configuration overrides from environment variables."""
        env_mappings = {
            "AQUALOG_DEBUG": ("app", "debug", bool),
            "AQUALOG_DB_PATH": ("database", "path", str),
            "AQUALOG_SESSION_TIMEOUT": ("auth", "session_timeout_minutes", int),
            "AQUALOG_MAX_LOGIN_ATTEMPTS": ("auth", "max_login_attempts", int),
            "AQUALOG_LOG_LEVEL": ("logging", "level", str),
            "AQUALOG_REQUIRE_AUTH": ("auth", "require_auth", bool),
        }

        for env_var, (section, key, type_func) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    if type_func == bool:
                        value = value.lower() in ("true", "1", "yes", "on")
                    else:
                        value = type_func(value)

                    config[section][key] = value
                    logger.info(f"Override from env: {env_var} = {value}")
                except ValueError as e:
                    logger.warning(f"Invalid value for {env_var}: {value} ({e})")

    def _create_config_file(self, config: Dict[str, Any]) -> None:
        """Create configuration file with current settings."""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)

            logger.info(f"Created configuration file at {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to create config file: {e}")

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any) -> None:
        """Set configuration value."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

    def save(self) -> bool:
        """Save current configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    def get_database_path(self) -> str:
        """Get database file path."""
        return self.get("database", "path", "data/aqualog.duckdb")

    def get_credentials_file(self) -> str:
        """Get credentials file path."""
        return self.get("auth", "credentials_file", ".streamlit/credentials.json")

    def is_auth_required(self) -> bool:
        """Check if authentication is required."""
        return self.get("auth", "require_auth", True)

    def get_session_timeout(self) -> int:
        """Get session timeout in minutes."""
        return self.get("auth", "session_timeout_minutes", 60)

    def get_max_login_attempts(self) -> int:
        """Get maximum login attempts."""
        return self.get("auth", "max_login_attempts", 5)

    def get_lockout_duration(self) -> int:
        """Get lockout duration in minutes."""
        return self.get("auth", "lockout_duration_minutes", 15)

    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get("app", "debug", False)

    def get_log_level(self) -> str:
        """Get logging level."""
        return self.get("logging", "level", "INFO")


# Global configuration instance
_config = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def create_default_credentials() -> None:
    """Create default credentials file if it doesn't exist."""
    config = get_config()
    credentials_file = Path(config.get_credentials_file())

    if not credentials_file.exists():
        try:
            # Ensure directory exists
            credentials_file.parent.mkdir(parents=True, exist_ok=True)

            # Hash default password
            import hashlib

            default_password_hash = hashlib.sha256("aqualog2025".encode()).hexdigest()

            default_credentials = {
                "credentials": {"admin": default_password_hash},
                "session_timeout_minutes": config.get_session_timeout(),
                "max_login_attempts": config.get_max_login_attempts(),
                "lockout_duration_minutes": config.get_lockout_duration(),
            }

            with open(credentials_file, "w") as f:
                json.dump(default_credentials, f, indent=2)

            logger.info(f"Created default credentials file at {credentials_file}")

        except Exception as e:
            logger.error(f"Failed to create default credentials: {e}")


def setup_logging() -> None:
    """Setup logging configuration."""
    config = get_config()
    log_level = config.get_log_level()
    log_file = config.get("logging", "file", "logs/aqualog.log")

    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure loguru
    logger.remove()  # Remove default handler

    # Add console handler
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    # Add file handler
    logger.add(
        sink=log_file,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=f"{config.get('logging', 'max_size_mb', 10)} MB",
        retention=config.get("logging", "backup_count", 5),
    )

    logger.info(f"Logging configured: level={log_level}, file={log_file}")


# Initialize configuration and logging on import
if __name__ != "__main__":
    setup_logging()
    create_default_credentials()
