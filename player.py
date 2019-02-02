import pygame 

from physics import Body, AABB

LEFT = 0
RIGHT = 1
WALK_SPEED = 4
JUMP_FORCE = 10

class Player(Body):
    def __init__(self, start_pos=(0, 0)):
        shape = AABB(start_pos, (38, 35))
        super().__init__(shape)

        self.img = pygame.image.load('assets/player/lama.png').convert()
        self.img.set_colorkey((255, 255, 255))

        self.directions = [False, False]  # [Left, Right]
        self.jumping = False
        self.was_jumping = False

    def render(self, surf, offset=(0, 0)):
        surf.blit(self.img, self.topleft + offset)

    def update(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.directions[LEFT] = True
            elif event.key == pygame.K_RIGHT:
                self.directions[RIGHT] = True
            elif event.key == pygame.K_UP:
                self.jumping = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.directions[LEFT] = False
            elif event.key == pygame.K_RIGHT:
                self.directions[RIGHT] = False
            elif event.key == pygame.K_UP:
                self.jumping = False

    def internal_logic(self):
        self.vertical_logic()
        self.horizontal_logic()

        self.was_jumping = self.jumping

    def vertical_logic(self):
        # player starts jumping from the ground
        if self.jumping and not self.was_jumping and self.collide_down:
            self.apply_force((0, -JUMP_FORCE))

        if self.jumping and self.velocity.y < 0:
            # jumping in upward phase
            self.apply_force(-self.space.gravity * 0.6)
        elif self.jumping and self.velocity.y > 0:
            # hovering down when jump is still pressed
            self.apply_force(-self.space.gravity * 0.2)
        elif not self.jumping and self.velocity.y < 0:
            # still going up but not jumping, we want to go down as fast as we can
            self.apply_force(self.space.gravity)



    def horizontal_logic(self):
        if self.directions[LEFT]:
            self.apply_force((-WALK_SPEED, 0))
        if self.directions[RIGHT]:
            self.apply_force((WALK_SPEED, 0))

        if self.collide_down:
            # feet friction
            self.apply_force(-0.2*self.velocity.horizontal)
        else:
            self.apply_force(-0.25*self.velocity.horizontal)
