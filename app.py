import re

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from models import Application, JobPosting, User, db


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ears.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "ears-development-secret-key"

db.init_app(app)


def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."

    if not re.search(r"\d", password):
        return "Password must contain at least one number."

    if not re.search(r"[!@#$%^&*]", password):
        return "Password must contain at least one special character."

    return None


def login_required():
    return "user_id" in session


def has_role(required_role):
    return login_required() and session.get("role") == required_role


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

        # Administrator cannot be selected from the public registration page.
        allowed_roles = {"Applicant", "Reviewer", "Chairperson"}

        if role not in allowed_roles:
            flash("Please select a valid role.")
            return render_template("register.html")

        password_error = validate_password(password)

        if password_error:
            flash(password_error)
            return render_template("register.html")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.")
            return render_template("register.html")

        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
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
    if not login_required():
        flash("Please log in first.")
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        user_name=session["user_name"],
        role=session["role"],
    )


# ---------------------------------------------------------
# Applicant routes
# ---------------------------------------------------------

@app.route("/jobs")
def jobs():
    if not has_role("Applicant"):
        flash("Applicant access is required.")
        return redirect(url_for("dashboard"))

    open_jobs = (
        JobPosting.query.filter_by(status="Open")
        .order_by(JobPosting.created_at.desc())
        .all()
    )

    return render_template("jobs.html", jobs=open_jobs)


@app.route("/apply/<int:job_id>", methods=["GET", "POST"])
def apply(job_id):
    if not has_role("Applicant"):
        flash("Applicant access is required.")
        return redirect(url_for("dashboard"))

    job = JobPosting.query.get_or_404(job_id)

    if job.status != "Open":
        flash("This job posting is no longer open.")
        return redirect(url_for("jobs"))

    existing_application = Application.query.filter_by(
        applicant_id=session["user_id"],
        job_id=job.id,
    ).first()

    if existing_application:
        flash("You have already applied for this job.")
        return redirect(url_for("applications"))

    if request.method == "POST":
        cover_letter = request.form.get("cover_letter", "").strip()

        if not cover_letter:
            flash("Cover letter is required.")
            return render_template("apply.html", job=job)

        application = Application(
            cover_letter=cover_letter,
            status="Submitted",
            applicant_id=session["user_id"],
            job_id=job.id,
        )

        db.session.add(application)
        db.session.commit()

        flash("Application submitted successfully.")
        return redirect(url_for("applications"))

    return render_template("apply.html", job=job)


@app.route("/applications")
def applications():
    if not has_role("Applicant"):
        flash("Applicant access is required.")
        return redirect(url_for("dashboard"))

    applicant_applications = (
        Application.query.filter_by(
            applicant_id=session["user_id"]
        )
        .order_by(Application.submitted_at.desc())
        .all()
    )

    return render_template(
        "applications.html",
        applications=applicant_applications,
    )


# ---------------------------------------------------------
# Chairperson routes
# ---------------------------------------------------------

@app.route("/manage-jobs", methods=["GET", "POST"])
def manage_jobs():
    if not has_role("Chairperson"):
        flash("Chairperson access is required.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if not title or not description:
            flash("Job title and description are required.")
            return redirect(url_for("manage_jobs"))

        job = JobPosting(
            title=title,
            description=description,
            status="Open",
        )

        db.session.add(job)
        db.session.commit()

        flash("Job posting created successfully.")
        return redirect(url_for("manage_jobs"))

    all_jobs = JobPosting.query.order_by(
        JobPosting.created_at.desc()
    ).all()

    return render_template(
        "manage_jobs.html",
        jobs=all_jobs,
    )


@app.route("/jobs/<int:job_id>/toggle", methods=["POST"])
def toggle_job_status(job_id):
    if not has_role("Chairperson"):
        flash("Chairperson access is required.")
        return redirect(url_for("dashboard"))

    job = JobPosting.query.get_or_404(job_id)

    job.status = "Closed" if job.status == "Open" else "Open"

    db.session.commit()

    flash("Job status updated.")
    return redirect(url_for("manage_jobs"))


# ---------------------------------------------------------
# Administrator routes
# ---------------------------------------------------------

@app.route("/admin")
def admin_overview():
    if not has_role("Administrator"):
        flash("Administrator access is required.")
        return redirect(url_for("dashboard"))

    statistics = {
        "total_users": User.query.count(),
        "applicants": User.query.filter_by(role="Applicant").count(),
        "reviewers": User.query.filter_by(role="Reviewer").count(),
        "chairpersons": User.query.filter_by(role="Chairperson").count(),
        "jobs": JobPosting.query.count(),
        "open_jobs": JobPosting.query.filter_by(status="Open").count(),
        "applications": Application.query.count(),
    }

    recent_users = (
        User.query.order_by(User.id.desc())
        .limit(5)
        .all()
    )

    recent_applications = (
        Application.query.order_by(
            Application.submitted_at.desc()
        )
        .limit(5)
        .all()
    )

    return render_template(
        "admin_overview.html",
        statistics=statistics,
        recent_users=recent_users,
        recent_applications=recent_applications,
    )


@app.route("/admin/applicant-view")
def admin_applicant_view():
    if not has_role("Administrator"):
        flash("Administrator access is required.")
        return redirect(url_for("dashboard"))

    applicants = (
        User.query.filter_by(role="Applicant")
        .order_by(User.name.asc())
        .all()
    )

    open_jobs = (
        JobPosting.query.filter_by(status="Open")
        .order_by(JobPosting.created_at.desc())
        .all()
    )

    all_applications = (
        Application.query.order_by(
            Application.submitted_at.desc()
        )
        .all()
    )

    return render_template(
        "admin_applicant_view.html",
        applicants=applicants,
        jobs=open_jobs,
        applications=all_applications,
    )


@app.route("/admin/reviewer-view")
def admin_reviewer_view():
    if not has_role("Administrator"):
        flash("Administrator access is required.")
        return redirect(url_for("dashboard"))

    reviewers = (
        User.query.filter_by(role="Reviewer")
        .order_by(User.name.asc())
        .all()
    )

    all_applications = (
        Application.query.order_by(
            Application.submitted_at.desc()
        )
        .all()
    )

    return render_template(
        "admin_reviewer_view.html",
        reviewers=reviewers,
        applications=all_applications,
    )


@app.route("/admin/chairperson-view")
def admin_chairperson_view():
    if not has_role("Administrator"):
        flash("Administrator access is required.")
        return redirect(url_for("dashboard"))

    chairpersons = (
        User.query.filter_by(role="Chairperson")
        .order_by(User.name.asc())
        .all()
    )

    all_jobs = (
        JobPosting.query.order_by(
            JobPosting.created_at.desc()
        )
        .all()
    )

    all_applications = (
        Application.query.order_by(
            Application.submitted_at.desc()
        )
        .all()
    )

    return render_template(
        "admin_chairperson_view.html",
        chairpersons=chairpersons,
        jobs=all_jobs,
        applications=all_applications,
    )


@app.route("/manage-users")
def manage_users():
    if not has_role("Administrator"):
        flash("Administrator access is required.")
        return redirect(url_for("dashboard"))

    users = User.query.order_by(User.id.asc()).all()

    return render_template(
        "manage_users.html",
        users=users,
        current_user_id=session["user_id"],
    )


@app.route("/users/<int:user_id>/update-role", methods=["POST"])
def update_user_role(user_id):
    if not has_role("Administrator"):
        flash("Administrator access is required.")
        return redirect(url_for("dashboard"))

    user = User.query.get_or_404(user_id)

    if user.id == session["user_id"]:
        flash("You cannot change your own administrator role.")
        return redirect(url_for("manage_users"))

    new_role = request.form.get("role", "")
    allowed_roles = {"Applicant", "Reviewer", "Chairperson"}

    if new_role not in allowed_roles:
        flash("Please select a valid role.")
        return redirect(url_for("manage_users"))

    user.role = new_role
    db.session.commit()

    flash(f"{user.name}'s role was updated successfully.")
    return redirect(url_for("manage_users"))


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    if not has_role("Administrator"):
        flash("Administrator access is required.")
        return redirect(url_for("dashboard"))

    if user_id == session["user_id"]:
        flash("You cannot delete your own administrator account.")
        return redirect(url_for("manage_users"))

    user = User.query.get_or_404(user_id)
    user_name = user.name

    db.session.delete(user)
    db.session.commit()

    flash(f"{user_name}'s account was deleted successfully.")
    return redirect(url_for("manage_users"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        admin_user = User.query.filter_by(
            email="admin@ears.com"
        ).first()

        if admin_user is None:
            admin_user = User(
                name="EARS Administrator",
                email="admin@ears.com",
                password_hash=generate_password_hash("Admin123!"),
                role="Administrator",
            )

            db.session.add(admin_user)
            db.session.commit()

            print("Default administrator account created.")

    app.run(debug=True)