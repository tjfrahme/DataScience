import turtle

# create a canvas instance
myturtle = turtle.Turtle()

#Goes to a certain coordinate, will draw a line, 
# otherwise startes in the center.  need to use a penup and pendown
myturtle.penup()
myturtle.forward (100)
myturtle.pendown()

myturtle.goto(50, 75)  
myturtle.left (90)
myturtle.forward (200)

turtle.done()