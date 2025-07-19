import pygame
class WallSet:
    def __init__(self):
        self.walls = []
        self.frames = [...]  # Load animated frames if needed
        self.frame_index = 0
        self.time_accumulator = 0
        self.anim_speed = 0.15

    def add_wall(self, type, rect):
        self.walls.append((type, rect))

    def clear(self):
        self.walls.clear()

    def update(self, dt):
        self.time_accumulator += dt
        if self.time_accumulator > self.anim_speed:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.time_accumulator = 0

    def draw(self, screen, camera):
        for type, rect in self.walls:
            # You can customize rendering based on type
            pygame.draw.rect(screen, (200, 200, 210), camera.apply(rect))
