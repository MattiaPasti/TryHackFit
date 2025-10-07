# 🔎 **TryHackFit — Open Demo** (Flask Password Manager)

[![Python](https://img.shields.io/badge/Python-3.9-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0.1-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-24.0-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Live Demo](https://img.shields.io/badge/🌍_Live_Demo-TryHackFit-2E7D32?style=for-the-badge&logo=globe&logoColor=white)](https://tryme.mattiapasti.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 📌 Overview
TryHackFit is a lightweight Flask-based web application designed as an **educational** password manager demo. The app shows basic flows for user roles, password testing, and ephemeral storage behavior. It is container-ready and can be run locally or with Docker.

> **Important:** This project is a demo. Do **not** use real or sensitive credentials with this app. Demo data may be visible or cleared automatically. See the Security section.

---

## ✨ Features
- Simple Flask backend with templated UI and static assets.
- Role-based UI: two demonstration roles (Role 1, Role 2) with different permissions.
- Demo storage for passwords (ephemeral) — intended for testing only.
- Background watcher that periodically clears the `Password` table to keep demo data transient.
- Docker Compose & Dockerfile for easy deployment.
- Clear privacy/disclaimer pages included.

---

## 🛠 Tech Stack
- **Backend:** Python, Flask, Gunicorn
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Database:** SQL (configurable via `get_db_connection()` in `app.py`)
- **Deployment:** Docker & Docker Compose

---

## 🚦 Roles (demo)
This project includes two sample roles to demonstrate how the UI and permissions change for different users.

- **Role 1 — Regular User**
  - Typical demo user.
  - Can log in, store and retrieve demo passwords in the testing area.
  - Intended for showing the per-user flows and UI of the app.
  - **WARNING:** Do not store your real credentials — demo passwords are ephemeral and considered public for the demo.

- **Role 2 — Admin**
  - Elevated demo role with additional UI features (management pages, overview).
  - Can view aggregated demo data and perform admin-only demo actions (for testing).
  - Admin accounts are for demonstration — do not use real accounts or admin credentials in public demos.

> These role labels are for demo/learning only. Implementations for production must include proper authentication, MFA, logging, and least-privilege DB accounts.

---

## Repository structure
```
C:.
├── .env
├── app.py
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
├── sql-db-1.sql
├── sql-db-2.sql
├── db/
│   └── init.sql
├── media/
├── static/
│   ├── css/
│   │   ├── common_admin.css
│   │   ├── common_user.css
│   │   ├── index_admin.css
│   │   ├── index_user.css
│   │   ├── login.css
│   │   ├── password_test.css
│   │   ├── privacy.css
│   │   └── signin.css
│   ├── imgs/
│   │   ├── logo.png
│   │   ├── site1.png
│   │   └── site2.png
│   └── js/
│       ├── common_admin.js
│       ├── index_user.js
│       ├── login.js
│       ├── password_test.js
│       └── signin.js
└── templates/
    ├── common.html
    ├── common_admin.html
    ├── common_user.html
    ├── index_admin.html
    ├── index_user.html
    ├── login.html
    ├── password_test.html
    ├── privacy.html
    └── signin.html
```

---

## 🚀 Getting started

### Prerequisites
- Python 3.9+ (3.10 recommended)
- pip
- (Optional) Docker & Docker Compose
- A SQL-compatible DB (MySQL/Postgres/SQLite). Configure connection inside `app.py` via `get_db_connection()`.

### Quick local setup
```bash
git clone https://github.com/MattiaPasti/TryHackFit.git
cd TryHackFit

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Run (development)
```bash
# from project root
python app.py
# Open http://localhost:5000
```

### Run with Docker
```bash
docker compose up --build -d
# Open http://localhost:8000 (or the port defined in docker-compose)
```

---

## 🔁 Watcher: automatic password cleanup (demo behavior)
To keep demo data transient, a simple watcher runs in a background thread that **periodically deletes all rows** from the `Password` table.

- **Default interval (public demo commit):** 3600 seconds (1 hour).  
  You can change it via the environment variable `WIPE_INTERVAL` (seconds) or edit the watcher block in `app.py`.

- **To disable the watcher:**
  1. Remove or comment out the watcher block located **before** the `if __name__ == "__main__":` block in `app.py`.  
     OR
  2. Configure the watcher guard (if present) — e.g., `WIPE_ENABLED=false` — and restart the app.

> **WARNING:** The watcher executes `DELETE FROM Password;`. This is destructive and irreversible. Only use it in demo/test environments.

---

## 🔒 Security & privacy notes
- **Do NOT** enter real passwords, personal accounts, or sensitive data into this demo.
- Demo data is ephemeral and intended for testing — assume it is publicly visible or will be removed.
- The repository is **not** production-ready. If you plan to make a production version:
  - Use secure secret management (do not commit `.env`).
  - Use least-privileged DB users.
  - Protect admin actions with authentication & audit trails.
  - Replace destructive background jobs with scheduled, auditable tasks or protected admin endpoints.
  - Add HTTPS, strong auth, and monitoring.

---

## 🌍 Live Demo
You can try the public demo at: **https://tryme.mattiapasti.com**  

---

## 📸 Screenshots

<img width="1885" height="928" alt="Screenshot 2025-10-07 125813" src="https://github.com/user-attachments/assets/934a0d60-1652-489c-8044-faeef03ec951" />
<img width="1886" height="927" alt="Screenshot 2025-10-07 125753" src="https://github.com/user-attachments/assets/36c896f4-60d1-4bfd-b6bf-003292ad9cb7" />

---

## 🧩 Contributing
Contributions are welcome for:
- improving security and separating demo code from production code,
- adding configuration flags for the watcher (enable/disable, token-based triggers),
- adding tests and CI for non-destructive behavior.

Please file issues or pull requests with clear descriptions.

---

## 📜 License
MIT License — see `LICENSE` for details.

---

## ✉️ Contact
Author: **Mattia Pasti** — pastimattia772@gmail.com

---

⚡ Built with ❤️ for educational purposes and portfolio demonstrations.
