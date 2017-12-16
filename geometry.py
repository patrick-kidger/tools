import Tools.helpers as helpers
import Tools.mixins as mixins


class Circle(mixins.HasXYPositionMixin):
    __sentinel = object()

    def __init__(self, radius, center):
        self.radius = radius
        super(Circle, self).__init__(pos=center)

    def collidepoint(self, x, y=__sentinel):
        # So that we can call it as self.collidepoint((x, y))
        if y == self.__sentinel:
            x, y = x
        return (x - self.x) ** 2 + (y - self.y) ** 2 < self.radius ** 2

    def colliderect(self, rect):
        closest_x = helpers.clamp(self.x, min(rect.left, rect.right), max(rect.left, rect.right))
        closest_y = helpers.clamp(self.y, min(rect.top, rect.bottom), max(rect.top, rect.bottom))
        return self.collidepoint(closest_x, closest_y)
