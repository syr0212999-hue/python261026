#문자열처리연습.py
strA = """
이 문자열은
다중 라인으로
저장되어 있습니다.
"""

strB = "python is very powerful"


#디버깅
print(strA)
print(strB)
print(strA+strB)
print(len(strB))
print(strB[0])
print(strB[0:3])
print(strB[:6])
print(strB[-2:])


#리스트
colors = ["red", "white", "green"]
print(colors)
colors.append("blue")
print(colors)
colors.insert(1,"black")
print(colors)

#삭제
colors.remove("red")
print(colors)
for item in colors:
    print(item)

#정렬
colors.extend(["white"])
print(colors)
for item in colors:
    print(item)
colors.sort()
print("colors")

#세트형식

a = {1,2,3,4}
b = {3,4,4,5}

print(a)
print(b)
print(a.union(b))
print(a.intersection(b))

#튜플형식
tp = (100,200,300)
print(type(tp))
print(tp[0])
tp2 = (400)

def times(a,b):
    return a+b

result = times(3,4)
print(result)

print('id:%s, name:%s' % ("syr02129","황인성"))
