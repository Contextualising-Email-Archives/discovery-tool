import pandas as pd 

mylist = range(3)

def createGenerator(mylist):
    
    for i in mylist:
        yield i*i

mygenerator = createGenerator(mylist) 
for i in mygenerator:
    print (i)


