import tkinter as tk 
from tkinter import ttk
from tkstudent import Student_Tb
from tkinstructor import inst_Tb
from tkcourse import crs_tb

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("School Management System")
        self.geometry("1080x650")
        self._build_ntbk()

    def _build_ntbk(self):
        self.nb = ttk.Notebook(self)    
        self.studtab = Student_Tb(self.nb)
        self.nb.add(self.studtab,text="Students")
        self.insttab = inst_Tb(self.nb)
        self.nb.add(self.insttab,text="Instructors")
        self.courtab = crs_tb(self.nb)
        self.nb.add(self.courtab,text="Courses")
        self.nb.pack(fill="both", expand=True)

if __name__ =="__main__":
    App().mainloop()
        