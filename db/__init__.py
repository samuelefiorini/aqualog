"""
Aqualog Database Module

This module provides database functionality for the freediving management system,
including connection management, data models, queries, and utilities.
"""

from .connection import DatabaseConnection, get_db_connection
from .models import Member, CooperTest, IndoorTrial, DatabaseStats, PerformanceTrend
from .queries import (
    get_all_members,
    get_member_by_id,
    get_all_cooper_tests,
    get_cooper_tests_by_member,
    get_all_indoor_trials,
    get_indoor_trials_by_member,
    get_database_stats,
    insert_member,
    insert_cooper_test,
    insert_indoor_trial,
    get_performance_trends_cooper,
    get_performance_trends_trials,
)
from .utils import (
    initialize_database,
    clear_all_data,
    validate_database_integrity,
    export_database_schema,
    get_detailed_stats,
    backup_database,
    optimize_database,
)

__all__ = [
    # Connection
    "DatabaseConnection",
    "get_db_connection",
    # Models
    "Member",
    "CooperTest",
    "IndoorTrial",
    "DatabaseStats",
    "PerformanceTrend",
    # Queries
    "get_all_members",
    "get_member_by_id",
    "get_all_cooper_tests",
    "get_cooper_tests_by_member",
    "get_all_indoor_trials",
    "get_indoor_trials_by_member",
    "get_database_stats",
    "insert_member",
    "insert_cooper_test",
    "insert_indoor_trial",
    "get_performance_trends_cooper",
    "get_performance_trends_trials",
    # Utilities
    "initialize_database",
    "clear_all_data",
    "validate_database_integrity",
    "export_database_schema",
    "get_detailed_stats",
    "backup_database",
    "optimize_database",
]
