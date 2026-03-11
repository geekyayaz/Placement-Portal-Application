from flask import render_template, request, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from backend.models import *
from app import app
from flask_login import login_user, login_required, current_user, logout_user
from datetime import datetime
import os


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
            if student_obj.is_active!=True:
                return render_template("login.html", error="Your account is backlisted by Admin. Contact admin@placement.com")
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



#Admin Dashboard
@app.route("/dashboard/admin", methods=['GET','POST'])
@login_required
def admin_dashboard():
     if isinstance(current_user,Admin):
        company=Company.query.filter_by(approval_status="Approved").all()
        students=Student.query.filter_by(is_active=True).all()
        pending_companies = Company.query.filter_by(approval_status="Pending").all()
        drives=Placement_Drive.query.filter_by(is_active=True, status="Approved").all()
        pending_drives=Placement_Drive.query.filter_by(is_active=True, status="Pending").all()
        comple_drive=Placement_Drive.query.filter_by(is_active=False).all()
        application=db.session.query(Application).all()
        rejected_companies = Company.query.filter_by(approval_status="Rejected").all()
        blacklist_student=Student.query.filter_by(is_active=False).all()
        return render_template("admin/admin_dashboard.html",company=company, pending_drives=pending_drives,student=students, pending_companies=pending_companies, drives=drives, application=application, rejected_companies=rejected_companies, comple_drive=comple_drive,blacklist_student=blacklist_student)
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
            new_pwd = request.form.get("password")
            if new_pwd:
                company.password = generate_password_hash(new_pwd)
            company.hr_contact    = request.form.get("hr_contact")
            company.website       = request.form.get("website")
            company.approval_status = request.form.get("approval_status")

            db.session.commit()
            return redirect("/dashboard/admin#company")
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
            return redirect("/dashboard/admin#student")
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
        return redirect("/dashboard/admin#company")
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
        return redirect("/dashboard/admin#student")
    return "Not Authorized", 403

# Admin Dashboard- Approve/Reject
@app.route("/admin/company/blacklist/<int:company_id>")
@login_required
def blacklist_company(company_id):
    if isinstance(current_user, Admin):
        company = Company.query.get_or_404(company_id)
        company.is_active = False
        db.session.commit()
        return redirect("/dashboard/admin#Rejected_Companies")
    return "Not Authorized", 403


@app.route("/admin/student/blacklist/<int:student_id>")
@login_required
def blacklist_student(student_id):
    if isinstance(current_user, Admin):
        student = Student.query.get_or_404(student_id)
        student.is_active = False
        db.session.commit()
        return redirect("/dashboard/admin#bstudent")
    return "Not Authorized", 403


@app.route("/admin/student/approve/<int:student_id>")
@login_required
def approve_student(student_id):
    if isinstance(current_user, Admin):
        student = Student.query.get_or_404(student_id)
        student.is_active = True
        db.session.commit()
        return redirect("/dashboard/admin#student")
    return "Not Authorized", 403


@app.route("/admin/company/approve/<int:company_id>")
@login_required
def approve_company(company_id):
    if isinstance(current_user, Admin):
        company = Company.query.get_or_404(company_id)
        company.approval_status = "Approved"
        db.session.commit()
        return redirect("/dashboard/admin#company")
    return "Not Authorized", 403

@app.route("/admin/company/reject/<int:company_id>")
@login_required
def reject_company(company_id):
    if isinstance(current_user, Admin):
        company = Company.query.get_or_404(company_id)
        company.approval_status = "Rejected"
        db.session.commit()
        return redirect("/dashboard/admin#Rejected_Companies")
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
        applications=Placement_Drive.query.get(drive_id)
        return render_template("drives_details.html",drive=drive, applications=applications)
     else:
        return "You are not Authorized"

@app.route("/admin/drive/approve/<int:drive_id>")
@login_required
def approve_drive(drive_id):
    if isinstance(current_user,Admin):
        drive=Placement_Drive.query.get(drive_id)
        drive.status= "Approved"
        db.session.commit()
    return redirect("/dashboard/admin#drives")

@app.route("/admin/drive/reject/<int:drive_id>")
@login_required
def reject_drive(drive_id):
    if isinstance(current_user, Admin):
        drive = Placement_Drive.query.get(drive_id)
        drive.status = "Rejected"
        db.session.commit()
        return redirect(f"/dashboard/admin#drives")
    return "Not Authorized", 403

@app.route("/drive/complete/<int:drive_id>")
@login_required
def end_drive(drive_id):

    if isinstance(current_user, (Admin, Company)):

        drive = Placement_Drive.query.get_or_404(drive_id)

        drive.is_active = False
        db.session.commit()

        if isinstance(current_user, Admin):
            return redirect("/dashboard/admin#cdrives")

        elif isinstance(current_user, Company):
            return redirect("/dashboard/company")

    return "You are not Authorized", 403



@app.route("/dashboard/company/<int:company_id>")
@login_required
def company_details(company_id):
    if isinstance(current_user,(Admin,Company)):
        company=db.session.get(Company,company_id)
        drives=Placement_Drive.query.filter_by(status="Approved", company_id=company.company_id).all()
        pending_drives=Placement_Drive.query.filter_by(status="Pending", is_active=True, company_id=company.company_id).all()
        old_drives=Placement_Drive.query.filter_by(company_id=company.company_id, is_active=False).all()
        r_drives=Placement_Drive.query.filter_by(company_id=company.company_id, status="Rejected" ).all()
        return render_template("view_company.html", company=company, drives=drives, r_drives=r_drives,pending_drives=pending_drives, old_drives=old_drives)
    else:
        return "Not Authorized"
    
@app.route("/dashboard/company")
@login_required
def company_dashboard():
    if isinstance(current_user, Company):
        on_drives = Placement_Drive.query.filter_by(
            status="Approved",
            is_active=True,
            company_id=current_user.company_id
        ).all()

        for d in on_drives:
            d.applicant_count = Application.query.filter_by(drive_id=d.drive_id).count()

        rejected_drives = Placement_Drive.query.filter_by(
            status="Rejected",
            company_id=current_user.company_id
        ).all()

        pending_drives = Placement_Drive.query.filter_by(
            status="Pending", is_active=True,
            company_id=current_user.company_id
        ).all()

        closed_drives = Placement_Drive.query.filter_by(
            is_active=False,
            company_id=current_user.company_id
        ).all()

        for d in closed_drives:
            d.applicant_count = Application.query.filter_by(drive_id=d.drive_id).count()

        return render_template("company/company_dashboard.html",
                               rejected_drives=rejected_drives,
                               on_drives=on_drives,
                               company=current_user,
                               pending_drives=pending_drives,
                               closed_drives=closed_drives)
    return "You are not Authorized", 403



@app.route("/dashboard/student/<int:student_id>")
@login_required
def student_page(student_id):
    if isinstance(current_user,Admin):
        student=Student.query.get(student_id)
        return render_template("admin/view_student.html", student=student)
    else:
        return "You are not authorized",403

@app.route("/company/new_drive", methods=["GET", "POST"])
@login_required
def new_drive():
    if isinstance(current_user, Company):

        if request.method == "POST":
            job_title       = request.form.get("job_title")
            job_description = request.form.get("job_description")
            eligibility     = request.form.get("eligibility")
            location        = request.form.get("location")
            salary_range    = request.form.get("salary_range")
            required_skills = request.form.get("required_skills")
            deadline        = datetime.strptime(request.form.get("deadline"), "%Y-%m-%d")

            drive = Placement_Drive(
                company_id=current_user.company_id,
                job_title=job_title,
                job_description=job_description,
                eligibility=eligibility,
                location=location, salary_range=salary_range, required_skills=required_skills,
                deadline=deadline)
            db.session.add(drive)
            db.session.commit()
            return redirect("/dashboard/company")

        return render_template("company/create_drive.html")

    return "You are not Authorized", 403

@app.route("/company/edit_drive/<int:drive_id>", methods=["GET", "POST"])
@login_required
def edit_drive(drive_id):
    if isinstance(current_user, Company):
        drive = Placement_Drive.query.get_or_404(drive_id)


        if drive.company_id != current_user.company_id:
            return "Not Authorized", 403

        if request.method == "GET":
            return render_template("company/edit_drive.html", drive=drive)

        if request.method == "POST":
            drive.job_title       = request.form.get("job_title")
            drive.job_description = request.form.get("job_description")
            drive.eligibility     = request.form.get("eligibility")
            drive.location        = request.form.get("location")
            drive.salary_range    = request.form.get("salary_range")
            drive.required_skills = request.form.get("required_skills")
            drive.deadline        = datetime.strptime(request.form.get("deadline"), "%Y-%m-%d")
            drive.status = "Pending"
            db.session.commit()
            flash("Drive updated! Awaiting admin re-approval.")
            return redirect("/dashboard/company")

    return "Not Authorized", 403

@app.route("/company/view_applicants/<int:drive_id>")
@login_required
def view_applications(drive_id):
    if isinstance(current_user, (Admin,Company)):
        applications = Application.query.filter_by(drive_id=drive_id).all()
        return render_template("company/view_applicants.html",
                               applications=applications)
    return "You are not Authorized", 403



#student_dashboard
@app.route("/dashboard/student",  methods=['GET','POST'])
@login_required
def student_dashboard():
    if isinstance(current_user,Student):
        companies=Company.query.filter_by(approval_status="Approved").all()
        for c in companies:
            c.active_drive_count = Placement_Drive.query.filter_by(
                company_id=c.company_id,
                is_active=True,
                status="Approved"
            ).count()
        applications = Application.query.filter_by(
            student_id=current_user.student_id
        ).all()
        drives = Placement_Drive.query.filter_by(
            status="Approved",
            is_active=True
        ).all()
        notifications = Application.query.filter(
            Application.student_id == current_user.student_id,
            Application.status != "Applied"
        ).all()
        return render_template("student/student_dashboard.html",
                               companies=companies,
                               applications=applications, drives=drives, notifications=notifications)
    return "You are not Authorized", 403




#Application
@app.route("/dashboard/application/<int:application_id>")
@login_required
def application_details(application_id):
    application = Application.query.get_or_404(application_id)

    if isinstance(current_user, Admin):
        pass
    elif isinstance(current_user, Company):
        drive = Placement_Drive.query.get(application.drive_id)
        if drive.company_id != current_user.company_id:
            return "You are not Authorized", 403
    elif isinstance(current_user, Student):
        if application.student_id != current_user.student_id:
            return "You are not Authorized", 403
    else:
        return "You are not Authorized", 403

    return render_template("student_application.html", application=application)


@app.route("/application/status/<int:application_id>/<status>")
@login_required                                                   
def update_application_status(application_id, status):
    if isinstance(current_user, (Admin, Company)):
        application = Application.query.get_or_404(application_id)
        application.status = status
        db.session.commit()
        return redirect(f"/dashboard/application/{application_id}")
    return "You are not Authorized", 403

@app.route("/dashboard/student/edit", methods=['POST','GET'])
@login_required
def edit_profile():
    if isinstance(current_user, Student):
        if request.method == "GET":
            return render_template("student/edit_profile.html", student=current_user)

        if request.method == "POST":
            current_user.full_name  = request.form.get("full_name")
            current_user.email      = request.form.get("email")
            current_user.phone      = request.form.get("phone")
            current_user.branch     = request.form.get("branch")
            current_user.institute  = request.form.get("institute")
            current_user.cgpa       = request.form.get("cgpa")
            current_user.grad_year  = request.form.get("grad_year")

            new_pwd = request.form.get("password")
            if new_pwd:
                current_user.password = generate_password_hash(new_pwd)

            # Resume upload
            file = request.files.get("resume")
            if file and file.filename.endswith(".pdf"):
                filename = secure_filename(f"student_{current_user.student_id}_resume.pdf")
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                file_path = f"/static/resumes/{filename}"
                if current_user.resume:
                    current_user.resume.file_path = file_path
                else:
                    db.session.add(Resume(student_id=current_user.student_id, file_path=file_path))

            db.session.commit()
            flash("Profile edited successfully!")
            return redirect("/dashboard/student")

    return "You are not Authorized", 403

@app.route('/register/student', methods=['POST', 'GET'])
def register_student():
    if request.method == "GET":
        return render_template("student/register.html")

    name      = request.form.get("full_name")
    email     = request.form.get("email")
    pwd       = request.form.get("password")
    confirm   = request.form.get("confirm_password")
    phone     = request.form.get("phone")
    branch    = request.form.get("branch")
    institute = request.form.get("institute")
    cgpa      = request.form.get("cgpa")
    grad_year = request.form.get("grad_year")

    # validation first
    if pwd != confirm:
        return render_template("student/register.html", error="Passwords do not match")
    if Student.query.filter_by(email=email).first():
        return render_template("student/register.html", error="Email already registered")
    if Student.query.filter_by(phone=phone).first():
        return render_template("student/register.html", error="Phone already registered")

    # create student
    s = Student(full_name=name, email=email,
                password=generate_password_hash(pwd),
                phone=phone, branch=branch,
                institute=institute, cgpa=cgpa, grad_year=grad_year)
    db.session.add(s)
    db.session.flush() 


    file = request.files.get("resume")
    if file and file.filename != "" and file.filename.endswith(".pdf"):
        filename = secure_filename(f"student_{s.student_id}_resume.pdf")
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        file_path = f"/static/resumes/{filename}"
        db.session.add(Resume(student_id=s.student_id, file_path=file_path))

    db.session.commit()
    flash("Registration successful! Please login.")
    return redirect("/login")


@app.route('/register/company', methods=['POST','GET'])
def register_company():
    if request.method=='GET':
        return render_template('company/register.html')
    name=request.form.get("company_name")
    email=request.form.get("email")
    pwd=request.form.get("password")
    confrim=request.form.get("confirm_password")
    hr_contact=request.form.get("hr_contact")
    website=request.form.get("website")

    if pwd!=confrim:
        return render_template("/company/register.html", error="Passwords do not match")
    if Company.query.filter_by(email=email).first():
        return render_template("/company/register.html", error="Email already registered")
    c= Company(company_name=name, email=email, password=generate_password_hash(pwd), hr_contact=hr_contact, website=website)
    db.session.add(c)
    db.session.commit()
    flash("Registration successful! Please login.")
    return redirect("/login")

@app.route("/student/search")
@login_required
def student_search():
    if isinstance(current_user, Student):
        q           = request.args.get("q", "").strip()
        search_type = request.args.get("type", "all")

        companies = []
        drives    = []

        if search_type in ("all", "company"):
            companies = Company.query.filter(
                Company.company_name.ilike(f"%{q}%"),
                Company.approval_status == "Approved"
            ).all()

        if search_type in ("all", "position", "skills"):
            drives = Placement_Drive.query.filter(
                (Placement_Drive.job_title.ilike(f"%{q}%"))       |
                (Placement_Drive.job_description.ilike(f"%{q}%")) |
                (Placement_Drive.eligibility.ilike(f"%{q}%"))     |
                (Placement_Drive.required_skills.ilike(f"%{q}%")),
                Placement_Drive.status == "Approved",
                Placement_Drive.is_active == True
            ).all()

        applications = Application.query.filter_by(
            student_id=current_user.student_id
        ).all()


        for c in companies:
            c.active_drive_count = Placement_Drive.query.filter_by(
                company_id=c.company_id,
                is_active=True,
                status="Approved"
            ).count()

        return render_template("student/student_dashboard.html",
                               companies=companies,
                               drives=drives,
                               applications=applications,
                               search_query=q,
                               search_type=search_type)
    return "Not Authorized", 403

@app.route("/dashboard/student/company/<int:company_id>")
@login_required
def company_info(company_id):
    if isinstance(current_user, Student):
        company = db.session.get(Company, company_id)

        applications = Application.query.filter(
            Application.student_id == current_user.student_id,
            Application.drive_id == Placement_Drive.drive_id,
            Placement_Drive.company_id == company_id
        ).all()
        drives=Placement_Drive.query.filter_by(status="Approved", company_id=company.company_id).all()

        return render_template("student/view_company.html",
                               company=company,
                               applications=applications, drives=drives)
    return "Not Authorized", 403
    
@app.route("/dashboard/student/history")
@login_required
def student_history():
    if isinstance(current_user, Student):
        applications = Application.query.filter_by(student_id=current_user.student_id).all()
        return render_template("student/history.html", applications=applications)
    return "Not Authorized", 403

@app.route("/student/apply/<int:drive_id>")
@login_required
def apply_drive(drive_id):
    if isinstance(current_user, Student):
        drive = Placement_Drive.query.get_or_404(drive_id)

        if drive.status != "Approved" or not drive.is_active:
            flash("This drive is not accepting applications.")
            return redirect(f"/dashboard/drive/{drive_id}")

        existing = Application.query.filter_by(
            student_id=current_user.student_id,
            drive_id=drive_id).first()
        if existing:
            flash("You have already applied for this drive.")
            return redirect(f"/dashboard/drive/{drive_id}")


        if not current_user.resume:
            flash("Please upload a resume before applying.")
            return redirect("/dashboard/student/edit")

        application = Application(
            student_id=current_user.student_id,
            drive_id=drive_id,
            resume_id=current_user.resume.id
        )
        db.session.add(application)
        db.session.commit()
        flash("Applied successfully!")
        return redirect(f"/dashboard/drive/{drive_id}")

    return "You are not Authorized", 403
