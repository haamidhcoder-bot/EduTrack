# Developer Change Report — Teacher-Side Class-Teacher Access

## Objective

Change the teacher-side Student Performance Analysis flow so that:

- A teacher does not choose a class/section manually to view marks.
- The class and section are taken from the logged-in teacher's `Teacher.class_teacher` and `Teacher.class_teacher_sec`.
- A class teacher can view marks only for that assigned class and section.
- The leaderboard is restricted to that same class and section.
- Direct URL manipulation cannot be used to view/edit another class student's marks or reports.
- Duplicate/stale class-selection code is removed where it is no longer needed.

## Changes made

### 1. `shared/decorators.py`

Added a reusable `class_teacher_required` decorator.

It:
- Requires an authenticated session.
- Looks up the logged-in teacher from the database.
- Reads the authoritative `class_teacher` and `class_teacher_sec` values from the Teacher record.
- Synchronizes those values into the session.
- Blocks access when the teacher has no class-teacher assignment.

This centralizes authorization instead of repeating the same class/section check in every route.

### 2. `Student_Performance_Analysis_teacher_side/app/routes/auth.py`

Changed teacher login so that after successful authentication:

- A clean session is created.
- `username` and `logged_in` are stored.
- `class_teacher` and `class_teacher_sec` are stored from the Teacher database record.
- `session.permanent` is used only for the Remember Me behavior.

The previous `session.permanent` check was removed from the login decision. A permanent session is a cookie-lifetime setting, not an authentication/authorization check.

### 3. `app/routes/home.py`

Removed the old class-selection backend logic.

Previously, `/refresh` and `/show_results` accepted a class from the request and wrote it into:

- `session["class_value"]`
- `session["sec"]`

That allowed the teacher-side flow to select arbitrary classes.

Now:
- Class = logged-in teacher's assigned class.
- Section = logged-in teacher's assigned section.
- Only subject and exam are submitted by the Home page.
- `/show_results` stores only the selected subject/exam.
- Results queries are restricted to the teacher's assigned class and section.
- The "All Subjects" totals also filter by section.

The obsolete `/refresh` route was removed.

### 4. `app/routes/marks.py`

Strengthened mark editing.

Before changing a mark, the route now verifies:

- Student exists.
- Student class equals teacher's assigned class.
- Student section equals teacher's assigned section.
- The mark belongs to that student/class/subject/exam.

Therefore a teacher cannot bypass the restriction by changing `roll_no`, `subject`, or `exam_id` in the URL.

### 5. `app/routes/reports.py`

Protected:
- Individual subject graph.
- Pie graph.
- Leaderboard.
- Attendance.

Graph routes now verify that the requested student belongs to the logged-in teacher's class and section.

Leaderboard no longer accepts a class from the form. It always uses the teacher's assigned class and section.

Attendance also uses the assigned class/section and rejects attendance updates for students outside that assignment.

### 6. `app/services/leaderboard_service.py`

Changed the leaderboard service from:

`class + exam`

to:

`class + section + exam`

The leaderboard query joins `Student` so the section restriction is enforced at database-query level.

### 7. `templates/leaderboard.html`

Removed the manual class input.

The page now displays:

`Class X - Section Y Leaderboard`

and the teacher selects only the exam.

### 8. `templates/base.html`

Removed the obsolete `/refresh` route from the Home navigation active-state logic.

### 9. `app/routes/email.py`

The result-sending endpoint now also requires class-teacher authorization.

The marks query is restricted to the teacher's assigned section as well.

### 10. Removed duplicate attendance route

The teacher-side `app/routes/attendance.py` was an older duplicate attendance implementation registered separately from the newer `/attendence` route in `reports.py`.

It was removed from blueprint registration and deleted to avoid having two competing attendance implementations.

## Security/authorization flow

The resulting flow is:

    Teacher login
          |
          v
    Teacher database record
          |
          +--> class_teacher = 10
          |
          +--> class_teacher_sec = "A"
          |
          v
    Protected teacher routes
          |
          v
    Class 10 / Section A only

A form or URL can no longer select Class 11 or Section B to access those students.

## Validation performed

- Python source files were compiled with `compileall`: PASS.
- All HTML/Jinja templates were parsed with Jinja2: PASS.
- Teacher-side source was checked for the old class-selection patterns:
  - `request.form.get("class")`: none remaining.
  - `name="class"` in teacher-side templates: none remaining.
  - `session["class_value"] = class_input`: none remaining.

## Important note

The implementation assumes the existing database design discussed for this project:

- `Teacher.class_teacher` = class number.
- `Teacher.class_teacher_sec` = section.
- `Student.student_class` = class number.
- `Student.section` = section.

No database schema migration is required for this change.
