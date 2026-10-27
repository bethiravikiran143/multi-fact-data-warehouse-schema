"""
warehouse_schema.py
-------------------
Defines the Multi-Fact Data Warehouse Schema (Fact Constellation / Galaxy Schema)
for student academic performance, course engagement, and semester progression across departments.
"""

import sqlite3
import os

SCHEMA_DDL = """
-- ==========================================================
-- DIMENSION TABLES (Conformed Dimensions shared across facts)
-- ==========================================================

CREATE TABLE IF NOT EXISTS dim_department (
    department_key INTEGER PRIMARY KEY AUTOINCREMENT,
    dept_code TEXT UNIQUE NOT NULL,
    dept_name TEXT NOT NULL,
    hod_name TEXT NOT NULL,
    established_year INTEGER NOT NULL,
    total_faculty INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_faculty (
    faculty_key INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_id TEXT UNIQUE NOT NULL,
    faculty_name TEXT NOT NULL,
    dept_code TEXT NOT NULL,
    designation TEXT NOT NULL,
    qualification TEXT NOT NULL,
    experience_years INTEGER NOT NULL,
    FOREIGN KEY (dept_code) REFERENCES dim_department(dept_code)
);

CREATE TABLE IF NOT EXISTS dim_course (
    course_key INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT UNIQUE NOT NULL,
    course_name TEXT NOT NULL,
    dept_code TEXT NOT NULL,
    course_type TEXT NOT NULL, -- Core, Professional Elective, Open Elective, Lab
    credits INTEGER NOT NULL,
    semester_offered INTEGER NOT NULL,
    FOREIGN KEY (dept_code) REFERENCES dim_department(dept_code)
);

CREATE TABLE IF NOT EXISTS dim_time_semester (
    time_key INTEGER PRIMARY KEY, -- e.g. 202401 for 2023-24 Sem 1
    academic_year TEXT NOT NULL,  -- e.g. '2023-2024'
    semester_number INTEGER NOT NULL, -- 1 to 8
    semester_name TEXT NOT NULL,   -- 'Semester 1' .. 'Semester 8'
    semester_type TEXT NOT NULL,   -- 'Odd' or 'Even'
    year_of_study TEXT NOT NULL,   -- '1st Year', '2nd Year', '3rd Year', '4th Year'
    exam_cycle TEXT NOT NULL       -- 'Winter Exam' or 'Summer Exam'
);

CREATE TABLE IF NOT EXISTS dim_student (
    student_key INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT UNIQUE NOT NULL,
    student_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    dept_code TEXT NOT NULL,
    cohort_batch TEXT NOT NULL,     -- '2021-2025', '2022-2026', '2023-2027', '2024-2028'
    admission_type TEXT NOT NULL,   -- 'Regular', 'Lateral Entry', 'Management'
    current_year INTEGER NOT NULL,
    current_semester INTEGER NOT NULL,
    academic_status TEXT NOT NULL,  -- 'Active', 'Graduated'
    mobile_no TEXT,
    gmail_id TEXT,
    parent_mobile TEXT,
    FOREIGN KEY (dept_code) REFERENCES dim_department(dept_code)
);

-- ==========================================================
-- FACT TABLE 1: FACT_EXAM_PERFORMANCE
-- Granularity: 1 row per Student per Course per Academic Semester
-- ==========================================================

CREATE TABLE IF NOT EXISTS fact_exam_performance (
    performance_key INTEGER PRIMARY KEY AUTOINCREMENT,
    student_key INTEGER NOT NULL,
    course_key INTEGER NOT NULL,
    department_key INTEGER NOT NULL,
    time_key INTEGER NOT NULL,
    faculty_key INTEGER NOT NULL,
    internal_marks REAL NOT NULL,      -- Max 30
    external_marks REAL NOT NULL,      -- Max 70
    total_marks REAL NOT NULL,         -- Max 100
    grade_point REAL NOT NULL,         -- 0 to 10
    letter_grade TEXT NOT NULL,        -- 'O', 'A+', 'A', 'B+', 'B', 'C', 'F'
    credits_earned INTEGER NOT NULL,   -- credits or 0 if failed
    is_passed INTEGER NOT NULL,        -- 1 = Yes, 0 = No
    is_backlog INTEGER NOT NULL,       -- 1 = Yes, 0 = No
    attempt_number INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (student_key) REFERENCES dim_student(student_key),
    FOREIGN KEY (course_key) REFERENCES dim_course(course_key),
    FOREIGN KEY (department_key) REFERENCES dim_department(department_key),
    FOREIGN KEY (time_key) REFERENCES dim_time_semester(time_key),
    FOREIGN KEY (faculty_key) REFERENCES dim_faculty(faculty_key)
);

-- ==========================================================
-- FACT TABLE 2: FACT_ATTENDANCE_ENGAGEMENT
-- Granularity: 1 row per Student per Course per Academic Semester
-- ==========================================================

CREATE TABLE IF NOT EXISTS fact_attendance_engagement (
    attendance_key INTEGER PRIMARY KEY AUTOINCREMENT,
    student_key INTEGER NOT NULL,
    course_key INTEGER NOT NULL,
    department_key INTEGER NOT NULL,
    time_key INTEGER NOT NULL,
    total_classes INTEGER NOT NULL,
    classes_attended INTEGER NOT NULL,
    attendance_pct REAL NOT NULL,
    is_condonation_risk INTEGER NOT NULL, -- 1 if 65 <= pct < 75
    is_detained_risk INTEGER NOT NULL,    -- 1 if pct < 65
    assignments_submitted INTEGER NOT NULL,
    assignments_total INTEGER NOT NULL,
    assignment_score_pct REAL NOT NULL,
    FOREIGN KEY (student_key) REFERENCES dim_student(student_key),
    FOREIGN KEY (course_key) REFERENCES dim_course(course_key),
    FOREIGN KEY (department_key) REFERENCES dim_department(department_key),
    FOREIGN KEY (time_key) REFERENCES dim_time_semester(time_key)
);

-- ==========================================================
-- FACT TABLE 3: FACT_SEMESTER_SUMMARY (Periodic Snapshot Fact)
-- Granularity: 1 row per Student per Academic Semester
-- ==========================================================

CREATE TABLE IF NOT EXISTS fact_semester_summary (
    summary_key INTEGER PRIMARY KEY AUTOINCREMENT,
    student_key INTEGER NOT NULL,
    department_key INTEGER NOT NULL,
    time_key INTEGER NOT NULL,
    credits_registered INTEGER NOT NULL,
    credits_earned INTEGER NOT NULL,
    sgpa REAL NOT NULL,
    cgpa REAL NOT NULL,
    backlogs_in_sem INTEGER NOT NULL,
    total_cumulative_backlogs INTEGER NOT NULL,
    sem_attendance_avg REAL NOT NULL,
    risk_level TEXT NOT NULL, -- 'Low', 'Medium', 'High'
    academic_standing TEXT NOT NULL, -- 'Good Standing', 'Academic Warning', 'Critical Probation'
    FOREIGN KEY (student_key) REFERENCES dim_student(student_key),
    FOREIGN KEY (department_key) REFERENCES dim_department(department_key),
    FOREIGN KEY (time_key) REFERENCES dim_time_semester(time_key)
);

-- ==========================================================
-- INDEXES FOR FAST OLAP QUERIES & DRILL-DOWNS
-- ==========================================================

CREATE INDEX IF NOT EXISTS idx_fep_student ON fact_exam_performance(student_key);
CREATE INDEX IF NOT EXISTS idx_fep_dept ON fact_exam_performance(department_key);
CREATE INDEX IF NOT EXISTS idx_fep_course ON fact_exam_performance(course_key);
CREATE INDEX IF NOT EXISTS idx_fep_time ON fact_exam_performance(time_key);

CREATE INDEX IF NOT EXISTS idx_fae_student ON fact_attendance_engagement(student_key);
CREATE INDEX IF NOT EXISTS idx_fae_dept ON fact_attendance_engagement(department_key);
CREATE INDEX IF NOT EXISTS idx_fae_course ON fact_attendance_engagement(course_key);
CREATE INDEX IF NOT EXISTS idx_fae_time ON fact_attendance_engagement(time_key);

CREATE INDEX IF NOT EXISTS idx_fss_student ON fact_semester_summary(student_key);
CREATE INDEX IF NOT EXISTS idx_fss_dept ON fact_semester_summary(department_key);
CREATE INDEX IF NOT EXISTS idx_fss_time ON fact_semester_summary(time_key);
"""

def init_warehouse_db(db_path: str):
    """Initializes the SQLite database with the Multi-Fact Schema."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA_DDL)
    conn.commit()
    conn.close()
    print(f"[OK] Multi-Fact Data Warehouse schema initialized successfully at: {db_path}")

if __name__ == "__main__":
    default_db = os.path.join(os.path.dirname(__file__), "..", "data", "warehouse", "academic_dw.db")
    init_warehouse_db(default_db)
