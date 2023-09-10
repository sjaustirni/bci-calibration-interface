import argparse
import matplotlib.pyplot as plt
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

from filter import Filter
from flow import Flow
from emg_setup import EMGSetup


def create_scene(mode, threshold):
    if mode == "setup":
        return EMGSetup(threshold)
    # elif mode == "game":
    #     pass
    # elif mode == "instructions":
    #     pass
    else:
        raise ValueError(f"Unknown mode: {mode}")


def main():
    arg_parser = argparse.ArgumentParser(description="BCI calibration")
    arg_parser.add_argument("--playback", action="store_true", help="Use a file as input instead of the EMG device")
    arg_parser.add_argument("--threshold", type=int, help="The EMG threshold, default 8", default=8)
    arg_parser.add_argument("--mode", help="'setup' (default), 'game' or 'instructions'", default="setup")
    
    THRESHOLD = arg_parser.parse_args().threshold
    
    pygame.init()
    pygame.display.set_caption("BCI calibration")
    screen = pygame.display.set_mode((640, 480))
    
    try:
        scene = create_scene(arg_parser.parse_args().mode, THRESHOLD)
    except ValueError as e:
        print(e)
        return
    
    flow = Flow(playback=arg_parser.parse_args().playback)
    flow.start()
    
    emg_filter = Filter()
    
    running = True
    while running:
        emg = flow.get_user_input()
        
        if emg is not None:
            emg = emg_filter.apply(emg)
        
        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        scene.draw(screen, emg)
    
    plt.plot(emg_filter.output)
    plt.show()
    flow.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
