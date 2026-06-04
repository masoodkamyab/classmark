# PROJECT_STATE.md — ClassPulse

Last updated: 2026-06-04

## Project status

Status: Phase 7 teacher dashboard complete

ClassPulse is a Django + PostgreSQL attendance management MVP.

The app is intended for a teacher who wants QR-based and manual attendance tracking.

## Current stack

Actual stack:

```text
Backend: Django 5.2
Database: PostgreSQL via psycopg
Test database: SQLite in memory
Frontend: Django templates
Authentication: Django custom user model
Environment loading: python-dotenv
Tests: Django test framework
```

## Current apps

Actual apps:

```text
accounts
courses
attendance
reports
```

## Current business rules

These rules are confirmed:

```text
1 class session = 3 sections
1 section = 45 physical minutes
1 section = 1 counted attendance hour
attendance is tracked per section
every 3 late records = 1 absence equivalent
leave/excused absence is counted separately
```

Attendance statuses:

```text
PRESENT
LATE
ABSENT
LEAVE
```

Session statuses:

```text
DRAFT
ACTIVE
CLOSED
```

Attendance record methods:

```text
MANUAL
QR
SYSTEM
```

## Implemented features

* Django project named `config`
* Environment-based development and production settings
* PostgreSQL database configuration
* Isolated SQLite test configuration
* Custom `accounts.User` model with ADMIN, TEACHER, and STUDENT roles
* Student code and optional phone number account fields
* Student code validation and custom user admin integration
* Course and enrollment models with role validation and database constraints
* Course and enrollment Django admin integration
* Class session and three-section structure with transactional section creation
* Session and section Django admin integration
* Attendance records with status and recorded-method choices
* Attendance enrollment and course/session/section relationship validation
* Attendance record database constraints and Django admin integration
* Attendance services for manual section/session marking, manual corrections, and
  transactional missing-record absent marking
* Teacher dashboard with course list, course detail, session creation, and
  session detail pages
* Teacher-only dashboard permissions with course and session ownership checks
* Session attendance matrix showing active enrolled students and each section's
  current attendance status
* Requested Django app structure
* Basic shared templates and project home page
* Initial boot, account, course, session, section, attendance record model, and
  attendance service and teacher dashboard view tests
* Setup documentation and `.env.example`

## Pending feature checklist

### Phase 1 — Project foundation

* [x] Create Django project named `config`
* [x] Configure PostgreSQL
* [x] Add environment-based settings
* [x] Add `.env.example`
* [x] Add README
* [x] Add base tests

### Phase 2 — Accounts

* [x] Create custom user model
* [x] Add roles: ADMIN, TEACHER, STUDENT
* [x] Add student code field
* [x] Add admin integration
* [x] Add account tests

### Phase 3 — Courses

* [x] Create `Course` model
* [x] Create `Enrollment` model
* [x] Add teacher ownership validation
* [x] Add student enrollment validation
* [x] Add uniqueness constraints
* [x] Add course tests

### Phase 4 — Sessions and sections

* [x] Create `ClassSession`
* [x] Create `SessionSection`
* [x] Auto-create 3 sections per session
* [x] Add session statuses
* [x] Add constraints
* [x] Add tests

### Phase 5 — Attendance records

* [x] Create `AttendanceRecord`
* [x] Add statuses: PRESENT, LATE, ABSENT, LEAVE
* [x] Add recorded methods: MANUAL, QR, SYSTEM
* [x] Enforce one record per student per section
* [x] Validate enrollment
* [x] Add tests

### Phase 6 — Attendance services

* [x] Add `attendance/services.py`
* [x] Mark one student for one section
* [x] Mark one student for all 3 sections
* [x] Update existing record safely
* [x] Bulk mark missing records absent
* [x] Add service tests

### Phase 7 — Teacher UI

* [x] Course list page
* [x] Course detail page
* [x] Create session page
* [x] Session detail page
* [x] Permission checks
* [x] View tests

### Phase 8 — Manual attendance UI

* [ ] Manual attendance form
* [ ] Mark one section
* [ ] Mark all sections
* [ ] Optional note field
* [ ] Messages
* [ ] Tests

### Phase 9 — QR token system

* [ ] Create `AttendanceToken`
* [ ] Add secure token generation
* [ ] Add expiry logic
* [ ] Add active/inactive logic
* [ ] Add token tests

### Phase 10 — Teacher QR display

* [ ] Generate QR for session
* [ ] Display QR code
* [ ] Refresh QR token
* [ ] Deactivate old tokens
* [ ] Add permission tests

### Phase 11 — Student QR scan flow

* [ ] Add `/attendance/scan/<token>/`
* [ ] Require login
* [ ] Validate enrollment
* [ ] Validate token
* [ ] Reject expired tokens
* [ ] Reject closed sessions
* [ ] Record present/late
* [ ] Add tests

### Phase 12 — Session closing

* [ ] Close active session
* [ ] Fill missing records as ABSENT
* [ ] Preserve existing records
* [ ] Reject QR scans after close
* [ ] Add tests

### Phase 13 — Reports

* [ ] Add report services
* [ ] Calculate present sections
* [ ] Calculate late sections
* [ ] Calculate absent sections
* [ ] Calculate leave sections
* [ ] Calculate absence hours
* [ ] Calculate late-equivalent absences
* [ ] Calculate total absence equivalent
* [ ] Add tests

### Phase 14 — CSV export

* [ ] Export summary report CSV
* [ ] Export detailed attendance CSV
* [ ] Add permission tests
* [ ] Add CSV content tests

### Phase 15 — Polish

* [ ] Add sample data command
* [ ] Improve README
* [ ] Review permissions
* [ ] Improve error messages
* [ ] Improve basic styling
* [ ] Remove dead code
* [ ] Run full test suite

## Current data model

Implemented models:

```text
User
  role: ADMIN, TEACHER, or STUDENT
  student_code: unique and required by model validation for students
  phone_number: optional

Course
  title
  code
  teacher: must have TEACHER role
  start_date
  end_date: must be on or after start_date
  is_active

Enrollment
  course
  student: must have STUDENT role
  created_at
  is_active
  unique per course/student

ClassSession
  course
  date
  start_time
  end_time: optional and after start_time when provided
  status: DRAFT, ACTIVE, or CLOSED
  unique per course/date
  creates exactly 3 sections transactionally on initial save

SessionSection
  session
  section_number: 1, 2, or 3 and unique per session
  duration_minutes: fixed at 45
  counted_hours: fixed at 1

AttendanceRecord
  student: must have an active enrollment in course
  course
  session: must belong to course
  section: must belong to session and unique per student
  status: PRESENT, LATE, ABSENT, or LEAVE
  recorded_by: optional user reference
  recorded_method: MANUAL, QR, or SYSTEM
  recorded_at
  note: optional
```

Planned models:

```text
AttendanceToken
```

## Current URLs

Implemented URLs:

```text
/
/admin/
/courses/
/courses/<course_id>/
/courses/<course_id>/sessions/create/
/attendance/sessions/<session_id>/
```

Planned URLs may include:

```text
/accounts/login/
/accounts/logout/

/attendance/sessions/<session_id>/manual/
/attendance/sessions/<session_id>/qr/
/attendance/scan/<token>/

/reports/courses/<course_id>/
/reports/courses/<course_id>/export.csv
/reports/courses/<course_id>/details.csv
```

## Current services

Implemented attendance services:

```text
mark_student_for_section
  validates status, active enrollment, session/course, and section/session
  creates or updates one manual attendance record

mark_student_for_session
  validates status, active enrollment, session/course, and the 3-section structure
  transactionally creates or updates all 3 manual attendance records

bulk_mark_missing_students_absent
  validates session/course and the 3-section structure
  transactionally creates SYSTEM/ABSENT records for missing active-enrollment records
  preserves all existing attendance records

change_attendance_record_manually
  validates the existing record relationships and new status
  safely changes the existing record to a manual correction
```

Planned services:

```text
reports/services.py
```

## Current permissions

Implemented teacher dashboard permissions:

* anonymous users are redirected to login from teacher dashboard pages
* non-teacher users receive a forbidden response from teacher dashboard pages
* teachers see only their own courses in the course list
* teachers receive a not-found response for another teacher's course, session
  creation page, or session detail page

Course ownership and enrollment roles remain validated at the model level.

Pending permission rules:

* students scan only enrolled course QR codes
* teachers access only their own reports

## Configuration assumptions

Expected environment variables:

```text
SECRET_KEY
DEBUG
ALLOWED_HOSTS
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
QR_TOKEN_TTL_SECONDS
LATE_THRESHOLD_MINUTES
```

Default business settings:

```text
QR_TOKEN_TTL_SECONDS = 30
LATE_THRESHOLD_MINUTES = 5
SESSION_SECTION_COUNT = 3
SECTION_DURATION_MINUTES = 45
SECTION_COUNTED_HOURS = 1
```

These can be changed later if the teacher wants 10 minutes instead of 5 minutes for late threshold.

## Known decisions

### Decision: Track attendance per section

Reason:

The teacher must calculate absence hours, and one session has 3 sections. Tracking per section gives accurate reports.

### Decision: Keep `LEAVE` separate

Reason:

Leave means excused absence. It should not be mixed with unexcused absence unless requirements change.

### Decision: Use short-lived QR tokens

Reason:

The teacher wants to reduce screenshot sharing between students.

### Decision: Keep frontend simple

Reason:

This is a DIY MVP. Django templates are enough.

### Decision: Filter teacher dashboard objects by ownership

Reason:

Filtering course and session lookups by the signed-in teacher prevents private
course details from being revealed and keeps permission checks explicit.

### Decision: Keep account roles on the custom user model

Reason:

The MVP needs only simple role checks and student-specific identifiers, so
separate profile tables would add unnecessary complexity.

### Decision: Create session sections during initial session save

Reason:

Creating all three fixed sections in the same database transaction keeps session
creation predictable and prevents a partially created session from persisting.

### Decision: Validate attendance relationship consistency

Reason:

Attendance records keep course, session, and section references for direct
queries, so model validation ensures the session belongs to the course, the
section belongs to the session, and the student has an active course enrollment.

### Decision: Keep attendance writes idempotent and transactional

Reason:

Manual section and session marking update an existing student/section record
instead of creating duplicates. Multi-record session marking and missing-record
absent marking run in transactions so partial attendance writes are rolled back.

## Known risks

* QR codes cannot fully prevent cheating.
* Students can still send screenshots quickly.
* Stronger anti-cheating features like GPS, Wi-Fi restriction, or device binding are outside the MVP.
* Authentication and permissions must be tested carefully.
* The custom user model exists from project start; future account fields should be
  added before dependent domain models.

## Test command

Expected command:

```bash
python manage.py test
```

Last result on 2026-06-04 using `.venv/bin/python manage.py test`:

```text
Ran 59 tests in 1.683s
OK
```

If pytest is added later:

```bash
pytest
```

## How agents should update this file

After every meaningful implementation step, update:

* `Last updated`
* `Project status`
* `Implemented features`
* `Pending feature checklist`
* `Current data model`
* `Current URLs`
* `Current services`
* `Current permissions`
* `Known decisions`
* `Known risks`

Do not mark a feature complete unless it is implemented and tested.

Do not claim tests pass unless they were actually run.
