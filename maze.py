import random
import pygame
from utils.settings import MAZE_COLS, MAZE_ROWS, CELL_SIZE
from cell import Cell  # Using modular Cell definition

class Maze:
    def __init__(self):
        self.cols = MAZE_COLS
        self.rows = MAZE_ROWS
        self.grid = self.generate_prims()

    def get_cell(self, x, y):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.grid[x][y]
        return None

    def get_neighbors(self, cell):
        directions = [
            ('top', cell.x, cell.y - 1),
            ('right', cell.x + 1, cell.y),
            ('bottom', cell.x, cell.y + 1),
            ('left', cell.x - 1, cell.y),
        ]
        neighbors = []
        for direction, nx, ny in directions:
            neighbor = self.get_cell(nx, ny)
            if neighbor and not neighbor.visited:
                neighbors.append((direction, neighbor))
        return neighbors

    def remove_walls(self, cell1, cell2, direction):
        opposites = {'top': 'bottom', 'bottom': 'top', 'left': 'right', 'right': 'left'}
        cell1.walls[direction] = False
        cell2.walls[opposites[direction]] = False

    def generate_prims(self):
        # Initialize grid
        grid = [[Cell(x, y) for y in range(self.rows)] for x in range(self.cols)]

        # Start from random cell
        start = grid[random.randint(0, self.cols - 1)][random.randint(0, self.rows - 1)]
        start.visited = True
        frontier = []

        def local_neighbors(c):
            directions = [
                ('top', c.x, c.y - 1),
                ('right', c.x + 1, c.y),
                ('bottom', c.x, c.y + 1),
                ('left', c.x - 1, c.y),
            ]
            neighbors = []
            for direction, nx, ny in directions:
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    neighbor = grid[nx][ny]
                    if not neighbor.visited:
                        neighbors.append((direction, neighbor))
            return neighbors

        for direction, neighbor in local_neighbors(start):
            frontier.append((start, direction, neighbor))

        while frontier:
            current, direction, next_cell = random.choice(frontier)
            frontier.remove((current, direction, next_cell))

            if not next_cell.visited:
                self.remove_walls(current, next_cell, direction)
                next_cell.visited = True

                for dir2, neighbor2 in local_neighbors(next_cell):
                    frontier.append((next_cell, dir2, neighbor2))

        # Entrance and exit
        grid[0][0].walls['left'] = False
        grid[self.cols - 1][self.rows - 1].walls['right'] = False

        return grid

    def draw(self, screen, camera, visited_cells):
        for x in range(self.cols):
            for y in range(self.rows):
                cx = x * CELL_SIZE
                cy = y * CELL_SIZE
                cell = self.grid[x][y]

                if (x, y) in visited_cells:
                    pygame.draw.rect(screen, (20, 20, 20), camera.apply(pygame.Rect(cx, cy, CELL_SIZE, CELL_SIZE)))

                if cell.walls['top']:
                    pygame.draw.line(screen, (255, 255, 255),
                                     camera.apply(pygame.Rect(cx, cy, CELL_SIZE, 2)).topleft,
                                     camera.apply(pygame.Rect(cx + CELL_SIZE, cy, CELL_SIZE, 2)).topleft, 2)
                if cell.walls['right']:
                    pygame.draw.line(screen, (255, 255, 255),
                                     camera.apply(pygame.Rect(cx + CELL_SIZE, cy, 2, CELL_SIZE)).topleft,
                                     camera.apply(pygame.Rect(cx + CELL_SIZE, cy + CELL_SIZE, 2, CELL_SIZE)).topleft, 2)
                if cell.walls['bottom']:
                    pygame.draw.line(screen, (255, 255, 255),
                                     camera.apply(pygame.Rect(cx, cy + CELL_SIZE, CELL_SIZE, 2)).topleft,
                                     camera.apply(pygame.Rect(cx + CELL_SIZE, cy + CELL_SIZE, CELL_SIZE, 2)).topleft, 2)
                if cell.walls['left']:
                    pygame.draw.line(screen, (255, 255, 255),
                                     camera.apply(pygame.Rect(cx, cy, 2, CELL_SIZE)).topleft,
                                     camera.apply(pygame.Rect(cx, cy + CELL_SIZE, 2, CELL_SIZE)).topleft, 2)
