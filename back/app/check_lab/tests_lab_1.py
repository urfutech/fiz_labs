from .check_lab_1 import check_definition
import unittest


class test_definition_checker(unittest.TestCase):
    def test_same_1(self):
        a, b = "A", "A"
        self.assertTrue(check_definition(a, b))

    def test_same_2(self):
        a, b = "abcdefg;;123!@#$", "abcdefg;;123!@#$"
        self.assertTrue(check_definition(a, b))
