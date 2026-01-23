return a ** b
def say_hello(name):
    print("Hello",name)

def area_square(side):
    return print("square x = ",side ** 2)

def power(a=2,b=2):
    pass

def multiply(a,b):
    return a*b

def find_min(my_list):
    min = 123456
    for i in my_list:
        if i < min:
            min = i
    return min