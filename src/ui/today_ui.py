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

        self.sleep_input, layout1 = self.create_input_field("몇 시간 정도 주무셨나요?", "hh:mm:ss",
                                                            "시간, 분, 초를 정확하게 입력해주세요.")
        self.activity_input, layout2 = self.create_input_field("어제 활동(운동, 외출 등)은 얼마나 하셨나요?", "hh:mm:ss",
                                                               "시간, 분, 초를 정확하게 입력해주세요.")
        self.phone_input, layout3 = self.create_input_field("어제 핸드폰은 얼마나 사용하셨나요?", "hh:mm:ss",
                                                            "시간, 분, 초를 정확하게 입력해주세요.")
        self.caffeine_input, layout4 = self.create_input_field("어제 커피, 에너지 음료를 몇 잔 드셨나요?", "Number of coffee cups",
                                                               "카페인이 함류된 음료의 잔 수를 입력해주세요.")
        self.mood_input, layout5 = self.create_input_field("오늘의 아침 컨디션은 몇 점인가요?", "1 - 100",
                                                           "1부터 100까지의 숫자를 입력해주세요.")
        self.temp_input, layout6 = self.create_input_field("오늘의 예상 평균 기온은 몇 도인가요?", "Temperature in °C",
                                                           "온도(°C)를 숫자로 입력해주세요.")
        self.humidity_input, layout7 = self.create_input_field("오늘의 습도는 몇 %인가요?", "Humidity in %",
                                                               "습도(%)를 숫자로 입력해주세요.")
        self.pm10_input, layout8 = self.create_input_field("오늘의 미세먼지(PM10) 수치는 얼마인가요?", "Fine dust level",
                                                           "미세먼지(PM10)를 숫자로 입력해주세요.")

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