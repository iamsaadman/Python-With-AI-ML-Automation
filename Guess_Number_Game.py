import random

print("🎯 Welcome to the Number Guessing Game!")
print("I'm thinking of a number between 1 and 100.")

# generate a secret number
target = random.randint(1, 100)
attempts = 0

while True:
    try:
        guess = int(input("Enter your guess: "))
    except ValueError:
        print("Please enter a valid integer.")
        continue

    attempts += 1
    if guess < target:
        print("Too low, try again.")
    elif guess > target:
        print("Too high, try again.")
    else:
        print(f"🎉 Congratula­tions! You guessed the number {target} in {attempts} attempts.")
        break
