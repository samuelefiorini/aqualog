# Requirements Document

## Introduction

Aqualog is an internal web application for a small Italian freediving society to manage and visualize training and test data. The system will provide a clean, production-ready solution using Streamlit for the web interface, DuckDB for data storage, and synthetic data generation capabilities using Faker. The application will serve as a comprehensive tool for tracking member information, Cooper test results, and indoor training trials with data visualization capabilities.

## Requirements

### Requirement 1

**User Story:** As a freediving society administrator, I want a secure login system, so that only authorized personnel can access the member and training data.

#### Acceptance Criteria

1. WHEN a user accesses the application THEN the system SHALL display a login page as the first interface
2. WHEN a user enters valid credentials THEN the system SHALL grant access to the main application
3. WHEN a user enters invalid credentials THEN the system SHALL display an error message and remain on the login page
4. IF no authentication backend is available THEN the system SHALL use basic credentials stored in configuration files or environment variables

### Requirement 2

**User Story:** As a freediving society administrator, I want a landing dashboard, so that I can quickly view key metrics about our organization.

#### Acceptance Criteria

1. WHEN a user successfully logs in THEN the system SHALL display a landing page with key performance indicators
2. WHEN the landing page loads THEN the system SHALL display the total number of registered members
3. WHEN the landing page loads THEN the system SHALL display the total number of tests and trials recorded
4. WHEN the landing page loads THEN the system SHALL display the current database file size
5. WHEN the landing page loads THEN the system SHALL display a friendly welcome message

### Requirement 3

**User Story:** As a freediving society administrator, I want to view member information, so that I can access the complete registry of society members.

#### Acceptance Criteria

1. WHEN a user navigates to the members page THEN the system SHALL display a read-only table of all registered members
2. WHEN viewing the members table THEN the system SHALL include member ID, name, surname, date of birth, contact information, and membership start date
3. WHEN viewing the members table THEN the system SHALL provide sorting capabilities for all columns
4. WHEN viewing the members table THEN the system SHALL provide search functionality to filter members
5. WHEN the members data is requested THEN the system SHALL use caching to optimize database performance

### Requirement 4

**User Story:** As a freediving coach, I want to visualize Cooper test results, so that I can track member performance trends over time.

#### Acceptance Criteria

1. WHEN a user navigates to the Cooper tests page THEN the system SHALL display performance trend visualizations
2. WHEN viewing Cooper test data THEN the system SHALL show average distance over time per member
3. WHEN viewing Cooper test data THEN the system SHALL display diving time versus surface time relationships for individual cycles
4. WHEN viewing Cooper test data THEN the system SHALL show performance patterns across multiple dive/surface cycles within each 12-minute session
4. WHEN Cooper test visualizations are requested THEN the system SHALL use cached data for optimal performance
5. WHEN displaying test results THEN the system SHALL include test ID, member ID, date, diving times array, surface times array, pool length in meters, and notes

### Requirement 5

**User Story:** As a freediving coach, I want to visualize indoor trial results, so that I can analyze training session effectiveness and member progress.

#### Acceptance Criteria

1. WHEN a user navigates to the indoor trials page THEN the system SHALL display performance trend visualizations
2. WHEN viewing indoor trial data THEN the system SHALL show distance versus time plots
3. WHEN viewing indoor trial data THEN the system SHALL display performance trends over time
4. WHEN indoor trial visualizations are requested THEN the system SHALL use cached data for optimal performance
5. WHEN displaying trial results THEN the system SHALL include trial ID, member ID, date, location, distance in meters, optional time in seconds, and pool length in meters

### Requirement 6

**User Story:** As a system administrator, I want a robust database system, so that all member and training data is reliably stored and accessible.

#### Acceptance Criteria

1. WHEN the system initializes THEN the database SHALL be implemented using DuckDB as a single .duckdb file
2. WHEN the database is created THEN it SHALL contain three tables: members, cooper_tests, and indoor_trials
3. WHEN storing member data THEN the members table SHALL include id, name, surname, date_of_birth, contact_info, and membership_start_date
4. WHEN storing Cooper test data THEN the cooper_tests table SHALL include id, member_id, date, diving_times TIME array, surface_times TIME array, pool_length_meters, and notes
5. WHEN storing indoor trial data THEN the indoor_trials table SHALL include id, member_id, date, location, distance_meters, optional time_seconds, and pool_length_meters
6. WHEN relating test and trial data THEN the system SHALL use foreign keys (member_id) to maintain referential integrity

### Requirement 7

**User Story:** As a system administrator, I want synthetic data generation capabilities, so that the system can be tested and demonstrated with realistic data.

#### Acceptance Criteria

1. WHEN synthetic data is needed THEN the system SHALL provide a standalone script using Faker library
2. WHEN the data generation script runs THEN it SHALL create realistic member profiles appropriate for freediving athletes
3. WHEN the data generation script runs THEN it SHALL create plausible Cooper test results with consistent performance patterns
4. WHEN the data generation script runs THEN it SHALL create realistic indoor trial data with appropriate time and distance relationships
5. WHEN the populate script is executed THEN it SHALL be runnable as a CLI command (python scripts/populate_db.py)

### Requirement 8

**User Story:** As a developer, I want a modern, maintainable codebase, so that the system can be easily developed, tested, and deployed.

#### Acceptance Criteria

1. WHEN the project is structured THEN it SHALL use Python 3.13 as the runtime version
2. WHEN managing dependencies THEN the system SHALL use uv for environment and package management
3. WHEN code quality is enforced THEN the system SHALL use ruff for linting and formatting
4. WHEN code is committed THEN pre-commit hooks SHALL run ruff and requirements compilation
5. WHEN functions are defined THEN they SHALL include mandatory type hints
6. WHEN the code is written THEN it SHALL be PEP8-compliant and well-organized
7. WHEN database operations are performed THEN they SHALL be centralized in dedicated query modules
8. WHEN the application runs THEN Streamlit pages SHALL use st.cache_data for database reads

### Requirement 9

**User Story:** As a system administrator, I want containerized deployment options, so that the application can be easily deployed and scaled.

#### Acceptance Criteria

1. WHEN the application is containerized THEN it SHALL include a working Dockerfile
2. WHEN the Docker container runs THEN it SHALL expose the Streamlit app on port 8501
3. WHEN building the container THEN it SHALL be buildable with "docker build -t freedive_app ."
4. WHEN running the container THEN it SHALL be executable with "docker run -p 8501:8501 freedive_app"
5. WHEN the application starts THEN it SHALL be launchable with "uv run streamlit run app/main.py"