import os

# Base path for project files (current working directory)
BASE_PATH = os.getcwd()

def writer(text: str):
    with open(os.path.join(BASE_PATH, "temp.txt"), 'w') as f:
        f.write(text)
        f.write('\n')

def spacer():
    with open(os.path.join(BASE_PATH, "temp.txt"), 'w') as f:
        f.write('\n')
        f.write('\n')

def appender(text: str):
    with open(os.path.join(BASE_PATH, "temp.txt"), 'a') as f:
        f.write(text)
        f.write('\n')

def filewriter(text: str, filename: str):
    with open(os.path.join(BASE_PATH, filename + '.txt'), 'w') as f:
        f.write(text)
        f.write('\n')

def fileappender(text: str, filename: str):
    with open(os.path.join(BASE_PATH, filename + '.txt'), 'a') as f:
        f.write(text)
        f.write('\n')