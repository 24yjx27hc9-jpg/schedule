from models.subject import Subject
from models.teacher import Teacher
from models.school_class import SchoolClass

class Lesson:
    def __init__(self, subject : Subject, teachers : list[Teacher], school_class : SchoolClass):
        self.subject = subject
        self.teachers = teachers
        self.school_class = school_class
