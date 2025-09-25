import tkinter as tk 
from tkinter import ttk , messagebox
from databasemanager import DBmanager
from tkinter import filedialog
import json

class crs_tb(ttk.Frame):
    def __init__(self,prnt):
        super().__init__(prnt)
        
        self.columnconfigure(0,weight = 1 )
        self.rowconfigure(1,weight = 1)
        
        tp= ttk.LabelFrame(self,text= "CourseActions..")
        tp.grid(row = 0 , column = 0 , sticky = "ew", padx = 10 , pady = 10 )
        
        ttk.Label(tp,text = "Course ID").grid(row=0,column=0,padx=5, pady=5)
        self.entry_cid = ttk.Entry(tp,width=15); self.entry_cid.grid(row=0,column=1)
        ttk.Label(tp, text="Course Name ").grid(row=0, column=2, padx=5, pady=5)
        self.entry_cname = ttk.Entry(tp, width=15); self.entry_cname.grid(row=0, column=3)
        ttk.Label(tp, text="Instructor ID").grid(row=0, column=4, padx=5, pady=5)
        self.entry_instid = ttk.Entry(tp, width=5); self.entry_instid.grid(row=0, column=5)

        ttk.Button(tp, text="Create", command=self.create).grid(row=0, column=8, padx=5)
        ttk.Button(tp, text="Bulk Create (JSON)", command=self.bulk_create_courses_json).grid(row=0, column=9, padx=5)

        ttk.Label(tp, text="Course ID").grid(row=2, column=0, padx=5, pady=5)
        self.entry_cid_del = ttk.Entry(tp, width=15); self.entry_cid_del.grid(row=2, column=1)
        
        ttk.Button(tp, text="Delete", command=self.on_delete).grid(row=2, column=2, padx=5)

        tablef = ttk.Frame(self)
        tablef.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tablef.columnconfigure(0, weight=1)
        tablef.rowconfigure(0, weight=1)

        cols = ("course_id", "course name", "instructor id ", "students")
        self.tree = ttk.Treeview(tablef, columns=cols, show="headings")
        for col, width in zip(cols, (180, 180, 180, 300)):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=width, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(tablef, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)
        ttk.Button(tablef, text="Refresh", command=self.reload_view).grid(row=1, column=0, sticky="w", padx=5, pady=(6,0))
        ttk.Button(tablef, text="Export to JSON", command=self.export_json).grid(row=1, column=1, sticky="w", padx=5, pady=(6,0))

        self.reload_view()

    def bulk_create_courses_json(self):
        """
        Accepts either:
        [
        {"course_id":"EECE200","course_name":"Circuits","instructor_id":"I001"},
        {"course_id":"PHYS210","course_name":"Mechanics"}  # instructor_id optional
        ]
        or
        { "courses": [ { ... }, { ... } ] }
        """
        path = filedialog.askopenfilename(
            title="Select Courses JSON",
            filetypes=[("JSON files","*.json"), ("All files","*.*")]
        )
        if not path:
            return

        ok, errs = 0, []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            items = data.get("courses", []) if isinstance(data, dict) else data
            if not isinstance(items, list):
                raise ValueError("JSON must be a list of course objects or an object with key 'courses' containing a list.")

            for obj in items:
                try:
                    cid = str(obj.get("course_id", "")).strip()
                    cname = str(obj.get("course_name", "")).strip()
                    inst  = obj.get("instructor_id", None)
                    inst_uid = str(inst).strip() if inst not in (None, "") else None
                    if not (cid and cname):
                        raise ValueError("Missing required fields: course_id, course_name")
                    DBmanager.ins_course_record(cid, cname, inst_uid)
                    ok += 1
                except Exception as e:
                    errs.append(f"{obj}: {e}")

            self.reload_view()
            msg = f"Created {ok} course(s)."
            if errs:
                msg += f"\n{len(errs)} error(s):\n" + "\n".join(errs[:10])
                if len(errs) > 10:
                    msg += f"\n...and {len(errs)-10} more."
            messagebox.showinfo("Bulk Create (Courses JSON)", msg)
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
                title="Save Courses JSON"
            )
            if not path:
                return

            with open(path, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Export", f"Exported {len(out)} course row(s) to JSON.")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

        
    def create(self):
        cid = self.entry_cid.get().strip()
        cname = self.entry_cname.get().strip()
        instid = self.entry_instid.get().strip() or None
        if not (cid and cname): 
            return messagebox.showerror("Error","Course ID and Name required.")
        try : 
            DBmanager.ins_course_record(cid, cname, instid)
            self.entry_cid.delete(0,"end")
            self.entry_cname.delete(0,"end")
            self.entry_instid.delete(0,"end")
            self.reload_view()
        except Exception as error : 
            messagebox.showerror("Error",str(error))
  
            
    def on_delete(self):
        cid = self.entry_cid_del.get().strip()
        if not cid : 
            return messagebox.showerror("Err", "Missing Course Id")
        try : 
            DBmanager.del_course(cid)
            self.entry_cid_del.delete(0,"end")
            self.reload_view()
        except Exception as e : 
            messagebox.showerror("Err",str(e))
    
    def on_select_row(self,_event): 
        sel = self.tree.selection()
        if not sel: return 
        vals = self.tree.item(sel[0],"values")
        cid = vals[0]
        self.entry_cid_del.delete(0,"end") ; self.entry_cid_del.insert(0,cid)
        
    def reload_view(self):
        for iid in self.tree.get_children(): 
            self.tree.delete(iid)
        rows = DBmanager.all_courses()
        for (_pk,cid,cname,instid) in rows : 
            students = DBmanager.get_students_in_course(cid)
            self.tree.insert("", "end", values=(cid, cname, instid or "", ", ".join(students)))
            
            
        
        
        