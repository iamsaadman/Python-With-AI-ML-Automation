# Turn your python project into a web app (with No JS)

#What is Streamlit?
# Streamlit is an open-source Python library that allows you to create interactive web applications for data
# science and machine learning projects with minimal effort. It provides a simple and intuitive API for building web apps, making it easy to share your work with others.


import streamlit as st

# Set the title of the app
st.title("My First AI App")
st.header("AI, ML, and Automation with Python")
st.write("Welcome to my first AI app!")


if st.button("Click Me"):
    st.success("Button clicked!")
    
    

name = st.text_input("Enter your name:")
if name:
    st.write(f"Hello, {name}! Welcome to the world of AI and ML with Python.")
    
age = st.slider("Select your age:", 0, 100, 25)
st.write(f"You are {age} years old.")

