import random

import pygame

import constants
from scene import Scene

GAME_SPEED = 4  # 2 tiles per second at 60 fps
GRAVITY = 0.065
HIT_PENALTY = 3000  # 3s of penalty


def _tint_surf(original, colour):
    surf = original.copy()
    surf.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    surf.fill(colour + (0,), None, pygame.BLEND_RGBA_ADD)
    return surf


class Player:
    def __init__(self, ground):
        self.player_walk_1 = pygame.image.load("assets/PNG/Players/128x256/Yellow/alienYellow_walk1.png")
        self.player_walk_2 = pygame.image.load("assets/PNG/Players/128x256/Yellow/alienYellow_walk2.png")
        self.player_jump = pygame.image.load("assets/PNG/Players/128x256/Yellow/alienYellow_jump.png")
        self.player_stand = pygame.image.load("assets/PNG/Players/128x256/Yellow/alienYellow_stand.png")
        self.player_hit = _tint_surf(self.player_stand, constants.RED)

        self.current_image = self.player_stand
        self.last_walk_tick = pygame.time.get_ticks()

        self.player_ground = ground - self.player_walk_1.get_height()
        self.y = self.player_ground
        self.x = pygame.display.get_window_size()[0] / 3 - self.current_image.get_width() / 2

        self.vel_y = 0
        self.last_hit = None
        self.started = False

    def draw(self, screen, started):
        self.started = started
        self._update()

        self._set_player_surface()
        screen.blit(self.current_image, (self.x, self.y))

    def jump(self):
        if not self._is_jumping():
            self.vel_y = -10

    def hit(self):
        self.last_hit = pygame.time.get_ticks()
        # Reset the velocity if we have hit corner
        self.vel_y = 0

    def _update(self):
        self.y += self.vel_y
        self.vel_y += GRAVITY

        if self.y > self.player_ground:
            self.y = self.player_ground
            self.vel_y = 0

    def _draw_walk(self):
        ticks = pygame.time.get_ticks()
        if ticks - self.last_walk_tick > 200:
            self.last_walk_tick = ticks
            self.current_image = self.player_walk_1 if self.current_image == self.player_walk_2 else self.player_walk_2

    def _draw_jump(self):
        self.current_image = self.player_jump

    def _is_jumping(self):
        return self.y < self.player_ground

    def _set_player_surface(self):
        ticks = pygame.time.get_ticks()
        if self.started:
            if self.last_hit is not None:
                time_since_hit = ticks - self.last_hit
                if time_since_hit < HIT_PENALTY:
                    self.current_image = self.player_hit
                    return
            if self._is_jumping():
                self._draw_jump()
                return
            self._draw_walk()
            return
        self.current_image = self.player_stand


class GameScene(Scene):
    def __init__(self):
        super().__init__()

        self.background_image = pygame.image.load("assets/Backgrounds/backgroundEmpty.png")
        self.background_image = pygame.transform.scale(self.background_image, pygame.display.get_window_size())

        self.ground_left = pygame.image.load("assets/PNG/Ground/Grass/grassLeft.png")
        self.ground_right = pygame.image.load("assets/PNG/Ground/Grass/grassRight.png")
        self.ground = pygame.image.load("assets/PNG/Ground/Grass/grassMid.png")

        self.cactus = pygame.image.load("assets/PNG/Tiles/cactus.png")
        self.spikes = pygame.image.load("assets/PNG/Tiles/spikes.png")

        self.tile_width = self.ground.get_width()
        self.tile_height = self.ground.get_height()

        self.obstacle_no = 20
        self.tiles_per_obstacle = 20  # (a little over) 5 seconds at 60 fps
        self.start_tile = 20

        self.left_corner = 0
        self.level_width = self.start_tile + self.tiles_per_obstacle * (self.obstacle_no + 4)  # in tiles
        self.y = pygame.display.get_window_size()[1] - self.tile_height

        self.player = Player(ground=self.y)
        self.obstacles = self._generate_obstacles()
        self.started = False

    def draw(self, screen, _emg):
        # Only move player forward if the game is running and they are not under penalty
        if self.started and self._time_since_hit_gt(HIT_PENALTY):
            self.left_corner -= GAME_SPEED

        screen.fill(constants.BACKGROUND)
        screen.blit(self.background_image, (0, 0))

        self._draw_ground(screen)
        self._draw_obstacles(screen)

        self.player.draw(screen, self.started)
        self.update(screen)

        # Flip the display
        pygame.display.flip()

    def update(self, screen):
        player_colour = constants.BLUE
        obstacle_colour = constants.YELLOW
        hit_colour = constants.RED

        # Check for player <-> obstacle collision
        padding = 15 # add some collision padding to give the player some slack and be more visually consistent
        player_rect = pygame.Rect(self.player.x, self.player.y + self.tile_height + padding, self.tile_width - padding, self.tile_height - padding * 2)
        obstacle_rects = [
            pygame.Rect(obstacle[1] + self.left_corner + padding, self.y - self.tile_height + padding * 2, self.tile_width - padding * 3, self.tile_height - padding * 2)
            for obstacle in self.obstacles]
        hit_obstacle = player_rect.collidelist(obstacle_rects)

        # Give player 2s to get out of the obstacle
        hit_amnesty = not self._time_since_hit_gt(HIT_PENALTY + 2000)
        if hit_obstacle >= 0:
            if self.player.last_hit is None or not hit_amnesty:  # First hit
                self.player.hit()

        debug = False
        if not debug:
            return
        for i, obstacle_rect in enumerate(obstacle_rects):
            colour = hit_colour if i == hit_obstacle else obstacle_colour
            pygame.draw.rect(screen, color=colour, rect=obstacle_rect)

        pygame.draw.rect(screen, color=player_colour, rect=player_rect)

    def process_event(self, event):
        if self.started and (self.player.last_hit is None or self._time_since_hit_gt(HIT_PENALTY)):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.jump()
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                self.started = True

    def _generate_obstacles(self):
        obstacles = []
        for i in range(0, self.obstacle_no):
            x = self.tile_width * self.start_tile + self.tile_width * self.tiles_per_obstacle * i
            if random.random() < 0.5:
                obstacles.append(("CACTUS", x))
            else:
                obstacles.append(("SPIKES", x))
        return obstacles

    def _time_since_hit_gt(self, duration):
        """
        Returns True if time since the player hit an obstacle last time is greater than the supplied duration in ms.
        Otherwise, returns False.
        """
        if self.player.last_hit is not None:
            ticks = pygame.time.get_ticks()
            return (ticks - self.player.last_hit) > duration
        return True

    def _draw_obstacles(self, screen):
        a = self.left_corner
        for obstacle in self.obstacles:
            if obstacle[0] == "CACTUS":
                screen.blit(self.cactus, (a + obstacle[1], self.y - self.cactus.get_height()))
            elif obstacle[0] == "SPIKES":
                screen.blit(self.spikes, (a + obstacle[1], self.y - self.spikes.get_height()))

    def _draw_ground(self, screen):
        a = self.left_corner
        y = self.y

        screen.blit(self.ground_left, (a, y))
        for i in range(1, self.level_width):
            screen.blit(self.ground, (a + i * self.tile_width, y))
        screen.blit(self.ground_right, (a + self.level_width * self.tile_width, y))
