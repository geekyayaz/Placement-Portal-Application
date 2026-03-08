from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class Admin(db.Model, UserMixin):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def get_id(self):
        return f"admin-{self.id}"

    def __repr__(self):
        return f"<Admin {self.username}>"


class Company(db.Model, UserMixin):
    __tablename__ = "company"

    company_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    hr_contact = db.Column(db.String(15), nullable=False)
    website = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), default="Pending")
    is_active = db.Column(db.Boolean, default=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    drives = db.relationship('Placement_Drive', backref='company', lazy=True)
    placements = db.relationship('Placement', backref='company', lazy=True,
                                 foreign_keys='Placement.company_id')

    def get_id(self):
        return f"company-{self.company_id}"

    def __repr__(self):
        return f"<Company {self.company_name}>"


class Student(db.Model, UserMixin):
    __tablename__ = "student"

    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    institute = db.Column(db.String(150))
    cgpa = db.Column(db.Float)
    grad_year = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='student', lazy=True)
    resume = db.relationship('Resume', backref='student', uselist=False)
    placements = db.relationship('Placement', backref='student', lazy=True,
                                 foreign_keys='Placement.student_id')

    def get_id(self):
        return f"student-{self.student_id}"

    def __repr__(self):
        return f"<Student {self.full_name}>"


class Resume(db.Model):
    __tablename__ = "resume"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'),
                           nullable=False, unique=True)
    file_path = db.Column(db.String(300), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)       # ✅ no brackets

    def __repr__(self):
        return f"<Resume student_id={self.student_id}>"


class Placement_Drive(db.Model):
    __tablename__ = "drive"

    drive_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'),
                           nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text)
    eligibility = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    applications = db.relationship('Application', backref='drive', lazy=True)

    def __repr__(self):
        return f"<Drive {self.job_title}>"


class Application(db.Model):
    __tablename__ = "application"

    application_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'),
                           nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.drive_id'),
                         nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'),
                          nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Applied")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,  
                           onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),
    )
    resume = db.relationship('Resume', backref='resume', lazy=True)

    def __repr__(self):
        return f"<Application student={self.student_id} drive={self.drive_id}>"


class Placement(db.Model):
    __tablename__ = "placement"

    placement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.drive_id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('application.application_id'),
                               nullable=False)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)         # ✅ no brackets
    package = db.Column(db.Float)

    def __repr__(self):
        return f"<Placement student={self.student_id} company={self.company_id}>"