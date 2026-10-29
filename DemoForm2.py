import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic
#크롤링
from bs4 import BeautifulSoup
#웹 서버에 요청
import urllib.request
#정규표현식
import re


#화면을 로딩
from_class = uic.loadUiType("DemoForm2.ui")[0]

#폼클래스 정의
class DemoForm(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label.setText("PyQt6 사용하기")

    # 슬롯 메서드 추가
    def firstClick(self):
        #파일에 저장
        f = open("todayhumor.txt", "wt", encoding="utf-8")


        #헤더
        hdr = {'User-Agent': 'Mozilla/5.0'} 
        base_url = "https://www.clien.net/service/board/sold?&od=T31&category=0&po="
        for page in range(1, 11):
            url = base_url + str(page)
            #주소 확인
            print(url)

            #요청객체 생성
            req = urllib.request.Request(url, headers=hdr)
            page = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(page, "html.parser")

            #매물 정보 추출
            items = soup.find_all("span", attrs={"data-role": "list-title-text"})
            for item in items:
                title = item.text.strip()
                #화면 있는 입력 문자열
                search = self.lineEdit.text()
                title = title.replace("\n", "")
                if re.search("search", title):
                    print(title)
                    f.write(title + "\n")
        f.close()

        self.label.setText("아이폰 크롤링!")

    def secondClick(self):
        self.label.setText("두번째 버튼 클릭!")

    def thirdClick(self):
        self.label.setText("세번째 버튼 클릭!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = DemoForm()
    demo.show()
    app.exec()