import pygame
from utils.settings import CELL_SIZE, PLAYER_SPEED, PLAYER_SIZE

class Player:
    def __init__(self, x=0, y=0):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.direction = pygame.Vector2(1, 0)  # starts moving right
        self.next_direction = pygame.Vector2(1, 0)

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.next_direction = pygame.Vector2(-1, 0)
        elif keys[pygame.K_RIGHT]:
            self.next_direction = pygame.Vector2(1, 0)
        elif keys[pygame.K_UP]:
            self.next_direction = pygame.Vector2(0, -1)
        elif keys[pygame.K_DOWN]:
            self.next_direction = pygame.Vector2(0, 1)

    def move(self, maze):
        # Try to set direction from input anytime
        test_rect = self.rect.move(self.next_direction.x * PLAYER_SPEED, self.next_direction.y * PLAYER_SPEED)
        if not self.collides_with_wall(test_rect, maze):
            self.direction = self.next_direction

        # Try moving in current direction
        next_rect = self.rect.move(self.direction.x * PLAYER_SPEED, self.direction.y * PLAYER_SPEED)
        if not self.collides_with_wall(next_rect, maze):
            self.rect = next_rect


    def collides_with_wall(self, next_rect, maze):
        self.collided_walls = []  # Clear previous collisions

        for x in range(maze.cols):
            for y in range(maze.rows):
                cell = maze.grid[x][y]
                cx = x * CELL_SIZE
                cy = y * CELL_SIZE

                if cell.walls['top']:
                    wall_rect = pygame.Rect(cx, cy, CELL_SIZE, 2)
                    if wall_rect.collidepoint(next_rect.center):
                        self.collided_walls.append(('top', wall_rect))
                        return True
                if cell.walls['right']:
                    wall_rect = pygame.Rect(cx + CELL_SIZE - 2, cy, 2, CELL_SIZE)
                    if wall_rect.collidepoint(next_rect.center):
                        self.collided_walls.append(('right', wall_rect))
                        return True
                if cell.walls['bottom']:
                    wall_rect = pygame.Rect(cx, cy + CELL_SIZE - 2, CELL_SIZE, 2)
                    if wall_rect.collidepoint(next_rect.center):
                        self.collided_walls.append(('bottom', wall_rect))
                        return True
                if cell.walls['left']:
                    wall_rect = pygame.Rect(cx, cy, 2, CELL_SIZE)
                    if wall_rect.collidepoint(next_rect.center):
                        self.collided_walls.append(('left', wall_rect))
                        return True
        return False

    def draw(self, screen, camera):
        adjusted_rect = camera.apply(self.rect)
        pygame.draw.circle(screen, (255, 255, 0), adjusted_rect.center, PLAYER_SIZE // 2)
