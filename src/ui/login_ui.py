import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QSpacerItem, QSizePolicy, QCheckBox, QGraphicsDropShadowEffect, QFrame
)
# [추가] 시그널을 위한 QtCore
from PySide6.QtCore import Qt, QTimer, QDateTime, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer


class LoginWindow(QWidget):
    # [추가] 로그인 성공 시 보낼 신호(signal) 정의
    login_successful = Signal()

    def __init__(self):
        super().__init__()
        self.initUI()
        self.initTimer()

    def initUI(self):
        # ... (이전과 동일한 UI 설정 코드)
        self.setWindowTitle("Login")
        self.setFixedSize(400, 800)
        self.setObjectName("mainWindow")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container_widget = QWidget()
        container_widget.setObjectName("container")
        container_widget.setFixedSize(360, 650)
        main_layout.addWidget(container_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(30, 30, 30, 30)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 50))
        container_widget.setGraphicsEffect(shadow)

        self.time_label = QLabel()
        self.time_label.setObjectName("timeLabel")

        top_layout = QVBoxLayout()
        top_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignLeft)
        top_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        bottom_layout = QVBoxLayout()
        bottom_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        main_layout.insertLayout(0, top_layout)
        main_layout.addLayout(bottom_layout)

        title_label = QLabel("로그인")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        signup_label = QLabel("계정이 없으신가요? <a href='#' style='color: #007BFF; text-decoration: none;'>회원가입 하기</a>")
        signup_label.setObjectName("subtleLabel")
        signup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signup_label.setTextFormat(Qt.TextFormat.RichText)
        signup_label.setOpenExternalLinks(False)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("이메일을 입력해주세요.")
        self.email_input.setObjectName("inputField")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("비밀번호를 입력해주세요.")
        self.password_input.setObjectName("inputField")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("toggleButton")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedSize(40, 40)
        self.update_eye_icon()

        self.remember_checkbox = QCheckBox("자동 로그인")
        self.remember_checkbox.setObjectName("subtleLabel")

        forgot_label = QLabel("<a href='#' style='color: #007BFF; text-decoration: none;'>비밀번호를 잊어버리셨나요?</a>")
        forgot_label.setObjectName("subtleLabel")
        forgot_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        forgot_label.setTextFormat(Qt.TextFormat.RichText)
        forgot_label.setOpenExternalLinks(False)

        login_button = QPushButton("로그인 하기")
        login_button.setObjectName("loginButton")

        or_label = QLabel("Or")
        or_label.setObjectName("subtleLabel")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        google_button = QPushButton("Google으로 로그인 하기")
        google_button.setObjectName("socialButton")
        google_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 48 48"><path fill="#FFC107" d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8c-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4C12.955 4 4 12.955 4 24s8.955 20 20 20s20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z"></path><path fill="#FF3D00" d="m6.306 14.691l6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4C16.318 4 9.656 8.337 6.306 14.691z"></path><path fill="#4CAF50" d="m24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238A11.91 11.91 0 0 1 24 36c-5.222 0-9.618-3.224-11.288-7.661l-6.522 5.025C9.505 39.556 16.227 44 24 44z"></path><path fill="#1976D2" d="m43.611 20.083H42V20H24v8h11.303c-.792 2.237-2.231 4.166-4.087 5.571l6.19 5.238C42.612 34.869 44 30.138 44 24c0-1.341-.138-2.65-.389-3.917z"></path></svg>"""
        google_button.setIcon(self.create_svg_icon(google_svg))

        facebook_button = QPushButton("Facebook으로 로그인 하기")
        facebook_button.setObjectName("socialButton")
        facebook_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="#1877F2" d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12c0 4.84 3.44 8.87 8 9.8V15H8v-3h2V9.5C10 7.57 11.57 6 13.5 6H16v3h-1.5c-1.11 0-1 .56-1 1v2h2.5l-.5 3H13v6.95c5.05-.95 9-5.16 9-9.95z"/></svg>"""
        facebook_button.setIcon(self.create_svg_icon(facebook_svg))

        container_layout.addWidget(title_label)
        container_layout.addWidget(signup_label)
        container_layout.addSpacing(30)
        container_layout.addWidget(QLabel("이메일"))
        container_layout.addWidget(self.email_input)
        container_layout.addSpacing(20)
        container_layout.addWidget(QLabel("비밀번호"))
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_button)
        container_layout.addLayout(password_layout)
        options_layout = QHBoxLayout()
        options_layout.addWidget(self.remember_checkbox)
        options_layout.addWidget(forgot_label)
        container_layout.addLayout(options_layout)
        container_layout.addSpacing(30)
        container_layout.addWidget(login_button)
        container_layout.addSpacing(20)

        # 수정 후 코드
        or_layout = QHBoxLayout()
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("color: #DDDDDD;")

        or_label = QLabel("Or")
        or_label.setObjectName("subtleLabel")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("color: #DDDDDD;")
        or_layout.addWidget(line1, 1)
        or_layout.addWidget(or_label)
        or_layout.addWidget(line2, 1)
        container_layout.addLayout(or_layout)

        container_layout.addSpacing(20)
        social_layout = QVBoxLayout()
        social_layout.addWidget(google_button)
        social_layout.addWidget(facebook_button)
        container_layout.addLayout(social_layout)
        container_layout.addStretch()

        # [수정] 시그널 연결
        self.toggle_button.clicked.connect(self.toggle_password_visibility)
        login_button.clicked.connect(self.login_attempt)
        google_button.clicked.connect(self.social_login_attempt)
        facebook_button.clicked.connect(self.social_login_attempt)

        self.setStyleSheet(self.get_stylesheet())

    # [수정] login_attempt 함수
    def login_attempt(self):
        email = self.email_input.text()
        password = self.password_input.text()
        print(f"로그인 시도 >> Email: {email}, Password: {password}")

        # 이메일과 비밀번호가 모두 입력되었는지 확인
        if email and password:
            self.login_successful.emit()  # 성공 신호 보내기
        else:
            print("이메일과 비밀번호를 모두 입력해주세요.")
            # 여기에 사용자에게 알림을 주는 팝업(QMessageBox)을 추가할 수 있습니다.

    # [추가] 소셜 로그인 함수
    def social_login_attempt(self):
        # 어떤 버튼이 눌렸는지 확인 (선택적)
        sender = self.sender()
        print(f"{sender.text()} 버튼 클릭됨 >> 로그인 성공 처리")
        self.login_successful.emit()  # 성공 신호 보내기

    # ... (나머지 함수는 이전과 동일)
    def create_svg_icon(self, svg_data):
        renderer = QSvgRenderer(svg_data.encode('utf-8'))
        pixmap = QPixmap(renderer.defaultSize())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)

    def update_eye_icon(self):
        eye_open_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#888888" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>"""
        eye_closed_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#888888" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>"""
        if self.toggle_button.isChecked():
            self.toggle_button.setIcon(self.create_svg_icon(eye_open_svg))
        else:
            self.toggle_button.setIcon(self.create_svg_icon(eye_closed_svg))
        self.toggle_button.setIconSize(QSize(24, 24))

    def initTimer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

    def update_time(self):
        current_time = QDateTime.currentDateTime().toString('hh:mm')
        self.time_label.setText(current_time)

    def toggle_password_visibility(self):
        if self.toggle_button.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.update_eye_icon()

    def get_stylesheet(self):
        return """
            QWidget#mainWindow { background-color: #EFEFEF; }
            QWidget#container {
                background-color: #FFFFFF;
                border: 1px solid #DDDDDD;
                border-radius: 15px;
            }
            QLabel { color: #000000; font-size: 14px; }
            QLabel#timeLabel { font-size: 16px; font-weight: bold; color: #555555; }
            QLabel#titleLabel { font-size: 40px; font-weight: bold; margin-bottom: 10px; }
            QLabel#subtleLabel, QCheckBox { color: #888888; }
            QLabel a { color: #3498db; text-decoration: none; }
            QLineEdit#inputField {
                background-color: #F0F0F0; color: #000000; border: 1px solid #DDDDDD;
                border-radius: 8px; padding: 12px; font-size: 16px;
            }
            QPushButton#toggleButton { background-color: transparent; border: none; }
            QPushButton#loginButton {
                background-color: #3498db; color: #FFFFFF; font-size: 18px;
                font-weight: bold; border: none; border-radius: 8px; padding: 15px;
            }
            QPushButton#loginButton:hover { background-color: #2980b9; }
            QPushButton#socialButton {
                background-color: #FFFFFF; color: #333333; font-size: 16px;
                border: 1px solid #DDDDDD; border-radius: 8px; 
                padding: 12px 20px; /* [수정] 위아래 여백을 줄여 공간 확보 */
                text-align: center;
            }
            QPushButton#socialButton:hover { background-color: #F5F5F5; }
            QCheckBox::indicator { width: 20px; height: 20px; }
        """