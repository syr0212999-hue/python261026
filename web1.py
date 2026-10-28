from bs4 import BeautifulSoup

#파일 로딩
page = open("CHAP09_TEST.html", "rt", encoding="utf-8").read()
#검색 객체
soup = BeautifulSoup(page, "html.parser")
#전체 보기
#print(soup.prettify())

#p테그 검색
#print(soup.find_all("p")) 

#첫번째 p테그 검색
#print(soup.find("p"))
# print(soup.find_all("p", class_="outer-text"))
# print(soup.find_all("p", attrs={"class": "outer-text"}))

# print(soup.find_all("p", id="first"))

for tag in soup.find_all("p"):
    title = tag.text.strip()
    title = title.replace("\n", "")
    print(title)

print("============문자열 처리 메서드==================")
data = "<<< spam ham eggs >>>"
result = data.strip("<>")
print(result)
print(data)


#정규표현식
import re

result = re.search("[0-9]*th", "35th, 17th, 1st, 2nd")
print(result)
print(result.group())

result = re.search("\d{4}", "1234올해는 2026년")
print(result)
print(result.group())

result = re.search("apple", "this is apple")
print(result)
print(result.group())
