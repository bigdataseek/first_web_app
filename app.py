from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)


# 데이터베이스 연결 설정
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY", "12345"
)  # 환경변수가 없다면 12345로 설정

db = SQLAlchemy(app)


import time


# def wait_for_db(host, port, user, password, db, retries=5, delay=5):
#     for i in range(retries):
#         try:
#             conn = pymysql.connect(
#                 host=host, port=port, user=user, password=password, db=db
#             )
#             conn.close()
#             print("Database is ready!")
#             return
#         except pymysql.MySQLError as e:
#             print(f"Database connection failed (Attempt {i + 1}/{retries}): {e}")
#             time.sleep(delay)
#     raise Exception("Database connection failed after retries")


def init_db():
    db.create_all()


# User 모델 정의
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


# 데이터베이스에서 사용자 조회
def get_user(username):
    return User.query.filter_by(username=username).first()


# 데이터베이스에 사용자 추가
def add_user(username, password):
    try:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False


@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("main"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("모든 필드를 입력해주세요.", "danger")
            return redirect(url_for("register"))

        if add_user(username, password):
            flash("회원가입이 완료되었습니다. \n로그인해주세요.", "success")
            return redirect(url_for("login"))
        else:
            flash("이미 존재하는 아이디입니다.", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user(username)
        if user and user.password == password:
            session["username"] = username
            flash("로그인에 성공했습니다!", "success")
            return redirect(url_for("main"))
        else:
            flash("아이디 또는 비밀번호가 잘못되었습니다.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/main")
def main():
    if "username" not in session:
        flash("로그인이 필요합니다.", "warning")
        return redirect(url_for("login"))
    return render_template("main.html", username=session["username"])


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("로그아웃 되었습니다.", "info")
    return redirect(url_for("login"))


if not is_docker:
    if __name__ == "__main__":
        # init_db()  # 애플리케이션 시작 시 데이터베이스 초기화
        print("개발버전으로 실행됨")
        app.run(debug=True, port=8000)
else:
    with app.app_context():
        print("app_context is called")
        init_db()
