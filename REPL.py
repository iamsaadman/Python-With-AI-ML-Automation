# #REPL Calculator

# num1 = int(input("Enter the first number: "))
# num2 = int(input("Enter the second number: "))

# print("The sum of the two numbers is: ", num1 + num2)
# print("The difference of the two numbers is: ", num1 - num2)
# print("The product of the two numbers is: ", num1 * num2)
# print("The quotient of the two numbers is: ", num1 / num2)
   
   
# # ASCII Code

# print("The ASCII code of 'A' is: ", ord('A'))
# print("The ASCII code of 'a' is: ", ord('a'))   
# print(ord("😂"))
# print(ord("😀"))
# print(ord("😎"))


# #Lucky Number Fortune Teller
# lucky_number = int(input("Enter your lucky number: "))
# if lucky_number % 2 == 0:
#     print("Your lucky number is even! You will have a great day!")  
# else:
#     print("Your lucky number is odd! You will have an adventurous day!")


# # Simple Interest Calculator
# principal = float(input("Enter the principal amount: "))
# rate = float(input("Enter the annual interest rate (in %): "))
# time = float(input("Enter the time (in years): "))
# simple_interest = (principal * rate * time) / 100
# print("The simple interest is: ", simple_interest)

# # Temperature Converter
# celsius = float(input("Enter the temperature in Celsius: "))
# fahrenheit = (celsius * 9/5) + 32
# print("The temperature in Fahrenheit is: ", fahrenheit)

# # BMI Calculator
# weight = float(input("Enter your weight in kilograms: "))
# height = float(input("Enter your height in meters: "))
# bmi = weight / (height ** 2)
# print("Your Body Mass Index (BMI) is: ", bmi)

# # Currency Converter
# usd_amount = float(input("Enter the amount in USD: "))
# exchange_rate = float(input("Enter the exchange rate (1 USD to target currency): "))
# target_currency_amount = usd_amount * exchange_rate
# print("The amount in the target currency is: ", target_currency_amount)

# # Simple Age Calculator
# current_year = int(input("Enter the current year: "))
# birth_year = int(input("Enter your birth year: "))
# age = current_year - birth_year
# print("Your age is: ", age)

# # Simple Password Strength Checker
# password = input("Enter your password: ")
# if len(password) < 6:
#     print("Your password is weak! It should be at least 6 characters long.")
# elif len(password) < 12:
#     print("Your password is moderate! Consider using a longer password for better security.")
    
# else:
#     print("Your password is strong! Great job!")
    

# # Red Text Generator
# text = input("Enter the text you want to display in red: ")
# red_text = "\033[31m" + text + "\033[0m"   
# print(red_text) 

# # Golden Text Generator 
# text = input("Enter the text you want to display in golden color: ")
# golden_text = "\033[93m" + text + "\033[0m"
# print(golden_text)

# # Green Text Generator
# text = input("Enter the text you want to display in green: ")
# green_text = "\033[92m" + text + "\033[0m"
# print(green_text)

# # User with Variables
# name = input("Enter your name: ")
# print("\033[92mHello, " + name + "!\033[0m Welcome to the world of programming!")


# # Mini Math with pow() , roud() ,  abs() , divmod() , max() , min() , sum() , len() , sorted() , reversed() , enumerate() , zip() , map() , filter() , reduce() , lambda functions
# print(pow(2, 3))  # 2 raised to the power of 3
# print(round(3.14159, 2))  # Round to 2 decimal places
# print(abs(-5))  # Absolute value of -5
# print(divmod(10, 3))  # Quotient and remainder of 10 divided by 3
# print(max(1, 5, 3))  # Maximum of the numbers
# print(min(1, 5, 3))  # Minimum of the numbers
# print(sum([1, 2, 3, 4, 5]))  # Sum of the numbers in the list
# print(len("Hello"))  # Length of the string
# print(sorted([3, 1, 4, 2]))  # Sorted list
# print(list(reversed([1, 2, 3, 4, 5])))  # Reversed list
# print(list(enumerate(['a', 'b', 'c'])))  # Enumerate the list
# print(list(zip([1, 2, 3], ['a', 'b', 'c'])))  # Zip two lists together
# print(list(map(lambda x: x * 2, [1, 2, 3, 4, 5])))  # Map a function to a list
# print(list(filter(lambda x: x % 2 == 0, [1, 2, 3, 4, 5])))  # Filter even numbers from the list
# from functools import reduce    
# print(reduce(lambda x, y: x + y, [1, 2, 3, 4, 5]))  # Reduce the list to a single value by summing it up

# Opens a cartoon in browser
# import antigravity



# Using Built-in datetime Module 

from datetime import datetime
current_datetime = datetime.now()
print("Current date and time: ", current_datetime)

birth_year = 2004
current_year = 2026
age = current_year - birth_year
print("Your age is: ", age)



# Dream Job Predictor 
name = input("Enter your name: ")
month = input("Enter your birth month (1-12): ") 

if month.lower() in ["january", "february", "march"]:
    print("\033[93m" + name + ", your dream job is: Software Developer!\033[0m")
elif month.lower() in ["april", "may", "june"]:
    print("\033[92m" + name + ", your dream job is: Data Scientist!\033[0m")
elif month.lower() in ["july", "august", "september"]:
    print("\033[31m" + name + ", your dream job is: Graphic Designer!\033[0m")
elif month.lower() in ["october", "november", "december"]:
    print("\033[94m" + name + ", your dream job is: Marketing Manager!\033[0m")
else:
    print("Invalid month! Please enter a valid month name.")    