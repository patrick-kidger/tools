import Tools.objects as objects


# Adapted from
# http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm
def line(start, end, endpoints=True):
    """Bresenham's Line Algorithm
    Produces a list of Objects from start and end
 
    >>> points1 = line(Object(x=0, y=0), Object(x=3, y=4))
    >>> points2 = line(Object(x=3, y=4), Object(x=0, y=0))
    >>> assert(set(points1) == set(points2))
    >>> print points1
    [{'x': 0, 'y': 0}, {'x': 1, 'y': 1}, {'x': 1, 'y': 1}, {'x': 2, 'y': 3}, {'x': 3, 'y': 4}]
    >>> print points2
    [{'x': 3, 'y': 4}, {'x': 2, 'y': 3}, {'x': 1, 'y': 1}, {'x': 1, 'y': 1}, {'x': 0, 'y': 0}]
    """
    # Setup initial conditions
    x1, y1 = start.x, start.y
    x2, y2 = end.x, end.y
    dx = x2 - x1
    dy = y2 - y1
    offset = 0 if endpoints else 1
 
    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)
 
    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
 
    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True
 
    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1
 
    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1
 
    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1 + offset, x2 + 1 - offset):
        coord = (y, x) if is_steep else (x, y)
        points.append(objects.Object(x=coord[0], y=coord[1]))
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx
 
    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points