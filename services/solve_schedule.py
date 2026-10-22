from models.schedule import Schedule
from models.lesson import Lesson
from models.time_slot import TimeSlot
from models.day import Day
import random

def solve_schedule(schedule: Schedule, lessons: list[Lesson], max_nodes: int = 100_000, max_attempts: int = 20) -> bool:
    original_lessons = {
        slot: list(items)
        for slot, items in schedule.lessons.items()
    }
    class_totals = {}
    for lesson in lessons:
        school_class = lesson.school_class
        class_totals[school_class] = (
            class_totals.get(school_class, 0) + 1
        )
    def ideal_balance_score() -> float:
        result = 0.0
        days_count = len(Day)
        for total in class_totals.values():
            target = total / days_count
            base, remainder = divmod(total, days_count)
            result += (
                remainder * (base + 1 - target) ** 2
                + (days_count - remainder) * (base - target) ** 2
            )
        return result

    # Чем меньше значение, тем равномернее расписание.
    def balance_score() -> float:
        result = 0.0
        days_count = len(Day)
        for school_class, total in class_totals.items():
            target = total / days_count
            for day in Day:
                count = schedule.get_class_lesson_count(
                    school_class, day
                )
                result += (count - target) ** 2
        return result

    best_schedule = None
    best_score = float('inf')
    total_nodes = 0
    ideal_score = ideal_balance_score()

    def search(remaining: list[Lesson], nodes: list[int]) -> bool:
        if not remaining:
            return True
        if nodes[0] >= max_nodes:
            return False
        nodes[0] += 1
        candidates = []
        for lesson in remaining:
            slots = get_valid_slots(schedule, lesson)
            if not slots:
                return False
            candidates.append((lesson, slots))
        lesson, slots = min(
            candidates,
            key=lambda item: len(item[1])
        )
        next_remaining = list(remaining)
        next_remaining.remove(lesson)
        slots.sort(
            key=lambda slot: schedule.score_slot(lesson, slot),
            reverse=True
        )
        for slot in slots:
            if not schedule.place_lesson(lesson, slot):
                continue
            if search(next_remaining, nodes):
                return True
            schedule.lessons[slot].remove(lesson)
            if not schedule.lessons[slot]:
                del schedule.lessons[slot]
        return False
    for attempt in range(max_attempts):
        schedule.lessons = {
            slot: list(items)
            for slot, items in original_lessons.items()
        }
        shuffled_lessons = list(lessons)
        random.shuffle(shuffled_lessons)
        nodes = [0]
        success = search(shuffled_lessons, nodes)
        total_nodes += nodes[0]
        if not success:
            continue
        current_score = balance_score()
        if current_score < best_score:
            best_score = current_score
            best_schedule = {
                slot: list(items)
                for slot, items in schedule.lessons.items()
            }
        if best_score <= ideal_score:
            break
    if best_schedule is not None:
        schedule.lessons = best_schedule
        print(
            f'Поиск завершён. Попыток: {attempt + 1}; '
            f'проверено узлов: {total_nodes}'
        )
        print(f'Оценка равномерности: {best_score:.2f}')
        return True
    schedule.lessons = original_lessons
    print(
        f'Решение не найдено. Попыток: {max_attempts}; '
        f'проверено узлов: {total_nodes}'
    )
    return False


def get_valid_slots(schedule: Schedule, lesson: Lesson) -> list[TimeSlot]:
    return schedule.get_available_slots(lesson)

def print_difficulty_report(schedule: Schedule):
    school_classes = set()

    for lessons in schedule.lessons.values():
        for lesson in lessons:
            school_classes.add(lesson.school_class)

    print('\n' + '=' * 60)
    print('РАСПРЕДЕЛЕНИЕ СЛОЖНОСТИ ПРЕДМЕТОВ')
    print('=' * 60)

    for school_class in sorted(school_classes, key=str):
        print(f'\nКласс {school_class}:')
        total_lessons = 0
        total_difficulty = 0

        for day in Day:
            lessons = schedule.get_class_lessons(
                school_class,
                day
            )

            difficulty = sum(
                schedule.SUBJECT_DIFFICULTY.get(
                    lesson.subject.name,
                    2
                )
                for lesson in lessons
            )

            count = len(lessons)
            average = difficulty / count if count else 0

            total_lessons += count
            total_difficulty += difficulty

            print(
                f'  {day.name:<10} | '
                f'уроков: {count} | '
                f'сложность: {difficulty:>2} | '
                f'средняя: {average:.2f}'
            )

        average_week = (
            total_difficulty / total_lessons
            if total_lessons else 0
        )

        print(
            f'  За неделю: {total_lessons} уроков, '
            f'сумма сложности: {total_difficulty}, '
            f'средняя сложность: {average_week:.2f}'
        )