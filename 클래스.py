#클래스

class person:
    def __init__(self):
        self.name = "defalut name"

    def introduce(self):
        print(f"안녕하세요, 제 이름은 {self.name}입니다")

p1 = person()
p2 = person()

p1.name = "황인성"
p1.introduce()
p2.introduce()


name = "황인성"

class person2:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        print(f"안녕하세요, 제 이름은 {self.name}입니다")