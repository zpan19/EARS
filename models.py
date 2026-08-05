from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    applications = db.relationship(
        "Application",
        backref="applicant",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User {self.email}>"


class JobPosting(db.Model):
    __tablename__ = "job_postings"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Open")
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    applications = db.relationship(
        "Application",
        backref="job",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<JobPosting {self.title}>"


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    cover_letter = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.String(30),
        nullable=False,
        default="Submitted",
    )
    submitted_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    applicant_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("job_postings.id"),
        nullable=False,
    )

    __table_args__ = (
        db.UniqueConstraint(
            "applicant_id",
            "job_id",
            name="unique_applicant_job_application",
        ),
    )

    def __repr__(self):
        return f"<Application {self.id}>"


class ReviewerAssignment(db.Model):
    __tablename__ = "reviewer_assignments"

    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id"),
        nullable=False,
    )

    reviewer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Assigned",
    )

    assigned_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    application = db.relationship(
        "Application",
        backref=db.backref(
            "reviewer_assignments",
            lazy=True,
            cascade="all, delete-orphan",
        ),
    )

    reviewer = db.relationship(
        "User",
        foreign_keys=[reviewer_id],
        backref=db.backref(
            "assigned_reviews",
            lazy=True,
        ),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "application_id",
            "reviewer_id",
            name="unique_application_reviewer",
        ),
    )

    def __repr__(self):
        return f"<ReviewerAssignment {self.id}>"


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)

    assignment_id = db.Column(
        db.Integer,
        db.ForeignKey("reviewer_assignments.id"),
        unique=True,
        nullable=False,
    )

    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, nullable=False)
    recommendation = db.Column(db.String(30), nullable=False)

    submitted_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    assignment = db.relationship(
        "ReviewerAssignment",
        backref=db.backref(
            "review",
            uselist=False,
            cascade="all, delete-orphan",
        ),
    )

    def __repr__(self):
        return f"<Review {self.id}>"