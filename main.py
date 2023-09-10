import matplotlib.pyplot as plt
import pygame

from filter import Filter
from flow import Flow

THRESHOLD = 8


class Game():
    def __init__(self):
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

        if self.emg > THRESHOLD:
            pygame.draw.circle(screen, (0, 0, 255), (250, 250), self.emg)


def main():
    pygame.init()
    pygame.display.set_caption("BCI calibration")
    screen = pygame.display.set_mode((640, 480))

    flow = Flow(playback=True)
    flow.start()

    emg_filter = Filter()

    game = Game()

    running = True
    while running:
        emg = flow.get_user_input()

        if emg is not None:
            emg = emg_filter.apply(emg)

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        game.draw(screen, emg)
    plt.plot(emg_filter.output)
    plt.show()
    flow.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
