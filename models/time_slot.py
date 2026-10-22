from models.day import Day

class TimeSlot:
    def __init__(self, day : Day, lesson_number : int):
        self.day = day
        self.lesson_number = lesson_number

    def __eq__(self, other):
        if not isinstance(other, TimeSlot):
            return NotImplemented
        return (
                self.day == other.day
                and self.lesson_number == other.lesson_number
        )

    def __hash__(self):
        return hash((self.day, self.lesson_number))