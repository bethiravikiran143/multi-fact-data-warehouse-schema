"""
app.py
------
Streamlit Academic Analytics Dashboard
Working Prototype for Student-Performance Data Warehouse Across Departments
Using A Multi-Fact Data-Warehouse Schema.

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Setup python path to import src modules
SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

import analytics_queries as aq
from risk_model import risk_detector

# Page Configuration
st.set_page_config(
    page_title="Academic Data Warehouse & Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 1.85rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .meta-badge {
        display: inline-block;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 0.85rem;
        color: #334155;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-card h3 {
        margin: 0;
        font-size: 1.8rem;
        color: #0284c7;
    }
    .metric-card p {
        margin: 0;
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# Top Header Banner
# ----------------------------------------------------
st.markdown('<div class="main-header">🎓 Student-Performance Multi-Fact Data Warehouse & Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Design and Development of a Working Prototype for Student-Performance Data Warehouse Across Departments Using A Multi-Fact Schema</div>', unsafe_allow_html=True)

meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)
with meta_col1:
    st.markdown('<div class="meta-badge">👤 <b>Student:</b> BETHI RAVI KIRAN</div>', unsafe_allow_html=True)
with meta_col2:
    st.markdown('<div class="meta-badge">🆔 <b>Roll No:</b> 24ME5A5402 (Sec A)</div>', unsafe_allow_html=True)
with meta_col3:
    st.markdown('<div class="meta-badge">👨‍🏫 <b>Guide:</b> Mr. K. Rajendra</div>', unsafe_allow_html=True)
with meta_col4:
    st.markdown('<div class="meta-badge">🏛️ <b>Domain:</b> Big Data Analytics & DW</div>', unsafe_allow_html=True)

st.markdown("---")

# ----------------------------------------------------
# Sidebar Filters & Controls
# ----------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/database.png", width=64)
st.sidebar.title("OLAP Slicing Controls")

departments = ["ALL", "CSE", "AIDS", "ECE", "MECH", "CIVIL"]
selected_dept = st.sidebar.selectbox("Filter Department:", departments)

cohorts = ["ALL", "2021-2025", "2022-2026", "2023-2027", "2024-2028"]
selected_cohort = st.sidebar.selectbox("Filter Cohort Batch:", cohorts)

st.sidebar.markdown("---")
st.sidebar.subheader("Warehouse Architecture")
st.sidebar.info("""
**Multi-Fact Galaxy Schema:**
- **Fact 1:** Fact_Exam_Performance
- **Fact 2:** Fact_Attendance_Engagement
- **Fact 3:** Fact_Semester_Summary
- **Conformed Dims:** Dim_Student, Dim_Course, Dim_Department, Dim_Time_Semester, Dim_Faculty
""")

# Re-run ETL button if needed
if st.sidebar.button("🔄 Reload / Re-sync Warehouse"):
    with st.spinner("Executing ETL Pipeline..."):
        from etl_pipeline import run_etl
        run_etl()
    st.sidebar.success("Warehouse re-synced successfully!")

# ----------------------------------------------------
# Main Tabs Navigation
# ----------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Institutional Overview",
    "🔍 Cohort & Course Drill-Down",
    "📈 Multi-Fact Cross Analysis",
    "⚠️ Risk Early Warning (ML)",
    "👤 Student 360° Profile",
    "🏛️ Schema Architecture"
])

# ----------------------------------------------------
# TAB 1: Institutional Overview
# ----------------------------------------------------
with tab1:
    st.subheader("Institutional Executive Summary Across Departments")
    dept_df = aq.get_department_overview()

    total_students = int(dept_df["total_students"].sum())
    overall_avg_sgpa = round(dept_df["avg_sgpa"].mean(), 2)
    overall_pass_rate = round(dept_df["overall_pass_rate"].mean(), 1)
    overall_att_avg = round(dept_df["avg_attendance"].mean(), 1)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><h3>{total_students}</h3><p>Total Active Students</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><h3>{overall_avg_sgpa} / 10</h3><p>Institutional Mean SGPA</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><h3>{overall_pass_rate}%</h3><p>Overall Exam Pass Rate</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><h3>{overall_att_avg}%</h3><p>Average Attendance</p></div>', unsafe_allow_html=True)

    st.markdown("### Department Performance Benchmarking")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig_sgpa = px.bar(
            dept_df,
            x="dept_code",
            y="avg_sgpa",
            color="dept_code",
            text="avg_sgpa",
            title="Mean SGPA by Department",
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={"dept_code": "Department", "avg_sgpa": "Average SGPA"}
        )
        fig_sgpa.update_traces(textposition="outside")
        fig_sgpa.update_layout(showlegend=False, yaxis_range=[0, 10])
        st.plotly_chart(fig_sgpa, use_container_width=True)

    with col_chart2:
        fig_pass = px.bar(
            dept_df,
            x="dept_code",
            y="overall_pass_rate",
            color="dept_code",
            text="overall_pass_rate",
            title="Course Pass Percentage (%) by Department",
            color_discrete_sequence=px.colors.qualitative.Prism,
            labels={"dept_code": "Department", "overall_pass_rate": "Pass Rate (%)"}
        )
        fig_pass.update_traces(textposition="outside")
        fig_pass.update_layout(showlegend=False, yaxis_range=[0, 105])
        st.plotly_chart(fig_pass, use_container_width=True)

    st.markdown("### Department Summary Metric Mart")
    st.dataframe(
        dept_df.rename(columns={
            "dept_code": "Code",
            "dept_name": "Department Name",
            "hod_name": "Head of Department (HOD)",
            "total_students": "Students",
            "avg_sgpa": "Avg SGPA",
            "avg_attendance": "Attendance %",
            "overall_pass_rate": "Pass Rate %",
            "avg_marks": "Avg Marks",
            "high_risk_instances": "At-Risk Instances"
        }),
        use_container_width=True,
        hide_index=True
    )

# ----------------------------------------------------
# TAB 2: Cohort & Course Drill-Down Analytics
# ----------------------------------------------------
with tab2:
    st.subheader("Cohort Progression & Course Difficulty Drill-Down")
    
    col_prog1, col_prog2 = st.columns([1, 1])
    prog_df = aq.get_cohort_progression(dept_filter=selected_dept)

    with col_prog1:
        st.markdown(f"#### SGPA Trajectory by Cohort ({selected_dept})")
        if not prog_df.empty:
            fig_prog = px.line(
                prog_df,
                x="semester_name",
                y="avg_sgpa",
                color="cohort_batch",
                markers=True,
                title="SGPA Progression Across Semesters",
                labels={"semester_name": "Semester", "avg_sgpa": "Avg SGPA", "cohort_batch": "Cohort Batch"}
            )
            fig_prog.update_layout(yaxis_range=[5, 9.5])
            st.plotly_chart(fig_prog, use_container_width=True)
        else:
            st.info("No cohort progression data found for selected filter.")

    with col_prog2:
        st.markdown(f"#### Backlog Frequency by Semester ({selected_dept})")
        if not prog_df.empty:
            fig_backlog = px.bar(
                prog_df,
                x="semester_name",
                y="total_backlogs",
                color="cohort_batch",
                barmode="group",
                title="Total Backlogs Incurred Across Semesters",
                labels={"semester_name": "Semester", "total_backlogs": "Backlogs Count", "cohort_batch": "Cohort"}
            )
            st.plotly_chart(fig_backlog, use_container_width=True)

    st.markdown("---")
    st.markdown(f"### Subject-Level Course Difficulty Matrix ({selected_dept})")
    st.caption("Drill down into individual course pass percentages, average marks, and backlog counts.")

    course_df = aq.get_course_difficulty_analysis(dept_filter=selected_dept)
    
    col_c1, col_c2 = st.columns([2, 1])
    with col_c1:
        fig_course = px.scatter(
            course_df,
            x="avg_attendance",
            y="pass_percentage",
            size="enrollments",
            color="dept_code",
            hover_name="course_name",
            text="course_code",
            title="Course Difficulty: Attendance vs Pass Percentage",
            labels={"avg_attendance": "Average Attendance (%)", "pass_percentage": "Pass Percentage (%)"}
        )
        fig_course.update_traces(textposition="top center")
        st.plotly_chart(fig_course, use_container_width=True)

    with col_c2:
        st.markdown("#### Toughest Courses (Lowest Pass %)")
        lowest_pass = course_df.sort_values(by="pass_percentage").head(6)[["course_code", "course_name", "pass_percentage", "backlog_count"]]
        st.dataframe(lowest_pass, use_container_width=True, hide_index=True)

    with st.expander("📄 View Full Course Catalog Performance"):
        st.dataframe(course_df, use_container_width=True, hide_index=True)

# ----------------------------------------------------
# TAB 3: Multi-Fact Cross-Join Analysis
# ----------------------------------------------------
with tab3:
    st.subheader("Multi-Fact Constellation Cross-Join Analysis")
    st.caption("Directly correlates Fact_Exam_Performance with Fact_Attendance_Engagement across shared conformed dimensions.")

    multi_fact_df = aq.get_multi_fact_correlation(dept_filter=selected_dept, cohort_filter=selected_cohort)

    mf_col1, mf_col2 = st.columns([1, 1])

    with mf_col1:
        st.markdown("#### Attendance Percentage vs Final Total Marks")
        fig_scatter = px.scatter(
            multi_fact_df,
            x="attendance_pct",
            y="total_marks",
            color="letter_grade",
            title="Impact of Class Attendance on Final Marks (OLAP Drill-Across)",
            labels={"attendance_pct": "Class Attendance (%)", "total_marks": "Total Exam Marks (out of 100)"},
            hover_data=["student_name", "course_name", "dept_code"]
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with mf_col2:
        st.markdown("#### Marks Distribution by Attendance Bracket")
        # Bucket attendance
        multi_fact_df["attendance_bracket"] = pd.cut(
            multi_fact_df["attendance_pct"],
            bins=[0, 65, 75, 85, 100],
            labels=["<65% (Detention Risk)", "65-75% (Condonation)", "75-85% (Good)", ">85% (Excellent)"]
        )
        fig_box = px.box(
            multi_fact_df,
            x="attendance_bracket",
            y="total_marks",
            color="attendance_bracket",
            title="Exam Mark Spread by Attendance Risk Brackets",
            labels={"attendance_bracket": "Attendance Bracket", "total_marks": "Exam Marks"}
        )
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("#### Grade Distribution Count across Courses")
    grade_counts = multi_fact_df["letter_grade"].value_counts().reindex(["O", "A+", "A", "B+", "B", "C", "F"]).reset_index()
    grade_counts.columns = ["Letter Grade", "Frequency"]
    fig_grade = px.bar(
        grade_counts,
        x="Letter Grade",
        y="Frequency",
        color="Letter Grade",
        text="Frequency",
        title="Institutional Grade Spectrum",
        color_discrete_map={"O": "#10b981", "A+": "#3b82f6", "A": "#6366f1", "B+": "#8b5cf6", "B": "#eab308", "C": "#f97316", "F": "#ef4444"}
    )
    st.plotly_chart(fig_grade, use_container_width=True)

# ----------------------------------------------------
# TAB 4: Student Risk Early Warning System (ML)
# ----------------------------------------------------
with tab4:
    st.subheader("Student Academic Risk Early Warning & Intervention System")
    st.markdown("Empowered by a **Random Forest Classifier** trained directly on the Multi-Fact warehouse facts.")

    col_sim, col_res = st.columns([1, 1])

    with col_sim:
        st.markdown("### 🎛️ Interactive What-If Risk Simulator")
        sim_att = st.slider("Class Attendance Percentage (%)", min_value=30.0, max_value=100.0, value=68.0, step=0.5)
        sim_int = st.slider("Mid-Term Internal Marks (out of 30)", min_value=0.0, max_value=30.0, value=14.0, step=0.5)
        sim_ass = st.slider("LMS Assignment Submission Rate (%)", min_value=0.0, max_value=100.0, value=60.0, step=1.0)

        pred_result = risk_detector.predict_risk(sim_att, sim_int, sim_ass)

    with col_res:
        st.markdown("### 🔮 Predicted Academic Outcome")
        fail_prob = pred_result["failure_probability_pct"]
        cat = pred_result["risk_category"]
        color = pred_result["color"]
        rec = pred_result["recommendation"]

        # Gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fail_prob,
            title={'text': f"Failure / Detention Probability ({cat})"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 30], 'color': "#dcfce7"},
                    {'range': [30, 60], 'color': "#fef3c7"},
                    {'range': [60, 100], 'color': "#fee2e2"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 60
                }
            }
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown(f"**Recommended Intervention Action:**")
        st.info(f"💡 {rec}")

    st.markdown("---")
    st.markdown("### 🚨 Active At-Risk Students Registry (Multi-Fact DW Identification)")
    risk_filter = st.selectbox("Filter Risk Level:", ["ALL", "High", "Medium", "Low"])
    risk_df = aq.get_at_risk_students(dept_filter=selected_dept, risk_filter=risk_filter)

    st.write(f"Showing **{len(risk_df)}** student semester snapshots matching criteria.")
    st.dataframe(risk_df.head(100), use_container_width=True, hide_index=True)

    csv_data = risk_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export At-Risk Registry (CSV)",
        data=csv_data,
        file_name=f"at_risk_students_{selected_dept}.csv",
        mime="text/csv"
    )

# ----------------------------------------------------
# TAB 5: Student 360° Profile
# ----------------------------------------------------
with tab5:
    st.subheader("Student 360° Comprehensive Academic Profile")
    
    # Get all roll numbers
    conn = aq.get_connection()
    all_rolls = pd.read_sql("SELECT roll_no, student_name, dept_code FROM dim_student ORDER BY roll_no", conn)
    conn.close()

    roll_options = all_rolls["roll_no"].tolist()
    # Default to user's roll number if present!
    default_idx = roll_options.index("24ME5A5402") if "24ME5A5402" in roll_options else 0
    selected_roll = st.selectbox("Search & Select Student by Roll Number:", roll_options, index=default_idx)

    stu_info, sem_history, course_history = aq.get_student_360_profile(selected_roll)

    if stu_info:
        st.markdown("#### Student Metadata Card")
        c_p1, c_p2, c_p3, c_p4 = st.columns(4)
        with c_p1:
            st.write(f"**Name:** {stu_info['student_name']}")
            st.write(f"**Roll Number:** `{stu_info['roll_no']}`")
        with c_p2:
            st.write(f"**Department:** {stu_info['dept_name']} ({stu_info['dept_code']})")
            st.write(f"**Cohort Batch:** {stu_info['cohort_batch']}")
        with c_p3:
            st.write(f"**Admission Type:** {stu_info['admission_type']}")
            st.write(f"**Current Status:** `{stu_info['academic_status']}`")
        with c_p4:
            st.write(f"**Current Year:** Year {stu_info['current_year']}")
            st.write(f"**Semester:** Sem {stu_info['current_semester']}")

        st.markdown("---")
        st.markdown("#### Semester-by-Semester Progression")
        
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            fig_stu_prog = px.line(
                sem_history,
                x="semester_name",
                y="sgpa",
                markers=True,
                title="SGPA Trajectory",
                labels={"semester_name": "Semester", "sgpa": "SGPA"}
            )
            fig_stu_prog.update_layout(yaxis_range=[0, 10])
            st.plotly_chart(fig_stu_prog, use_container_width=True)

        with col_t2:
            fig_stu_att = px.bar(
                sem_history,
                x="semester_name",
                y="sem_attendance_avg",
                text="sem_attendance_avg",
                color="sem_attendance_avg",
                color_continuous_scale="RdYlGn",
                range_color=[50, 100],
                title="Average Attendance % Across Semesters",
                labels={"semester_name": "Semester", "sem_attendance_avg": "Attendance %"}
            )
            fig_stu_att.update_traces(textposition="outside")
            st.plotly_chart(fig_stu_att, use_container_width=True)

        st.markdown("#### Multi-Fact Detailed Course Transcript")
        st.dataframe(
            course_history.rename(columns={
                "semester_name": "Semester",
                "course_code": "Code",
                "course_name": "Subject Name",
                "credits": "Credits",
                "course_type": "Type",
                "internal_marks": "Internal (30)",
                "external_marks": "External (70)",
                "total_marks": "Total (100)",
                "grade_point": "Grade Pt",
                "letter_grade": "Grade",
                "is_passed": "Passed",
                "classes_attended": "Attended",
                "total_classes": "Total Classes",
                "attendance_pct": "Att %",
                "assignment_score_pct": "LMS Score %",
                "faculty_name": "Faculty Instructor"
            }),
            use_container_width=True,
            hide_index=True
        )

# ----------------------------------------------------
# TAB 6: Data Warehouse Architecture & Schema Visualizer
# ----------------------------------------------------
with tab6:
    st.subheader("Multi-Fact Constellation Schema (Galaxy Architecture)")
    st.markdown("""
    In Kimball dimensional modeling, an academic institution is best modeled as a **Multi-Fact Constellation (Galaxy Schema)**.
    Multiple business processes generate measurements at different grains, but share **Conformed Dimensions**.
    """)

    st.markdown("""
    ```
                      +-------------------+
                      |   DIM_STUDENT     |
                      | (Student_Key PK)  |
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
    | (Course_Key PK)|    | (Dept_Key PK) |    |  (Time_Key PK)    |
    +----------------+    +---------------+    +-------------------+
    ```
    """)

    st.markdown("### Warehouse Storage & Volume Metrics")
    metrics = aq.get_warehouse_storage_metrics()
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.markdown("#### Conformed Dimensions")
        st.write(f"- **Dim_Department:** {metrics['dim_department']} records")
        st.write(f"- **Dim_Faculty:** {metrics['dim_faculty']} records")
        st.write(f"- **Dim_Course:** {metrics['dim_course']} records")
        st.write(f"- **Dim_Time_Semester:** {metrics['dim_time_semester']} records")
        st.write(f"- **Dim_Student:** {metrics['dim_student']} records")
    with c_m2:
        st.markdown("#### Fact Tables")
        st.write(f"- **Fact_Exam_Performance:** {metrics['fact_exam_performance']:,} facts")
        st.write(f"- **Fact_Attendance_Engagement:** {metrics['fact_attendance_engagement']:,} facts")
        st.write(f"- **Fact_Semester_Summary:** {metrics['fact_semester_summary']:,} periodic snapshots")
    with c_m3:
        db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "warehouse", "academic_dw.db")
        db_size_kb = round(os.path.getsize(db_file) / 1024, 1) if os.path.exists(db_file) else 0
        st.markdown("#### Database Engine")
        st.write(f"- **Storage Engine:** SQLite 3 OLAP Mart")
        st.write(f"- **Database Size:** {db_size_kb} KB")
        st.write(f"- **Indexing:** B-Tree Foreign Key Indexes Active")

    st.markdown("---")
    st.markdown("### 💻 Interactive Live OLAP SQL Query Console")
    st.caption("Execute custom SQL queries against the multi-fact schema.")
    
    default_query = """SELECT 
    d.dept_code,
    c.course_type,
    COUNT(fep.performance_key) AS enrollments,
    ROUND(AVG(fep.total_marks), 2) AS mean_marks,
    ROUND(AVG(fae.attendance_pct), 2) AS mean_attendance,
    ROUND(SUM(CASE WHEN fep.is_passed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(fep.performance_key), 1) AS pass_pct
FROM fact_exam_performance fep
JOIN fact_attendance_engagement fae 
    ON fep.student_key = fae.student_key 
    AND fep.course_key = fae.course_key 
    AND fep.time_key = fae.time_key
JOIN dim_department d ON fep.department_key = d.department_key
JOIN dim_course c ON fep.course_key = c.course_key
GROUP BY d.dept_code, c.course_type
ORDER BY d.dept_code, pass_pct DESC;"""

    user_sql = st.text_area("Enter SQL Query:", value=default_query, height=160)
    if st.button("▶️ Execute Query"):
        try:
            conn = aq.get_connection()
            result_df = pd.read_sql(user_sql, conn)
            conn.close()
            st.success(f"Query returned {len(result_df)} rows.")
            st.dataframe(result_df, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")

# ----------------------------------------------------
# Footer
# ----------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94a3b8; font-size: 0.85rem;'>"
    "Academic Performance Multi-Fact Data Warehouse & Analytics | Bethi Ravi Kiran (24ME5A5402) | Supervised by Mr. K. Rajendra"
    "</div>",
    unsafe_allow_html=True
)
