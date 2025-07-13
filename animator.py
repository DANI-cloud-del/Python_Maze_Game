import pygame

class Animator:
    def __init__(self, animations, frame_duration=120):
        self.animations = animations  # {'walk_up': [frame1, frame2, ...], ...}
        self.frame_duration = frame_duration
        self.current_state = 'idle_down'
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()

    def set_state(self, new_state):
        if new_state != self.current_state:
            self.current_state = new_state
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_state])
            self.last_update = now

    def get_current_frame(self):
        return self.animations[self.current_state][self.frame_index]
