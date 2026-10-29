import sys

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QTableWidgetItem

from kimpga_coin_top20 import fetch_top20, save_to_excel
from kimpga_coin_top20_gui import CoinTop20Window


class FetchThread(QThread):
    finished_data = pyqtSignal(list)
    failed = pyqtSignal(str)

    def run(self):
        try:
            self.finished_data.emit(fetch_top20())
        except Exception as error:
            self.failed.emit(str(error))


class CoinTop20App(CoinTop20Window):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.fetch_thread = None
        self.fetch_button.clicked.connect(self.fetch_coins)
        self.save_button.clicked.connect(self.save_excel)

    def fetch_coins(self):
        self.fetch_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.status_label.setText("업비트 데이터를 조회하는 중입니다...")

        self.fetch_thread = FetchThread()
        self.fetch_thread.finished_data.connect(self.on_fetch_finished)
        self.fetch_thread.failed.connect(self.on_fetch_failed)
        self.fetch_thread.start()

    def on_fetch_finished(self, rows):
        self.rows = rows
        self.display_rows(rows)
        self.fetch_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.status_label.setText(f"조회 완료: 상위 {len(rows)}개 코인")

    def on_fetch_failed(self, message):
        self.fetch_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.status_label.setText("조회 실패")
        QMessageBox.critical(self, "조회 오류", f"업비트 데이터를 가져오지 못했습니다:\n{message}")

    def display_rows(self, rows):
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            rank, name, symbol, price, trade_volume, change_rate = row
            values = [rank, name, symbol, f"{price:,.0f}", f"{trade_volume:,.0f}", f"{change_rate:.2f}"]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if column_index in (0, 3, 4, 5):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_index, column_index, item)

    def save_excel(self):
        if not self.rows:
            QMessageBox.warning(self, "저장 불가", "먼저 코인 데이터를 조회하세요.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "엑셀 파일 저장", "kimpga_coin_top20.xlsx", "Excel 파일 (*.xlsx)"
        )
        if not file_path:
            return
        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"

        try:
            saved_path = save_to_excel(self.rows, file_path)
            self.status_label.setText(f"엑셀 저장 완료: {saved_path}")
            QMessageBox.information(self, "저장 완료", f"엑셀 파일을 저장했습니다:\n{saved_path}")
        except Exception as error:
            QMessageBox.critical(self, "저장 오류", f"엑셀 파일을 저장하지 못했습니다:\n{error}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoinTop20App()
    window.show()
    sys.exit(app.exec())
