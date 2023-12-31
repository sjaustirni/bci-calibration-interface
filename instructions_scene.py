import time

import pygame

import constants
from scene import Scene

NOT_RUNNING = "Not running"
PREPARE = "Forbered dig på bevægelse"
MOTOR_TASK = "Bevæg håndledet"
RELAX = "Slap af"


class TimingTask:
    def __init__(self, scene, no_attempts=5, prepare_phase: int = 2, motor_task_phase: int = 5, relax_phase: int = 5, ):
        """
        :param no_attempts: The number of attempts to perform the motor imagery task
        :param prepare_phase: Number of seconds to prepare
        :param motor_task_phase: Number of seconds to perform the motor imagery task
        :param relax_phase: Number of seconds to relax
        """
        super().__init__()
        self.scene = scene
        self.no_attempts = no_attempts
        self.prepare_phase = prepare_phase
        self.motor_task_phase = motor_task_phase
        self.relax_phase = relax_phase
        self.clock_start = None

        self.current_phase = None

        self.attempt_duration = self.prepare_phase + self.motor_task_phase + self.relax_phase

    def start(self):
        self.clock_start = time.time()
        self.scene.log("InstructionStart", None)

    def stop(self):
        self.clock_start = None
        self.scene.log("InstructionStop", None)

    def get_phase(self):
        if self.clock_start is None:
            return NOT_RUNNING, None, None, None

        now = time.time()
        elapsed = now - self.clock_start

        full_attempts = int(elapsed / self.attempt_duration)
        partial_attempt = elapsed % self.attempt_duration

        if full_attempts >= self.no_attempts:
            self._log_phase("NotRunning")
            return NOT_RUNNING, None, None, None
        if partial_attempt < self.prepare_phase:
            self._log_phase("Prepare")
            return PREPARE, self.prepare_phase - partial_attempt, self.prepare_phase, constants.YELLOW
        elif partial_attempt < self.prepare_phase + self.motor_task_phase:
            self._log_phase("MotorTask")
            return MOTOR_TASK, self.prepare_phase + self.motor_task_phase - partial_attempt, self.motor_task_phase, constants.BLUE
        elif partial_attempt < self.prepare_phase + self.motor_task_phase + self.relax_phase:
            self._log_phase("Relax")
            return RELAX, self.prepare_phase + self.motor_task_phase + self.relax_phase - partial_attempt, self.relax_phase, constants.GREEN
        self._log_phase("NotRunning")
        return NOT_RUNNING, None, None, None

    def _log_phase(self, phase):
        if phase != self.current_phase:
            self.scene.log("Phase", phase)
            self.current_phase = phase


class InstructionScene(Scene):
    """
    Displays the instructions for motor imagery without giving any feedback.
    """

    def __init__(self):
        super().__init__()

        self.font = pygame.font.SysFont('Arial', 30)
        self.timing_task = TimingTask(self)

    def draw(self, screen, _emg):
        # Fill the background with white
        screen.fill(constants.BACKGROUND)

        self._draw_instructions(screen)

        # Flip the display
        pygame.display.flip()

    def process_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            self.timing_task.start()

    def _draw_instructions(self, screen):
        size = pygame.display.get_window_size()
        center = (size[0] / 2, size[1] / 2)

        phase, seconds_left, total_phase_time, colour = self.timing_task.get_phase()

        phase_surf = self.font.render(phase, True, constants.TEXT)
        screen.blit(phase_surf, (center[0] - phase_surf.get_width() / 2, center[1] - phase_surf.get_height() / 2 - 100))

        if seconds_left is not None and total_phase_time is not None and colour is not None:
            max_width = size[0] * 0.5
            width = max_width * (seconds_left / total_phase_time)
            # Don't draw a bar if the phase is PREPARE because it's too short
            if phase != PREPARE:
                pygame.draw.rect(screen, colour, pygame.Rect(center[0] - max_width / 2, center[1], width, 30))