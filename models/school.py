from models.school_class import SchoolClass

class School:
    def __init__(self, classes : list[SchoolClass]):
        self.classes = classes