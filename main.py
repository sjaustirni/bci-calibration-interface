import pygame

from flow import Flow

THRESHOLD = 4


class Game():
    def __init__(self):
        self.left = 0
        self.right = 0
    
    def draw(self, screen, left, right):
        # Fill the background with white
        screen.fill((255, 255, 255))
        
        self.draw_test(screen, (left, right))
        
        # Flip the display
        pygame.display.flip()
    
    def draw_test(self, screen, user_input):
        left, right = user_input
        # If there is a change in the user input, update the left and right values
        if left > 0 or right > 0:
            self.left = left
            self.right = right
        if self.left > THRESHOLD:
            self.left = 10
        else:
            self.left = 0
        if self.right > THRESHOLD:
            self.right = 10
        else:
            self.right = 0
        pygame.draw.circle(screen, (0, 0, 255), (250, 250), self.left)
        pygame.draw.circle(screen, (0, 255, 0), (350, 250), self.right)


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    
    flow = Flow(playback=True)
    flow.start()
    
    game = Game()
    
    running = True
    while running:
        left, right = flow.get_user_input()
        
        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        game.draw(screen, left, right)
    flow.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
