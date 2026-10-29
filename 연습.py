import sqlite3
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


DB_PATH = Path(__file__).resolve().parent / "MyProduct.db"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("자전거용품 관리")
        self.resize(700, 500)
        self.create_database()
        self.setup_ui()
        self.load_products()

    def create_database(self):
        with sqlite3.connect(DB_PATH) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS MyProduct (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL
                )
            """)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        input_layout = QHBoxLayout()
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("자동 생성")
        self.id_input.setReadOnly(False)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("용품 이름")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("가격")

        self.name_input.returnPressed.connect(self.insert_product)
        self.price_input.returnPressed.connect(self.insert_product)

        input_layout.addWidget(QLabel("ID"))
        input_layout.addWidget(self.id_input)
        input_layout.addWidget(QLabel("이름"))
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(QLabel("가격"))
        input_layout.addWidget(self.price_input)
        main_layout.addLayout(input_layout)

        button_layout = QHBoxLayout()
        insert_button = QPushButton("입력")
        update_button = QPushButton("수정")
        delete_button = QPushButton("삭제")
        search_button = QPushButton("검색")
        insert_button.clicked.connect(self.insert_product)
        self.id_input.returnPressed.connect(self.insert_product)
        update_button.clicked.connect(self.update_product)
        delete_button.clicked.connect(self.delete_product)
        search_button.clicked.connect(self.search_products)
        button_layout.addWidget(insert_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(search_button)
        main_layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "이름", "가격"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.select_row)
        main_layout.addWidget(self.table)

    def show_message(self, title, message, icon=QMessageBox.Icon.Information):
        QMessageBox(icon, title, message, QMessageBox.StandardButton.Ok, self).exec()

    def clear_inputs(self):
        self.id_input.clear()
        self.name_input.clear()
        self.price_input.clear()

    def validate_inputs(self, require_name=True, require_price=True):
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()
        if require_name and not name:
            self.show_message("입력 오류", "용품 이름을 입력하세요.", QMessageBox.Icon.Warning)
            return None
        if require_price and not price_text:
            self.show_message("입력 오류", "가격을 입력하세요.", QMessageBox.Icon.Warning)
            return None
        if require_price:
            try:
                price = int(price_text)
            except ValueError:
                self.show_message("입력 오류", "가격은 정수로 입력하세요.", QMessageBox.Icon.Warning)
                return None
            if price < 0:
                self.show_message("입력 오류", "가격은 0 이상으로 입력하세요.", QMessageBox.Icon.Warning)
                return None
        else:
            price = None
        return name, price

    def insert_product(self):
        values = self.validate_inputs()
        if values is None:
            return
        name, price = values
        try:
            with sqlite3.connect(DB_PATH) as con:
                con.execute("INSERT INTO MyProduct (name, price) VALUES (?, ?)", (name, price))
        except sqlite3.Error as error:
            self.show_message("DB 오류", str(error), QMessageBox.Icon.Critical)
            return
        self.clear_inputs()
        self.load_products()
        self.id_input.setFocus()

    def update_product(self):
        product_id = self.id_input.text().strip()
        if not product_id:
            self.show_message("선택 필요", "목록에서 수정할 용품을 선택하세요.", QMessageBox.Icon.Warning)
            return
        values = self.validate_inputs()
        if values is None:
            return
        name, price = values
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.execute(
                "UPDATE MyProduct SET name = ?, price = ? WHERE id = ?",
                (name, price, int(product_id)),
            )
        if cursor.rowcount == 0:
            self.show_message("오류", "수정할 데이터를 찾을 수 없습니다.", QMessageBox.Icon.Warning)
            return
        self.clear_inputs()
        self.load_products()

    def delete_product(self):
        product_id = self.id_input.text().strip()
        if not product_id:
            self.show_message("선택 필요", "목록에서 삭제할 용품을 선택하세요.", QMessageBox.Icon.Warning)
            return
        reply = QMessageBox.question(
            self,
            "삭제 확인",
            "선택한 용품을 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        with sqlite3.connect(DB_PATH) as con:
            con.execute("DELETE FROM MyProduct WHERE id = ?", (int(product_id),))
        self.clear_inputs()
        self.load_products()

    def search_products(self):
        search_id = self.id_input.text().strip()
        search_name = self.name_input.text().strip()
        search_price = self.price_input.text().strip()
        conditions = []
        parameters = []

        if search_id:
            if not search_id.isdigit():
                self.show_message("입력 오류", "ID는 숫자로 입력하세요.", QMessageBox.Icon.Warning)
                return
            conditions.append("id = ?")
            parameters.append(int(search_id))
        if search_name:
            conditions.append("name LIKE ?")
            parameters.append(f"%{search_name}%")
        if search_price:
            try:
                parameters.append(int(search_price))
            except ValueError:
                self.show_message("입력 오류", "가격은 정수로 입력하세요.", QMessageBox.Icon.Warning)
                return
            conditions.append("price = ?")

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        with sqlite3.connect(DB_PATH) as con:
            rows = con.execute(
                f"SELECT id, name, price FROM MyProduct{where_clause} ORDER BY id",
                parameters,
            ).fetchall()
        self.display_products(rows)

    def load_products(self):
        with sqlite3.connect(DB_PATH) as con:
            rows = con.execute("SELECT id, name, price FROM MyProduct ORDER BY id").fetchall()
        self.display_products(rows)

    def display_products(self, rows):
        self.table.setRowCount(len(rows))
        for row_number, row in enumerate(rows):
            for column, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                if column == 0 or column == 2:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_number, column, item)

    def select_row(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        self.id_input.setText(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        self.price_input.setText(self.table.item(row, 2).text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())