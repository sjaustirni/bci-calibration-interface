import random

import pygame

import constants
from scene import Scene

GAME_SPEED = 4  # 2 tiles per second at 60 fps
GRAVITY = 0.062
HIT_PENALTY = 3000  # 3s of penalty


def _tint_surf(original, colour):
    surf = original.copy()
    surf.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    surf.fill(colour + (0,), None, pygame.BLEND_RGBA_ADD)
    return surf


class Flag:
    def __init__(self, game):
        self.game = game
        self.flag_1 = pygame.image.load("assets/PNG/Items/flagYellow1.png")
        self.flag_2 = pygame.image.load("assets/PNG/Items/flagYellow2.png")

        self.current_image = self.flag_1
        self.last_flag_tick = pygame.time.get_ticks()

    def draw(self, screen):
        self._update()

        a = self.game.left_corner
        flag_tile = self.game.level_width
        x = a + flag_tile * self.game.tile_width
        y = self.game.y - self.flag_1.get_height()

        screen.blit(self.current_image, (x, y))

    def _update(self):
        ticks = pygame.time.get_ticks()
        if ticks - self.last_flag_tick > 200:
            self.last_flag_tick = ticks
            self.current_image = self.flag_1 if self.current_image == self.flag_2 else self.flag_2


class Player:
    def __init__(self, game, ground):
        self.game = game
        self.player_walk_1 = pygame.image.load("assets/PNG/Players/128x256/Yellow/alienYellow_walk1.png")
        self.player_walk_2 = pygame.image.load("assets/PNG/Players/128x256/Yellow/alienYellow_walk2.png")
        self.player_jump = pygame.image.load("assets/PNG/Players/128x256/Yellow/alienYellow_jump.png")
        self.player_stand = pygame.image.load("assets/PNG/Players/128x256/Yellow/alienYellow_stand.png")
        self.player_hit = _tint_surf(self.player_stand, constants.RED)

        self.current_image = self.player_stand
        self.last_walk_tick = pygame.time.get_ticks()

        self.player_ground = ground - self.player_walk_1.get_height()
        self.y = self.player_ground
        self.x = self.get_start_position()

        self.vel_y = 0
        self.last_hit = None
        self.started = False

    def get_start_position(self):
        return pygame.display.get_window_size()[0] / 3 - self.current_image.get_width() / 2

    def draw(self, screen, started):
        self.started = started
        self._update()

        self._set_player_surface()
        screen.blit(self.current_image, (self.x, self.y))

    def jump(self):
        # Only allow jumping if the game is running
        if self.game.reached_goal():
            return
        # No double jump allowed
        if self.is_jumping():
            return
        # Only allow jumping in the motor task (perform) phase
        if self.game.current_game_tile() in self.game.get_non_jumpy_tiles():
            return
        # Only allow jumping if we are not under penalty
        if self.last_hit is None or self.game.time_since_hit_gt(HIT_PENALTY):
            self.game.log("PlayerJump", None)
            self.vel_y = -10

    def hit(self):
        self.game.log("PlayerHit", None)
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

    def is_jumping(self):
        return self.y < self.player_ground

    def _set_player_surface(self):
        ticks = pygame.time.get_ticks()
        if self.started:
            if self.last_hit is not None:
                time_since_hit = ticks - self.last_hit
                if time_since_hit < HIT_PENALTY:
                    self.current_image = self.player_hit
                    return
            if self.is_jumping():
                self._draw_jump()
                return
            if self.game.reached_goal():
                self.current_image = self.player_stand
            else:
                self._draw_walk()
            return
        self.current_image = self.player_stand


class GameScene(Scene):
    def __init__(self):
        super().__init__()
        
        self.threshold = None
        self.background_image = pygame.image.load("assets/Backgrounds/backgroundEmpty.png")
        self.background_image = pygame.transform.scale(self.background_image, pygame.display.get_window_size())

        self.ground_left = pygame.image.load("assets/PNG/Ground/Grass/grassLeft.png")
        self.sand_right = pygame.image.load("assets/PNG/Ground/Sand/sandRight.png")
        self.ground = pygame.image.load("assets/PNG/Ground/Grass/grassMid.png")
        self.sand = pygame.image.load("assets/PNG/Ground/Sand/sandMid.png")

        self.cactus = pygame.image.load("assets/PNG/Tiles/cactus.png")
        self.spikes = pygame.image.load("assets/PNG/Tiles/spikes.png")

        self.star = pygame.image.load("assets/PNG/Items/star.png")

        self.tile_width = self.ground.get_width()
        self.tile_height = self.ground.get_height()

        self.obstacle_no = 5
        self.tiles_per_obstacle = 26  # (a little over) 5 seconds at 60 fps
        self.start_tile = 31

        self.left_corner = 0
        self.level_width = (self.tiles_per_obstacle - 8) + self.tiles_per_obstacle * self.obstacle_no  # in tiles
        self.y = pygame.display.get_window_size()[1] - self.tile_height

        self.no_obstacles_hit = 0

        self.player = Player(game=self, ground=self.y)
        self.obstacles = self._generate_obstacles()
        self.started = False

        self.flag = Flag(self)
        self.current_phase = None

    def draw(self, screen, emg):
        if self.started and self.threshold and emg > self.threshold and self.time_since_hit_gt(HIT_PENALTY + 2000):
            self.player.jump()
        # Only move player forward if the game is running and they are not under penalty
        if self.started and self.time_since_hit_gt(HIT_PENALTY) and not self.reached_goal():
            # Make jump a little faster to account for the extra tile with obstacle
            if self.player.is_jumping():
                self.left_corner -= GAME_SPEED * 1.2
            else:
                self.left_corner -= GAME_SPEED

        screen.fill(constants.BACKGROUND)
        screen.blit(self.background_image, (0, 0))

        self._draw_ground(screen)
        self._draw_obstacles(screen)

        self.player.draw(screen, self.started)
        self.flag.draw(screen)

        if self.reached_goal():
            self._draw_end_screen(screen)

        self.update(screen)

        # Flip the display
        pygame.display.flip()

    def update(self, screen):
        self.log_phase(self._get_phase())

        player_colour = constants.BLUE
        obstacle_colour = constants.YELLOW
        hit_colour = constants.RED

        # Check for player <-> obstacle collision
        padding = 15  # add some collision padding to give the player some slack and be more visually consistent
        player_rect = pygame.Rect(self.player.x, self.player.y + self.tile_height + padding, self.tile_width - padding,
                                  self.tile_height - padding * 2)
        obstacle_rects = [pygame.Rect(obstacle[1] + self.left_corner + padding, self.y - self.tile_height + padding * 2,
                                      self.tile_width - padding * 3, self.tile_height - padding * 2) for obstacle in
                          self.obstacles]
        hit_obstacle = player_rect.collidelist(obstacle_rects)

        # Give player 2s to get out of the obstacle
        hit_amnesty = not self.time_since_hit_gt(HIT_PENALTY + 2000)
        if hit_obstacle >= 0 and not self.player.is_jumping():
            if self.player.last_hit is None or not hit_amnesty:
                self.player.hit()
                self.no_obstacles_hit += 1

        debug = False
        if not debug:
            return
        for i, obstacle_rect in enumerate(obstacle_rects):
            colour = hit_colour if i == hit_obstacle else obstacle_colour
            pygame.draw.rect(screen, color=colour, rect=obstacle_rect)

        pygame.draw.rect(screen, color=player_colour, rect=player_rect)

    def process_event(self, event):
        if self.started:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.jump()
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                self.started = True

    def set_threshold(self, threshold):
        if threshold != self.threshold:
            self.log("Threshold", threshold)
        self.threshold = threshold

    def _get_phase(self):
        if not self.started or self.reached_goal():
            return "NotRunning"
        non_jumpy_tiles = self.get_non_jumpy_tiles()
        if self.current_game_tile() in non_jumpy_tiles:
            return "Relax"
        else:
            return "MotorTask"

    def log_phase(self, phase):
        if phase != self.current_phase:
            self.log("Phase", phase)
            self.current_phase = phase

    def _generate_obstacles(self):
        obstacles = []
        for i in range(0, self.obstacle_no):
            x = self.tile_width * self.start_tile + self.tile_width * self.tiles_per_obstacle * i
            if random.random() < 0.5:
                obstacles.append(("CACTUS", x))
            else:
                obstacles.append(("SPIKES", x))
        return obstacles

    def time_since_hit_gt(self, duration):
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

        non_jumpy_tiles = self.get_non_jumpy_tiles()
        for i in range(1, self.level_width):
            tile = self.sand if i in non_jumpy_tiles else self.ground
            screen.blit(tile, (a + i * self.tile_width, y))
        screen.blit(self.sand_right, (a + self.level_width * self.tile_width, y))

    def _draw_end_screen(self, screen):
        obstacles_avoided = self.obstacle_no - self.no_obstacles_hit
        win_ratio = obstacles_avoided / self.obstacle_no
        no_stars = 3 if win_ratio > 0.9 else 2 if win_ratio > 0.5 else 1

        for i in range(0, no_stars):
            screen.blit(self.star, (pygame.display.get_window_size()[0] / 2 - self.star.get_width() * (
                    no_stars - 1) / 2 + i * self.star.get_width(), pygame.display.get_window_size()[1] / 2))

    def get_non_jumpy_tiles(self):
        obstacle_tiles = self.get_obstacle_tiles()
        preparation_tiles = []
        for obstacle_tile in obstacle_tiles:
            preparation_tiles.extend(
                [obstacle_tile - i for i in range(self.tiles_per_obstacle - 14, self.tiles_per_obstacle)])
        return obstacle_tiles + preparation_tiles + list(range(0, min(preparation_tiles))) + list(
            range(max(obstacle_tiles), self.level_width))

    def get_obstacle_tiles(self):
        return [(self.start_tile + self.tiles_per_obstacle * i) for i in range(0, self.obstacle_no)]

    def current_game_tile(self):
        """
        :return: The no. tile the player is currently on.
        """

        return int((-self.left_corner + self.player.get_start_position()) / self.tile_width)

    def reached_goal(self):
        """
        :return: True if the player has reached the goal, False otherwise.
        """

        return self.current_game_tile() >= self.level_width
