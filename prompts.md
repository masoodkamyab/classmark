
Read AGENTS.md, PROJECT_STATE.md, and .codex/context.md first.

Follow the project rules exactly.

Implement only the next task below.
Do not add extra features.
Update PROJECT_STATE.md after the implementation.
Run or explain the test command.

Task:




# 15 Incremental Codex Prompts for Django Attendance QR App

## Prompt 1 — Project setup

Create a clean Django project for an attendance management application.

Requirements:

* Use Django and PostgreSQL.
* Use environment variables for configuration.
* Create a project named `config`.
* Create these Django apps:

  * `accounts`
  * `courses`
  * `attendance`
  * `reports`
* Use a custom user model from the beginning.
* Add basic project structure suitable for long-term maintenance.
* Add `.env.example`.
* Add `requirements.txt` or `pyproject.toml`.
* Add `README.md` with setup instructions.
* Add initial tests to verify the project boots correctly.

Quality requirements:

* Keep code simple and readable.
* Do not over-engineer.
* Use Django best practices.
* Add comments only where they clarify non-obvious logic.
* Make sure `python manage.py test` passes.

---

## Prompt 2 — Custom user model and roles

Implement authentication models for the app.

Requirements:

* Use a custom `User` model.
* Add user roles:

  * `TEACHER`
  * `STUDENT`
  * `ADMIN`
* Students should have:

  * student number / student code
  * optional phone number
* Teachers should be able to manage their own classes later.
* Add Django Admin configuration for the custom user model.
* Create tests for:

  * creating a teacher user
  * creating a student user
  * role validation
  * string representation

Quality requirements:

* Keep roles simple.
* Do not add unnecessary profile tables unless clearly needed.
* Make tests clear and isolated.

---

## Prompt 3 — Course and enrollment models

Create the course/class management models.

Requirements:

* In the `courses` app, create:

  * `Course`
  * `Enrollment`
* A course should have:

  * title
  * code
  * teacher
  * start date
  * end date
  * active/inactive status
* Enrollment should connect students to courses.
* A student should not be enrolled twice in the same course.
* Only users with role `STUDENT` can be enrolled as students.
* Only users with role `TEACHER` can own a course.
* Add Django Admin setup.
* Add model tests.

Quality requirements:

* Use database constraints where appropriate.
* Use model-level validation where appropriate.
* Keep names explicit and readable.

---

## Prompt 4 — Class sessions and sections

Implement session structure.

Business rule:

* One class meeting/session has 3 sections.
* Each section is physically 45 minutes.
* For attendance calculation, each section counts as 1 hour.

Requirements:

* In the `attendance` app, create:

  * `ClassSession`
  * `SessionSection`
* `ClassSession` should belong to a course and have:

  * date
  * start time
  * optional end time
  * status: draft, active, closed
* When a session is created, automatically create 3 sections:

  * Section 1
  * Section 2
  * Section 3
* Each section should store:

  * section number
  * duration_minutes = 45
  * counted_hours = 1
* Prevent duplicate sessions for the same course and date unless there is a good reason.
* Add admin configuration.
* Add tests for automatic section creation.

Quality requirements:

* Keep section creation predictable.
* Avoid magic numbers by using constants.
* Add tests for edge cases.

---

## Prompt 5 — Attendance records

Implement attendance records.

Attendance statuses:

* `PRESENT`
* `LATE`
* `ABSENT`
* `LEAVE`

Business rules:

* Attendance is tracked per section.
* Each student can have only one attendance record per section.
* `LEAVE` means excused absence.
* `LATE` is not immediately an absence, but every 3 lates count as 1 absence in reports.

Requirements:

* Create `AttendanceRecord`.
* Fields:

  * student
  * course
  * session
  * section
  * status
  * recorded_by
  * recorded_method: manual or qr
  * recorded_at
  * optional note
* Add constraints to avoid duplicate records.
* Add useful query helpers or model methods where appropriate.
* Add admin configuration.
* Add tests for:

  * one record per student per section
  * valid status choices
  * valid enrollment requirement
  * manual record creation

Quality requirements:

* Keep the model normalized.
* Avoid duplicating calculated totals in the database.
* Use readable constants for statuses.

---

## Prompt 6 — Attendance services layer

Create a service layer for attendance operations.

Requirements:

* Add an `attendance/services.py`.
* Implement service functions for:

  * marking one student for one section
  * marking one student for all 3 sections of a session
  * bulk marking absent students at the end of a session
  * changing a previous attendance record manually
* Services should validate:

  * student is enrolled in the course
  * session belongs to course
  * section belongs to session
  * status is valid
* Add tests for service behavior.

Quality requirements:

* Keep business logic out of views.
* Views should call services.
* Services should be easy to test without templates.
* Use transactions where multiple records are created.

---

## Prompt 7 — Teacher dashboard views

Create the first teacher-facing UI.

Requirements:

* Use Django templates.
* Use simple Bootstrap or clean plain HTML.
* Add views for:

  * course list
  * course detail
  * create session
  * session detail
* On session detail, show:

  * session date
  * 3 sections
  * enrolled students
  * each student’s attendance status per section
* Add permissions:

  * only teachers can access teacher dashboard
  * teachers can only access their own courses
* Add URL routes.
* Add basic tests for permissions and page access.

Quality requirements:

* Keep views simple.
* Avoid complex frontend frameworks.
* Use class-based or function-based views consistently.
* Make templates readable.

---

## Prompt 8 — Manual attendance entry UI

Implement manual attendance entry.

Requirements:

* On the session detail page, allow the teacher to manually mark attendance.
* Teacher should be able to mark:

  * all 3 sections at once
  * or one specific section
* Status options:

  * Present
  * Late
  * Absent
  * Leave
* Add optional note field for leave/excused cases.
* Use POST forms.
* Use CSRF protection.
* Show success/error messages.
* Add tests for:

  * valid manual submission
  * invalid student
  * unauthorized teacher
  * duplicate update should update existing record, not crash

Quality requirements:

* Keep form handling clean.
* Use Django forms where appropriate.
* Do not put business rules directly in templates.

---

## Prompt 9 — QR token model and generation

Implement temporary QR attendance tokens.

Requirements:

* Create `AttendanceToken`.
* A token should belong to:

  * course
  * session
  * optionally section
* Fields:

  * token
  * created_at
  * expires_at
  * is_active
* Token should expire quickly, for example after 15 or 30 seconds.
* Add a secure random token generator.
* Add service function to create a new token.
* Add method/property:

  * `is_expired`
  * `is_valid`
* Add tests for:

  * token creation
  * expiry logic
  * inactive token invalidation
  * token uniqueness

Quality requirements:

* Do not store predictable tokens.
* Use timezone-aware datetimes.
* Keep expiry duration configurable.

---

## Prompt 10 — QR code display for teacher

Implement QR code display for active sessions.

Requirements:

* Add a teacher page/action to generate a QR code for a session.
* QR code should contain a URL like:
  `/attendance/scan/<token>/`
* Use a Python QR library.
* Display the QR code on the teacher screen.
* Add a “refresh QR” button that generates a new token.
* Old tokens should be deactivated when a new token is generated for the same session.
* Add tests for:

  * teacher can generate QR for own session
  * teacher cannot generate QR for another teacher’s session
  * QR token URL is correct
  * old token invalidation

Quality requirements:

* Keep QR generation separate from view logic if possible.
* Do not expose raw implementation details in templates.
* Use clean routes.

---

## Prompt 11 — Student QR scan flow

Implement the student scan attendance flow.

Requirements:

* Add route:
  `/attendance/scan/<token>/`
* Student must be logged in.
* Only students enrolled in the course can submit attendance.
* When a student scans a valid token:

  * check token exists
  * check token is active
  * check token is not expired
  * check session is active
  * record attendance
* Use automatic status based on scan time:

  * within allowed present window: `PRESENT`
  * after late threshold: `LATE`
* Late threshold should be configurable, default 5 or 10 minutes.
* Add a confirmation page after successful scan.
* Add clear error pages/messages for invalid or expired QR.
* Add tests for:

  * valid scan
  * expired token
  * inactive token
  * unenrolled student
  * duplicate scan
  * late scan

Quality requirements:

* Keep the flow secure.
* Avoid leaking course/session data to unauthorized users.
* Make duplicate scans idempotent or safely handled.

---

## Prompt 12 — Session closing and automatic absences

Implement closing a session.

Requirements:

* Teacher can close an active session.
* When closing a session:

  * every enrolled student without a record for a section should be marked `ABSENT`
  * existing records should not be overwritten
* Closed sessions should not accept QR scans.
* Closed sessions can still be manually corrected by the teacher.
* Add tests for:

  * closing session creates missing absences
  * existing present/late/leave records are preserved
  * QR scan rejected after close
  * unauthorized teacher cannot close session

Quality requirements:

* Use transaction for closing session.
* Keep operation repeat-safe: closing twice should not duplicate records.
* Make state transitions explicit.

---

## Prompt 13 — Reports and absence calculation

Implement attendance reports.

Business rules:

* Each section counts as 1 attendance hour.
* One session has 3 sections, so one full missed session equals 3 absent hours.
* Every 3 late records count as 1 absence equivalent.
* `LEAVE` should be counted separately from unexcused absences.
* Reports should show both raw data and calculated totals.

Requirements:

* Add report service functions.
* For each student in a course, calculate:

  * present sections
  * late sections
  * absent sections
  * leave sections
  * absence hours
  * late-equivalent absences
  * total absence equivalent
* Add teacher report page for a course.
* Add per-student detail page.
* Add tests for report calculations.

Quality requirements:

* Keep calculations in services/query functions, not templates.
* Make formula behavior explicit and tested.
* Avoid storing report totals unless necessary.

---

## Prompt 14 — Export reports to CSV

Add CSV export for attendance reports.

Requirements:

* Teacher can export course attendance report as CSV.
* CSV should include:

  * student name
  * student code
  * present sections
  * late sections
  * absent sections
  * leave sections
  * absence hours
  * late-equivalent absences
  * total absence equivalent
* Add a second export for detailed records:

  * date
  * session
  * section number
  * student
  * status
  * recorded method
  * note
* Add tests for:

  * CSV response
  * permissions
  * correct headers
  * correct calculated values

Quality requirements:

* Keep export code clean.
* Use Django `HttpResponse` with CSV writer.
* Do not add heavy dependencies unless needed.

---

## Prompt 15 — Polish, cleanup, tests, and documentation

Review and polish the whole application.

Requirements:

* Improve README with:

  * project purpose
  * setup instructions
  * environment variables
  * database setup
  * how to run tests
  * basic usage flow
* Add sample data command:

  * create teacher
  * create students
  * create course
  * enroll students
  * create sample session
* Review permissions across all views.
* Add missing tests.
* Add useful error messages.
* Add basic styling improvements.
* Add docstrings only for important service functions.
* Run full test suite.
* Fix failing tests.
* Remove dead code.
* Ensure migrations are clean.

Quality requirements:

* Keep code DIY-friendly.
* Keep the UI simple and understandable.
* Prefer explicit code over clever code.
* Make sure the app can be understood and modified by a junior developer.
* Final result should be a clean MVP, not an over-engineered enterprise system.
