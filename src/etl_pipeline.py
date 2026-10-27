"""
etl_pipeline.py
---------------
Extract, Transform, and Load (ETL) Pipeline for the Student Performance
Multi-Fact Data Warehouse.
Extracts raw institutional files, cleans and transforms them, maps surrogate keys,
and loads into the Multi-Fact Constellation SQLite Data Warehouse.
"""

import os
import sqlite3
import pandas as pd
from warehouse_schema import SCHEMA_DDL

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DW_DIR = os.path.join(BASE_DIR, "data", "warehouse")
DB_PATH = os.path.join(DW_DIR, "academic_dw.db")

class AcademicETLPipeline:
    def __init__(self, raw_dir: str = RAW_DIR, db_path: str = DB_PATH):
        self.raw_dir = raw_dir
        self.db_path = db_path
        self.stats = {}

    def extract(self):
        """Extracts raw source files."""
        print("[ETL: 1/3] Extracting raw institutional data...")
        self.raw_depts = pd.read_csv(os.path.join(self.raw_dir, "raw_departments.csv"))
        self.raw_faculty = pd.read_csv(os.path.join(self.raw_dir, "raw_faculty.csv"))
        self.raw_courses = pd.read_csv(os.path.join(self.raw_dir, "raw_courses.csv"))
        self.raw_time = pd.read_csv(os.path.join(self.raw_dir, "raw_time_semesters.csv"))
        self.raw_students = pd.read_csv(os.path.join(self.raw_dir, "raw_students.csv"))
        self.raw_exams = pd.read_csv(os.path.join(self.raw_dir, "raw_exam_scores.csv"))
        self.raw_attendance = pd.read_csv(os.path.join(self.raw_dir, "raw_attendance_records.csv"))
        self.raw_sem_summary = pd.read_csv(os.path.join(self.raw_dir, "raw_semester_summaries.csv"))

        self.stats["extracted"] = {
            "departments": len(self.raw_depts),
            "faculty": len(self.raw_faculty),
            "courses": len(self.raw_courses),
            "time_semesters": len(self.raw_time),
            "students": len(self.raw_students),
            "exam_scores": len(self.raw_exams),
            "attendance_records": len(self.raw_attendance),
            "semester_summaries": len(self.raw_sem_summary)
        }
        print(f"    Extracted {self.stats['extracted']['students']} students, "
              f"{self.stats['extracted']['exam_scores']} exam records, "
              f"{self.stats['extracted']['attendance_records']} attendance records.")

    def transform_and_load(self):
        """Transforms dimensions, builds surrogate key maps, and loads facts."""
        print("[ETL: 2/3] Transforming data and loading into Multi-Fact Warehouse...")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        # Drop existing tables safely without file-locking PermissionError on Windows
        conn.executescript("""
            DROP TABLE IF EXISTS fact_exam_performance;
            DROP TABLE IF EXISTS fact_attendance_engagement;
            DROP TABLE IF EXISTS fact_semester_summary;
            DROP TABLE IF EXISTS dim_student;
            DROP TABLE IF EXISTS dim_course;
            DROP TABLE IF EXISTS dim_faculty;
            DROP TABLE IF EXISTS dim_department;
            DROP TABLE IF EXISTS dim_time_semester;
        """)
        conn.executescript(SCHEMA_DDL)
        cursor = conn.cursor()

        # ----------------------------------------------------
        # 1. Load Dim_Department
        # ----------------------------------------------------
        self.raw_depts.to_sql("dim_department", conn, if_exists="append", index=False)
        dept_map = pd.read_sql("SELECT department_key, dept_code FROM dim_department", conn)
        dept_lookup = dict(zip(dept_map["dept_code"], dept_map["department_key"]))

        # ----------------------------------------------------
        # 2. Load Dim_Faculty
        # ----------------------------------------------------
        self.raw_faculty.to_sql("dim_faculty", conn, if_exists="append", index=False)
        fac_map = pd.read_sql("SELECT faculty_key, faculty_id FROM dim_faculty", conn)
        fac_lookup = dict(zip(fac_map["faculty_id"], fac_map["faculty_key"]))

        # ----------------------------------------------------
        # 3. Load Dim_Course
        # ----------------------------------------------------
        self.raw_courses.to_sql("dim_course", conn, if_exists="append", index=False)
        course_map = pd.read_sql("SELECT course_key, course_code, dept_code FROM dim_course", conn)
        course_lookup = dict(zip(course_map["course_code"], course_map["course_key"]))
        course_dept_lookup = dict(zip(course_map["course_code"], course_map["dept_code"]))

        # ----------------------------------------------------
        # 4. Load Dim_Time_Semester
        # ----------------------------------------------------
        self.raw_time.to_sql("dim_time_semester", conn, if_exists="append", index=False)

        # ----------------------------------------------------
        # 5. Load Dim_Student
        # ----------------------------------------------------
        if "mobile_no" not in self.raw_students.columns:
            self.raw_students["mobile_no"] = self.raw_students["roll_no"].apply(
                lambda r: f"+91 98{abs(hash(r)) % 90000000 + 10000000}"
            )
        if "gmail_id" not in self.raw_students.columns:
            self.raw_students["gmail_id"] = self.raw_students.apply(
                lambda r: f"{str(r['student_name']).split()[0].lower()}.{str(r['roll_no']).lower()}@gmail.com", axis=1
            )
        if "parent_mobile" not in self.raw_students.columns:
            self.raw_students["parent_mobile"] = self.raw_students["roll_no"].apply(
                lambda r: f"+91 94{abs(hash(r + 'p')) % 90000000 + 10000000}"
            )

        cols_student = [
            "roll_no", "student_name", "gender", "dept_code", "cohort_batch",
            "admission_type", "current_year", "current_semester", "academic_status",
            "mobile_no", "gmail_id", "parent_mobile"
        ]
        stu_to_load = self.raw_students[[c for c in cols_student if c in self.raw_students.columns]]
        stu_to_load.to_sql("dim_student", conn, if_exists="append", index=False)
        stu_map = pd.read_sql("SELECT student_key, roll_no, dept_code FROM dim_student", conn)
        student_lookup = dict(zip(stu_map["roll_no"], stu_map["student_key"]))
        student_dept_lookup = dict(zip(stu_map["roll_no"], stu_map["dept_code"]))

        # ----------------------------------------------------
        # 6. Transform & Load Fact_Exam_Performance
        # ----------------------------------------------------
        exam_facts = self.raw_exams.copy()
        exam_facts["student_key"] = exam_facts["roll_no"].map(student_lookup)
        exam_facts["course_key"] = exam_facts["course_code"].map(course_lookup)
        # Determine department key: department owning student / course
        exam_facts["dept_code"] = exam_facts["roll_no"].map(student_dept_lookup)
        exam_facts["department_key"] = exam_facts["dept_code"].map(dept_lookup)
        exam_facts["faculty_key"] = exam_facts["faculty_id"].map(fac_lookup).fillna(1).astype(int)

        # Quality check: drop unmapped rows
        exam_facts = exam_facts.dropna(subset=["student_key", "course_key", "department_key"])
        cols_exam = [
            "student_key", "course_key", "department_key", "time_key", "faculty_key",
            "internal_marks", "external_marks", "total_marks", "grade_point", "letter_grade",
            "credits_earned", "is_passed", "is_backlog", "attempt_number"
        ]
        exam_facts[cols_exam].to_sql("fact_exam_performance", conn, if_exists="append", index=False)

        # ----------------------------------------------------
        # 7. Transform & Load Fact_Attendance_Engagement
        # ----------------------------------------------------
        att_facts = self.raw_attendance.copy()
        att_facts["student_key"] = att_facts["roll_no"].map(student_lookup)
        att_facts["course_key"] = att_facts["course_code"].map(course_lookup)
        att_facts["dept_code"] = att_facts["roll_no"].map(student_dept_lookup)
        att_facts["department_key"] = att_facts["dept_code"].map(dept_lookup)

        att_facts = att_facts.dropna(subset=["student_key", "course_key", "department_key"])
        cols_att = [
            "student_key", "course_key", "department_key", "time_key",
            "total_classes", "classes_attended", "attendance_pct",
            "is_condonation_risk", "is_detained_risk",
            "assignments_submitted", "assignments_total", "assignment_score_pct"
        ]
        att_facts[cols_att].to_sql("fact_attendance_engagement", conn, if_exists="append", index=False)

        # ----------------------------------------------------
        # 8. Transform & Load Fact_Semester_Summary
        # ----------------------------------------------------
        sum_facts = self.raw_sem_summary.copy()
        sum_facts["student_key"] = sum_facts["roll_no"].map(student_lookup)
        sum_facts["dept_code"] = sum_facts["roll_no"].map(student_dept_lookup)
        sum_facts["department_key"] = sum_facts["dept_code"].map(dept_lookup)

        sum_facts = sum_facts.dropna(subset=["student_key", "department_key"])
        cols_sum = [
            "student_key", "department_key", "time_key",
            "credits_registered", "credits_earned", "sgpa", "cgpa",
            "backlogs_in_sem", "total_cumulative_backlogs",
            "sem_attendance_avg", "risk_level", "academic_standing"
        ]
        sum_facts[cols_sum].to_sql("fact_semester_summary", conn, if_exists="append", index=False)

        conn.commit()
        conn.close()

        self.stats["loaded"] = {
            "fact_exam_performance": len(exam_facts),
            "fact_attendance_engagement": len(att_facts),
            "fact_semester_summary": len(sum_facts)
        }
        print(f"[ETL: 3/3] Successfully loaded all facts into {self.db_path}:")
        print(f"    - Fact_Exam_Performance: {len(exam_facts)} rows")
        print(f"    - Fact_Attendance_Engagement: {len(att_facts)} rows")
        print(f"    - Fact_Semester_Summary: {len(sum_facts)} rows")
        print(f"[SUCCESS] Multi-Fact Data Warehouse ETL execution complete!")

def run_etl():
    etl = AcademicETLPipeline()
    etl.extract()
    etl.transform_and_load()

if __name__ == "__main__":
    run_etl()
