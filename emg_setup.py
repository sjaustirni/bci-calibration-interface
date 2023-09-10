import pygame


class EMGSetup():
    """
    Used to determine the correct EMG threshold for the user.
    """
    
    def __init__(self, threshold):
        self.threshold = threshold
        self.font = pygame.font.SysFont('Arial', 30)
        self.emg = 0
    
    def draw(self, screen, emg):
        if emg:
            self.emg = emg
        
        # Fill the background with white
        screen.fill((255, 255, 255))
        
        self.draw_test(screen)
        
        # Flip the display
        pygame.display.flip()
    
    def draw_test(self, screen):
        text_surf = self.font.render(str(int(self.emg)), True, (0, 128, 0))
        screen.blit(text_surf, (10, 10))
        
        if self.emg > self.threshold:
            pygame.draw.circle(screen, (0, 0, 255), (250, 250), self.emg)
