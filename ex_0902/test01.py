# 변수를 이용해보자.
def myfunc(x):
    sentence = f"""
AI 서비스 백엔드 프로그래밍 실무
===================
파이썬 기본 문법, 시간:{x}
클래스, 시간:{x}
데코레이터, 시간:{x}
예외 처리, 시간:{x}
로깅, 시간:{x}"""

    return sentence

print(myfunc(8))
print("-------------------------------")


# 리스트를 이용해보자
title = "AI 서비스 백엔드 프로그래밍 실무"
line = "==================="
time = 8
myList = ["파이썬 기본 문법", "클래스", "데코레이터", "예외 처리", "로깅"]

print(title)
print(line)
for x in range(len(myList)):
    print(myList[x], time, sep=", 시간:")

print("----------------------------------------------------")


# 함수를 이용해보자
def cel(f):
    return (f - 32) * 5/9

print(cel(77))
print(cel(95))
print(cel(50))
print("----------------------------------------------------")


# 전체 응용
title = "AI 서비스 백엔드 프로그래밍 실무"
line = "==================="
time = 8
myList = ["파이썬 기본 문법", "클래스", "데코레이터", "예외 처리", "로깅"]
sep = ", 시간:"

def myfunc(x):
    sentence = f"{title}\n{line}"
    for i in range(len(myList)):
        sentence += f"\n{myList[i]}{sep}{x}"

    return sentence

print(myfunc(time))
print("----------------------------------------------------")


# 사칙연산
def f1(su):
    return su + 100

def f2(su):
    return su - 100

def f3(su):
    return su * 100

def f4(su):
    return su / 100

print(f1(5))
print(f2(5))
print(f3(5))
print(f4(5))
