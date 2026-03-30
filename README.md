# medlang backend

This repository is a production-oriented Django + PostgreSQL backend skeleton.

Quick start:

1. Create a virtual env and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2. Configure env vars (see .env.example)
3. Run migrations and start server
```bash
python manage.py migrate
python manage.py runserver
```
