from flask import Flask
from backend.models import db
def create_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.sqlite"
    db.init_app(app)
    app.app_context().push()
    return app

app=create_app()
from backend.create_initialdata import *
from backend.routes import *
seed_data()
if __name__=="__main__":
    app.run(debug=True)
