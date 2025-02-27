a = (float(input('Side 1: ')))
b = (float(input('Side 2: ')))
c = (float(input('Side 3: ')))

if a == b == c:
    print('The triangle is equilateral')

elif a == b or b==c or a ==c:
    print('The triangle is isosceles')

elif a**2 + b**2 == c**2 or b**2 + c**2 == a**2 or c**2 + b**2 == a**2:
    print('The triangle is right angled')    

else:
    print('the triangle is scalene')
