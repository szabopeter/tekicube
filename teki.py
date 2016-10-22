#!env python3

PLACEIDS = 'ABCDEF'

ROT_NONE = ""
ROT_CLOCKW = "-90"
ROT_COUNTER= "+90"
ROT_180DEG = "180"
ROTATIONS = ( ROT_NONE, ROT_CLOCKW, ROT_COUNTER, ROT_180DEG, )
ROTATION_FROM_CODE = { '+' : ROT_CLOCKW, '-' : ROT_COUNTER, 'r' : ROT_180DEG }
ROTATION_CODES = "".join(ROTATION_FROM_CODE.keys())
ROTATION_VALUES = {
    ROT_COUNTER: -1,
    ROT_NONE: 0,
    ROT_CLOCKW: 1,
    ROT_180DEG: 2,
    }

ROT_REV = {
    ROT_NONE: ROT_NONE,
    ROT_CLOCKW: ROT_COUNTER,
    ROT_COUNTER: ROT_CLOCKW,
    ROT_180DEG: ROT_180DEG,
    }

DIR_TOP = "TOP"
DIR_LEFT = "LEFT"
DIR_RIGHT = "RIGHT"
DIR_BOTTOM = "BOTTOM"
DIRECTIONS = ( DIR_TOP, DIR_RIGHT, DIR_BOTTOM, DIR_LEFT, )
DIR_VALUES = dict([(x[1],x[0]) for x in enumerate(DIRECTIONS)]) 

def rotate_direction(direction, rot):
    dirval = (DIR_VALUES[direction] + ROTATION_VALUES[rot])%len(DIRECTIONS)
    return DIRECTIONS[dirval]

DIR_OPS = {}
for direction in DIRECTIONS:
    DIR_OPS[direction] = {}
    for rot in ROTATIONS:
        DIR_OPS[direction][rot] = rotate_direction(direction, rot)


class Edge(object):
    def __init__(self, str_rep, direction):
        self.pixel = [ x for x in str_rep ]

    def __len__(self):
        return len(self.pixel)

    def matches(self, edge):
        for i in range(len(self.pixel)):
            if self.pixel[i] == edge.pixel[i]:
                return False
        return True

    def getDisplayChar(self, i):
        return self.pixel[i]


class Side(object):
    def __init__(self, name, edges):
       self.name = name
       self.left = edges[DIR_LEFT]
       self.right = edges[DIR_RIGHT]
       self.top = edges[DIR_TOP]
       self.bottom = edges[DIR_BOTTOM]
       #self.edges = [ self.top, self.right, self.bottom, self.left, ]
       self.edges = edges
       self.rot = ROT_NONE
       self.size = len(self.top)

    def getEdge(self, direction):
        return self.edges[DIR_OPS[direction][self.rot]]

    def rotated(self, rot):
        #TODO
        return self

    def getDisplayChar(self, x, y):
        if 0 < x < self.size-1 and 0 < y < self.size-1:
            return "O"
        if x == 0: return self.left.getDisplayChar(y)
        if y == 0: return self.top.getDisplayChar(x)
        if x == self.size-1: return self.right.getDisplayChar(y)
        if y == self.size-1: return self.bottom.getDisplayChar(x)
        return "?"
        
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
8
BC CD B+A A+D B-E ED+ FrB DFr
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
        DIR_TOP: Edge(edge_top, DIR_TOP),
        DIR_RIGHT: Edge(edge_right, DIR_RIGHT),
        DIR_BOTTOM: Edge(edge_bottom, DIR_BOTTOM),
        DIR_LEFT: Edge(edge_left, DIR_LEFT),
        }
    side = Side(name, edges)
    sides.append(side)


class Arrangement(object):
    def __init__(self, sides):
        self.sides = sides
        self.byid = {}
        for i, placeid in enumerate(PLACEIDS):
            self.byid[placeid] = i

    def getPlace(self, placeid, rot=ROT_NONE):
        return self.sides[self.byid[placeid]].rotated(rot)

    def dump(self, layout):
        def substitute(line):
            for placeid in PLACEIDS:
                line = line.replace(placeid, self.getPlace(placeid).name)
            return line
        substitution = [ substitute(line) for line in layout ]
        blocksize = len(self.sides[0].getEdge(DIR_TOP))
        outlines = [ {} for i in range(blocksize * len(layout)) ]
        for line_nr, line in enumerate(layout):
            for block_nr, placeid in enumerate(line):
                if placeid in PLACEIDS:
                    side = self.getPlace(placeid)
                    for y in range(blocksize):
                        for x in range(blocksize):
                            ch = side.getDisplayChar(x,y)
                            outlines[line_nr*blocksize+y][block_nr*blocksize+x] = ch
        def toline(chdict):
            maxpos = max(chdict.keys())
            line = [ " " for i in range(maxpos+1) ]
            for i, ch in chdict.items():
                line[i] = ch
            return "".join(line)

        for i in range(len(outlines)):
            outlines[i] = toline(outlines[i])

        return "\n".join(substitution + outlines)


class Rule(object):
    def check(self, arrangement):
        pass


class VerticalRule(Rule):
    def __init__(self, top_place, bottom_place):
        self.top = top_place
        self.bottom = bottom_place
    
    def check(self, arrangement):
        top = arrangement.getPlace(self.top)
        bottom = arrangement.getPlace(self.bottom)
        edge_from_top = top.getEdge(DIR_BOTTOM)
        edge_from_bottom = bottom.getEdge(DIR_TOP)
        return edge_from_top.matches(edge_from_bottom)
        

class HorizontalRule(Rule):
    def __init__(self, left_place, left_rot, right_place, right_rot):
        self.left, self.lrot = left_place, left_rot
        self.right, self.rrot = right_place, right_rot

    def check(self, arrangement):
        left = arrangement.getPlace(self.left, self.lrot)
        right = arrangement.getPlace(self.right, self.rrot)
        edge_from_left = left.getEdge(DIR_RIGHT)
        edge_from_right = right.getEdge(DIR_LEFT)
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
        left_rot = ROT_NONE
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
        right_rot = ROT_NONE
        endindex = right_start

    rules.append(HorizontalRule(left_place, left_rot, right_place, right_rot))
    #print("Horizontal rule: %s[%s] - %s[%s]"%(left_place, left_rot, right_place, right_rot, ))

print_layout = []
line = get_line()
while line:
    print_layout.append(line)
    line = get_line()

arr = Arrangement(sides)
print(arr.dump(print_layout))
