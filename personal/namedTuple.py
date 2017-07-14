import collections

bob = ('Bob', 30, 'male')
print 'Representation:', bob

jane = ('Jane', 29, 'female')
print '\nField by index:', jane[0]

print '\nFields by index:'
for p in [ bob, jane ]:
    print '%s is a %d year old %s' % p

Person = collections.namedtuple('Person','name age gender')
print 'Type of Person:',type(Person)

bob_1 = Person(name='Bob', age=30, gender='male')
print '\nRepresentation:', bob_1

jane_1 = Person(name='Jane', age=29, gender='female')
print '\nField by name:', jane_1.name

print '\nFields by index:'
for p in [ bob_1, jane_1 ]:
    print '%s is a %d year old %s' % p