
import random
from collections import Counter

from models.school import School
from models.school_class import SchoolClass
from models.subject import Subject
from models.subject_requirement import SubjectRequirement
from models.teacher import Teacher
from services.schedule_creator import create_schedule


# ==================================================
# НАСТРОЙКИ СТРЕСС-ТЕСТА
# ==================================================

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

BUILDING = "1"

CLASS_NAMES = [
    "5А", "5Б",
    "6А", "6Б",
    "7А", "7Б",
    "8А", "8Б",
    "9А", "9Б",
]

# Максимальное количество уроков в день
MAX_LESSONS = {
    5: 6,
    6: 6,
    7: 7,
    8: 7,
    9: 8,
}


# ==================================================
# УЧЕБНЫЕ ПЛАНЫ
# Часы в неделю на один класс
# ==================================================

CURRICULUM = {
    5: {
        "Русский язык": 5,
        "Литература": 3,
        "Математика": 5,
        "Английский язык": 3,
        "История": 2,
        "География": 1,
        "Биология": 1,
        "Информатика": 1,
        "Физкультура": 3,
        "Технология": 1,
        "Музыка": 1,
        "ИЗО": 1,
        "ОДНКНР": 1,
    },
    6: {
        "Русский язык": 5,
        "Литература": 3,
        "Математика": 5,
        "Английский язык": 3,
        "История": 2,
        "География": 2,
        "Биология": 1,
        "Информатика": 1,
        "Физкультура": 3,
        "Технология": 1,
        "Музыка": 1,
        "ИЗО": 1,
        "ОДНКНР": 1,
    },
    7: {
        "Русский язык": 4,
        "Литература": 2,
        "Алгебра": 3,
        "Геометрия": 2,
        "Английский язык": 3,
        "История": 2,
        "Обществознание": 1,
        "География": 2,
        "Биология": 2,
        "Физика": 2,
        "Информатика": 1,
        "Физкультура": 3,
        "Технология": 1,
        "Музыка": 1,
        "ИЗО": 1,
    },
    8: {
        "Русский язык": 3,
        "Литература": 2,
        "Алгебра": 3,
        "Геометрия": 2,
        "Английский язык": 3,
        "История": 2,
        "Обществознание": 1,
        "География": 2,
        "Биология": 2,
        "Физика": 2,
        "Химия": 2,
        "Информатика": 1,
        "Физкультура": 3,
        "Технология": 1,
        "ОБЗР": 1,
    },
    9: {
        "Русский язык": 3,
        "Литература": 3,
        "Алгебра": 3,
        "Геометрия": 2,
        "Английский язык": 3,
        "История": 2,
        "Обществознание": 2,
        "География": 2,
        "Биология": 2,
        "Физика": 3,
        "Химия": 2,
        "Информатика": 2,
        "Физкультура": 3,
        "ОБЗР": 1,
    },
}


# ==================================================
# СОЗДАНИЕ ПРЕДМЕТОВ И УЧИТЕЛЕЙ
# ==================================================

all_subject_names = {
    subject_name
    for curriculum in CURRICULUM.values()
    for subject_name in curriculum
}

subjects = {
    name: Subject(name)
    for name in sorted(all_subject_names)
}

# Один учитель на предмет.
# Он может вести уроки во всех подходящих классах.
teachers = {
    name: Teacher(
        name=f"Учитель: {name}",
        subjects=[subject],
        classes=[],
        class_room={BUILDING: number},
    )
    for number, (name, subject) in enumerate(
        subjects.items(),
        start=1,
    )
}


# ==================================================
# СОЗДАНИЕ 10 КЛАССОВ
# ==================================================

school_classes = []

for class_name in CLASS_NAMES:
    grade = int(class_name[:-1])

    school_class = SchoolClass(
        name=class_name,
        building=BUILDING,
        subjects=[],
        max_lesson_per_day=MAX_LESSONS[grade],
    )

    # Если поле есть в модели — задаём лимит.
    school_class.max_lesson_per_day = MAX_LESSONS[grade]

    for subject_name, hours in CURRICULUM[grade].items():
        subject = subjects[subject_name]
        teacher = teachers[subject_name]

        school_class.subjects.append(
            SubjectRequirement(
                teachers=[teacher],
                hours=hours,
                subject=subject,
            )
        )

        teacher.classes.append(school_class)

    school_classes.append(school_class)


school = School(classes=school_classes)


# ==================================================
# ПРЕДВАРИТЕЛЬНАЯ СТАТИСТИКА
# ==================================================

expected_by_class = {
    school_class.name: sum(
        requirement.hours
        for requirement in school_class.subjects
    )
    for school_class in school_classes
}

expected_total = sum(expected_by_class.values())

print("=" * 60)
print("СТРЕСС-ТЕСТ ГЕНЕРАТОРА РАСПИСАНИЯ")
print("=" * 60)

print(f"Классов: {len(school_classes)}")
print(f"Предметов: {len(subjects)}")
print(f"Учителей: {len(teachers)}")
print(f"Всего уроков по учебному плану: {expected_total}")

print("\nНагрузка по классам:")

for school_class in school_classes:
    name = school_class.name
    grade = int(name[:-1])

    print(
        f"  {name}: {expected_by_class[name]} уроков/неделю; "
        f"максимум {MAX_LESSONS[grade]} в день"
    )


# ==================================================
# ЗАПУСК ГЕНЕРАТОРА
# ==================================================

print("\n" + "=" * 60)
print("ГЕНЕРАЦИЯ РАСПИСАНИЯ")
print("=" * 60)

schedule = create_schedule(school)


# ==================================================
# ПРОВЕРКА РЕЗУЛЬТАТА
# ==================================================

actual_by_class = Counter()
actual_by_teacher_slot = Counter()
actual_by_class_day = Counter()
actual_by_class_subject = Counter()

for slot, lessons in schedule.lessons.items():
    for lesson in lessons:
        class_name = lesson.school_class.name

        actual_by_class[class_name] += 1
        actual_by_class_day[
            (class_name, slot.day)
        ] += 1

        actual_by_class_subject[
            (class_name, lesson.subject.name)
        ] += 1

        for teacher in lesson.teachers:
            actual_by_teacher_slot[
                (teacher.name, slot.day, slot.lesson_number)
            ] += 1


placed_total = sum(actual_by_class.values())

print("\n" + "=" * 60)
print("РЕЗУЛЬТАТЫ СТРЕСС-ТЕСТА")
print("=" * 60)

print(f"Поставлено уроков: {placed_total} / {expected_total}")
print(f"Не поставлено: {expected_total - placed_total}")

print("\nНагрузка по классам:")

for school_class in school_classes:
    name = school_class.name
    expected = expected_by_class[name]
    actual = actual_by_class[name]

    daily_load = [
        actual_by_class_day[(name, day)]
        for day in __import__(
            "models.day", fromlist=["Day"]
        ).Day
    ]

    status = "OK" if actual == expected else "ОШИБКА"

    print(
        f"  {name}: {actual}/{expected} уроков; "
        f"по дням {daily_load}; {status}"
    )


# Проверка конфликтов учителей
teacher_conflicts = {
    key: count
    for key, count in actual_by_teacher_slot.items()
    if count > 1
}

# Проверка дневных лимитов
daily_limit_errors = []

for school_class in school_classes:
    name = school_class.name
    grade = int(name[:-1])
    limit = MAX_LESSONS[grade]

    for day in __import__(
        "models.day", fromlist=["Day"]
    ).Day:
        count = actual_by_class_day[(name, day)]

        if count > limit:
            daily_limit_errors.append(
                (name, day, count, limit)
            )

# Проверка количества уроков по каждому предмету
subject_errors = []

for school_class in school_classes:
    name = school_class.name

    for requirement in school_class.subjects:
        subject_name = requirement.subject.name
        actual = actual_by_class_subject[
            (name, subject_name)
        ]

        if actual != requirement.hours:
            subject_errors.append(
                (name, subject_name, actual, requirement.hours)
            )


print("\n" + "=" * 60)
print("ПРОВЕРКА ОГРАНИЧЕНИЙ")
print("=" * 60)

print(f"Конфликтов учителей: {len(teacher_conflicts)}")
print(f"Нарушений дневных лимитов: {len(daily_limit_errors)}")
print(f"Ошибок по предметным часам: {len(subject_errors)}")

if teacher_conflicts:
    print("\nКонфликты учителей:")
    for (teacher, day, lesson_number), count in teacher_conflicts.items():
        print(
            f"  {teacher}, {day}, урок {lesson_number}: "
            f"{count} занятий одновременно"
        )

if daily_limit_errors:
    print("\nПревышения дневных лимитов:")
    for name, day, count, limit in daily_limit_errors:
        print(f"  {name}, {day}: {count} при лимите {limit}")

if subject_errors:
    print("\nОшибки по предметам:")
    for name, subject, actual, expected in subject_errors:
        print(
            f"  {name}, {subject}: "
            f"{actual}/{expected} уроков"
        )


print("\n" + "=" * 60)

if (
    placed_total == expected_total
    and not teacher_conflicts
    and not daily_limit_errors
    and not subject_errors
):
    print("СТРЕСС-ТЕСТ ПРОЙДЕН!")
else:
    print("СТРЕСС-ТЕСТ НЕ ПРОЙДЕН: смотри ошибки выше.")

print("=" * 60)

# Полное расписание
schedule.print_schedule()


