from PyQt5 import QtWidgets
from databasemanager import DBmanager
import json

class stud_p(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        v = QtWidgets.QVBoxLayout(self)

        form1 = QtWidgets.QHBoxLayout()
        self.in_sid = QtWidgets.QLineEdit(); self.in_sid.setPlaceholderText("student_id")
        self.in_name = QtWidgets.QLineEdit(); self.in_name.setPlaceholderText("name")
        self.in_age = QtWidgets.QLineEdit(); self.in_age.setPlaceholderText("age (int)")
        self.in_email = QtWidgets.QLineEdit(); self.in_email.setPlaceholderText("email")
        self.btn_create = QtWidgets.QPushButton("Create")
        self.btn_bulk = QtWidgets.QPushButton("Bulk Create (JSON)")
        form1.addWidget(self.in_sid); form1.addWidget(self.in_name)
        form1.addWidget(self.in_age); form1.addWidget(self.in_email)
        form1.addWidget(self.btn_create); form1.addWidget(self.btn_bulk)
        v.addLayout(form1)

        form2 = QtWidgets.QHBoxLayout()
        self.reg_sid = QtWidgets.QLineEdit(); self.reg_sid.setPlaceholderText("student_id")
        self.reg_cid = QtWidgets.QLineEdit(); self.reg_cid.setPlaceholderText("course_id")
        self.btn_reg = QtWidgets.QPushButton("Register")
        self.btn_drop = QtWidgets.QPushButton("Drop")
        form2.addWidget(self.reg_sid); form2.addWidget(self.reg_cid)
        form2.addWidget(self.btn_reg); form2.addWidget(self.btn_drop)
        v.addLayout(form2)

        form3 = QtWidgets.QHBoxLayout()
        self.del_sid = QtWidgets.QLineEdit(); self.del_sid.setPlaceholderText("student_id")
        self.btn_del = QtWidgets.QPushButton("Delete")
        form3.addWidget(self.del_sid); form3.addWidget(self.btn_del)
        v.addLayout(form3)

        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["student_id","name","age","email","courses"])
        self.table.horizontalHeader().setStretchLastSection(True)
        v.addWidget(self.table)

        row_actions = QtWidgets.QHBoxLayout()
        self.btn_refresh = QtWidgets.QPushButton("Refresh")
        self.btn_export = QtWidgets.QPushButton("Export visible to JSON")
        row_actions.addWidget(self.btn_refresh)
        row_actions.addWidget(self.btn_export)
        row_actions.addStretch(1)
        v.addLayout(row_actions)

        self.btn_refresh.clicked.connect(self.reload)
        self.btn_export.clicked.connect(self.export_json)
        self.btn_create.clicked.connect(self.create_one)
        self.btn_bulk.clicked.connect(self.bulk_create_json)
        self.btn_reg.clicked.connect(self.register)
        self.btn_drop.clicked.connect(self.drop)
        self.btn_del.clicked.connect(self.delete)
        self.table.itemSelectionChanged.connect(self._on_row_selected)
        self.reload()

    def _info(self, msg): QtWidgets.QMessageBox.information(self, "Info", msg)
    def _err(self, msg):  QtWidgets.QMessageBox.critical(self, "Error", msg)

    def _save_json_path(self, title):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, title, "", "JSON (*.json)")
        return path

    def _open_json_path(self, title):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, title, "", "JSON (*.json)")
        return path

    def reload(self):
        self.table.setRowCount(0)
        rows = DBmanager.all_stu()  
        for (_pk, sid, name, age, email) in rows:
            courses = ", ".join(DBmanager.get_courses_for_student(sid))
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, val in enumerate((sid, name, str(age), email, courses)):
                self.table.setItem(r, c, QtWidgets.QTableWidgetItem(val))

    def export_json(self):
        path = self._save_json_path("Save Students JSON")
        if not path: return
        data = []
        for r in range(self.table.rowCount()):
            row = {
                "student_id": self.table.item(r,0).text() if self.table.item(r,0) else "",
                "name": self.table.item(r,1).text() if self.table.item(r,1) else "",
                "age": self.table.item(r,2).text() if self.table.item(r,2) else "",
                "email": self.table.item(r,3).text() if self.table.item(r,3) else "",
                "courses": self.table.item(r,4).text() if self.table.item(r,4) else "",
            }
            data.append(row)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self._info(f"Exported {len(data)} row(s).")

    def create_one(self):
        sid = self.in_sid.text().strip()
        name = self.in_name.text().strip()
        age = self.in_age.text().strip()
        email = self.in_email.text().strip()
        if not (sid and name and age.isdigit() and email):
            return self._err("Fill all student fields correctly.")
        try:
            DBmanager.ins_student_record(sid, name, int(age), email)
            self.in_sid.clear(); self.in_name.clear(); self.in_age.clear(); self.in_email.clear()
            self.reload()
        except Exception as e:
            self._err(str(e))

    def bulk_create_json(self):
        path = self._open_json_path("Select Students JSON")
        if not path: return
        ok, errs = 0, []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("students", []) if isinstance(data, dict) else data
            if not isinstance(items, list):
                return self._err("JSON must be a list or have key 'students'.")
            for obj in items:
                try:
                    sid = str(obj.get("student_id","")).strip()
                    name = str(obj.get("name","")).strip()
                    age = obj.get("age", None)
                    email = str(obj.get("email","")).strip()
                    if not (sid and name and email and isinstance(age, (int,float,str))):
                        raise ValueError("Missing student_id,name,age,email")
                    DBmanager.ins_student_record(sid, name, int(age), email)
                    ok += 1
                except Exception as e:
                    errs.append(f"{obj}: {e}")
            self.reload()
            msg = f"Created {ok} student(s)."
            if errs: msg += f"\nErrors: {len(errs)} (showing first 10)\n" + "\n".join(errs[:10])
            self._info(msg)
        except Exception as e:
            self._err(str(e))

    def register(self):
        sid = self.reg_sid.text().strip()
        cid = self.reg_cid.text().strip()
        if not (sid and cid): return self._err("Provide student_id and course_id.")
        try:
            DBmanager.reg_student_in_course(sid, cid)
            self.reg_sid.clear(); self.reg_cid.clear()
            self.reload()
        except Exception as e:
            self._err(str(e))

    def drop(self):
        sid = self.reg_sid.text().strip()
        cid = self.reg_cid.text().strip()
        if not (sid and cid): return self._err("Provide student_id and course_id.")
        try:
            DBmanager.drop_student_from_course(sid, cid)
            self.reg_sid.clear(); self.reg_cid.clear()
            self.reload()
        except Exception as e:
            self._err(str(e))

    def delete(self):
        sid = self.del_sid.text().strip()
        if not sid: return self._err("Provide student_id.")
        try:
            DBmanager.del_student(sid)
            self.del_sid.clear()
            self.reload()
        except Exception as e:
            self._err(str(e))

    def _on_row_selected(self):
        r = self.table.currentRow()
        if r < 0: return
        item = self.table.item(r, 0)
        sid = item.text() if item else ""
        self.reg_sid.setText(sid)
        self.del_sid.setText(sid)
