# Tupple vs List

# A tuple is an ordered collection of items that is immutable (cannot be changed after creation).
# Tuples are defined using parentheses ().
my_tuple = (1, 2, 3)
print(my_tuple) # Output: (1, 2, 3)
print(type(my_tuple)) # Output: <class 'tuple'>
# Accessing Tuple Elements
print(my_tuple[0]) # Output: 1
print(my_tuple[1]) # Output: 2
print(my_tuple[2]) # Output: 3
# Modifying Tuple Elements (This will raise an error because tuples are immutable)
# my_tuple[0] = 10 # TypeError: 'tuple' object does not support item assignment     


#slicing 

numbering = (10, 20, 30, 40, 50 , 60 ,70)
print(numbering[1:5]) # Output: (20, 30, 40, 50)
print(numbering[:4]) # Output: (10, 20, 30, 40)
print(numbering[3:6]) # Output: (40, 50, 60)
print(numbering[3:]) # Output: (40, 50, 60, 70)
print(numbering[::2]) # Output: (10, 30, 50, 70)

print(len(numbering)) # Output: 7
print(numbering.count(30)) # Output: 1

print(numbering[::-1]) # Output: (70, 60, 50, 40, 30, 20, 10)
print(numbering[-1]) # Output: 70

# loop 
for num in numbering:
    print(num)
    
    
# packing and unpacking

# Packing
my_tuple = 1, 2, 3
print(my_tuple) # Output: (1, 2, 3)

# Unpacking
a, b, c = my_tuple
print(a) # Output: 1
print(b) # Output: 2
print(c) # Output: 3

packed_tuple = ("apple", "banana", "cherry")
fruit1, fruit2, fruit3 = packed_tuple
print(fruit1) # Output: apple
print(fruit2) # Output: banana
print(fruit3) # Output: cherry

print(len(packed_tuple)) # Output: 3
print(packed_tuple.count("banana")) # Output: 1


#Convert tuple to list
my_tuple = (1, 2, 3)
my_list = list(my_tuple)
print(my_list) # Output: [1, 2, 3]


# Convert list to tuple
my_list = [1, 2, 3]
my_tuple = tuple(my_list)
print(my_tuple) # Output: (1, 2, 3)


colors = ("red", "green", "blue")
color_list = list(colors)
print(color_list) # Output: ['red', 'green', 'blue']

color_tuple = tuple(color_list)
print(color_tuple) # Output: ('red', 'green', 'blue')

#sorting
numbers = (5, 2, 9, 1, 5, 6)
sorted_numbers = sorted(numbers)
print(sorted_numbers) # Output: [1, 2, 5, 5, 6, 9]


# Find the topper 
def find_topper(students):
    highest_avg = 0
    topper_name = ""
    for name, marks in students:
        avg = sum(marks) / len(marks)
        if avg > highest_avg:
            highest_avg = avg
            topper_name = name
    return topper_name, highest_avg


students = [
    ("John", [85, 90, 78]),
    ("Alice", [92, 88, 95]),
    ("Bob", [78, 82, 80]),
    ("Eve", [95, 90, 92])
]

print(find_topper(students)) # Output: ('Eve', 92.33333333333333)
