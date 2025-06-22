import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QScrollArea, QGridLayout, QStackedWidget
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QParallelAnimationGroup
from PyQt6.QtGui import QFont

from backend import update_data
from day_rasp import get_raspisanie_day
from all_rasp import get_all_raspisanie


class AnimatedStackedWidget(QStackedWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._animation_group = None

    def slide_to_widget(self, next_widget, direction="left"):
        current_widget = self.currentWidget()
        if current_widget == next_widget:
            return

        offset = self.frameRect().width()
        offset = offset if direction == "left" else -offset

        next_widget.setGeometry(self.rect().translated(offset, 0))
        next_widget.show()

        anim_old = QPropertyAnimation(current_widget, b"geometry")
        anim_old.setDuration(300)
        anim_old.setStartValue(current_widget.geometry())
        anim_old.setEndValue(current_widget.geometry().translated(-offset, 0))

        anim_new = QPropertyAnimation(next_widget, b"geometry")
        anim_new.setDuration(300)
        anim_new.setStartValue(next_widget.geometry())
        anim_new.setEndValue(self.rect())

        group = QParallelAnimationGroup()
        group.addAnimation(anim_old)
        group.addAnimation(anim_new)

        def on_finished():
            self.setCurrentWidget(next_widget)
            next_widget.setGeometry(self.rect())
            self._animation_group = None

        group.finished.connect(on_finished)

        self._animation_group = group
        group.start()


DAYS = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ВОСКРЕСЕНЬЕ"]


class ScheduleApp(QWidget):
    def __init__(self):
        super().__init__()

        update_data()
        self.TIME_LAST_CHECK = datetime.now()
        self.ALL_RASPISANIE = get_all_raspisanie()
        self.DAY_RAPISANIE = get_raspisanie_day()

        self.current_data = None
        self.setWindowTitle("Расписание")
        self.showFullScreen()

        self.stack = AnimatedStackedWidget()
        self.menu_page = QWidget()
        self.schedule_page = QWidget()

        self.create_menu_page()
        self.create_schedule_page()

        self.stack.addWidget(self.menu_page)
        self.stack.addWidget(self.schedule_page)

        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)

    def check_update_rasp(self):
        now = datetime.now()
        if (now - self.TIME_LAST_CHECK).seconds > 3600 or now.day > self.TIME_LAST_CHECK.day:
            self.TIME_LAST_CHECK = now
            update_data()
            self.ALL_RASPISANIE = get_all_raspisanie()
            self.DAY_RAPISANIE = get_raspisanie_day()
            self.create_menu_page()

    def create_menu_page(self):
        layout = QVBoxLayout()

        today_day_name = DAYS[datetime.today().weekday()] if DAYS[datetime.today().weekday()] in DAYS else \
            DAYS[(datetime.today().weekday() + 1) % 6]

        self.current_data = self.DAY_RAPISANIE.get(today_day_name, self.ALL_RASPISANIE[today_day_name])

        label = QLabel(today_day_name)
        label.setFont(QFont("Arial", 12))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        scroll = QScrollArea()
        container = QWidget()
        grid = QGridLayout()

        all_lessons = {}
        for cls, lessons in self.current_data.items():
            for lesson in lessons:
                key = (lesson['урок'], cls)
                all_lessons.setdefault(key, []).append(lesson)

        class_names = sorted(self.current_data.keys())

        for col, cls in enumerate(class_names):
            header = QLabel(cls)
            header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(header, 0, col + 1)

        for row in range(7):
            label = QLabel(f"{row + 1}")
            label.setFont(QFont("Arial", 12))
            grid.addWidget(label, row + 1, 0)

            for col, cls in enumerate(class_names):
                lessons = all_lessons.get((row + 1, cls), [])
                content = "\n---\n".join(f"{l['предмет']} ({l['кабинет']})\n{l['учитель']}" for l in lessons) if lessons else "—"
                cell = QLabel(content)
                cell.setStyleSheet("background-color: white; color: black; padding: 3px; border: 1px solid gray; border-radius: 5px; font-size: 8pt;")
                cell.setWordWrap(True)
                grid.addWidget(cell, row + 1, col + 1)

        container.setLayout(grid)
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)

        buttons_layout = QHBoxLayout()
        for cls in sorted(self.current_data):
            btn = QPushButton(f"{cls}")
            btn.setFont(QFont("Arial", 14))
            btn.clicked.connect(lambda _, c=cls: self.show_schedule(c))
            buttons_layout.addWidget(btn)

        exit_btn = QPushButton("Выход")
        exit_btn.setFont(QFont("Arial", 14))
        exit_btn.clicked.connect(QApplication.quit)

        layout.addWidget(scroll)
        layout.addLayout(buttons_layout)
        layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.menu_page.setLayout(layout)

    def create_schedule_page(self):
        self.schedule_layout = QVBoxLayout()
        self.schedule_grid = QGridLayout()
        self.schedule_grid.setSpacing(10)

        scroll = QScrollArea()
        container = QWidget()
        container.setLayout(self.schedule_grid)
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)

        self.class_label = QLabel("")
        self.class_label.setFont(QFont("Arial", 20))
        self.class_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("Назад")
        back_btn.setFont(QFont("Arial", 12))
        back_btn.setFixedSize(120, 40)
        back_btn.clicked.connect(self.back_to_menu)

        self.schedule_layout.addWidget(self.class_label)
        self.schedule_layout.addWidget(scroll)
        self.schedule_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.schedule_page.setLayout(self.schedule_layout)

    def show_schedule(self, class_name):
        self.class_label.setText(f"Расписание для {class_name}")

        # Очистка сетки
        while self.schedule_grid.count():
            item = self.schedule_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for col, day in enumerate(DAYS[:-1]):
            header = QLabel(day)
            header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.schedule_grid.addWidget(header, 0, col + 1)

            if day not in self.ALL_RASPISANIE:
                continue
            lessons = self.ALL_RASPISANIE[day].get(class_name, [])

            for i in range(1, 8):
                label = QLabel(f"{i}:")
                label.setFont(QFont("Arial", 12))
                self.schedule_grid.addWidget(label, i, 0)

                cell_texts = [f"{l['предмет']} ({l['кабинет']})\n{l['учитель']}" for l in lessons if l['урок'] == i]
                content = "\n---\n".join(cell_texts) if cell_texts else "—"

                text_label = QLabel(content)
                text_label.setStyleSheet("background-color: white; color: black; padding: 8px; border: 1px solid #999; border-radius: 6px;")
                text_label.setWordWrap(True)
                self.schedule_grid.addWidget(text_label, i, col + 1)

        self.stack.slide_to_widget(self.schedule_page, direction="left")

    def back_to_menu(self):
        self.check_update_rasp()
        self.stack.slide_to_widget(self.menu_page, direction="right")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScheduleApp()
    window.show()
    sys.exit(app.exec())
