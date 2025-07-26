import random
import pygame
from cell import CellType
from utils.settings import CELL_SIZE, PATH_WIDTH  

class SpecialEffects:
    def __init__(self, maze):
        self.maze = maze
        self.reset_time = 0
        self.reset_cooldown = 10000
        self.teleport_pairs = []  # To store all teleport pairs
        self.used_teleports = set()  # To track used teleports
    
    def generate_special_cells(self):
        exit_x, exit_y = self.maze.exit_pos
        self.maze.grid[exit_x][exit_y].type = CellType.EXIT
        
        # Generate traps (5% of cells)
        trap_count = int(self.maze.cols * self.maze.rows * 0.05)
        for _ in range(trap_count):
            while True:
                x, y = random.randint(0, self.maze.cols-1), random.randint(0, self.maze.rows-1)
                if (x,y) != self.maze.start_pos and (x,y) != self.maze.exit_pos:
                    self.maze.grid[x][y].type = CellType.TRAP
                    break
        
        # Generate teleporters (4 pairs)
        teleport_count = 4
        positions = []
        
        # First find all valid positions
        valid_positions = []
        for x in range(self.maze.cols):
            for y in range(self.maze.rows):
                if (x,y) != self.maze.start_pos and (x,y) != self.maze.exit_pos:
                    # Ensure position isn't in a corner (less likely to get stuck)
                    if not (x in [0, self.maze.cols-1] and y in [0, self.maze.rows-1]):
                        valid_positions.append((x,y))
        
        random.shuffle(valid_positions)
        
        # Create teleport pairs
        for i in range(0, teleport_count*2, 2):
            x1, y1 = valid_positions[i]
            x2, y2 = valid_positions[i+1]
            
            self.maze.grid[x1][y1].type = CellType.TELEPORT
            self.maze.grid[x1][y1].linked_teleport = (x2, y2)
            self.maze.grid[x2][y2].type = CellType.TELEPORT
            self.maze.grid[x2][y2].linked_teleport = (x1, y1)
            
            self.teleport_pairs.append(((x1,y1), (x2,y2)))
        
        # Generate buttons
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
        
        elif cell.type == CellType.TELEPORT and not cell.triggered and (x,y) not in self.used_teleports:
            cell.triggered = True
            self.used_teleports.add((x,y))
            
            # Find the target teleport
            tele_x, tele_y = cell.linked_teleport
            self.used_teleports.add((tele_x, tele_y))
            
            # Calculate safe landing position (center of the target cell)
            teleport_pos = (
                tele_x * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2,
                tele_y * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
            )
            
            return "teleport", teleport_pos, (tele_x, tele_y)
        
        elif cell.type == CellType.BUTTON and not cell.triggered:
            current_time = pygame.time.get_ticks()
            if current_time - self.reset_time > self.reset_cooldown:
                cell.triggered = True
                self.reset_time = current_time
                return "maze_reset", (x, y)  # Return button position
        
        elif cell.type == CellType.EXIT:
            return "exit"
            
        return None