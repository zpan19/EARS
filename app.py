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


def seed_demo_data():
    """Create realistic demonstration data without creating duplicates."""

    demo_users = [
        {
            "name": "EARS Administrator",
            "email": "admin@ears.com",
            "password": "Admin123!",
            "role": "Administrator",
        },
        {
            "name": "Dr. Emily Carter",
            "email": "chairperson@ears.com",
            "password": "Chair123!",
            "role": "Chairperson",
        },
        {
            "name": "Dr. Michael Chen",
            "email": "reviewer1@ears.com",
            "password": "Review123!",
            "role": "Reviewer",
        },
        {
            "name": "Prof. Sarah Wilson",
            "email": "reviewer2@ears.com",
            "password": "Review123!",
            "role": "Reviewer",
        },
        {
            "name": "Alice Johnson",
            "email": "alice@applicant.com",
            "password": "Applicant123!",
            "role": "Applicant",
        },
        {
            "name": "Daniel Brown",
            "email": "daniel@applicant.com",
            "password": "Applicant123!",
            "role": "Applicant",
        },
        {
            "name": "Sophia Lee",
            "email": "sophia@applicant.com",
            "password": "Applicant123!",
            "role": "Applicant",
        },
    ]

    for demo_user in demo_users:
        existing_user = User.query.filter_by(
            email=demo_user["email"]
        ).first()

        if existing_user is None:
            new_user = User(
                name=demo_user["name"],
                email=demo_user["email"],
                password_hash=generate_password_hash(
                    demo_user["password"]
                ),
                role=demo_user["role"],
            )

            db.session.add(new_user)

    db.session.commit()

    demo_jobs = [
        {
            "title": "Assistant Professor – Artificial Intelligence",
            "description": (
                "The School of Computer Science and Technology is seeking "
                "an Assistant Professor specializing in artificial "
                "intelligence, machine learning, and data science. "
                "Responsibilities include teaching, research, and student "
                "supervision."
            ),
            "status": "Open",
        },
        {
            "title": "Sessional Instructor – Software Engineering",
            "description": (
                "The successful applicant will teach undergraduate software "
                "engineering courses, including software design, testing, "
                "project management, and agile development."
            ),
            "status": "Open",
        },
        {
            "title": "Research Assistant – Data Analytics",
            "description": (
                "This position supports a research project involving data "
                "collection, Python programming, statistical analysis, and "
                "the preparation of research reports."
            ),
            "status": "Open",
        },
        {
            "title": "Teaching Assistant – Introduction to Programming",
            "description": (
                "The teaching assistant will support laboratory sessions, "
                "answer student questions, grade assignments, and assist "
                "with introductory Python programming activities."
            ),
            "status": "Closed",
        },
    ]

    for demo_job in demo_jobs:
        existing_job = JobPosting.query.filter_by(
            title=demo_job["title"]
        ).first()

        if existing_job is None:
            new_job = JobPosting(
                title=demo_job["title"],
                description=demo_job["description"],
                status=demo_job["status"],
            )

            db.session.add(new_job)

    db.session.commit()

    alice = User.query.filter_by(
        email="alice@applicant.com"
    ).first()

    daniel = User.query.filter_by(
        email="daniel@applicant.com"
    ).first()

    sophia = User.query.filter_by(
        email="sophia@applicant.com"
    ).first()

    ai_job = JobPosting.query.filter_by(
        title="Assistant Professor – Artificial Intelligence"
    ).first()

    software_job = JobPosting.query.filter_by(
        title="Sessional Instructor – Software Engineering"
    ).first()

    data_job = JobPosting.query.filter_by(
        title="Research Assistant – Data Analytics"
    ).first()

    demo_applications = [
        {
            "applicant": alice,
            "job": ai_job,
            "cover_letter": (
                "I am applying for the Assistant Professor position because "
                "my academic background and research interests focus on "
                "machine learning and responsible artificial intelligence."
            ),
            "status": "Under Review",
        },
        {
            "applicant": daniel,
            "job": software_job,
            "cover_letter": (
                "I have professional software development experience and "
                "strong knowledge of agile methods, testing, and software "
                "architecture."
            ),
            "status": "Submitted",
        },
        {
            "applicant": sophia,
            "job": data_job,
            "cover_letter": (
                "My experience with Python, statistics, and data visualization "
                "makes me a strong candidate for the research assistant role."
            ),
            "status": "Shortlisted",
        },
        {
            "applicant": alice,
            "job": data_job,
            "cover_letter": (
                "I would like to contribute my programming and analytical "
                "skills to the data analytics research project."
            ),
            "status": "Submitted",
        },
    ]

    for demo_application in demo_applications:
        if (
            demo_application["applicant"] is None
            or demo_application["job"] is None
        ):
            continue

        existing_application = Application.query.filter_by(
            applicant_id=demo_application["applicant"].id,
            job_id=demo_application["job"].id,
        ).first()

        if existing_application is None:
            new_application = Application(
                applicant_id=demo_application["applicant"].id,
                job_id=demo_application["job"].id,
                cover_letter=demo_application["cover_letter"],
                status=demo_application["status"],
            )

            db.session.add(new_application)

    db.session.commit()

    print("Demo users, jobs, and applications are ready.")



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
        seed_demo_data()

    app.run(debug=True)