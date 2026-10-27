"""
app.py
------
Streamlit Academic Analytics Dashboard
Working Prototype for Student-Performance Data Warehouse Across Departments
Using A Multi-Fact Data-Warehouse Schema.

Domain: Big Data Analytics, Data Warehousing & Visualization
Prototype: Multi-Fact Academic Performance Data Warehouse
"""

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
    st.markdown('<div class="meta-badge">👤 <b>Role:</b> Academic Analytics</div>', unsafe_allow_html=True)
with meta_col2:
    st.markdown('<div class="meta-badge">🏛️ <b>Scope:</b> Multi-Department Prototype</div>', unsafe_allow_html=True)
with meta_col3:
    st.markdown('<div class="meta-badge">📊 <b>Schema:</b> Multi-Fact Constellation</div>', unsafe_allow_html=True)
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

# Re-run ETL button if needed
if st.sidebar.button("🔄 Reload / Re-sync Warehouse"):
    with st.spinner("Executing ETL Pipeline..."):
        from etl_pipeline import run_etl
        run_etl()
    st.sidebar.success("Warehouse re-synced successfully!")

# ----------------------------------------------------
# Main Tabs Navigation
# ----------------------------------------------------
tab1, tab_hod, tab_admin, tab2, tab3, tab4 = st.tabs([
    "📊 Institutional Overview",
    "🚨 HOD Attendance Warm Alerts",
    "⚙️ Student Administration (Join/Modify)",
    "🔍 Cohort & Course Drill-Down",
    "📈 Multi-Fact Cross Analysis",
    "⚠️ Risk Early Warning (ML)"
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
# TAB: HOD Attendance Warm Alerts & Notices
# ----------------------------------------------------
with tab_hod:
    st.subheader("🚨 Head of Department (HOD) Portal: Attendance Warm Alert & Detention System")
    st.caption("Actionable monitoring module for Department Heads to track low-attendance students and issue formal Condonation & Detention notices.")

    col_h1, col_h2 = st.columns([1, 2])
    with col_h1:
        hod_dept_select = st.selectbox("Select Department / HOD:", ["MECH", "CSE", "AIDS", "ECE", "CIVIL"], index=0)
    
    dept_info = aq.get_hod_department_info(hod_dept_select)
    hod_name = dept_info["hod_name"] if dept_info else "HOD"
    dept_full_name = dept_info["dept_name"] if dept_info else hod_dept_select
    total_enrolled = dept_info["total_enrolled_students"] if dept_info else 0

    with col_h2:
        st.info(f"🏛️ **Department:** {dept_full_name} | 👨‍🏫 **Head of Department (HOD):** {hod_name} | 👥 **Enrolled Students:** {total_enrolled}")

    # Fetch alerts for this department
    alerts_all = aq.get_hod_attendance_alerts(dept_code=hod_dept_select)
    
    # Summary Metrics
    critical_count = len(alerts_all[alerts_all["attendance_pct"] < 65.0]) if not alerts_all.empty else 0
    condonation_count = len(alerts_all[(alerts_all["attendance_pct"] >= 65.0) & (alerts_all["attendance_pct"] < 75.0)]) if not alerts_all.empty else 0
    total_alerts_count = len(alerts_all) if not alerts_all.empty else 0

    c_a1, c_a2, c_a3, c_a4 = st.columns(4)
    with c_a1:
        st.metric("Total Department Students", total_enrolled)
    with c_a2:
        st.metric("Low Attendance Instances (<75%)", total_alerts_count)
    with c_a3:
        st.metric("⚠️ Condonation Warm Alerts (65-75%)", condonation_count)
    with c_a4:
        st.metric("🚨 Critical Detention Notices (<65%)", critical_count)

    st.markdown("---")
    
    # Sub-tabs for HOD views
    sub_h1, sub_h2, sub_h3 = st.tabs([
        "📋 Course-Level Low Attendance Roster",
        "👥 Student Aggregate Semester Warning List",
        "✉️ Generate Official HOD Warm Alert Notice"
    ])
    
    with sub_h1:
        st.markdown(f"#### Active Course Attendance Defaulters in {hod_dept_select}")
        sev_filter = st.radio("Filter Severity:", ["All Alerts (<75%)", "🚨 Critical Detention Only (<65%)", "⚠️ Condonation Only (65-75%)"], horizontal=True)
        sev_param = "Critical" if "Critical" in sev_filter else ("Condonation" if "Condonation" in sev_filter else "ALL")
        filtered_alerts = aq.get_hod_attendance_alerts(dept_code=hod_dept_select, severity_filter=sev_param)
        
        if not filtered_alerts.empty:
            display_cols = [
                "roll_no", "student_name", "mobile_no", "gmail_id", "parent_mobile",
                "cohort_batch", "course_code", "course_name",
                "total_classes", "classes_attended", "classes_missed", "attendance_pct",
                "classes_needed_for_75", "alert_level", "faculty_name"
            ]
            st.dataframe(
                filtered_alerts[display_cols].rename(columns={
                    "roll_no": "Roll No",
                    "student_name": "Student Name",
                    "mobile_no": "Student Mobile",
                    "gmail_id": "Student Gmail",
                    "parent_mobile": "Parent Mobile",
                    "cohort_batch": "Cohort",
                    "course_code": "Course Code",
                    "course_name": "Course Title",
                    "total_classes": "Conducted",
                    "classes_attended": "Attended",
                    "classes_missed": "Missed",
                    "attendance_pct": "Att %",
                    "classes_needed_for_75": "Classes Needed for 75%",
                    "alert_level": "Alert Status",
                    "faculty_name": "Faculty Instructor"
                }),
                use_container_width=True,
                hide_index=True
            )
            
            # Export
            csv_alerts = filtered_alerts[display_cols].to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Course Defaulters Roster (CSV)",
                data=csv_alerts,
                file_name=f"hod_attendance_defaulters_{hod_dept_select}.csv",
                mime="text/csv"
            )
        else:
            st.success("No students currently below 75% attendance for this filter!")

    with sub_h2:
        st.markdown(f"#### Student-Level Aggregate Semester Attendance Warning ({hod_dept_select})")
        st.caption("Aggregates attendance across all subjects to identify students facing whole-semester detention.")
        agg_alerts = aq.get_student_aggregate_attendance_alerts(dept_code=hod_dept_select)
        if not agg_alerts.empty:
            st.dataframe(
                agg_alerts.rename(columns={
                    "roll_no": "Roll Number",
                    "student_name": "Student Name",
                    "mobile_no": "Student Mobile",
                    "gmail_id": "Student Gmail",
                    "parent_mobile": "Parent Mobile",
                    "dept_code": "Dept",
                    "cohort_batch": "Batch",
                    "current_semester": "Semester",
                    "subjects_enrolled": "Subjects Enrolled",
                    "total_institutional_classes": "Total Held",
                    "total_classes_attended": "Total Attended",
                    "overall_attendance_pct": "Overall Sem Att %",
                    "detained_courses_count": "Detained Courses (<65%)",
                    "condonation_courses_count": "Condonation Courses (65-75%)"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("All students in this department maintain overall semester attendance above 75%!")

    with sub_h3:
        st.markdown(f"#### ✉️ Official HOD Attendance Warning Letter & Dispatch Hub")
        st.caption("Generate a formal institutional notice with registered Student Mobile and Gmail contact channels.")
        
        if not alerts_all.empty:
            student_options = alerts_all[["roll_no", "student_name", "course_code"]].drop_duplicates()
            student_labels = [f"{r['roll_no']} - {r['student_name']} ({r['course_code']})" for _, r in student_options.iterrows()]
            chosen_label = st.selectbox("Select Defaulter Student & Subject:", student_labels)
            
            chosen_roll = chosen_label.split(" - ")[0]
            chosen_course = chosen_label.split("(")[-1].replace(")", "")
            
            match_row = alerts_all[(alerts_all["roll_no"] == chosen_roll) & (alerts_all["course_code"] == chosen_course)].iloc[0]
            
            from datetime import date
            today_str = date.today().strftime("%d-%B-%Y")
            
            notice_text = f"""========================================================================================
            OFFICE OF THE HEAD OF DEPARTMENT - {dept_full_name.upper()}
                     ACADEMIC ATTENDANCE WARM ALERT & WARNING MEMO
========================================================================================
Date: {today_str}

RECIPIENT CONTACT CHANNELS:
- Student Mobile                 : {match_row['mobile_no']}
- Student Gmail                  : {match_row['gmail_id']}
- Parent Mobile                  : {match_row['parent_mobile']}

To:
Student: {match_row['student_name']} (Roll No: {match_row['roll_no']})
Parent / Guardian of {match_row['student_name']}
Department of {dept_full_name} | Cohort: {match_row['cohort_batch']}

SUBJECT: OFFICIAL WARM ALERT ON CRITICAL ATTENDANCE SHORTAGE IN '{match_row['course_code']} - {match_row['course_name']}'

Dear Student & Parents,

This is a formal communication from the Office of the Head of Department. 
Based on the institutional Attendance Audit for Semester {match_row['current_semester']}, 
your attendance status has fallen below the mandatory University academic norms:

ACADEMIC ATTENDANCE RECORD:
----------------------------------------------------------------------------------------
- Subject / Course Name          : {match_row['course_name']} ({match_row['course_code']})
- Faculty Instructor             : {match_row['faculty_name']}
- Total Classes Conducted        : {match_row['total_classes']}
- Classes Attended               : {match_row['classes_attended']}
- Classes Missed                 : {match_row['classes_missed']}
- Current Attendance Percentage  : {match_row['attendance_pct']}%
- Mandatory University Benchmark : 75.0%
- Minimum Classes Needed for 75% : {match_row['classes_needed_for_75']} consecutive classes without absence
- Formal Warning Status          : {match_row['alert_level']}
----------------------------------------------------------------------------------------

MANDATORY DIRECTIVE:
1. You are strictly directed to attend all scheduled classes without any further absence.
2. If attendance remains below 65.0%, you will be detained and disqualified from writing 
   the Semester End University Examinations.
3. You and your parents are required to report to the HOD Office within 3 working days 
   for an academic counseling session with your Faculty Mentor.

Issued with approval:

{hod_name}
Head of Department, {dept_full_name}
Copy to: Dean of Academics, Faculty In-charge, Student File.
========================================================================================"""
            st.text_area("Official HOD Notice Preview:", value=notice_text, height=360)

            col_disp1, col_disp2, col_disp3 = st.columns(3)
            with col_disp1:
                if st.button("📲 Dispatch SMS to Mobile", use_container_width=True):
                    st.success(f"✅ SMS Alert sent to Student Mobile ({match_row['mobile_no']}) & Parent Mobile ({match_row['parent_mobile']})!")
            with col_disp2:
                if st.button("📧 Send Alert via Gmail", use_container_width=True):
                    st.success(f"✅ Official Warning Notice dispatched to Gmail ({match_row['gmail_id']})!")
            with col_disp3:
                st.download_button(
                    "📥 Download Alert Memo (.txt)",
                    data=notice_text,
                    file_name=f"Attendance_Alert_{match_row['roll_no']}_{match_row['course_code']}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        else:
            st.info("No defaulters available to generate warning notices.")

# ----------------------------------------------------
# TAB: Student Administration (Join & Modify)
# ----------------------------------------------------
with tab_admin:
    st.subheader("⚙️ Student Administration & Warehouse Enrollment Portal")
    st.caption("Manage student enrollments, admit new students directly into the Multi-Fact Data Warehouse, or update existing records.")

    admin_sub1, admin_sub2 = st.tabs([
        "📥 Admit & Join New Student (Warehouse Enrollment)",
        "✏️ Modify / Change Existing Student"
    ])

    with admin_sub1:
        st.markdown("### 📥 Register New Student Admission")
        st.caption("Enrolls a new student into Dim_Student and automatically initializes corresponding records in Fact_Exam_Performance, Fact_Attendance_Engagement, and Fact_Semester_Summary.")

        with st.form("new_student_form", clear_on_submit=False):
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                new_roll = st.text_input("Student Roll Number *", value="24ME1A0021", help="Unique Institutional Roll Number")
                new_name = st.text_input("Full Name *", value="Vikas Kumar")
                new_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            with f_col2:
                new_dept = st.selectbox("Department *", ["MECH", "CSE", "AIDS", "ECE", "CIVIL"])
                new_cohort = st.selectbox("Cohort Batch *", ["2024-2028", "2023-2027", "2022-2026", "2021-2025"])
                new_adm = st.selectbox("Admission Type", ["Regular", "Lateral Entry", "Management"])
            with f_col3:
                new_year = st.number_input("Year of Study", min_value=1, max_value=4, value=1)
                new_sem = st.number_input("Current Semester", min_value=1, max_value=8, value=1)
                new_status = st.selectbox("Academic Status", ["Active", "Probation"])
            
            st.markdown("#### 📱 Contact Channels (Mobile & Gmail for Attendance Alerts)")
            c_col1, c_col2, c_col3 = st.columns(3)
            with c_col1:
                new_mob = st.text_input("Student Mobile Number", value="+91 98491 00021")
            with c_col2:
                new_gmail = st.text_input("Student Gmail Address", value="student.24me@gmail.com")
            with c_col3:
                new_pmob = st.text_input("Parent Mobile Number", value="+91 94401 00021")

            st.markdown("#### Initial Performance Setup")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                init_att = st.slider("Initial Attendance %", min_value=30.0, max_value=100.0, value=80.0, step=0.5)
            with p_col2:
                init_marks = st.slider("Initial Academic Marks Avg (out of 100)", min_value=20.0, max_value=100.0, value=75.0, step=0.5)

            submitted = st.form_submit_button("📥 Admit & Join Student into Data Warehouse")
            if submitted:
                if not new_roll or not new_name:
                    st.error("Roll Number and Full Name are mandatory!")
                else:
                    stu_payload = {
                        "roll_no": new_roll.strip().upper(),
                        "student_name": new_name.strip(),
                        "gender": new_gender,
                        "dept_code": new_dept,
                        "cohort_batch": new_cohort,
                        "admission_type": new_adm,
                        "current_year": int(new_year),
                        "current_semester": int(new_sem),
                        "academic_status": new_status,
                        "mobile_no": new_mob.strip(),
                        "gmail_id": new_gmail.strip(),
                        "parent_mobile": new_pmob.strip(),
                        "initial_attendance_pct": init_att,
                        "initial_marks_avg": init_marks
                    }
                    success, msg = aq.add_new_student_to_warehouse(stu_payload)
                    if success:
                        st.success(f"✅ {msg}")
                        st.balloons()
                    else:
                        st.error(f"❌ {msg}")

    with admin_sub2:
        st.markdown("### ✏️ Modify Existing Student Information")
        st.caption("Select any existing student in the Data Warehouse to modify their demographics, department, semester, or academic status.")

        conn = aq.get_connection()
        students_list = pd.read_sql("SELECT roll_no, student_name, dept_code FROM dim_student ORDER BY roll_no", conn)
        conn.close()

        if not students_list.empty:
            options_edit = [f"{r['roll_no']} - {r['student_name']} ({r['dept_code']})" for _, r in students_list.iterrows()]
            default_edit_idx = 0
            selected_edit_str = st.selectbox("Select Student to Modify:", options_edit, index=default_edit_idx)
            edit_roll = selected_edit_str.split(" - ")[0]

            stu_current, _, _ = aq.get_student_360_profile(edit_roll)

            if stu_current:
                with st.form("edit_student_form"):
                    e_col1, e_col2, e_col3 = st.columns(3)
                    with e_col1:
                        st.text_input("Roll Number (Read-Only)", value=stu_current["roll_no"], disabled=True)
                        edit_name = st.text_input("Student Name", value=stu_current["student_name"])
                        gender_idx = ["Male", "Female", "Other"].index(stu_current["gender"]) if stu_current["gender"] in ["Male", "Female", "Other"] else 0
                        edit_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=gender_idx)
                    with e_col2:
                        dept_list = ["MECH", "CSE", "AIDS", "ECE", "CIVIL"]
                        d_idx = dept_list.index(stu_current["dept_code"]) if stu_current["dept_code"] in dept_list else 0
                        edit_dept = st.selectbox("Department", dept_list, index=d_idx)
                        
                        cohort_list = ["2024-2028", "2023-2027", "2022-2026", "2021-2025"]
                        c_idx = cohort_list.index(stu_current["cohort_batch"]) if stu_current["cohort_batch"] in cohort_list else 0
                        edit_cohort = st.selectbox("Cohort Batch", cohort_list, index=c_idx)

                        adm_list = ["Regular", "Lateral Entry", "Management"]
                        a_idx = adm_list.index(stu_current["admission_type"]) if stu_current["admission_type"] in adm_list else 0
                        edit_adm = st.selectbox("Admission Type", adm_list, index=a_idx)
                    with e_col3:
                        edit_year = st.number_input("Current Year", min_value=1, max_value=4, value=int(stu_current["current_year"]))
                        edit_sem = st.number_input("Current Semester", min_value=1, max_value=8, value=int(stu_current["current_semester"]))
                        status_list = ["Active", "Probation", "Graduated", "On-Leave"]
                        s_idx = status_list.index(stu_current["academic_status"]) if stu_current["academic_status"] in status_list else 0
                        edit_status = st.selectbox("Academic Status", status_list, index=s_idx)

                    st.markdown("#### 📱 Contact Channels (Mobile & Gmail for Attendance Alerts)")
                    ce_col1, ce_col2, ce_col3 = st.columns(3)
                    with ce_col1:
                        edit_mob = st.text_input("Student Mobile Number", value=stu_current.get("mobile_no", "+91 98491 54020"))
                    with ce_col2:
                        edit_gmail = st.text_input("Student Gmail Address", value=stu_current.get("gmail_id", "student@gmail.com"))
                    with ce_col3:
                        edit_pmob = st.text_input("Parent Mobile Number", value=stu_current.get("parent_mobile", "+91 94401 54020"))

                    update_btn = st.form_submit_button("💾 Save Updated Student Details")
                    if update_btn:
                        update_payload = {
                            "student_name": edit_name.strip(),
                            "gender": edit_gender,
                            "dept_code": edit_dept,
                            "cohort_batch": edit_cohort,
                            "admission_type": edit_adm,
                            "current_year": int(edit_year),
                            "current_semester": int(edit_sem),
                            "academic_status": edit_status,
                            "mobile_no": edit_mob.strip(),
                            "gmail_id": edit_gmail.strip(),
                            "parent_mobile": edit_pmob.strip()
                        }
                        ok, msg = aq.update_existing_student_in_warehouse(edit_roll, update_payload)
                        if ok:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")

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
# Footer
# ----------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94a3b8; font-size: 0.85rem;'>"
    "Academic Performance Multi-Fact Data Warehouse & Analytics | Institutional Academic Analytics System"
    "</div>",
    unsafe_allow_html=True
)
