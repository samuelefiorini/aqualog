"""
Database utility functions for Aqualog.
Provides database management, validation, and maintenance operations.
"""

from pathlib import Path
from typing import Any

from loguru import logger

from .connection import get_db_connection


def initialize_database(db_path: str = "data/aqualog.duckdb") -> bool:
    """Initialize database with schema and return success status."""
    try:
        # Create database connection (this will automatically initialize schema)
        from .connection import DatabaseConnection

        db = DatabaseConnection(db_path)
        db.connect()

        logger.info(f"Database initialized successfully at {db_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False


def clear_all_data() -> bool:
    """Clear all data from database tables while preserving schema."""
    try:
        db = get_db_connection()

        # Clear tables in correct order (respecting foreign key constraints)
        tables = ["cooper_tests", "indoor_trials", "members"]

        for table in tables:
            db.execute_query(f"DELETE FROM {table}")
            logger.info(f"Cleared all data from {table} table")

        logger.info("All database data cleared successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to clear database data: {e}")
        return False


def validate_database_integrity() -> dict[str, Any]:
    """Validate database integrity and return validation results."""
    try:
        db = get_db_connection()
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "table_counts": {},
            "foreign_key_violations": [],
        }

        # Check table existence and get counts
        tables = ["members", "cooper_tests", "indoor_trials"]

        for table in tables:
            try:
                count_result = db.fetch_one(f"SELECT COUNT(*) FROM {table}")
                validation_results["table_counts"][table] = (
                    count_result[0] if count_result else 0
                )
            except Exception as e:
                validation_results["errors"].append(
                    f"Table {table} not accessible: {e}"
                )
                validation_results["valid"] = False

        # Check foreign key constraints
        # Check cooper_tests references
        orphaned_cooper = db.fetch_one("""
            SELECT COUNT(*) FROM cooper_tests ct
            LEFT JOIN members m ON ct.member_id = m.id
            WHERE m.id IS NULL
        """)

        if orphaned_cooper and orphaned_cooper[0] > 0:
            validation_results["foreign_key_violations"].append(
                f"Found {orphaned_cooper[0]} Cooper tests with invalid member references"
            )
            validation_results["valid"] = False

        # Check indoor_trials references
        orphaned_trials = db.fetch_one("""
            SELECT COUNT(*) FROM indoor_trials it
            LEFT JOIN members m ON it.member_id = m.id
            WHERE m.id IS NULL
        """)

        if orphaned_trials and orphaned_trials[0] > 0:
            validation_results["foreign_key_violations"].append(
                f"Found {orphaned_trials[0]} indoor trials with invalid member references"
            )
            validation_results["valid"] = False

        # Check for data quality issues
        # Members with future birth dates
        future_births = db.fetch_one("""
            SELECT COUNT(*) FROM members
            WHERE date_of_birth > CURRENT_DATE
        """)

        if future_births and future_births[0] > 0:
            validation_results["warnings"].append(
                f"Found {future_births[0]} members with future birth dates"
            )

        # Members with membership dates before birth dates
        invalid_membership = db.fetch_one("""
            SELECT COUNT(*) FROM members
            WHERE membership_start_date < date_of_birth
        """)

        if invalid_membership and invalid_membership[0] > 0:
            validation_results["warnings"].append(
                f"Found {invalid_membership[0]} members with membership dates before birth dates"
            )

        # Cooper tests with empty time arrays
        empty_cooper_times = db.fetch_one("""
            SELECT COUNT(*) FROM cooper_tests
            WHERE array_length(diving_times) = 0 OR array_length(surface_times) = 0
        """)

        if empty_cooper_times and empty_cooper_times[0] > 0:
            validation_results["warnings"].append(
                f"Found {empty_cooper_times[0]} Cooper tests with empty time arrays"
            )

        # Indoor trials with zero distance
        zero_distance_trials = db.fetch_one("""
            SELECT COUNT(*) FROM indoor_trials
            WHERE distance_meters <= 0
        """)

        if zero_distance_trials and zero_distance_trials[0] > 0:
            validation_results["warnings"].append(
                f"Found {zero_distance_trials[0]} indoor trials with zero or negative distance"
            )

        logger.info(
            f"Database validation completed. Valid: {validation_results['valid']}"
        )
        return validation_results

    except Exception as e:
        logger.error(f"Database validation failed: {e}")
        return {
            "valid": False,
            "errors": [f"Validation process failed: {e}"],
            "warnings": [],
            "table_counts": {},
            "foreign_key_violations": [],
        }


def export_database_schema(output_path: str | None = None) -> str:
    """Export database schema to SQL file and return the schema as string."""
    try:
        db = get_db_connection()

        # Get schema information for all tables
        schema_query = """
        SELECT sql FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """

        schema_rows = db.fetch_all(schema_query)

        # Get index information
        index_query = """
        SELECT sql FROM sqlite_master
        WHERE type='index' AND name NOT LIKE 'sqlite_%' AND sql IS NOT NULL
        ORDER BY name
        """

        index_rows = db.fetch_all(index_query)

        # Build schema string
        schema_lines = [
            "-- Aqualog Database Schema Export",
            f"-- Generated on: {logger._core.now()}",
            "",
            "-- Tables",
        ]

        for row in schema_rows:
            if row[0]:  # sql column
                schema_lines.append(row[0] + ";")
                schema_lines.append("")

        schema_lines.extend(["-- Indexes", ""])

        for row in index_rows:
            if row[0]:  # sql column
                schema_lines.append(row[0] + ";")
                schema_lines.append("")

        schema_content = "\n".join(schema_lines)

        # Write to file if path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                f.write(schema_content)

            logger.info(f"Database schema exported to {output_path}")

        return schema_content

    except Exception as e:
        logger.error(f"Failed to export database schema: {e}")
        return ""


def get_detailed_stats() -> dict[str, Any]:
    """Get detailed database statistics for analysis."""
    try:
        db = get_db_connection()

        stats = {
            "basic_stats": {},
            "member_stats": {},
            "cooper_test_stats": {},
            "indoor_trial_stats": {},
            "performance_summary": {},
        }

        # Basic statistics
        basic_stats = get_database_stats()
        stats["basic_stats"] = {
            "total_members": basic_stats.total_members,
            "total_cooper_tests": basic_stats.total_cooper_tests,
            "total_indoor_trials": basic_stats.total_indoor_trials,
            "database_size_mb": basic_stats.database_size_mb,
        }

        # Member statistics
        member_age_stats = db.fetch_one("""
            SELECT
                MIN(EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM date_of_birth)) as min_age,
                MAX(EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM date_of_birth)) as max_age,
                AVG(EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM date_of_birth)) as avg_age
            FROM members
        """)

        if member_age_stats:
            stats["member_stats"] = {
                "min_age": member_age_stats[0],
                "max_age": member_age_stats[1],
                "avg_age": round(member_age_stats[2], 1) if member_age_stats[2] else 0,
            }

        # Cooper test statistics
        cooper_stats = db.fetch_one("""
            SELECT
                COUNT(DISTINCT member_id) as members_with_tests,
                AVG(array_length(diving_times)) as avg_cycles_per_test,
                MIN(test_date) as earliest_test,
                MAX(test_date) as latest_test
            FROM cooper_tests
        """)

        if cooper_stats:
            stats["cooper_test_stats"] = {
                "members_with_tests": cooper_stats[0],
                "avg_cycles_per_test": round(cooper_stats[1], 1)
                if cooper_stats[1]
                else 0,
                "earliest_test": cooper_stats[2],
                "latest_test": cooper_stats[3],
            }

        # Indoor trial statistics
        trial_stats = db.fetch_one("""
            SELECT
                COUNT(DISTINCT member_id) as members_with_trials,
                AVG(distance_meters) as avg_distance,
                MIN(distance_meters) as min_distance,
                MAX(distance_meters) as max_distance,
                COUNT(CASE WHEN time_seconds IS NOT NULL THEN 1 END) as trials_with_time
            FROM indoor_trials
        """)

        if trial_stats:
            stats["indoor_trial_stats"] = {
                "members_with_trials": trial_stats[0],
                "avg_distance": round(trial_stats[1], 1) if trial_stats[1] else 0,
                "min_distance": trial_stats[2],
                "max_distance": trial_stats[3],
                "trials_with_time": trial_stats[4],
                "time_tracking_percentage": round(
                    (trial_stats[4] / basic_stats.total_indoor_trials * 100)
                    if basic_stats.total_indoor_trials > 0
                    else 0,
                    1,
                ),
            }

        # Performance summary
        most_active_member = db.fetch_one("""
            SELECT m.name || ' ' || m.surname as member_name,
                   COUNT(ct.id) + COUNT(it.id) as total_activities
            FROM members m
            LEFT JOIN cooper_tests ct ON m.id = ct.member_id
            LEFT JOIN indoor_trials it ON m.id = it.member_id
            GROUP BY m.id, m.name, m.surname
            ORDER BY total_activities DESC
            LIMIT 1
        """)

        if most_active_member:
            stats["performance_summary"] = {
                "most_active_member": most_active_member[0],
                "most_active_member_activities": most_active_member[1],
            }

        logger.info("Generated detailed database statistics")
        return stats

    except Exception as e:
        logger.error(f"Failed to generate detailed stats: {e}")
        return {}


def backup_database(backup_path: str) -> bool:
    """Create a backup of the database file."""
    try:
        db = get_db_connection()
        source_path = Path(db.db_path)
        backup_file = Path(backup_path)

        # Ensure backup directory exists
        backup_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy database file
        import shutil

        shutil.copy2(source_path, backup_file)

        logger.info(f"Database backed up to {backup_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to backup database: {e}")
        return False


def optimize_database() -> bool:
    """Optimize database performance by running VACUUM and ANALYZE."""
    try:
        db = get_db_connection()

        # Run VACUUM to reclaim space and defragment
        db.execute_query("VACUUM")
        logger.info("Database VACUUM completed")

        # Run ANALYZE to update query planner statistics
        db.execute_query("ANALYZE")
        logger.info("Database ANALYZE completed")

        logger.info("Database optimization completed successfully")
        return True

    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        return False
