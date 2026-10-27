"""
risk_model.py
-------------
Machine Learning Risk Detection Model for Student Academic Failure & Detention.
Trained on Multi-Fact warehouse features (Attendance, Internal Scores, Assignment Submissions).
"""

import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "warehouse", "academic_dw.db")

class StudentRiskDetector:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=6)
        self.feature_names = ["attendance_pct", "internal_marks", "assignment_score_pct", "is_condonation_risk"]
        self.is_trained = False
        self.accuracy = 0.0
        self.feature_importances = {}

    def fetch_training_data(self):
        """Extracts multi-fact joined records to train risk classifier."""
        conn = sqlite3.connect(self.db_path)
        query = """
        SELECT 
            fae.attendance_pct,
            fep.internal_marks,
            fae.assignment_score_pct,
            fae.is_condonation_risk,
            fep.is_backlog AS target_backlog
        FROM fact_exam_performance fep
        JOIN fact_attendance_engagement fae 
            ON fep.student_key = fae.student_key 
            AND fep.course_key = fae.course_key 
            AND fep.time_key = fae.time_key;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def train(self):
        """Trains the Random Forest Risk Classifier."""
        df = self.fetch_training_data()
        X = df[self.feature_names]
        y = df["target_backlog"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        self.accuracy = round(accuracy_score(y_test, y_pred) * 100.0, 2)
        self.is_trained = True

        importances = self.model.feature_importances_
        self.feature_importances = dict(zip(self.feature_names, [round(float(imp) * 100, 2) for imp in importances]))

        print(f"[OK] Student Risk Model trained successfully. Test Accuracy: {self.accuracy}%")
        print(f"     Feature Importances: {self.feature_importances}")
        return self.accuracy

    def predict_risk(self, attendance_pct: float, internal_marks: float, assignment_pct: float):
        """
        Evaluates risk for a given student course scenario.
        Returns risk probability, risk category, and action recommendation.
        """
        if not self.is_trained:
            self.train()

        condonation_flag = 1 if (65.0 <= attendance_pct < 75.0) else 0
        input_data = pd.DataFrame([{
            "attendance_pct": attendance_pct,
            "internal_marks": internal_marks,
            "assignment_score_pct": assignment_pct,
            "is_condonation_risk": condonation_flag
        }])

        prob_failure = float(self.model.predict_proba(input_data)[0][1])
        fail_prob_pct = round(prob_failure * 100.0, 1)

        if fail_prob_pct >= 60.0 or attendance_pct < 65.0:
            category = "Critical Risk"
            color = "#ef4444"
            recommendation = "Immediate Mentor Counseling + Compulsory Remedial Classes + Parent Notification"
        elif fail_prob_pct >= 30.0 or attendance_pct < 75.0:
            category = "Moderate Risk"
            color = "#f59e0b"
            recommendation = "Monitor Attendance Closely + Peer Tutoring on Weak Concepts + Assignment Resubmission"
        else:
            category = "Low / Safe"
            color = "#10b981"
            recommendation = "On Track. Encourage Advanced Electives and Industry Capstone Projects."

        return {
            "failure_probability_pct": fail_prob_pct,
            "risk_category": category,
            "color": color,
            "recommendation": recommendation
        }

# Global singleton instance
risk_detector = StudentRiskDetector()

if __name__ == "__main__":
    detector = StudentRiskDetector()
    detector.train()
    # Test sample scenario
    res = detector.predict_risk(attendance_pct=62.0, internal_marks=12.0, assignment_pct=50.0)
    print("Sample Risk Prediction (Detention/Fail Risk):", res)
    res_safe = detector.predict_risk(attendance_pct=92.0, internal_marks=28.0, assignment_pct=95.0)
    print("Sample Safe Prediction:", res_safe)
