from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class CoinTop20Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("업비트 거래대금 상위 20개 코인")
        self.resize(900, 600)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        button_layout = QHBoxLayout()
        self.fetch_button = QPushButton("코인 조회")
        self.save_button = QPushButton("엑셀 저장")
        button_layout.addWidget(self.fetch_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        self.status_label = QLabel("조회 버튼을 눌러 데이터를 가져오세요.")
        layout.addWidget(self.status_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "순위", "종목명", "심볼", "업비트 원화가격", "24시간 거래대금", "등락률(%)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
