from models.subject import Subject


class Teacher:
    def __init__(self, name : str, subjects : list[Subject], classes: list, class_room : dict[str, int]):
        self.name = name
        self.subjects = subjects
        self.classes = classes
        self.class_room = class_room
