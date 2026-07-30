from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
)

from werkzeug.security import generate_password_hash

from models import db, User


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ears.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "ears-development-secret-key"

db.init_app(app)


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "")

        if not name or not email or not password or not role:
            flash("All fields are required.")
            return render_template("register.html")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.")
            return render_template("register.html")

        password_hash = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)