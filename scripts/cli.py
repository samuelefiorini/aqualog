#!/usr/bin/env python3
"""
Aqualog CLI - Data Population and Management Tool

This CLI tool provides commands for populating the Aqualog database with
synthetic data and managing database operations.
"""

import typer
from typing import Optional
from pathlib import Path
from loguru import logger
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

app = typer.Typer(
    name="aqualog",
    help="Aqualog CLI - Sistema di Gestione Società di Apnea",
    add_completion=False,
)

# Import database modules
try:
    from db import (
        initialize_database,
        clear_all_data,
        validate_database_integrity,
        export_database_schema,
        get_detailed_stats,
        backup_database,
        optimize_database,
        get_database_stats,
    )
except ImportError as e:
    logger.error(f"Failed to import database modules: {e}")
    typer.echo(
        "Error: Database modules not available. Please ensure the database layer is properly installed."
    )
    raise typer.Exit(1)


@app.command()
def init_db(
    db_path: str = typer.Option(
        "data/aqualog.duckdb",
        "--db-path",
        "-d",
        help="Path to the DuckDB database file",
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force initialization even if database exists"
    ),
) -> None:
    """Initialize the Aqualog database with schema."""
    logger.info(f"Initializing database at {db_path}")

    db_file = Path(db_path)
    if db_file.exists() and not force:
        typer.echo(
            f"Database already exists at {db_path}. Use --force to reinitialize."
        )
        raise typer.Exit(1)

    try:
        success = initialize_database(db_path)
        if success:
            typer.echo(f"✅ Database initialized successfully at {db_path}")
            logger.info("Database initialization completed")
        else:
            typer.echo("❌ Database initialization failed")
            raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        typer.echo(f"❌ Error initializing database: {e}")
        raise typer.Exit(1)


@app.command()
def clear_data(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Clear all data from the database."""
    if not confirm:
        confirm = typer.confirm(
            "Are you sure you want to clear all data? This cannot be undone."
        )
        if not confirm:
            typer.echo("Operation cancelled.")
            return

    logger.info("Clearing all database data")

    try:
        success = clear_all_data()
        if success:
            typer.echo("✅ All data cleared successfully")
            logger.info("Database data cleared")
        else:
            typer.echo("❌ Failed to clear data")
            raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        typer.echo(f"❌ Error clearing data: {e}")
        raise typer.Exit(1)


@app.command()
def validate(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed validation results"
    ),
) -> None:
    """Validate database integrity and data quality."""
    logger.info("Starting database validation")

    try:
        results = validate_database_integrity()

        if results["valid"]:
            typer.echo("✅ Database validation passed")
        else:
            typer.echo("❌ Database validation failed")

        if verbose or not results["valid"]:
            # Show table counts
            typer.echo("\n📊 Table Counts:")
            for table, count in results["table_counts"].items():
                typer.echo(f"  {table}: {count}")

            # Show errors
            if results["errors"]:
                typer.echo("\n❌ Errors:")
                for error in results["errors"]:
                    typer.echo(f"  • {error}")

            # Show warnings
            if results["warnings"]:
                typer.echo("\n⚠️  Warnings:")
                for warning in results["warnings"]:
                    typer.echo(f"  • {warning}")

            # Show foreign key violations
            if results["foreign_key_violations"]:
                typer.echo("\n🔗 Foreign Key Violations:")
                for violation in results["foreign_key_violations"]:
                    typer.echo(f"  • {violation}")

        if not results["valid"]:
            raise typer.Exit(1)

    except Exception as e:
        logger.error(f"Validation error: {e}")
        typer.echo(f"❌ Error during validation: {e}")
        raise typer.Exit(1)


@app.command()
def stats(
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed statistics"
    ),
) -> None:
    """Show database statistics."""
    logger.info("Retrieving database statistics")

    try:
        if detailed:
            stats_data = get_detailed_stats()

            typer.echo("📊 Detailed Database Statistics")
            typer.echo("=" * 40)

            # Basic stats
            basic = stats_data.get("basic_stats", {})
            typer.echo(f"\n📈 Basic Statistics:")
            typer.echo(f"  Members: {basic.get('total_members', 0)}")
            typer.echo(f"  Cooper Tests: {basic.get('total_cooper_tests', 0)}")
            typer.echo(f"  Indoor Trials: {basic.get('total_indoor_trials', 0)}")
            typer.echo(f"  Database Size: {basic.get('database_size_mb', 0):.2f} MB")

            # Member stats
            member_stats = stats_data.get("member_stats", {})
            if member_stats:
                typer.echo(f"\n👥 Member Statistics:")
                typer.echo(
                    f"  Age Range: {member_stats.get('min_age', 0)} - {member_stats.get('max_age', 0)} years"
                )
                typer.echo(f"  Average Age: {member_stats.get('avg_age', 0)} years")

            # Cooper test stats
            cooper_stats = stats_data.get("cooper_test_stats", {})
            if cooper_stats:
                typer.echo(f"\n🏊 Cooper Test Statistics:")
                typer.echo(
                    f"  Members with Tests: {cooper_stats.get('members_with_tests', 0)}"
                )
                typer.echo(
                    f"  Avg Cycles per Test: {cooper_stats.get('avg_cycles_per_test', 0)}"
                )
                if cooper_stats.get("earliest_test"):
                    typer.echo(
                        f"  Date Range: {cooper_stats.get('earliest_test')} to {cooper_stats.get('latest_test')}"
                    )

            # Indoor trial stats
            trial_stats = stats_data.get("indoor_trial_stats", {})
            if trial_stats:
                typer.echo(f"\n🏊‍♂️ Indoor Trial Statistics:")
                typer.echo(
                    f"  Members with Trials: {trial_stats.get('members_with_trials', 0)}"
                )
                typer.echo(
                    f"  Distance Range: {trial_stats.get('min_distance', 0)} - {trial_stats.get('max_distance', 0)} meters"
                )
                typer.echo(
                    f"  Average Distance: {trial_stats.get('avg_distance', 0)} meters"
                )
                typer.echo(
                    f"  Trials with Time Data: {trial_stats.get('time_tracking_percentage', 0)}%"
                )

            # Performance summary
            performance = stats_data.get("performance_summary", {})
            if performance:
                typer.echo(f"\n🏆 Performance Summary:")
                typer.echo(
                    f"  Most Active Member: {performance.get('most_active_member', 'N/A')}"
                )
                typer.echo(
                    f"  Total Activities: {performance.get('most_active_member_activities', 0)}"
                )

        else:
            # Simple stats
            stats_data = get_database_stats()
            typer.echo("📊 Database Statistics")
            typer.echo("=" * 25)
            typer.echo(f"Members: {stats_data.total_members}")
            typer.echo(f"Cooper Tests: {stats_data.total_cooper_tests}")
            typer.echo(f"Indoor Trials: {stats_data.total_indoor_trials}")
            typer.echo(f"Database Size: {stats_data.database_size_mb:.2f} MB")

    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        typer.echo(f"❌ Error retrieving statistics: {e}")
        raise typer.Exit(1)


@app.command()
def export_schema(
    output: str = typer.Option(
        "schema_export.sql", "--output", "-o", help="Output file path for schema export"
    ),
) -> None:
    """Export database schema to SQL file."""
    logger.info(f"Exporting database schema to {output}")

    try:
        schema_content = export_database_schema(output)
        if schema_content:
            typer.echo(f"✅ Schema exported successfully to {output}")
            logger.info(f"Schema export completed: {output}")
        else:
            typer.echo("❌ Schema export failed")
            raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Schema export error: {e}")
        typer.echo(f"❌ Error exporting schema: {e}")
        raise typer.Exit(1)


@app.command()
def backup(
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Backup file path (default: backup_YYYYMMDD_HHMMSS.duckdb)",
    ),
) -> None:
    """Create a backup of the database."""
    if output is None:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"backup_{timestamp}.duckdb"

    logger.info(f"Creating database backup: {output}")

    try:
        success = backup_database(output)
        if success:
            typer.echo(f"✅ Database backed up successfully to {output}")
            logger.info(f"Database backup completed: {output}")
        else:
            typer.echo("❌ Database backup failed")
            raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Backup error: {e}")
        typer.echo(f"❌ Error creating backup: {e}")
        raise typer.Exit(1)


@app.command()
def optimize() -> None:
    """Optimize database performance (VACUUM and ANALYZE)."""
    logger.info("Optimizing database performance")

    try:
        success = optimize_database()
        if success:
            typer.echo("✅ Database optimization completed successfully")
            logger.info("Database optimization completed")
        else:
            typer.echo("❌ Database optimization failed")
            raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        typer.echo(f"❌ Error optimizing database: {e}")
        raise typer.Exit(1)


@app.command()
def populate(
    members: int = typer.Option(
        50, "--members", "-m", help="Number of members to generate", min=1, max=1000
    ),
    min_tests: int = typer.Option(
        1, "--min-tests", help="Minimum Cooper tests per member", min=0, max=20
    ),
    max_tests: int = typer.Option(
        5, "--max-tests", help="Maximum Cooper tests per member", min=1, max=20
    ),
    min_trials: int = typer.Option(
        2, "--min-trials", help="Minimum indoor trials per member", min=0, max=50
    ),
    max_trials: int = typer.Option(
        8, "--max-trials", help="Maximum indoor trials per member", min=1, max=50
    ),
    clear_first: bool = typer.Option(
        False, "--clear", "-c", help="Clear existing data before populating"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed progress information"
    ),
) -> None:
    """Populate database with synthetic Italian freediving data."""

    # Validate parameters
    if min_tests > max_tests:
        typer.echo("❌ Error: min-tests cannot be greater than max-tests")
        raise typer.Exit(1)

    if min_trials > max_trials:
        typer.echo("❌ Error: min-trials cannot be greater than max-trials")
        raise typer.Exit(1)

    logger.info(f"Starting data population: {members} members")

    # Clear data if requested
    if clear_first:
        typer.echo("🗑️  Clearing existing data...")
        try:
            success = clear_all_data()
            if not success:
                typer.echo("❌ Failed to clear existing data")
                raise typer.Exit(1)
            typer.echo("✅ Existing data cleared")
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            typer.echo(f"❌ Error clearing data: {e}")
            raise typer.Exit(1)

    # Import data generator
    try:
        from data_generator import DataGenerator
    except ImportError as e:
        logger.error(f"Failed to import data generator: {e}")
        typer.echo("❌ Error: Data generator not available")
        raise typer.Exit(1)

    # Initialize generator
    generator = DataGenerator()

    # Show generation plan
    estimated_tests = members * ((min_tests + max_tests) // 2)
    estimated_trials = members * ((min_trials + max_trials) // 2)

    typer.echo(f"📊 Generation Plan:")
    typer.echo(f"  Members: {members}")
    typer.echo(
        f"  Cooper Tests: ~{estimated_tests} ({min_tests}-{max_tests} per member)"
    )
    typer.echo(
        f"  Indoor Trials: ~{estimated_trials} ({min_trials}-{max_trials} per member)"
    )
    typer.echo()

    # Progress callback
    def progress_callback(message: str):
        if verbose:
            typer.echo(f"  {message}")

    try:
        stats = generator.populate_database(
            num_members=members,
            tests_per_member=(min_tests, max_tests),
            trials_per_member=(min_trials, max_trials),
            progress_callback=progress_callback,
        )

        # Show results
        typer.echo("✅ Data generation completed!")
        typer.echo(f"📊 Results:")
        typer.echo(f"  Members created: {stats['members_created']}")
        typer.echo(f"  Cooper tests created: {stats['cooper_tests_created']}")
        typer.echo(f"  Indoor trials created: {stats['indoor_trials_created']}")

        if stats["errors"]:
            typer.echo(f"\n⚠️  Errors encountered: {len(stats['errors'])}")
            if verbose:
                for error in stats["errors"]:
                    typer.echo(f"    • {error}")

        logger.info(f"Data population completed successfully: {stats}")

    except Exception as e:
        logger.error(f"Data population error: {e}")
        typer.echo(f"❌ Error during data generation: {e}")
        raise typer.Exit(1)


@app.command()
def generate_sample(
    output_dir: str = typer.Option(
        "sample_data", "--output", "-o", help="Output directory for sample data files"
    ),
) -> None:
    """Generate sample data files for testing (without database insertion)."""
    from pathlib import Path
    import json

    logger.info(f"Generating sample data files in {output_dir}")

    try:
        from data_generator import DataGenerator
    except ImportError as e:
        logger.error(f"Failed to import data generator: {e}")
        typer.echo("❌ Error: Data generator not available")
        raise typer.Exit(1)

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    generator = DataGenerator()

    try:
        # Generate sample members
        members_data = []
        for i in range(10):
            member_data = generator.generate_member()
            members_data.append(
                {
                    "id": i + 1,
                    "first_name": member_data[0],
                    "last_name": member_data[1],
                    "birth_date": member_data[2].isoformat(),
                    "email": member_data[3],
                    "membership_date": member_data[4].isoformat(),
                }
            )

        # Save members data
        with open(output_path / "sample_members.json", "w", encoding="utf-8") as f:
            json.dump(members_data, f, indent=2, ensure_ascii=False)

        # Generate sample Cooper tests
        cooper_tests = []
        for i in range(5):
            test_data = generator.generate_cooper_test(i + 1, "intermediate")
            cooper_tests.append(
                {
                    "member_id": test_data[0],
                    "test_date": test_data[1].isoformat(),
                    "diving_times": [t.strftime("%H:%M:%S") for t in test_data[2]],
                    "surface_times": [t.strftime("%H:%M:%S") for t in test_data[3]],
                    "pool_length_meters": test_data[4],
                    "notes": test_data[5],
                }
            )

        # Save Cooper tests data
        with open(output_path / "sample_cooper_tests.json", "w", encoding="utf-8") as f:
            json.dump(cooper_tests, f, indent=2, ensure_ascii=False)

        # Generate sample indoor trials
        indoor_trials = []
        for i in range(8):
            trial_data = generator.generate_indoor_trial(i + 1, "intermediate")
            indoor_trials.append(
                {
                    "member_id": trial_data[0],
                    "trial_date": trial_data[1].isoformat(),
                    "location": trial_data[2],
                    "distance_meters": trial_data[3],
                    "time_seconds": trial_data[4],
                    "pool_length_meters": trial_data[5],
                }
            )

        # Save indoor trials data
        with open(
            output_path / "sample_indoor_trials.json", "w", encoding="utf-8"
        ) as f:
            json.dump(indoor_trials, f, indent=2, ensure_ascii=False)

        typer.echo(f"✅ Sample data files generated in {output_dir}/")
        typer.echo(f"  • sample_members.json (10 members)")
        typer.echo(f"  • sample_cooper_tests.json (5 tests)")
        typer.echo(f"  • sample_indoor_trials.json (8 trials)")

        logger.info(f"Sample data generation completed: {output_dir}")

    except Exception as e:
        logger.error(f"Sample data generation error: {e}")
        typer.echo(f"❌ Error generating sample data: {e}")
        raise typer.Exit(1)


@app.command()
def create_user(
    username: str = typer.Option(
        ..., "--username", "-u", help="Username for the new user"
    ),
    password: str = typer.Option(
        ..., "--password", "-p", help="Password for the new user"
    ),
    role: str = typer.Option("user", "--role", "-r", help="User role (admin or user)"),
    full_name: str = typer.Option(None, "--name", "-n", help="Full name of the user"),
    email: str = typer.Option(None, "--email", "-e", help="Email address of the user"),
) -> None:
    """Create a new dashboard user."""

    if role not in ["admin", "user"]:
        typer.echo("❌ Error: Role must be 'admin' or 'user'")
        raise typer.Exit(1)

    logger.info(f"Creating user: {username} (role: {role})")

    try:
        from app.auth.db_auth import get_db_auth_manager

        db_auth = get_db_auth_manager()

        # Check if user already exists
        existing_user = db_auth.get_user_by_username(username)
        if existing_user:
            typer.echo(f"❌ Error: User '{username}' already exists")
            raise typer.Exit(1)

        # Create user
        user_id = db_auth.create_user(
            username=username,
            password=password,
            role=role,
            full_name=full_name,
            email=email,
        )

        typer.echo(f"✅ User '{username}' created successfully (ID: {user_id})")
        typer.echo(f"   Role: {role}")
        if full_name:
            typer.echo(f"   Name: {full_name}")
        if email:
            typer.echo(f"   Email: {email}")

        logger.info(f"User creation completed: {username}")

    except Exception as e:
        logger.error(f"User creation error: {e}")
        typer.echo(f"❌ Error creating user: {e}")
        raise typer.Exit(1)


@app.command()
def list_users() -> None:
    """List all dashboard users."""
    logger.info("Listing all users")

    try:
        from app.auth.db_auth import get_db_auth_manager

        db_auth = get_db_auth_manager()
        users = db_auth.get_all_users()

        if not users:
            typer.echo("No users found.")
            return

        typer.echo("👥 Dashboard Users")
        typer.echo("=" * 50)

        for user in users:
            status = "🟢 Active" if user.is_active else "🔴 Inactive"
            locked = " 🔒 Locked" if user.is_locked else ""
            role_icon = "👑" if user.is_admin else "👤"

            typer.echo(f"{role_icon} {user.username} ({user.role}) - {status}{locked}")
            if user.full_name:
                typer.echo(f"   Name: {user.full_name}")
            if user.email:
                typer.echo(f"   Email: {user.email}")
            if user.last_login:
                typer.echo(f"   Last Login: {user.last_login}")
            typer.echo(f"   Created: {user.created_at}")
            typer.echo()

        logger.info(f"Listed {len(users)} users")

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        typer.echo(f"❌ Error listing users: {e}")
        raise typer.Exit(1)


@app.command()
def change_password(
    username: str = typer.Option(
        ..., "--username", "-u", help="Username to change password for"
    ),
    new_password: str = typer.Option(..., "--password", "-p", help="New password"),
) -> None:
    """Change user password."""
    logger.info(f"Changing password for user: {username}")

    try:
        from app.auth.db_auth import get_db_auth_manager

        db_auth = get_db_auth_manager()

        # Check if user exists
        user = db_auth.get_user_by_username(username)
        if not user:
            typer.echo(f"❌ Error: User '{username}' not found")
            raise typer.Exit(1)

        # Change password
        success = db_auth.change_password(username, new_password)

        if success:
            typer.echo(f"✅ Password changed successfully for user '{username}'")
            logger.info(f"Password changed for user: {username}")
        else:
            typer.echo(f"❌ Failed to change password for user '{username}'")
            raise typer.Exit(1)

    except Exception as e:
        logger.error(f"Password change error: {e}")
        typer.echo(f"❌ Error changing password: {e}")
        raise typer.Exit(1)


@app.command()
def change_role(
    username: str = typer.Option(
        ..., "--username", "-u", help="Username to change role for"
    ),
    role: str = typer.Option(..., "--role", "-r", help="New role (admin or user)"),
) -> None:
    """Change user role."""

    if role not in ["admin", "user"]:
        typer.echo("❌ Error: Role must be 'admin' or 'user'")
        raise typer.Exit(1)

    logger.info(f"Changing role for user: {username} to {role}")

    try:
        from app.auth.db_auth import get_db_auth_manager

        db_auth = get_db_auth_manager()

        # Check if user exists
        user = db_auth.get_user_by_username(username)
        if not user:
            typer.echo(f"❌ Error: User '{username}' not found")
            raise typer.Exit(1)

        # Change role
        success = db_auth.update_user_role(username, role)

        if success:
            typer.echo(
                f"✅ Role changed successfully for user '{username}' to '{role}'"
            )
            logger.info(f"Role changed for user: {username} to {role}")
        else:
            typer.echo(f"❌ Failed to change role for user '{username}'")
            raise typer.Exit(1)

    except Exception as e:
        logger.error(f"Role change error: {e}")
        typer.echo(f"❌ Error changing role: {e}")
        raise typer.Exit(1)


@app.command()
def deactivate_user(
    username: str = typer.Option(
        ..., "--username", "-u", help="Username to deactivate"
    ),
) -> None:
    """Deactivate user account."""
    logger.info(f"Deactivating user: {username}")

    try:
        from app.auth.db_auth import get_db_auth_manager

        db_auth = get_db_auth_manager()

        # Check if user exists
        user = db_auth.get_user_by_username(username)
        if not user:
            typer.echo(f"❌ Error: User '{username}' not found")
            raise typer.Exit(1)

        # Deactivate user
        success = db_auth.deactivate_user(username)

        if success:
            typer.echo(f"✅ User '{username}' deactivated successfully")
            logger.info(f"User deactivated: {username}")
        else:
            typer.echo(f"❌ Failed to deactivate user '{username}'")
            raise typer.Exit(1)

    except Exception as e:
        logger.error(f"User deactivation error: {e}")
        typer.echo(f"❌ Error deactivating user: {e}")
        raise typer.Exit(1)


@app.command()
def activate_user(
    username: str = typer.Option(..., "--username", "-u", help="Username to activate"),
) -> None:
    """Activate user account."""
    logger.info(f"Activating user: {username}")

    try:
        from app.auth.db_auth import get_db_auth_manager

        db_auth = get_db_auth_manager()

        # Check if user exists
        user = db_auth.get_user_by_username(username)
        if not user:
            typer.echo(f"❌ Error: User '{username}' not found")
            raise typer.Exit(1)

        # Activate user
        success = db_auth.activate_user(username)

        if success:
            typer.echo(f"✅ User '{username}' activated successfully")
            logger.info(f"User activated: {username}")
        else:
            typer.echo(f"❌ Failed to activate user '{username}'")
            raise typer.Exit(1)

    except Exception as e:
        logger.error(f"User activation error: {e}")
        typer.echo(f"❌ Error activating user: {e}")
        raise typer.Exit(1)


@app.command()
def unlock_user(
    username: str = typer.Option(..., "--username", "-u", help="Username to unlock"),
) -> None:
    """Unlock user account."""
    logger.info(f"Unlocking user: {username}")

    try:
        from app.auth.db_auth import get_db_auth_manager

        db_auth = get_db_auth_manager()

        # Check if user exists
        user = db_auth.get_user_by_username(username)
        if not user:
            typer.echo(f"❌ Error: User '{username}' not found")
            raise typer.Exit(1)

        # Unlock user
        success = db_auth.unlock_user(username)

        if success:
            typer.echo(f"✅ User '{username}' unlocked successfully")
            logger.info(f"User unlocked: {username}")
        else:
            typer.echo(f"❌ Failed to unlock user '{username}'")
            raise typer.Exit(1)

    except Exception as e:
        logger.error(f"User unlock error: {e}")
        typer.echo(f"❌ Error unlocking user: {e}")
        raise typer.Exit(1)


@app.command()
def delete_user(
    username: str = typer.Option(..., "--username", "-u", help="Username to delete"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete user account permanently."""

    # Prevent deleting the default admin
    if username == "admin":
        typer.echo("❌ Error: Cannot delete the default admin user")
        raise typer.Exit(1)

    if not confirm:
        confirm = typer.confirm(
            f"Are you sure you want to delete user '{username}'? This cannot be undone."
        )
        if not confirm:
            typer.echo("Operation cancelled.")
            return

    logger.info(f"Deleting user: {username}")

    try:
        from app.auth.db_auth import get_db_auth_manager

        db_auth = get_db_auth_manager()

        # Check if user exists
        user = db_auth.get_user_by_username(username)
        if not user:
            typer.echo(f"❌ Error: User '{username}' not found")
            raise typer.Exit(1)

        # Delete user
        success = db_auth.delete_user(username)

        if success:
            typer.echo(f"✅ User '{username}' deleted successfully")
            logger.info(f"User deleted: {username}")
        else:
            typer.echo(f"❌ Failed to delete user '{username}'")
            raise typer.Exit(1)

    except Exception as e:
        logger.error(f"User deletion error: {e}")
        typer.echo(f"❌ Error deleting user: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
