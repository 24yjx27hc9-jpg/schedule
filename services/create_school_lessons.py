from models.school import School
from models.lesson import Lesson
from services.lesson_creator import lessons_creator

def creator_school_lessons(school : School) -> list[Lesson]:
    result = []
    for school_class in school.classes:
        result.extend(lessons_creator(school_class))
    return result