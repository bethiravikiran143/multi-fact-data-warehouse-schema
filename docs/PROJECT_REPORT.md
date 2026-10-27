# ACADEMIC MINI PROJECT REPORT

## Design and Development of a Working Prototype for Student-Performance Data Warehouse Across Departments Using a Multi-Fact Data-Warehouse Schema

---

### Project Metadata
- **Domain:** Big Data Analytics, Data Warehousing & Visualization
- **Scope:** Institutional Multi-Department Data Warehouse Prototype
- **Academic Year:** 2024–2026

---

## 1. ABSTRACT

Modern higher education institutions capture vast volumes of student records scattered across isolated systems, including examination management portals, biometric attendance logs, and learning management systems (LMS). Traditional transactional databases (OLTP) are optimized for daily operational updates but perform poorly when performing cross-departmental, multi-semester analytical queries. Furthermore, attempts to model institutional performance in a single monolithic star schema fail due to divergent business event granularities (e.g., continuous daily attendance vs. semester-end exam results).

This project implements a **Multi-Fact Data Warehouse Schema (Fact Constellation / Galaxy Schema)** to enable high-performance drill-down, roll-up, and slice-and-dice analytics across academic departments (CSE, AIDS, ECE, MECH, CIVIL) and 4 cohorts (2021-2025, 2022-2026, 2023-2027, 2024-2028). The architecture incorporates shared conformed dimensions (`Dim_Student`, `Dim_Course`, `Dim_Department`, `Dim_Time_Semester`, `Dim_Faculty`) linked with two atomic transaction fact tables (`Fact_Exam_Performance`, `Fact_Attendance_Engagement`) and a periodic snapshot fact table (`Fact_Semester_Summary`). An automated ETL pipeline cleans, normalizes, transforms, and loads institutional data into an indexed OLAP repository. 

Additionally, an embedded **Random Forest Risk Classifier** achieves **82.61% accuracy** in predicting course failure and detention risks from early attendance and internal exam signals. The entire working prototype is delivered as an interactive, production-grade **Academic Analytics Dashboard** using Streamlit and Plotly, providing department heads, mentors, and administrators with actionable insights to intervene early and enhance academic performance beyond the classroom.

---

## 2. INTRODUCTION & PROBLEM STATEMENT

### 2.1 Background
Educational institutions operate across distinct departments, each managing hundreds of students across 4-year degree programs. Data regarding student grades, attendance, assignment submissions, and backlogs are traditionally locked in transactional database silos. 

### 2.2 The Problem
1. **Cross-Departmental Blindspots:** University leadership and HODs lack a centralized view to compare academic standards, faculty load, and student pass percentages across departments.
2. **Incompatible Granularity in Star Schemas:** Forcing attendance (collected daily or cumulatively per course) and exam results (final summative marks) into a single star schema fact table causes fact duplication and cartesian fanning.
3. **Reactive Rather Than Proactive Remediation:** Students with deteriorating attendance and poor internal marks are typically identified only after semester results are published, by which time failure or detention is unavoidable.

### 2.3 Proposed Solution
We design and develop a complete working prototype consisting of:
1. A **Multi-Fact Constellation Data Warehouse** that models distinct academic processes while sharing standardized conformed dimensions.
2. An automated **Python ETL Pipeline** with data quality validation and surrogate key management.
3. An **Early Warning Machine Learning Model** predicting student failure and detention risk.
4. An interactive **Streamlit Academic Analytics Dashboard** featuring 6 specialized modules with drill-down and SQL console capabilities.

---

## 3. MULTI-FACT DATA WAREHOUSE SCHEMA & DIMENSIONAL MODELING

```
+------------------------------------------------------------------------------------+
|                               ETL PIPELINE (Python)                                |
|  Raw CSV Feeds -> Validation -> Surrogate Key Mapping -> Dimension & Fact Loading  |
+------------------------------------------------------------------------------------+
                                         |
                                         v
+------------------------------------------------------------------------------------+
|                         MULTI-FACT CONSTELLATION SCHEMA                            |
|                                                                                    |
|       +------------------------------------+   +---------------------------------+ |
|       |     FACT_EXAM_PERFORMANCE          |   |   FACT_ATTENDANCE_ENGAGEMENT    | |
|       |------------------------------------|   |---------------------------------| |
|       | * student_key (FK)                 |   | * student_key (FK)              | |
|       | * course_key (FK)                  |   | * course_key (FK)               | |
|       | * department_key (FK)              |   | * department_key (FK)           | |
|       | * time_key (FK)                    |   | * time_key (FK)                 | |
|       | * faculty_key (FK)                 |   | Measures:                       | |
|       | Measures:                          |   | - total_classes                 | |
|       | - internal_marks, external_marks   |   | - classes_attended              | |
|       | - total_marks, grade_point, grade  |   | - attendance_pct                | |
|       | - is_passed, is_backlog            |   | - is_condonation/detention_risk | |
|       +-----------------+------------------+   +----------------+----------------+ |
|                         |                                       |                  |
|                         +-------------------+-------------------+                  |
|                                             |                                      |
|                                             v                                      |
|                             +-------------------------------+                      |
|                             |      CONFORMED DIMENSIONS     |                      |
|                             |-------------------------------|                      |
|                             | * Dim_Student                 |                      |
|                             | * Dim_Department              |                      |
|                             | * Dim_Course                  |                      |
|                             | * Dim_Time_Semester           |                      |
|                             | * Dim_Faculty                 |                      |
|                             +---------------+---------------+                      |
|                                             |                                      |
|                         +-------------------+-------------------+                  |
|                         |                                       |                  |
|                         v                                       v                  |
|       +------------------------------------+   +---------------------------------+ |
|       |       FACT_SEMESTER_SUMMARY        |   |    B-TREE ACCELERATION INDEXES  | |
|       | (Periodic Snapshot Fact Table)     |   | Fast OLAP Joins & Slicing       | |
|       | - credits_reg, credits_earned      |   +---------------------------------+ |
|       | - sgpa, cgpa, backlogs_in_sem      |                                       |
|       +------------------------------------+                                       |
+------------------------------------------------------------------------------------+
                                         |
                                         v
+------------------------------------------------------------------------------------+
|                    INTERACTIVE STREAMLIT ANALYTICS DASHBOARD                       |
|   Executive KPI Mart | HOD Warm Alerts | Student Admin | ML Risk Early Warning     |
|   Cohort Progression | Galaxy Join     | Course Difficulty Matrix                  |
+------------------------------------------------------------------------------------+
```

---

## 4. IMPLEMENTATION MODULES

### 4.1 Module 1: Synthetic Institutional Data Generator (`src/generate_raw_data.py`)
- Simulates realistic multi-department data across **5 engineering branches**:
  - Mechanical Engineering (`MECH`)
  - Computer Science & Engineering (`CSE`)
  - Artificial Intelligence & Data Science (`AIDS`)
  - Electronics & Communication Engineering (`ECE`)
  - Civil Engineering (`CIVIL`)
- Generates data for **4 distinct cohorts** (`2021-2025`, `2022-2026`, `2023-2027`, `2024-2028`).
- Modeled realistic non-linear correlations: attendance strictly impacts internal assessment marks and probability of examination failure.

### 4.2 Module 2: Automated ETL Engine (`src/etl_pipeline.py`)
- **Extraction:** Ingests raw source tables from `data/raw/`.
- **Transformation:** 
  - Validates missing attributes, nulls, and data ranges.
  - Generates integer surrogate primary keys for all conformed dimensions.
  - Maps natural business keys (`roll_no`, `course_code`, `dept_code`, `faculty_id`) to warehouse surrogate foreign keys.
  - Derives OLAP status flags (`is_passed`, `is_backlog`, `is_condonation_risk`, `is_detained_risk`).
- **Loading:** Loads transformed data into SQLite Data Warehouse (`data/warehouse/academic_dw.db`) and constructs B-Tree indexes.

### 4.3 Module 3: OLAP Aggregations & Query Engine (`src/analytics_queries.py`)
- Employs **Kimball Drill-Across** using SQL Common Table Expressions (CTEs) to join multiple fact tables without Cartesian explosion.
- Supports multi-level drill-down:
  `Institution -> Department -> Cohort -> Semester -> Course -> Student`.

### 4.4 Module 4: Machine Learning Early Warning System (`src/risk_model.py`)
- Algorithm: `RandomForestClassifier` (100 estimators, max depth 6).
- Features: `attendance_pct`, `internal_marks`, `assignment_score_pct`, `is_condonation_risk`.
- **Test Set Accuracy:** **82.61%**.
- **Feature Importance Breakdown:**
  - Attendance Percentage: **68.43%** (Dominant predictor)
  - Assignment Completion Score: **15.29%**
  - Mid-Term Internal Marks: **13.00%**
  - Condonation Flag: **3.28%**
- Provides dynamic **What-If simulation** with risk categories:
  - Critical Risk (Red)
  - Moderate Risk (Amber)
  - Safe / Good Standing (Green)

### 4.5 Module 5: Streamlit Web Analytics Dashboard (`app.py`)
Features 6 interactive modules:
1. **Institutional Overview:** Executive KPIs, Department benchmarks (SGPA, Pass %, Attendance).
2. **HOD Attendance Warm Alerts & Notices:** Head of Department portal for tracking low-attendance students (<75% and <65%), calculating consecutive recovery classes needed, and generating official warning notices with registered Student Mobile and Gmail contact channels.
3. **Student Administration (Join/Modify):** Administration portal to admit/enroll new students into the Multi-Fact Data Warehouse with automatic dimension and fact generation, plus full capability to modify existing student records.
4. **Cohort & Course Drill-Down:** SGPA trajectory over 8 semesters, backlog frequency bar charts, course difficulty scatter plots.
5. **Multi-Fact Cross Analysis:** Scatter plots correlating attendance % to final marks, grade distribution spectrum, attendance risk bracket boxplots.
6. **Risk Early Warning (ML):** Interactive sliders for What-If scenario analysis, real-time risk gauge, and downloadable At-Risk roster CSV.

---

## 5. EXPERIMENTAL RESULTS & FINDINGS

### 5.1 Warehouse Data Volumes
| Warehouse Entity | Entity Type | Record Count |
| :--- | :--- | :--- |
| `dim_department` | Conformed Dimension | 5 |
| `dim_faculty` | Conformed Dimension | 17 |
| `dim_course` | Conformed Dimension | 56 |
| `dim_time_semester` | Conformed Dimension | 40 |
| `dim_student` | Conformed Dimension | 397 |
| `fact_exam_performance` | Transaction Fact Table | 5,151 |
| `fact_attendance_engagement` | Transaction Fact Table | 5,151 |
| `fact_semester_summary` | Periodic Snapshot Fact Table | 2,190 |
| **Total Warehouse Facts** | **Multi-Fact Repository** | **12,492** |

### 5.2 Key Analytical Findings
1. **Attendance Threshold Effect:** Students with attendance below 65% had a course failure rate exceeding 68%, whereas students with attendance above 85% achieved a 96.4% pass rate and average SGPA of 8.12.
2. **First-Year Transition Impact:** Semester 1 and Semester 2 exhibit the highest backlog density across all departments (principally in Mathematics and Mechanics/Physics courses).
3. **Early Warning Efficacy:** Using internal mid-term marks and attendance by week 8 of a semester enables the model to identify 85% of at-risk students before final external exams.

---

## 6. CONCLUSION & FUTURE SCOPE

The developed prototype successfully demonstrates how a **Multi-Fact Constellation Schema** solves the limitations of traditional star schemas in institutional analytics. By modeling examination performance, daily engagement, and semester milestones as distinct fact tables sharing conformed dimensions, the system enables high-speed OLAP drill-downs across departments and cohorts.

### Practical Adoption Beyond the Classroom:
1. **Institutional Accreditation (NAAC / NBA):** Instant generation of criterion-level academic outcomes, pass rates, and cohort progression reports.
2. **Proactive Mentorship Interventions:** Automated attendance warm alerts generated for mentors and parents to initiate timely counseling whenever a student's attendance drops below thresholds.
3. **Curriculum Revision Insights:** Pinpointing bottleneck courses with historically high backlog rates across multiple cohorts.

---

## 7. REFERENCES
1. Kimball, R., & Ross, M. (2013). *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*. John Wiley & Sons.
2. Inmon, W. H. (2005). *Building the Data Warehouse*. John Wiley & Sons.
3. Romero, C., & Ventura, S. (2010). *Educational Data Mining: A Review of the State of the Art*. IEEE Transactions on Systems, Man, and Cybernetics.
4. Streamlit Documentation: *Interactive Data Applications in Python* (2024).
5. Scikit-learn: *Machine Learning in Python*, Pedregosa et al., JMLR 12, pp. 2825-2830, 2011.
