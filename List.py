# A list is a collection of items that are ordered and changeable. Lists are defined using square brackets [].
# Think of it like a shopping bag - you can add , remove, and change the items inside it.

grocery_list = ["milk", "eggs", "bread"]
print(grocery_list) # Output: ['milk', 'eggs', 'bread']
print(type(grocery_list)) # Output: <class 'list'>

# Accessing List Elements
print(grocery_list[0]) # Output: milk
print(grocery_list[1]) # Output: eggs
print(grocery_list[2]) # Output: bread

# Modifying List Elements
grocery_list[0] = "almond milk"
print(grocery_list) # Output: ['almond milk', 'eggs', 'bread

# List Methods
grocery_list.append("butter") # Adds an item to the end of the list
print(grocery_list) # Output: ['almond milk', 'eggs', 'bread', 'butter']
grocery_list.insert(1, "cheese") # Inserts an item at a specific index
print(grocery_list) # Output: ['almond milk', 'cheese', 'eggs', 'bread', 'butter']
grocery_list.remove("eggs") # Removes the first occurrence of an item
print(grocery_list) # Output: ['almond milk', 'cheese', 'bread', 'butter']
grocery_list.pop() # Removes the last item from the list
print(grocery_list) # Output: ['almond milk', 'cheese', 'bread']
grocery_list.clear() # Removes all items from the list
print(grocery_list) # Output: []

# Length and Looping through a List
grocery_list = ["milk", "eggs", "bread"]
print(len(grocery_list)) # Output: 3
for item in grocery_list:
    print(item)
# Output:
# milk
# eggs
# bread


# List Slicing
grocery_list = ["milk", "eggs", "bread", "butter", "cheese"]
print(grocery_list[1:4]) # Output: ['eggs', 'bread', 'butter']
print(grocery_list[:3]) # Output: ['milk', 'eggs', 'bread
print(grocery_list[2:]) # Output: ['bread', 'butter', 'cheese']


# List Comprehension
# squared_numbers = [x**2 for x in range(1, 6)]
# print(squared_numbers) # Output: [1, 4, 9, 16, 25]
# even_numbers = [x for x in range(1, 11) if x % 2 == 0]
# print(even_numbers) # Output: [2, 4, 6, 8, 10]

numbers = [10, 20, 33, 40, 50]
squared_numbers = [x*x for x in numbers]
print(squared_numbers) # Output: [100, 400, 1089, 1600, 2500]



# Nested Lists
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(matrix[0]) # Output: [1, 2, 3]    
print(matrix[1][2]) # Output: 6


