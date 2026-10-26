# 📊 AttendX — Digital Attendance Analytics Dashboard
### MCA 3rd Semester Project | Python + Flask + Chart.js

---

## 🚀 How to Run in VS Code

### Step 1 — Open the folder
```
File → Open Folder → select `attendance_dashboard`
```

### Step 2 — Open Terminal
```
View → Terminal   (or press  Ctrl + `)
```

### Step 3 — Install Flask (only once)
```bash
pip install flask
```

### Step 4 — Run the app
```bash
python app.py
```

### Step 5 — Open in Browser
```
http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
attendance_dashboard/
│
├── app.py               ← Flask backend (API + routes)
├── requirements.txt     ← Dependencies
├── README.md            ← This file
│
└── templates/
    └── index.html       ← Frontend dashboard (HTML + CSS + JS)
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 Dashboard | KPI cards, 30-day trend line, donut chart, bar chart |
| 🎓 Students | Card-based student grid with attendance % |
| 📚 Subjects | Per-subject student attendance table |
| 🔔 Alerts | Auto-detects students below 75% threshold |
| ✅ Mark Attendance | Form to record new attendance sessions |
| 📄 Reports | Ranked leaderboard of student attendance |

---

## 🛠 Technology Stack

- **Backend** — Python 3, Flask
- **Frontend** — HTML5, CSS3, Vanilla JS
- **Charts** — Chart.js 4.4
- **Fonts** — Google Fonts (Syne + DM Sans)
- **Data** — Simulated (10 students × 6 subjects × 90 days)

---

## 📌 Key Concepts Demonstrated

1. **REST API design** with Flask routes
2. **Data simulation** mimicking real attendance records
3. **Analytics computation** (averages, trends, alerts)
4. **Interactive dashboards** with dynamic chart rendering
5. **Responsive UI** with modern CSS design patterns

---

*Built for MCA 3rd Semester — Digital Attendance Analytics Dashboard*
