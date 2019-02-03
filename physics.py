"""
Custom physics engine that take care only of AABBs.

Maybe one day it'll get bigger.
"""

from math import cos, sin, pi, sqrt
from typing import List, TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from level import Level


def clamp(x, mini=float('-inf'), maxi=float('inf')):
    if maxi < mini:
        return x
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x


class Pos:
    """A vector."""

    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        self.x = args[0]
        self.y = args[1]

    def __len__(self):
        return 2

    def __iter__(self):
        yield self.x
        yield self.y

    def __bool__(self):
        return bool(self.x and self.y)

    def __eq__(self, other):
        return self.x == other[0] and self.y == other[1]

    def __repr__(self):
        return f"Pos({round(self.x, 3)}, {round(self.y, 3)})"

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        raise IndexError(f"Pos has no item {item}")

    def __add__(self, other):
        return Pos(self[0] + other[0], self[1] + other[1])

    def __radd__(self, other):
        return Pos(self.x + other[0], self.y + other[1])

    def __sub__(self, other):
        return Pos(self[0] - other[0], self[1] - other[1])

    def __rsub__(self, other):
        return Pos(other[0] - self[0], other[1] - self[1])

    def __neg__(self):
        return Pos(-self[0], -self[1])

    def __mul__(self, other):
        return Pos(self[0] * other, self[1] * other)

    def __rmul__(self, other):
        return Pos(self.x * other, self.y * other)

    def __truediv__(self, other: float):
        return Pos(self[0] / other, self[1] / other)

    def __floordiv__(self, other: float):
        return Pos(self[0] // other, self[1] // other)

    @property
    def t(self):
        """The vector as a tuple"""
        return self[0], self[1]

    @property
    def ti(self):
        """The vector as a tuple of integer (round to closest)"""
        return round(self[0]), round(self[1])

    @property
    def i(self):
        """The vector as an integer Pos (round to closest)"""
        return Pos(round(self[0]), round(self[1]))

    def squared_norm(self):
        """Return the squared norm of the vector"""
        return self[0] ** 2 + self[1] ** 2

    def norm(self):
        """Return the norm of the vector"""
        return sqrt(self.squared_norm())

    def normalise(self):
        return self / self.norm()

    def rotate(self, degree):
        c = cos(pi / 180 * degree)
        s = sin(pi / 180 * degree)
        return Pos(c * self[0] + s * self[1],
                   s * self[0] - c * self[1])

    def copy(self):
        return Pos(self.x, self.y)

    @property
    def horizontal(self):
        return Pos(self.x, 0)

    @property
    def vertical(self):
        return Pos(0, self.y)

    @staticmethod
    def unit_x():
        return Pos(1, 0)

    @staticmethod
    def unit_y():
        return Pos(0, 1)

    def debug_draw(self, surf, offset=(0, 0), start=(0, 0), color=(255, 0, 0)):
        start = Pos(start) + offset
        end = start + self
        pygame.draw.line(surf, color, start, end)


class AABB:
    """Axis aligned rectangle: the basic shape."""

    def __init__(self, *args):
        """Create a axis aligned rectangle. Args a in the same style as pygame.Rect args."""
        if len(args) == 1:
            args = args[0]

        if isinstance(args, (pygame.rect.RectType, AABB)):
            tl = args.topleft
            s = args.size
        elif len(args) == 0:
            tl = 0, 0
            s = 0, 0
        elif len(args) == 2:
            tl = args[0]
            s = args[1]
        elif len(args) == 4:
            tl = args[:2]
            s = args[2:]
        else:
            raise TypeError(f"Arguments are not in a rect style: {args}")

        self.topleft = Pos(tl)
        self.size = Pos(s)

    def __repr__(self):
        return f"<AABB({self.x}, {self.y}, {self.size.x}, {self.size.y})>"

    def collide(self, other):
        return self.collide_aabb(other)

    def collide_aabb(self, other):
        """
        Check this collides with an AABB.

        Rects do collide even if they have only an edge in common.
        This is different that the pygame.colliderect function.
        So an AABB(0, 0, 4, 4) and AABB(0, 4, 4, 4) will not collide.

        :type other: AABB
        """

        # the collide in 2D if they collide on both axis
        if self.right <= other.left or other.right <= self.left:
            return False
        if self.bottom <= other.top or other.bottom <= self.top:
            # the condition is the way because the y axis is inverted
            return False

        return True

    @property
    def center(self):
        return self.topleft + self.half_size

    @center.setter
    def center(self, value):
        self.topleft = Pos(value) - self.half_size

    @property
    def half_size(self):
        return self.size / 2

    @property
    def left(self):
        return self.topleft.x

    @left.setter
    def left(self, value):
        self.topleft.x = value

    x = left

    @property
    def right(self):
        return self.topleft.x + self.size.x

    @right.setter
    def right(self, value):
        self.topleft.x = value - self.size.x

    @property
    def bottom(self):
        return self.topleft.y + self.size.y

    @bottom.setter
    def bottom(self, value):
        self.topleft.y = value - self.size.y

    @property
    def top(self):
        return self.topleft.y

    @top.setter
    def top(self, value):
        self.topleft.y = value

    y = top

    @property
    def pygame_rect(self):
        return pygame.Rect(self.topleft, self.size)

    def debug_draw(self, surf, offset=(0, 0)):
        rect = self.pygame_rect
        rect.topleft += offset
        surf.fill((0, 0, 255), rect)


class AASegment(AABB):
    def __init__(self, start, end, pos, vertical=False):
        """
        The start and end position are the x or y coordinate depending wheter the segment is vertical or not.
        pos is the other (shared) coordinate.
        """

        self.vertical = vertical
        if self.vertical:
            super().__init__((pos, min(start, end)), (1, abs(start - end)))
        else:
            super().__init__((min(start, end), pos), (abs(start - end), 1))


class Body:
    """A moving object."""

    def __init__(self, shape, mass=1, elasticity=0, max_velocity=(None, None), space=None):

        self.dead = False
        self.elasticity = elasticity
        self.mass = mass
        self.shape = shape  # type: AABB
        self.space = space  # type: Space

        self.velocity = Pos(0, 0)
        self.max_velocity = Pos(max_velocity)
        self.acceleration = Pos(0, 0)

        self.collide_left = False
        self.collide_down = False
        self.collide_right = False
        self.collide_top = False

        self.last_collide_left = 0
        self.last_collide_down = 0
        self.last_collide_right = 0
        self.last_collide_top = 0

        self.collisions = []

    def __repr__(self):
        return f"<Body: s {self.shape}, v {self.velocity}, a {self.acceleration}>"

    @property
    def topleft(self):
        return self.shape.topleft

    @property
    def center(self):
        return self.shape.center

    @center.setter
    def center(self, value):
        self.shape.center = value

    def update_x(self, tiles):
        """Updates the position on the x coordinate and check for collision with the shapes."""

        self.velocity.x += self.acceleration.x
        self.clamp_speed()
        self.shape.x += self.velocity.x

        intersect = [s for s in tiles if self.shape.collide(s)]

        if self.velocity.x > 0:
            # we are going right
            for aabb in intersect:
                if aabb.left < self.shape.right:
                    self.shape.right = aabb.left
                    self.velocity.x *= -self.elasticity
                    self.collisions.append(tiles[aabb])
        elif self.velocity.x < 0:
            # we are going left
            for aabb in intersect:
                if self.shape.left < aabb.right:
                    self.shape.left = aabb.right
                    self.velocity.x *= -self.elasticity
                    self.collisions.append(tiles[aabb])

        self.acceleration.x = 0

    def update_y(self, tiles):
        self.velocity.y += self.acceleration.y
        self.clamp_speed()
        self.shape.y += self.velocity.y

        intersect = [s for s in tiles if self.shape.collide(s)]

        if self.velocity.y > 0:
            # we are going down
            for aabb in intersect:
                if self.shape.bottom > aabb.top:
                    self.shape.bottom = aabb.top
                    self.velocity.y *= -self.elasticity
                    self.collisions.append(tiles[aabb])
        elif self.velocity.y < 0:
            # we are going up
            for aabb in intersect:
                if aabb.bottom > self.shape.top:
                    self.shape.top = aabb.bottom
                    self.velocity.y *= -self.elasticity
                    self.collisions.append(tiles[aabb])

        self.acceleration.y = 0

    def check_collisions(self, projectiles):
        for proj in projectiles:
            if self.shape.collide(proj.shape):
                self.collisions.append(proj)

    def clamp_speed(self):
        if self.max_velocity.x is not None:
            self.velocity.x = clamp(self.velocity.x, -self.max_velocity.x, self.max_velocity.x)
        if self.max_velocity.y is not None:
            self.velocity.y = clamp(self.velocity.y, -self.max_velocity.y, self.max_velocity.y)

    def apply_force(self, force=(0, 0)):
        """
        Apply of force respecting the mass of the object.

        If the object has no mass, just add the force to the acceleration.
        """

        if self.mass == 0:
            self.acceleration += force
        else:
            self.acceleration += Pos(force) / self.mass

    def update_sensors(self, shapes):
        left = AASegment(self.shape.top, self.shape.bottom, self.shape.left - 1, vertical=True)
        right = AASegment(self.shape.top, self.shape.bottom, self.shape.right + 1, vertical=True)
        top = AASegment(self.shape.left, self.shape.right, self.shape.top - 1, vertical=False)
        bottom = AASegment(self.shape.left, self.shape.right, self.shape.bottom + 1, vertical=False)

        self.collide_left = any(left.collide(s) for s in shapes)
        self.collide_right = any(right.collide(s) for s in shapes)
        self.collide_down = any(bottom.collide(s) for s in shapes)
        self.collide_top = any(top.collide(s) for s in shapes)

    def update_history(self):
        self.last_collide_top += 1
        self.last_collide_down += 1
        self.last_collide_left += 1
        self.last_collide_right += 1

        if self.collide_top:
            self.last_collide_top = 0
        if self.collide_down:
            self.last_collide_down = 0
        if self.collide_left:
            self.last_collide_left = 0
        if self.collide_right:
            self.last_collide_right = 0

    def internal_logic(self):
        """Called once per simulation turn."""

        pass

    def render(self, surf, offset=(0, 0)):
        pass

    def debug_draw(self, surf, offset=(0, 0)):
        self.shape.debug_draw(surf, offset)
        (10 * self.velocity).debug_draw(surf, offset, self.center)


class Projectile(Body):
    """
    Not necessarily a bullet, but any collectible/brochette...

    A projectile isn't moved when there is a collision with the player, nor the player does.
    (at least, not automatically)
    """

    def update_sensors(self, shapes):
        # don't care about sensors
        pass


class Space:
    def __init__(self, tile_map=None, gravity=(0, 0)):
        self.projectiles = []  # type: List[Projectile]
        self.tile_map = tile_map  # type: Level
        self.gravity = Pos(gravity)
        self.static_bodies = []  # type: List[AABB]
        self.moving_bodies = []  # type: List[Body]

    def add(self, *bodies):
        for body in bodies:
            if isinstance(body, Projectile):
                self.projectiles.append(body)
            elif isinstance(body, Body):
                self.moving_bodies.append(body)
            else:
                self.static_bodies.append(body)
            body.space = self

    def possible_collision_for(self, body):
        tl = self.tile_map.world_to_map(body.topleft)
        br = self.tile_map.world_to_map(body.topleft + body.shape.size)
        d = {}
        for x in range(tl[0] - 1, br[0] + 2):
            for y in range(tl[1] - 1, br[1] + 2):
                block = self.tile_map.get_block((x, y))
                if block.solid:
                    rect = AABB(self.tile_map.get_block_world_rect((x, y)))
                    d[rect] = block
        return d

    def simulate(self):

        # first we update/move all projectiles
        for proj in self.projectiles[:]:
            proj.internal_logic()
            if proj.dead:
                self.projectiles.remove(proj)
            else:
                proj.collisions.clear()
                if proj.mass:
                    proj.apply_force(self.gravity)
                proj.update_x(self.possible_collision_for(proj))
                proj.update_y(self.possible_collision_for(proj))

        for body in self.moving_bodies[:]:
            body.internal_logic()
            if body.dead:
                self.moving_bodies.remove(body)
            else:
                body.collisions.clear()
                if body.mass:
                    body.apply_force(self.gravity)

                # check collision horizontally
                # we don't do both at the same time because it simplifies A LOT the thing
                # plus it's accurate enough
                body.update_x(self.possible_collision_for(body))
                body.update_y(self.possible_collision_for(body))

                # we check for collisions with projectiles
                body.check_collisions(self.projectiles)

                # Finally we check if we are grounded/against a wall...
                body.update_sensors(self.possible_collision_for(body))
                body.update_history()

    def debug_draw(self, surf, offset=(0, 0)):
        for body in self.moving_bodies + self.projectiles:
            body.debug_draw(surf, offset)