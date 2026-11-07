# Student Performance Multi-Fact Data Warehouse & Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E.svg)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3%20OLAP-003B57.svg)](https://www.sqlite.org/)
[![Architecture](https://img.shields.io/badge/Schema-Multi--Fact%20Constellation-success.svg)](#warehouse-architecture)

> **Design and Development of a Working Prototype for Student-Performance Data Warehouse Across Departments Using a Multi-Fact Schema.**

---

## 📌 Project Overview

Educational institutions generate massive volumes of heterogeneous data across disparate operational silos (examination branches, attendance logging systems, learning management systems, and departmental administration). Traditional relational (OLTP) databases struggle with complex cross-departmental analytical queries, historical trend tracking, and multi-grain aggregations.

This project implements an end-to-end **Academic Data Warehouse (ADW)** built upon a **Multi-Fact Constellation (Galaxy Schema)** dimensional model following Ralph Kimball's methodology. The system unifies exam evaluation, class attendance, and semester progress into a cohesive analytical repository paired with an interactive **Streamlit OLAP Analytics Dashboard** and a **Machine Learning Risk Early Warning System**.

---

## 🏛️ Warehouse Architecture

The data warehouse employs a **Multi-Fact Constellation Schema** where multiple business processes share standardized **Conformed Dimensions**.

```
                      +-------------------+
                      |   DIM_STUDENT     |
                      | (student_key PK)  |
                      +---------+---------+
                                |
               +----------------+----------------+
               |                                 |
               v                                 v
    +----------------------+          +--------------------------+
    | FACT_EXAM_PERFORMANCE|          | FACT_ATTENDANCE_ENGAGE   |
    |----------------------|          |--------------------------|
    | * student_key (FK)   |          | * student_key (FK)       |
    | * course_key (FK)    |          | * course_key (FK)        |
    | * department_key (FK)|          | * department_key (FK)    |
    | * time_key (FK)      |          | * time_key (FK)          |
    | * faculty_key (FK)   |          |                          |
    | Measures:            |          | Measures:                |
    | - internal_marks     |          | - total_classes          |
    | - external_marks     |          | - classes_attended       |
    | - total_marks        |          | - attendance_pct         |
    | - grade_point        |          | - condonation_risk_flag  |
    | - is_passed          |          | - detention_risk_flag    |
    | - is_backlog         |          | - assignment_score_pct   |
    +----------+-----------+          +------------+-------------+
               |                                   |
               +----------------+------------------+
                                |
                   +------------+------------+
                   |       CONFORMED         |
                   |       DIMENSIONS        |
                   +------------+------------+
                                |
        +-----------------------+-----------------------+
        |                       |                       |
        v                       v                       v
    +----------------+    +---------------+    +-------------------+
    |  DIM_COURSE    |    |DIM_DEPARTMENT |    | DIM_TIME_SEMESTER |
    | (course_key PK)|    | (dept_key PK) |    |  (time_key PK)    |
    +----------------+    +---------------+    +-------------------+
```

### Fact Tables
1. **`fact_exam_performance`** (Transaction Fact):
   - **Grain**: One row per student, per course, per semester.
   - **Measures**: `internal_marks`, `external_marks`, `total_marks`, `grade_point`, `is_passed`, `is_backlog`.
2. **`fact_attendance_engagement`** (Periodic Accumulating Fact):
   - **Grain**: One row per student, per course, per semester.
   - **Measures**: `total_classes`, `classes_attended`, `attendance_pct`, `assignment_score_pct`, `condonation_risk_flag`, `detention_risk_flag`.
3. **`fact_semester_summary`** (Periodic Snapshot Fact):
   - **Grain**: One row per student, per semester.
   - **Measures**: `sgpa`, `cgpa`, `credits_registered`, `credits_earned`, `sem_attendance_avg`, `backlogs_in_sem`, `risk_level`.

### Conformed Dimensions
- **`dim_student`**: Student demographic and enrollment details (`roll_no`, `student_name`, `gender`, `cohort_batch`, `admission_type`, `current_semester`).
- **`dim_course`**: Academic catalog details (`course_code`, `course_name`, `credits`, `course_type`, `syllabus_regulation`).
- **`dim_department`**: Academic units (`dept_code`, `dept_name`, `hod_name`, `intake_capacity`).
- **`dim_time_semester`**: Temporal hierarchy (`academic_year`, `semester_number`, `semester_name`, `term_type`).
- **`dim_faculty`**: Instructional personnel (`faculty_code`, `faculty_name`, `designation`).

---

## 🚀 Key Features & Modules

### 1. Interactive Streamlit Analytics Dashboard (`app.py`)
- **📊 Tab 1: Institutional Overview**:
  - Executive KPI metrics: Active students, institutional mean SGPA, exam pass rate, and campus-wide attendance.
  - Cross-department performance benchmarking and pass-percentage comparisons.
- **🔍 Tab 2: Cohort & Course Drill-Down**:
  - Longitudinal cohort progression curves (tracking SGPA trajectories across Semesters 1 to 8).
  - Backlog accumulation analysis grouped by cohort batch.
  - Course Difficulty Matrix identifying high-attrition/low-pass-rate subjects.
- **📈 Tab 3: Multi-Fact Cross Analysis**:
  - OLAP Drill-Across correlating `fact_exam_performance` and `fact_attendance_engagement`.
  - Attendance vs. Final Marks scatter plots and box plots categorized by attendance risk brackets (`<65%`, `65-75%`, `75-85%`, `>85%`).
  - Institutional Letter Grade Distribution spectrum (`O`, `A+`, `A`, `B+`, `B`, `C`, `F`).
- **⚠️ Tab 4: Student Risk Early Warning System (ML)**:
  - Real-time **What-If Risk Simulator** powered by a Random Forest Classifier.
  - Probability gauge for academic failure/detention risk with automated intervention recommendations.
  - Downloadable registry of at-risk students for remedial planning (CSV export).
- **👤 Tab 5: Student 360° Profile**:
  - Holistic individual student lookup by Roll Number.
  - Complete academic transcript across semesters, SGPA curves, and course-by-course attendance and marks breakdown.

---

## 🤖 Machine Learning Risk Detector

- **Model**: Random Forest Classifier (`src/risk_model.py`)
- **Input Features**:
  1. `attendance_pct`: Cumulative class attendance percentage.
  2. `internal_marks`: Continuous assessment / mid-term score (out of 30).
  3. `assignment_score_pct`: LMS assignment submission and coursework score (out of 100).
- **Target Classes**:
  - `High Risk`: Attendance < 65% or failing internal assessments (immediate faculty intervention required).
  - `Medium Risk`: Attendance 65–75% (condonation bracket) or borderline performance.
  - `Low Risk`: Good academic standing.

---

## 📁 Repository Structure

```plaintext
multi-fact-data-warehouse-schema/
├── .gitignore                          # Git ignore definitions
├── README.md                           # Project documentation
├── app.py                              # Streamlit Analytics Dashboard
├── requirements.txt                    # Project Python dependencies
├── run_app.bat                         # Quick-launch batch file for Windows
├── data/
│   ├── raw/                            # Source transactional data (CSV format)
│   │   ├── raw_students.csv
│   │   ├── raw_departments.csv
│   │   ├── raw_faculty.csv
│   │   ├── raw_courses.csv
│   │   ├── raw_time_semesters.csv
│   │   ├── raw_exam_scores.csv
│   │   ├── raw_attendance_records.csv
│   │   └── raw_semester_summaries.csv
│   └── warehouse/
│       └── academic_dw.db              # SQLite Data Warehouse (Star/Galaxy Schema)
└── src/
    ├── __init__.py
    ├── warehouse_schema.py             # DDL script creating dimension & fact tables
    ├── generate_raw_data.py            # Synthetic academic dataset generator
    ├── etl_pipeline.py                 # ETL script: Extracts, Transforms & Loads to DW
    ├── analytics_queries.py            # OLAP analytics & dimensional query engine
    └── risk_model.py                   # Machine learning risk classification model
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python **3.10** or higher
- Git installed on your system

### 2. Clone the Repository
```bash
git clone https://github.com/bethiravikiran143/multi-fact-data-warehouse-schema.git
cd multi-fact-data-warehouse-schema
```

### 3. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚡ Running the Project

### Option A: Using the Windows Batch Launcher
Double-click `run_app.bat` or run:
```cmd
run_app.bat
```
*(This script checks for the database, runs the ETL pipeline if needed, and launches Streamlit automatically).*

### Option B: Manual Execution via Terminal

1. **(Optional) Re-generate raw data & execute ETL:**
   ```bash
   python src/generate_raw_data.py
   python src/etl_pipeline.py
   ```

2. **Launch the Streamlit Analytics Application:**
   ```bash
   streamlit run app.py
   ```

3. **Access Dashboard in Browser:**
   Open: [`http://localhost:8501`](http://localhost:8501)

---

## 📊 Supported OLAP Operations

| OLAP Operation | Description | Implementation in System |
| :--- | :--- | :--- |
| **Roll-Up** | Aggregates fine-grained measures to higher levels | Course-level exam scores aggregated to Semester SGPA and Departmental Pass Rates. |
| **Drill-Down** | De-aggregates summary data into granular detail | Department summary $\rightarrow$ Cohort $\rightarrow$ Specific Course $\rightarrow$ Individual Student Transcript. |
| **Slice** | Selects a single dimension member | Filtering metrics by a specific Department (e.g., `CSE`, `ECE`, `AIDS`, `MECH`, `CIVIL`). |
| **Dice** | Selects a sub-cube spanning multiple dimensions | Slicing by Department = `CSE` AND Cohort = `2022-2026`. |
| **Drill-Across** | Joins across multiple fact tables using conformed dimensions | Correlating `fact_exam_performance` with `fact_attendance_engagement` on shared student and course keys. |

---

## 📜 Technology Stack

- **Data Warehousing & Dimensional Modeling**: Kimball Methodology, Multi-Fact Galaxy Schema
- **Database Engine**: SQLite 3 with B-Tree Foreign Key Indexes
- **ETL Pipeline**: Python (`pandas`, `numpy`, surrogate key mapping & cleansing)
- **Data Visualization & Dashboard**: Streamlit, Plotly Express & Plotly Graph Objects
- **Predictive Analytics**: Scikit-Learn (`RandomForestClassifier`)

---

## 📄 License
This project is developed for educational, academic, and research purposes.
