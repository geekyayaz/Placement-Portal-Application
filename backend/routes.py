from flask import render_template, request, redirect
from werkzeug.security import check_password_hash
from backend.models import *
from app import app
from flask_login import login_user, login_required, current_user, logout_user


@app.route('/')
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        femail = request.form.get("email")
        fpwd = request.form.get("password")

        admin_obj   = Admin.query.filter_by(email=femail).first()
        student_obj = Student.query.filter_by(email=femail).first()
        company_obj = Company.query.filter_by(email=femail).first()

        if admin_obj and check_password_hash(admin_obj.password, fpwd):
            login_user(admin_obj)
            return redirect("/dashboard/admin")

        elif student_obj and check_password_hash(student_obj.password, fpwd):
            login_user(student_obj)
            return redirect("/dashboard/student")

        elif company_obj and check_password_hash(company_obj.password, fpwd):
            if company_obj.approval_status != "Approved": 
                return render_template("login.html", error="Your account is pending admin approval.")
            login_user(company_obj)
            return redirect("/dashboard/company")

        else:
            return render_template("login.html", error="Invalid email or password")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route("/dashboard/student")
@login_required
def student_dashboard():
    if isinstance(current_user,Student):
        return f"Welcome to Student Dashboard {current_user.full_name}"
    else:
        return "You are not Authorized"


@app.route("/dashboard/company")
@login_required
def company_dashboard():
    if isinstance(current_user,Company):
        return f"Welcome to Company Dashboard {current_user.company_name}"
    else:
        return "You are not Authorized"


@app.route("/dashboard/admin")
@login_required
def admin_dashboard():
     if isinstance(current_user,Admin):
        return f"Welcome to Admin Dashboard {current_user.username}"
     else:
        return "You are not Authorized"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")