#Installation

```bash
pip install -r requirements.txt
python app.py
```

Open:

```
http://127.0.0.1:5000
```

Demo Accounts

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

Database

- User
- JobPosting
- Application
- ReviewerAssignment
- Review

Workflow

Applicant → Submit Application

↓

Chairperson → Assign Reviewer

↓

Reviewer → Submit Review

↓

Chairperson → Review Summary → Update Status
