import imp
from msilib.schema import Patch
from multiprocessing import Event


import os
import os

from sqlalchemy import table
path = 'sessions'
rez = sorted(os.listdir(path))
for n, item in enumerate(rez):
    print(n+1, item) 
