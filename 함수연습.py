#함수연습

def times(a,b):
    return a+b,a*b

def setValue(newValue):
    x = newValue
    print("지역변수", x)

result = setValue(5)

print(result)


x= 10
def func(a):
    return a+x

print(func(1))



def fanc2(a):
    x = 5
    return a+x

print(fanc2(1))


#기본값 명시
def time(a=10, b=20):
    return a*b

#호출
print(time())
print(time(5))
print(time(5,20))

#키워드인자
def connectURI(server, port):
    strURL = "http://" + server + ":" + port
    return strURL
#호출
print(connectURI("credu.com", "8080"))
print(connectURI(port="8080", server="credu.com"))

#가변인자
def union(*ar):
    result = []
    for item in ar:
        for x in item:
            if x not in result:
                result.append(x)
    return result

print(union("HAM", "EGG"))
print(union("HAM", "EGG", "SPAM"))


#람다함수
g = lambda x, y : x*y

print(g(3,4))

print((lambda x, y : x*y)(3,4))
print(dir())
print(globals())