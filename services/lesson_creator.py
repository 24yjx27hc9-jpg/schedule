from models.school_class import SchoolClass
from models.lesson import Lesson

def lessons_creator(school_class : SchoolClass) -> list[Lesson]:
    result = []
    for requirement in school_class.subjects:
        for _ in range(requirement.hours):
            result.append(Lesson(school_class=school_class, subject=requirement.subject, teachers=requirement.teachers))
    return result