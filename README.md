# simple-school-ms

A Python-based project that demonstrates Object-Oriented Programming, GUI development with Tkinter and PyQt5, and database integration with SQLite. The system manages Students, Instructors, and Courses with full CRUD operations, search, data persistence (JSON/CSV/DB), and export/backup features.

Manage **Students**, **Instructors**, and **Courses**. Two UIs included:

- **PyQt5** (sidebar + pages, no tabs)
- **Tkinter** (tabbed fallback)

Both talk to the same SQLite DB (`school.db`).

---

## Quick Start

```bash
# 1) Install (PyQt only; Tkinter is stdlib)
pip install PyQt5

# 2) Run PyQt UI
python pyqtapp.py

# (or) Run Tkinter UI
python tkapp.py
```

> On first run, the DB schema is created automatically (or via `init_all()` in `databasemanager.py`).

---

## What You Can Do

- **Create / Delete** students, instructors, courses
- **Bulk Create (JSON)** on each page/tab
- **Relationships**

  - Students ↔ Courses: Register / Drop
  - Instructors ↔ Courses: Assign / Unassign

- **Export visible table → JSON** (UI snapshot)

---

## Minimal Project Layout

```
pyqtapp.py          # PyQt entry (sidebar + pages)
pyqtstudent.py      # Students page (PyQt)
pyqtinstructor.py   # Instructors page (PyQt)
pyqtcourse.py       # Courses page (PyQt)

tkapp.py            # Tk entry (tabs)
tkstudent.py        # Students tab (Tk)
tkinstructor.py     # Instructors tab (Tk)
tkcourse.py         # Courses tab (Tk)

databasemanager.py  # SQLite connection + schema + CRUD + relations
classes.py          # (optional) small helpers / models
```

---

## Bulk JSON Format (examples)

**Students**

```json
[
  {
    "student_id": "S001",
    "name": "Ali Barakat",
    "age": 20,
    "email": "ali.barakat@example.com"
  },
  {
    "student_id": "S002",
    "name": "Sara Haddad",
    "age": 21,
    "email": "sara.haddad@aub.edu.lb"
  }
]
```

**Instructors**

```json
[
  {
    "instructor_id": "I001",
    "name": "Dr. Kamal Khalil",
    "age": 45,
    "email": "kamal.khalil@example.com"
  }
]
```

**Courses**

```json
[
  {
    "course_id": "CS101",
    "course_name": "Intro to Programming",
    "instructor_id": "I001"
  },
  { "course_id": "EECE200", "course_name": "Circuits I" }
]
```

> Also accepted: `{ "students": [... ] }`, `{ "instructors": [ ... ] }`, `{ "courses": [ ... ] }`.

---

## PyQt vs Tkinter (what’s different?)

- **PyQt**

  - Left **sidebar** + **pages** (QStackedWidget)
  - File dialogs for **Bulk Create (JSON)** and **Export**
  - Tables via `QTableWidget`

- **Tkinter**

  - **Tabs** (ttk.Notebook)
  - Same actions (create, bulk create, relationships, export)
  - Tables via `ttk.Treeview`

Functionally the same; only the UI toolkit changes.

---

## Common Issue

**Bulk JSON imports show nothing**

- Click **Refresh** on the page/tab.
- Check keys/values match the examples above.

---

## That’s it

- Run **PyQt** for the sidebar/pages experience.
- Use **Tkinter** if you prefer tabs or want stdlib-only.
- Bulk import JSON, manage relationships, and export what you see.

