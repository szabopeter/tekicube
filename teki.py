#!env python3

import itertools

PLACEIDS = 'ABCDEF'

class ROT(object):
    def __init__(self, code): self.code = code

ROT.NONE = ROT("")
ROT.CLOCKW = ROT("-90")
ROT.COUNTER = ROT("+90")
ROT.DEG180 = ROT("180")

ROT.ALL = ( ROT.NONE, ROT.CLOCKW, ROT.DEG180, ROT.COUNTER, )
ROT.SINGLE = ( ROT.NONE, )
ROTATION_FROM_CODE = { '+' : ROT.CLOCKW, '-' : ROT.COUNTER, 'r' : ROT.DEG180 }
ROTATION_CODES = "".join(ROTATION_FROM_CODE.keys())
ROT.VALUES = {
    ROT.COUNTER: -1,
    ROT.NONE: 0,
    ROT.CLOCKW: 1,
    ROT.DEG180: 2,
    }

ROT.REV = {
    ROT.NONE: ROT.NONE,
    ROT.CLOCKW: ROT.COUNTER,
    ROT.COUNTER: ROT.CLOCKW,
    ROT.DEG180: ROT.DEG180,
    }

ROT.NEXT = {}
prevrot = ROT.ALL[-1]
for rot in ROT.ALL:
    ROT.NEXT[prevrot] = rot
    prevrot = rot

class DIR(object):
    def __init__(self, code): self.code = code

DIR.TOP = "TOP"
DIR.LEFT = "LEFT"
DIR.RIGHT = "RIGHT"
DIR.BOTTOM = "BOTTOM"

DIR.ALL = ( DIR.TOP, DIR.RIGHT, DIR.BOTTOM, DIR.LEFT, )
DIR.VALUES = dict([(x[1],x[0]) for x in enumerate(DIR.ALL)]) 

def rotate_direction(direction, rot):
    dirval = (DIR.VALUES[direction] + ROT.VALUES[rot])%len(DIR.ALL)
    return DIR.ALL[dirval]

DIR.OPS = {}
for direction in DIR.ALL:
    DIR.OPS[direction] = {}
    for rot in ROT.ALL:
        DIR.OPS[direction][rot] = rotate_direction(direction, rot)

#in the order of DIR.ALL on both axes
EDGE_TRANSITION_MATRIX_RAW = """
++--
++--
--++
--++
"""
EDGE_TRANSITION_STEP = { '-' : -1, '+': +1, }
EDGE_TRANSITION_MATRIX_RAW = [ [ EDGE_TRANSITION_STEP[ch] for ch in line.strip()] for line in EDGE_TRANSITION_MATRIX_RAW.splitlines() if line ]
EDGE_TRANSITION_MATRIX = {}
for col,d1 in enumerate(DIR.ALL):
    EDGE_TRANSITION_MATRIX[d1] = {}
    for row,d2 in enumerate(DIR.ALL):
        EDGE_TRANSITION_MATRIX[d1][d2] = EDGE_TRANSITION_MATRIX_RAW[col][row]
        
class Edge(object):
    def __init__(self, str_rep, direction):
        self.pixel = [ x for x in str_rep ]
        self.direction = direction

    def __len__(self):
        return len(self.pixel)

    def matches(self, edge):
        for i in range(len(self.pixel)):
            if self.pixel[i] == edge.pixel[i]:
                return False
        return True

    def clone(self):
        return Edge(self.pixel, self.direction)

    def getDisplayChar(self, i):
        return self.pixel[i]

    def __str__(self):
        return "".join(self.pixel)

    def __repr__(self):
        return str(self)

class Side(object):
    def __init__(self, name, edges):
       self.name = name
       self.left = edges[DIR.LEFT]
       self.right = edges[DIR.RIGHT]
       self.top = edges[DIR.TOP]
       self.bottom = edges[DIR.BOTTOM]
       #self.edges = [ self.top, self.right, self.bottom, self.left, ]
       self.edges = edges
       self.rot = ROT.NONE
       self.size = len(self.top)

    def getEdge(self, direction):
        return self.edges[DIR.OPS[direction][self.rot]]

    def rotated(self, target_rot):
        rot = ROT.NONE
        edge_clones = [ edge.clone() for edge in self.edges.values() ]

        while rot != target_rot:
            new_edges = []
            for edge in edge_clones:
                newdir = DIR.OPS[edge.direction][ROT.CLOCKW]
                transition = EDGE_TRANSITION_MATRIX[edge.direction][newdir]
                newedge = Edge(edge.pixel[::transition], newdir)
                new_edges.append(newedge)
            edge_clones = new_edges
            rot = ROT.NEXT[rot]
        edgeclones = dict( [ (edge.direction, edge) for edge in edge_clones ] )
        #print("Old edges: %s"%self.edges)
        #print("New edges: %s"%edgeclones)
        clone = Side(self.name, edgeclones)
        clone.rot = target_rot
        return clone

    def getDisplayChar(self, x, y):
        if 0 < x < self.size-1 and 0 < y < self.size-1:
            return "O"
        if x == 0: return self.left.getDisplayChar(y)
        if y == 0: return self.top.getDisplayChar(x)
        if x == self.size-1: return self.right.getDisplayChar(y)
        if y == self.size-1: return self.bottom.getDisplayChar(x)
        return "?"

    def __str__(self):
        lines = [self.shortStr()]
        for y in range(self.size):
            line = [ self.getDisplayChar(x,y) for x in range(self.size) ]
            lines.append("".join(line))
        return "\n".join(lines)

    shortStrWidth = 15
    def shortStr(self):
        return ("Side %s (rot=%s):"%(self.name, self.rot,)).ljust(Side.shortStrWidth)
        
simpleHRules = """
2
BC CD
"""
allHRules = """
8
BC CD B+A A+D B-E ED+ FrB DFr
"""

raw = """
6 6
1
X XX X
XXXXXX
 XXXX
 XXXX
XXXXXX
  XX  
2
  XX
 XXXX
XXXXXX
XXXXXX
 XXXX
  XX
3
 X  X
 XXXXX
XXXXX
XXXXX
 XXXXX
  XX
4
 X  X
 XXXXX
XXXXX
XXXXX
 XXXXX
XX  XX
5
XX  X
 XXXX
XXXXXX
XXXXXX
 XXXX
 X  X
6
XX  XX
XXXXX
 XXXXX
 XXXXX
XXXXX
XX  X
4
A C E F
C E F A
""" + simpleHRules + """ 
 A
BCD
 E
 F
"""

def linefeed_generator():
    for line in raw.splitlines():
        if not line: continue
        yield line

linefeeder = linefeed_generator()
def get_line(): 
    try:
        return next(linefeeder)
    except StopIteration:
        return None

sidecount,edgesize = [ int(x) for x in get_line().split() ]
sides = []
for i in range(sidecount):
    name = get_line()
    lines = [ get_line().ljust(edgesize) for j in range(edgesize) ]
    edge_top = [ lines[0][x] for x in range(edgesize) ]
    edge_bottom = [ lines[-1][x] for x in range(edgesize) ]
    edge_left = [ lines[x][0] for x in range(edgesize) ]
    edge_right = [ lines[x][-1] for x in range(edgesize) ]
    edges = { 
        DIR.TOP: Edge(edge_top, DIR.TOP),
        DIR.RIGHT: Edge(edge_right, DIR.RIGHT),
        DIR.BOTTOM: Edge(edge_bottom, DIR.BOTTOM),
        DIR.LEFT: Edge(edge_left, DIR.LEFT),
        }
    side = Side(name, edges)
    sides.append(side)


class Arrangement(object):
    def __init__(self, sides):
        self.sides = sides
        self.byid = {}
        for i, placeid in enumerate(PLACEIDS):
            self.byid[placeid] = i
        #print("Arrangement created: "+("-".join([side.name+side.rot for side in sides])))

    def __str__(self):
        return " ".join([side.name+side.rot for side in sides])

    def getPlace(self, placeid, rot=ROT.NONE):
        return self.sides[self.byid[placeid]].rotated(rot)

    def dump(self, layout):
        substDict = {" ": ' '*Side.shortStrWidth}
        for placeid in PLACEIDS:
            substDict[placeid] = self.getPlace(placeid).shortStr()
        substitution = [ "".join([ substDict[ch] for ch in line]) for line in layout ]
        blocksize = len(self.sides[0].getEdge(DIR.TOP))
        outlines = [ {} for i in range((blocksize+1) * len(layout)) ]
        for line_nr, line in enumerate(layout):
            for block_nr, placeid in enumerate(line):
                if placeid in PLACEIDS:
                    side = self.getPlace(placeid)
                    for y in range(blocksize):
                        for x in range(blocksize):
                            ch = side.getDisplayChar(x,y)
                            outlines[line_nr*(blocksize+1)+y][block_nr*(blocksize+1)+x] = ch

        def toline(chdict):
            if not chdict:
                return ""
            maxpos = max(chdict.keys())
            line = [ " " for i in range(maxpos+1) ]
            for i, ch in chdict.items():
                line[i] = ch
            return "".join(line)

        for i in range(len(outlines)):
            outlines[i] = toline(outlines[i])

        return "\n".join(substitution + outlines)

    def check(self, rules, no_compromises = False):
        violations = []
        score = 0
        for rule in rules:
            if not rule.check(self):
                violations.append(rule)
                if no_compromises:
                    break
            else:
                score += 1
        return violations, score


class Rule(object):
    def check(self, arrangement):
        pass


class VerticalRule(Rule):
    def __init__(self, top_place, bottom_place):
        self.top = top_place
        self.bottom = bottom_place

    def __str__(self):
        return "V %s %s"%(self.top, self.bottom,)
    
    def check(self, arrangement):
        top = arrangement.getPlace(self.top)
        bottom = arrangement.getPlace(self.bottom)
        edge_from_top = top.getEdge(DIR.BOTTOM)
        edge_from_bottom = bottom.getEdge(DIR.TOP)
        return edge_from_top.matches(edge_from_bottom)
        

class HorizontalRule(Rule):
    def __init__(self, left_place, left_rot, right_place, right_rot):
        self.left, self.lrot = left_place, left_rot
        self.right, self.rrot = right_place, right_rot

    def __str__(self):
        return "H %s %s"%(self.left, self.right,)

    def check(self, arrangement):
        left = arrangement.getPlace(self.left, self.lrot)
        right = arrangement.getPlace(self.right, self.rrot)
        edge_from_left = left.getEdge(DIR.RIGHT)
        edge_from_right = right.getEdge(DIR.LEFT)
        return edge_from_left.matches(edge_from_right)


rules = []

vertical_rule_count = int(get_line())
vertical_top = get_line().split()
vertical_bottom = get_line().split()
for i in range(vertical_rule_count):
    top_place = vertical_top[i]
    bottom_place = vertical_bottom[i]
    rules.append(VerticalRule(top_place, bottom_place))

horizontal_rule_count = int(get_line())
for rulestr in get_line().split():
    left_place = rulestr[0]
    if rulestr[1] in PLACEIDS:
        left_rot = ROT.NONE
        right_start = 1
        
    elif rulestr[1] in ROTATION_CODES:
        left_rot = ROTATION_FROM_CODE[rulestr[1]]
        right_start = 2
    else:
        print("Invalid rule specification: " + rulestr)
        sys.exit(1)

    right_place = rulestr[right_start]
    if right_start+1 < len(rulestr) and rulestr[right_start+1] in ROTATION_CODES:
        right_rot = ROTATION_FROM_CODE[rulestr[right_start+1]]
        endindex = right_start+2
    else:
        right_rot = ROT.NONE
        endindex = right_start

    rules.append(HorizontalRule(left_place, left_rot, right_place, right_rot))
    #print("Horizontal rule: %s[%s] - %s[%s]"%(left_place, left_rot, right_place, right_rot, ))

print_layout = []
line = get_line()
while line:
    print_layout.append(line)
    line = get_line()

def arrangement_generation(original_sides):
    siderefs = range(len(original_sides))
    for sidepermutation in itertools.permutations(siderefs):
        if sidepermutation[0] != 0:
            continue # let's fix one side
        #for rotations in itertools.product(ROT.SINGLE, ROT.ALL, ROT.ALL, ROT.ALL, ROT.ALL, ROT.ALL):
        for rotations in itertools.product(ROT.SINGLE, ROT.SINGLE, ROT.SINGLE, ROT.SINGLE, ROT.SINGLE, ROT.SINGLE):
            sides = [ original_sides[i].rotated(rotations[i]) for i in sidepermutation ]
            yield Arrangement(sides)

if __name__ == '__main__':
    #limit = 8
    limit = 9999
    best_score = -1
    best_arrangement = None
    for arr in arrangement_generation(sides):
        check = arr.check(rules, True)
        violations, score = check 
        #if violations:
        #    print("Arrangement %s scored %d, failed rule check %s"%(arr, score, violations,))
        if score > best_score:
            best_score, best_arrangement = score, arr
        limit -= 1
        if limit <= 0: break

    print("Best score: %d"%best_score)
    print(best_arrangement.dump(print_layout))

