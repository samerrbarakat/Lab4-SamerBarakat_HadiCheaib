from PyQt5 import QtWidgets
from databasemanager import DBmanager
import json

class cors_p(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        v = QtWidgets.QVBoxLayout(self)

        form1 = QtWidgets.QHBoxLayout()
        self.in_cid = QtWidgets.QLineEdit(); self.in_cid.setPlaceholderText("course_id")
        self.in_cname = QtWidgets.QLineEdit(); self.in_cname.setPlaceholderText("course_name")
        self.in_inst = QtWidgets.QLineEdit(); self.in_inst.setPlaceholderText("instructor_id (optional)")
        self.btn_create = QtWidgets.QPushButton("Create")
        self.btn_bulk = QtWidgets.QPushButton("Bulk Create (JSON)")
        form1.addWidget(self.in_cid); form1.addWidget(self.in_cname); form1.addWidget(self.in_inst)
        form1.addWidget(self.btn_create); form1.addWidget(self.btn_bulk)
        v.addLayout(form1)

        form2 = QtWidgets.QHBoxLayout()
        self.del_cid = QtWidgets.QLineEdit(); self.del_cid.setPlaceholderText("course_id")
        self.btn_del = QtWidgets.QPushButton("Delete")
        form2.addWidget(self.del_cid); form2.addWidget(self.btn_del)
        v.addLayout(form2)

        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["course_id","course_name","instructor_id","students"])
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
        rows = DBmanager.all_courses()  
        for (_pk, cid, cname, instid) in rows:
            students = ", ".join(DBmanager.get_students_in_course(cid))
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, val in enumerate((cid, cname, instid or "", students)):
                self.table.setItem(r, c, QtWidgets.QTableWidgetItem(val))

    def export_json(self):
        path = self._save_json_path("Save Courses JSON")
        if not path: return
        data = []
        for r in range(self.table.rowCount()):
            row = {
                "course_id": self.table.item(r,0).text() if self.table.item(r,0) else "",
                "course_name": self.table.item(r,1).text() if self.table.item(r,1) else "",
                "instructor_id": self.table.item(r,2).text() if self.table.item(r,2) else "",
                "students": self.table.item(r,3).text() if self.table.item(r,3) else "",
            }
            data.append(row)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self._info(f"Exported {len(data)} row(s).")

    def create_one(self):
        cid = self.in_cid.text().strip()
        cname = self.in_cname.text().strip()
        inst = self.in_inst.text().strip() or None
        if not (cid and cname): return self._err("course_id and course_name required.")
        try:
            DBmanager.ins_course_record(cid, cname, inst)
            self.in_cid.clear(); self.in_cname.clear(); self.in_inst.clear()
            self.reload()
        except Exception as e:
            self._err(str(e))

    def bulk_create_json(self):
        path = self._open_json_path("Select Courses JSON")
        if not path: return
        ok, errs = 0, []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("courses", []) if isinstance(data, dict) else data
            if not isinstance(items, list):
                return self._err("JSON must be a list or have key 'courses'.")
            for obj in items:
                try:
                    cid = str(obj.get("course_id","")).strip()
                    cname = str(obj.get("course_name","")).strip()
                    inst = obj.get("instructor_id", None)
                    inst_uid = str(inst).strip() if inst not in (None, "") else None
                    if not (cid and cname):
                        raise ValueError("Missing course_id, course_name")
                    DBmanager.ins_course_record(cid, cname, inst_uid)
                    ok += 1
                except Exception as e:
                    errs.append(f"{obj}: {e}")
            self.reload()
            msg = f"Created {ok} course(s)."
            if errs: msg += f"\nErrors: {len(errs)} (showing first 10)\n" + "\n".join(errs[:10])
            self._info(msg)
        except Exception as e:
            self._err(str(e))

    def delete(self):
        cid = self.del_cid.text().strip()
        if not cid: return self._err("Provide course_id.")
        try:
            DBmanager.del_course(cid)
            self.del_cid.clear()
            self.reload()
        except Exception as e:
            self._err(str(e))

    def _on_row_selected(self):
        r = self.table.currentRow()
        if r < 0: return
        item = self.table.item(r, 0)
        cid = item.text() if item else ""
        self.del_cid.setText(cid)
