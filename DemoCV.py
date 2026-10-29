import base64
import os
import sys
from pathlib import Path

import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4.1-mini"


def load_env_file():
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


class AnalysisThread(QThread):
    finished_analysis = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, image_path, api_key):
        super().__init__()
        self.image_path = image_path
        self.api_key = api_key

    def run(self):
        try:
            image_data = Path(self.image_path).read_bytes()
            encoded_image = base64.b64encode(image_data).decode("ascii")
            mime_type = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }.get(Path(self.image_path).suffix.lower(), "application/octet-stream")

            response = requests.post(
                OPENAI_API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": DEFAULT_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 이미지 분석 전문가입니다. 한국어로 상세하고 정확하게 설명하세요.",
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "이 사진을 분석해서 다음 내용을 한국어로 알려주세요: 주요 대상, 장소 또는 상황, 색상과 구도, 화면에 보이는 글자 또는 표시, 그리고 전체적인 해석.",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"},
                                },
                            ],
                        },
                    ],
                    "max_tokens": 1000,
                },
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()
            analysis = result["choices"][0]["message"]["content"]
            self.finished_analysis.emit(analysis)
        except requests.RequestException as error:
            detail = ""
            if getattr(error, "response", None) is not None:
                try:
                    detail = error.response.json().get("error", {}).get("message", "")
                except ValueError:
                    detail = error.response.text
            self.failed.emit(detail or str(error))
        except (KeyError, IndexError, OSError, ValueError) as error:
            self.failed.emit(str(error))


class Form(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_path = None
        self.analysis_thread = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Vision AI Studio")
        self.resize(1100, 720)

        central_widget = QWidget()
        central_widget.setObjectName("central")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        title = QLabel("VISION AI STUDIO")
        title.setObjectName("title")
        subtitle = QLabel("AI 기반 이미지 분석 및 시각 콘텐츠 인사이트")
        subtitle.setObjectName("subtitle")
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 12, 16, 12)
        top_layout.setSpacing(12)

        self.select_button = QPushButton("  사진 업로드")
        self.select_button.setObjectName("primaryButton")
        self.analyze_button = QPushButton("  AI 분석 시작")
        self.analyze_button.setObjectName("analyzeButton")
        self.analyze_button.setEnabled(False)
        self.select_button.clicked.connect(self.select_image)
        self.analyze_button.clicked.connect(self.analyze_image)
        top_layout.addWidget(self.select_button)
        top_layout.addWidget(self.analyze_button)
        top_layout.addStretch()

        self.status_label = QLabel("준비 완료")
        self.status_label.setObjectName("status")
        top_layout.addWidget(self.status_label)
        main_layout.addWidget(top_bar)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        image_panel = QWidget()
        image_panel.setObjectName("panel")
        image_layout = QVBoxLayout(image_panel)
        image_layout.setContentsMargins(16, 16, 16, 16)
        image_layout.setSpacing(10)
        image_heading = QLabel("SOURCE IMAGE")
        image_heading.setObjectName("sectionHeading")
        image_layout.addWidget(image_heading)

        self.image_label = QLabel("사진을 업로드하세요")
        self.image_label.setObjectName("imageViewer")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(420, 420)
        image_layout.addWidget(self.image_label, 1)
        content_layout.addWidget(image_panel, 1)

        result_panel = QWidget()
        result_panel.setObjectName("panel")
        result_layout = QVBoxLayout(result_panel)
        result_layout.setContentsMargins(16, 16, 16, 16)
        result_layout.setSpacing(10)
        result_heading = QLabel("ANALYSIS RESULT")
        result_heading.setObjectName("sectionHeading")
        result_layout.addWidget(result_heading)

        self.result_text = QTextEdit()
        self.result_text.setObjectName("resultText")
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("AI가 분석한 내용이 여기에 표시됩니다.")
        result_layout.addWidget(self.result_text, 1)
        content_layout.addWidget(result_panel, 1)
        main_layout.addLayout(content_layout, 1)

        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet("""
            QWidget#central {
                background: #0b1120;
                color: #e5e7eb;
                font-family: '맑은 고딕', Segoe UI;
            }
            QLabel#title {
                color: #f8fafc;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            QLabel#subtitle {
                color: #94a3b8;
                font-size: 12px;
                margin-bottom: 4px;
            }
            QWidget#topBar, QWidget#panel {
                background: #111827;
                border: 1px solid #263244;
                border-radius: 10px;
            }
            QLabel#sectionHeading {
                color: #64748b;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 2px;
            }
            QLabel#status {
                color: #34d399;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#imageViewer {
                background: #0a0f1a;
                border: 1px dashed #475569;
                border-radius: 8px;
                color: #64748b;
                font-size: 14px;
            }
            QTextEdit#resultText {
                background: #0a0f1a;
                border: 1px solid #263244;
                border-radius: 8px;
                color: #dbeafe;
                font-size: 14px;
                padding: 14px;
                selection-background-color: #2563eb;
            }
            QPushButton {
                min-height: 38px;
                padding: 0 18px;
                border-radius: 7px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton#primaryButton {
                background: #2563eb;
                color: white;
                border: 1px solid #3b82f6;
            }
            QPushButton#primaryButton:hover { background: #1d4ed8; }
            QPushButton#analyzeButton {
                background: #0891b2;
                color: white;
                border: 1px solid #22d3ee;
            }
            QPushButton#analyzeButton:hover { background: #0e7490; }
            QPushButton:disabled {
                background: #1e293b;
                color: #64748b;
                border: 1px solid #334155;
            }
        """)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "사진 선택",
            "",
            "이미지 파일 (*.jpg *.jpeg *.png *.gif *.webp)",
        )
        if not file_path:
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "사진 오류", "지원하지 않는 이미지 파일입니다.")
            return

        self.image_path = file_path
        self.show_preview(pixmap)
        self.analyze_button.setEnabled(True)
        self.result_text.clear()
        self.status_label.setText("이미지 준비 완료")

    def show_preview(self, pixmap):
        preview = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(preview)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_path and self.image_label.pixmap():
            self.show_preview(QPixmap(self.image_path))

    def analyze_image(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            QMessageBox.warning(self, "API 키 오류", ".env 파일에 OPENAI_API_KEY가 설정되어 있어야 합니다.")
            return

        self.analyze_button.setEnabled(False)
        self.select_button.setEnabled(False)
        self.result_text.setPlainText("OpenAI Vision이 이미지를 분석하고 있습니다…")
        self.status_label.setText("AI 분석 중…")

        self.analysis_thread = AnalysisThread(self.image_path, api_key)
        self.analysis_thread.finished_analysis.connect(self.on_analysis_finished)
        self.analysis_thread.failed.connect(self.on_analysis_failed)
        self.analysis_thread.start()

    def on_analysis_finished(self, analysis):
        self.result_text.setPlainText(analysis)
        self.analyze_button.setEnabled(True)
        self.select_button.setEnabled(True)
        self.status_label.setText("분석 완료")

    def on_analysis_failed(self, message):
        self.analyze_button.setEnabled(True)
        self.select_button.setEnabled(True)
        QMessageBox.critical(self, "분석 오류", f"사진 분석에 실패했습니다:\n{message}")
        self.result_text.clear()
        self.status_label.setText("분석 실패")


if __name__ == "__main__":
    load_env_file()
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    sys.exit(app.exec())
