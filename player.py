import os
from enum import Enum, auto

import pygame

from blocks import Block
from config import CONFIG, PLAYERS
from constants import PLAYER_FOLDER
from entities import AK47
from physics import Body, AABB, Pos, CollisionType

LEFT = 0
RIGHT = 1
WALK_FORCE = 1
RUN_FORCE = 2
FEET_FRICTION = 0.1
FRAMES_TO_STILL = 2
JUMP_FORCE = 10
WALL_JUMP_FORCE = 30
WALL_JUMP_ANGLE = 60
INPUT_TOLERANCE = 2
JUMP_GRAVITY_FACTOR = 0.7
WALL_SLIDE_GRAVITY = 0.8
WALL_SLIDE_FRICTION = 0.01
MAX_WALL_VELOCITY = 5
WALL_STIKY_FRAMES = 15


class State(Enum):
    STILL = auto()
    WALK = auto()
    RUN = auto()
    JUMP = auto()
    FALL = auto()
    WALL_SLIDE = auto()
    WALL_JUMP = auto()
    OUT_OF_WALL_SLIDE = auto()


class Player(Body):
    def __init__(self, start_pos=(0, 0), respawn=False):
        size = (76 * 3 // 4, 70 * 3 // 4)
        shape = AABB(start_pos, size)
        super().__init__(shape, max_velocity=(16, 16))
        self.visible = True

        self.img = pygame.image.load(os.path.join(PLAYER_FOLDER, PLAYERS[CONFIG.player][0])).convert()
        self.img.set_colorkey((255, 0, 255))
        self.img = pygame.transform.scale(self.img, size)
        self.img_left = pygame.transform.flip(self.img, True, False)

        self.directions = [False, False]  # [Left, Right]
        self.jumping = False
        self.just_jumped = False
        self.looking = RIGHT
        self.run = False
        self.state = State.STILL
        self.state_duration = 0
        self.respawn = 50 if respawn else 0
        self.ak47 = False

    def render(self, surf, offset=(0, 0)):
        if not self.visible:
            return

        if self.looking == RIGHT:
            img = self.img
        else:
            img = self.img_left

        surf.blit(img, self.topleft + offset)

        if self.ak47:
            ak47_img = AK47.get_img(self.looking == RIGHT)

            y = self.shape.center.y + ak47_img.get_height() // 2
            if self.looking == LEFT:
                pos = (self.shape.left, y)
            else:
                pos = (self.shape.right - ak47_img.get_width(), y)
            surf.blit(ak47_img, pos + offset)

    def update(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == CONFIG.bindings.left:
                self.directions[LEFT] = True
            elif event.key == CONFIG.bindings.right:
                self.directions[RIGHT] = True
            elif event.key == CONFIG.bindings.jump:
                if self.collide_right or self.collide_left or self.collide_down:
                    self.jumping = True
                    self.just_jumped = True
            elif event.key == CONFIG.bindings.run:
                self.run = True

        elif event.type == pygame.KEYUP:
            if event.key == CONFIG.bindings.left:
                self.directions[LEFT] = False
            elif event.key == CONFIG.bindings.right:
                self.directions[RIGHT] = False
            elif event.key == CONFIG.bindings.jump:
                self.jumping = False
            elif event.key == CONFIG.bindings.run:
                self.run = False

    def internal_logic(self):
        if self.respawn > 0:
            self.visible = not self.visible
            self.respawn -= 1
        elif self.respawn == 0:
            self.visible = True

        new_state = self.get_state()
        if self.state == new_state:
            self.state_duration += 1
        else:
            self.state_duration = 0

        self.state = new_state

        self.vertical_logic()
        self.horizontal_logic()

        self.just_jumped = False
        if self.velocity.x < 0:
            self.looking = LEFT
        elif self.velocity.x > 0:
            self.looking = RIGHT

        self.handle_collisions()

    def get_state(self):
        if self.collide_down:
            # on the ground
            if self.just_jumped:
                # Jumping against a wall
                if self.last_collide_left < INPUT_TOLERANCE or self.last_collide_right < INPUT_TOLERANCE:
                    return State.WALL_SLIDE
                else:
                    return State.JUMP
            else:
                if self.directions[LEFT] == self.directions[RIGHT]:
                    return State.STILL
                elif self.run:
                    return State.RUN
                else:
                    return State.WALK
        else:
            if self.last_collide_left < INPUT_TOLERANCE or self.last_collide_right < INPUT_TOLERANCE:
                # against a wall
                if self.just_jumped:
                    return State.WALL_JUMP
                elif self.last_collide_left < INPUT_TOLERANCE and self.directions[RIGHT]:
                    return State.OUT_OF_WALL_SLIDE
                elif self.last_collide_right < INPUT_TOLERANCE and self.directions[LEFT]:
                    return State.OUT_OF_WALL_SLIDE
                else:
                    return State.WALL_SLIDE
            else:
                # not against a wall
                if self.jumping and self.velocity.y < 0:
                    return State.JUMP
                else:
                    return State.FALL

    def vertical_logic(self):
        if self.state in (State.STILL, State.WALK, State.RUN):
            pass  # no vertical movement apart from gravity
        elif self.state_duration is State.FALL:
            pass
        elif self.state is State.JUMP:
            if self.just_jumped:
                self.apply_force((0, -JUMP_FORCE))
            else:
                self.apply_force(-JUMP_GRAVITY_FACTOR * self.space.gravity.vertical)

        elif self.state in (State.WALL_SLIDE, State.OUT_OF_WALL_SLIDE):
            # jump boost
            if self.just_jumped:
                self.apply_force((0, -JUMP_FORCE))
            else:
                self.apply_force(-WALL_SLIDE_GRAVITY * self.space.gravity.vertical)
        elif self.state is State.WALL_JUMP:
            self.apply_force((0, -JUMP_FORCE))

    def horizontal_logic(self):
        direc = -self.directions[0] + self.directions[1]

        if self.state is State.STILL:
            # we want to stop quickly
            self.apply_force(-self.velocity.horizontal / FRAMES_TO_STILL )
        elif self.state in (State.WALK, State.RUN):
            # Walk/Run force
            force = RUN_FORCE if self.state is State.RUN else WALK_FORCE
            self.apply_force((direc * force, 0))
            # feet friction (aka max speed)
            self.apply_force(-FEET_FRICTION * self.velocity.horizontal)
        elif self.state in (State.FALL, State.JUMP):
            # no forces if we don't press l/r key aka constant speed
            if direc:
                force = RUN_FORCE if self.state is State.RUN else WALK_FORCE
                self.apply_force((direc * force, 0))
                self.apply_force(-FEET_FRICTION * self.velocity.horizontal)
            else:
                if abs(self.velocity.x) > WALK_FORCE/FEET_FRICTION:
                    self.apply_force(-FEET_FRICTION * self.velocity.horizontal)

        elif self.state == State.WALL_SLIDE:
            # nothing to do, we are against the wall
            pass
        elif self.state == State.WALL_JUMP:
            if self.collide_right:
                direc = -1
            else:
                direc = 1
            self.velocity = Pos(0, 0)
            self.apply_force((direc * JUMP_FORCE * (self.run * 0.5  + 1), 0))
        elif self.state is State.OUT_OF_WALL_SLIDE:
            # The wall is sticky
            if self.state_duration < WALL_STIKY_FRAMES:
                pass
            else:
                # Walk/Run force
                force = RUN_FORCE if self.state is State.RUN else WALK_FORCE
                self.apply_force((direc * force, 0))
                # feet friction (aka max speed)
                self.apply_force(-FEET_FRICTION * self.velocity.horizontal)

    def handle_collisions(self):
        for colli in self.collisions:
            if colli.type == CollisionType.PROJECTILE:
                proj = colli.object
                if proj.deadly:
                    self.space.tile_map.reset()
                if isinstance(proj, AK47):
                    self.ak47 = True
                    CONFIG.levels_stats[str(self.space.tile_map.num)][2] = 1
                    proj.dead = True  # we picked it up
            if colli.type is CollisionType.BLOCK:
                block = colli.object
                assert isinstance(block, Block)
                if block.deadly:
                    self.space.tile_map.reset()
                elif block.character == 'E':
                    self.space.tile_map.explode(block.pos)
