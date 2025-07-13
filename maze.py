import random
import pygame
from utils.settings import MAZE_COLS, MAZE_ROWS, CELL_SIZE, PATH_WIDTH, WALL_THICKNESS

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

class Maze:
    def __init__(self):
        self.cols = MAZE_COLS
        self.rows = MAZE_ROWS
        self.grid = self.generate_maze()
        
    def generate_maze(self):
        grid = [[Cell(x, y) for y in range(self.rows)] for x in range(self.cols)]
        
        # Prim's algorithm with path width consideration
        start_x, start_y = random.randint(0, self.cols-1), random.randint(0, self.rows-1)
        grid[start_x][start_y].visited = True
        walls = self.get_wall_list(grid[start_x][start_y], grid)
        
        while walls:
            wall = random.choice(walls)
            walls.remove(wall)
            
            x, y = wall[1].x, wall[1].y
            if not grid[x][y].visited:
                grid[wall[0].x][wall[0].y].walls[wall[2]] = False
                grid[x][y].walls[self.opposite_wall(wall[2])] = False
                grid[x][y].visited = True
                walls.extend(self.get_wall_list(grid[x][y], grid))
                
        return grid
    
    def opposite_wall(self, wall):
        return {'top':'bottom', 'bottom':'top', 'left':'right', 'right':'left'}[wall]
    
    def get_wall_list(self, cell, grid):
        walls = []
        for dx, dy, direction in [(0, -1, 'top'), (1, 0, 'right'), 
                                 (0, 1, 'bottom'), (-1, 0, 'left')]:
            nx, ny = cell.x + dx, cell.y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                walls.append((cell, grid[nx][ny], direction))
        return walls
        
    def draw(self, screen, camera, visited_cells):
        for x in range(self.cols):
            for y in range(self.rows):
                if (x, y) not in visited_cells:
                    continue
                    
                cell = self.grid[x][y]
                cx = x * CELL_SIZE
                cy = y * CELL_SIZE
                
                # Draw paths (visible spacing)
                path_rect = pygame.Rect(
                    cx + (CELL_SIZE - PATH_WIDTH)//2,
                    cy + (CELL_SIZE - PATH_WIDTH)//2,
                    PATH_WIDTH,
                    PATH_WIDTH
                )
                pygame.draw.rect(screen, (30, 30, 40), camera.apply(path_rect))
                
                # Draw walls
                if cell.walls['top']:
                    wall_rect = pygame.Rect(cx, cy, CELL_SIZE, WALL_THICKNESS)
                    pygame.draw.rect(screen, (200, 200, 210), camera.apply(wall_rect))
                if cell.walls['right']:
                    wall_rect = pygame.Rect(cx + CELL_SIZE - WALL_THICKNESS, cy, 
                                           WALL_THICKNESS, CELL_SIZE)
                    pygame.draw.rect(screen, (200, 200, 210), camera.apply(wall_rect))
                if cell.walls['bottom']:
                    wall_rect = pygame.Rect(cx, cy + CELL_SIZE - WALL_THICKNESS, 
                                           CELL_SIZE, WALL_THICKNESS)
                    pygame.draw.rect(screen, (200, 200, 210), camera.apply(wall_rect))
                if cell.walls['left']:
                    wall_rect = pygame.Rect(cx, cy, WALL_THICKNESS, CELL_SIZE)
                    pygame.draw.rect(screen, (200, 200, 210), camera.apply(wall_rect))

    def can_move(self, x, y, direction):
        """Check if movement is possible in given direction from cell (x,y)"""
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
            
        cell = self.grid[x][y]
        
        if direction == (-1, 0):  # Left
            return not cell.walls['left']
        elif direction == (1, 0):  # Right
            return not cell.walls['right']
        elif direction == (0, -1):  # Up
            return not cell.walls['top']
        elif direction == (0, 1):  # Down
            return not cell.walls['bottom']
            
        return False