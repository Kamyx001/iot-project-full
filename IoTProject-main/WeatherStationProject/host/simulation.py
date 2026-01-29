import random

def getData():
    temp = round(random.uniform(15.0, 25.0), 2)
    humid = round(random.uniform(30.0, 70.0), 2)
    return temp, humid