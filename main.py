import argparse
import matplotlib.pyplot as plt
import os

from scene import Scene

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from filter import Filter
from flow import Flow
from instructions_scene import InstructionScene
from emg_setup import EMGSetup


def create_scene(mode, threshold):
    if mode == "setup":
        return EMGSetup(threshold)
    # elif mode == "game":
    #     pass
    elif mode == "instructions":
        return InstructionScene()
    else:
        raise ValueError(f"Unknown mode: {mode}")


def main():
    arg_parser = argparse.ArgumentParser(description="BCI calibration")
    arg_parser.add_argument("--fullscreen", action="store_true", help="Run in fullscreen mode", default=False)
    arg_parser.add_argument("--playback", action="store_true", help="Use a file as input instead of the EMG device")
    arg_parser.add_argument("--threshold", type=int, help="The EMG threshold, default 8", default=8)
    arg_parser.add_argument("--mode", help="'setup' (default), 'game' or 'instructions'", default="setup")
    
    THRESHOLD = arg_parser.parse_args().threshold
    
    pygame.init()
    pygame.display.set_caption("BCI calibration")
    if arg_parser.parse_args().fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((1024, 768))
    
    try:
        scene: Scene = create_scene(arg_parser.parse_args().mode, THRESHOLD)
    except ValueError as e:
        print(e)
        return
    
    flow = Flow(playback=arg_parser.parse_args().playback)
    flow.start()
    
    emg_filter = Filter(sampling_frequency=flow.get_sample_rate(), bandpass_high=min(flow.get_sample_rate() / 2 - 1, 200))
    
    running = True
    while running:
        emg = flow.get_user_input()
        
        if emg is not None:
            emg = emg_filter.apply(emg)
        
        for event in pygame.event.get():
            # Did the user click the window close button?
            if event.type == pygame.QUIT:
                running = False
            # Did the user press Q?
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False
            # Did the user press F?
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
            scene.process_event(event)
            
        scene.draw(screen, emg)
    
    plt.plot(emg_filter.output)
    plt.show()
    
    plt.plot(emg_filter.input)
    plt.show()

    flow.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
