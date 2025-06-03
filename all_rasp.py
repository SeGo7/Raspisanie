# coding: utf-8
import re
from collections import defaultdict

pattern_day = r'^(Понедельник|Вторник|Среда|Четверг|Пятница|Суббота)$'


def get_all_raspisanie(file_name="all.csv"):
    file_path = file_name

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    class_line = lines[1].strip().split(",")

    classes = {}

    # Определяем индексы классов
    class_indices = []
    for idx, name in enumerate(class_line):
        name = name.strip()
        if re.match(r'\d{1,2} [а-я]', name.lower()):
            class_indices.append((name, idx))

    # Добавим последний индекс для корректного расчета диапазонов
    class_indices.append(("END", len(class_line)))

    # Заполняем classes
    for i in range(len(class_indices) - 1):
        name, start_idx = class_indices[i]
        next_idx = class_indices[i + 1][1]
        num_cells = next_idx - start_idx

        if num_cells >= 4:
            # две подгруппы
            classes[name] = [start_idx, start_idx + 2]
        else:
            # одна подгруппа
            classes[name] = [start_idx]

    # Парсинг расписания
    all = {}
    schedule = defaultdict(list)
    i = 3
    lesson_number = 1

    while i < len(lines) - 1:
        subject_line = lines[i].strip().split(",")
        teacher_line = lines[i + 1].strip().split(",")

        if re.match(pattern_day, subject_line[0], re.IGNORECASE):
            all[subject_line[0]] = defaultdict(list)
            schedule = all[subject_line[0]]
            lesson_number = 1

        i += 2

        for class_name, indices in classes.items():
            for group_idx, col in enumerate(indices, start=1):
                try:
                    subject = subject_line[col].strip()
                    teacher = teacher_line[col].strip()
                    # Поиск кабинета:
                    # если следующая ячейка (col+1) не содержит предмета или учителя — вероятно, это кабинет
                    room = ""
                    if col + 1 < len(subject_line) and subject_line[col + 1] != "":
                        room = subject_line[col + 1]
                    elif col + 3 < len(subject_line):
                        room = subject_line[col + 3]

                    if subject:
                        lesson = {
                            "урок": lesson_number,
                            "предмет": subject,
                            "кабинет": room,
                            "учитель": teacher
                        }
                        schedule[class_name].append(lesson)

                except IndexError:
                    continue
        lesson_number += 1

    return all


if __name__ == '__main__':
    for key, val in get_all_raspisanie().items():
        print(key, dict(val))
