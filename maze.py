import random
import pygame
from cell import Cell, CellType
from enemy import Enemy
from utils.settings import *
from special_effects import SpecialEffects

class Maze:
    def __init__(self, cols=None, rows=None, enemy_count=5, trap_damage=20):
        self.cols = cols if cols else MAZE_COLS * 2
        self.rows = rows if rows else MAZE_ROWS * 2
        self.grid = self.generate_maze()
        self.enemies = []
        self.start_pos = (0, 0)
        # Random exit position in the far half of the maze
        self.exit_pos = (random.randint(self.cols//2, self.cols-1), 
                        random.randint(self.rows//2, self.rows-1))
        self.reset_time = 0
        self.reset_cooldown = 10000
        self.trap_damage = trap_damage
        self.special_effects = SpecialEffects(self)
        self.generate_enemies(enemy_count)
        self.special_effects.generate_special_cells()
        
    def generate_maze(self):
        grid = [[Cell(x, y) for y in range(self.rows)] for x in range(self.cols)]
        
        # Prim's algorithm with path width consideration
        start_x, start_y = random.randint(0, self.cols//4), random.randint(0, self.rows//4)
        self.start_pos = (start_x, start_y)
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

    def generate_special_cells(self):
        """Generate all special cells (traps, teleporters, buttons, exit)"""
        # Set exit cell
        exit_x, exit_y = self.exit_pos
        self.grid[exit_x][exit_y].type = CellType.EXIT
        
        # Add traps (5% of cells)
        trap_count = int(self.cols * self.rows * 0.05)
        for _ in range(trap_count):
            x, y = random.randint(0, self.cols-1), random.randint(0, self.rows-1)
            if (x,y) != self.start_pos and (x,y) != self.exit_pos:
                self.grid[x][y].type = CellType.TRAP
        
        # Add teleporters (pairs)
        teleport_count = 4
        positions = []
        for _ in range(teleport_count * 2):
            while True:
                x, y = random.randint(0, self.cols-1), random.randint(0, self.rows-1)
                if (x,y) not in positions and (x,y) != self.start_pos and (x,y) != self.exit_pos:
                    positions.append((x,y))
                    break
        
        for i in range(0, len(positions), 2):
            x1, y1 = positions[i]
            x2, y2 = positions[i+1]
            self.grid[x1][y1].type = CellType.TELEPORT
            self.grid[x1][y1].linked_teleport = (x2, y2)
            self.grid[x2][y2].type = CellType.TELEPORT
            self.grid[x2][y2].linked_teleport = (x1, y1)
        
        # Add maze reset buttons
        button_count = 3
        for _ in range(button_count):
            while True:
                x, y = random.randint(0, self.cols-1), random.randint(0, self.rows-1)
                if (x,y) != self.start_pos and (x,y) != self.exit_pos and self.grid[x][y].type == CellType.NORMAL:
                    self.grid[x][y].type = CellType.BUTTON
                    break

    def generate_enemies(self, count):
        """Generate enemies away from start position"""
        self.enemies = []
        min_distance = 5  # Minimum distance from start position
        
        for _ in range(count):
            while True:
                x = random.randint(0, self.cols-1)
                y = random.randint(0, self.rows-1)
                
                # Check distance from start
                if (abs(x - self.start_pos[0]) + abs(y - self.start_pos[1])) >= min_distance:
                    # Pass self as maze reference
                    self.enemies.append(Enemy(x, y, self))
                    break

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
 

    def generate_maze(self):
        grid = [[Cell(x, y) for y in range(self.rows)] for x in range(self.cols)]
        
        start_x, start_y = random.randint(0, self.cols//4), random.randint(0, self.rows//4)
        self.start_pos = (start_x, start_y)
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
    
    def reset_maze(self, triggered_button_pos=None):
        """Reorganize the maze walls and move reset buttons"""
        # Reset all walls and cell states
        for x in range(self.cols):
            for y in range(self.rows):
                self.grid[x][y].walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
                self.grid[x][y].visited = False
                self.grid[x][y].triggered = False
        
        # Regenerate maze with same dimensions
        start_x, start_y = self.start_pos
        self.grid[start_x][start_y].visited = True
        walls = self.get_wall_list(self.grid[start_x][start_y], self.grid)
        
        while walls:
            wall = random.choice(walls)
            walls.remove(wall)
            
            x, y = wall[1].x, wall[1].y
            if not self.grid[x][y].visited:
                self.grid[wall[0].x][wall[0].y].walls[wall[2]] = False
                self.grid[x][y].walls[self.opposite_wall(wall[2])] = False
                self.grid[x][y].visited = True
                walls.extend(self.get_wall_list(self.grid[x][y], self.grid))
        
        # Reset special effects (including teleports)
        self.special_effects = SpecialEffects(self)
        self.special_effects.generate_special_cells()
        
        # Don't place a button where the triggering button was
        self.relocate_reset_buttons(triggered_button_pos)

    def relocate_reset_buttons(self, exclude_pos=None):
        """Move all reset buttons to new random locations"""
        # First clear all existing buttons
        for x in range(self.cols):
            for y in range(self.rows):
                if self.grid[x][y].type == CellType.BUTTON:
                    self.grid[x][y].type = CellType.NORMAL
        
        # Place new buttons
        button_count = 3
        placed_buttons = 0
        attempts = 0
        max_attempts = 100
        
        while placed_buttons < button_count and attempts < max_attempts:
            attempts += 1
            x = random.randint(0, self.cols-1)
            y = random.randint(0, self.rows-1)
            
            # Skip if this is the excluded position or start/exit positions
            if (exclude_pos and (x,y) == exclude_pos) or \
            (x,y) == self.start_pos or \
            (x,y) == self.exit_pos or \
            self.grid[x][y].type != CellType.NORMAL:
                continue
            
            self.grid[x][y].type = CellType.BUTTON
            placed_buttons += 1
    
    def check_special_cells(self, player_rect):
        """Delegate special cell checking to SpecialEffects"""
        return self.special_effects.check_special_cells(player_rect)

    def draw(self, screen, camera, visited_cells, player_direction, player_pos):
        current_time = pygame.time.get_ticks()
        
        for x in range(self.cols):
            for y in range(self.rows):
                if (x, y) not in visited_cells:
                    continue
                    
                cell = self.grid[x][y]
                cell.visible = True
                cx = x * CELL_SIZE
                cy = y * CELL_SIZE
                
                # Draw cell background based on type
                path_rect = pygame.Rect(
                    cx + (CELL_SIZE - PATH_WIDTH)//2,
                    cy + (CELL_SIZE - PATH_WIDTH)//2,
                    PATH_WIDTH,
                    PATH_WIDTH
                )
                
                if cell.type == CellType.TRAP and cell.triggered:
                    color = (200, 0, 0)  # Red for triggered trap
                elif cell.type == CellType.TRAP:
                    color = (100, 0, 0)  # Dark red for trap
                elif cell.type == CellType.TELEPORT:
                    color = (0, 100, 200)  # Blue for teleporter
                elif cell.type == CellType.BUTTON:
                    color = (200, 200, 0)  # Yellow for button
                elif cell.type == CellType.EXIT:
                    color = (0, 200, 0)  # Green for exit
                else:
                    color = (30, 30, 40)  # Default color
                
                pygame.draw.rect(screen, color, camera.apply(path_rect))
                
                # Draw walls
                wall_color = (200, 200, 210)
                if cell.walls['top']:
                    wall_rect = pygame.Rect(cx, cy, CELL_SIZE, WALL_THICKNESS)
                    pygame.draw.rect(screen, wall_color, camera.apply(wall_rect))
                if cell.walls['right']:
                    wall_rect = pygame.Rect(cx + CELL_SIZE - WALL_THICKNESS, cy, 
                                           WALL_THICKNESS, CELL_SIZE)
                    pygame.draw.rect(screen, wall_color, camera.apply(wall_rect))
                if cell.walls['bottom']:
                    wall_rect = pygame.Rect(cx, cy + CELL_SIZE - WALL_THICKNESS, 
                                           CELL_SIZE, WALL_THICKNESS)
                    pygame.draw.rect(screen, wall_color, camera.apply(wall_rect))
                if cell.walls['left']:
                    wall_rect = pygame.Rect(cx, cy, WALL_THICKNESS, CELL_SIZE)
                    pygame.draw.rect(screen, wall_color, camera.apply(wall_rect))
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen, camera, player_direction, player_pos)

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
    
    def check_collision(self, rect):
        """Check if a rectangle collides with maze walls"""
        grid_x = rect.centerx // CELL_SIZE
        grid_y = rect.centery // CELL_SIZE
        
        if not (0 <= grid_x < self.cols and 0 <= grid_y < self.rows):
            return True
            
        cell = self.grid[grid_x][grid_y]
        
        margin = (CELL_SIZE - PATH_WIDTH)//2
        if (cell.walls['left'] and rect.left < grid_x * CELL_SIZE + margin) or \
        (cell.walls['right'] and rect.right > (grid_x+1) * CELL_SIZE - margin) or \
        (cell.walls['top'] and rect.top < grid_y * CELL_SIZE + margin) or \
        (cell.walls['bottom'] and rect.bottom > (grid_y+1) * CELL_SIZE - margin):
            return True
            
        return False