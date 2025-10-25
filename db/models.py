"""
Data models for Aqualog freediving management system.
Defines dataclasses for type safety and data validation.
"""

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import List, Optional


@dataclass
class Member:
    """Represents a freediving society member."""

    id: int
    name: str
    surname: str
    date_of_birth: date
    contact_info: str | None
    membership_start_date: date
    created_at: datetime

    @property
    def full_name(self) -> str:
        """Get member's full name."""
        return f"{self.name} {self.surname}"

    @property
    def age(self) -> int:
        """Calculate member's current age."""
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )


@dataclass
class CooperTest:
    """Represents a 12-minute Cooper test session with diving/surface cycles."""

    id: int
    member_id: int
    test_date: date
    diving_times: list[time]  # Array of diving times for each cycle
    surface_times: list[time]  # Array of surface times for each cycle
    pool_length_meters: int  # Swimming pool length (e.g., 25m, 50m)
    notes: str | None
    created_at: datetime

    @property
    def total_cycles(self) -> int:
        """Get total number of dive/surface cycles."""
        return min(len(self.diving_times), len(self.surface_times))

    @property
    def total_diving_time_seconds(self) -> float:
        """Calculate total diving time in seconds."""
        return sum(
            t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000
            for t in self.diving_times
        )

    @property
    def total_surface_time_seconds(self) -> float:
        """Calculate total surface time in seconds."""
        return sum(
            t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000
            for t in self.surface_times
        )

    @property
    def average_diving_time_seconds(self) -> float:
        """Calculate average diving time per cycle in seconds."""
        if not self.diving_times:
            return 0.0
        return self.total_diving_time_seconds / len(self.diving_times)

    @property
    def estimated_distance_meters(self) -> float:
        """Estimate total distance covered based on diving times and pool length."""
        # Rough estimation: assume average swimming speed during diving phases
        # This is a simplified calculation for visualization purposes
        avg_speed_mps = 1.2  # meters per second (conservative estimate)
        return self.total_diving_time_seconds * avg_speed_mps


@dataclass
class IndoorTrial:
    """Represents an indoor training trial session."""

    id: int
    member_id: int
    trial_date: date
    location: str | None
    distance_meters: int
    time_seconds: int | None  # Optional: sometimes only distance is tracked
    pool_length_meters: int  # Swimming pool length (e.g., 25m, 50m)
    created_at: datetime

    @property
    def laps_completed(self) -> float:
        """Calculate number of pool laps completed."""
        return self.distance_meters / self.pool_length_meters

    @property
    def average_speed_mps(self) -> float | None:
        """Calculate average speed in meters per second if time is available."""
        if self.time_seconds and self.time_seconds > 0:
            return self.distance_meters / self.time_seconds
        return None

    @property
    def pace_per_100m(self) -> float | None:
        """Calculate pace per 100 meters in seconds if time is available."""
        if self.time_seconds and self.distance_meters > 0:
            return (self.time_seconds / self.distance_meters) * 100
        return None


@dataclass
class DatabaseStats:
    """Represents database statistics for dashboard display."""

    total_members: int
    total_cooper_tests: int
    total_indoor_trials: int
    database_size_mb: float

    @property
    def total_tests_and_trials(self) -> int:
        """Get combined total of all tests and trials."""
        return self.total_cooper_tests + self.total_indoor_trials


@dataclass
class PerformanceTrend:
    """Represents performance trend data for visualizations."""

    member_name: str
    dates: list[date]
    values: list[float]
    metric_type: str  # e.g., "distance", "diving_time", "cycles"

    @property
    def data_points(self) -> int:
        """Get number of data points in the trend."""
        return min(len(self.dates), len(self.values))

    @property
    def latest_value(self) -> float | None:
        """Get the most recent performance value."""
        return self.values[-1] if self.values else None

    @property
    def improvement_trend(self) -> str | None:
        """Determine if performance is improving, declining, or stable."""
        if len(self.values) < 2:
            return None

        recent_avg = sum(self.values[-3:]) / min(3, len(self.values))
        older_avg = sum(self.values[:3]) / min(3, len(self.values))

        if recent_avg > older_avg * 1.05:  # 5% improvement threshold
            return "improving"
        elif recent_avg < older_avg * 0.95:  # 5% decline threshold
            return "declining"
        else:
            return "stable"


@dataclass
class DashboardUser:
    """Represents a dashboard user with authentication and role information."""

    id: int
    username: str
    password_hash: str
    salt: str
    email: Optional[str]
    full_name: Optional[str]
    role: str  # 'admin' or 'user'
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    login_attempts: int
    locked_until: Optional[datetime]

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == "admin"

    @property
    def is_locked(self) -> bool:
        """Check if user account is currently locked."""
        if self.locked_until is None:
            return False
        return datetime.now() < self.locked_until

    @property
    def can_write(self) -> bool:
        """Check if user has write permissions."""
        return self.is_admin and self.is_active

    @property
    def can_read(self) -> bool:
        """Check if user has read permissions."""
        return self.is_active

    @property
    def display_name(self) -> str:
        """Get display name for the user."""
        return self.full_name or self.username
