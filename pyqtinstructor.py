# instructors_page.py
from PyQt5 import QtWidgets
from databasemanager import DBmanager
import json

class inst_p(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        v = QtWidgets.QVBoxLayout(self)

        form1 = QtWidgets.QHBoxLayout()
        self.in_iid = QtWidgets.QLineEdit(); self.in_iid.setPlaceholderText("instructor_id")
        self.in_name = QtWidgets.QLineEdit(); self.in_name.setPlaceholderText("name")
        self.in_age = QtWidgets.QLineEdit(); self.in_age.setPlaceholderText("age (int)")
        self.in_email = QtWidgets.QLineEdit(); self.in_email.setPlaceholderText("email")
        self.btn_create = QtWidgets.QPushButton("Create")
        self.btn_bulk = QtWidgets.QPushButton("Bulk Create (JSON)")
        form1.addWidget(self.in_iid); form1.addWidget(self.in_name)
        form1.addWidget(self.in_age); form1.addWidget(self.in_email)
        form1.addWidget(self.btn_create); form1.addWidget(self.btn_bulk)
        v.addLayout(form1)

        form2 = QtWidgets.QHBoxLayout()
        self.reg_iid = QtWidgets.QLineEdit(); self.reg_iid.setPlaceholderText("instructor_id")
        self.reg_cid = QtWidgets.QLineEdit(); self.reg_cid.setPlaceholderText("course_id")
        self.btn_assign = QtWidgets.QPushButton("Assign")
        self.btn_unassign = QtWidgets.QPushButton("Unassign")
        form2.addWidget(self.reg_iid); form2.addWidget(self.reg_cid)
        form2.addWidget(self.btn_assign); form2.addWidget(self.btn_unassign)
        v.addLayout(form2)

        form3 = QtWidgets.QHBoxLayout()
        self.del_iid = QtWidgets.QLineEdit(); self.del_iid.setPlaceholderText("instructor_id")
        self.btn_del = QtWidgets.QPushButton("Delete")
        form3.addWidget(self.del_iid); form3.addWidget(self.btn_del)
        v.addLayout(form3)

        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["instructor_id","name","age","email","courses"])
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
        self.btn_assign.clicked.connect(self.assign)
        self.btn_unassign.clicked.connect(self.unassign)
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
        rows = DBmanager.all_instructors()  
        for (_pk, iid, name, age, email) in rows:
            courses = ", ".join(DBmanager.get_courses_for_instructor(iid))
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, val in enumerate((iid, name, str(age), email, courses)):
                self.table.setItem(r, c, QtWidgets.QTableWidgetItem(val))

    def export_json(self):
        path = self._save_json_path("Save Instructors JSON")
        if not path: return
        data = []
        for r in range(self.table.rowCount()):
            row = {
                "instructor_id": self.table.item(r,0).text() if self.table.item(r,0) else "",
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
        iid = self.in_iid.text().strip()
        name = self.in_name.text().strip()
        age = self.in_age.text().strip()
        email = self.in_email.text().strip()
        if not (iid and name and age.isdigit() and email):
            return self._err("Fill all instructor fields correctly.")
        try:
            DBmanager.ins_instructor_record(iid, name, int(age), email)
            self.in_iid.clear(); self.in_name.clear(); self.in_age.clear(); self.in_email.clear()
            self.reload()
        except Exception as e:
            self._err(str(e))

    def bulk_create_json(self):
        path = self._open_json_path("Select Instructors JSON")
        if not path: return
        ok, errs = 0, []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("instructors", []) if isinstance(data, dict) else data
            if not isinstance(items, list):
                return self._err("JSON must be a list or have key 'instructors'.")
            for obj in items:
                try:
                    iid = str(obj.get("instructor_id","")).strip()
                    name = str(obj.get("name","")).strip()
                    age = obj.get("age", None)
                    email = str(obj.get("email","")).strip()
                    if not (iid and name and email and isinstance(age, (int,float,str))):
                        raise ValueError("Missing instructor_id,name,age,email")
                    DBmanager.ins_instructor_record(iid, name, int(age), email)
                    ok += 1
                except Exception as e:
                    errs.append(f"{obj}: {e}")
            self.reload()
            msg = f"Created {ok} instructor(s)."
            if errs: msg += f"\nErrors: {len(errs)} (showing first 10)\n" + "\n".join(errs[:10])
            self._info(msg)
        except Exception as e:
            self._err(str(e))

    def assign(self):
        iid = self.reg_iid.text().strip()
        cid = self.reg_cid.text().strip()
        if not (iid and cid): return self._err("Provide instructor_id and course_id.")
        try:
            DBmanager.assign_inst_to_course(iid, cid)
            self.reg_iid.clear(); self.reg_cid.clear()
            self.reload()
        except Exception as e:
            self._err(str(e))

    def unassign(self):
        iid = self.reg_iid.text().strip()
        cid = self.reg_cid.text().strip()
        if not (iid and cid): return self._err("Provide instructor_id and course_id.")
        try:
            DBmanager.unassign_inst_from_course(iid, cid)
            self.reg_iid.clear(); self.reg_cid.clear()
            self.reload()
        except Exception as e:
            self._err(str(e))

    def delete(self):
        iid = self.del_iid.text().strip()
        if not iid: return self._err("Provide instructor_id.")
        try:
            DBmanager.del_instructor(iid)
            self.del_iid.clear()
            self.reload()
        except Exception as e:
            self._err(str(e))

    def _on_row_selected(self):
        r = self.table.currentRow()
        if r < 0: return
        item = self.table.item(r, 0)
        iid = item.text() if item else ""
        self.reg_iid.setText(iid)
        self.del_iid.setText(iid)
