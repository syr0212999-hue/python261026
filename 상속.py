#부모클래스 정의

class person:
    def __init__(self, name, phonenumber):
        self.name = name
        self.phonenumber = phonenumber

    def printInfo(self):
        print(f"이름: {self.name}, 전화번호: {self.phonenumber}")

class student(person):
    def __init__(self, name, phonenumber, studentID):
        super().__init__(name, phonenumber)
        self.studentID = studentID
        
p = person("황인성", "010-1234-5678")
p.printInfo()

p2 = student("홍길동", "010-9876-5432", "2023001")
p2.printInfo()
