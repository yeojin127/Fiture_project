import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt


class ResultPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("resultPage")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 상단 뒤로가기 버튼 ---
        top_bar = QWidget()
        top_bar_layout = QHBoxLayout(top_bar)
        self.back_button = QPushButton("← Enter Condition")
        self.back_button.setObjectName("backButton")
        top_bar_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # --- 스크롤 가능한 콘텐츠 영역 ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scrollArea")

        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 5, 25, 25)
        content_layout.setSpacing(10)

        # 1. 오늘의 컨디션 예측 칸
        title_label = QLabel("오늘의 컨디션 예측")
        title_label.setObjectName("resultTitle")
        subtitle_label = QLabel("Grade your condition")
        subtitle_label.setObjectName("resultSubtitle")

        result_box = QFrame()
        result_box.setObjectName("resultBox")
        result_box_layout = QVBoxLayout(result_box)
        result_box_layout.setSpacing(10)

        grade_title_label = QLabel("컨디션 등급")
        grade_title_label.setObjectName("boxTitle")

        self.grade_label = QLabel()
        self.grade_label.setObjectName("gradeLabel")
        initial_grade_text = f"<span style='color:#3498db;'>?</span><span style='color:#222222;'> 등급</span>"
        self.grade_label.setText(initial_grade_text)

        self.summary_label = QLabel("오늘의 데이터를 입력하고 결과를 확인해보세요.")
        self.summary_label.setObjectName("summaryLabel")
        self.summary_label.setWordWrap(True)

        result_box_layout.addWidget(grade_title_label)
        result_box_layout.addWidget(self.grade_label)
        result_box_layout.addWidget(self.summary_label)

        content_layout.addWidget(title_label)
        content_layout.addWidget(subtitle_label)
        content_layout.addWidget(result_box)

        # --- [TOP3 섹션] ---
        top3_title = QLabel("컨디션에 영향을 준 요인 TOP3")
        top3_title.setObjectName("resultTitle")
        content_layout.addWidget(top3_title)

        self.top3_box = QFrame()
        self.top3_box.setObjectName("resultBox")
        self.top3_container = QVBoxLayout(self.top3_box)
        content_layout.addWidget(self.top3_box)

        self.top3_items = []
        for i in range(3):
            item_widget = QWidget()
            item_widget.setObjectName("top3Item")
            item_widget.setStyleSheet(f"""
                QWidget#top3Item {{
                    background-color: #FFFFFF;
                    border: 1px solid #EAEAEA;
                    border-radius: 10px;
                    padding: 15px;
                }}
            """)

            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(15, 0, 15, 0)

            rank_label = QLabel(str(i + 1))
            rank_label.setStyleSheet(f"""
                font-size: 16px;
                font-weight: bold;
                color: #FFFFFF;
                background-color: #3498db;
                border-radius: 15px;
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
                qproperty-alignment: 'AlignCenter';
            """)

            reason_label = QLabel("...")
            reason_label.setObjectName("top3Reason")
            reason_label.setStyleSheet("font-size: 16px; font-weight: 500;")

            item_layout.addWidget(rank_label)
            item_layout.addSpacing(15)
            item_layout.addWidget(reason_label)
            item_layout.addStretch()

            self.top3_container.addWidget(item_widget)
            self.top3_items.append(reason_label)

        # --- [경고 섹션] (순서 변경) ---
        warning_title = QLabel("환경 알림")
        warning_title.setObjectName("resultTitle")
        content_layout.addWidget(warning_title)

        self.warning_box = QFrame()
        self.warning_box.setObjectName("resultBox")
        self.warning_container = QVBoxLayout(self.warning_box)
        content_layout.addWidget(self.warning_box)

        self.warning_items = []

        # --- [오늘의 조언 섹션] (순서 변경) ---
        advice_title = QLabel("오늘의 조언")
        advice_title.setObjectName("resultTitle")
        content_layout.addWidget(advice_title)

        self.advice_container = QVBoxLayout()
        self.advice_container.setSpacing(15)
        content_layout.addLayout(self.advice_container)

        self.advice_widgets = []

        # --- [식단 추천 섹션] (순서 변경) ---
        food_title = QLabel("오늘의 식단 추천")
        food_title.setObjectName("resultTitle")
        content_layout.addWidget(food_title)

        food_box = QFrame()
        food_box.setObjectName("resultBox")
        food_box_layout = QVBoxLayout(food_box)
        food_box_layout.setSpacing(10)

        self.food_morning_layout, self.food_morning_label = self.create_food_item("아침")
        self.food_snack_layout, self.food_snack_label = self.create_food_item("간식")
        self.food_dinner_layout, self.food_dinner_label = self.create_food_item("저녁")

        food_box_layout.addLayout(self.food_morning_layout)
        food_box_layout.addLayout(self.food_snack_layout)
        food_box_layout.addLayout(self.food_dinner_layout)

        content_layout.addWidget(food_box)

        content_layout.addStretch()

        main_layout.addWidget(top_bar)
        main_layout.addWidget(scroll_area, 1)

    def create_food_item(self, meal_name):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(meal_name)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #555555;")

        content_label = QLabel("...")
        content_label.setStyleSheet("font-size: 14px; color: #222222; margin-left: 10px;")

        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(content_label)

        return layout, content_label

    def check_ui_warnings(self, raw_data):
        ui_warnings = []
        try:
            pm = float(raw_data.get("pm10", "0"))
            temp = float(raw_data.get("temp", "0"))
            humid = float(raw_data.get("humidity", "0"))

            if pm > 80:
                ui_warnings.append("미세먼지 높음: 실내 운동, 마스크 착용")
            if temp > 30:
                ui_warnings.append("더위 주의: 한낮 외출 줄이고 수분 보충")
            if humid < 30:
                ui_warnings.append("건조 주의: 가습 40~60% 유지")
        except (ValueError, TypeError):
            pass
        return ui_warnings

    def update_results(self, card_result, raw_data):
        grade_num = card_result['title'].split('/')[0].split(' ')[-1]
        summary_text = card_result['summary']

        grade_text = f"<span style='color:#3498db;'>{grade_num}</span><span style='color:#222222;'> 등급</span>"
        self.grade_label.setText(grade_text)
        self.summary_label.setText(summary_text)

        # TOP3 업데이트 로직
        reasons = card_result.get('reasons', [])
        for i in range(3):
            if i < len(reasons):
                self.top3_items[i].setText(reasons[i])
            else:
                self.top3_items[i].setText("없음")

        # 식단 추천 업데이트 로직
        food_data = card_result.get('food', {})
        self.food_morning_label.setText(food_data.get('morning', '정보 없음'))
        self.food_snack_label.setText(food_data.get('snack', '정보 없음'))
        self.food_dinner_label.setText(food_data.get('dinner', '정보 없음'))

        # 경고 업데이트 로직 (ui_warnings 사용)
        for widget in self.warning_items:
            self.warning_container.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()
        self.warning_items.clear()

        ui_warnings_data = self.check_ui_warnings(raw_data)
        if ui_warnings_data:
            for warning_text in ui_warnings_data:
                warning_label = QLabel(f"⚠️ {warning_text}")
                warning_label.setWordWrap(True)
                warning_label.setStyleSheet("font-size: 14px; color: #e74c3c; font-weight: bold;")
                self.warning_container.addWidget(warning_label)
                self.warning_items.append(warning_label)
        else:
            no_warning_label = QLabel("경고 사항이 없습니다. 좋은 컨디션을 유지하고 있습니다!")
            no_warning_label.setWordWrap(True)
            no_warning_label.setStyleSheet("font-size: 14px; color: #2ecc71; font-weight: bold;")
            self.warning_container.addWidget(no_warning_label)
            self.warning_items.append(no_warning_label)

        # 오늘의 조언 업데이트 로직
        for widget in self.advice_widgets:
            self.advice_container.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()
        self.advice_widgets.clear()

        actions_data = card_result.get('actions', [])
        if actions_data:
            for advice_text in actions_data:
                advice_label = QLabel(f"• {advice_text}")
                advice_label.setWordWrap(True)
                advice_label.setStyleSheet("font-size: 14px; color: #555555; margin-left: 10px;")
                self.advice_container.addWidget(advice_label)
                self.advice_widgets.append(advice_label)
        else:
            no_advice_label = QLabel("제공된 조언이 없습니다.")
            no_advice_label.setWordWrap(True)
            no_advice_label.setStyleSheet("font-size: 14px; color: #AAAAAA;")
            self.advice_container.addWidget(no_advice_label)
            self.advice_widgets.append(no_advice_label)