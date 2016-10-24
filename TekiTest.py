#!env python3
import unittest
from teki import Edge, Side, Arrangement
from teki import VerticalRule, HorizontalRule
from teki import ROT, DIR

class TekiTestCase(unittest.TestCase):
    def testEdgeMatch(self):
        e1 = Edge("X  XXX", DIR.TOP)
        e2 = Edge(" XX   ", DIR.BOTTOM)
        self.assertTrue(e1.matches(e2))

    def testEdgeDoesNotMatch_XvsX(self):
        e1 = Edge("XX  XX", DIR.TOP)
        e2 = Edge("  XX X", DIR.BOTTOM)
        self.assertFalse(e1.matches(e2))

    def testEdgeDoesNotMatch_SpaceVsSpace(self):
        e1 = Edge("XX  X ", DIR.TOP)
        e2 = Edge("  XX  ", DIR.BOTTOM)
        self.assertFalse(e1.matches(e2))

    def makeEdgeDict(self, special_edge = None):
        edges = {}
        for d in DIR.ALL:
            edges[d] = Edge(" "*6, d)
        if special_edge:
            edges[special_edge.direction] = special_edge
        return edges

    def testVerticalRuleMatch_noRotation(self):
        topside = Side("top", self.makeEdgeDict(Edge("X  XXX", DIR.BOTTOM)))
        bottomside = Side("bottom", self.makeEdgeDict(Edge(" XX   ", DIR.TOP)))
        rule = VerticalRule('A', 'B')
        check = rule.check(Arrangement([topside, bottomside]))
        self.assertTrue(check)

    def testHorizontalRuleMatch_noRotation(self):
        leftside = Side("left", self.makeEdgeDict(Edge("X  XXX", DIR.RIGHT)))
        rightside = Side("right", self.makeEdgeDict(Edge(" XX   ", DIR.LEFT)))
        rule = HorizontalRule('A', ROT.NONE, 'B', ROT.NONE)
        check = rule.check(Arrangement([leftside, rightside]))
        self.assertTrue(check)

if __name__ == '__main__':
    unittest.main()
