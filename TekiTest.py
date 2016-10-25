#!env python3
import unittest
from teki import Edge, Side, Arrangement
from teki import VerticalRule, HorizontalRule
from teki import ROT, DIR

def dump(*objects):
    print()
    for o in objects:
        print(str(o))

class TekiTestCase(unittest.TestCase):
    def testEdgeMatch_parallel(self):
        e1 = Edge("X  XXX", DIR.TOP)
        e2 = Edge(" XX   ", DIR.BOTTOM)
        self.assertTrue(e1.matches(e2))

    def testEdgeMatch_orthogonal(self):
        e1 = Edge("X  XXX", DIR.RIGHT)
        e2 = Edge("   XX ", DIR.TOP)
        self.assertTrue(e1.matches(e2))

    def testEdgeMatch_orthogonal2(self):
        e1 = Edge("X  XXX", DIR.RIGHT)
        e2 = Edge(" XX   ", DIR.BOTTOM)
        self.assertTrue(e1.matches(e2))

    def testEdgeDoesNotMatch_XvsX(self):
        e1 = Edge("XX  XX", DIR.TOP)
        e2 = Edge("  XX X", DIR.BOTTOM)
        self.assertFalse(e1.matches(e2))

    def testEdgeDoesNotMatch_SpaceVsSpace(self):
        e1 = Edge("XX  X ", DIR.TOP)
        e2 = Edge("  XX  ", DIR.BOTTOM)
        self.assertTrue(e1.matches(e2))

    def assertEqualsStripped(self, expected, actual, msg = None):
        self.assertEquals(expected.strip(), actual.strip(), msg)

    def testSideShortStr_withRotation(self):
        side = Side("bob", self.makeEdgeDict())
        self.assertEqualsStripped("bob (rot=)", side.shortStr())

        side = side.rotated(ROT.CLOCKW)
        self.assertEqualsStripped("bob (rot=-90)", side.shortStr())

        side = side.rotated(ROT.CLOCKW)
        self.assertEqualsStripped("bob (rot=180)", side.shortStr())


    def makeEdgeDict(self, *special_edge):
        edges = {}
        for d in DIR.ALL:
            edges[d] = Edge(" "*6, d)
        for edge in special_edge:
            edges[edge.direction] = edge
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

    def testHorizontalRuleMatch_cw_left(self):
        leftside = Side("left", self.makeEdgeDict(Edge("X  XXX", DIR.TOP)))
        rightside = Side("right", self.makeEdgeDict(Edge(" XX   ", DIR.LEFT)))
        rule = HorizontalRule('A', ROT.FROM_CODE['+'], 'B', ROT.NONE)
        check = rule.check(Arrangement([leftside, rightside]))
        self.assertTrue(check)

    def testHorizontalRuleMatch_ccw_right(self):
        leftside = Side("left", self.makeEdgeDict(Edge("X  XXX", DIR.RIGHT)))
        rightside = Side("right", self.makeEdgeDict(Edge("   XX ", DIR.TOP)))
        rule = HorizontalRule('A', ROT.NONE, 'B', ROT.FROM_CODE['-'])
        check = rule.check(Arrangement([leftside, rightside]))
        if not check: dump(leftside, rightside, leftside.getEdge(DIR.RIGHT), rightside.getEdge(DIR.TOP))
        self.assertTrue(check)

    def testEdgeRotation_cw(self):
        side = Side.parse("actual","""
XX    
 oooo 
 ooooX
 oooo 
 oooo 
 X X X
""".splitlines(), 6)
        rotated = side.rotated(ROT.CLOCKW)
        expected = Side.parse("expected", """
     X
XooooX
 oooo 
Xoooo 
 oooo 
X  X  
""".splitlines(), 6)
        for d in DIR.ALL:
            self.assertEquals(str(expected.getEdge(d)), str(rotated.getEdge(d)), 
                "Direction %s: %s != %s (expected)"%(d, rotated.getEdge(d), expected.getEdge(d),))

    def testEdgeRotation_deg180(self):
        side = Side.parse("actual","""
XX    
 oooo 
 ooooX
 oooo 
 oooo 
 X X X
""".splitlines(), 6)
        rotated = side.rotated(ROT.DEG180)
        expected = Side.parse("expected", """
X X X 
 oooo 
 oooo 
Xoooo 
 oooo 
    XX
""".splitlines(), 6)
        for d in DIR.ALL:
            self.assertEquals(str(expected.getEdge(d)), str(rotated.getEdge(d)), 
                "Direction %s: %s != %s (expected)"%(d, rotated.getEdge(d), expected.getEdge(d),))

    def testEdgeRotation_ccw(self):
        side = Side.parse("actual","""
XX    
 oooo 
 ooooX
 oooo 
 oooo 
 X X X
""".splitlines(), 6)
        rotated = side.rotated(ROT.COUNTER)
        expected = Side.parse("expected", """
  X  X
 oooo 
 ooooX
 oooo 
XooooX
X     
""".splitlines(), 6)
        for d in DIR.ALL:
            self.assertEquals(str(expected.getEdge(d)), str(rotated.getEdge(d)), 
                "Direction %s: %s != %s (expected)"%(d, rotated.getEdge(d), expected.getEdge(d),))

if __name__ == '__main__':
    unittest.main()
