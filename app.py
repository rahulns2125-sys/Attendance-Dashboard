from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime, timedelta
from functools import wraps
import random
import json

app = Flask(__name__)
app.secret_key = "attendx_mca3_secret_2026"

# ─── Users (Admin + Faculty) ──────────────────────────────────────────────────
USERS = {
    "admin":   {"password": "admin123",   "role": "Admin",   "name": "Mr. Rahul N"},
    "faculty": {"password": "faculty123", "role": "Faculty", "name": "Prof. Javed Pasha"},
    "hod":     {"password": "hod123",     "role": "HOD",     "name": "Prof. Dinesh"},
}

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ─── Simulated Database ───────────────────────────────────────────────────────

STUDENTS = [
    {"id": "MCA001", "name": "Aarav Sharma",    "branch": "MCA", "semester": 3},
    {"id": "MCA002", "name": "Priya Mehta",     "branch": "MCA", "semester": 3},
    {"id": "MCA003", "name": "Rohan Verma",     "branch": "MCA", "semester": 3},
    {"id": "MCA004", "name": "Sneha Pillai",    "branch": "MCA", "semester": 3},
    {"id": "MCA005", "name": "Karan Singh",     "branch": "MCA", "semester": 3},
    {"id": "MCA006", "name": "Divya Nair",      "branch": "MCA", "semester": 3},
    {"id": "MCA007", "name": "Arjun Patel",     "branch": "MCA", "semester": 3},
    {"id": "MCA008", "name": "Nisha Reddy",     "branch": "MCA", "semester": 3},
    {"id": "MCA009", "name": "Vikram Das",      "branch": "MCA", "semester": 3},
    {"id": "MCA010", "name": "Pooja Joshi",     "branch": "MCA", "semester": 3},
]

SUBJECTS = [
    {"code": "MCA301", "name": "Advanced Algorithms",      "credits": 4},
    {"code": "MCA302", "name": "Database Management",      "credits": 4},
    {"code": "MCA303", "name": "Web Technologies",         "credits": 3},
    {"code": "MCA304", "name": "Machine Learning",         "credits": 4},
    {"code": "MCA305", "name": "Cloud Computing",          "credits": 3},
    {"code": "MCA306", "name": "Software Engineering",     "credits": 3},
]

def generate_attendance():
    """Generate realistic attendance data for the last 90 days."""
    attendance = {}
    base_date = datetime.now() - timedelta(days=90)

    for student in STUDENTS:
        sid = student["id"]
        attendance[sid] = {}
        for subject in SUBJECTS:
            scode = subject["code"]
            # Each student has a base attendance % tendency
            base_pct = random.uniform(0.55, 0.98)
            records = []
            for day in range(90):
                date = base_date + timedelta(days=day)
                if date.weekday() < 5:  # Mon–Fri
                    present = random.random() < base_pct
                    records.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "present": present
                    })
            attendance[sid][scode] = records
    return attendance

ATTENDANCE_DATA = generate_attendance()


# ─── Helper Functions ─────────────────────────────────────────────────────────

def calc_percentage(records):
    if not records:
        return 0
    total = len(records)
    present = sum(1 for r in records if r["present"])
    return round((present / total) * 100, 1)

def get_student_stats(student_id):
    stats = []
    for subject in SUBJECTS:
        scode = subject["code"]
        records = ATTENDANCE_DATA.get(student_id, {}).get(scode, [])
        pct = calc_percentage(records)
        stats.append({
            "subject_code": scode,
            "subject_name": subject["name"],
            "credits": subject["credits"],
            "total_classes": len(records),
            "attended": sum(1 for r in records if r["present"]),
            "percentage": pct,
            "status": "Safe" if pct >= 75 else ("Warning" if pct >= 60 else "Critical")
        })
    return stats

def get_monthly_trend(student_id, subject_code):
    records = ATTENDANCE_DATA.get(student_id, {}).get(subject_code, [])
    monthly = {}
    for r in records:
        month = r["date"][:7]
        if month not in monthly:
            monthly[month] = {"total": 0, "present": 0}
        monthly[month]["total"] += 1
        if r["present"]:
            monthly[month]["present"] += 1
    result = []
    for month in sorted(monthly.keys()):
        d = monthly[month]
        pct = round((d["present"] / d["total"]) * 100, 1) if d["total"] else 0
        result.append({"month": month, "percentage": pct, "total": d["total"], "present": d["present"]})
    return result


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = USERS.get(username)
        if user and user["password"] == password:
            session["user"] = {"username": username, "role": user["role"], "name": user["name"]}
            return redirect(url_for("index"))
        error = "Invalid username or password. Please try again."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("index.html", user=session["user"])

@app.route("/api/session_user")
@login_required
def api_session_user():
    return jsonify(session["user"])

@app.route("/api/overview")
@login_required
def api_overview():
    """Dashboard overview stats."""
    total_students = len(STUDENTS)
    all_percentages = []
    critical_count = 0
    warning_count = 0
    safe_count = 0

    for student in STUDENTS:
        for subject in SUBJECTS:
            records = ATTENDANCE_DATA[student["id"]][subject["code"]]
            pct = calc_percentage(records)
            all_percentages.append(pct)
            if pct < 60:
                critical_count += 1
            elif pct < 75:
                warning_count += 1
            else:
                safe_count += 1

    avg_attendance = round(sum(all_percentages) / len(all_percentages), 1)

    # Subject-wise averages
    subject_avgs = []
    for subject in SUBJECTS:
        pcts = []
        for student in STUDENTS:
            records = ATTENDANCE_DATA[student["id"]][subject["code"]]
            pcts.append(calc_percentage(records))
        subject_avgs.append({
            "code": subject["code"],
            "name": subject["name"],
            "average": round(sum(pcts) / len(pcts), 1)
        })

    # Daily trend (last 30 days)
    daily_trend = []
    for day in range(29, -1, -1):
        date = (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d")
        day_records = []
        for student in STUDENTS:
            for subject in SUBJECTS:
                for r in ATTENDANCE_DATA[student["id"]][subject["code"]]:
                    if r["date"] == date:
                        day_records.append(r["present"])
        if day_records:
            pct = round(sum(day_records) / len(day_records) * 100, 1)
            daily_trend.append({"date": date, "percentage": pct})

    return jsonify({
        "total_students": total_students,
        "total_subjects": len(SUBJECTS),
        "avg_attendance": avg_attendance,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "safe_count": safe_count,
        "subject_averages": subject_avgs,
        "daily_trend": daily_trend
    })

@app.route("/api/students")
@login_required
def api_students():
    result = []
    for student in STUDENTS:
        stats = get_student_stats(student["id"])
        avg = round(sum(s["percentage"] for s in stats) / len(stats), 1)
        result.append({
            "id": student["id"],
            "name": student["name"],
            "semester": student["semester"],
            "avg_attendance": avg,
            "overall_status": "Safe" if avg >= 75 else ("Warning" if avg >= 60 else "Critical"),
            "subjects": stats
        })
    return jsonify(result)

@app.route("/api/student/<student_id>")
@login_required
def api_student_detail(student_id):
    student = next((s for s in STUDENTS if s["id"] == student_id), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    stats = get_student_stats(student_id)
    trend = get_monthly_trend(student_id, SUBJECTS[0]["code"])
    return jsonify({
        "student": student,
        "subject_stats": stats,
        "monthly_trend": trend
    })

@app.route("/api/subject/<subject_code>")
@login_required
def api_subject_detail(subject_code):
    subject = next((s for s in SUBJECTS if s["code"] == subject_code), None)
    if not subject:
        return jsonify({"error": "Subject not found"}), 404
    student_stats = []
    for student in STUDENTS:
        records = ATTENDANCE_DATA[student["id"]][subject_code]
        pct = calc_percentage(records)
        student_stats.append({
            "id": student["id"],
            "name": student["name"],
            "attended": sum(1 for r in records if r["present"]),
            "total": len(records),
            "percentage": pct,
            "status": "Safe" if pct >= 75 else ("Warning" if pct >= 60 else "Critical")
        })
    return jsonify({
        "subject": subject,
        "student_stats": sorted(student_stats, key=lambda x: x["percentage"], reverse=True)
    })

@app.route("/api/students_list")
@login_required
def api_students_list():
    return jsonify([{"id": s["id"], "name": s["name"]} for s in STUDENTS])

@app.route("/api/subjects_list")
@login_required
def api_subjects_list():
    return jsonify(SUBJECTS)

@app.route("/api/get_session_attendance")
@login_required
def api_get_session_attendance():
    subject_code = request.args.get("subject")
    date = request.args.get("date")
    if not subject_code or not date:
        return jsonify({"error": "Missing params"}), 400
    result = {}
    for student in STUDENTS:
        sid = student["id"]
        records = ATTENDANCE_DATA.get(sid, {}).get(subject_code, [])
        existing = next((r for r in records if r["date"] == date), None)
        result[sid] = existing["present"] if existing is not None else None
    return jsonify({"date": date, "subject": subject_code, "attendance": result})

@app.route("/api/record_attendance", methods=["POST"])
@login_required
def record_attendance():
    data = request.json
    subject_code = data.get("subject")
    date = data.get("date")
    records_in = data.get("records", {})
    if not subject_code or not date or not records_in:
        return jsonify({"error": "Missing data"}), 400
    subject = next((s for s in SUBJECTS if s["code"] == subject_code), None)
    if not subject:
        return jsonify({"error": "Invalid subject"}), 400
    updated = 0
    added = 0
    for student in STUDENTS:
        sid = student["id"]
        if sid not in records_in:
            continue
        present = bool(records_in[sid])
        existing_list = ATTENDANCE_DATA.setdefault(sid, {}).setdefault(subject_code, [])
        existing = next((r for r in existing_list if r["date"] == date), None)
        if existing:
            existing["present"] = present
            updated += 1
        else:
            existing_list.append({"date": date, "present": present})
            added += 1
    subj_name = subject["name"]
    return jsonify({"success": True, "message": f"Attendance saved for {subj_name} on {date}.", "updated": updated, "added": added})

if __name__ == "__main__":
    import webbrowser, threading
    print("\n" + "="*55)
    print("  📊 Digital Attendance Analytics Dashboard")
    print("  🎓 MCA 3rd Semester Project")
    print("  🌐 Opening in your browser...")
    print("="*55 + "\n")
    threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=False)
