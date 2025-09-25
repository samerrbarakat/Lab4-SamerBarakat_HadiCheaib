import tkinter as tk 
from tkinter import ttk , messagebox
from databasemanager import DBmanager
from tkinter import filedialog
import json
class inst_Tb(ttk.Frame):
    def __init__(self,prnt):
        super().__init__(prnt)
        
        self.columnconfigure(0,weight = 1 )
        self.rowconfigure(1,weight = 1)
        
        tp= ttk.LabelFrame(self,text= "Instructor Actions..")
        tp.grid(row = 0 , column = 0 , sticky = "ew", padx = 10 , pady = 10 )
        
        ttk.Label(tp,text = "Instructor ID").grid(row=0,column=0,padx=5, pady=5)
        self.entry_instid = ttk.Entry(tp,width=15); self.entry_instid.grid(row=0,column=1)
        ttk.Label(tp, text="Name").grid(row=0, column=2, padx=5, pady=5)
        self.entry_name = ttk.Entry(tp, width=15); self.entry_name.grid(row=0, column=3)
        ttk.Label(tp, text="Age").grid(row=0, column=4, padx=5, pady=5)
        self.entry_age = ttk.Entry(tp, width=5); self.entry_age.grid(row=0, column=5)
        ttk.Label(tp, text="Email").grid(row=0, column=6, padx=5, pady=5)
        self.entry_email = ttk.Entry(tp, width=20); self.entry_email.grid(row=0, column=7)
        ttk.Button(tp, text="Create", command=self.create).grid(row=0, column=8, padx=5)
        ttk.Button(tp, text="Bulk Create (JSON)", command=self.bulk_create_instructors_json).grid(row=0, column=9, padx=5)

        # Register / Drop
        ttk.Label(tp, text="Instructor ID").grid(row=1, column=0, padx=5, pady=5)
        self.entry_instid_reg = ttk.Entry(tp, width=15); self.entry_instid_reg.grid(row=1, column=1)
        ttk.Label(tp, text="Course ID").grid(row=1, column=2, padx=5, pady=5)
        self.entry_corsid_reg = ttk.Entry(tp, width=15); self.entry_corsid_reg.grid(row=1, column=3)
        ttk.Button(tp, text="Assign", command=self.register).grid(row=1, column=4, padx=5)
        ttk.Button(tp, text="Unassign", command=self.on_drop).grid(row=1, column=5, padx=5)

        # Delete instructor
        ttk.Label(tp, text="Instructor ID").grid(row=2, column=0, padx=5, pady=5)
        self.entry_instid_del = ttk.Entry(tp, width=15); self.entry_instid_del.grid(row=2, column=1)
        ttk.Button(tp, text="Delete", command=self.on_delete).grid(row=2, column=2, padx=5)

        # --- Bottom Panel: Table ---
        tablef = ttk.Frame(self)
        tablef.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tablef.columnconfigure(0, weight=1)
        tablef.rowconfigure(0, weight=1)

        cols = ("instructor_id", "name", "age", "email", "courses")
        self.tree = ttk.Treeview(tablef, columns=cols, show="headings")
        for col, width in zip(cols, (120, 180, 60, 220, 300)):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=width, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(tablef, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)
        ttk.Button(tablef, text="Refresh", command=self.reload_view).grid(row=1, column=0,sticky="w", padx=5, pady=(6,0))
        ttk.Button(tablef, text="Export to JSON", command=self.export_json).grid(row=1, column=1, sticky="w", padx=5, pady=(6,0))

        self.reload_view()


    def bulk_create_instructors_json(self):
        """
        Accepts either:
        [
        {"instructor_id":"I001","name":"Dr. Kamal","age":45,"email":"kamal@example.com"},
        {"instructor_id":"I002","name":"Ms. Rima","age":38,"email":"rima@aub.edu.lb"}
        ]
        or
        { "instructors": [ { ... }, { ... } ] }
        """
        path = filedialog.askopenfilename(
            title="Select Instructors JSON",
            filetypes=[("JSON files","*.json"), ("All files","*.*")]
        )
        if not path:
            return

        ok, errs = 0, []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            items = data.get("instructors", []) if isinstance(data, dict) else data
            if not isinstance(items, list):
                raise ValueError("JSON must be a list of instructor objects or an object with key 'instructors' containing a list.")

            for obj in items:
                try:
                    iid = str(obj.get("instructor_id", "")).strip()
                    name = str(obj.get("name", "")).strip()
                    age  = obj.get("age", None)
                    email = str(obj.get("email", "")).strip()
                    if not (iid and name and email and isinstance(age, (int, float, str))):
                        raise ValueError("Missing one of required fields: instructor_id, name, age, email")
                    age_i = int(age)
                    DBmanager.ins_instructor_record(iid, name, age_i, email)
                    ok += 1
                except Exception as e:
                    errs.append(f"{obj}: {e}")

            self.reload_view()
            msg = f"Created {ok} instructor(s)."
            if errs:
                msg += f"\n{len(errs)} error(s):\n" + "\n".join(errs[:10])
                if len(errs) > 10:
                    msg += f"\n...and {len(errs)-10} more."
            messagebox.showinfo("Bulk Create (Instructors JSON)", msg)
        except Exception as e:
            messagebox.showerror("Bulk Create failed", str(e))


    def export_json(self):
        try:
            cols = self.tree["columns"]
            out = []
            for iid in self.tree.get_children():
                vals = self.tree.item(iid, "values")
                out.append({k: v for k, v in zip(cols, vals)})

            path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files","*.json")],
                title="Save Instructors JSON"
            )
            if not path:
                return

            with open(path, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Export", f"Exported {len(out)} instructor row(s) to JSON.")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))
    
    def create(self):
        instid = self.entry_instid.get().strip()
        name = self.entry_name.get().strip()
        age = self.entry_age.get().strip()
        email = self.entry_email.get().strip()
        if not (instid and name and age.isdigit() and email): 
            return messagebox.showerror("Error"," Fill all fields correctly.")
        try : 
            DBmanager.ins_instructor_record(instid,name,int(age),email)
            self.entry_instid.delete(0,"end")
            self.entry_name.delete(0,"end")
            self.entry_age.delete(0,"end")
            self.entry_email.delete(0,"end")
            self.reload_view()
        except Exception as error : 
            messagebox.showerror("Error",str(error))
            
    def register(self):
        instid = self.entry_instid_reg.get().strip()
        corsid = self.entry_corsid_reg.get().strip()
        if not (instid and corsid):
            return messagebox.showerror("Error","Provide instructor id and course id . ")
        try: 
            DBmanager.assign_inst_to_course(instid,corsid)
            self.entry_instid_reg.delete(0,"end")
            self.entry_corsid_reg.delete(0,"end")
            self.reload_view() 
        
        except Exception as e : 
            messagebox.showerror("Err",str(e))
            
    def on_drop(self):
        instid = self.entry_instid_reg.get().strip()
        corsid = self.entry_corsid_reg.get().strip()
        if not (instid and corsid):
            return messagebox.showerror("Error","Provide instructor id and course id . ")
        try: 
            DBmanager.unassign_inst_from_course(instid,corsid)
            self.entry_instid_reg.delete(0,"end")
            self.entry_corsid_reg.delete(0,"end")
            self.reload_view() 
        
        except Exception as e : 
            messagebox.showerror("Err",str(e))
            
    def on_delete(self):
        stid = self.entry_instid_del.get().strip()
        if not stid : 
            return messagebox.showerror("Err", "Missing instructor Id")
        try : 
            DBmanager.del_instructor(stid)
            self.entry_instid_del.delete(0,"end")
            self.reload_view()
        except Exception as e : 
            messagebox.showerror("Err",str(e))
    def on_select_row(self,_event): 
        sel = self.tree.selection()
        if not sel: return 
        vals = self.tree.item(sel[0],"values")
        sid = vals[0]
        self.entry_instid_reg.delete(0,"end") ; self.entry_instid_reg.insert(0,sid)
        self.entry_instid_del.delete(0,"end") ; self.entry_instid_del.insert(0,sid)
        
    def reload_view(self):
        for iid in self.tree.get_children(): 
            self.tree.delete(iid)
        rows = DBmanager.all_instructors()
        for (_pk,sid,name,age,email) in rows : 
            courses = DBmanager.get_courses_for_instructor(sid)
            self.tree.insert("","end",values=(sid,name,age,email, ",".join(courses)))
            
            
        
        
        