import unittest
from activities import eat, nap, is_funny, laugh

# write unit tests encapsulated as classes that inherit from unittest.TestCase

class ActivityTests(unittest.TestCase):

    # def setUp(self):
    #     do setup stuff here, runs first (i.e. creating cust profiles)   
    #     pass

    # def tearDown(self)
    #     do teardown stuff here
    #     pass
   
   # calls eat and passes in broccoli and True for is healthy, expects an output
   # of "I'm eating broccoli, because my body....".  can also use different 
   # types of assert commands such as assertIn, assertTrue
   # https://docs.python.org/3/library/unittest.html
    def test_eat_healthy(self):
        """This is testing documentation""" # to run this in terminal python test.py -v

        self.assertEqual(
            eat("broccoli", is_healthy = True),
            "I'm eating broccoli, because my body is a temple"
        )   

    def test_eat_unhealthy(self):
        """eat should indicate you've given up eating unhealthy"""
        self.assertEqual(
            eat("pizza", is_healthy=False),
            "I'm eating pizza, because YOLO"
        )

# Testing for errors
# 
# class SomeTests(unittest.TestCase):
#     def testing_for_error(self):
#         """testing for an error"""
#         with self.assertRaises(IndexError):
#             list = [1,2,3]
#             list[100]


    def test_eat_healthy_boolean(self):
        """is_healthy must be a boolean"""
        with self.assertRaises(ValueError):
            eat("pizza", is_healthy="who cares?")


    def test_short_nap(self):
        self.assertEqual(
            nap(1),
            "I'm feeling refreshed after my 1 hour nap"
        )

    def test_long_nap(self):
        self.assertEqual(
            nap(3),
            "Ugh I overslept.  I didn't mean to nap for 3 hours"
        )

    def test_is_funny_tim(self):
        self.assertEqual(is_funny("tim"), False)   
    #    self.assertFalse(is_funny("tim"), "tim should not be funny")  
    #   return none, which is not really correct

    def test_is_funny_anyone_else(self):
        """anyone else but time should be funny"""
        self.assertTrue(is_funny("blue"), "blue should be funny")
        self.assertTrue(is_funny("tammy"), "tammy should be funny")
        self.assertTrue(is_funny("sven"), "sven should be funny")

    def test_laugh(self):
        self.assertIn(laugh(), ('lol', 'haha', 'tehehe'))



# This will run/execute tests in terminal
if __name__ == "__main__":
    unittest.main()

