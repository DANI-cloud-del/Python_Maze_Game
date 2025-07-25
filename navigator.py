import heapq
from collections import deque
import pygame
from utils.settings import *

class Navigator:
    def __init__(self, maze):
        self.maze = maze
        self.path = []
        self.current_target = None
        self.visible = False
        self.position = None
        self.algorithm = "a_star"  # Default algorithm
        self.normal_color = (255, 255, 255)  # White
        self.alert_color = (255, 0, 0)       # Red
        self.current_color = self.normal_color
        self.last_enemy_check = 0
        self.enemy_check_interval = 500  # ms between enemy checks
        self.follow_mode = False  # Toggle between pathfinding and follow modes
        self.follow_distance = 2  # Cells behind player to follow
        self.last_player_direction = None
        self.smooth_position = None  # For smooth movement
        self.speed = 0.05  # Movement speed (0-1)
        self.last_player_cell = None  # To track player movement
        self.current_direction = None  # Current suggested direction
        self.next_direction = None  # Next suggested direction
        self.direction_changed = False  # Flag for direction change
        self.deviation_threshold = 1  # Cells player can deviate before recalculating

    def toggle_follow_mode(self):
        """Toggle between pathfinding and follow modes"""
        self.follow_mode = not self.follow_mode
        if self.follow_mode:
            self.path = []  # Clear path when switching to follow mode
            self.current_target = None
        
    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
        
    def check_for_enemies(self, current_time):
        """Check if enemies are nearby and update color accordingly"""
        if current_time - self.last_enemy_check < self.enemy_check_interval:
            return
            
        self.last_enemy_check = current_time
        
        if not self.position:
            self.current_color = self.normal_color
            return
            
        # Convert position to cell coordinates
        bot_cell_x = int(self.position[0] / CELL_SIZE)
        bot_cell_y = int(self.position[1] / CELL_SIZE)
        
        # Check for enemies in adjacent cells
        enemy_nearby = False
        for enemy in self.maze.enemies:
            if abs(enemy.x - bot_cell_x) <= 1 and abs(enemy.y - bot_cell_y) <= 1:
                enemy_nearby = True
                break
                
        self.current_color = self.alert_color if enemy_nearby else self.normal_color
    
    def find_path(self, start, end):
        if self.algorithm == "dfs":
            return self.dfs(start, end)
        elif self.algorithm == "bfs":
            return self.bfs(start, end)
        elif self.algorithm == "a_star":
            return self.a_star(start, end)
        return []
    
    def dfs(self, start, end):
        stack = [(start, [start])]
        visited = set()
        
        while stack:
            (x, y), path = stack.pop()
            if (x, y) == end:
                return path
            if (x, y) not in visited:
                visited.add((x, y))
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.maze.cols and 0 <= ny < self.maze.rows and 
                        not self.maze.grid[x][y].walls[
                            'right' if dx == 1 else 'left' if dx == -1 else 
                            'bottom' if dy == 1 else 'top']):
                        stack.append(((nx, ny), path + [(nx, ny)]))
        return []
    
    def bfs(self, start, end):
        queue = deque([(start, [start])])
        visited = set()
        
        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == end:
                return path
            if (x, y) not in visited:
                visited.add((x, y))
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.maze.cols and 0 <= ny < self.maze.rows and 
                        not self.maze.grid[x][y].walls[
                            'right' if dx == 1 else 'left' if dx == -1 else 
                            'bottom' if dy == 1 else 'top']):
                        queue.append(((nx, ny), path + [(nx, ny)]))
        return []
    
    def a_star(self, start, end):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
            
        heap = []
        heapq.heappush(heap, (0, start, [start]))
        visited = set()
        
        while heap:
            cost, (x, y), path = heapq.heappop(heap)
            if (x, y) == end:
                return path
            if (x, y) not in visited:
                visited.add((x, y))
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.maze.cols and 0 <= ny < self.maze.rows and 
                        not self.maze.grid[x][y].walls[
                            'right' if dx == 1 else 'left' if dx == -1 else 
                            'bottom' if dy == 1 else 'top']):
                        new_cost = cost + 1
                        heapq.heappush(heap, (new_cost + heuristic((nx, ny), end), 
                                         (nx, ny), path + [(nx, ny)]))
        return []
    
    def calculate_directions(self, player_cell):
        """Calculate current and next directions based on path"""
        if len(self.path) < 2:
            self.current_direction = None
            self.next_direction = None
            return
            
        # Current direction (from player to next cell)
        next_cell = self.path[0]
        dx = next_cell[0] - player_cell[0]
        dy = next_cell[1] - player_cell[1]
        self.current_direction = self.vector_to_direction((dx, dy))
        
        # Next direction (from next cell to following cell)
        if len(self.path) > 1:
            following_cell = self.path[1]
            dx = following_cell[0] - next_cell[0]
            dy = following_cell[1] - next_cell[1]
            self.next_direction = self.vector_to_direction((dx, dy))
        else:
            self.next_direction = None
    
    def vector_to_direction(self, vector):
        """Convert a movement vector to a direction string"""
        dx, dy = vector
        if dx == 1:
            return "right"
        elif dx == -1:
            return "left"
        elif dy == 1:
            return "down"
        elif dy == -1:
            return "up"
        return None
    
    def has_player_deviated(self, player_cell):
        """Check if player has moved away from the suggested path"""
        if not self.path or len(self.path) < 1:
            return True
            
        # Check if player is at expected position or adjacent
        expected_cell = self.path[0]
        distance = abs(player_cell[0] - expected_cell[0]) + abs(player_cell[1] - expected_cell[1])
        return distance > self.deviation_threshold
    
    def calculate_follow_position(self, player_pos, player_direction):
        """Calculate position behind the player based on direction"""
        player_cell_x = player_pos[0] // CELL_SIZE
        player_cell_y = player_pos[1] // CELL_SIZE
        
        # Convert direction to vector (inverted for following behind)
        if player_direction == "up":
            dx, dy = 0, self.follow_distance
        elif player_direction == "down":
            dx, dy = 0, -self.follow_distance
        elif player_direction == "left":
            dx, dy = self.follow_distance, 0
        elif player_direction == "right":
            dx, dy = -self.follow_distance, 0
        else:
            dx, dy = 0, 0
        
        # Calculate target cell behind player
        target_x = player_cell_x + dx
        target_y = player_cell_y + dy
        
        # Ensure target is within bounds and accessible
        target_x = max(0, min(target_x, self.maze.cols - 1))
        target_y = max(0, min(target_y, self.maze.rows - 1))
        
        # Check if the target cell is accessible
        if not self.is_cell_accessible(target_x, target_y):
            # Try adjacent cells if primary target is blocked
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                alt_x, alt_y = player_cell_x + dx, player_cell_y + dy
                if (0 <= alt_x < self.maze.cols and 0 <= alt_y < self.maze.rows and
                    self.is_cell_accessible(alt_x, alt_y)):
                    target_x, target_y = alt_x, alt_y
                    break
        
        # Convert back to pixel coordinates
        return (
            target_x * CELL_SIZE + CELL_SIZE//2,
            target_y * CELL_SIZE + CELL_SIZE//2
        )
    
    def is_cell_accessible(self, x, y):
        """Check if a cell is accessible (not blocked by walls from adjacent cells)"""
        # Check all four possible wall configurations
        accessible = True
        if x > 0 and self.maze.grid[x][y].walls['left']:
            accessible = False
        if x < self.maze.cols-1 and self.maze.grid[x][y].walls['right']:
            accessible = False
        if y > 0 and self.maze.grid[x][y].walls['top']:
            accessible = False
        if y < self.maze.rows-1 and self.maze.grid[x][y].walls['bottom']:
            accessible = False
        return accessible
    
    def update(self, player_pos, player_direction, current_time, force_recalculate=False):
        if not self.visible:
            return
            
        # Check for nearby enemies
        self.check_for_enemies(current_time)
            
        player_cell = (player_pos[0] // CELL_SIZE, player_pos[1] // CELL_SIZE)
        
        if self.follow_mode:
            # In follow mode, just calculate position behind player
            target_pos = self.calculate_follow_position(player_pos, player_direction)
            
            # Smooth movement toward target
            if self.smooth_position is None:
                self.smooth_position = self.position if self.position else target_pos
            
            # Calculate direction vector
            dx = target_pos[0] - self.smooth_position[0]
            dy = target_pos[1] - self.smooth_position[1]
            
            # Move toward target
            self.smooth_position = (
                self.smooth_position[0] + dx * self.speed,
                self.smooth_position[1] + dy * self.speed
            )
            
            self.position = self.smooth_position
        else:
            # In pathfinding mode with turn-by-turn directions
            player_moved = (self.last_player_cell != player_cell)
            self.last_player_cell = player_cell
            
            # Recalculate path if:
            # 1. Forced to recalculate
            # 2. No path exists
            # 3. Player has reached the next cell in path
            # 4. Player has deviated from the path
            if (force_recalculate or not self.path or 
                (player_moved and len(self.path) > 0 and player_cell == self.path[0]) or
                self.has_player_deviated(player_cell)):
                
                self.path = self.find_path(player_cell, self.maze.exit_pos)
                if self.path:
                    self.current_target = self.path[0]  # Next cell to move to
                else:
                    self.current_target = None
            
            # Calculate directions for navigation hints
            if player_moved and self.path:
                self.calculate_directions(player_cell)
            
            # Update bot position to stay near player
            if self.current_target:
                target_x, target_y = self.current_target
                self.position = (
                    target_x * CELL_SIZE + CELL_SIZE//2,
                    target_y * CELL_SIZE + CELL_SIZE//2
                )

    def draw(self, screen, camera):
        if not self.visible or not self.position:
            return
            
        # Draw bot (simple circle with color based on enemy proximity)
        adjusted_pos = camera.apply_pos(self.position)
        pygame.draw.circle(screen, self.current_color, adjusted_pos, 10)
        
        # Draw path if we're in pathfinding mode and have a path
        if not self.follow_mode and self.path:
            for i, (x, y) in enumerate(self.path):
                if i < len(self.path) - 1:  # Don't draw line to exit
                    next_x, next_y = self.path[i+1]
                    start_pos = camera.apply_pos((
                        x * CELL_SIZE + CELL_SIZE//2,
                        y * CELL_SIZE + CELL_SIZE//2
                    ))
                    end_pos = camera.apply_pos((
                        next_x * CELL_SIZE + CELL_SIZE//2,
                        next_y * CELL_SIZE + CELL_SIZE//2
                    ))
                    pygame.draw.line(screen, (0, 255, 0, 150), start_pos, end_pos, 3)
        # Navigation arrows removed
