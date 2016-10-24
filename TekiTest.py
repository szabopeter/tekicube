#!env python3
import unittest
from teki import Edge, Side, Arrangement
from teki import DIR_TOP, DIR_BOTTOM

class TekiTestCase(unittest.TestCase):
    def testEdgeMatch(self):
        e1 = Edge("XX  XX", DIR_TOP)
        e2 = Edge("  XX  ", DIR_BOTTOM)
        self.assertTrue(e1.matches(e2))

if __name__ == '__main__':
    unittest.main()
