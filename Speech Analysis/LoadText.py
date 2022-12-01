import os

def find_file(filename):
    dir = os.getcwd()
    while 'Hostile-Narrative-Analysis' in dir:
        dir = os.path.dirname(dir)
        for root, dirs, files in os.walk(dir):
            if filename in files:
                return os.path.join(root, filename)
            
            
def load_text(filename):
    
    filepath = find_file(filename)
    with open(filepath, 'r') as text:
        return text.read()