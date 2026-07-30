from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    session,
)

from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ears.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "ears-development-secret-key"

db.init_app(app)


@app.route("/")
def home():
    return redirect(url_for("login"))


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

        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if user is None or not check_password_hash(
            user.password_hash,
            password,
        ):
            flash("Invalid email or password.")
            return render_template("login.html")

        session["user_id"] = user.id
        session["user_name"] = user.name
        session["role"] = user.role

        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        user_name=session["user_name"],
        role=session["role"],
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)