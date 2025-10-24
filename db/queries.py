"""
Centralized query functions for Aqualog database operations.
Provides type-safe database access with proper error handling.
"""

from datetime import date, time

from loguru import logger

from .connection import get_db_connection
from .models import CooperTest, DatabaseStats, IndoorTrial, Member, PerformanceTrend


def get_all_members() -> list[Member]:
    """Retrieve all members from the database."""
    try:
        db = get_db_connection()
        query = """
        SELECT id, name, surname, date_of_birth, contact_info,
               membership_start_date, created_at
        FROM members
        ORDER BY surname, name
        """

        rows = db.fetch_all(query)
        members = []

        for row in rows:
            member = Member(
                id=row[0],
                name=row[1],
                surname=row[2],
                date_of_birth=row[3],
                contact_info=row[4],
                membership_start_date=row[5],
                created_at=row[6],
            )
            members.append(member)

        logger.info(f"Retrieved {len(members)} members from database")
        return members

    except Exception as e:
        logger.error(f"Failed to retrieve members: {e}")
        return []


def get_member_by_id(member_id: int) -> Member | None:
    """Retrieve a specific member by ID."""
    try:
        db = get_db_connection()
        query = """
        SELECT id, name, surname, date_of_birth, contact_info,
               membership_start_date, created_at
        FROM members
        WHERE id = ?
        """

        row = db.fetch_one(query, (member_id,))
        if row:
            return Member(
                id=row[0],
                name=row[1],
                surname=row[2],
                date_of_birth=row[3],
                contact_info=row[4],
                membership_start_date=row[5],
                created_at=row[6],
            )
        return None

    except Exception as e:
        logger.error(f"Failed to retrieve member {member_id}: {e}")
        return None


def get_all_cooper_tests() -> list[CooperTest]:
    """Retrieve all Cooper tests from the database."""
    try:
        db = get_db_connection()
        query = """
        SELECT id, member_id, test_date, diving_times, surface_times,
               pool_length_meters, notes, created_at
        FROM cooper_tests
        ORDER BY test_date DESC, member_id
        """

        rows = db.fetch_all(query)
        tests = []

        for row in rows:
            test = CooperTest(
                id=row[0],
                member_id=row[1],
                test_date=row[2],
                diving_times=row[3] if row[3] else [],
                surface_times=row[4] if row[4] else [],
                pool_length_meters=row[5],
                notes=row[6],
                created_at=row[7],
            )
            tests.append(test)

        logger.info(f"Retrieved {len(tests)} Cooper tests from database")
        return tests

    except Exception as e:
        logger.error(f"Failed to retrieve Cooper tests: {e}")
        return []


def get_cooper_tests_by_member(member_id: int) -> list[CooperTest]:
    """Retrieve Cooper tests for a specific member."""
    try:
        db = get_db_connection()
        query = """
        SELECT id, member_id, test_date, diving_times, surface_times,
               pool_length_meters, notes, created_at
        FROM cooper_tests
        WHERE member_id = ?
        ORDER BY test_date DESC
        """

        rows = db.fetch_all(query, (member_id,))
        tests = []

        for row in rows:
            test = CooperTest(
                id=row[0],
                member_id=row[1],
                test_date=row[2],
                diving_times=row[3] if row[3] else [],
                surface_times=row[4] if row[4] else [],
                pool_length_meters=row[5],
                notes=row[6],
                created_at=row[7],
            )
            tests.append(test)

        logger.info(f"Retrieved {len(tests)} Cooper tests for member {member_id}")
        return tests

    except Exception as e:
        logger.error(f"Failed to retrieve Cooper tests for member {member_id}: {e}")
        return []


def get_all_indoor_trials() -> list[IndoorTrial]:
    """Retrieve all indoor trials from the database."""
    try:
        db = get_db_connection()
        query = """
        SELECT id, member_id, trial_date, location, distance_meters,
               time_seconds, pool_length_meters, created_at
        FROM indoor_trials
        ORDER BY trial_date DESC, member_id
        """

        rows = db.fetch_all(query)
        trials = []

        for row in rows:
            trial = IndoorTrial(
                id=row[0],
                member_id=row[1],
                trial_date=row[2],
                location=row[3],
                distance_meters=row[4],
                time_seconds=row[5],
                pool_length_meters=row[6],
                created_at=row[7],
            )
            trials.append(trial)

        logger.info(f"Retrieved {len(trials)} indoor trials from database")
        return trials

    except Exception as e:
        logger.error(f"Failed to retrieve indoor trials: {e}")
        return []


def get_indoor_trials_by_member(member_id: int) -> list[IndoorTrial]:
    """Retrieve indoor trials for a specific member."""
    try:
        db = get_db_connection()
        query = """
        SELECT id, member_id, trial_date, location, distance_meters,
               time_seconds, pool_length_meters, created_at
        FROM indoor_trials
        WHERE member_id = ?
        ORDER BY trial_date DESC
        """

        rows = db.fetch_all(query, (member_id,))
        trials = []

        for row in rows:
            trial = IndoorTrial(
                id=row[0],
                member_id=row[1],
                trial_date=row[2],
                location=row[3],
                distance_meters=row[4],
                time_seconds=row[5],
                pool_length_meters=row[6],
                created_at=row[7],
            )
            trials.append(trial)

        logger.info(f"Retrieved {len(trials)} indoor trials for member {member_id}")
        return trials

    except Exception as e:
        logger.error(f"Failed to retrieve indoor trials for member {member_id}: {e}")
        return []


def get_database_stats() -> DatabaseStats:
    """Get database statistics for dashboard display."""
    try:
        db = get_db_connection()

        # Count members
        members_count = db.fetch_one("SELECT COUNT(*) FROM members")[0]

        # Count Cooper tests
        cooper_tests_count = db.fetch_one("SELECT COUNT(*) FROM cooper_tests")[0]

        # Count indoor trials
        indoor_trials_count = db.fetch_one("SELECT COUNT(*) FROM indoor_trials")[0]

        # Get database file size
        db_size_mb = db.get_database_size()

        stats = DatabaseStats(
            total_members=members_count,
            total_cooper_tests=cooper_tests_count,
            total_indoor_trials=indoor_trials_count,
            database_size_mb=db_size_mb,
        )

        logger.info(f"Retrieved database stats: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Failed to retrieve database stats: {e}")
        return DatabaseStats(
            total_members=0,
            total_cooper_tests=0,
            total_indoor_trials=0,
            database_size_mb=0.0,
        )


def insert_member(
    name: str,
    surname: str,
    date_of_birth: date,
    contact_info: str | None,
    membership_start_date: date,
) -> int:
    """Insert a new member and return the member ID."""
    try:
        db = get_db_connection()
        # Get next ID
        max_id_result = db.fetch_one("SELECT COALESCE(MAX(id), 0) + 1 FROM members")
        member_id = max_id_result[0]

        query = """
        INSERT INTO members (id, name, surname, date_of_birth, contact_info, membership_start_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        db.execute_query(
            query,
            (
                member_id,
                name,
                surname,
                date_of_birth,
                contact_info,
                membership_start_date,
            ),
        )

        logger.info(f"Inserted new member: {name} {surname} (ID: {member_id})")
        return member_id

    except Exception as e:
        logger.error(f"Failed to insert member {name} {surname}: {e}")
        raise


def insert_cooper_test(
    member_id: int,
    test_date: date,
    diving_times: list[time],
    surface_times: list[time],
    pool_length_meters: int,
    notes: str | None = None,
) -> int:
    """Insert a new Cooper test and return the test ID."""
    try:
        db = get_db_connection()
        # Get next ID
        max_id_result = db.fetch_one(
            "SELECT COALESCE(MAX(id), 0) + 1 FROM cooper_tests"
        )
        test_id = max_id_result[0]

        query = """
        INSERT INTO cooper_tests (id, member_id, test_date, diving_times, surface_times,
                                pool_length_meters, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        db.execute_query(
            query,
            (
                test_id,
                member_id,
                test_date,
                diving_times,
                surface_times,
                pool_length_meters,
                notes,
            ),
        )

        logger.info(f"Inserted Cooper test for member {member_id} (Test ID: {test_id})")
        return test_id

    except Exception as e:
        logger.error(f"Failed to insert Cooper test for member {member_id}: {e}")
        raise


def insert_indoor_trial(
    member_id: int,
    trial_date: date,
    location: str | None,
    distance_meters: int,
    time_seconds: int | None,
    pool_length_meters: int,
) -> int:
    """Insert a new indoor trial and return the trial ID."""
    try:
        db = get_db_connection()
        # Get next ID
        max_id_result = db.fetch_one(
            "SELECT COALESCE(MAX(id), 0) + 1 FROM indoor_trials"
        )
        trial_id = max_id_result[0]

        query = """
        INSERT INTO indoor_trials (id, member_id, trial_date, location, distance_meters,
                                 time_seconds, pool_length_meters)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        db.execute_query(
            query,
            (
                trial_id,
                member_id,
                trial_date,
                location,
                distance_meters,
                time_seconds,
                pool_length_meters,
            ),
        )

        logger.info(
            f"Inserted indoor trial for member {member_id} (Trial ID: {trial_id})"
        )
        return trial_id

    except Exception as e:
        logger.error(f"Failed to insert indoor trial for member {member_id}: {e}")
        raise


def get_performance_trends_cooper(
    member_id: int | None = None,
) -> list[PerformanceTrend]:
    """Get Cooper test performance trends for visualization."""
    try:
        db = get_db_connection()

        if member_id:
            query = """
            SELECT m.name || ' ' || m.surname as member_name,
                   ct.test_date, ct.diving_times, ct.surface_times
            FROM cooper_tests ct
            JOIN members m ON ct.member_id = m.id
            WHERE ct.member_id = ?
            ORDER BY ct.test_date
            """
            rows = db.fetch_all(query, (member_id,))
        else:
            query = """
            SELECT m.name || ' ' || m.surname as member_name,
                   ct.test_date, ct.diving_times, ct.surface_times
            FROM cooper_tests ct
            JOIN members m ON ct.member_id = m.id
            ORDER BY m.id, ct.test_date
            """
            rows = db.fetch_all(query)

        # Process data into performance trends
        trends = {}

        for row in rows:
            member_name = row[0]
            test_date = row[1]
            diving_times = row[2] if row[2] else []
            surface_times = row[3] if row[3] else []

            if member_name not in trends:
                trends[member_name] = {
                    "dates": [],
                    "diving_values": [],
                    "surface_values": [],
                    "cycles_values": [],
                }

            # Calculate metrics
            total_diving_seconds = (
                sum(
                    t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000
                    for t in diving_times
                )
                if diving_times
                else 0
            )

            total_surface_seconds = (
                sum(
                    t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000
                    for t in surface_times
                )
                if surface_times
                else 0
            )

            total_cycles = min(len(diving_times), len(surface_times))

            trends[member_name]["dates"].append(test_date)
            trends[member_name]["diving_values"].append(total_diving_seconds)
            trends[member_name]["surface_values"].append(total_surface_seconds)
            trends[member_name]["cycles_values"].append(total_cycles)

        # Convert to PerformanceTrend objects
        result = []
        for member_name, data in trends.items():
            result.extend(
                [
                    PerformanceTrend(
                        member_name=member_name,
                        dates=data["dates"],
                        values=data["diving_values"],
                        metric_type="diving_time",
                    ),
                    PerformanceTrend(
                        member_name=member_name,
                        dates=data["dates"],
                        values=data["surface_values"],
                        metric_type="surface_time",
                    ),
                    PerformanceTrend(
                        member_name=member_name,
                        dates=data["dates"],
                        values=data["cycles_values"],
                        metric_type="cycles",
                    ),
                ]
            )

        logger.info(f"Generated {len(result)} Cooper test performance trends")
        return result

    except Exception as e:
        logger.error(f"Failed to get Cooper test performance trends: {e}")
        return []


def get_performance_trends_trials(
    member_id: int | None = None,
) -> list[PerformanceTrend]:
    """Get indoor trial performance trends for visualization."""
    try:
        db = get_db_connection()

        if member_id:
            query = """
            SELECT m.name || ' ' || m.surname as member_name,
                   it.trial_date, it.distance_meters, it.time_seconds
            FROM indoor_trials it
            JOIN members m ON it.member_id = m.id
            WHERE it.member_id = ?
            ORDER BY it.trial_date
            """
            rows = db.fetch_all(query, (member_id,))
        else:
            query = """
            SELECT m.name || ' ' || m.surname as member_name,
                   it.trial_date, it.distance_meters, it.time_seconds
            FROM indoor_trials it
            JOIN members m ON it.member_id = m.id
            ORDER BY m.id, it.trial_date
            """
            rows = db.fetch_all(query)

        # Process data into performance trends
        trends = {}

        for row in rows:
            member_name = row[0]
            trial_date = row[1]
            distance_meters = row[2]
            time_seconds = row[3]

            if member_name not in trends:
                trends[member_name] = {
                    "dates": [],
                    "distance_values": [],
                    "speed_values": [],
                }

            trends[member_name]["dates"].append(trial_date)
            trends[member_name]["distance_values"].append(float(distance_meters))

            # Calculate speed if time is available
            if time_seconds and time_seconds > 0:
                speed_mps = distance_meters / time_seconds
                trends[member_name]["speed_values"].append(speed_mps)
            else:
                trends[member_name]["speed_values"].append(0.0)

        # Convert to PerformanceTrend objects
        result = []
        for member_name, data in trends.items():
            result.extend(
                [
                    PerformanceTrend(
                        member_name=member_name,
                        dates=data["dates"],
                        values=data["distance_values"],
                        metric_type="distance",
                    ),
                    PerformanceTrend(
                        member_name=member_name,
                        dates=data["dates"],
                        values=data["speed_values"],
                        metric_type="speed",
                    ),
                ]
            )

        logger.info(f"Generated {len(result)} indoor trial performance trends")
        return result

    except Exception as e:
        logger.error(f"Failed to get indoor trial performance trends: {e}")
        return []
