import heapq
from collections import deque
import pygame
import random
from utils.settings import *
from cell import CellType

class Navigator:
    def __init__(self, maze):
        self.maze = maze
        self.path = []
        self.current_target = None
        self.visible = True
        self.position = (maze.start_pos[0] * CELL_SIZE, maze.start_pos[1] * CELL_SIZE)
        self.algorithm = "a_star"
        self.normal_color = (255, 255, 255)
        self.alert_color = (255, 0, 0)
        self.current_color = self.normal_color
        self.last_enemy_check = 0
        self.enemy_check_interval = 500
        self.follow_distance = 2
        self.speed = 0.5  # Increased speed for faster movement
        self.follow_mode = True
        self.exploration_path = []
        self.exploration_mode = False
        self.explored_cells = set()
        self.last_exploration_update = 0
        self.exploration_interval = 80  # Faster exploration updates
        self.returning_to_player = False
        self.found_exit = False
        self.special_cell_info = {
            CellType.TRAP: {"color": (255, 0, 0), "name": "Trap"},
            CellType.TELEPORT: {"color": (0, 100, 255), "name": "Teleport"},
            CellType.BUTTON: {"color": (255, 255, 0), "name": "Button"},
            CellType.EXIT: {"color": (0, 255, 0), "name": "Exit"},
            CellType.BATTERY: {"color": (0, 255, 255), "name": "Battery"},
            CellType.AMMO: {"color": (255, 165, 0), "name": "Ammo"}
        }
        self.knowledge = {
            "teleports": set(),
            "buttons": set(),
            "exit": None
        }
        self.last_path_update = 0
        self.path_update_interval = 300  # More frequent path updates
        self.smooth_position = None  # For smooth follow movement

    def toggle_follow_mode(self):
        """Toggle between follow mode and exploration mode"""
        if not self.follow_mode:
            # Switching to follow mode
            self.follow_mode = True
            self.exploration_mode = False
            self.returning_to_player = False
            self.found_exit = False
        else:
            # Switching to exploration mode
            self.follow_mode = False
            self.exploration_mode = True
            self.explored_cells = set()
            player_cell = (int(self.position[0] // CELL_SIZE), int(self.position[1] // CELL_SIZE))
            self.explored_cells.add(player_cell)
            self.exploration_path = self.generate_exploration_path(player_cell)
            self.returning_to_player = False
            self.found_exit = False

    def generate_exploration_path(self, start_cell):
        """Generate path exploring unknown areas using selected algorithm"""
        if self.algorithm == "dfs":
            return self.dfs_explore(start_cell)
        elif self.algorithm == "bfs":
            return self.bfs_explore(start_cell)
        else:  # A*
            return self.a_star_explore(start_cell)

    def dfs_explore(self, start_cell):
        """Depth-First Search exploration"""
        stack = [(start_cell, [start_cell])]
        visited = set()
        path = []
        
        while stack:
            (x, y), current_path = stack.pop()
            if (x, y) not in visited:
                visited.add((x, y))
                path.append((x, y))
                
                # Check if we found the exit
                if (x, y) == self.maze.exit_pos:
                    self.found_exit = True
                    return path
                
                # Explore neighbors in random order
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                random.shuffle(directions)
                
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.maze.cols and 0 <= ny < self.maze.rows and
                        not self.maze.grid[x][y].walls[
                            'right' if dx == 1 else 'left' if dx == -1 else 
                            'bottom' if dy == 1 else 'top']):
                        stack.append(((nx, ny), current_path + [(nx, ny)]))
        return path

    def bfs_explore(self, start_cell):
        """Breadth-First Search exploration"""
        queue = deque([(start_cell, [start_cell])])
        visited = set()
        path = []
        
        while queue:
            (x, y), current_path = queue.popleft()
            if (x, y) not in visited:
                visited.add((x, y))
                path.append((x, y))
                
                if (x, y) == self.maze.exit_pos:
                    self.found_exit = True
                    return path
                
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.maze.cols and 0 <= ny < self.maze.rows and
                        not self.maze.grid[x][y].walls[
                            'right' if dx == 1 else 'left' if dx == -1 else 
                            'bottom' if dy == 1 else 'top']):
                        queue.append(((nx, ny), current_path + [(nx, ny)]))
        return path

    def a_star_explore(self, start_cell):
        """A* exploration with frontier heuristic"""
        def heuristic(cell, frontier):
            # Prefer cells that are far from explored areas
            if not frontier:
                return 0
            distances = [abs(cell[0]-f[0]) + abs(cell[1]-f[1]) for f in frontier]
            return -min(distances)  # Negative because we want max distance
            
        heap = []
        heapq.heappush(heap, (0, start_cell, [start_cell]))
        visited = set()
        path = []
        frontier = set([start_cell])
        
        while heap:
            _, (x, y), current_path = heapq.heappop(heap)
            if (x, y) not in visited:
                visited.add((x, y))
                path.append((x, y))
                
                if (x, y) == self.maze.exit_pos:
                    self.found_exit = True
                    return path
                
                frontier.remove((x, y))
                
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.maze.cols and 0 <= ny < self.maze.rows and
                        not self.maze.grid[x][y].walls[
                            'right' if dx == 1 else 'left' if dx == -1 else 
                            'bottom' if dy == 1 else 'top'] and
                        (nx, ny) not in visited):
                        
                        frontier.add((nx, ny))
                        priority = heuristic((nx, ny), frontier)
                        heapq.heappush(heap, (priority, (nx, ny), current_path + [(nx, ny)]))
        return path

    def update_knowledge(self, cell_pos):
        """Update knowledge about special cells"""
        x, y = cell_pos
        cell = self.maze.grid[x][y]
        
        if cell.type == CellType.TRAP:
            pass  # Just track for visualization
        elif cell.type == CellType.TELEPORT and cell.linked_teleport:
            self.knowledge["teleports"].add((x, y))
            self.knowledge["teleports"].add(cell.linked_teleport)
        elif cell.type == CellType.BUTTON:
            self.knowledge["buttons"].add((x, y))
        elif cell.type == CellType.EXIT:
            self.knowledge["exit"] = (x, y)
            self.found_exit = True

    def set_algorithm(self, algorithm):
        """Set the pathfinding algorithm"""
        algo = algorithm.lower()
        if algo == "a*" or algo == "a_star" or algo == "astar":
            self.algorithm = "a_star"
        else:
            self.algorithm = algo

    def check_for_enemies(self, current_time):
        """Check for nearby enemies and update alert status"""
        if current_time - self.last_enemy_check < self.enemy_check_interval:
            return
            
        self.last_enemy_check = current_time
        
        if not self.position:
            self.current_color = self.normal_color
            return
            
        bot_cell_x = int(self.position[0] / CELL_SIZE)
        bot_cell_y = int(self.position[1] / CELL_SIZE)
        
        enemy_nearby = False
        for enemy in self.maze.enemies:
            if abs(enemy.x - bot_cell_x) <= 1 and abs(enemy.y - bot_cell_y) <= 1:
                enemy_nearby = True
                break
                
        self.current_color = self.alert_color if enemy_nearby else self.normal_color

    def find_path(self, start, end):
        """Find path using the selected algorithm"""
        if self.algorithm == "dfs":
            return self.dfs(start, end)
        elif self.algorithm == "bfs":
            return self.bfs(start, end)
        elif self.algorithm == "a_star":
            return self.a_star(start, end)
        return []

    def dfs(self, start, end):
        """Depth-First Search pathfinding"""
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
        """Breadth-First Search pathfinding"""
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
        """A* pathfinding with Manhattan distance heuristic"""
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

    def calculate_follow_position(self, player_pos, player_direction):
        """Calculate position behind player based on direction"""
        player_cell_x = player_pos[0] // CELL_SIZE
        player_cell_y = player_pos[1] // CELL_SIZE
        
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
        
        target_x = player_cell_x + dx
        target_y = player_cell_y + dy
        
        target_x = max(0, min(target_x, self.maze.cols - 1))
        target_y = max(0, min(target_y, self.maze.rows - 1))
        
        if not self.is_cell_accessible(target_x, target_y):
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                alt_x, alt_y = player_cell_x + dx, player_cell_y + dy
                if (0 <= alt_x < self.maze.cols and 0 <= alt_y < self.maze.rows and
                    self.is_cell_accessible(alt_x, alt_y)):
                    target_x, target_y = alt_x, alt_y
                    break
        
        return (
            target_x * CELL_SIZE + CELL_SIZE//2,
            target_y * CELL_SIZE + CELL_SIZE//2
        )

    def is_cell_accessible(self, x, y):
        """Check if cell is accessible (not blocked by walls)"""
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
        """Update navigator state"""
        if not self.visible:
            return
            
        self.check_for_enemies(current_time)
        player_cell = (player_pos[0] // CELL_SIZE, player_pos[1] // CELL_SIZE)
        
        # Update knowledge of player's current cell
        self.update_knowledge(player_cell)
        
        if self.follow_mode:
            # Follow mode - stay behind player
            target_pos = self.calculate_follow_position(player_pos, player_direction)
            
            # Smooth movement
            if self.smooth_position is None:
                self.smooth_position = self.position
                
            dx = target_pos[0] - self.smooth_position[0]
            dy = target_pos[1] - self.smooth_position[1]
            
            self.smooth_position = (
                self.smooth_position[0] + dx * 0.2,  # Smoothing factor
                self.smooth_position[1] + dy * 0.2
            )
            
            self.position = self.smooth_position
            
        elif self.exploration_mode:
            # Exploration mode - explore the maze
            if current_time - self.last_exploration_update < self.exploration_interval:
                return
                
            self.last_exploration_update = current_time
            
            if not self.exploration_path:
                if not self.returning_to_player:
                    # Find path back to player
                    current_cell = (int(self.position[0] // CELL_SIZE), int(self.position[1] // CELL_SIZE))
                    self.exploration_path = self.find_path(current_cell, player_cell)
                    self.returning_to_player = True
                else:
                    # Finished returning to player
                    self.exploration_mode = False
                    if self.found_exit:
                        # Now find path to exit
                        self.path = self.find_path(player_cell, self.knowledge["exit"])
                    return
            
            if self.exploration_path:
                next_cell = self.exploration_path[0]
                target_pos = (
                    next_cell[0] * CELL_SIZE + CELL_SIZE//2,
                    next_cell[1] * CELL_SIZE + CELL_SIZE//2
                )
                
                current_cell = (int(self.position[0] // CELL_SIZE), int(self.position[1] // CELL_SIZE))
                if current_cell == next_cell:
                    self.exploration_path.pop(0)
                    if not self.returning_to_player:
                        self.explored_cells.add(current_cell)
                        self.update_knowledge(current_cell)
                        if current_cell == self.maze.exit_pos:
                            self.found_exit = True
                            return
                else:
                    # Move toward target
                    dx = target_pos[0] - self.position[0]
                    dy = target_pos[1] - self.position[1]
                    self.position = (
                        self.position[0] + dx * self.speed,
                        self.position[1] + dy * self.speed
                    )
        else:
            # Pathfinding mode - go to exit
            if not self.found_exit:
                self.exploration_mode = True
                return
                
            if (force_recalculate or 
                current_time - self.last_path_update > self.path_update_interval or
                (self.path and player_cell == self.path[0])):
                
                self.last_path_update = current_time
                self.path = self.find_path(player_cell, self.knowledge["exit"])
                if self.path:
                    self.current_target = self.path[0]
                else:
                    self.current_target = None
            
            if self.current_target:
                target_x, target_y = self.current_target
                self.position = (
                    target_x * CELL_SIZE + CELL_SIZE//2,
                    target_y * CELL_SIZE + CELL_SIZE//2
                )

    def draw(self, screen, camera):
        """Draw navigator and its information"""
        if not self.visible or not self.position:
            return
            
        # Draw bot
        adjusted_pos = camera.apply_pos(self.position)
        pygame.draw.circle(screen, self.current_color, adjusted_pos, 10)
        
        # Draw path if in pathfinding mode
        if not self.follow_mode and self.path:
            for i in range(len(self.path)-1):
                start = camera.apply_pos((
                    self.path[i][0] * CELL_SIZE + CELL_SIZE//2,
                    self.path[i][1] * CELL_SIZE + CELL_SIZE//2
                ))
                end = camera.apply_pos((
                    self.path[i+1][0] * CELL_SIZE + CELL_SIZE//2,
                    self.path[i+1][1] * CELL_SIZE + CELL_SIZE//2
                ))
                pygame.draw.line(screen, (0, 255, 0, 150), start, end, 3)
        
        # Draw explored cells
        for x, y in self.explored_cells:
            center = camera.apply_pos((
                x * CELL_SIZE + CELL_SIZE//2,
                y * CELL_SIZE + CELL_SIZE//2
            ))
            pygame.draw.circle(screen, (100, 100, 150, 50), center, 3)
        
        # Draw special cells
        for cell_type, info in self.special_cell_info.items():
            if cell_type == CellType.TRAP:
                # Only show traps that have been explored
                for x, y in self.explored_cells:
                    if self.maze.grid[x][y].type == CellType.TRAP:
                        self.draw_special_cell(screen, camera, (x, y), info["color"])
            elif cell_type == CellType.EXIT and self.knowledge["exit"]:
                self.draw_special_cell(screen, camera, self.knowledge["exit"], info["color"])

    def draw_special_cell(self, screen, camera, pos, color):
        """Draw a special cell marker"""
        x, y = pos
        center = camera.apply_pos((
            x * CELL_SIZE + CELL_SIZE//2,
            y * CELL_SIZE + CELL_SIZE//2
        ))
        radius = int(6 * camera.zoom)
        pygame.draw.circle(screen, color, center, radius)