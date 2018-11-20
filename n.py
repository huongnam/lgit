#!/usr/bin/python3
import os
def find_lgit_path():
    all_dirs = list()
    path = os.getcwd()
    while path != '/':
        dirs = os.listdir(path)
        if '.lgit' in dirs:
            return path + '/' + '.lgit'
        path = os.path.dirname(path)
    return path

print(find_lgit_path()[:-5])
