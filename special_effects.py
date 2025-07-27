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
        # Set exit cell
        exit_x, exit_y = self.maze.exit_pos
        self.maze.grid[exit_x][exit_y].type = CellType.EXIT
        
        # Track all special cell positions for spacing
        special_cell_positions = [(exit_x, exit_y), self.maze.start_pos]
        min_distance = 5  # Minimum cells between special items
        
        def is_valid_position(x, y):
            # Check minimum distance from other special cells
            for (px, py) in special_cell_positions:
                if abs(x - px) + abs(y - py) < min_distance:
                    return False
            return (x,y) != self.maze.start_pos and (x,y) != self.maze.exit_pos
        
        # Generate traps (2% of cells)
        trap_count = int(self.maze.cols * self.maze.rows * 0.02)
        for _ in range(trap_count):
            attempts = 0
            while attempts < 100:
                x, y = random.randint(0, self.maze.cols-1), random.randint(0, self.maze.rows-1)
                if is_valid_position(x, y):
                    self.maze.grid[x][y].type = CellType.TRAP
                    special_cell_positions.append((x, y))
                    break
                attempts += 1
        
        # Generate teleporters (2 pairs)
        teleport_count = 2
        valid_positions = []
        for x in range(self.maze.cols):
            for y in range(self.maze.rows):
                if is_valid_position(x, y):
                    valid_positions.append((x,y))
        
        random.shuffle(valid_positions)
        
        for i in range(0, teleport_count*2, 2):
            if i+1 < len(valid_positions):
                x1, y1 = valid_positions[i]
                x2, y2 = valid_positions[i+1]
                
                self.maze.grid[x1][y1].type = CellType.TELEPORT
                self.maze.grid[x1][y1].linked_teleport = (x2, y2)
                self.maze.grid[x2][y2].type = CellType.TELEPORT
                self.maze.grid[x2][y2].linked_teleport = (x1, y1)
                self.teleport_pairs.append(((x1,y1), (x2,y2)))
                special_cell_positions.extend([(x1,y1), (x2,y2)])
        
        # Generate batteries (3)
        battery_count = 3
        for _ in range(battery_count):
            attempts = 0
            while attempts < 100:
                x, y = random.randint(0, self.maze.cols-1), random.randint(0, self.maze.rows-1)
                if is_valid_position(x, y) and self.maze.grid[x][y].type == CellType.NORMAL:
                    self.maze.grid[x][y].type = CellType.BATTERY
                    special_cell_positions.append((x,y))
                    break
                attempts += 1
        
        # Generate ammo (3)
        ammo_count = 3
        for _ in range(ammo_count):
            attempts = 0
            while attempts < 100:
                x, y = random.randint(0, self.maze.cols-1), random.randint(0, self.maze.rows-1)
                if is_valid_position(x, y) and self.maze.grid[x][y].type == CellType.NORMAL:
                    self.maze.grid[x][y].type = CellType.AMMO
                    special_cell_positions.append((x,y))
                    break
                attempts += 1
        
        # Generate buttons (2)
        button_count = 2
        for _ in range(button_count):
            attempts = 0
            while attempts < 100:
                x, y = random.randint(0, self.maze.cols-1), random.randint(0, self.maze.rows-1)
                if is_valid_position(x, y) and self.maze.grid[x][y].type == CellType.NORMAL:
                    self.maze.grid[x][y].type = CellType.BUTTON
                    special_cell_positions.append((x,y))
                    break
                attempts += 1
    
    def check_special_cells(self, player_rect):
        x = player_rect.centerx // CELL_SIZE
        y = player_rect.centery // CELL_SIZE
        
        if not (0 <= x < self.maze.cols and 0 <= y < self.maze.rows):
            return None
            
        cell = self.maze.grid[x][y]
        
        # Battery pickup
        if cell.type == CellType.BATTERY:
            cell.type = CellType.NORMAL
            return "battery"
        
        # Ammo pickup
        elif cell.type == CellType.AMMO:
            cell.type = CellType.NORMAL
            return "ammo"
        
        # Trap
        elif cell.type == CellType.TRAP and not cell.triggered:
            cell.triggered = True
            return "trap"
        
        # Teleporter
        elif cell.type == CellType.TELEPORT and not cell.triggered and (x,y) not in self.used_teleports:
            cell.triggered = True
            self.used_teleports.add((x,y))
            
            # Find the target teleport
            tele_x, tele_y = cell.linked_teleport
            self.used_teleports.add((tele_x, tele_y))
            
            # Calculate safe landing position
            teleport_pos = (
                tele_x * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2,
                tele_y * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
            )
            
            return "teleport", teleport_pos, (tele_x, tele_y)
        
        # Maze reset button
        elif cell.type == CellType.BUTTON and not cell.triggered:
            current_time = pygame.time.get_ticks()
            if current_time - self.reset_time > self.reset_cooldown:
                cell.triggered = True
                self.reset_time = current_time
                return "maze_reset", (x, y)
        
        # Exit
        elif cell.type == CellType.EXIT:
            return "exit"
            
        return None