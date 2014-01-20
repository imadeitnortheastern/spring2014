x = 5
y = 5
z = 10
 
########################### equal ###########################
if x == y:
    print "value to return when true"
 
############################ and ############################
if x == y and y == z:
    print "this will print only if both statements are true"
 
############################ or #############################
if x == y or y == z:
    print "this will print if EITHER statements is true"
 
########################### not #############################
if x != 7:
    print "this will print if x is not equal to 7"
 
if x is not 7:
    print "this will also print if x is not 7"
 
#################### if, elif, and else #####################
if x == 6:
    print "This will print whenever x is 5"
elif x == z:
    print "This will only print if x is equal to" + \
        " 10 AND x is not equal to 5"
else: 
    print "this will only print if the above cases are" + \
    " both false"
 
 
##############################################################
########################### loops ############################
##############################################################
 
l = [1, 3, 5, 7, 9]
j = 0
 
########################## range #############################
#for generates a list with all of the values from the first 
#argument, up to BUT NOT INCLUDING the second argument
one_to_ten = range(1,11)
print one_to_ten

########################### for ##############################
#Runs the indented code with i equal to each element in the 
#range, in turn
for i in range(0,5):
    print "the current value in the list is %d" % i

#iterates through the loop, storing the n-th value of the list
#in the variable i in turn 
for i in l:
    print "the current value in the list is %d" % i
 
########################## while ##############################
while j < len(l):
    print "the current value in l is %d" % l[j]
    print "don't forget to change j!"
    j = j + 1
 
while False:
    print "this will never be printed"
 
###############################################################
####################### functions #############################
###############################################################
#simple function that takes two inputs, adds them together
#and returns the sum
def adder(x, y):
    sums = x + y
    return sums
 
x = adder(3,5) #x now equals 8
 
##############################################################
#################### dictionaries ############################
##############################################################
#dictionaries are like lists, but allows for random access,
#which can be much faster. Values are stored in pairs, with 
#the first value (typically a string or number) acting as
#the reference you can use to get access to the second value
#which might be a more complex data structure, like a class
#instance
d = {'key1':'value1', 'key2':'value2'}
 
x = d['key1'] #will return the string 'value1'
 
###############################################################
####################### classes ###############################
###############################################################
#classes are moulds used to describe how you group your data
#in the below example, I created a class Person to hold 
#information about a college student. This mould also knows how 
#to tell, given another person, if that person is older than 
#this person. Functions that are built into classes (which take
#the 'self' argument are called 'methods')
class Person:
    def __init__(self, name, age, major):
        self.name = name
        self.age = age
        self.major = major
 
    #determines if this person is older than the given person
    #returns a boolean (true or false) value
    def older(self, other_person):
        return self.age > other_person.age
 
james = Person('James', 21, 'Computer Science')
zeev = Person("Ze'ev", 19, 'Lazy dropout')
x = james.older(zeev) #x now has value True
 
###############################################################
######################## Flask Stuff ##########################
###############################################################
#at the beginning of the file, we must tell python to get all of
#flasks tools so that we can use them
from flask import Flask #Optional: redirect, url_for, session,
                        #render_template
 
#if we want to work with the Flask framework, we must have an 
#instance of the framework, as all of the functionality is baked 
#into the flask object
my_app = Flask(__name__)
 
#Flask will listen to any HTTP 'GET' requests which hit our IP
#address. If someone requests our IP address and then a special
#extension, i.e. 127.0.0.1:5000/myProfile (not a real IP)
#we can tell flask to use that additional route information 
#to determine which web page to show them.
#in the below instance, we are saying that if the user requests
#MyIP/home/ followed by any string, we will display the page
#described by the functions below this route flag 
@my_app.route('/<username>'):
def hello(username):
    return "hello %s" % username
 
#When you first run a flask app, it will sprint through the file
#initializing variables, and finally getting to this line
#since we just used the default arguement when creating our Flask
#object (__name__), this will be true, and it will execute the 
#commands nested in this if statement
if __name__ == '__main__':
    #this turns on debug mode in your application, which means
    #if your application crashes, Flask will do it's best to 
    #help you figure out why by showing you all the commands
    #that were led to the crash
    my_app.debug = True
 
    #This starts your application!!
    #More specifically, it starts an HTTP listener, which keeps
    #an ear out for requests to your IP address, and then uses
    #the routes you used above, and their associated functions
    #to decide how best to service the requests
    my_app.run()
