def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y != 0:
        return x / y
    else:
        return "Error! Division by zero."

def square(x):
    return x * x

print("Select operation:")
print("1. Add")
print("2. Subtract")
print("3. Multiply")
print("4. Divide")
print("5. Square")

choice = input("Enter choice (1/2/3/4/5): ")

num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

# Check if the operation needs one or two numbers
if choice in ['1', '2', '3', '4']:
    more_numbers = input("Any more numbers? (yes/no): ").lower()
if more_numbers == 'yes':
    num3 = float(input("Enter your third number: "))
   
if choice == '1':
    result = add(num1, num2)
    if more_numbers == 'yes':
        result = add(result, num3)

elif choice == '2':
    result = subtract(num1, num2)
    if more_numbers == 'yes':
        result = subtract(result, num3)

elif choice == '3':
    result = multiply(num1, num2)
    if more_numbers == 'yes':
        result = multiply(result, num3)

elif choice == '4':
    result = divide(num1, num2)
    if more_numbers == 'yes':
        result = divide(result, num3)

elif choice == '5':
    result = square(num1)

else:
    result = "Invalid input"

print(f"Result: {result}")
