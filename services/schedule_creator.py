from models.schedule import Schedule
from models.school import School
from services.create_school_lessons import creator_school_lessons
from services.solve_schedule import solve_schedule
import random

def create_schedule(school : School) -> Schedule:
    lessons = creator_school_lessons(school)
    random.shuffle(lessons)
    schedule = Schedule()
    success = solve_schedule(schedule, lessons)
    if success:
        print(f'УСПЕШНО РАЗМЕЩЕНО {len(lessons)} УРОКОВ')
    else:
        print('НЕ УДАЛОСЬ НАЙТИ ПОЛНОЕ РАСАПИСАНИЕ')
    # placed_count = 0
    # for lesson in lessons:
    #     available_slots = schedule.get_available_slots(lesson)
    #     if not available_slots:
    #         print(
    #             f'Не удалось поставить урок: '
    #             f'{lesson.subject} — '
    #             f'{lesson.school_class}'
    #         )
    #         continue
    #     best_slot = max(available_slots, key=lambda slot: schedule.score_slot(lesson, slot))
    #     schedule.place_lesson(lesson, best_slot)
    #     placed_count += 1

    # print(f'Поставлено {placed_count} из {len(lessons)}')
    return schedule