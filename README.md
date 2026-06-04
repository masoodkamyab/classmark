# ClassPulse

ClassPulse is a Django and PostgreSQL attendance management application.

## Requirements

- Python 3.12+
- PostgreSQL

## Local setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a PostgreSQL database and user:

```sql
CREATE USER classpulse WITH PASSWORD 'classpulse';
CREATE DATABASE classpulse OWNER classpulse;
```

Copy the example environment file and replace its development values as needed:

```bash
cp .env.example .env
```

Apply migrations and start the development server:

```bash
python manage.py migrate
python manage.py runserver
```

The development server loads variables from `.env`. Production deployments
should provide environment variables directly and use
`config.settings.production`.

## Tests

Tests use an isolated in-memory SQLite database, so they do not require a
running PostgreSQL server:

```bash
python manage.py test
```

## Project structure

```text
accounts/    Custom user model and authentication behavior
attendance/  Sessions, sections, attendance records, and QR flows
config/      Project settings, URLs, and deployment entry points
courses/     Courses and enrollments
reports/     Attendance reports and exports
templates/   Shared Django templates
```
