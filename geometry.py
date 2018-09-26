import math

from . import iterable
from . import num
from . import objects


_sentinel = object()


class HasXYPositionMixin:
    """Gives the class a notion of x, y position."""
    def __init__(self, pos=None):
        self._pos = objects.Object(x=0, y=0)
        if pos is not None:
            self.pos = pos
        super(HasXYPositionMixin, self).__init__()

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        """Sets the object's current position"""
        self._pos.x = value.x
        self._pos.y = value.y

    @property
    def x(self):
        """The object's current x position."""
        return self._pos.x

    @property
    def y(self):
        """The object's current y position."""
        return self._pos.y

    @x.setter
    def x(self, val):
        self._pos.x = val

    @y.setter
    def y(self, val):
        self._pos.y = val


class HasPositionMixin:
    """Gives the class a notion of x, y, z position."""

    def __init__(self, pos=None):
        self._pos = objects.Object(x=0, y=0, z=0)
        if pos is not None:
            self.pos = pos
        super(HasPositionMixin, self).__init__()

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        """Sets the object's current position"""
        self._pos.x = value.x
        self._pos.y = value.y
        self._pos.z = value.z

    @property
    def x(self):
        """The object's current x position."""
        return self._pos.x

    @property
    def y(self):
        """The object's current y position."""
        return self._pos.y

    @x.setter
    def x(self, val):
        self._pos.x = val

    @y.setter
    def y(self, val):
        self._pos.y = val

    @property
    def z(self):
        """The object's current z position."""
        return self._pos.z

    @z.setter
    def z(self, val):
        self._pos.z = val


class _CircleMixin:
    """Provides helper functions for arcs and discs."""

    def within_disc(self, circle):
        """Determines whether this circle is entirely within another circle."""
        dist_sqr = (self.x - circle.x) ** 2 + (self.y - circle.y) ** 2
        return dist_sqr < (self.radius - circle.radius) ** 2

    def intersect_circle(self, circle):
        """Finds the intersection points between two circles. In the special cases of:
        - the circles being the same: it returns None, None, True
        - the circles don't intersect: it returns None, None, False
        Otherwise it returns P1, P2, None
        """
        # Using:
        # https://stackoverflow.com/questions/3349125/circle-circle-intersection-points
        # Who needs a maths degree when stackoverflow exists?

        dx = circle.x - self.x
        dy = circle.y - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist == 0 and self.radius == circle.radius:
            # Circles are the same
            return None, None, True
        if dist > self.radius + circle.radius:
            # Circles are too far apart
            return None, None, False
        if dist < abs(self.radius - circle.radius):
            # One circle is contained in the other
            return None, None, False

        a = (self.radius ** 2 - circle.radius ** 2 + dist ** 2) / (2 * dist)
        h = math.sqrt(self.radius ** 2 - a ** 2)

        dx_d = dx / dist
        dy_d = dy / dist

        xm = self.x + a * dx_d
        ym = self.y + a * dy_d

        hdx_d = h * dx_d
        hdy_d = h * dy_d

        p1 = objects.Object(x=xm + hdy_d, y=ym - hdx_d)
        p2 = objects.Object(x=xm - hdy_d, y=ym + hdx_d)

        return p1, p2, None


class Disc(_CircleMixin, HasXYPositionMixin):
    def __init__(self, radius, center, **kwargs):
        self.radius = radius
        super(Disc, self).__init__(pos=center, **kwargs)

    def collidepoint(self, x, y=_sentinel):
        """Determines collisions with a point."""
        if y == _sentinel:
            x, y = x.x, x.y
        return (x - self.x) ** 2 + (y - self.y) ** 2 < self.radius ** 2

    def colliderect(self, rect):
        """Determines collisions with an axis-aligned rectangle."""
        closest_x = num.clamp(self.x, min(rect.left, rect.right), max(rect.left, rect.right))
        closest_y = num.clamp(self.y, min(rect.top, rect.bottom), max(rect.top, rect.bottom))
        return self.collidepoint(closest_x, closest_y)

    def collide_disc(self, circle):
        """Determines collisions with a disc."""
        return (self.x - circle.x) ** 2 + (self.y - circle.y) ** 2 < (self.radius + circle.radius) ** 2

    def collide_arc(self, arc):
        """Determines collisions with an arc."""
        # Terminology: the circle of an arc is the circle created by extending the arc through all 360 degrees.
        #              the circle of a disc is its boundary circle.

        # A necessary condition for a collision is that their circles intersect.
        p1, p2, special = self.intersect_circle(arc)
        if special is not None:
            # If special is True then the circle of the arc is the circle of the disc. If special is False then they
            # don't intersect at all. If special is None then p1, p2 are the points of intersection.
            return special
        # Of course, an arc is smaller than its circle, so finally we need to check that the collision points are
        # actually in the arc.
        for p in (p1, p2):
            angle = math.atan2(p.y - arc.y, p.x - arc.x)
            if arc.contains(angle):
                return True
        else:
            return False

    def collide_irat(self, irat):
        """Determines collisions with an axis-aligned isosceles right-angled triangle."""
        closest_point = irat.closest_point(self.pos)
        return self.collidepoint(closest_point)


class Arc(_CircleMixin, HasXYPositionMixin):
    def __init__(self, radius, center, start_theta, end_theta, degrees=True, **kwargs):
        self.radius = radius
        mult = (math.pi / 180) if degrees else 1
        self.start_theta = (start_theta * mult) % (2 * math.pi)
        self.end_theta = (end_theta * mult) % (2 * math.pi)
        super(Arc, self).__init__(pos=center, **kwargs)

    @classmethod
    def from_disc(cls, disc, start_theta, end_theta):
        """Constructs the arc as being part of the boundary of the given disc."""
        return cls(disc.radius, disc.pos, start_theta, end_theta)

    def contains(self, angle):
        """Whether or not the angle, in radians, lies within the angle of the arc."""
        angle = angle % (2 * math.pi)
        if self.start_theta < self.end_theta:  # Arc does not contain 0
            return self.start_theta < angle < self.end_theta
        else:  # Arc does contain 0
            return self.start_theta < angle or angle < self.end_theta


class Irat:
    """Isosceles Right-Angled Triangle."""

    def __init__(self, side_length, pos, upleft=False, upright=False, downleft=False, downright=False, **kwargs):
        if not iterable.single_true((upleft, upright, downleft, downright)):
            raise TypeError('Precisely one of keyword arguments "upleft", "upright", "downleft", "downright" must be '
                            'True.')

        up = int(downleft or downright) - int(upleft or upright)
        right = int(downright or upright) - int(downleft or upleft)

        pos_two_offset = side_length * right
        pos_three_offset = side_length * up

        self.pos_one = objects.Object(x=pos.x, y=pos.y)
        self.pos_two = objects.Object(x=pos.x + pos_two_offset, y=pos.y)
        self.pos_three = objects.Object(x=pos.x, y=pos.y + pos_three_offset)
        self.upleft = upleft
        self.upright = upright
        self.downleft = downleft
        self.downright = downright
        super(Irat, self).__init__(**kwargs)

    def closest_point(self, pos):
        # First project onto the half-plane defined by the angled face of the triangle
        x_diff = pos.x - self.pos_two.x
        y_diff = pos.y - self.pos_two.y
        x_sum = pos.x + self.pos_two.x
        y_sum = pos.y + self.pos_two.y
        invariant_one = (y_diff > x_diff)
        invariant_two = (y_diff > -1 * x_diff)

        if (self.downleft and invariant_one) or (self.upright and not invariant_one):
            closest_x = 0.5 * (x_sum + y_diff)  # (pos.x + pos.y + self.pos_two.x - self.pos_two.y)
            closest_y = 0.5 * (y_sum + x_diff)  # (pos.x + pos.y - self.pos_two.x + self.pos_two.y)
        elif (self.downright and invariant_two) or (self.upleft and not invariant_two):
            closest_x = 0.5 * (x_sum - y_diff)  # (pos.x - pos.y + self.pos_two.x + self.pos_two.y)
            closest_y = 0.5 * (y_sum - x_diff)  # (-1 * pos.x + pos.y + self.pos_two.x + self.pos_two.y)
        else:
            closest_x = pos.x
            closest_y = pos.y

        # Then clamp
        closest_x = num.clamp(closest_x, min(self.pos_two.x, self.pos_one.x),
                               max(self.pos_two.x, self.pos_one.x))
        closest_y = num.clamp(closest_y, min(self.pos_three.y, self.pos_one.y),
                               max(self.pos_three.y, self.pos_one.y))
        return objects.Object(x=closest_x, y=closest_y)