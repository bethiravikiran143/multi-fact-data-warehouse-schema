"""
generate_raw_data.py
--------------------
Generates realistic institutional academic data across 5 engineering departments
(CSE, ECE, MECH, CIVIL, AIDS) spanning 4 cohorts (2021-25, 2022-26, 2023-27, 2024-28).
Produces raw source CSV files simulating college SIS / ERP database exports.
"""

import os
import random
import numpy as np
import pandas as pd

# Set random seed for reproducible realistic data
random.seed(42)
np.random.seed(42)

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# 1. Departments
DEPARTMENTS = [
    {
        "dept_code": "CSE",
        "dept_name": "Computer Science & Engineering",
        "hod_name": "Dr. V. Ramanathan",
        "established_year": 1998,
        "total_faculty": 28
    },
    {
        "dept_code": "AIDS",
        "dept_name": "Artificial Intelligence & Data Science",
        "hod_name": "Dr. P. Sunitha",
        "established_year": 2020,
        "total_faculty": 16
    },
    {
        "dept_code": "ECE",
        "dept_name": "Electronics & Communication Engineering",
        "hod_name": "Dr. K. Srinivas Rao",
        "established_year": 2001,
        "total_faculty": 24
    },
    {
        "dept_code": "MECH",
        "dept_name": "Mechanical Engineering",
        "hod_name": "Dr. N. Suresh Babu",
        "established_year": 2004,
        "total_faculty": 20
    },
    {
        "dept_code": "CIVIL",
        "dept_name": "Civil Engineering",
        "hod_name": "Dr. M. Venkat Reddy",
        "established_year": 2006,
        "total_faculty": 18
    }
]

# 2. Faculty list
FACULTY_LIST = [
    # MECH
    {"faculty_id": "FAC_ME01", "faculty_name": "Dr. N. Suresh Babu", "dept_code": "MECH", "designation": "Associate Professor & HOD", "qualification": "Ph.D.", "experience_years": 16},
    {"faculty_id": "FAC_ME02", "faculty_name": "Dr. Ramesh Babu", "dept_code": "MECH", "designation": "Professor", "qualification": "Ph.D.", "experience_years": 21},
    {"faculty_id": "FAC_ME03", "faculty_name": "Mrs. T. Anitha", "dept_code": "MECH", "designation": "Assistant Professor", "qualification": "M.Tech", "experience_years": 8},
    {"faculty_id": "FAC_ME04", "faculty_name": "Mr. S. Mahesh", "dept_code": "MECH", "designation": "Assistant Professor", "qualification": "M.Tech", "experience_years": 6},
    # CSE
    {"faculty_id": "FAC_CS01", "faculty_name": "Dr. V. Ramanathan", "dept_code": "CSE", "designation": "Professor & HOD", "qualification": "Ph.D.", "experience_years": 22},
    {"faculty_id": "FAC_CS02", "faculty_name": "Dr. A. Sudheer Kumar", "dept_code": "CSE", "designation": "Associate Professor", "qualification": "Ph.D.", "experience_years": 14},
    {"faculty_id": "FAC_CS03", "faculty_name": "Mrs. N. Lakshmi", "dept_code": "CSE", "designation": "Assistant Professor", "qualification": "M.Tech", "experience_years": 9},
    {"faculty_id": "FAC_CS04", "faculty_name": "Mr. G. Pradeep", "dept_code": "CSE", "designation": "Assistant Professor", "qualification": "M.Tech", "experience_years": 7},
    # AIDS
    {"faculty_id": "FAC_AI01", "faculty_name": "Dr. P. Sunitha", "dept_code": "AIDS", "designation": "Professor & HOD", "qualification": "Ph.D.", "experience_years": 17},
    {"faculty_id": "FAC_AI02", "faculty_name": "Dr. M. Karthik", "dept_code": "AIDS", "designation": "Associate Professor", "qualification": "Ph.D.", "experience_years": 12},
    {"faculty_id": "FAC_AI03", "faculty_name": "Mr. B. Vikram", "dept_code": "AIDS", "designation": "Assistant Professor", "qualification": "M.Tech", "experience_years": 5},
    # ECE
    {"faculty_id": "FAC_EC01", "faculty_name": "Dr. K. Srinivas Rao", "dept_code": "ECE", "designation": "Professor & HOD", "qualification": "Ph.D.", "experience_years": 24},
    {"faculty_id": "FAC_EC02", "faculty_name": "Dr. B. Radhika", "dept_code": "ECE", "designation": "Associate Professor", "qualification": "Ph.D.", "experience_years": 13},
    {"faculty_id": "FAC_EC03", "faculty_name": "Mr. Ch. Naresh", "dept_code": "ECE", "designation": "Assistant Professor", "qualification": "M.Tech", "experience_years": 8},
    # CIVIL
    {"faculty_id": "FAC_CE01", "faculty_name": "Dr. M. Venkat Reddy", "dept_code": "CIVIL", "designation": "Professor & HOD", "qualification": "Ph.D.", "experience_years": 20},
    {"faculty_id": "FAC_CE02", "faculty_name": "Mr. D. Suresh", "dept_code": "CIVIL", "designation": "Assistant Professor", "qualification": "M.Tech", "experience_years": 10},
    {"faculty_id": "FAC_CE03", "faculty_name": "Ms. K. Swathi", "dept_code": "CIVIL", "designation": "Assistant Professor", "qualification": "M.Tech", "experience_years": 6}
]

# 3. Courses definition by Department and Semester
COURSES_DATA = [
    # Common 1st Year (Sem 1 & Sem 2)
    {"course_code": "MA101", "course_name": "Linear Algebra & Calculus", "dept_code": "CSE", "course_type": "Core Theory", "credits": 4, "semester_offered": 1},
    {"course_code": "PH101", "course_name": "Applied Engineering Physics", "dept_code": "ECE", "course_type": "Core Theory", "credits": 3, "semester_offered": 1},
    {"course_code": "CS101", "course_name": "Programming for Problem Solving (C & Python)", "dept_code": "CSE", "course_type": "Core Theory", "credits": 3, "semester_offered": 1},
    {"course_code": "ME101", "course_name": "Engineering Graphics & Design", "dept_code": "MECH", "course_type": "Lab/Practical", "credits": 3, "semester_offered": 1},
    {"course_code": "MA201", "course_name": "Differential Equations & Numerical Methods", "dept_code": "MECH", "course_type": "Core Theory", "credits": 4, "semester_offered": 2},
    {"course_code": "EE201", "course_name": "Basic Electrical & Electronics Engineering", "dept_code": "ECE", "course_type": "Core Theory", "credits": 3, "semester_offered": 2},
    {"course_code": "CS201", "course_name": "Data Structures & Algorithms", "dept_code": "CSE", "course_type": "Core Theory", "credits": 3, "semester_offered": 2},

    # MECH
    {"course_code": "ME301", "course_name": "Engineering Mechanics & Dynamics", "dept_code": "MECH", "course_type": "Core Theory", "credits": 4, "semester_offered": 3},
    {"course_code": "ME302", "course_name": "Thermodynamics & Thermal Power", "dept_code": "MECH", "course_type": "Core Theory", "credits": 3, "semester_offered": 3},
    {"course_code": "ME303", "course_name": "Manufacturing Technology & Metallurgy", "dept_code": "MECH", "course_type": "Core Theory", "credits": 3, "semester_offered": 3},
    {"course_code": "ME401", "course_name": "Fluid Mechanics & Hydraulic Machinery", "dept_code": "MECH", "course_type": "Core Theory", "credits": 4, "semester_offered": 4},
    {"course_code": "ME402", "course_name": "Kinematics of Machinery", "dept_code": "MECH", "course_type": "Core Theory", "credits": 3, "semester_offered": 4},
    {"course_code": "ME501", "course_name": "Design of Machine Elements", "dept_code": "MECH", "course_type": "Core Theory", "credits": 4, "semester_offered": 5},
    {"course_code": "ME502", "course_name": "Heat Transfer & Refrigeration", "dept_code": "MECH", "course_type": "Core Theory", "credits": 3, "semester_offered": 5},
    {"course_code": "ME503", "course_name": "Industrial Robotics & Automation", "dept_code": "MECH", "course_type": "Professional Elective", "credits": 3, "semester_offered": 5},
    {"course_code": "ME601", "course_name": "CAD / CAM / CAE & FEA Analysis", "dept_code": "MECH", "course_type": "Core Theory", "credits": 3, "semester_offered": 6},
    {"course_code": "ME602", "course_name": "Automobile Engineering", "dept_code": "MECH", "course_type": "Professional Elective", "credits": 3, "semester_offered": 6},
    {"course_code": "ME701", "course_name": "Operations Research & Production Mgmt", "dept_code": "MECH", "course_type": "Core Theory", "credits": 3, "semester_offered": 7},
    {"course_code": "ME801", "course_name": "Renewable Energy & Power Plant Engg", "dept_code": "MECH", "course_type": "Core Theory", "credits": 3, "semester_offered": 8},

    # CSE
    {"course_code": "CS301", "course_name": "Database Management Systems (DBMS)", "dept_code": "CSE", "course_type": "Core Theory", "credits": 3, "semester_offered": 3},
    {"course_code": "CS302", "course_name": "Computer Organization & Architecture", "dept_code": "CSE", "course_type": "Core Theory", "credits": 3, "semester_offered": 3},
    {"course_code": "CS401", "course_name": "Operating Systems & System Programming", "dept_code": "CSE", "course_type": "Core Theory", "credits": 3, "semester_offered": 4},
    {"course_code": "CS402", "course_name": "Design & Analysis of Algorithms", "dept_code": "CSE", "course_type": "Core Theory", "credits": 4, "semester_offered": 4},
    {"course_code": "CS501", "course_name": "Data Warehousing & Data Mining", "dept_code": "CSE", "course_type": "Core Theory", "credits": 3, "semester_offered": 5},
    {"course_code": "CS502", "course_name": "Computer Networks & Security", "dept_code": "CSE", "course_type": "Core Theory", "credits": 3, "semester_offered": 5},
    {"course_code": "CS601", "course_name": "Software Engineering & Agile DevOps", "dept_code": "CSE", "course_type": "Core Theory", "credits": 3, "semester_offered": 6},
    {"course_code": "CS602", "course_name": "Cloud Computing & Distributed Systems", "dept_code": "CSE", "course_type": "Professional Elective", "credits": 3, "semester_offered": 6},
    {"course_code": "CS701", "course_name": "Information & Network Cyber Security", "dept_code": "CSE", "course_type": "Core Theory", "credits": 3, "semester_offered": 7},
    {"course_code": "CS801", "course_name": "Full Stack Web & Microservices", "dept_code": "CSE", "course_type": "Core Theory", "credits": 3, "semester_offered": 8},

    # AIDS
    {"course_code": "AI301", "course_name": "Foundations of Artificial Intelligence", "dept_code": "AIDS", "course_type": "Core Theory", "credits": 3, "semester_offered": 3},
    {"course_code": "AI302", "course_name": "Python for Data Science & EDA", "dept_code": "AIDS", "course_type": "Core Theory", "credits": 3, "semester_offered": 3},
    {"course_code": "AI401", "course_name": "Machine Learning Algorithms & Models", "dept_code": "AIDS", "course_type": "Core Theory", "credits": 4, "semester_offered": 4},
    {"course_code": "AI402", "course_name": "Big Data Technologies (Hadoop & Spark)", "dept_code": "AIDS", "course_type": "Core Theory", "credits": 3, "semester_offered": 4},
    {"course_code": "AI501", "course_name": "Deep Learning & Neural Architectures", "dept_code": "AIDS", "course_type": "Core Theory", "credits": 4, "semester_offered": 5},
    {"course_code": "AI502", "course_name": "Business Intelligence & Data Visualization", "dept_code": "AIDS", "course_type": "Core Theory", "credits": 3, "semester_offered": 5},
    {"course_code": "AI601", "course_name": "Natural Language Processing & LLMs", "dept_code": "AIDS", "course_type": "Core Theory", "credits": 3, "semester_offered": 6},
    {"course_code": "AI701", "course_name": "Computer Vision & Pattern Recognition", "dept_code": "AIDS", "course_type": "Professional Elective", "credits": 3, "semester_offered": 7},
    {"course_code": "AI801", "course_name": "MLOps & AI Model Deployment", "dept_code": "AIDS", "course_type": "Core Theory", "credits": 3, "semester_offered": 8},

    # ECE
    {"course_code": "EC301", "course_name": "Electronic Devices & Analog Circuits", "dept_code": "ECE", "course_type": "Core Theory", "credits": 3, "semester_offered": 3},
    {"course_code": "EC302", "course_name": "Digital Logic Design & Verilog", "dept_code": "ECE", "course_type": "Core Theory", "credits": 3, "semester_offered": 3},
    {"course_code": "EC401", "course_name": "Signals & Linear Systems", "dept_code": "ECE", "course_type": "Core Theory", "credits": 4, "semester_offered": 4},
    {"course_code": "EC402", "course_name": "Electromagnetic Waves & Antennas", "dept_code": "ECE", "course_type": "Core Theory", "credits": 3, "semester_offered": 4},
    {"course_code": "EC501", "course_name": "Microprocessors & Embedded Systems", "dept_code": "ECE", "course_type": "Core Theory", "credits": 3, "semester_offered": 5},
    {"course_code": "EC502", "course_name": "Digital Signal Processing (DSP)", "dept_code": "ECE", "course_type": "Core Theory", "credits": 4, "semester_offered": 5},
    {"course_code": "EC601", "course_name": "VLSI Design & Architecture", "dept_code": "ECE", "course_type": "Core Theory", "credits": 3, "semester_offered": 6},
    {"course_code": "EC701", "course_name": "Wireless & Cellular Communications", "dept_code": "ECE", "course_type": "Core Theory", "credits": 3, "semester_offered": 7},
    {"course_code": "EC801", "course_name": "IoT Architectures & Sensors", "dept_code": "ECE", "course_type": "Core Theory", "credits": 3, "semester_offered": 8},

    # CIVIL
    {"course_code": "CE301", "course_name": "Strength of Materials & Mechanics", "dept_code": "CIVIL", "course_type": "Core Theory", "credits": 4, "semester_offered": 3},
    {"course_code": "CE302", "course_name": "Fluid Mechanics in Civil Systems", "dept_code": "CIVIL", "course_type": "Core Theory", "credits": 3, "semester_offered": 3},
    {"course_code": "CE401", "course_name": "Structural Analysis & RCC Design", "dept_code": "CIVIL", "course_type": "Core Theory", "credits": 4, "semester_offered": 4},
    {"course_code": "CE402", "course_name": "Surveying & Geomatics", "dept_code": "CIVIL", "course_type": "Core Theory", "credits": 3, "semester_offered": 4},
    {"course_code": "CE501", "course_name": "Geotechnical & Soil Engineering", "dept_code": "CIVIL", "course_type": "Core Theory", "credits": 3, "semester_offered": 5},
    {"course_code": "CE502", "course_name": "Hydrology & Water Resources", "dept_code": "CIVIL", "course_type": "Core Theory", "credits": 3, "semester_offered": 5},
    {"course_code": "CE601", "course_name": "Transportation & Highway Engineering", "dept_code": "CIVIL", "course_type": "Core Theory", "credits": 3, "semester_offered": 6},
    {"course_code": "CE701", "course_name": "Environmental Engineering & Waste Mgmt", "dept_code": "CIVIL", "course_type": "Core Theory", "credits": 3, "semester_offered": 7},
    {"course_code": "CE801", "course_name": "Construction Planning & Project Mgmt", "dept_code": "CIVIL", "course_type": "Core Theory", "credits": 3, "semester_offered": 8}
]

# 4. Cohorts and time semesters
COHORTS = {
    "2021-2025": {"start_year": 2021, "semesters": [1, 2, 3, 4, 5, 6, 7, 8], "status": "Graduated"},
    "2022-2026": {"start_year": 2022, "semesters": [1, 2, 3, 4, 5, 6, 7], "status": "Active"},
    "2023-2027": {"start_year": 2023, "semesters": [1, 2, 3, 4, 5], "status": "Active"},
    "2024-2028": {"start_year": 2024, "semesters": [1, 2, 3], "status": "Active"}
}

def generate_time_dimension():
    """Builds Dim_Time_Semester entries."""
    rows = []
    # Academic years: 2021-22, 2022-23, 2023-24, 2024-25, 2025-26
    sem_map = {
        1: ("1st Year", "Odd", "Winter Exam"),
        2: ("1st Year", "Even", "Summer Exam"),
        3: ("2nd Year", "Odd", "Winter Exam"),
        4: ("2nd Year", "Even", "Summer Exam"),
        5: ("3rd Year", "Odd", "Winter Exam"),
        6: ("3rd Year", "Even", "Summer Exam"),
        7: ("4th Year", "Odd", "Winter Exam"),
        8: ("4th Year", "Even", "Summer Exam")
    }

    key = 1
    for start_yr in range(2021, 2026):
        ay = f"{start_yr}-{start_yr+1}"
        for sem_no in range(1, 9):
            yos, stype, cycle = sem_map[sem_no]
            t_key = int(f"{start_yr}{sem_no:02d}")
            rows.append({
                "time_key": t_key,
                "academic_year": ay,
                "semester_number": sem_no,
                "semester_name": f"Semester {sem_no}",
                "semester_type": stype,
                "year_of_study": yos,
                "exam_cycle": cycle
            })
            key += 1
    return pd.DataFrame(rows).drop_duplicates(subset=["time_key"])

# 5. Student Names pool
FIRST_NAMES = [
    "Aarav", "Aditi", "Akhil", "Ananya", "Bhavya", "Chaitanya", "Deepak", "Divya", "Ganesh",
    "Harini", "Ishaan", "Jahnavi", "Kavya", "Lokesh", "Manoj", "Meghana", "Nikhil",
    "Nandini", "Pranay", "Pooja", "Rahul", "Ramya", "Sai", "Sneha", "Suresh", "Swetha",
    "Tarun", "Teja", "Varun", "Veda", "Vikas", "Vinay", "Yamini", "Yashwanth"
]
LAST_NAMES = [
    "Reddy", "Sharma", "Rao", "Kumar", "Verma", "Patel", "Goud", "Naidu", "Chowdary",
    "Joshi", "Gupta", "Mishra", "Deshmukh", "Nair", "Iyer", "Yadav"
]

def generate_students():
    """Generates synthetic student cohort data across all departments."""
    students = []

    # Generate students per dept per cohort
    dept_codes = ["CSE", "AIDS", "ECE", "MECH", "CIVIL"]
    
    for batch, meta in COHORTS.items():
        batch_prefix = batch[2:4] # "21", "22", "23", "24"
        start_yr = meta["start_year"]
        
        for dept in dept_codes:
            # Generate 20 students per dept per cohort
            for i in range(1, 21):
                roll = f"{batch_prefix}{dept[:2]}1A{i:04d}"
                fn = random.choice(FIRST_NAMES)
                ln = random.choice(LAST_NAMES)
                name = f"{fn} {ln}"
                gender = "Female" if fn in ["Aditi", "Ananya", "Bhavya", "Divya", "Harini", "Jahnavi", "Kavya", "Meghana", "Nandini", "Pooja", "Ramya", "Sneha", "Swetha", "Veda", "Yamini"] else "Male"
                
                adm = random.choices(["Regular", "Lateral Entry", "Management"], weights=[0.8, 0.12, 0.08])[0]
                
                # Ability distribution
                ability = np.clip(np.random.normal(0.68, 0.16), 0.25, 0.98)
                
                max_sem = max(meta["semesters"])
                cur_yr = min(4, (max_sem + 1) // 2)
                
                mob_num = f"+91 98{abs(hash(roll)) % 90000000 + 10000000}"
                gmail_addr = f"{fn.lower()}.{roll.lower()}@gmail.com"
                pmob_num = f"+91 94{abs(hash(roll + 'parent')) % 90000000 + 10000000}"

                students.append({
                    "roll_no": roll,
                    "student_name": name,
                    "gender": gender,
                    "dept_code": dept,
                    "cohort_batch": batch,
                    "admission_type": adm,
                    "current_year": cur_yr,
                    "current_semester": max_sem,
                    "academic_status": meta["status"],
                    "baseline_ability": ability,
                    "mobile_no": mob_num,
                    "gmail_id": gmail_addr,
                    "parent_mobile": pmob_num
                })
                
    return pd.DataFrame(students)

def generate_performance_and_attendance(students_df, courses_df, faculty_df):
    """
    Simulates exam marks and attendance records with realistic correlations:
    - Higher attendance strongly correlates with higher internal & external marks.
    - Low attendance (<65%) heavily triggers condonation / detention risk and higher failure risk.
    """
    exam_rows = []
    attendance_rows = []
    semester_summary_rows = []
    
    # Map faculty by department
    dept_fac_map = {}
    for dept in ["CSE", "AIDS", "ECE", "MECH", "CIVIL"]:
        dept_fac_map[dept] = faculty_df[faculty_df["dept_code"] == dept]["faculty_id"].tolist()

    for _, stu in students_df.iterrows():
        roll = stu["roll_no"]
        dept = stu["dept_code"]
        cohort = stu["cohort_batch"]
        ability = stu["baseline_ability"]
        admitted_sem = 3 if stu["admission_type"] == "Lateral Entry" else 1
        
        cohort_info = COHORTS[cohort]
        active_sems = [s for s in cohort_info["semesters"] if s >= admitted_sem]
        start_yr = cohort_info["start_year"]
        
        cum_credits_reg = 0
        cum_credits_earn = 0
        cum_grade_pts_total = 0.0
        active_backlogs_count = 0
        
        for sem in active_sems:
            # Academic year mapping
            yr_offset = (sem - 1) // 2
            ay_start = start_yr + yr_offset
            time_key = int(f"{ay_start}{sem:02d}")
            
            # Find courses offered in this semester for this department
            # Include department courses + common 1st year courses
            if sem <= 2:
                # 1st year common
                sem_courses = courses_df[courses_df["semester_offered"] == sem]
            else:
                sem_courses = courses_df[(courses_df["dept_code"] == dept) & (courses_df["semester_offered"] == sem)]
                
            if sem_courses.empty:
                continue
                
            sem_credits_reg = 0
            sem_credits_earn = 0
            sem_grade_pts_earned = 0.0
            sem_backlogs = 0
            sem_attendance_list = []
            
            for _, crs in sem_courses.iterrows():
                crs_code = crs["course_code"]
                credits = crs["credits"]
                sem_credits_reg += credits
                
                # Pick faculty
                fac_pool = dept_fac_map.get(crs["dept_code"], dept_fac_map[dept])
                assigned_fac = random.choice(fac_pool) if fac_pool else "FAC_ME01"
                
                # 1. Simulate Attendance (Correlated with ability + personal variation)
                mean_att = np.clip(ability * 92 + np.random.normal(0, 7), 45, 98)
                total_classes = random.randint(48, 62)
                classes_attended = int(round((mean_att / 100.0) * total_classes))
                classes_attended = min(total_classes, max(15, classes_attended))
                att_pct = round((classes_attended / total_classes) * 100.0, 2)
                sem_attendance_list.append(att_pct)
                
                # Attendance risk flags
                condonation_risk = 1 if (65.0 <= att_pct < 75.0) else 0
                detention_risk = 1 if (att_pct < 65.0) else 0
                
                # LMS Assignments
                total_assign = random.randint(5, 8)
                sub_rate = np.clip((att_pct / 100.0) + np.random.normal(0, 0.08), 0.2, 1.0)
                sub_count = int(round(sub_rate * total_assign))
                assign_score_pct = round(sub_rate * 100.0, 1)
                
                attendance_rows.append({
                    "roll_no": roll,
                    "course_code": crs_code,
                    "time_key": time_key,
                    "total_classes": total_classes,
                    "classes_attended": classes_attended,
                    "attendance_pct": att_pct,
                    "is_condonation_risk": condonation_risk,
                    "is_detained_risk": detention_risk,
                    "assignments_submitted": sub_count,
                    "assignments_total": total_assign,
                    "assignment_score_pct": assign_score_pct
                })
                
                # 2. Simulate Exam Performance (Correlated with ability and attendance)
                # Max marks: Internal 30, External 70, Total 100
                att_factor = (att_pct / 100.0)
                internal_perf = np.clip((ability * 0.7 + att_factor * 0.3) * 30 + np.random.normal(0, 2.5), 8, 30)
                external_perf = np.clip((ability * 0.75 + att_factor * 0.25) * 70 + np.random.normal(0, 5.5), 18, 70)
                
                # Severe detention impact: if detained, cannot write regular external
                if detention_risk == 1 and random.random() < 0.65:
                    external_perf = min(external_perf, 24.0) # Fail threshold (needs 28+ out of 70)
                    
                total_marks = round(internal_perf + external_perf, 1)
                internal_marks = round(internal_perf, 1)
                external_marks = round(external_perf, 1)
                
                # Grading schema
                if total_marks >= 90:
                    grade_point = 10.0; letter_grade = "O"
                elif total_marks >= 80:
                    grade_point = 9.0; letter_grade = "A+"
                elif total_marks >= 70:
                    grade_point = 8.0; letter_grade = "A"
                elif total_marks >= 60:
                    grade_point = 7.0; letter_grade = "B+"
                elif total_marks >= 50:
                    grade_point = 6.0; letter_grade = "B"
                elif total_marks >= 40 and external_marks >= 25:
                    grade_point = 5.0; letter_grade = "C"
                else:
                    grade_point = 0.0; letter_grade = "F"
                    
                is_passed = 1 if grade_point >= 5.0 else 0
                is_backlog = 1 if is_passed == 0 else 0
                credits_earned = credits if is_passed else 0
                
                if is_backlog:
                    sem_backlogs += 1
                    active_backlogs_count += 1
                
                sem_credits_earn += credits_earned
                sem_grade_pts_earned += (grade_point * credits)
                
                exam_rows.append({
                    "roll_no": roll,
                    "course_code": crs_code,
                    "time_key": time_key,
                    "faculty_id": assigned_fac,
                    "internal_marks": internal_marks,
                    "external_marks": external_marks,
                    "total_marks": total_marks,
                    "grade_point": grade_point,
                    "letter_grade": letter_grade,
                    "credits_earned": credits_earned,
                    "is_passed": is_passed,
                    "is_backlog": is_backlog,
                    "attempt_number": 1
                })
                
            # Semester Summary Calculation
            sgpa = round(sem_grade_pts_earned / max(1, sem_credits_reg), 2)
            cum_credits_reg += sem_credits_reg
            cum_credits_earn += sem_credits_earn
            cum_grade_pts_total += sem_grade_pts_earned
            cgpa = round(cum_grade_pts_total / max(1, cum_credits_reg), 2)
            
            avg_sem_att = round(float(np.mean(sem_attendance_list)), 2) if sem_attendance_list else 80.0
            
            # Risk level estimation
            if sem_backlogs >= 2 or avg_sem_att < 65 or sgpa < 5.0:
                risk_lvl = "High"
                standing = "Critical Probation"
            elif sem_backlogs == 1 or avg_sem_att < 75 or sgpa < 6.5:
                risk_lvl = "Medium"
                standing = "Academic Warning"
            else:
                risk_lvl = "Low"
                standing = "Good Standing"
                
            semester_summary_rows.append({
                "roll_no": roll,
                "time_key": time_key,
                "credits_registered": sem_credits_reg,
                "credits_earned": sem_credits_earn,
                "sgpa": sgpa,
                "cgpa": cgpa,
                "backlogs_in_sem": sem_backlogs,
                "total_cumulative_backlogs": active_backlogs_count,
                "sem_attendance_avg": avg_sem_att,
                "risk_level": risk_lvl,
                "academic_standing": standing
            })
            
    return pd.DataFrame(exam_rows), pd.DataFrame(attendance_rows), pd.DataFrame(semester_summary_rows)

def main():
    print("[*] Generating raw institutional academic records...")
    
    # 1. Departments
    dept_df = pd.DataFrame(DEPARTMENTS)
    dept_df.to_csv(os.path.join(RAW_DATA_DIR, "raw_departments.csv"), index=False)
    
    # 2. Faculty
    faculty_df = pd.DataFrame(FACULTY_LIST)
    faculty_df.to_csv(os.path.join(RAW_DATA_DIR, "raw_faculty.csv"), index=False)
    
    # 3. Courses
    courses_df = pd.DataFrame(COURSES_DATA)
    courses_df.to_csv(os.path.join(RAW_DATA_DIR, "raw_courses.csv"), index=False)
    
    # 4. Time
    time_df = generate_time_dimension()
    time_df.to_csv(os.path.join(RAW_DATA_DIR, "raw_time_semesters.csv"), index=False)
    
    # 5. Students
    students_df = generate_students()
    # Save student raw without ability internal column
    students_export = students_df.drop(columns=["baseline_ability"])
    students_export.to_csv(os.path.join(RAW_DATA_DIR, "raw_students.csv"), index=False)
    
    # 6. Performance & Attendance
    exam_df, att_df, sem_sum_df = generate_performance_and_attendance(students_df, courses_df, faculty_df)
    exam_df.to_csv(os.path.join(RAW_DATA_DIR, "raw_exam_scores.csv"), index=False)
    att_df.to_csv(os.path.join(RAW_DATA_DIR, "raw_attendance_records.csv"), index=False)
    sem_sum_df.to_csv(os.path.join(RAW_DATA_DIR, "raw_semester_summaries.csv"), index=False)
    
    print(f"[OK] Generated {len(dept_df)} departments")
    print(f"[OK] Generated {len(faculty_df)} faculty members")
    print(f"[OK] Generated {len(courses_df)} courses")
    print(f"[OK] Generated {len(students_df)} students across 5 departments and 4 cohorts")
    print(f"[OK] Generated {len(exam_df)} course exam performance records (Fact Table 1 source)")
    print(f"[OK] Generated {len(att_df)} attendance & engagement records (Fact Table 2 source)")
    print(f"[OK] Generated {len(sem_sum_df)} semester summary snapshots (Fact Table 3 source)")
    print(f"[SUCCESS] All raw source data saved to {RAW_DATA_DIR}")

if __name__ == "__main__":
    main()
