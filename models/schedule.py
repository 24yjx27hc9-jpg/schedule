from models.time_slot import TimeSlot
from models.lesson import Lesson
from models.teacher import Teacher
from models.school_class import SchoolClass
from models.day import Day

class Schedule:
    DAYS = 5
    LESSON_PER_DAY = 8
    def __init__(self):
        self.lessons : dict[TimeSlot, list[Lesson]] = {}
        self.days = [
            [
                []
                for _ in range(self.LESSON_PER_DAY)
            ]
            for _ in range(self.DAYS)
        ]

    def find_lesson(self, lesson: Lesson, slot : TimeSlot) -> bool:
        if self.class_is_busy(lesson.school_class, slot):
            return False
        for teacher in lesson.teachers:
            if self.teacher_is_busy(teacher, slot):
                return False
        return True

    def place_lesson(self, lesson: Lesson, slot : TimeSlot) -> bool:
        if not self.find_lesson(lesson, slot):
            return False
        self.add_lesson(slot, lesson)
        return True

    def add_lesson(self, slot : TimeSlot, lesson: Lesson):
        if slot not in self.lessons:
            self.lessons[slot] = []
        self.lessons[slot].append(lesson)

    def teacher_is_busy(self, teacher : Teacher, slot : TimeSlot) -> bool:
        lessons = self.lessons.get(slot, [])
        return any(
            teacher in lesson.teachers
            for lesson in lessons)

    def class_is_busy(self, school_class : SchoolClass, slot : TimeSlot) -> bool:
        lessons = self.lessons.get(slot, [])
        return any(
            lesson.school_class == school_class
            for lesson in lessons)

    def get_available_slots(self, lesson: Lesson) -> list[TimeSlot]:
        results = []
        for day in Day:
            class_lessons = self.get_class_lessons(lesson.school_class, day)
            if len(class_lessons) >= lesson.school_class.max_lesson_per_day:
                continue
            for lesson_number in range(1, self.LESSON_PER_DAY + 1):
                slot = TimeSlot(day, lesson_number)
                if self.find_lesson(lesson, slot):
                    results.append(slot)
        slots_without_gaps = [
            slot
            for slot in results
            if not self.has_gap(lesson.school_class, slot)
        ]
        if slots_without_gaps:
            return slots_without_gaps
        return results

    def get_class_lesson_count(self, school_class : SchoolClass, day : Day) -> int:
        count = 0
        for slot, lessons in self.lessons.items():
            if slot.day != day:
                continue
            for lesson in lessons:
                if lesson.school_class == school_class:
                    count += 1
        return count

    def score_slot(self, lesson: Lesson, slot: TimeSlot) -> int:
        score = 0
        class_lessons = self.get_class_lessons(
            lesson.school_class,
            slot.day
        )
        score -= len(class_lessons) * 5
        previous_lesson = None
        next_lesson = None
        for current_slot, current_lessons in self.lessons.items():
            if current_slot.day != slot.day:
                continue
            if current_slot.lesson_number == slot.lesson_number - 1:
                for current_lesson in current_lessons:
                    if current_lesson.school_class == lesson.school_class:
                        previous_lesson = current_lesson
            if current_slot.lesson_number == slot.lesson_number + 1:
                for current_lesson in current_lessons:
                    if current_lesson.school_class == lesson.school_class:
                        next_lesson = current_lesson
        subject_days = self.get_subject_days(lesson.school_class, lesson.subject)
        for subject_day in subject_days:
            distance = abs(slot.day.value - subject_day.value)
            if distance == 1:
                score -= 8
            elif distance == 2:
                score -= 4
        if previous_lesson is not None:
            if previous_lesson.subject == lesson.subject:
                score -= 10
        if next_lesson is not None:
            if next_lesson.subject == lesson.subject:
                score -= 10
        if self.has_gap(lesson.school_class, slot):
            score -= 100
        score -= slot.lesson_number
        return score

    def has_gap(self, school_class: SchoolClass, slot: TimeSlot) -> bool:
        lesson_numbers = []
        for current_slot, lessons in self.lessons.items():
            if current_slot.day != slot.day:
                continue
            for lesson in lessons:
                if lesson.school_class == school_class:
                    lesson_numbers.append(current_slot.lesson_number)
        lesson_numbers.append(slot.lesson_number)
        lesson_numbers.sort()
        for i in range(len(lesson_numbers) - 1):
            if lesson_numbers[i + 1] - lesson_numbers[i] > 1:
                return True
        return False

    def get_class_lessons(self, school_class : SchoolClass, day : Day) -> list[Lesson]:
        results = []
        for slot, lessons in self.lessons.items():
            if slot.day != day:
                continue
            for lesson in lessons:
                if lesson.school_class == school_class:
                    results.append((slot, lesson))
        results.sort(key=lambda item: item[0].lesson_number)
        return [item[1] for item in results]

    def get_subject_days(self, school_class : SchoolClass, subject) -> list[Day]:
        result = []
        for slot, lessons in self.lessons.items():
            for lesson in lessons:
                if (
                        lesson.school_class == school_class
                        and lesson.subject == subject
                        and slot.day not in result
                ):
                    result.append(slot.day)
        return result

    def print_schedule(self):
        for slot, lessons in self.lessons.items():
            print(
                f'{slot.day.name} '
                f'{slot.lesson_number} урок:'
            )
            for lesson in lessons:
                print(
                    f'  {lesson.school_class} — '
                    f'{lesson.subject}'
                )