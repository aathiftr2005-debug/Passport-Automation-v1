# VISTARA — Smart Passport Automation v1.0

A full-stack passport application processing system built with **Python Flask**, **SQLAlchemy ORM**, and **Supabase PostgreSQL**. Deployed on **Render**.

🔗 **Live Demo:** [passport-automation-v1.onrender.com](https://passport-automation-v1.onrender.com/)

---

## Features

- **Public submission form** — applicants fill in personal details and submit passport requests
- **Unique application ID** — auto-generated on submission for tracking
- **Admin dashboard** — view all applications, approve or reject with one click
- **Live status tracking** — applicants track status via Application ID or Aadhar number
- **Cloud database** — Supabase PostgreSQL with session pooling via SQLAlchemy
- **Auto-deploy** — hosted on Render with environment variable config

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.x, Flask, Flask-SQLAlchemy |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy |
| Frontend | HTML5, Tailwind CSS, JavaScript |
| Hosting | Render |
| DB Hosting | Supabase (AWS ap-south-1) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Browser                          │
│           (Applicant / Admin / Tracker)                 │
└────────────────────┬────────────────────────────────────┘
                     │  HTTP request
                     ▼
┌─────────────────────────────────────────────────────────┐
│               Flask App  (Render)                       │
│                                                         │
│   /          →  Landing page                            │
│   /apply     →  Form submit → create Application row    │
│   /success   →  Show application ID                     │
│   /admin     →  Dashboard — list + update status        │
│   /track     →  Lookup by ID or Aadhar                  │
│                                                         │
│              SQLAlchemy ORM                             │
└────────────────────┬────────────────────────────────────┘
                     │  PostgreSQL connection
                     │  (port 6543, session pooling)
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Supabase PostgreSQL  (ap-south-1)             │
│                                                         │
│   Table: applications                                   │
│   ├── id           INT  PK  auto-increment              │
│   ├── full_name    VARCHAR(255)                         │
│   ├── dob          DATE                                 │
│   ├── gender       VARCHAR(20)                          │
│   ├── aadhar_no    VARCHAR(12)  UNIQUE                  │
│   ├── address      TEXT                                 │
│   ├── status       VARCHAR(50)  default: 'Pending'      │
│   └── applied_at   TIMESTAMP    default: now()          │
└─────────────────────────────────────────────────────────┘
```

---

## Project structure

```
Passport-Automation-v1/
├── app.py              # Flask app, routes, SQLAlchemy model
├── database.sql        # SQL schema for manual setup if needed
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── templates/
    ├── index.html      # Landing + submission form
    ├── success.html    # Post-submit confirmation page
    └── admin.html      # Admin dashboard
```

---

## Local setup

### 1. Clone the repo

```bash
git clone https://github.com/aathiftr2005-debug/Passport-Automation-v1.git
cd Passport-Automation-v1
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your Supabase credentials (see `.env.example` for what's needed).

### 5. Run the app

```bash
python app.py
```

App runs at `http://localhost:5000`

---

## Deployment (Render)

1. Push repo to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python app.py`
6. Add environment variables from `.env.example` in the Render dashboard
7. Deploy

> **Note:** Render spins down free services after inactivity. First request after sleep may take ~30 seconds.

---

## Environment variables

See `.env.example` for the full list. Required variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Full Supabase PostgreSQL connection string |
| `SECRET_KEY` | Flask session secret key |

---

## Key implementation notes

- Uses **port 6543** (session pooler) instead of 5432 for Supabase — required for stable connections on Render's free tier
- Password URL-encoded using `urllib.parse.quote` to handle special characters in the connection string
- `db.create_all()` on startup auto-creates tables if they don't exist
- SQLAlchemy `SQLALCHEMY_TRACK_MODIFICATIONS = False` to suppress deprecation warnings

---

## Author

**Aathif T R** — B.E. CSE, Mohamed Sathak Engineering College, Tamil Nadu  
[LinkedIn](https://linkedin.com/in/aathif-tr-) · [GitHub](https://github.com/aathiftr2005-debug)