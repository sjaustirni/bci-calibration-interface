import argparse
from datetime import datetime

import matplotlib.pyplot as plt
import os
from filter import Filter
from flow import Flow

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from scene import Scene
from emg_setup import EMGSetup
from instructions_scene import InstructionScene
from game_scene import GameScene


def create_scene(mode, threshold):
    if mode == "setup":
        return EMGSetup(threshold)
    elif mode == "game":
        return GameScene()
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
        screen = pygame.display.set_mode((800, 600))
    
    try:
        scene: Scene = create_scene(arg_parser.parse_args().mode, THRESHOLD)
    except ValueError as e:
        print(e)
        return
    
    flow = Flow(mode=arg_parser.parse_args().mode, playback=arg_parser.parse_args().playback)
    flow.start()
    
    emg_filter = Filter(sampling_frequency=flow.get_sample_rate(), bandpass_high=min(flow.get_sample_rate() / 2 - 1, 200))
    
    clock = pygame.time.Clock()
    running = True
    while running:
        emg = flow.get_user_input()

        if emg is not None:
            for sample in emg:
                emg_filter.apply(sample)

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

        try:
            last_sample = emg_filter.output[-1]
        except:
            last_sample = None
        scene.draw(screen, last_sample)
        clock.tick(60)
    
    plt.plot(emg_filter.output)
    plt.show()

    plt.plot(emg_filter.output)
    plt.savefig(f"logs/{datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')}_{arg_parser.parse_args().mode}.png", format="png")
    plt.show()

    plt.plot(emg_filter.input)
    plt.show()

    flow.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
