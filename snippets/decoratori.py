a_string = "This is a global variable"

def foo():
    a_string = "This is a local variable"
    return a_string

print foo()

def foo1(x):
    return locals()

print foo1(1)

def outer():
    x = 1
    def inner():
        print x
    inner()
outer()

def add(x,y):
    return x + y

def sub(x,y):
    return x-y

def apply(func,x,y):
    return func(x,y)

print apply(add, 3, 4)
print apply(sub, 3, 4)

def esterna():
    x = 1
    def interna():
        print x
    return interna

bar = esterna()

print bar
print bar()
print bar.func_closure

def esterna1(x):
    def interna1():
        print x
    return interna1

print1 = esterna1(1)
print2 = esterna1(2)
print1()
print2()

# A decorator is just a callable that takes a function as
# an argument and returns a replacement function.
def outer2(some_func):
    def inner2():
