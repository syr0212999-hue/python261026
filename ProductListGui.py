import sys

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

from ProductList import ProductList


class ProductListWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("자전거용품 관리")
        self.resize(700, 500)

        self.product_list = ProductList()
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        input_layout = QHBoxLayout()
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("자동 생성")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("자전거용품 이름")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("가격")

        input_layout.addWidget(QLabel("ID"))
        input_layout.addWidget(self.id_input)
        input_layout.addWidget(QLabel("이름"))
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(QLabel("가격"))
        input_layout.addWidget(self.price_input)
        layout.addLayout(input_layout)

        button_layout = QHBoxLayout()
        insert_button = QPushButton("입력")
        update_button = QPushButton("수정")
        delete_button = QPushButton("삭제")
        search_button = QPushButton("검색")
        insert_button.clicked.connect(self.insert_product)
        update_button.clicked.connect(self.update_product)
        delete_button.clicked.connect(self.delete_product)
        search_button.clicked.connect(self.search_product)

        for button in (insert_button, update_button, delete_button, search_button):
            button_layout.addWidget(button)
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "용품명", "가격"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.fill_inputs_from_selected_row)
        layout.addWidget(self.table)

        self.name_input.returnPressed.connect(self.insert_product)
        self.price_input.returnPressed.connect(self.insert_product)

    def clear_inputs(self):
        self.id_input.clear()
        self.name_input.clear()
        self.price_input.clear()

    def show_warning(self, message):
        QMessageBox.warning(self, "입력 확인", message)

    def parse_price(self):
        text = self.price_input.text().strip()
        try:
            price = int(text)
        except ValueError:
            self.show_warning("가격은 정수로 입력하세요.")
            return None
        if price < 0:
            self.show_warning("가격은 0 이상이어야 합니다.")
            return None
        return price

    def insert_product(self):
        name = self.name_input.text().strip()
        if not name:
            self.show_warning("용품 이름을 입력하세요.")
            return
        price = self.parse_price()
        if price is None:
            return

        self.product_list.insert(None, name, price)
        self.clear_inputs()
        self.load_products()
        self.name_input.setFocus()

    def update_product(self):
        product_id = self.id_input.text().strip()
        if not product_id.isdigit():
            self.show_warning("목록에서 수정할 용품을 선택하세요.")
            return
        name = self.name_input.text().strip()
        if not name:
            self.show_warning("용품 이름을 입력하세요.")
            return
        price = self.parse_price()
        if price is None:
            return

        if self.product_list.update(int(product_id), name, price) == 0:
            self.show_warning("수정할 용품을 찾을 수 없습니다.")
            return
        self.clear_inputs()
        self.load_products()

    def delete_product(self):
        product_id = self.id_input.text().strip()
        if not product_id.isdigit():
            self.show_warning("목록에서 삭제할 용품을 선택하세요.")
            return

        result = QMessageBox.question(
            self,
            "삭제 확인",
            "선택한 용품을 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if result == QMessageBox.StandardButton.Yes:
            self.product_list.delete(int(product_id))
            self.clear_inputs()
            self.load_products()

    def search_product(self):
        product_id = self.id_input.text().strip()
        if product_id:
            if not product_id.isdigit():
                self.show_warning("ID는 숫자로 입력하세요.")
                return
            rows = self.product_list.select(int(product_id))
        else:
            name = self.name_input.text().strip()
            rows = self.product_list.select()
            if name:
                rows = [row for row in rows if name.lower() in row[1].lower()]
        self.display_products(rows)

    def load_products(self):
        self.display_products(self.product_list.select())

    def display_products(self, rows):
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                if column_index in (0, 2):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_index, column_index, item)

    def fill_inputs_from_selected_row(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        self.id_input.setText(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        self.price_input.setText(self.table.item(row, 2).text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductListWindow()
    window.show()
    sys.exit(app.exec())
