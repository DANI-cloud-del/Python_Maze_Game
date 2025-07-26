from enum import Enum
import pygame
import random
from utils.settings import CELL_SIZE

class DoorState(Enum):
    OPEN = 0
    CLOSED = 1
    OPENING = 2
    CLOSING = 3

class Door:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = DoorState.CLOSED
        self.timer = 0
        self.open_duration = 5000  # ms
        self.closed_duration = 10000  # ms
        self.animation_progress = 0  # 0-1

    def update(self, current_time):
        if self.state == DoorState.OPEN:
            if current_time - self.timer > self.open_duration:
                self.state = DoorState.CLOSING
                self.timer = current_time
        elif self.state == DoorState.CLOSED:
            if current_time - self.timer > self.closed_duration:
                self.state = DoorState.OPENING
                self.timer = current_time
        elif self.state == DoorState.OPENING:
            self.animation_progress = min(1, (current_time - self.timer) / 500)
            if self.animation_progress >= 1:
                self.state = DoorState.OPEN
                self.timer = current_time
        elif self.state == DoorState.CLOSING:
            self.animation_progress = max(0, 1 - (current_time - self.timer) / 500)
            if self.animation_progress <= 0:
                self.state = DoorState.CLOSED
                self.timer = current_time

    def is_blocking(self):
        return self.state in [DoorState.CLOSED, DoorState.CLOSING]

    def draw(self, screen, camera):
        cx = self.x * CELL_SIZE + CELL_SIZE // 2
        cy = self.y * CELL_SIZE + CELL_SIZE // 2
        pos = camera.apply_pos((cx, cy))
        
        if self.is_blocking():
            alpha = 255 if self.state == DoorState.CLOSED else int(255 * self.animation_progress)
            door_color = (150, 50, 50, alpha)
            door_rect = pygame.Rect(
                pos[0] - 20 * camera.zoom,
                pos[1] - 30 * camera.zoom,
                40 * camera.zoom,
                60 * camera.zoom
            )
            door_surface = pygame.Surface((int(40 * camera.zoom), int(60 * camera.zoom)), pygame.SRCALPHA)
            pygame.draw.rect(door_surface, door_color, (0, 0, door_surface.get_width(), door_surface.get_height()))
            screen.blit(door_surface, door_rect)

class DoorSystem:
    def __init__(self, maze):
        self.doors = []
        self.setup_doors(maze)

    def setup_doors(self, maze):
        exit_x, exit_y = maze.exit_pos
        directions = [(0,1),(1,0),(0,-1),(-1,0)]
        random.shuffle(directions)
        
        for dx, dy in directions[:3]:  # Create 3 doors
            x, y = exit_x + dx, exit_y + dy
            if 0 <= x < maze.cols and 0 <= y < maze.rows:
                self.doors.append(Door(x, y))
                maze.grid[x][y].is_door = True

    def update(self, current_time):
        for door in self.doors:
            door.update(current_time)

    def check_collision(self, rect):
        for door in self.doors:
            if door.is_blocking():
                door_x = door.x * CELL_SIZE + CELL_SIZE // 2
                door_y = door.y * CELL_SIZE + CELL_SIZE // 2
                if (abs(rect.centerx - door_x) < CELL_SIZE and 
                    abs(rect.centery - door_y) < CELL_SIZE):
                    return True
        return False

    def draw(self, screen, camera):
        for door in self.doors:
            door.draw(screen, camera)