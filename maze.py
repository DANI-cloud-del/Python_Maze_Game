import random
import pygame
from utils.settings import *
from enum import Enum

class CellType(Enum):
    NORMAL = 0
    TRAP = 1
    TELEPORT = 2
    BUTTON = 3
    EXIT = 4

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False
        self.type = CellType.NORMAL
        self.linked_teleport = None
        self.triggered = False
        self.visible = False

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 1
        self.aggression = 0.5  # 0-1 how aggressive the enemy is
        self.detection_radius = 3  # cells
        self.visible = False
    
    def move_toward_player(self, player_x, player_y, maze):
        # Simple AI: move toward player when not in light
        dx = 1 if player_x > self.x else -1 if player_x < self.x else 0
        dy = 1 if player_y > self.y else -1 if player_y < self.y else 0
        
        # Randomize movement sometimes
        if random.random() > self.aggression:
            dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        
        # Check if movement is possible
        if maze.can_move(self.x, self.y, (dx, dy)):
            self.x += dx
            self.y += dy
    
    def draw(self, screen, camera, player_direction, player_pos):
        # Only draw if visible and not in player's view direction
        if not self.visible:
            return
            
        # Calculate if enemy is in player's peripheral vision
        player_cell_x, player_cell_y = player_pos
        rel_x, rel_y = self.x - player_cell_x, self.y - player_cell_y
        dot_product = player_direction.x * rel_x + player_direction.y * rel_y
        
        # Enemy is more visible when directly in front
        if dot_product < 0:  # Behind player
            return
            
        # Draw enemy
        cx = self.x * CELL_SIZE + CELL_SIZE//2
        cy = self.y * CELL_SIZE + CELL_SIZE//2
        adjusted_pos = camera.apply_pos((cx, cy))
        radius = int(CELL_SIZE * 0.3 * camera.zoom)
        
        # Fixed alpha calculation line:
        visibility = 0.3 + 0.7 * dot_product / (abs(rel_x) + abs(rel_y) + 0.1)
        alpha = min(255, max(50, int(255 * visibility)))
        
        enemy_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(enemy_surface, (255, 0, 0, alpha), (radius, radius), radius)
        screen.blit(enemy_surface, (adjusted_pos[0]-radius, adjusted_pos[1]-radius))

class Maze:
    def __init__(self):
        self.cols = MAZE_COLS * 2  # Bigger maze
        self.rows = MAZE_ROWS * 2
        self.grid = self.generate_maze()
        self.enemies = []
        self.start_pos = (0, 0)
        self.exit_pos = (self.cols-1, self.rows-1)
        self.generate_special_cells()
        self.generate_enemies()
        self.reset_time = 0
        self.reset_cooldown = 10000  # ms before maze can reset again
        
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
    
    def generate_enemies(self):
        enemy_count = 5
        for _ in range(enemy_count):
            while True:
                x, y = random.randint(0, self.cols-1), random.randint(0, self.rows-1)
                # Ensure enemies aren't too close to start
                if abs(x - self.start_pos[0]) + abs(y - self.start_pos[1]) > 10:
                    self.enemies.append(Enemy(x, y))
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
    
    def check_special_cells(self, player_rect):
        """Check if player is on a special cell and trigger effects"""
        x = player_rect.centerx // CELL_SIZE
        y = player_rect.centery // CELL_SIZE
        
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return None
            
        cell = self.grid[x][y]
        
        if cell.type == CellType.TRAP and not cell.triggered:
            cell.triggered = True
            return "trap"  # Player takes damage
        
        elif cell.type == CellType.TELEPORT and not cell.triggered:
            cell.triggered = True  # Prevent immediate re-trigger
            return "teleport", cell.linked_teleport
        
        elif cell.type == CellType.BUTTON and not cell.triggered:
            current_time = pygame.time.get_ticks()
            if current_time - self.reset_time > self.reset_cooldown:
                cell.triggered = True
                self.reset_time = current_time
                self.reset_maze()
                return "maze_reset"
        
        elif cell.type == CellType.EXIT:
            return "exit"
            
        return None
    
    def reset_maze(self):
        """Reorganize the maze walls"""
        # Reset all walls
        for x in range(self.cols):
            for y in range(self.rows):
                self.grid[x][y].walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
                self.grid[x][y].visited = False
        
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
        
        # Reset triggers but keep cell types
        for x in range(self.cols):
            for y in range(self.rows):
                self.grid[x][y].triggered = False
    
    def update_enemies(self, player_pos, player_direction, player_light_on):
        """Update enemy positions based on player state"""
        player_x = player_pos[0] // CELL_SIZE
        player_y = player_pos[1] // CELL_SIZE
        
        for enemy in self.enemies:
            # Determine if enemy is visible to player
            rel_x, rel_y = enemy.x - player_x, enemy.y - player_y
            distance = (rel_x**2 + rel_y**2)**0.5
            
            # Enemy is visible if in light and in front of player
            dot_product = player_direction.x * rel_x + player_direction.y * rel_y
            enemy.visible = (distance < 5 and dot_product > -0.5 and player_light_on)
            
            # Move toward player when not looking directly at them
            if not enemy.visible or random.random() > 0.8:
                enemy.move_toward_player(player_x, player_y, self)