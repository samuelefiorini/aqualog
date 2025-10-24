-- Aqualog Database Schema
-- Freediving Society Management System

-- Members table - stores information about freediving society members
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    contact_info VARCHAR(255),
    membership_start_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cooper tests table - stores 12-minute Cooper test results with diving/surface cycles
CREATE TABLE IF NOT EXISTS cooper_tests (
    id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL,
    test_date DATE NOT NULL,
    diving_times TIME[] NOT NULL,     -- Array of diving times for each cycle
    surface_times TIME[] NOT NULL,    -- Array of surface times for each cycle
    pool_length_meters INTEGER NOT NULL, -- Swimming pool length (e.g., 25m, 50m)
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id)
);

-- Indoor trials table - stores indoor training session results
CREATE TABLE IF NOT EXISTS indoor_trials (
    id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL,
    trial_date DATE NOT NULL,
    location VARCHAR(255),
    distance_meters INTEGER NOT NULL,
    time_seconds INTEGER,  -- Optional: sometimes only distance is tracked
    pool_length_meters INTEGER NOT NULL, -- Swimming pool length (e.g., 25m, 50m)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_cooper_tests_member_date ON cooper_tests(member_id, test_date);
CREATE INDEX IF NOT EXISTS idx_indoor_trials_member_date ON indoor_trials(member_id, trial_date);
CREATE INDEX IF NOT EXISTS idx_members_name ON members(surname, name);
CREATE INDEX IF NOT EXISTS idx_members_membership_date ON members(membership_start_date);