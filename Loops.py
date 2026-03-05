# # for loop example
# for i in range(5):
#     print(i)

# # while loop
# count = 0
# while count < 5:
#     print(count)
#     count += 1

# # Real-life example:
# emails = ["ss@gmail.com", "aa@gmail.com", "bb@gmail.com"]

# for email in emails:
#     print(f"Sending email to: {email}")
    
    
# while loop example
# i = 0
# while i < 5:
#     print(i)
#     i += 1
        
        
        
# #continue statement example
# for i in range(10):
#     if i % 2 == 0:
#         continue  # Skip even numbers
#     print(i)  # This will only print odd numbers
    
# #break statement example
# for i in range(10):
#     if i == 5:
#         break  # Exit the loop when i is 5
#     print(i)  # This will print numbers from 0 to 4
    
# #Loop with Lists, String
# fruits = ["apple", "banana", "cherry"]
# for fruit in fruits:
#     print(f"I like {fruit}")
    
# text = "Hello, World!"
# for char in text:
#     print(char)
    
# #Nested loops example
# for i in range(3):
#     for j in range(2):
#         print(f"Outer loop: {i}, Inner loop: {j}")
    
    
#Automation Bot to Rename Files:

files = ["report1.txt", "report2.txt", "report3.txt"]
for i, f in enumerate(files, start=1):
    new_name = f"renamed_report_{i}.txt"
    print(f"Renaming {f} to new_{new_name}")