# maze.py

import random
import pygame
from utils.settings import MAZE_COLS, MAZE_ROWS, CELL_SIZE

class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

class Maze:
    def __init__(self):
        self.cols = MAZE_COLS
        self.rows = MAZE_ROWS
        self.grid = [[Cell(x, y) for y in range(self.rows)] for x in range(self.cols)]
        self.generate_prims()

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
        start = self.get_cell(random.randint(0, self.cols - 1), random.randint(0, self.rows - 1))
        start.visited = True
        frontier = []

        for direction, neighbor in self.get_neighbors(start):
            frontier.append((start, direction, neighbor))

        while frontier:
            current, direction, next_cell = random.choice(frontier)
            frontier.remove((current, direction, next_cell))

            if not next_cell.visited:
                self.remove_walls(current, next_cell, direction)
                next_cell.visited = True

                for dir2, neighbor2 in self.get_neighbors(next_cell):
                    frontier.append((next_cell, dir2, neighbor2))

    # Entrance and exit
        entrance = self.get_cell(0, 0)
        entrance.walls['left'] = False
        exit = self.get_cell(self.cols - 1, self.rows - 1)
        exit.walls['right'] = False


    def draw(self, screen):
        for x in range(self.cols):
            for y in range(self.rows):
                cell = self.grid[x][y]
                px = x * CELL_SIZE
                py = y * CELL_SIZE
                if cell.walls['top']:
                    pygame.draw.line(screen, (255, 255, 255), (px, py), (px + CELL_SIZE, py), 2)
                if cell.walls['right']:
                    pygame.draw.line(screen, (255, 255, 255), (px + CELL_SIZE, py), (px + CELL_SIZE, py + CELL_SIZE), 2)
                if cell.walls['bottom']:
                    pygame.draw.line(screen, (255, 255, 255), (px + CELL_SIZE, py + CELL_SIZE), (px, py + CELL_SIZE), 2)
                if cell.walls['left']:
                    pygame.draw.line(screen, (255, 255, 255), (px, py + CELL_SIZE), (px, py), 2)
