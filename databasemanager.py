import sqlite3

db = sqlite3.connect("school.db")
c = db.cursor()
class DBmanager : 
    @classmethod
    def init_all(self):
        query = """
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL, 
            name  TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL
        ) ; 
        CREATE TABLE IF NOT EXISTS instructors(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            instructor_id TEXT UNIQUE NOT NULL, 
            name TEXT NOT NULL, 
            age INTEGER NOT NULL,
            email TEXT NOT NULL
        ) ; 
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT UNIQUE NOT NULL,
            course_name TEXT NOT NULL,
            instructor_id TEXT,
            FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS student_courses(
            student_id INTEGER, 
            course_id INTEGER, 
            PRIMARY KEY (student_id, course_id), 
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE, 
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS instructor_courses(
            instructor_id INTEGER, 
            course_id INTEGER, 
            PRIMARY KEY (instructor_id, course_id), 
            FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE CASCADE, 
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        )
        """
        c.executescript(query)
        db.commit()

    # Insert Functions: 
    @staticmethod
    def ins_student_record(student_id, name , age, email):
        c.execute("INSERT INTO students(student_id,name,age,email) VALUES (?,?,?,?)", (student_id,name,age,email))
        db.commit()

    @staticmethod
    def ins_instructor_record(instructor_id, name , age, email):
        c.execute("INSERT INTO instructors (instructor_id,name,age,email) VALUES (?,?,?,?)", (instructor_id,name,age,email))
        db.commit()
    @staticmethod
    @staticmethod
    def ins_course_record(course_id, course_name, instructor_uid=None):
        # If an instructor is provided, check existence
        if instructor_uid:
            row = c.execute(
                "SELECT 1 FROM instructors WHERE instructor_id = ?",
                (instructor_uid,)
            ).fetchone()
            if not row:
                raise ValueError(f"Instructor {instructor_uid} does not exist")

        # Insert the course
        c.execute(
            "INSERT INTO courses (course_id, course_name, instructor_id) VALUES (?, ?, ?)",
            (course_id, course_name, instructor_uid)
        )
        db.commit()


    #Delete Function: 
    @staticmethod
    def del_student(student_id):
        check = c.execute("SELECT id FROM students WHERE student_id = ?",(student_id,)).fetchone()
        if check : 
            c.execute("DELETE  FROM students   WHERE id=?",(check[0],))
            db.commit() 
        else : 
            raise ValueError("Student doesnt exist..")
        
        
        
    @staticmethod    
    def del_instructor(instructorid):
        check = c.execute("SELECT id FROM   instructors WHERE instructor_id = ?",(instructorid,)).fetchone()
        if check : 
            c.execute("DELETE    FROM    instructors  WHERE id =?",( check[0] , )  )
            db.commit(  ) 
        else : 
            raise ValueError("Instructor doesnot exist..")
    @staticmethod    
    def del_course(cid):
        check = c.execute("SELECT id FROM courses WHERE course_id = ?",(cid,)).fetchone()
        if check : 
            c.execute("DELETE  FROM courses   WHERE id=?",(check[0],))
            db.commit() 
        else : 
            raise ValueError("Course was not found")
        
    #register/drop pstudent functions
    @staticmethod
    def reg_student_in_course(student, course):
        check_s = c.execute("SELECT id FROM students WHERE student_id = ?",(student,)).fetchone()
        check_c= c.execute("SELECT id FROM courses WHERE course_id = ?",(course,)).fetchone()
        if  (check_s and check_c):
            c.execute("INSERT OR IGNORE INTO student_courses(student_id,course_id) VALUES (?,?)", 
                    (check_s[0],check_c[0]))
            db.commit()
            return 
        raise ValueError("IDs weren't found")
    @staticmethod
    def drop_student_from_course(student, course):
        check_s = c.execute("SELECT id FROM students WHERE student_id = ?",(student,)).fetchone()
        check_c= c.execute("SELECT id FROM courses WHERE course_id = ?",(course,)).fetchone()
        if  (check_s and check_c):
            c.execute("DELETE FROM student_courses WHERE student_id = ?  AND course_id = ?", 
                    (check_s[0],check_c[0]))
            db.commit()
            return 
        raise ValueError("IDs weren't found")

    @staticmethod
    def assign_inst_to_course(instructor_uid, course_uid):
        # Get primary keys
        inst_row = c.execute("SELECT id FROM instructors WHERE instructor_id = ?", (instructor_uid,)).fetchone()
        course_row = c.execute("SELECT id FROM courses WHERE course_id = ?", (course_uid,)).fetchone()

        if not inst_row or not course_row:
            raise ValueError("Instructor or Course not found")

        inst_pk = inst_row[0]
        course_pk = course_row[0]

        c.execute("UPDATE courses SET instructor_id = ? WHERE id = ?", (instructor_uid, course_pk))
        db.commit()
    @staticmethod
    def unassign_inst_from_course(instructor_uid: str, course_uid: str):
        # Resolve UIDs -> PKs
        inst_row = c.execute(
            "SELECT id FROM instructors WHERE instructor_id = ?",
            (instructor_uid,)
        ).fetchone()
        if not inst_row:
            raise ValueError(f"Instructor {instructor_uid} not found")
        inst_pk = inst_row[0]

        course_row = c.execute(
            "SELECT id, instructor_id FROM courses WHERE course_id = ?",
            (course_uid,)
        ).fetchone()
        if not course_row:
            raise ValueError(f"Course {course_uid} not found")
        course_pk, current = course_row

        # Validate assignment
        if current is None:
            raise ValueError(f"Course {course_uid} has no instructor assigned")

        # current may be an INTEGER PK or a TEXT UID
        if isinstance(current, int):
            # PK schema
            if current != inst_pk:
                # show human-readable UID in the error if possible
                cur_uid = c.execute(
                    "SELECT instructor_id FROM instructors WHERE id = ?",
                    (current,)
                ).fetchone()
                cur_uid = cur_uid[0] if cur_uid else f"pk={current}"
                raise ValueError(f"Course {course_uid} is assigned to {cur_uid}, not {instructor_uid}")
        else:
            # UID schema (TEXT)
            if str(current) != instructor_uid:
                raise ValueError(f"Course {course_uid} is assigned to {current}, not {instructor_uid}")

        # Unassign in courses
        c.execute("UPDATE courses SET instructor_id = NULL WHERE id = ?", (course_pk,))

        # Clean the join table (assumes it stores PKs)
        c.execute(
            "DELETE FROM instructor_courses WHERE instructor_id = ? AND course_id = ?",
            (inst_pk, course_pk)
        )

        db.commit()




    @staticmethod
    def all_stu():
        q = "SELECT * FROM students"
        return c.execute(q).fetchall()
    @staticmethod
    def all_instructors():
        query = "SELECT * FROM instructors"
        return c.execute(query).fetchall()
    @staticmethod
    def all_courses():
        q = "SELECT * FROM courses"
        return c.execute(q).fetchall()

    @staticmethod
    def get_courses_for_student(studentid):
        check = c.execute("SELECT id FROM students WHERE student_id = ? ", (studentid,)).fetchone( )
        if not check : 
            raise ValueError("Student isnt found..")
        sid = check[0]
        q = """
            SELECT courses.course_id FROM courses 
            JOIN student_courses ON courses.id = student_courses.course_id
            WHERE student_courses.student_id = ?
        """
        res = c.execute(q,(sid,)).fetchall()
        return [r[0] for r in res]

    @staticmethod
    def get_courses_for_instructor(instructor_uid):
        q = "SELECT course_id FROM courses WHERE instructor_id = ?"
        rows = c.execute(q, (instructor_uid,)).fetchall()
        return [r[0] for r in rows]

    @staticmethod
    def get_students_in_course(courseid):
        check = c.execute("SELECT id FROM courses WHERE course_id = ? ", (courseid,)).fetchone( )
        if not check : 
            raise ValueError("Course isnot found..")
        cid = check[0]
        q = """
            SELECT students.student_id FROM students
            JOIN student_courses ON students.id = student_courses.student_id
            WHERE student_courses.course_id = ?
        """
        res = c.execute(q,(cid,)).fetchall()
        return [r[0] for r in res]


d= DBmanager()
d.init_all()