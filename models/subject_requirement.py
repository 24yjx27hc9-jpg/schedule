from models.teacher import Teacher
from models.subject import Subject

class SubjectRequirement:
    def __init__(self, teachers : list[Teacher], hours : int, subject : Subject):
        self.teachers = teachers
        self.hours = hours
        self.subject = subject
