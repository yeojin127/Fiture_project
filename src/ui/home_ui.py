import sys
import math
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QSize, QDateTime
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QPainterPath, QLinearGradient


class MonthlyOverviewGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        padding_top_bottom = 20
        padding_sides = 25
        graph_width = width - (padding_sides * 2)
        graph_height = height - (padding_top_bottom * 2)

        data_points = [0.95, 0.65, 0.4, 0.7, 0.5, 0.8, 0.6]
        month_labels = ["2월", "3월", "4월", "5월", "6월", "7월", "8월"]
        bar_count = len(data_points)
        bar_width = graph_width / (bar_count * 2)

        pen = QPen(QColor("#EAEAEA"), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        for i in range(1, 5):
            y = padding_top_bottom + (i * graph_height / 4)
            painter.drawLine(padding_sides, int(y), width - padding_sides, int(y))

        for i, point in enumerate(data_points):
            x = padding_sides + (i * 2 * bar_width) + (bar_width / 2)
            bar_height = point * graph_height
            y = padding_top_bottom + (1 - point) * graph_height

            if point >= 0.75:
                base_color = QColor("#005cbf")
            elif point >= 0.5:
                base_color = QColor("#007BFF")
            elif point >= 0.25:
                base_color = QColor("#58a6ff")
            else:
                base_color = QColor("#a8cfff")

            gradient = QLinearGradient(x, y, x, y + bar_height)
            gradient.setColorAt(0, base_color)
            lighter_color = base_color.lighter(150)
            gradient.setColorAt(1, lighter_color)

            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_height), 5, 5)

            painter.setPen(QColor("#AAAAAA"))
            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)
            text_x = int(x + bar_width / 2 - painter.fontMetrics().horizontalAdvance(month_labels[i]) / 2)
            text_y = height - 5
            painter.drawText(text_x, text_y, month_labels[i])


class WeeklyTrendGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        padding = 20
        graph_width = width - 2 * padding
        graph_height = height - (padding * 2)

        pen = QPen(QColor("#EAEAEA"), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        for i in range(1, 5):
            y = padding + (i * graph_height / 4)
            painter.drawLine(padding, int(y), width - padding, int(y))

        data_points = []
        for i in range(20):
            sine_value = (math.sin(i * 0.5) + 1) / 2
            noise = (i % 3) * 0.1 - 0.1
            point = max(0, min(1, sine_value + noise))
            data_points.append(point)

        path = QPainterPath()
        start_point_x = padding
        start_point_y = padding + (1 - data_points[0]) * graph_height
        path.moveTo(start_point_x, start_point_y)

        for i in range(len(data_points) - 1):
            x1 = padding + (i / (len(data_points) - 1)) * graph_width
            y1 = padding + (1 - data_points[i]) * graph_height
            x2 = padding + ((i + 1) / (len(data_points) - 1)) * graph_width
            y2 = padding + (1 - data_points[i + 1]) * graph_height
            cx1 = x1 + graph_width / (len(data_points) - 1) / 2
            cy1 = y1
            cx2 = x2 - graph_width / (len(data_points) - 1) / 2
            cy2 = y2
            path.cubicTo(cx1, cy1, cx2, cy2, x2, y2)

        line_path = QPainterPath(path)

        path.lineTo(width - padding, height - padding)
        path.lineTo(padding, height - padding)
        path.closeSubpath()

        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(52, 152, 219, 150))
        gradient.setColorAt(1, QColor(52, 152, 219, 20))
        painter.fillPath(path, gradient)

        pen = QPen(QColor("#333333"), 2.5)
        painter.setPen(pen)
        painter.drawPath(line_path)

        painter.setPen(QColor("#AAAAAA"))
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(width - padding - 30, height - 5, "Days")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    # [추가] 예측 결과를 받아 UI를 업데이트하는 함수
    def update_today_card(self, card_result):
        # 1. 오늘 날짜를 "YYYY.MM.DD" 형식으로 가져옴
        today_date = QDateTime.currentDateTime().toString("yyyy.MM.dd")

        # 2. card_result에서 필요한 정보 추출
        # title에서 등급 숫자만 추출
        grade = card_result['title'].split('/')[0].split(' ')[-1]
        summary = card_result['summary']
        # reasons가 비어있으면 기본 메시지, 있으면 목록을 문자열로 변환
        reasons = ", ".join(card_result['reasons']) if card_result['reasons'] else "특별한 저하 요인이 없습니다."

        # 3. 저장해둔 라벨들의 텍스트를 새로운 정보로 변경
        self.today_date_label.setText(today_date)
        self.today_desc_label.setText(reasons)
        grade_text = f"컨디션 등급 : <span style='color:#3498db; font-weight:bold;'>{grade}</span> 등급"
        self.today_grade_label.setText(grade_text)

        # TODO: card_result의 다른 정보들(actions, food 등)을 표시할 위젯이 있다면
        #       이곳에서 함께 업데이트할 수 있습니다.
        print(f"{today_date}의 데이터로 홈 화면이 업데이트되었습니다.")

    def initUI(self):
        self.setWindowTitle("Fiture")
        self.setObjectName("mainWindow")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(20, 10, 20, 10)

        title_label = QLabel("😴 Fiture")
        title_label.setObjectName("mainTitle")
        title_bar_layout.addWidget(title_label)
        main_layout.addWidget(title_bar)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        main_layout.addWidget(content_widget, 1)

        self.home_tabs = QWidget()
        home_tabs_layout = QHBoxLayout(self.home_tabs)
        home_tabs_layout.setContentsMargins(20, 0, 20, 15)
        home_tabs_layout.setSpacing(15)

        self.report_btn = QPushButton("📄\nCondition\nReport")
        self.more_btn = QPushButton("🔍\nMore")
        self.rank_btn = QPushButton("📊\nRank")

        self.report_btn.setObjectName("homeTabButton")
        self.more_btn.setObjectName("homeTabButton")
        self.rank_btn.setObjectName("homeTabButton")

        self.report_btn.setCheckable(True)
        self.more_btn.setCheckable(True)
        self.rank_btn.setCheckable(True)

        home_tabs_layout.addWidget(self.report_btn)
        home_tabs_layout.addWidget(self.more_btn)
        home_tabs_layout.addWidget(self.rank_btn)
        content_layout.addWidget(self.home_tabs)

        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        self.report_page = self.create_report_page()
        self.more_page = QLabel("More Page Content")
        self.rank_page = QLabel("Rank Page Content")

        self.more_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rank_page.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stacked_widget.addWidget(self.report_page)
        self.stacked_widget.addWidget(self.more_page)
        self.stacked_widget.addWidget(self.rank_page)

        self.report_btn.clicked.connect(lambda: self.switch_page(0))
        self.more_btn.clicked.connect(lambda: self.switch_page(1))
        self.rank_btn.clicked.connect(lambda: self.switch_page(2))

        self.switch_page(0)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.report_btn.setChecked(index == 0)
        self.more_btn.setChecked(index == 1)
        self.rank_btn.setChecked(index == 2)

    def create_report_page(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scrollArea")
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(25)

        layout.addWidget(self.create_section_title("최근 3일"))

        # --- [수정] history_data를 self 변수로 만들고, 첫 번째 아이템을 업데이트 가능하도록 변경 ---
        # 1. 업데이트할 라벨들을 self 변수에 저장
        main_layout, self.today_date_label, self.today_desc_label, self.today_grade_label = self.create_history_item(
            "...", "오늘의 데이터를 입력해주세요.", "?")
        layout.addLayout(main_layout)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setObjectName("separatorLine")
        layout.addWidget(line1)

        history_data = [
            ("2025.08.25", "수면 시간, 습도, 카페인 섭취량", "2"),
            ("2025.08.24", "카페인 섭취량, 기온, 아침 기분 점수", "1")
        ]
        for date, desc, grade in history_data:
            item_layout, _, _, _ = self.create_history_item(date, desc, grade)
            layout.addLayout(item_layout)
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setObjectName("separatorLine")
            layout.addWidget(line)

        weekly_card = QWidget()
        weekly_card.setObjectName("cardWidget")
        weekly_card_layout = QVBoxLayout(weekly_card)
        weekly_card_layout.addLayout(self.create_section_header("최근 일주일", "Condition Grade"))
        weekly_card_layout.addWidget(WeeklyTrendGraph())
        layout.addWidget(weekly_card)

        monthly_card = QWidget()
        monthly_card.setObjectName("cardWidget")
        monthly_card_layout = QVBoxLayout(monthly_card)
        monthly_card_layout.addLayout(self.create_section_header("달별 분석", "Condition Score"))
        monthly_card_layout.addWidget(MonthlyOverviewGraph())
        layout.addWidget(monthly_card)

        layout.addStretch()
        return scroll_area

    def create_section_title(self, text):
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        return label

    def create_section_header(self, title, subtitle):
        layout = QVBoxLayout()
        layout.setSpacing(2)
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("sectionSubtitle")
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.setContentsMargins(15, 10, 15, 5)
        return layout

    def create_history_item(self, date, description, grade):
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)
        date_label = QLabel(date)
        date_label.setObjectName("historyDate")
        desc_label = QLabel(description)
        desc_label.setObjectName("historyDesc")
        left_layout.addWidget(date_label)
        left_layout.addWidget(desc_label)

        grade_text = f"컨디션 등급 : <span style='color:#3498db; font-weight:bold;'>{grade}</span> 등급"
        grade_label = QLabel(grade_text)
        grade_label.setObjectName("historyGrade")

        main_layout.addLayout(left_layout, 1)
        main_layout.addWidget(grade_label)

        return main_layout, date_label, desc_label, grade_label