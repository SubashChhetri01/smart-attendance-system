from flask import Flask, jsonify, request, send_from_directory
from database import get_db_connection, init_db
from datetime import date, datetime
import sqlite3

app = Flask(__name__)

# Initialize database
init_db()


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/health")
def health():
    return jsonify({"status": "OK"})


# =================================
# STUDENT MANAGEMENT
# =================================

# Get all students
@app.route("/students", methods=["GET"])
def get_students():

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# Register a student
@app.route("/students", methods=["POST"])
def add_student():

    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    student_id = data.get("student_id")
    name = data.get("name")
    email = data.get("email")

    if not student_id or not name or not email:
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db_connection()

    try:
        conn.execute(
            """INSERT INTO students (student_id, name, email)
               VALUES (?, ?, ?)""",
            (student_id.strip(), name.strip(), email.strip())
        )

        conn.commit()

        return jsonify({
            "message": "Student registered successfully!"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student ID or email already exists"
        }), 400

    finally:
        conn.close()


# =================================
# ATTENDANCE MANAGEMENT
# =================================

# Get attendance records
@app.route("/attendance", methods=["GET"])
def get_attendance():

    attendance_date = request.args.get(
        "date", date.today().isoformat()
    )

    conn = get_db_connection()

    records = conn.execute("""
        SELECT
            attendance.id,
            attendance.student_id,
            students.name,
            attendance.attendance_date,
            attendance.status
        FROM attendance
        JOIN students
            ON attendance.student_id = students.student_id
        WHERE attendance.attendance_date = ?
        ORDER BY students.name
    """, (attendance_date,)).fetchall()

    conn.close()

    return jsonify([dict(record) for record in records])


# Mark attendance
@app.route("/attendance", methods=["POST"])
def mark_attendance():

    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    student_id = data.get("student_id")
    status = data.get("status")
    attendance_date = data.get(
        "attendance_date", date.today().isoformat()
    )

    if not student_id or not status:
        return jsonify({
            "error": "Student ID and status are required"
        }), 400

    if status not in ["Present", "Absent"]:
        return jsonify({
            "error": "Status must be Present or Absent"
        }), 400

    try:
        datetime.strptime(attendance_date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return jsonify({
            "error": "Date must use YYYY-MM-DD format"
        }), 400

    conn = get_db_connection()

    try:
        conn.execute("""
            INSERT INTO attendance
                (student_id, attendance_date, status)
            VALUES (?, ?, ?)

            ON CONFLICT(student_id, attendance_date)
            DO UPDATE SET status = excluded.status
        """, (student_id, attendance_date, status))

        conn.commit()

        return jsonify({
            "message": "Attendance marked successfully!",
            "student_id": student_id,
            "date": attendance_date,
            "status": status
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student not found. Register the student first."
        }), 400

    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)