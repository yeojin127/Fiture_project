import sys
import os

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

import numpy as np
import pandas as pd
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QMessageBox

from login_ui import LoginWindow
from home_ui import MainWindow
from today_ui import TodayInputPage
from result_ui import ResultPage
from coach.pipeline import CoachPipeline


class ApplicationWindow(QWidget):
    def __init__(self, pipeline: CoachPipeline, feature_names: list):
        super().__init__()
        self.pipeline = pipeline
        self.feature_names = feature_names

        self.setWindowTitle("Fiture")
        self.setFixedSize(400, 800)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()

        self.home_page = MainWindow()
        self.today_page = TodayInputPage()
        self.result_page = ResultPage()

        # 스택 위젯에 페이지 추가 (Home: 0, Today 입력: 1, 결과: 2)
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.today_page)
        self.stacked_widget.addWidget(self.result_page)

        # 신호 연결
        self.today_page.data_submitted.connect(self.handle_prediction)
        self.result_page.back_button.clicked.connect(lambda: self.switch_page(1))

        # 하단 내비게이션 바 생성
        nav_bar = QWidget()
        nav_bar.setObjectName("navBar")
        nav_bar_layout = QHBoxLayout(nav_bar)
        nav_bar_layout.setContentsMargins(10, 5, 10, 5)

        self.home_btn = QPushButton("🏠\nHome")
        self.today_btn = QPushButton("💡\nToday")
        self.challenge_btn = QPushButton("🎯\nChallenge")
        self.community_btn = QPushButton("👥\nCommunity")

        self.nav_buttons = [self.home_btn, self.today_btn, self.challenge_btn, self.community_btn]
        for btn in self.nav_buttons:
            btn.setCheckable(True)
            nav_bar_layout.addWidget(btn)

        main_layout.addWidget(self.stacked_widget, 1)
        main_layout.addWidget(nav_bar)

        self.home_btn.clicked.connect(lambda: self.switch_page(0))
        self.today_btn.clicked.connect(lambda: self.switch_page(1))
        self.challenge_btn.clicked.connect(lambda: self.switch_page(0))
        self.community_btn.clicked.connect(lambda: self.switch_page(0))

        self.setStyleSheet(self.get_stylesheet())
        self.switch_page(0)

    def handle_prediction(self, raw_data: dict):
        try:
            print("Today's input data:", raw_data)
            def time_str_to_hours(time_str):
                parts = time_str.split(':')
                h, m, s = 0, 0, 0
                if len(parts) >= 2: h, m = map(int, parts[:2])
                if len(parts) == 3: s = int(parts[2])
                return h + (m / 60) + (s / 3600)

            sleep_time = time_str_to_hours(raw_data["sleep_time"])
            activity_time = time_str_to_hours(raw_data["activity_time"])
            phone_time = time_str_to_hours(raw_data["phone_time"])
            caffeine = int(raw_data["caffeine"])
            mood_score = int(raw_data["mood_score"])
            temp = float(raw_data["temp"])
            humidity = float(raw_data["humidity"])
            pm10 = float(raw_data["pm10"])
            input_df = pd.DataFrame(
                [{"SleepTime": sleep_time, "ActivityTime": activity_time, "PhoneTime": phone_time, "Caffeine": caffeine,
                  "MoodScore": mood_score, "Temp": temp, "Humidity": humidity, "PM10": pm10}])
            input_processed = pd.get_dummies(input_df).reindex(columns=self.feature_names, fill_value=0)
            X_row = input_processed.values.astype(np.float32)
            card_result = self.pipeline.predict_card(X_row)
            print("Generated card_result:", card_result)

            print("받아온 card_result 내용:", card_result)

            # --- [수정 시작] 한국어 변환 로직 추가 ---
            reason_map = {
                'sleep_low': '수면 시간',
                'activity_low': '전날 활동 시간',
                'phone_high': '휴대폰 사용 시간',
                'caffeine_high': '카페인 섭취량',
                'mood_low': '기분 점수',
                'temp_high': '기온',
                'humid_high': '습도',
                'pm_high': '미세먼지'
            }
            english_reasons = card_result.get('reasons', [])
            korean_reasons = [reason_map.get(reason, reason) for reason in english_reasons]
            card_result['reasons'] = korean_reasons
            # --- [수정 끝] ---

            self.home_page.update_today_card(card_result)

            self.result_page.update_results(card_result, raw_data)
            self.switch_page(2)

        except (ValueError, KeyError, IndexError) as e:
            QMessageBox.warning(self, "Input Error", "입력값을 확인해주세요. 시간은 hh:mm:ss 형식, 나머지는 숫자로 입력해야 합니다.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"예측 중 오류가 발생했습니다:\n{e}")

    def switch_page(self, index):
        if index == 2:
            self.stacked_widget.setCurrentIndex(2)
            self.today_btn.setChecked(True)
            self.home_btn.setChecked(False)
            self.challenge_btn.setChecked(False)
            self.community_btn.setChecked(False)
        else:
            self.stacked_widget.setCurrentIndex(index)
            self.home_btn.setChecked(index == 0)
            self.today_btn.setChecked(index == 1)
            self.challenge_btn.setChecked(index == 0 and self.sender() == self.challenge_btn)
            self.community_btn.setChecked(index == 0 and self.sender() == self.community_btn)

    def get_stylesheet(self):
        return """
            /* ==================================
             * 내비게이션 바 & 공통 스타일
             * ================================== */
            QWidget#navBar { background-color: #3498db; }
            QPushButton {
                border: none; font-size: 12px; padding: 5px;
                color: #FFFFFF; background-color: transparent;
            }
            QPushButton:checked {
                color: #3498db;
                background-color: #FFFFFF;
                border-radius: 10px;
            }
            /* ==================================
             * Home 화면 (home_ui.py) 스타일
             * ================================== */
            QWidget#mainWindow, QScrollArea, QScrollArea > QWidget > QWidget {
                background-color: #FFFFFF;
            }
            QWidget#titleBar { background-color: #FFFFFF; border-bottom: 2px solid #3498db; }
            QLabel#mainTitle { color: #3498db; font-size: 24px; font-weight: 900; }
            QPushButton#homeTabButton {
                background-color: transparent; border: none;
                border-top: 3px solid transparent;
                font-size: 14px; font-weight: bold;
                padding: 5px 0px; color: #888888;
            }
            QPushButton#homeTabButton:checked { color: #3498db; border-top: 3px solid #3498db; }
            QScrollArea { border: none; }
            QLabel#sectionTitle { font-size: 18px; font-weight: 800; color: #222222; }
            QLabel#sectionSubtitle { font-size: 13px; color: #AAAAAA; }
            QLabel#historyDate { font-size: 16px; color: #333333; font-weight: 600; }
            QLabel#historyDesc { font-size: 12px; color: #666666; }
            QLabel#historyGrade { font-size: 14px; color: #333333; font-weight: 600; }
            QFrame#separatorLine { border: 1px solid #F0F0F0; }
            QWidget#cardWidget {
                background-color: #FFFFFF;
                border: 1px solid #EAEAEA;
                border-radius: 10px;
            }

            /* ==================================
             * Today 입력 화면 (today_ui.py) 스타일
             * ================================== */
            QWidget#todayPage {
                background-color: #FFFFFF;
                border: none;
            }
            QLabel#inputTitle {
                font-size: 18px;
                font-weight: bold;
                color: #222222;
            }
            QLineEdit#inputField {
                background-color: #F7F7F7;
                border: 1px solid #EAEAEA;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
            }
            QLabel#inputDescription {
                font-size: 13px;
                color: #AAAAAA;
                padding-left: 5px;
            }
            QPushButton#saveButton {
                background-color: #3498db;
                color: #FFFFFF;
                font-size: 18px;
                font-weight: bold;
                border: none;
                padding: 15px;
                margin: 0px;
                min-height: 50px;
            }
            QPushButton#saveButton:hover {
                background-color: #2980b9;
            }

            /* ==================================
             * Result 화면 (result_ui.py) 스타일
             * ================================== */
            QWidget#resultPage {
                background-color: #FFFFFF;
            }
            QPushButton#backButton {
                background-color: transparent;
                border: none;
                color: #3498db;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton#backButton:hover {
                color: #2980b9;
            }
            QLabel#resultTitle {
                font-size: 22px;
                font-weight: 900;
                color: #222222;
            }
            QLabel#resultSubtitle {
                font-size: 14px;
                color: #AAAAAA;
            }
            QFrame#resultBox {
                background-color: #FFFFFF;
                border: 1px solid #EAEAEA;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel#boxTitle {
                font-size: 14px;
                color: #555555;
                font-weight: bold;
            }
            QLabel#gradeLabel {
                font-size: 32px;
                font-weight: 900;
                padding-top: 5px;
                padding-bottom: 5px;
            }
            QLabel#summaryLabel {
                font-size: 13px;
                color: #3498db;
            }
        """

# MainApplication 클래스와 if __name__ == '__main__' 부분은 이전과 동일
class MainApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = LoginWindow()

        # --- [핵심] 백엔드 파이프라인 객체 생성 ---
        # 1. 프로젝트 최상위 경로 계산
        # 현재 파일(main_ui.py) 위치: .../src/ui/
        # 최상위 경로(PROJECT_ROOT): .../Fiture_project/
        PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        # 2. 모델 및 데이터 경로 설정
        model_path = os.path.join(PROJECT_ROOT, "data", "models", "model_lgbm.pkl")
        train_data_path = os.path.join(PROJECT_ROOT, "data", "processed", "train.csv")

        # 3. SHAP 분석을 위한 배경 데이터 준비
        df_train = pd.read_csv(train_data_path)
        X_train = pd.get_dummies(df_train.drop("ConditionLabel", axis=1))

        background_X = X_train.head(100).values.astype(np.float32)

        self.feature_names = X_train.columns.tolist()

        # 4. 파이프라인 객체 생성
        self.pipeline = CoachPipeline(
            model_path=model_path,
            background_X=background_X,
            feature_names=self.feature_names
        )

        print("="*50)
        print("로드된 모델 객체의 정보:")
        print(self.pipeline.model)
        print("="*50)

        self.app_window = ApplicationWindow(self.pipeline, self.feature_names)

        self.login_window.login_successful.connect(self.show_main_window)

    def run(self):
        self.login_window.show()
        sys.exit(self.app.exec())

    def show_main_window(self):
        self.login_window.close()
        self.app_window.show()


if __name__ == '__main__':
    main_app = MainApplication()
    main_app.run()