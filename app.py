from flask import Flask
from backend.models import db
from flask_login import LoginManager


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.sqlite"
    app.config["SECRET_KEY"] = "mysecretkey"

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        from backend.models import Admin, Student, Company

        if "-" not in user_id:
            return None

        role, id = user_id.split("-")
        id = int(id)

        if role == "admin":
            return Admin.query.get(id)
        elif role == "student":
            return Student.query.filter_by(student_id=id).first()
        elif role == "company":
            return Company.query.filter_by(company_id=id).first()

        return None

    app.app_context().push()
    return app


app = create_app()

from backend.create_initialdata import *
from backend.routes import *

seed_data()

if __name__ == "__main__":
    app.run(debug=True)