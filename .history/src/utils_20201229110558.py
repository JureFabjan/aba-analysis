# from https://www.tutorialspoint.com/How-can-I-create-a-directory-if-it-does-not-exist-using-Python

import os

def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path