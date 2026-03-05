#Introduction to Strings in Python

a = "Hello, World!"
print(a)

#String Concatenation
str1 = "Hello"
str2 = "World"
result = str1 + " " + str2
print(result)

#String Formatting
name = "Alice"
age = 30
formatted_string = f"My name is {name} and I am {age} years old."

print(formatted_string)

#String Methods
text = "Hello, World!"
print(text.upper())  # Convert to uppercase
print(text.lower())  # Convert to lowercase
print(text.replace("World", "Python"))  # Replace a substring
print(text.split(", "))  # Split the string into a list

# String Repetition
repeat_text = "Hello! " * 3
print(repeat_text)

# String Slicing
sliced_text = text[0:5]
print(sliced_text)

#String Length
length = len(text)
print(length)

#strip
stripped_text = text.strip()
print(stripped_text)


#replace (old, new)
replaced_text = text.replace("Hello", "Hi")
print(replaced_text)

#split (separator)
split_text = text.split(", ")
print(split_text)

#split(deliminter) - Splits string into list

text = "Hello, World!"
items = text.split(", ")
print(items)

#join (iterable) - Joins elements of an iterable into a string
items = ["Python", "is", "great"]
joined_text = " ".join(items)
print(joined_text)

#title() - Converts the first character of each word to uppercase
text = "python is powerful"
print(text.title())
print(text.capitalize())  # Capitalizes the first character of the string

#find() and index() - Find the index of a substring
text = "Python is powerful"
index = text.find("powerful")
print(index) # Output: 10
index = text.index("powerful")
print(index) # Output: 10

#count() - Counts the occurrences of a substring
text = "Python is powerful. Python is popular."
count = text.count("Python")
print(count) # Output: 2

# startswith() and endswith() - Check if a string starts or ends with a specific substring
text = "Hello World Python!"
starts_with = text.startswith("Hello")
ends_with = text.endswith("Python!")
print(starts_with) # Output: True
print(ends_with) # Output: True


#String Indexing and Slicing
text = "Hello, World!"


#Indexing
first_char = text[0]
print(first_char) # Output: H
last_char = text[-1]
print(last_char) # Output: !

#Slicing
substring = text[0:5]
print(substring) # Output: Hello
substring = text[7:]
print(substring) # Output: World!


# String Formating Techniques
s = "Python is fun"
print(f"String: {s}") # Using f-string
print("String: {}".format(s)) # Using format() method
