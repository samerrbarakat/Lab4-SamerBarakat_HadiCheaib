from PyQt5 import QtWidgets
from pyqtstudent import stud_p 
from pyqtinstructor import inst_p 
from pyqtcourse import cors_p

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__() 
        self.setWindowTitle("School Management System")
        self.resize(1080,680)
        
        c = QtWidgets.QWidget()
        self.setCentralWidget(c)
        h = QtWidgets.QHBoxLayout(c)
        
        sidemenu = QtWidgets.QVBoxLayout()
        self.btn_stud = QtWidgets.QPushButton("Students")
        self.btn_inst = QtWidgets.QPushButton("Instructors")
        self.btn_cors = QtWidgets.QPushButton("Courses")
        sidemenu.addWidget(self.btn_stud)
        sidemenu.addWidget(self.btn_inst)
        sidemenu.addWidget(self.btn_cors)
        sidemenu.addStretch(1)
        self.stack = QtWidgets.QStackedWidget()
        self.pagestud = stud_p()
        self.pageinst = inst_p()
        self.pagecors = cors_p()
        self.stack.addWidget(self.pagestud)     
        self.stack.addWidget(self.pageinst)   
        self.stack.addWidget(self.pagecors)   
        h.addLayout(sidemenu)
        h.addWidget(self.stack,1)
        self.btn_stud.clicked.connect(lambda:self.stack.setCurrentIndex(0))
        self.btn_inst.clicked.connect(lambda:self.stack.setCurrentIndex(1))
        self.btn_cors.clicked.connect(lambda:self.stack.setCurrentIndex(2))
        
        self.stack.setCurrentIndex(0)
        
def main(): 
    import sys 
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
            
        
