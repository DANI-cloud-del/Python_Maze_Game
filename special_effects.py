import random
import pygame
from cell import CellType
from utils.settings import CELL_SIZE, PATH_WIDTH  


class SpecialEffects:
    def __init__(self, maze):
        self.maze = maze
        self.reset_time = 0
        self.reset_cooldown = 10000
    
    def generate_special_cells(self):
        exit_x, exit_y = self.maze.exit_pos
        self.maze.grid[exit_x][exit_y].type = CellType.EXIT
        
        trap_count = int(self.maze.cols * self.maze.rows * 0.05)
        for _ in range(trap_count):
            x, y = random.randint(0, self.maze.cols-1), random.randint(0, self.maze.rows-1)
            if (x,y) != self.maze.start_pos and (x,y) != self.maze.exit_pos:
                self.maze.grid[x][y].type = CellType.TRAP
        
        teleport_count = 4
        positions = []
        for _ in range(teleport_count * 2):
            while True:
                x, y = random.randint(0, self.maze.cols-1), random.randint(0, self.maze.rows-1)
                if (x,y) not in positions and (x,y) != self.maze.start_pos and (x,y) != self.maze.exit_pos:
                    positions.append((x,y))
                    break
        
        for i in range(0, len(positions), 2):
            x1, y1 = positions[i]
            x2, y2 = positions[i+1]
            self.maze.grid[x1][y1].type = CellType.TELEPORT
            self.maze.grid[x1][y1].linked_teleport = (x2, y2)
            self.maze.grid[x2][y2].type = CellType.TELEPORT
            self.maze.grid[x2][y2].linked_teleport = (x1, y1)
        
        button_count = 3
        for _ in range(button_count):
            while True:
                x, y = random.randint(0, self.maze.cols-1), random.randint(0, self.maze.rows-1)
                if (x,y) != self.maze.start_pos and (x,y) != self.maze.exit_pos and self.maze.grid[x][y].type == CellType.NORMAL:
                    self.maze.grid[x][y].type = CellType.BUTTON
                    break
    
    def check_special_cells(self, player_rect):
        x = player_rect.centerx // CELL_SIZE
        y = player_rect.centery // CELL_SIZE
        
        if not (0 <= x < self.maze.cols and 0 <= y < self.maze.rows):
            return None
            
        cell = self.maze.grid[x][y]
        
        if cell.type == CellType.TRAP and not cell.triggered:
            cell.triggered = True
            return "trap"
        
        elif cell.type == CellType.TELEPORT and not cell.triggered:
            cell.triggered = True
            return "teleport", cell.linked_teleport
        
        elif cell.type == CellType.BUTTON and not cell.triggered:
            current_time = pygame.time.get_ticks()
            if current_time - self.reset_time > self.reset_cooldown:
                cell.triggered = True
                self.reset_time = current_time
                # Return player's current cell position to move them back after reset
                return "maze_reset", (player_rect.centerx // CELL_SIZE, 
                                    player_rect.centery // CELL_SIZE)
        
        elif cell.type == CellType.EXIT:
            return "exit"
            
        return None