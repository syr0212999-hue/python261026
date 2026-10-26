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
