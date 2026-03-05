#Password Strength Checker

while True:
    password = input("Enter a password: ")
    
    length = len(password)
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for char in password)
    
    if length >= 6 and length <= 20 and has_upper and has_lower and has_digit and has_special:
        print("Password is strong.")
        break
    else:
        print("Password is weak. Please try again.")
