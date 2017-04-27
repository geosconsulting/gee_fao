class A(object):

    def foo(self, x):
        print "executing foo(%s,%s)" % (self, x)

    @classmethod
    def class_foo(cls, x):
        print "executing class_foo(%s,%s)" % (cls, x)

    @staticmethod
    def static_foo(x):
        print "executing static_foo(%s)" % x

a = A()
# The object instance, a, is implicitly passed as the first argument.
print a

# With classmethods, the class of the object instance is implicitly passed as the first argument instead of self.
print a.class_foo(1)

# With staticmethods, neither self (the object instance) nor  cls (the class) is implicitly passed as the first argument.
print a.static_foo(1)
print A.static_foo('hi')
