import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit,
    QScrollArea
)
from PySide6.QtCore import Qt, Signal


class TodayInputPage(QWidget):
    data_submitted = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("todayPage")
        self.setWindowTitle("Enter Today's Condition")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scrollArea")

        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(25)

        self.sleep_input, layout1 = self.create_input_field("Yesterday's Sleep Time", "hh:mm:ss",
                                                            "Enter the time you slept yesterday")
        self.activity_input, layout2 = self.create_input_field("Yesterday's Activity Time", "hh:mm:ss",
                                                               "Enter the duration of your activity yesterday")
        self.phone_input, layout3 = self.create_input_field("Yesterday's Phone Usage Time", "hh:mm:ss",
                                                            "Enter the amount of time spent on your phone")
        self.caffeine_input, layout4 = self.create_input_field("Yesterday's Caffeine Intake", "Number of coffee cups",
                                                               "How many cups of coffee did you drink?")
        self.mood_input, layout5 = self.create_input_field("Today's Morning Mood Score", "1 - 100",
                                                           "Rate your mood from 1 to 100")
        self.temp_input, layout6 = self.create_input_field("Today's Temperature(°C)", "Temperature in °C",
                                                           "What is the current temperature?")
        self.humidity_input, layout7 = self.create_input_field("Today's Humidity(%)", "Humidity in %",
                                                               "What is the current humidity level?")
        self.pm10_input, layout8 = self.create_input_field("Today's Air Quality(Fine Dust Level)", "Fine dust level",
                                                           "What is the current air quality level?")

        for layout in [layout1, layout2, layout3, layout4, layout5, layout6, layout7, layout8]:
            content_layout.addLayout(layout)

        content_layout.addStretch()

        save_button = QPushButton("저장하고 예측하기")
        save_button.setObjectName("saveButton")
        save_button.clicked.connect(self.on_save_clicked)

        # [핵심 수정] 스크롤 영역이 남는 공간을 모두 차지하고, 버튼은 하단에 위치하도록 설정
        main_layout.addWidget(scroll_area, 1)
        main_layout.addWidget(save_button)

    def create_input_field(self, title_text, placeholder_text, description_text):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        title_label = QLabel(title_text)
        title_label.setObjectName("inputTitle")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        line_edit.setObjectName("inputField")
        description_label = QLabel(description_text)
        description_label.setObjectName("inputDescription")
        layout.addWidget(title_label)
        layout.addWidget(line_edit)
        layout.addWidget(description_label)
        return line_edit, layout

    def on_save_clicked(self):
        raw_data = {
            "sleep_time": self.sleep_input.text(), "activity_time": self.activity_input.text(),
            "phone_time": self.phone_input.text(), "caffeine": self.caffeine_input.text(),
            "mood_score": self.mood_input.text(), "temp": self.temp_input.text(),
            "humidity": self.humidity_input.text(), "pm10": self.pm10_input.text()
        }
        self.data_submitted.emit(raw_data)