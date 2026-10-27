#반복연습

value = 5
while value > 0:
    print(value)
    value -= 1

print("---for in---")
for i in range(5):
    print(i)


print("---날짜, 연도를 생성---")
print(list(range(2000, 2023)))
print(list(range(1, 32)))

Date = list(range(1995, 2030))
for year in Date:
    print(f"{year}년")

print([i for i in range(1, 32) if i % 2 == 1])

