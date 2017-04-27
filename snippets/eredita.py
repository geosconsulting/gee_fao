class Parent(object):
    saluto = ["hello"]

class Child(Parent):
    saluto = Parent.saluto + ['world']

testolo = Child()
print testolo.saluto