
skills = [
    "Python","automation","machine learning","data analysis","deep learning",
    "natural language processing","computer vision","reinforcement learning",
    "neural networks","scikit-learn","TensorFlow","Keras","PyTorch",
    "pandas","NumPy","matplotlib","seaborn","SQL",]

resume = "Looking for a Python developer with experience in machine learning, data analysis, and deep learning. Familiarity with libraries such as scikit-learn, TensorFlow, and Keras is a plus. Experience with natural language processing and computer vision is also desirable.".lower()

for skill in skills:
    if skill in resume:
        print(f"Found skill: {skill}")
        
    