from scene import Scene
import pygame
import constants
import random

GAME_SPEED = 4
GRAVITY = 0.4

class Player:
    def __init__(self, ground):
        self.player_walk_1 = pygame.image.load("assets/PNG/Players/128x256/Yellow/alienYellow_walk1.png")
        self.player_walk_2 = pygame.image.load("assets/PNG/Players/128x256/Yellow/alienYellow_walk2.png")
        self.player_jump = pygame.image.load("assets/PNG/Players/128x256/Yellow/alienYellow_jump.png")
        
        self.current_image = self.player_walk_1
        self.last_walk_tick = pygame.time.get_ticks()
        
        self.player_ground = ground - self.player_walk_1.get_height()
        self.y = self.player_ground
        
        self.vel_y = 0
    
    def draw(self, screen):
        self._update()

        if self._is_jumping():
            self._draw_jump()
        else:
            self._draw_walk()

        screen.blit(self.current_image,
                    (pygame.display.get_window_size()[0] / 3 - self.current_image.get_width() / 2, self.y))
        
    def jump(self):
        if not self._is_jumping():
            self.vel_y = -20
    
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
        
        self.obstacle_no = 10
        self.tiles_per_obstacle = 5
        self.start_tile = 20
        
        self.left_corner = 0
        self.level_width = self.start_tile + self.tiles_per_obstacle * (self.obstacle_no + 4) # in tiles
        self.y = pygame.display.get_window_size()[1] - self.tile_height
        
        self.player = Player(ground=self.y)
        self.obstacles = self._generate_obstacles()
    
    
    def draw(self, screen, _emg):
        self.left_corner -= GAME_SPEED
        
        screen.fill(constants.BACKGROUND)
        screen.blit(self.background_image, (0, 0))
        
        self._draw_ground(screen)
        self._draw_obstacles(screen)
        
        self.player.draw(screen)
        
        # Flip the display
        pygame.display.flip()
    
    def process_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.player.jump()
    
    def _generate_obstacles(self):
        obstacles = []
        for i in range(0, 10):
            x = random.randrange(self.tile_width*self.start_tile, self.tile_width * self.level_width, self.tile_width*self.tiles_per_obstacle)
            print(x)
            if random.random() < 0.5:
                obstacles.append(("CACTUS", x))
            else:
                obstacles.append(("SPIKES", x))
        return obstacles

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
        
        
