import tkinter as tk 
from tkinter import ttk , messagebox
from databasemanager import DBmanager
from tkinter import filedialog
import json

class Student_Tb(ttk.Frame):
    def __init__(self,prnt):
        super().__init__(prnt)
        
        self.columnconfigure(0,weight = 1 )
        self.rowconfigure(1,weight = 1)
        
        tp= ttk.LabelFrame(self,text= "Student Actions..")
        tp.grid(row = 0 , column = 0 , sticky = "ew", padx = 10 , pady = 10 )
        
        ttk.Label(tp,text = "Student ID").grid(row=0,column=0,padx=5, pady=5)
        self.entry_stuid = ttk.Entry(tp,width=15); self.entry_stuid.grid(row=0,column=1)
        ttk.Label(tp, text="Name").grid(row=0, column=2, padx=5, pady=5)
        self.entry_name = ttk.Entry(tp, width=15); self.entry_name.grid(row=0, column=3)
        ttk.Label(tp, text="Age").grid(row=0, column=4, padx=5, pady=5)
        self.entry_age = ttk.Entry(tp, width=5); self.entry_age.grid(row=0, column=5)
        ttk.Label(tp, text="Email").grid(row=0, column=6, padx=5, pady=5)
        self.entry_email = ttk.Entry(tp, width=20); self.entry_email.grid(row=0, column=7)
        ttk.Button(tp, text="Create", command=self.create).grid(row=0, column=8, padx=5)
        ttk.Button(tp, text="Bulk Create (JSON)", command=self.bulk_create_students_json).grid(row=0, column=9, padx=5)

        # Register / Drop
        ttk.Label(tp, text="Student ID").grid(row=1, column=0, padx=5, pady=5)
        self.entry_stuid_reg = ttk.Entry(tp, width=15); self.entry_stuid_reg.grid(row=1, column=1)
        ttk.Label(tp, text="Course ID").grid(row=1, column=2, padx=5, pady=5)
        self.entry_corsid_reg = ttk.Entry(tp, width=15); self.entry_corsid_reg.grid(row=1, column=3)
        ttk.Button(tp, text="Register", command=self.register).grid(row=1, column=4, padx=5)
        ttk.Button(tp, text="Drop", command=self.on_drop).grid(row=1, column=5, padx=5)

        # Delete Student
        ttk.Label(tp, text="Student ID").grid(row=2, column=0, padx=5, pady=5)
        self.entry_stuid_del = ttk.Entry(tp, width=15); self.entry_stuid_del.grid(row=2, column=1)
        ttk.Button(tp, text="Delete", command=self.on_delete).grid(row=2, column=2, padx=5)

        # --- Bottom Panel: Table ---
        tablef = ttk.Frame(self)
        tablef.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tablef.columnconfigure(0, weight=1)
        tablef.rowconfigure(0, weight=1)

        cols = ("student_id", "name", "age", "email", "courses")
        self.tree = ttk.Treeview(tablef, columns=cols, show="headings")
        for col, width in zip(cols, (120, 180, 60, 220, 300)):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=width, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(tablef, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)
        ttk.Button(tablef, text="Refresh", command=self.reload_view).grid(row=1, column=0, sticky="w", padx=5, pady=(6,0))
        ttk.Button(tablef, text="Export to JSON", command=self.export_json).grid(row=1, column=0, sticky="w", padx=5, pady=(6,0))

        self.reload_view()

    def bulk_create_students_json(self):
        """
        Accepts either:
        [
        {"student_id":"S001","name":"Ali","age":20,"email":"ali@example.com"},
        {"student_id":"S002","name":"Sara","age":21,"email":"sara@aub.edu.lb"}
        ]
        or
        { "students": [ { ... }, { ... } ] }
        """
        path = filedialog.askopenfilename(
            title="Select Students JSON",
            filetypes=[("JSON files","*.json"), ("All files","*.*")]
        )
        if not path:
            return

        ok, errs = 0, []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # normalize: allow either list or {"students":[...]}
            if isinstance(data, dict):
                items = data.get("students", [])
            else:
                items = data

            if not isinstance(items, list):
                raise ValueError("JSON must be a list of student objects or an object with key 'students' containing a list.")

            for obj in items:
                try:
                    sid = str(obj.get("student_id", "")).strip()
                    name = str(obj.get("name", "")).strip()
                    age  = obj.get("age", None)
                    email = str(obj.get("email", "")).strip()
                    if not (sid and name and email and isinstance(age, (int, float, str))):
                        raise ValueError("Missing one of required fields: student_id, name, age, email")
                    age_i = int(age)
                    DBmanager.ins_student_record(sid, name, age_i, email)
                    ok += 1
                except Exception as e:
                    errs.append(f"{obj}: {e}")

            self.reload_view()
            msg = f"Created {ok} student(s)."
            if errs:
                msg += f"\n{len(errs)} error(s):\n" + "\n".join(errs[:10])
                if len(errs) > 10:
                    msg += f"\n...and {len(errs)-10} more."
            messagebox.showinfo("Bulk Create (Students JSON)", msg)
        except Exception as e:
            messagebox.showerror("Bulk Create failed", str(e))

    def export_json(self):
        try:
            # Build an array of dicts using the Treeview’s current columns & values
            cols = self.tree["columns"]
            out = []
            for iid in self.tree.get_children():
                vals = self.tree.item(iid, "values")
                out.append({k: v for k, v in zip(cols, vals)})

            path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files","*.json")],
                title="Save Students JSON"
            )
            if not path:
                return

            with open(path, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Export", f"Exported {len(out)} student row(s) to JSON.")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def create(self):
        stuid = self.entry_stuid.get().strip()
        name = self.entry_name.get().strip()
        age = self.entry_age.get().strip()
        email = self.entry_email.get().strip()
        if not (stuid and name and age.isdigit() and email): 
            return messagebox.showerror("Error"," Fill all fields correctly.")
        try : 
            DBmanager.ins_student_record(stuid,name,int(age),email)
            self.entry_stuid.delete(0,"end")
            self.entry_name.delete(0,"end")
            self.entry_age.delete(0,"end")
            self.entry_email.delete(0,"end")
            self.reload_view()
        except Exception as error : 
            messagebox.showerror("Error",str(error))
            
    def register(self):
        stuid = self.entry_stuid_reg.get().strip()
        corsid = self.entry_corsid_reg.get().strip()
        if not (stuid and corsid):
            return messagebox.showerror("Error","Provide Student id and course id . ")
        try: 
            DBmanager.reg_student_in_course(stuid,corsid)
            self.entry_stuid_reg.delete(0,"end")
            self.entry_corsid_reg.delete(0,"end")
            self.reload_view() 
        
        except Exception as e : 
            messagebox.showerror("Err",str(e))
            
    def on_drop(self):
        stuid = self.entry_stuid_reg.get().strip()
        corsid = self.entry_corsid_reg.get().strip()
        if not (stuid and corsid):
            return messagebox.showerror("Error","Provide Student id and course id . ")
        try: 
            DBmanager.drop_student_from_course(stuid,corsid)
            self.entry_stuid_reg.delete(0,"end")
            self.entry_corsid_reg.delete(0,"end")
            self.reload_view() 
        
        except Exception as e : 
            messagebox.showerror("Err",str(e))
            
    def on_delete(self):
        stid = self.entry_stuid_del.get().strip()
        if not stid : 
            return messagebox.showerror("Err", "Missing Student Id")
        try : 
            DBmanager.del_student(stid)
            self.entry_stuid_del.delete(0,"end")
            self.reload_view()
        except Exception as e : 
            messagebox.showerror("Err",str(e))
    def on_select_row(self,_event): 
        sel = self.tree.selection()
        if not sel: return 
        vals = self.tree.item(sel[0],"values")
        sid = vals[0]
        self.entry_stuid_reg.delete(0,"end") ; self.entry_stuid_reg.insert(0,sid)
        self.entry_stuid_del.delete(0,"end") ; self.entry_stuid_del.insert(0,sid)
        
    def reload_view(self):
        for iid in self.tree.get_children(): 
            self.tree.delete(iid)
        rows = DBmanager.all_stu()
        for (_pk,sid,name,age,email) in rows : 
            courses = DBmanager.get_courses_for_student(sid)
            self.tree.insert("","end",values=(sid,name,age,email, ",".join(courses)))
            
            
        
        
        