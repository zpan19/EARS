# EARS - Employment Application Review System

EARS is a web-based Employment Application Review System developed using **Flask**, **SQLite**, and **Bootstrap**.
A role-based recruitment management system developed as a Software Engineering course project at Algoma University.

## Features

- User Registration & Login
- Role-based Access Control
- Job Management
- Job Application
- Reviewer Assignment
- Review Submission
- Administrator Dashboard
- SQLite Database

## Technologies

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Bootstrap 5

## Installation

```bash
pip install -r requirements.txt
python app.py
```

Open:

```
http://127.0.0.1:5000
```

## Demo Accounts

| Role          | Email                | Password      |
| ------------- | -------------------- | ------------- |
| Administrator | admin@ears.com       | Admin123!     |
| Chairperson   | chairperson@ears.com | Chair123!     |
| Reviewer      | reviewer1@ears.com   | Review123!    |
| Reviewer      | reviewer2@ears.com   | Review123!    |
| Applicant     | alice@applicant.com  | Applicant123! |
| Applicant     | daniel@applicant.com | Applicant123! |
| Applicant     | sophia@applicant.com | Applicant123! |

> These accounts are provided for demonstration purposes only.

## Database

- User
- JobPosting
- Application
- ReviewerAssignment
- Review

## Workflow

Applicant → Submit Application

↓

Chairperson → Assign Reviewer

↓

Reviewer → Submit Review

↓

Chairperson → Review Summary → Update Status
