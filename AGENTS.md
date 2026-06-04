# AGENTS.md — ClassPulse

This file gives coding agents the operating rules for the ClassPulse project.

## Project identity

Project name: `ClassPulse`

ClassPulse is a Django + PostgreSQL classroom attendance application.

The MVP helps a teacher:

* manage courses
* enroll students
* create class sessions
* track attendance per section
* generate short-lived QR codes
* manually edit attendance
* close sessions
* calculate absence reports

## Main rule

Do not drift from the MVP.

When implementing features, follow the current task only. Do not add unrelated features, libraries, apps, APIs, or frontend frameworks.

## Business rules that must not change without approval

1. One class session has exactly 3 sections.
2. Each section is physically 45 minutes.
3. Each section counts as 1 attendance hour.
4. Attendance is recorded per section.
5. Status values are:

   * `PRESENT`
   * `LATE`
   * `ABSENT`
   * `LEAVE`
6. `LEAVE` means excused absence and is counted separately.
7. Every 3 `LATE` records count as 1 absence equivalent in reports.
8. A student can have only one attendance record per section.
9. Teachers can manage only their own courses.
10. Students can scan QR only for courses they are enrolled in.
11. QR tokens must be temporary, secure, and expire quickly.
12. Closed sessions must reject QR scans.
13. Closing a session marks missing records as `ABSENT` without overwriting existing records.

## Technical stack

Use:

* Django
* PostgreSQL
* Django templates
* Django forms
* Django auth with custom user model
* Python QR generation library
* Django tests

Do not add these unless explicitly requested:

* React
* Vue
* Next.js
* Django REST Framework
* Celery
* Redis
* Channels/WebSockets
* Docker
* Kubernetes
* GraphQL
* external authentication providers

If one of these seems useful, mention it as a future option but do not implement it.

## Expected Django apps

Use or preserve these apps:

```text
accounts
courses
attendance
reports
```

Do not create new apps unless the existing apps clearly cannot own the behavior.

## Architecture rules

### Keep business logic out of views

Views should coordinate request/response behavior.

Put attendance operations in:

```text
attendance/services.py
```

Put report calculations in:

```text
reports/services.py
```

Use forms for validation of user input where appropriate.

### Keep templates simple

Templates should render data.

Templates should not contain business calculations.

### Use database constraints

Use constraints for:

* unique enrollment per course/student
* unique section number per session
* unique attendance record per student/section
* unique QR token

### Use transactions

Use transactions when:

* creating or updating multiple attendance records
* closing a session
* generating a new QR token while deactivating old tokens
* creating a session and its 3 sections

## Security and permissions

Always check permissions.

Teacher access:

* teacher can view own courses
* teacher can create sessions only for own courses
* teacher can generate QR only for own sessions
* teacher can manually update only own course attendance
* teacher can view reports only for own courses

Student access:

* student must be logged in to scan QR
* student must be enrolled in the course connected to the token
* student cannot access teacher pages
* student cannot submit attendance for another student

Anonymous access:

* redirect to login for protected pages
* do not reveal private course/session details to anonymous users

## QR token rules

Tokens must be generated using secure randomness.

Acceptable:

```python
secrets.token_urlsafe(...)
```

Do not use predictable values such as:

* incremental IDs
* timestamps only
* course IDs only
* session IDs only

A token is valid only if:

* it exists
* `is_active` is true
* current time is before `expires_at`
* the related session is active
* the scanning user is an enrolled student

## Attendance service behavior

Implement attendance writes through service functions.

Expected service capabilities:

* mark one student for one section
* mark one student for all sections in a session
* update an existing record safely
* close session and fill missing records as absent
* create QR attendance from a valid token

Duplicate record behavior:

* do not crash
* update existing record when manual
* handle duplicate QR scans idempotently or return a clear message

## Report service behavior

Reports should calculate values from `AttendanceRecord`.

Formula:

```python
present_sections = count(PRESENT)
late_sections = count(LATE)
absent_sections = count(ABSENT)
leave_sections = count(LEAVE)

absence_hours = absent_sections
late_equivalent_absences = late_sections // 3
total_absence_equivalent = absent_sections + late_equivalent_absences
```

Do not count `LEAVE` as unexcused absence.

Do not use floating point math for these calculations.

## Testing rules

Every meaningful change should include tests.

Add or update tests for:

* model constraints
* model validation
* service behavior
* views
* permissions
* QR token expiry
* QR scan flow
* session closing
* reports
* CSV export

Before saying the task is complete, run:

```bash
python manage.py test
```

If the project uses pytest, run:

```bash
pytest
```

If tests cannot be run, clearly state why.

## Migration rules

When changing models:

1. update model
2. create migration
3. inspect migration
4. run tests

Do not hand-edit migrations unless needed.

Do not delete migrations unless the project is still in initial setup and the user agrees.

## Environment rules

Use environment variables for sensitive settings.

Expected variables may include:

```text
SECRET_KEY
DEBUG
DATABASE_URL
ALLOWED_HOSTS
QR_TOKEN_TTL_SECONDS
LATE_THRESHOLD_MINUTES
```

Never hardcode secrets.

Never commit real credentials.

## Code style

Prefer:

* readable names
* small functions
* explicit validation
* clear constants
* simple Django conventions
* isolated tests

Avoid:

* clever abstractions
* hidden side effects
* large views
* duplicated formulas
* unnecessary dependencies
* premature optimization
* code that only works for sample data

## UI rules

Keep the UI simple.

Teacher pages should support:

* course list
* course detail
* session creation
* session detail
* manual attendance marking
* QR display
* reports
* CSV export

Student pages should support:

* QR scan confirmation
* clear error messages

Use Django messages for success/error feedback.

## Documentation rules

Update documentation when behavior changes.

Keep `PROJECT_STATE.md` current after meaningful changes.

Update:

* completed features
* pending features
* known issues
* commands to run
* assumptions

## Agent workflow

For each task:

1. Read `PROJECT_STATE.md`.
2. Read `.codex/context.md`.
3. Understand the requested scope.
4. Make the smallest useful change.
5. Add or update tests.
6. Run tests.
7. Update `PROJECT_STATE.md`.
8. Summarize what changed.

## Stop conditions

Stop and ask for human review if:

* a requirement conflicts with the business rules
* database schema direction is unclear
* a destructive migration is needed
* authentication model changes after migrations exist
* adding a major dependency seems necessary
* production credentials or secrets are encountered

## Do not hallucinate

If something is not implemented, say it is not implemented.

If a file does not exist, check before assuming.

If a model or function name differs from this document, inspect the actual code and follow the codebase.

Do not claim tests pass unless they were actually run.
