
import sqlite3
import os

# Database file location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "attendance.db")


# Connect to database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Create database tables
def init_db():

    conn = get_db_connection()

    # Students table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Attendance table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            attendance_date DATE NOT NULL,
            status TEXT NOT NULL
                CHECK(status IN ('Present', 'Absent')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(student_id, attendance_date),

            FOREIGN KEY(student_id)
            REFERENCES students(student_id)
            ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

    print("Database initialized successfully!")
