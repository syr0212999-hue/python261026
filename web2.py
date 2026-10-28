#web2.py
#웹크롤링을 위한 선언
from bs4 import BeautifulSoup
#웹 서버에 요청
import urllib.request
#정규표현식
import re

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
        title = title.replace("\n", "")
        if re.search("아이폰", title):
            print(title)
            f.write(title + "\n")
f.close()


    # <span class="subject_fixed" data-role="list-title-text" title="아이폰17프로맥스 256 실버 자급제">
    # 							아이폰17프로맥스 256 실버 자급제
    # 						</span>



