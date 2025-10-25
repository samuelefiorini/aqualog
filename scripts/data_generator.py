"""
Data generation module for Aqualog.
Generates realistic synthetic data for Italian freediving society members.
"""

from faker import Faker
from faker.providers import BaseProvider
from typing import List, Tuple, Optional
from datetime import date, time, datetime, timedelta
import random
from loguru import logger

import sys
from pathlib import Path

# Add parent directory to path for db imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import insert_member, insert_cooper_test, insert_indoor_trial


class FreedivingProvider(BaseProvider):
    """Custom Faker provider for freediving-specific data."""

    # Italian freediving locations
    italian_pools = [
        "Piscina Comunale di Milano",
        "Centro Nuoto Torino",
        "Piscina Olimpica Roma",
        "Aquatic Center Napoli",
        "Piscina Comunale Firenze",
        "Centro Sportivo Bologna",
        "Piscina Comunale Venezia",
        "Aquatic Club Genova",
        "Centro Nuoto Palermo",
        "Piscina Comunale Bari",
        "Centro Sportivo Catania",
        "Piscina Olimpica Verona",
    ]

    # Common Italian email domains
    italian_email_domains = [
        "gmail.com",
        "libero.it",
        "virgilio.it",
        "alice.it",
        "tin.it",
        "hotmail.it",
        "yahoo.it",
        "tiscali.it",
    ]

    def italian_pool_location(self) -> str:
        """Generate an Italian pool location."""
        return self.random_element(self.italian_pools)

    def italian_email(self, first_name: str, last_name: str) -> str:
        """Generate an Italian email address."""
        domain = self.random_element(self.italian_email_domains)

        # Various email formats
        formats = [
            f"{first_name.lower()}.{last_name.lower()}@{domain}",
            f"{first_name.lower()}{last_name.lower()}@{domain}",
            f"{first_name[0].lower()}.{last_name.lower()}@{domain}",
            f"{first_name.lower()}{random.randint(1, 99)}@{domain}",
            f"{last_name.lower()}.{first_name.lower()}@{domain}",
        ]

        return self.random_element(formats)

    def diving_time(self, min_seconds: int = 10, max_seconds: int = 40) -> time:
        """Generate a realistic diving time for Cooper tests."""
        seconds = random.randint(min_seconds, max_seconds)
        return time(0, seconds // 60, seconds % 60)

    def surface_time(self, min_seconds: int = 15, max_seconds: int = 40) -> time:
        """Generate a realistic surface recovery time for Cooper tests."""
        seconds = random.randint(min_seconds, max_seconds)
        return time(0, seconds // 60, seconds % 60)

    def cooper_test_cycles(self, min_cycles: int = 12, max_cycles: int = 36) -> int:
        """Generate number of cycles for a Cooper test."""
        return random.randint(min_cycles, max_cycles)

    def pool_length(self) -> int:
        """Generate a realistic pool length."""
        return random.choice([25, 50])  # Standard pool lengths

    def freediving_distance(self, skill_level: str = "intermediate") -> int:
        """Generate realistic freediving distance based on skill level."""
        if skill_level == "beginner":
            return random.randint(25, 100)
        elif skill_level == "intermediate":
            return random.randint(75, 200)
        elif skill_level == "advanced":
            return random.randint(150, 400)
        else:
            return random.randint(50, 250)

    def freediving_time(self, distance: int, pool_length: int) -> Optional[int]:
        """Generate realistic time for a given distance (sometimes None)."""
        # 30% chance of no time recorded
        if random.random() < 0.3:
            return None

        # Calculate approximate time based on distance
        # Assume average speed of 0.8-1.5 m/s for freediving
        speed = random.uniform(0.8, 1.5)
        base_time = distance / speed

        # Add some variation and rest time between laps
        laps = distance / pool_length
        rest_time = laps * random.uniform(2, 8)  # 2-8 seconds rest per lap

        total_time = int(base_time + rest_time)
        return total_time


class DataGenerator:
    """Main data generator class for Aqualog synthetic data."""

    def __init__(self, locale: str = "it_IT"):
        """Initialize the data generator with Italian locale."""
        self.fake = Faker(locale)
        self.fake.add_provider(FreedivingProvider)

        # Skill level distribution (realistic for a freediving society)
        self.skill_levels = ["beginner", "intermediate", "advanced"]
        self.skill_weights = [
            0.4,
            0.5,
            0.1,
        ]  # 40% beginners, 50% intermediate, 10% advanced

        logger.info(f"DataGenerator initialized with locale: {locale}")

    def generate_member(self) -> Tuple[str, str, date, str, date]:
        """Generate a single member's data."""
        # Generate basic info
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()

        # Birth date: 18-65 years old
        birth_date = self.fake.date_of_birth(minimum_age=18, maximum_age=65)

        # Email
        email = self.fake.italian_email(first_name, last_name)

        # Membership start date: within last 5 years, after birth date
        min_membership_date = max(
            birth_date + timedelta(days=18 * 365),  # At least 18 years old
            date.today() - timedelta(days=5 * 365),  # Within last 5 years
        )
        max_membership_date = date.today()

        membership_date = self.fake.date_between(
            start_date=min_membership_date, end_date=max_membership_date
        )

        return first_name, last_name, birth_date, email, membership_date

    def generate_cooper_test(
        self, member_id: int, member_skill: str, test_date: Optional[date] = None
    ) -> Tuple[int, date, List[time], List[time], int, str]:
        """Generate Cooper test data for a member."""
        if test_date is None:
            # Random test date within last 2 years
            test_date = self.fake.date_between(
                start_date=date.today() - timedelta(days=730), end_date=date.today()
            )

        # Cooper test is exactly 12 minutes (720 seconds)
        # Generate cycles until we reach or exceed 720 seconds, then cut off
        COOPER_TEST_DURATION = 720  # 12 minutes in seconds

        diving_times = []
        surface_times = []
        total_time = 0
        cycle_count = 0

        # Generate cycles until we exceed 12 minutes
        while total_time < COOPER_TEST_DURATION:
            # Diving times get shorter as fatigue sets in
            fatigue_factor = 1 - (cycle_count * 0.03)  # 3% reduction per cycle

            if member_skill == "beginner":
                base_diving = random.randint(12, 25)  # 12-25 seconds for beginners
                base_surface = random.randint(25, 35)  # 25-35 seconds surface time
            elif member_skill == "intermediate":
                base_diving = random.randint(15, 30)  # 15-30 seconds for intermediate
                base_surface = random.randint(20, 35)  # 20-35 seconds surface time
            else:  # advanced
                base_diving = random.randint(18, 35)  # 18-35 seconds for advanced
                base_surface = random.randint(
                    18, 30
                )  # 18-30 seconds surface time (shorter recovery)

            # Apply fatigue
            diving_seconds = max(
                10, int(base_diving * fatigue_factor)
            )  # Minimum 10 seconds
            surface_seconds = max(
                15, int(base_surface * (1 + (cycle_count * 0.02)))
            )  # Slight increase in surface time with fatigue

            # Check if this complete cycle would fit within 12 minutes
            cycle_time = diving_seconds + surface_seconds
            if total_time + cycle_time <= COOPER_TEST_DURATION:
                # Complete cycle fits, add it
                diving_times.append(time(0, diving_seconds // 60, diving_seconds % 60))
                surface_times.append(
                    time(0, surface_seconds // 60, surface_seconds % 60)
                )
                total_time += cycle_time
                cycle_count += 1
            else:
                # This cycle would exceed 12 minutes, stop here
                break

        pool_length = self.fake.pool_length()

        # Generate notes (sometimes)
        notes = None
        if random.random() < 0.3:  # 30% chance of notes
            note_options = [
                "Buona performance generale",
                "Miglioramento rispetto al test precedente",
                "Difficoltà negli ultimi cicli",
                "Ottima tecnica di respirazione",
                "Da lavorare sulla fase di recupero",
                "Performance stabile durante tutto il test",
                "Leggera stanchezza iniziale",
            ]
            notes = random.choice(note_options)

        return member_id, test_date, diving_times, surface_times, pool_length, notes

    def generate_indoor_trial(
        self, member_id: int, member_skill: str, trial_date: Optional[date] = None
    ) -> Tuple[int, date, str, int, Optional[int], int]:
        """Generate indoor trial data for a member."""
        if trial_date is None:
            # Random trial date within last 2 years
            trial_date = self.fake.date_between(
                start_date=date.today() - timedelta(days=730), end_date=date.today()
            )

        location = self.fake.italian_pool_location()
        distance = self.fake.freediving_distance(member_skill)
        pool_length = self.fake.pool_length()
        time_seconds = self.fake.freediving_time(distance, pool_length)

        return member_id, trial_date, location, distance, time_seconds, pool_length

    def populate_database(
        self,
        num_members: int = 50,
        tests_per_member: Tuple[int, int] = (1, 5),
        trials_per_member: Tuple[int, int] = (2, 8),
        progress_callback: Optional[callable] = None,
    ) -> dict:
        """
        Populate the database with synthetic data.

        Args:
            num_members: Number of members to generate
            tests_per_member: Min and max Cooper tests per member
            trials_per_member: Min and max indoor trials per member
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with generation statistics
        """
        logger.info(f"Starting data population: {num_members} members")

        stats = {
            "members_created": 0,
            "cooper_tests_created": 0,
            "indoor_trials_created": 0,
            "errors": [],
        }

        # Generate members
        members_data = []
        for i in range(num_members):
            try:
                member_data = self.generate_member()
                skill_level = random.choices(
                    self.skill_levels, weights=self.skill_weights
                )[0]

                # Insert member
                member_id = insert_member(*member_data)
                members_data.append((member_id, skill_level))
                stats["members_created"] += 1

                if progress_callback:
                    progress_callback(
                        f"Created member {i + 1}/{num_members}: {member_data[0]} {member_data[1]}"
                    )

            except Exception as e:
                error_msg = f"Error creating member {i + 1}: {e}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)

        # Generate Cooper tests
        for member_id, skill_level in members_data:
            num_tests = random.randint(*tests_per_member)

            for j in range(num_tests):
                try:
                    test_data = self.generate_cooper_test(member_id, skill_level)
                    insert_cooper_test(*test_data)
                    stats["cooper_tests_created"] += 1

                    if progress_callback:
                        progress_callback(
                            f"Created Cooper test {j + 1}/{num_tests} for member {member_id}"
                        )

                except Exception as e:
                    error_msg = (
                        f"Error creating Cooper test for member {member_id}: {e}"
                    )
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)

        # Generate indoor trials
        for member_id, skill_level in members_data:
            num_trials = random.randint(*trials_per_member)

            for j in range(num_trials):
                try:
                    trial_data = self.generate_indoor_trial(member_id, skill_level)
                    insert_indoor_trial(*trial_data)
                    stats["indoor_trials_created"] += 1

                    if progress_callback:
                        progress_callback(
                            f"Created indoor trial {j + 1}/{num_trials} for member {member_id}"
                        )

                except Exception as e:
                    error_msg = (
                        f"Error creating indoor trial for member {member_id}: {e}"
                    )
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)

        logger.info(f"Data population completed: {stats}")
        return stats
