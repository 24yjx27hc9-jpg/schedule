from  models.subject_requirement import SubjectRequirement

class SchoolClass:
    def __init__(self, name : str, building : str, subjects : list[SubjectRequirement], max_lesson_per_day : int):
        self.name = name
        self.building = building
        self.subjects = subjects
        self.max_lesson_per_day = max_lesson_per_day

    def __str__(self):
        return self.name