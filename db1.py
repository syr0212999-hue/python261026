#db1.py
import sqlite3

con = sqlite3.connect(r"c//work//test.db")

#커서 객체 생성
cur = con.cursor()

#테이블 구조
cur.execute("CREATE TABLE PHONEBOOK (name text, phone_nuber text)")

#1건 입력
cur.execute(
"INSERT INTO PHONEBOOK VALUES ('홍길동', '010-1234-5678')"
)

#입력 파라메터 처리
name = "황인성"
phone_number = "010-5555-6666"
cur.execute("INSERT INTO PHONEBOOK VALUES (?, ?)", (name, phone_number))

#여러건 입력
cur.executemany(
"INSERT INTO PHONEBOOK VALUES (?, ?)",
[('김철수', '010-9876-5432'), ('이영희', '010-1111-2222')]
)

#검색
cur.execute("SELECT * FROM PHONEBOOK")
for row in cur:
    print(row)

con.commit()
con.close()
