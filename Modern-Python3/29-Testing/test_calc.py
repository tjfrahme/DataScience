import unittest
import calc

# First create a class

class TestCalc(unittest.TestCase):      # inherit class from unittest.TestCase

    def test_add(self):
        self.assertEqual(calc.add(10, 5), 15)  # calls the calc file, and the add method    
        self.assertEqual(calc.add(-1, 1), 0)  
        self.assertEqual(calc.add(-1, -1), -2)  


    def test_subtract(self):
        self.assertEqual(calc.subtract(10, 5), 5)  # calls the calc file, and the add method    
        self.assertEqual(calc.subtract(-1, 1), -2)  
        self.assertEqual(calc.subtract(-1, -1), 0)  


    def test_multiply(self):
        self.assertEqual(calc.multiply(10, 5), 50)  # calls the calc file, and the add method    
        self.assertEqual(calc.multiply(-1, 1), -1)  
        self.assertEqual(calc.multiply(-1, -1), 1) 
    #    self.assertEqual(calc.multiply(-1, -1), -1)    # purposful failure


    def test_divide(self):
        self.assertEqual(calc.divide(10, 5), 2)  # calls the calc file, and the add method    
        self.assertEqual(calc.divide(-1, 1), -1)  
        self.assertEqual(calc.divide(-1, -1), 1)  

       # self.assertRaises(ValueError, calc.divide, 10, 0)  # Method 1
        with self.assertRaises(ValueError)                  # Alt Method
            calc.divide(10, 0)

# Run the code within the conditional. Allows us to run from console instead of terminal.  
# w/o you would need to enter python -m unittest test_calc.py in the terminal window
# now in terminal can write python test_calc.py
if __name__ == '__main__':
    unittest.main()