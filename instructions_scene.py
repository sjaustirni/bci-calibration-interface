import time
import constants
import pygame
from scene import Scene

NOT_RUNNING = "Not running"
PREPARE = "Prepare to perform the motor imagery task"
MOTOR_IMAGERY = "Perform the motor imagery task"
RELAX = "Relax"

class TimingTask(Scene):
    def __init__(self, no_attempts=5, prepare_phase: int = 2, motor_imagery_phase: int = 5,relax_phase: int = 5,):
        """
        :param no_attempts: The number of attempts to perform the motor imagery task
        :param prepare_phase: Number of seconds to prepare
        :param motor_imagery_phase: Number of seconds to perform the motor imagery task
        :param relax_phase: Number of seconds to relax
        """
        super().__init__()
        self.no_attempts = no_attempts
        self.prepare_phase = prepare_phase
        self.motor_imagery_phase = motor_imagery_phase
        self.relax_phase = relax_phase
        self.clock_start = None
        
        self.attempt_duration = self.prepare_phase + self.motor_imagery_phase + self.relax_phase
    
    def start(self):
        self.clock_start = time.time()
        
    def stop(self):
        self.clock_start = None
        
    def get_phase(self):
        if self.clock_start is None:
            return NOT_RUNNING, None, None, None
        
        now = time.time()
        elapsed = now - self.clock_start
        
        full_attempts = int(elapsed / self.attempt_duration)
        partial_attempt = elapsed % self.attempt_duration
        
        if full_attempts >= self.no_attempts:
            return NOT_RUNNING, None, None, None
        
        if partial_attempt < self.prepare_phase:
            return PREPARE, self.prepare_phase - partial_attempt, self.prepare_phase, constants.YELLOW
        elif partial_attempt < self.prepare_phase + self.motor_imagery_phase:
            return MOTOR_IMAGERY, self.prepare_phase + self.motor_imagery_phase - partial_attempt, self.motor_imagery_phase, constants.BLUE
        elif partial_attempt < self.prepare_phase + self.motor_imagery_phase + self.relax_phase:
            return RELAX, self.prepare_phase + self.motor_imagery_phase + self.relax_phase - partial_attempt, self.relax_phase, constants.GREEN
        
        return NOT_RUNNING, None, None, None

class InstructionScene:
    """
    Displays the instructions for motor imagery without giving any feedback.
    """
    def __init__(self, threshold):
        super().__init__(threshold)

        self.font = pygame.font.SysFont('Arial', 30)
        self.timing_task = TimingTask()
    
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
            pygame.draw.rect(screen, colour, pygame.Rect(center[0] - max_width / 2, center[1],
                                                                      width, 30))
            seconds_left_surf = self.font.render(f"{seconds_left:.1f}", True, constants.TEXT)
            screen.blit(seconds_left_surf, (10, 50))