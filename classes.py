import re
email_validation= re.compile(r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$')
class validator: 
    @staticmethod
    def string_validation(s,field):
        if  not isinstance(s,str) or not s.strip(): 
            raise ValueError(field+ " must be a non-empty string")
    @staticmethod
    def age_validation(i):
        if not isinstance(i,int):
            raise TypeError("Age must be an interger")
        if i <0 : 
            raise ValueError("Age must be non-negative ")
    @staticmethod
    def email_validation(e):
        if not isinstance(e,str) or not email_validation.fullmatch(e): 
            raise ValueError("Invalid Email")
    @staticmethod
    def course_validation(courses):
        if not isinstance(courses, list):
            raise TypeError("courses must be a list")
        if not all(isinstance(c,Course ) for c in courses): 
            raise ValueError("all items in courses must be Course instances")
    @staticmethod
    def student_validation(students): 
        if not isinstance(students, list):
            raise TypeError("students must be a list")
        if not all(isinstance(c,Student) for c in students): 
            raise ValueError("all items in students must be Students instances")
    @staticmethod
    def instructor_validation(instructor):
        if not isinstance(instructor,Instructor): 
            raise TypeError("Instructor must be instant of class instructor") 
    @staticmethod
    def one_course_validation(course):
        if not isinstance(course,Course):
            raise TypeError ("Expected a Course Class instance")
    @staticmethod
    def one_student_validation(student):
        if not isinstance(student, Student):
            raise TypeError("Expected a student class instance ")
###################################
class Person : 
    def __init__(self,name,age,email):
        validator.string_validation(name,"Name")
        validator.age_validation(age)
        validator.email_validation(email)
        self.name = name 
        self.age = age 
        self.__email = email 
    def get_email(self):
        return self.__email  
    def introduce (self): 
        print ("Name : ", self.name , " Age : ", self.age , "-years-old")
    # def to_dict(self):
    #     return {
    #         "class" :"Person", 
    #         "name" : self.name , 
    #         "age" : self.age, 
    #         "email": self.__email, 
    #     }
    # @classmethod
    # def from_dict(cls,data, lookup = None): 
    #     return cls(data["name"], data["age"], data["email"]) 
    
class Student(Person): 
    def __init__(self, name, age,email, student_id,courses= None): 
        super().__init__(name,age,email) 
        validator.string_validation(student_id,"student_id")
        self.student_id = student_id  
        if courses is None : 
            self.registered_courses = []
        else : 
            validator.course_validation(courses)
            self.registered_courses = courses[:]
    def register_course(self,course): 
        validator.one_course_validation(course)
        if course not in self.registered_courses: 
            self.registered_courses.append(course) 
    # def to_dict(self):
    #     return { 
    #         "class" : "Student", 
    #         "name":self.name , 
    #         "age": self.age, 
    #         "email" : self.get_email(), 
    #         "student_id": self.student_id , 
    #         "registered_courses" : [c.course_id for c in self.registered_courses], 
    #         }
    # @classmethod
    # def from_dict(cls,data,lookup=None): 
    #     registered_courses = [Course.from_dict(sd) for sd in data["registered_courses"]]
    #     return cls(data["name"], data["age"],data["email"],data["student_id"], registered_courses)
        
class Instructor(Person): 
    def __init__(self, name, age, email, instructor_id,courses=None):
        super().__init__(name, age, email)
        validator.string_validation(instructor_id,"instructor_id")
        self.instructor_id = instructor_id  
        if courses is None : 
            self.assigned_courses = []
        else : 
            validator.course_validation(courses)
            self.assigned_courses = courses[:]
    def assign_course(self,course): 
        validator.one_course_validation(course)
        if (course not in self.assigned_courses ): 
            self.assigned_courses.append(course)
    # def to_dict(self):
    #     return { 
    #         "class" : "Instructor", 
    #         "name":self.name,
    #         "age": self.age, 
    #         "email" :self.get_email(), 
    #         "instructor_id": self.instructor_id , 
    #         "assigned_courses" : [c.to_dict() for c in self.assigned_courses], 
    #         }
    # @classmethod
    # def from_dict(cls,data,lookup = None): 
    #     assigned_courses = [Course.from_dict(cd) for cd in data["assigned_courses"]]
    #     return cls(data["name"],data["age"],data["email"],data["instructor_id"],assigned_courses)
            
class Course: 
    def __init__(self,course_id, course_name , instructor, students=None): 
        validator.string_validation(course_id,"course_id")
        validator.string_validation(course_name,"course_name")
        validator.instructor_validation(instructor)
        
        self.course_id = course_id 
        self.course_name = course_name
        self.instructor = instructor 
        if students is None : 
            self.enrolled_students = []
        else : 
            validator.student_validation(students)
            self.enrolled_students = students[:]
    def add_student(self,student): 
        validator.one_student_validation(student)
        if student not in self.enrolled_students : 
            self.enrolled_students.append(student) 
    # def to_dict(self):
    #     return { 
    #         "course_id" : self.course_id, 
    #         "course_name" :self.course_name, 
    #         "instructor" : self.instructor.to_dict(), 
    #         "students" : [s.student_id for  s in self.enrolled_students], 
    #         }
    # @classmethod
    # def from_dict(cls,data, lookup=None): 
    #     students = [Student.from_dict(sd) for sd in data["students"]]
    #     instructor = Instructor.from_dict(data["instructor"])
    #     return cls(data["course_id"],data["course_name"], instructor, students )
            
