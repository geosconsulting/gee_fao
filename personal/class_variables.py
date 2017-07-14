class MyClass:
    static_elem = 123

    def __init__(self):
        self.object_elem = 456

c1 = MyClass()
c2 = MyClass()

# Initial values of both elements
print "Original cl static %d object %d" % (c1.static_elem, c1.object_elem)
print "Original c2 static %d object %d" % (c2.static_elem, c2.object_elem)
print

# Nothing new so far ...
# Let's try changing the static element
MyClass.static_elem = 999

print "Changed Static cl static %d object %d" % (c1.static_elem, c1.object_elem)
print "Changed Static c2 static %d object %d" % (c2.static_elem, c2.object_elem)
print

# Now, let's try changing the object element
c1.object_elem = 888

print "Changed Object cl static %d object %d" % (c1.static_elem, c1.object_elem)
print "Changed Object c2 static %d object %d" % (c2.static_elem, c2.object_elem)
