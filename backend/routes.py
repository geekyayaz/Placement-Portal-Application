from flask import render_template, request, redirect
from werkzeug.security import check_password_hash
from backend.models import *
from app import app
from flask_login import login_user, login_required, current_user, logout_user


@app.route('/')
def home():
    return render_template("home.html")

# Login
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

#Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

#Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")


#student_dashboard
@app.route("/dashboard/student",  methods=['GET','POST'])
@login_required
def student_dashboard():
    if isinstance(current_user,Student):
        return f"Welcome to Student Dashboard {current_user.full_name}"
    else:
        return "You are not Authorized"

# Company Dashboard
@app.route("/dashboard/company")
@login_required
def company_dashboard():
    if isinstance(current_user,Company):
        return f"Welcome to Company Dashboard {current_user.company_name}"
    else:
        return "You are not Authorized"

#Admin Dashboard
@app.route("/dashboard/admin", methods=['GET','POST'])
@login_required
def admin_dashboard():
     if isinstance(current_user,Admin):
        company=Company.query.filter_by(approval_status="Approved").all()
        students=db.session.query(Student).all()
        pending_companies = Company.query.filter_by(approval_status="Pending").all()
        drives=Placement_Drive.query.filter_by(is_active=True).all()
        comple_drive=Placement_Drive.query.filter_by(is_active=False).all()
        application=db.session.query(Application).all()
        rejected_companies = Company.query.filter_by(approval_status="Rejected").all()
        return render_template("/admin/admin_dashboard.html/",company=company, student=students, pending_companies=pending_companies, drives=drives, application=application, rejected_companies=rejected_companies, comple_drive=comple_drive)
     else:
        return "You are not Authorized"

# Admin Dashboard- Edit
@app.route("/admin/company/edit/<int:company_id>", methods=["GET", "POST"])
@login_required
def edit_company(company_id):
    if isinstance(current_user, Admin):
        company = Company.query.get_or_404(company_id)

        if request.method == "GET":
            return render_template("admin/edit_company.html", company=company)

        if request.method == "POST":
            company.company_name  = request.form.get("company_name")
            company.email         = request.form.get("email")
            company.password         = request.form.get("password")
            company.hr_contact    = request.form.get("hr_contact")
            company.website       = request.form.get("website")
            company.approval_status = request.form.get("approval_status")

            db.session.commit()
            return redirect("/dashboard/admin")
    else:
        return "You are not Authorized", 403

@app.route("/admin/student/edit/<int:student_id>", methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    if isinstance(current_user, Admin):
        student = Student.query.get_or_404(student_id)

        if request.method == "GET":
            return render_template("admin/edit_student.html", student=student)

        if request.method == "POST":
            student.full_name  = request.form.get("full_name")
            student.email      = request.form.get("email")
            student.phone      = request.form.get("phone")
            student.branch     = request.form.get("branch")
            student.institute  = request.form.get("institute")
            student.cgpa       = request.form.get("cgpa")
            student.grad_year  = request.form.get("grad_year")

            db.session.commit()
            return redirect("/dashboard/admin")
    else:
        return "You are not Authorized", 403


# Admin Dashboard- Delete
@app.route("/admin/company/delete/<int:company_id>")
@login_required
def delete_company(company_id):
    if isinstance(current_user, Admin):
        company = Company.query.get_or_404(company_id)

        drives = Placement_Drive.query.filter_by(company_id=company_id).all()
        for drive in drives:
            Placement.query.filter_by(drive_id=drive.drive_id).delete()
            Application.query.filter_by(drive_id=drive.drive_id).delete()

        Placement_Drive.query.filter_by(company_id=company_id).delete()
        Placement.query.filter_by(company_id=company_id).delete()

        db.session.delete(company)
        db.session.commit()
        return redirect("/dashboard/admin")
    return "Not Authorized", 403

@app.route("/admin/student/delete/<int:student_id>")
@login_required
def delete_student(student_id):
    if isinstance(current_user, Admin):
        student = Student.query.get_or_404(student_id)

        Application.query.filter_by(student_id=student_id).delete()
        Resume.query.filter_by(student_id=student_id).delete()

        db.session.delete(student)
        db.session.commit()
        return redirect("/dashboard/admin")
    return "Not Authorized", 403

# Admin Dashboard- Approve/Reject
@app.route("/admin/company/blacklist/<int:company_id>")
@login_required
def blacklist_company(company_id):
    if isinstance(current_user, Admin):
        company = Company.query.get_or_404(company_id)
        company.is_active = False
        db.session.commit()
        return redirect("/dashboard/admin")
    return "Not Authorized", 403


@app.route("/admin/company/approve/<int:company_id>")
@login_required
def approve_company(company_id):
    if isinstance(current_user, Admin):
        company = Company.query.get_or_404(company_id)
        company.approval_status = "Approved"
        db.session.commit()
        return redirect("/dashboard/admin")
    return "Not Authorized", 403
@app.route("/admin/company/reject/<int:company_id>")
@login_required
def reject_company(company_id):
    if isinstance(current_user, Admin):
        company = Company.query.get_or_404(company_id)
        company.approval_status = "Rejected"
        db.session.commit()
        return redirect("/dashboard/admin")
    return "Not Authorized", 403

## Admin Dashboard- Search
@app.route("/admin/search")
@login_required
def admin_search():
    if isinstance(current_user, Admin):
        q           = request.args.get("q", "").strip()
        search_type = request.args.get("type", "all")

        company  = []
        student  = []

        if search_type in ("all", "company"):
            company = Company.query.filter(
                Company.company_name.ilike(f"%{q}%")
            ).all()

        if search_type in ("all", "student"):
            student = Student.query.filter(
                (Student.full_name.ilike(f"%{q}%")) |
                (Student.phone.ilike(f"%{q}%"))     |
                (Student.email.ilike(f"%{q}%"))
            ).all()

        pending_companies = Company.query.filter_by(approval_status="Pending").all()
        drives            = Placement_Drive.query.filter_by(status="Approved").all()
        application       = Application.query.all()

        return render_template("admin/admin_dashboard.html",
                               company=company,
                               student=student,
                               drives=drives,
                               application=application,
                               pending_companies=pending_companies,
                               search_query=q,
                               search_type=search_type)
    return "Not Authorized", 403

# Admin Dashboard- Drive
@app.route("/dashboard/drive/<int:drive_id>")
@login_required
def drive_details(drive_id):
     if isinstance(current_user, (Admin, Student, Company)):
        drive = Placement_Drive.query.get(drive_id)
        return render_template("drives_details.html",drive=drive)
     else:
        return "You are not Authorized"

@app.route("/admin/drive/approve/<int:drive_id>")
@login_required
def approve_drive(drive_id):
    if isinstance(current_user,Admin):
        drive=Placement_Drive.query.get(drive_id)
        drive.status= "Approved"
        db.session.commit()
    return redirect("/dashboard/admin")

@app.route("/admin/drive/reject/<int:drive_id>")
@login_required
def reject_drive(drive_id):
        if isinstance(current_user,Admin):
            drive=Placement_Drive.query.get(drive_id)
            drive.status= "Reject"
            db.session.commit()
        return redirect("/dashboard/admin")

@app.route("/admin/drive/complete/<int:drive_id>")
@login_required
def end_drive(drive_id):
        if isinstance(current_user,Admin):
            drive=Placement_Drive.query.get(drive_id)
            drive.is_active= False
            db.session.commit()
        return redirect("/dashboard/admin")

@app.route("/dashboard/application/<int:application_id>")
@login_required
def application_details(application_id):
    if isinstance(current_user, (Admin, Student, Company)):
        application=Application.query.get(application_id)
        return render_template("student_application.html", application=application)
    else:
        return "You are not Authorized"

@app.route("/dashboard/company/<int:company_id>")
@login_required
def company_details(company_id):
    if isinstance(current_user,(Admin,Company,Student)):
        company=db.session.get(Company,company_id)
        return render_template("view_company.html", company=company)
    else:
        return "Not Authorized"