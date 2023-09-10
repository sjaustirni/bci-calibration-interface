import pygame
import constants
from scene import Scene


class EMGSetup(Scene):
    """
    Used to determine the correct EMG threshold for the user.
    """
    
    def __init__(self, threshold):
        super().__init__()
        self.threshold = threshold
        self.font = pygame.font.SysFont('Arial', 30)
        self.emg = 0
    
    def draw(self, screen, emg):
        if emg:
            self.emg = emg
        
        # Fill the background with white
        screen.fill(constants.BACKGROUND)
        
        self.draw_test(screen)
        
        # Flip the display
        pygame.display.flip()
    
    def draw_test(self, screen):
        text_surf = self.font.render(str(int(self.emg)), True, constants.TEXT)
        screen.blit(text_surf, (10, 10))
        
        size = pygame.display.get_window_size()
        center = (size[0] / 2, size[1] / 2)
        
        if self.emg > self.threshold:
            pygame.draw.circle(screen, constants.HIGHLIGHT, center, self.emg)
