from flask import current_app as app
from .models import db, Admin, Company, Student, Placement_Drive, Application, Resume, Placement
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def seed_data():
    db.create_all()

    if Admin.query.first():
        print("Database already seeded. Skipping.")
        return

    print("Seeding database...")

    # ────────────────────── ADMIN ──────────────────────
    admin = Admin(
        username="admin",
        email="admin@placement.com",
        password=generate_password_hash("admin123"),
        is_active=True
    )
    db.session.add(admin)

    # ────────────────────── COMPANIES ──────────────────────
    companies_data = [
        ("Google",       "hr@google.com",       "+1456987321",   "https://google.com"),
        ("Meta",         "hr@meta.com",          "+917894561230", "https://meta.com"),
        ("Amazon",       "hr@amazon.com",        "+14151234003",  "https://amazon.com"),
        ("Apple",        "hr@apple.com",         "+14151237004",  "https://apple.com"),
        ("Netflix",      "hr@netflix.com",       "+14151238005",  "https://netflix.com"),
        ("Infosys",      "hr@infosys.com",       "+917001234001", "https://infosys.com"),
        ("Anime Mentor", "hr@animementor.com",   "+918617521478", "https://animementor.com"),
    ]

    companies = []
    for name, email, phone, website in companies_data:
        c = Company(
            company_name=name,
            email=email,
            password=generate_password_hash("company123"),
            hr_contact=phone,
            website=website,
            approval_status="Approved",
            is_active=True
        )
        db.session.add(c)
        companies.append(c)

    db.session.flush()

    #pending Company
    pending_companies_data = [
        ("TCS",          "hr@tcs.com",           "+917001234002", "https://tcs.com"),
        ("Wipro",        "hr@wipro.com",         "+917001234003", "https://wipro.com"),
        ("SKG",          "hr@skg.com",           "+918617854715", "https://skg.com"),
        ("Razorpay",     "hr@razorpay.com",      "+918001234004", "https://razorpay.com"),
        ("Zerodha",      "hr@zerodha.com",       "+918001234005", "https://zerodha.com"),
    ]

    pcompanies = []
    for name, email, phone, website in pending_companies_data:
        p = Company(
            company_name=name,
            email=email,
            password=generate_password_hash("company123"),
            hr_contact=phone,
            website=website,
            approval_status="Pending",
            is_active=True
        )
        db.session.add(p)
        companies.append(p)

    db.session.flush()

    # ────────────────────── STUDENTS ──────────────────────
    students_data = [
        ("Ram Sharma",   "ram@student.com",    "9876543210", "Computer Science",       "ABC College",    8.5, 2025),
        ("Anikit Verma", "anikit@student.com", "9876543211", "Information Technology", "XYZ Institute",  7.8, 2025),
        ("Ayan Khan",    "ayan@student.com",   "9876543212", "Electronics",            "PQR University", 9.1, 2025),
        ("Parth Patel",  "parth@student.com",  "9876543213", "Computer Science",       "ABC College",    8.0, 2026),
        ("Rakesh Singh", "rakesh@student.com", "9876543214", "Mechanical",             "LMN College",    6.9, 2025),
        ("Arpan Das",    "arpan@student.com",  "9876543215", "Computer Science",       "XYZ Institute",  8.8, 2026),
        ("Santu Mondal", "santu@student.com",  "9876543216", "Data Science",           "ABC College",    9.3, 2025),
    ]

    students = []
    for name, email, phone, branch, institute, cgpa, grad_year in students_data:
        s = Student(
            full_name=name,
            email=email,
            password=generate_password_hash("student123"),
            phone=phone,
            branch=branch,
            institute=institute,
            cgpa=cgpa,
            grad_year=grad_year,
            is_active=True
        )
        db.session.add(s)
        students.append(s)

    db.session.flush()

    # ────────────────────── PLACEMENT DRIVES ──────────────────────
    drives_data = [
        (companies[0],  "Full Stack Developer", "3+ years React, Node.js experience", "CGPA 7.5+, CS/IT branch",        "Bangalore"),
        (companies[1],  "ML Engineer",          "Deep learning, PyTorch, TensorFlow", "CGPA 8.0+, any branch",          "Hyderabad"),
        (companies[2],  "Backend Developer",    "Java, Spring Boot, AWS",             "CGPA 7.0+, CS/IT branch",        "Pune"),
        (companies[3],  "iOS Developer",        "Swift, Xcode, UIKit",                "CGPA 7.5+, CS branch",           "Bangalore"),
        (companies[4],  "Video Editor",         "Premiere Pro, After Effects",        "Any branch, portfolio required", "Remote"),
        (companies[5],  "Software Engineer",    "Java, Python, problem solving",      "CGPA 6.5+, any branch",          "Chennai"),
        (companies[6],  "System Analyst",       "SQL, business analysis",             "CGPA 7.0+, any branch",          "Mumbai"),
        (companies[7],  "DevOps Engineer",      "Docker, Kubernetes, CI/CD",          "CGPA 7.0+, CS/IT branch",        "Pune"),
        (companies[8],  "Backend Engineer",     "Node.js, PostgreSQL, Redis",         "CGPA 7.5+, CS branch",           "Bangalore"),
        (companies[9],  "Data Analyst",         "Python, SQL, Excel, Tableau",        "CGPA 7.0+, any branch",          "Bangalore"),
        (companies[10], "Content Writer",       "Strong English, SEO knowledge",      "Any branch",                     "Remote"),
        (companies[11], "Anime Script Writer",  "Storytelling, Japanese culture",     "Any branch, passion for anime",  "Remote"),
    ]

    drives = []
    for company, title, desc, eligibility, location in drives_data:
        d = Placement_Drive(
            company_id=company.company_id,
            job_title=title,
            job_description=desc,
            eligibility=eligibility,
            location=location,
            deadline=datetime.utcnow() + timedelta(days=30),
            status="Pending"
        )
        db.session.add(d)
        drives.append(d)

    db.session.flush()

    # ────────────────────── RESUMES ──────────────────────
    for student in students:
        r = Resume(
            student_id=student.student_id,
            file_path=f"resumes/{student.full_name.replace(' ', '_').lower()}_resume.pdf"
        )
        db.session.add(r)

    db.session.flush()

    # ────────────────────── APPLICATIONS ──────────────────────
    applications_data = [
        (students[0], drives[0],  "Applied"),
        (students[0], drives[5],  "Shortlisted"),
        (students[1], drives[1],  "Applied"),
        (students[1], drives[6],  "Rejected"),
        (students[2], drives[1],  "Selected"),
        (students[2], drives[9],  "Applied"),
        (students[3], drives[0],  "Applied"),
        (students[3], drives[2],  "Shortlisted"),
        (students[4], drives[5],  "Applied"),
        (students[4], drives[10], "Applied"),
        (students[5], drives[7],  "Selected"),
        (students[5], drives[3],  "Applied"),
        (students[6], drives[1],  "Shortlisted"),
        (students[6], drives[9],  "Applied"),
    ]

    for student, drive, status in applications_data:
        resume = Resume.query.filter_by(student_id=student.student_id).first()
        a = Application(
            student_id=student.student_id,
            drive_id=drive.drive_id,
            resume_id=resume.id,
            status=status
        )
        db.session.add(a)

    db.session.flush()                                        # flush before querying Selected

    # ────────────────────── PLACEMENTS ──────────────────────
    selected_apps = Application.query.filter_by(status="Selected").all()

    for selected in selected_apps:                            # renamed 'app' to 'selected' to avoid clash with Flask app
        drive = Placement_Drive.query.get(selected.drive_id)
        p = Placement(
            student_id=selected.student_id,
            drive_id=selected.drive_id,
            company_id=drive.company_id,
            application_id=selected.application_id,
            package=12.5
        )
        db.session.add(p)                                     # inside the loop now

    db.session.commit()
    print("Database seeded successfully!")