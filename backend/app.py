# =========================================================
# SIMPLE WORKING BACKEND (NO CLEANING, CLEANED EXCEL ONLY)
# Save as: app.py
# Keep cleaned_data.xlsx in same folder
# =========================================================

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# =========================================================
# LOAD CLEANED DATA ONLY
# =========================================================
df = pd.read_excel(r"C:\Users\dell\Documents\my_tools\my_docs\student\cleaned_data.xlsx",engine='openpyxl')


# =========================================================
# FILTER FUNCTION
# =========================================================
def apply_filters(data):
    filtered = data.copy()

    facility = request.args.get("facility")
    gender = request.args.get("gender")
    academic_year = request.args.get("academic_year")
    hostel = request.args.get("hostel")

    if facility:
        filtered = filtered[filtered["facility_rated"] == facility]

    if gender:
        filtered = filtered[filtered["gender"] == gender]

    if academic_year:
        filtered = filtered[filtered["academic_year"] == academic_year]

    if hostel:
        filtered = filtered[filtered["hostel_resident"] == hostel]

    return filtered


# =========================================================
# FILTER OPTIONS
# =========================================================
@app.route("/filters", methods=["GET"])
def get_filters():
    return jsonify({
        "facilities": sorted(df["facility_rated"].dropna().unique().tolist()),
        "genders": sorted(df["gender"].dropna().unique().tolist()),
        "years": sorted(df["academic_year"].dropna().unique().tolist()),
        "hostel": sorted(df["hostel_resident"].dropna().unique().tolist())
    })


# =========================================================
# FULL DATA
# =========================================================
@app.route("/data", methods=["GET"])
def get_data():
    filtered = apply_filters(df)
    return jsonify(filtered.fillna("").to_dict(orient="records"))


# =========================================================
# KPI
# =========================================================
@app.route("/kpi", methods=["GET"])
def get_kpi():
    filtered = apply_filters(df)

    return jsonify({
        "total_students": int(filtered["student_id"].nunique()),
        "avg_satisfaction": round(filtered["satisfaction_score"].mean(), 2),
        "avg_attendance": round(filtered["attendance_percentage"].mean(), 2),
        "avg_study_hours": round(filtered["study_hours_per_week"].mean(), 2)
    })


# =========================================================
# YEARLY SATISFACTION
# =========================================================
@app.route("/yearly_satisfaction", methods=["GET"])
@app.route("/filter", methods=["GET"])   # old frontend compatibility
def yearly_satisfaction():
    filtered = apply_filters(df)

    yearly = filtered.groupby("academic_year")["satisfaction_score"].mean()
    yearly = yearly.reindex(["1st", "2nd", "3rd", "4th"])

    return jsonify({
        "labels": yearly.index.tolist(),
        "values": [
            round(v, 2) if pd.notna(v) else None
            for v in yearly.values
        ]
    })


# =========================================================
# GENDER SATISFACTION
# =========================================================
@app.route("/gender_satisfaction", methods=["GET"])
def gender_satisfaction():
    filtered = apply_filters(df)

    gender_avg = filtered.groupby("gender")["satisfaction_score"].mean()

    return jsonify({
        "labels": gender_avg.index.tolist(),
        "values": [round(v, 2) for v in gender_avg.values]
    })


# =========================================================
# FACILITY SATISFACTION
# =========================================================
@app.route("/facility_satisfaction", methods=["GET"])
def facility_satisfaction():
    filtered = apply_filters(df)

    facility_avg = filtered.groupby("facility_rated")["satisfaction_score"].mean().sort_values()

    return jsonify({
        "labels": facility_avg.index.tolist(),
        "values": [round(v, 2) for v in facility_avg.values]
    })


# =========================================================
# PLACEMENT DISTRIBUTION
# =========================================================
@app.route("/placement_distribution", methods=["GET"])
def placement_distribution():
    filtered = apply_filters(df)

    counts = filtered["placement_confidence"].value_counts().sort_index()

    return jsonify({
        "labels": counts.index.tolist(),
        "values": counts.values.tolist()
    })


# =========================================================
# HOSTEL DISTRIBUTION
# =========================================================
@app.route("/hostel_distribution", methods=["GET"])
def hostel_distribution():
    filtered = apply_filters(df)

    counts = filtered["hostel_resident"].value_counts()

    return jsonify({
        "labels": counts.index.tolist(),
        "values": counts.values.tolist()
    })


# =========================================================
# MAJOR SATISFACTION
# =========================================================
@app.route("/major_satisfaction", methods=["GET"])
def major_satisfaction():
    filtered = apply_filters(df)

    major_avg = filtered.groupby("major")["satisfaction_score"].mean().sort_values()

    return jsonify({
        "labels": major_avg.index.tolist(),
        "values": [round(v, 2) for v in major_avg.values]
    })


# =========================================================
# FACILITY DISTRIBUTION
# =========================================================
@app.route("/facility_distribution", methods=["GET"])
def facility_distribution():
    filtered = apply_filters(df)

    counts = filtered["facility_rated"].value_counts()

    return jsonify({
        "labels": counts.index.tolist(),
        "values": counts.values.tolist()
    })


# =========================================================
# CORRELATION HEATMAP
# =========================================================
@app.route("/correlation_heatmap", methods=["GET"])
def correlation_heatmap():
    filtered = apply_filters(df)

    cols = [
        "satisfaction_score",
        "attendance_percentage",
        "study_hours_per_week",
        "faculty_rating",
        "placement_confidence"
    ]

    corr = filtered[cols].corr().round(2)

    return jsonify({
        "labels": corr.columns.tolist(),
        "matrix": corr.values.tolist()
    })


# =========================================================
# RUN SERVER
# =========================================================
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)