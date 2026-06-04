# ClassPulse — Codex Context

## Project summary

ClassPulse is a Django + PostgreSQL attendance management application for teachers.

The app helps a teacher manage classroom attendance using:

* short-lived QR codes
* manual attendance entry
* class sessions
* 3 attendance sections per session
* late, present, absent, and excused leave statuses
* end-of-term absence calculations

This project is a DIY, clean-code MVP. Prefer simple Django patterns over complex architecture.

## Core business requirements

A teacher wants to track attendance for students in her classes.

Each class meeting is called a `ClassSession`.

Each `ClassSession` has exactly 3 `SessionSection` records.

Business rule:

```text
1 class session = 3 sections
1 section = physically 45 minutes
1 section = counted as 1 attendance hour
1 full missed session = 3 absent hours
```

Attendance is tracked per section, not only per whole session.

Supported attendance statuses:

```text
PRESENT
LATE
ABSENT
LEAVE
```

Meaning:

* `PRESENT`: student attended on time.
* `LATE`: student attended after the allowed present window.
* `ABSENT`: student did not attend and has no valid excuse.
* `LEAVE`: student had an accepted excuse, such as illness, work, prior notice, or certificate.

Late rule:

```text
Every 3 LATE records count as 1 absence equivalent.
```

For reports, calculate:

* present sections
* late sections
* absent sections
* leave sections
* absence hours
* late-equivalent absences
* total absence equivalent

Do not store report totals unless there is a strong reason. Prefer calculated reports.

## Recommended stack

Use:

```text
Backend: Django
Database: PostgreSQL
Frontend: Django templates
Styling: Bootstrap or simple CSS
Authentication: Django auth with custom User model
QR generation: Python qrcode library
Testing: Django TestCase / pytest-django if already configured
```

Avoid adding React, DRF, Celery, Redis, Channels, or complex frontend tooling unless explicitly requested.

## App structure

Expected Django apps:

```text
accounts
courses
attendance
reports
```

Suggested responsibilities:

### accounts

* custom user model
* roles:

  * ADMIN
  * TEACHER
  * STUDENT
* authentication-related logic

### courses

* Course
* Enrollment
* teacher-course ownership
* student enrollment

### attendance

* ClassSession
* SessionSection
* AttendanceRecord
* AttendanceToken
* QR flow
* manual attendance entry
* session closing

### reports

* course report
* per-student report
* CSV export
* absence calculations

## Core models

The project should eventually include these models or equivalent names.

### User

Custom user model.

Fields should support:

* email or username login
* role
* student code for students
* optional phone number

Roles:

```text
ADMIN
TEACHER
STUDENT
```

### Course

Represents a teacher’s class/course.

Fields:

* title
* code
* teacher
* start_date
* end_date
* is_active

Rules:

* only users with role `TEACHER` can own a course

### Enrollment

Connects students to courses.

Fields:

* course
* student
* created_at
* is_active

Rules:

* a student cannot be enrolled twice in the same course
* only users with role `STUDENT` can be enrolled

### ClassSession

Represents one class meeting.

Fields:

* course
* date
* start_time
* optional end_time
* status:

  * DRAFT
  * ACTIVE
  * CLOSED

Rules:

* each session has exactly 3 sections
* when a session is created, create 3 sections automatically
* avoid duplicate sessions for the same course/date unless deliberately changed later

### SessionSection

Represents one of the 3 sections in a class session.

Fields:

* session
* section_number: 1, 2, or 3
* duration_minutes: default 45
* counted_hours: default 1

Rules:

* one session must not have duplicate section numbers
* valid section numbers are 1, 2, and 3

### AttendanceRecord

Represents one student’s attendance status for one section.

Fields:

* student
* course
* session
* section
* status:

  * PRESENT
  * LATE
  * ABSENT
  * LEAVE
* recorded_by
* recorded_method:

  * MANUAL
  * QR
  * SYSTEM
* recorded_at
* optional note

Rules:

* one student can have only one attendance record per section
* student must be enrolled in the course
* session must belong to the course
* section must belong to the session
* manual corrections should update existing records instead of creating duplicates

### AttendanceToken

Represents a temporary QR token.

Fields:

* token
* course
* session
* optional section
* created_at
* expires_at
* is_active

Rules:

* tokens must be secure and unpredictable
* tokens expire quickly, for example after 15–30 seconds
* inactive tokens are invalid
* expired tokens are invalid
* old tokens for the same session should be deactivated when a new one is generated

## QR attendance flow

Teacher flow:

1. Teacher opens a session.
2. Teacher activates the session.
3. Teacher generates a QR code.
4. The QR code points to:

```text
/attendance/scan/<token>/
```

5. Teacher can refresh the QR code.
6. Refreshing creates a new token and deactivates old active tokens for that session.

Student flow:

1. Student logs in.
2. Student scans QR code.
3. System validates:

   * token exists
   * token is active
   * token has not expired
   * session is active
   * student is enrolled in the course
   * student has not already been recorded for the target section/session logic
4. System records attendance.
5. Student sees confirmation.

QR anti-cheating notes:

* QR codes reduce cheating but do not eliminate it.
* The QR token should be short-lived.
* Student login is required.
* Duplicate scans must be safely handled.
* Never trust only the QR code; always check authorization and enrollment.

## Manual attendance flow

Teachers can manually mark attendance.

Requirements:

* mark one section
* mark all 3 sections at once
* update existing records safely
* add optional note
* support PRESENT, LATE, ABSENT, LEAVE

Manual corrections are allowed even after session close.

## Session closing flow

When a teacher closes a session:

* every missing attendance record for enrolled students should become `ABSENT`
* existing records must not be overwritten
* closed sessions reject QR scans
* closing should be idempotent
* use transactions for bulk close operations

## Report calculation rules

For one student in one course:

```text
present_sections = count(PRESENT)
late_sections = count(LATE)
absent_sections = count(ABSENT)
leave_sections = count(LEAVE)

absence_hours = absent_sections * 1
late_equivalent_absences = floor(late_sections / 3)
total_absence_equivalent = absent_sections + late_equivalent_absences
```

Important:

* `LEAVE` is counted separately.
* `LEAVE` does not count as unexcused absence unless requirements change.
* each section counts as 1 hour.
* one full missed session means 3 absent sections / 3 absent hours.

## Permissions

Rules:

* ADMIN can access Django admin.
* TEACHER can manage only their own courses.
* STUDENT can scan QR only for courses they are enrolled in.
* STUDENT cannot access teacher dashboard.
* TEACHER cannot access another teacher’s course/session/report.
* Unauthenticated users should be redirected to login.

Always add tests for permission-sensitive views.

## Coding standards

Follow these rules:

* Keep the app simple.
* Prefer explicit code over clever abstractions.
* Keep business logic in services, not templates.
* Keep complex queries/calculations in services or query helpers.
* Use database constraints for uniqueness and integrity.
* Use model validation where business rules require it.
* Use transactions for multi-record writes.
* Do not add dependencies without clear need.
* Write tests for models, services, permissions, and calculations.
* Keep templates readable.
* Avoid premature optimization.

## Testing expectations

Each feature should include tests.

Minimum test areas:

* model constraints
* model validation
* service functions
* attendance marking
* QR token expiry
* QR scan flow
* permission checks
* session closing
* report calculations
* CSV export

Run before completing a task:

```bash
python manage.py test
```

If pytest is configured:

```bash
pytest
```

## Non-goals for MVP

Do not implement these unless explicitly requested:

* mobile app
* React frontend
* REST API
* real-time WebSocket QR refresh
* Redis
* Celery
* GPS/location tracking
* face recognition
* payment system
* multi-school SaaS tenancy
* advanced analytics dashboard

## Preferred implementation style

Use a clean Django monolith.

Acceptable patterns:

* Django models
* Django forms
* function-based views or class-based views, consistently
* service functions in `services.py`
* selectors/query helpers if needed
* simple templates
* Django messages framework
* Django permissions/login decorators/mixins

Avoid:

* fat views
* business logic in templates
* duplicated report formulas
* hardcoded magic numbers scattered across the codebase
* storing calculated report totals too early
* adding infrastructure before needed
