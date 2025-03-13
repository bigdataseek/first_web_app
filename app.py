from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
import os
from sqlalchemy.exc import IntegrityError


# .env 파일 로드
load_dotenv()

database_url = os.getenv("DATABASE_URI")


# Flask 애플리케이션 생성
app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"  # 임의의 긴 문자열로 설정

# 데이터베이스 설정
app.config["SQLALCHEMY_DATABASE_URI"] = database_url


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# 모델 정의
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Post {self.title}>"


# 라우트 정의
@app.route("/")
def home():
    posts = Post.query.all()
    return render_template("home.html", posts=posts)


@app.route("/user/<username>")
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("profile.html", user=user)


@app.route("/post/new", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]

        # 사용자 이름과 이메일로 사용자 검색
        user = User.query.filter_by(username=username, email=email).first()

        if not user:
            # 사용자가 존재하지 않으면 생성
            try:
                user = User(username=username, email=email)
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("이미 존재하는 이메일입니다.", "error")  # 플래시 메시지 설정
                return redirect(url_for("new_post"))  # 다시 글 작성 페이지로 리다이렉트

        post = Post(
            title=request.form["title"], content=request.form["content"], author=user
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("create_post.html")


# 애플리케이션 실행을 위한 코드
if __name__ == "__main__":  # 개발 버전
    with app.app_context():
        db.create_all()  # 데이터베이스 테이블 생성
    app.run(debug=True, port=8000)
else:  # 배포 버전(gunicorn 실행시 __name__은 app이다. 도커 실행시입니다.)
    # with app.app_context():
    #     db.create_all()  # 데이터베이스 테이블 생성
    pass
