"""
analytics_queries.py
--------------------
Provides OLAP queries, drill-down aggregations, and multi-fact cross-joins
for the Student Performance Data Warehouse.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "warehouse", "academic_dw.db")

def ensure_schema_migrations(conn):
    """Auto-migrates and patches missing contact columns in dim_student if connected to legacy DB."""
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(dim_student)")
        columns = [row[1] for row in cur.fetchall()]
        if columns and "mobile_no" not in columns:
            cur.execute("ALTER TABLE dim_student ADD COLUMN mobile_no TEXT")
            cur.execute("UPDATE dim_student SET mobile_no = '+91 98' || (ABS(RANDOM()) % 90000000 + 10000000)")
        if columns and "gmail_id" not in columns:
            cur.execute("ALTER TABLE dim_student ADD COLUMN gmail_id TEXT")
            cur.execute("UPDATE dim_student SET gmail_id = LOWER(SUBSTR(student_name, 1, INSTR(student_name || ' ', ' ') - 1)) || '.' || LOWER(roll_no) || '@gmail.com'")
        if columns and "parent_mobile" not in columns:
            cur.execute("ALTER TABLE dim_student ADD COLUMN parent_mobile TEXT")
            cur.execute("UPDATE dim_student SET parent_mobile = '+91 94' || (ABS(RANDOM()) % 90000000 + 10000000)")
        conn.commit()
    except Exception:
        pass

def get_connection(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    ensure_schema_migrations(conn)
    return conn

def get_department_overview(db_path: str = DB_PATH):
    """
    Roll-up aggregation of KPIs at the Department level using Kimball 'Drill-Across' technique:
    Aggregates Fact_Semester_Summary and Fact_Exam_Performance in separate CTEs
    to prevent fact table cartesian product fanning.
    """
    query = """
    WITH dept_students AS (
        SELECT dept_code, COUNT(student_key) AS total_students
        FROM dim_student
        GROUP BY dept_code
    ),
    dept_summary_metrics AS (
        SELECT 
            d.dept_code,
            ROUND(AVG(fss.sgpa), 2) AS avg_sgpa,
            ROUND(AVG(fss.sem_attendance_avg), 1) AS avg_attendance,
            SUM(CASE WHEN fss.risk_level = 'High' THEN 1 ELSE 0 END) AS high_risk_instances
        FROM fact_semester_summary fss
        JOIN dim_department d ON fss.department_key = d.department_key
        GROUP BY d.dept_code
    ),
    dept_exam_metrics AS (
        SELECT 
            d.dept_code,
            COUNT(fep.performance_key) AS total_exams,
            ROUND(SUM(CASE WHEN fep.is_passed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(fep.performance_key), 1) AS overall_pass_rate,
            ROUND(AVG(fep.total_marks), 1) AS avg_marks
        FROM fact_exam_performance fep
        JOIN dim_department d ON fep.department_key = d.department_key
        GROUP BY d.dept_code
    )
    SELECT 
        d.dept_code,
        d.dept_name,
        d.hod_name,
        ds.total_students,
        dsm.avg_sgpa,
        dsm.avg_attendance,
        dem.overall_pass_rate,
        dem.avg_marks,
        dsm.high_risk_instances
    FROM dim_department d
    LEFT JOIN dept_students ds ON d.dept_code = ds.dept_code
    LEFT JOIN dept_summary_metrics dsm ON d.dept_code = dsm.dept_code
    LEFT JOIN dept_exam_metrics dem ON d.dept_code = dem.dept_code
    ORDER BY dsm.avg_sgpa DESC;
    """
    conn = get_connection(db_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_cohort_progression(dept_filter: str = "ALL", db_path: str = DB_PATH):
    """Tracks SGPA and attendance across semesters for cohorts."""
    dept_clause = "" if dept_filter == "ALL" else f"AND d.dept_code = '{dept_filter}'"
    query = f"""
    SELECT 
        s.cohort_batch,
        t.semester_number,
        t.semester_name,
        ROUND(AVG(fss.sgpa), 2) AS avg_sgpa,
        ROUND(AVG(fss.sem_attendance_avg), 1) AS avg_attendance,
        SUM(fss.backlogs_in_sem) AS total_backlogs,
        COUNT(DISTINCT s.student_key) AS student_count
    FROM fact_semester_summary fss
    JOIN dim_student s ON fss.student_key = s.student_key
    JOIN dim_department d ON fss.department_key = d.department_key
    JOIN dim_time_semester t ON fss.time_key = t.time_key
    WHERE 1=1 {dept_clause}
    GROUP BY s.cohort_batch, t.semester_number, t.semester_name
    ORDER BY s.cohort_batch, t.semester_number;
    """
    conn = get_connection(db_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_multi_fact_correlation(dept_filter: str = "ALL", cohort_filter: str = "ALL", db_path: str = DB_PATH):
    """
    Multi-Fact Cross-Join (Galaxy Schema Query):
    Combines Fact_Exam_Performance with Fact_Attendance_Engagement
    via conformed dimensions Dim_Student, Dim_Course, and Dim_Time_Semester.
    """
    conditions = []
    if dept_filter != "ALL":
        conditions.append(f"d.dept_code = '{dept_filter}'")
    if cohort_filter != "ALL":
        conditions.append(f"s.cohort_batch = '{cohort_filter}'")
    where_sql = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    query = f"""
    SELECT 
        s.roll_no,
        s.student_name,
        d.dept_code,
        s.cohort_batch,
        c.course_code,
        c.course_name,
        c.course_type,
        t.semester_name,
        -- Fact 1 Measures (Exam Performance)
        fep.internal_marks,
        fep.external_marks,
        fep.total_marks,
        fep.grade_point,
        fep.letter_grade,
        fep.is_passed,
        fep.is_backlog,
        -- Fact 2 Measures (Attendance & Engagement)
        fae.total_classes,
        fae.classes_attended,
        fae.attendance_pct,
        fae.is_condonation_risk,
        fae.is_detained_risk,
        fae.assignment_score_pct,
        -- Faculty
        f.faculty_name
    FROM fact_exam_performance fep
    JOIN fact_attendance_engagement fae 
        ON fep.student_key = fae.student_key 
        AND fep.course_key = fae.course_key 
        AND fep.time_key = fae.time_key
    JOIN dim_student s ON fep.student_key = s.student_key
    JOIN dim_department d ON fep.department_key = d.department_key
    JOIN dim_course c ON fep.course_key = c.course_key
    JOIN dim_time_semester t ON fep.time_key = t.time_key
    JOIN dim_faculty f ON fep.faculty_key = f.faculty_key
    {where_sql}
    LIMIT 2000;
    """
    conn = get_connection(db_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_course_difficulty_analysis(dept_filter: str = "ALL", db_path: str = DB_PATH):
    """Analyzes course-level performance and fail rates across departments."""
    dept_clause = "" if dept_filter == "ALL" else f"WHERE d.dept_code = '{dept_filter}'"
    query = f"""
    SELECT 
        c.course_code,
        c.course_name,
        d.dept_code,
        c.course_type,
        c.semester_offered,
        COUNT(fep.performance_key) AS enrollments,
        ROUND(AVG(fep.total_marks), 1) AS avg_marks,
        ROUND(AVG(fae.attendance_pct), 1) AS avg_attendance,
        ROUND(SUM(CASE WHEN fep.is_passed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(fep.performance_key), 1) AS pass_percentage,
        SUM(fep.is_backlog) AS backlog_count
    FROM fact_exam_performance fep
    JOIN fact_attendance_engagement fae 
        ON fep.student_key = fae.student_key 
        AND fep.course_key = fae.course_key 
        AND fep.time_key = fae.time_key
    JOIN dim_course c ON fep.course_key = c.course_key
    JOIN dim_department d ON fep.department_key = d.department_key
    {dept_clause}
    GROUP BY c.course_code, c.course_name, d.dept_code, c.course_type, c.semester_offered
    ORDER BY pass_percentage ASC;
    """
    conn = get_connection(db_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_at_risk_students(dept_filter: str = "ALL", risk_filter: str = "ALL", db_path: str = DB_PATH):
    """Early Warning Identification of At-Risk Students."""
    conditions = []
    if dept_filter != "ALL":
        conditions.append(f"d.dept_code = '{dept_filter}'")
    if risk_filter != "ALL":
        conditions.append(f"fss.risk_level = '{risk_filter}'")
    where_sql = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    query = f"""
    SELECT 
        s.roll_no,
        s.student_name,
        d.dept_code,
        s.cohort_batch,
        t.semester_name,
        fss.sgpa,
        fss.cgpa,
        fss.sem_attendance_avg,
        fss.backlogs_in_sem,
        fss.total_cumulative_backlogs,
        fss.risk_level,
        fss.academic_standing
    FROM fact_semester_summary fss
    JOIN dim_student s ON fss.student_key = s.student_key
    JOIN dim_department d ON fss.department_key = d.department_key
    JOIN dim_time_semester t ON fss.time_key = t.time_key
    {where_sql}
    ORDER BY fss.backlogs_in_sem DESC, fss.sem_attendance_avg ASC;
    """
    conn = get_connection(db_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_student_360_profile(roll_no: str, db_path: str = DB_PATH):
    """Fetches complete academic transcript, progression, and multi-fact breakdown for a single student."""
    conn = get_connection(db_path)
    
    # 1. Student metadata
    stu_df = pd.read_sql(f"""
        SELECT s.*, d.dept_name, d.hod_name 
        FROM dim_student s
        JOIN dim_department d ON s.dept_code = d.dept_code
        WHERE s.roll_no = '{roll_no}'
    """, conn)
    
    if stu_df.empty:
        conn.close()
        return None, None, None

    # 2. Semester progression (Fact_Semester_Summary)
    sem_df = pd.read_sql(f"""
        SELECT 
            t.semester_number,
            t.semester_name,
            t.academic_year,
            fss.sgpa,
            fss.cgpa,
            fss.credits_registered,
            fss.credits_earned,
            fss.sem_attendance_avg,
            fss.backlogs_in_sem,
            fss.risk_level,
            fss.academic_standing
        FROM fact_semester_summary fss
        JOIN dim_student s ON fss.student_key = s.student_key
        JOIN dim_time_semester t ON fss.time_key = t.time_key
        WHERE s.roll_no = '{roll_no}'
        ORDER BY t.semester_number ASC
    """, conn)

    # 3. Course breakdown across both Fact tables
    courses_df = pd.read_sql(f"""
        SELECT 
            t.semester_name,
            c.course_code,
            c.course_name,
            c.credits,
            c.course_type,
            fep.internal_marks,
            fep.external_marks,
            fep.total_marks,
            fep.grade_point,
            fep.letter_grade,
            fep.is_passed,
            fae.total_classes,
            fae.classes_attended,
            fae.attendance_pct,
            fae.assignment_score_pct,
            fac.faculty_name
        FROM fact_exam_performance fep
        JOIN fact_attendance_engagement fae 
            ON fep.student_key = fae.student_key 
            AND fep.course_key = fae.course_key 
            AND fep.time_key = fae.time_key
        JOIN dim_student s ON fep.student_key = s.student_key
        JOIN dim_course c ON fep.course_key = c.course_key
        JOIN dim_time_semester t ON fep.time_key = t.time_key
        JOIN dim_faculty fac ON fep.faculty_key = fac.faculty_key
        WHERE s.roll_no = '{roll_no}'
        ORDER BY t.semester_number, c.course_code
    """, conn)

    conn.close()
    return stu_df.iloc[0].to_dict(), sem_df, courses_df

def get_warehouse_storage_metrics(db_path: str = DB_PATH):
    """Retrieves table row counts and schema metadata."""
    conn = get_connection(db_path)
    tables = [
        "dim_department", "dim_faculty", "dim_course", "dim_time_semester", "dim_student",
        "fact_exam_performance", "fact_attendance_engagement", "fact_semester_summary"
    ]
    counts = {}
    for tbl in tables:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        counts[tbl] = cur.fetchone()[0]
    conn.close()
    return counts

# ==========================================================
# HOD PORTAL & ATTENDANCE ALERT ENGINE
# ==========================================================

def get_hod_department_info(dept_code: str, db_path: str = DB_PATH):
    """Fetches department profile and HOD details."""
    conn = get_connection(db_path)
    query = f"""
    SELECT 
        d.department_key,
        d.dept_code,
        d.dept_name,
        d.hod_name,
        d.established_year,
        d.total_faculty,
        COUNT(DISTINCT s.student_key) AS total_enrolled_students
    FROM dim_department d
    LEFT JOIN dim_student s ON d.dept_code = s.dept_code
    WHERE d.dept_code = '{dept_code}'
    GROUP BY d.dept_code;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[0].to_dict() if not df.empty else None

def get_hod_attendance_alerts(dept_code: str = "ALL", severity_filter: str = "ALL", db_path: str = DB_PATH):
    """
    Generates actionable 'Warm Alerts' and 'Detention Notices' for HODs
    identifying students with attendance below mandatory university limits (<75% and <65%).
    Computes recovery classes required to reach 75%.
    """
    dept_clause = "" if dept_code == "ALL" else f"AND d.dept_code = '{dept_code}'"
    conn = get_connection(db_path)

    query = f"""
    SELECT 
        s.student_key,
        s.roll_no,
        s.student_name,
        s.mobile_no,
        s.gmail_id,
        s.parent_mobile,
        d.dept_code,
        d.dept_name,
        d.hod_name,
        s.cohort_batch,
        s.current_semester,
        c.course_code,
        c.course_name,
        c.course_type,
        t.semester_name,
        fae.total_classes,
        fae.classes_attended,
        (fae.total_classes - fae.classes_attended) AS classes_missed,
        fae.attendance_pct,
        fae.is_condonation_risk,
        fae.is_detained_risk,
        fep.internal_marks,
        fep.grade_point,
        fac.faculty_name
    FROM fact_attendance_engagement fae
    JOIN dim_student s ON fae.student_key = s.student_key
    JOIN dim_department d ON fae.department_key = d.department_key
    JOIN dim_course c ON fae.course_key = c.course_key
    JOIN dim_time_semester t ON fae.time_key = t.time_key
    LEFT JOIN fact_exam_performance fep 
        ON fae.student_key = fep.student_key 
        AND fae.course_key = fep.course_key 
        AND fae.time_key = fep.time_key
    LEFT JOIN dim_faculty fac ON fep.faculty_key = fac.faculty_key
    WHERE fae.attendance_pct < 75.0 {dept_clause}
    ORDER BY fae.attendance_pct ASC, s.roll_no ASC;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        return df

    # Calculate consecutive classes needed to reach 75%
    # Formula: (Attended + x) / (Total + x) >= 0.75  =>  x >= 3*Total - 4*Attended
    def calc_needed(row):
        tot = row["total_classes"]
        att = row["classes_attended"]
        needed = (3 * tot) - (4 * att)
        return max(0, int(needed))

    df["classes_needed_for_75"] = df.apply(calc_needed, axis=1)

    # Classify Alert Category
    def classify_alert(pct):
        if pct < 65.0:
            return "🚨 Critical Detention Alert (<65%)"
        else:
            return "⚠️ Condonation Warm Alert (65-75%)"

    df["alert_level"] = df["attendance_pct"].apply(classify_alert)

    if severity_filter == "Critical":
        df = df[df["attendance_pct"] < 65.0]
    elif severity_filter == "Condonation":
        df = df[(df["attendance_pct"] >= 65.0) & (df["attendance_pct"] < 75.0)]

    return df

def get_student_aggregate_attendance_alerts(dept_code: str = "ALL", db_path: str = DB_PATH):
    """
    Student-level aggregate attendance warning across all subjects in current semester.
    """
    dept_clause = "" if dept_code == "ALL" else f"AND d.dept_code = '{dept_code}'"
    conn = get_connection(db_path)

    query = f"""
    SELECT 
        s.roll_no,
        s.student_name,
        s.mobile_no,
        s.gmail_id,
        s.parent_mobile,
        d.dept_code,
        d.hod_name,
        s.cohort_batch,
        s.current_semester,
        COUNT(fae.course_key) AS subjects_enrolled,
        SUM(fae.total_classes) AS total_institutional_classes,
        SUM(fae.classes_attended) AS total_classes_attended,
        ROUND(AVG(fae.attendance_pct), 1) AS overall_attendance_pct,
        SUM(CASE WHEN fae.attendance_pct < 65.0 THEN 1 ELSE 0 END) AS detained_courses_count,
        SUM(CASE WHEN fae.attendance_pct >= 65.0 AND fae.attendance_pct < 75.0 THEN 1 ELSE 0 END) AS condonation_courses_count
    FROM fact_attendance_engagement fae
    JOIN dim_student s ON fae.student_key = s.student_key
    JOIN dim_department d ON fae.department_key = d.department_key
    WHERE 1=1 {dept_clause}
    GROUP BY s.roll_no, s.student_name, s.mobile_no, s.gmail_id, s.parent_mobile, d.dept_code, d.hod_name, s.cohort_batch, s.current_semester
    HAVING overall_attendance_pct < 75.0
    ORDER BY overall_attendance_pct ASC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ==========================================================
# STUDENT ADMINISTRATION: ADMISSION & MODIFICATION ENGINE
# ==========================================================

def add_new_student_to_warehouse(student_data: dict, db_path: str = DB_PATH):
    """
    Enrolls/Joins a new student directly into the Multi-Fact Data Warehouse.
    1. Inserts student into Dim_Student (generates surrogate key).
    2. Enrolls student in department courses for current semester in Fact_Attendance and Fact_Exam.
    3. Initializes periodic snapshot in Fact_Semester_Summary.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    roll_no = student_data["roll_no"].strip().upper()
    
    # Check duplicate
    cursor.execute("SELECT student_key FROM dim_student WHERE roll_no = ?", (roll_no,))
    if cursor.fetchone():
        conn.close()
        return False, f"Student with Roll Number '{roll_no}' already exists in the Data Warehouse!"

    # Get department_key
    cursor.execute("SELECT department_key FROM dim_department WHERE dept_code = ?", (student_data["dept_code"],))
    dept_row = cursor.fetchone()
    if not dept_row:
        conn.close()
        return False, f"Invalid Department Code: {student_data['dept_code']}"
    dept_key = dept_row[0]

    # Insert into Dim_Student
    mob = student_data.get("mobile_no", f"+91 98{abs(hash(roll_no)) % 90000000 + 10000000}")
    gmail = student_data.get("gmail_id", f"{student_data['student_name'].split()[0].lower()}.{roll_no.lower()}@gmail.com")
    pmob = student_data.get("parent_mobile", f"+91 94{abs(hash(roll_no + 'parent')) % 90000000 + 10000000}")

    cursor.execute("""
        INSERT INTO dim_student (
            roll_no, student_name, gender, dept_code, cohort_batch, 
            admission_type, current_year, current_semester, academic_status,
            mobile_no, gmail_id, parent_mobile
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        roll_no,
        student_data["student_name"].strip(),
        student_data["gender"],
        student_data["dept_code"],
        student_data["cohort_batch"],
        student_data["admission_type"],
        student_data["current_year"],
        student_data["current_semester"],
        student_data.get("academic_status", "Active"),
        mob,
        gmail,
        pmob
    ))
    new_student_key = cursor.lastrowid

    # Determine time_key based on cohort start year & current semester
    # Cohort format: "YYYY-YYYY"
    try:
        start_year = int(student_data["cohort_batch"][:4])
    except Exception:
        start_year = 2024
    sem_no = int(student_data["current_semester"])
    time_key = int(f"{start_year + (sem_no - 1) // 2}{sem_no:02d}")

    # Ensure time_key exists in dim_time_semester
    cursor.execute("SELECT time_key FROM dim_time_semester WHERE time_key = ?", (time_key,))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT OR IGNORE INTO dim_time_semester (
                time_key, academic_year, semester_number, semester_name, semester_type, year_of_study, exam_cycle
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            time_key, f"{start_year}-{start_year+1}", sem_no, f"Semester {sem_no}",
            "Odd" if sem_no % 2 != 0 else "Even", f"Year {student_data['current_year']}", "Winter Exam"
        ))

    # Initial attendance & marks from input
    init_att = float(student_data.get("initial_attendance_pct", 78.0))
    init_marks = float(student_data.get("initial_marks_avg", 72.0))

    # Find courses for this department and semester
    if sem_no <= 2:
        cursor.execute("SELECT course_key, credits FROM dim_course WHERE semester_offered = ?", (sem_no,))
    else:
        cursor.execute(
            "SELECT course_key, credits FROM dim_course WHERE dept_code = ? AND semester_offered = ?",
            (student_data["dept_code"], sem_no)
        )
    courses = cursor.fetchall()
    if not courses:
        # Fallback to any course
        cursor.execute("SELECT course_key, credits FROM dim_course LIMIT 4")
        courses = cursor.fetchall()

    total_credits = 0
    # Enroll in Fact_Exam_Performance & Fact_Attendance_Engagement
    for c_key, creds in courses:
        total_credits += creds
        tot_classes = 50
        attended = int(round((init_att / 100.0) * tot_classes))
        is_cond = 1 if (65.0 <= init_att < 75.0) else 0
        is_det = 1 if init_att < 65.0 else 0

        # Attendance fact
        cursor.execute("""
            INSERT INTO fact_attendance_engagement (
                student_key, course_key, department_key, time_key,
                total_classes, classes_attended, attendance_pct,
                is_condonation_risk, is_detained_risk,
                assignments_submitted, assignments_total, assignment_score_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_student_key, c_key, dept_key, time_key,
            tot_classes, attended, init_att,
            is_cond, is_det, 5, 5, init_att
        ))

        # Exam fact
        int_m = round((init_marks / 100.0) * 30.0, 1)
        ext_m = round((init_marks / 100.0) * 70.0, 1)
        tot_m = round(int_m + ext_m, 1)
        gp = round(tot_m / 10.0, 1)
        grade = "A" if gp >= 8.0 else ("B" if gp >= 6.0 else "C")
        is_pass = 1 if gp >= 5.0 else 0

        # Assign default faculty
        cursor.execute("SELECT faculty_key FROM dim_faculty WHERE dept_code = ? LIMIT 1", (student_data["dept_code"],))
        fac_row = cursor.fetchone()
        fac_key = fac_row[0] if fac_row else 1

        cursor.execute("""
            INSERT INTO fact_exam_performance (
                student_key, course_key, department_key, time_key, faculty_key,
                internal_marks, external_marks, total_marks, grade_point,
                letter_grade, credits_earned, is_passed, is_backlog, attempt_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_student_key, c_key, dept_key, time_key, fac_key,
            int_m, ext_m, tot_m, gp, grade,
            creds if is_pass else 0, is_pass, 0 if is_pass else 1, 1
        ))

    # Initialize Fact_Semester_Summary
    sgpa = round(init_marks / 10.0, 2)
    risk = "High" if init_att < 65 or sgpa < 5.0 else ("Medium" if init_att < 75 or sgpa < 6.5 else "Low")
    cursor.execute("""
        INSERT INTO fact_semester_summary (
            student_key, department_key, time_key,
            credits_registered, credits_earned, sgpa, cgpa,
            backlogs_in_sem, total_cumulative_backlogs,
            sem_attendance_avg, risk_level, academic_standing
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        new_student_key, dept_key, time_key,
        total_credits, total_credits, sgpa, sgpa,
        0, 0, init_att, risk, "Good Standing" if risk == "Low" else "Academic Warning"
    ))

    conn.commit()
    conn.close()

    # Also sync into raw_students.csv for source persistence
    raw_csv = os.path.join(BASE_DIR, "data", "raw", "raw_students.csv")
    if os.path.exists(raw_csv):
        new_row = pd.DataFrame([{
            "roll_no": roll_no,
            "student_name": student_data["student_name"].strip(),
            "gender": student_data["gender"],
            "dept_code": student_data["dept_code"],
            "cohort_batch": student_data["cohort_batch"],
            "admission_type": student_data["admission_type"],
            "current_year": student_data["current_year"],
            "current_semester": student_data["current_semester"],
            "academic_status": student_data.get("academic_status", "Active")
        }])
        new_row.to_csv(raw_csv, mode="a", header=False, index=False)

    return True, f"Student '{student_data['student_name']}' ({roll_no}) successfully admitted and joined into the Data Warehouse!"

def update_existing_student_in_warehouse(roll_no: str, updated_data: dict, db_path: str = DB_PATH):
    """
    Modifies / updates an existing student's demographic or academic information in Dim_Student.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Verify student exists
    cursor.execute("SELECT student_key, dept_code FROM dim_student WHERE roll_no = ?", (roll_no,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, f"Student with Roll Number '{roll_no}' not found!"

    student_key, old_dept = row

    # Fetch new department_key if department changed
    new_dept = updated_data.get("dept_code", old_dept)
    cursor.execute("SELECT department_key FROM dim_department WHERE dept_code = ?", (new_dept,))
    dept_row = cursor.fetchone()
    new_dept_key = dept_row[0] if dept_row else 1

    # Update Dim_Student
    cursor.execute("""
        UPDATE dim_student
        SET student_name = ?,
            gender = ?,
            dept_code = ?,
            cohort_batch = ?,
            admission_type = ?,
            current_year = ?,
            current_semester = ?,
            academic_status = ?,
            mobile_no = COALESCE(?, mobile_no),
            gmail_id = COALESCE(?, gmail_id),
            parent_mobile = COALESCE(?, parent_mobile)
        WHERE roll_no = ?
    """, (
        updated_data["student_name"].strip(),
        updated_data["gender"],
        new_dept,
        updated_data["cohort_batch"],
        updated_data["admission_type"],
        updated_data["current_year"],
        updated_data["current_semester"],
        updated_data["academic_status"],
        updated_data.get("mobile_no"),
        updated_data.get("gmail_id"),
        updated_data.get("parent_mobile"),
        roll_no
    ))

    # If department changed, update department_key in facts
    if new_dept != old_dept:
        cursor.execute("UPDATE fact_exam_performance SET department_key = ? WHERE student_key = ?", (new_dept_key, student_key))
        cursor.execute("UPDATE fact_attendance_engagement SET department_key = ? WHERE student_key = ?", (new_dept_key, student_key))
        cursor.execute("UPDATE fact_semester_summary SET department_key = ? WHERE student_key = ?", (new_dept_key, student_key))

    conn.commit()
    conn.close()

    # Sync raw_students.csv
    raw_csv = os.path.join(BASE_DIR, "data", "raw", "raw_students.csv")
    if os.path.exists(raw_csv):
        df_raw = pd.read_csv(raw_csv)
        idx = df_raw.index[df_raw["roll_no"] == roll_no].tolist()
        if idx:
            df_raw.loc[idx[0], "student_name"] = updated_data["student_name"].strip()
            df_raw.loc[idx[0], "gender"] = updated_data["gender"]
            df_raw.loc[idx[0], "dept_code"] = new_dept
            df_raw.loc[idx[0], "cohort_batch"] = updated_data["cohort_batch"]
            df_raw.loc[idx[0], "admission_type"] = updated_data["admission_type"]
            df_raw.loc[idx[0], "current_year"] = updated_data["current_year"]
            df_raw.loc[idx[0], "current_semester"] = updated_data["current_semester"]
            df_raw.loc[idx[0], "academic_status"] = updated_data["academic_status"]
            df_raw.to_csv(raw_csv, index=False)

    return True, f"Student '{roll_no}' information successfully updated in the Data Warehouse!"
