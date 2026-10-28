import sqlite3
from pathlib import Path


class ProductList:
    def __init__(self, db_name="MyProduct.db"):
        self.db_path = str(Path(__file__).resolve().parent / db_name)
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):
        with self.connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS Products (
                    productID INTEGER PRIMARY KEY,
                    productName TEXT NOT NULL,
                    productPrice INTEGER NOT NULL
                )
            """)

    def insert(self, product_id, product_name, product_price):
        with self.connect() as con:
            con.execute(
                "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
                (product_id, product_name, product_price),
            )

    def update(self, product_id, product_name=None, product_price=None):
        fields = []
        params = []

        if product_name is not None:
            fields.append("productName = ?")
            params.append(product_name)
        if product_price is not None:
            fields.append("productPrice = ?")
            params.append(product_price)
        if not fields:
            return 0

        params.append(product_id)
        with self.connect() as con:
            cursor = con.execute(
                f"UPDATE Products SET {', '.join(fields)} WHERE productID = ?",
                params,
            )
            return cursor.rowcount

    def delete(self, product_id):
        with self.connect() as con:
            cursor = con.execute("DELETE FROM Products WHERE productID = ?", (product_id,))
            return cursor.rowcount

    def select(self, product_id=None):
        with self.connect() as con:
            if product_id is None:
                rows = con.execute(
                    "SELECT productID, productName, productPrice FROM Products ORDER BY productID"
                ).fetchall()
            else:
                row = con.execute(
                    "SELECT productID, productName, productPrice FROM Products WHERE productID = ?",
                    (product_id,),
                ).fetchone()
                rows = [] if row is None else [row]
            return rows

    def prepare_sample_data(self, count=1000):
        with self.connect() as con:
            con.execute("DELETE FROM Products")
            con.executemany(
                "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
                [
                    (product_id, f"전자제품 {product_id:04d}", 10000 + (product_id * 1700 % 990000))
                    for product_id in range(1, count + 1)
                ],
            )


if __name__ == "__main__":
    products = ProductList()
    products.prepare_sample_data(1000)
    print(f"{len(products.select())}개의 샘플 데이터가 저장되었습니다: {products.db_path}")
