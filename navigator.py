import heapq
from collections import deque
import pygame
import random
import math
from utils.settings import *
from cell import CellType

class ChildBot:
    def __init__(self, mother, start_pos, exploration_quadrant=None):
        self.mother = mother
        self.position = (start_pos[0], start_pos[1])
        self.target_position = None
        self.path = []
        self.speed = 2.0  # Increase from 0.7
        self.color = (100, 200, 255)  # Light blue
        self.radius = 5  # Smaller than mother
        self.state = "exploring"  # exploring, reporting, returning
        self.found_exit = False
        self.knowledge = {
            "traps": set(),
            "teleports": set(),
            "buttons": set(),
            "exit": None
        }
        self.last_report_time = 0
        self.report_interval = 1000  # Time to report to mother
        self.current_target = None
        self.exploration_timer = 0
        self.exploration_interval = 2000  # Reduce from 5000
        self.knowledge_sharing_interval = 500  # Share every 0.5 seconds
        self.last_knowledge_share = 0
        self.max_path_length = 10  # Limit path length for more frequent updates
        self.exploration_quadrant = exploration_quadrant
        self.stuck_timer = 0
        self.last_position = start_pos

    def update_knowledge(self, cell_pos):
        x, y = cell_pos
        cell = self.mother.maze.grid[x][y]
        
        if cell.type == CellType.TRAP:
            self.knowledge["traps"].add((x, y))
        elif cell.type == CellType.TELEPORT and cell.linked_teleport:
            self.knowledge["teleports"].add((x, y))
            self.knowledge["teleports"].add(cell.linked_teleport)
        elif cell.type == CellType.BUTTON:
            self.knowledge["buttons"].add((x, y))
        elif cell.type == CellType.EXIT:
            self.knowledge["exit"] = (x, y)
            self.found_exit = True
            # Immediately share with mother instead of returning
            self.share_knowledge()
            # Optionally continue exploring or mark as done
            self.state = "exploring"  # or "idle"
            
    def find_path(self, start, end):
        """Find path using mother's algorithm"""
        return self.mother.find_path(start, end)
    
    def explore(self):
        """Explore the maze with quadrant-based targeting"""
        current_cell = (int(self.position[0] // CELL_SIZE), 
                       int(self.position[1] // CELL_SIZE))
        
        # Check if stuck
        if math.dist(self.position, self.last_position) < 2:
            self.stuck_timer += 1
            if self.stuck_timer > 60:  # ~1 second of being stuck
                self.path = []
                self.stuck_timer = 0
        self.last_position = self.position

        # If we don't have a path, get a new one targeting our quadrant
        if not self.path:
            target = self.find_quadrant_target(current_cell)
            if not target:  # If no target in quadrant, look elsewhere
                target = self.find_distant_unexplored_cell(current_cell)
            
            if target:
                path = self.find_path(current_cell, target)
                if path and len(path) > 1:
                    self.path = path[:self.max_path_length]

        if self.path:
            self.follow_path()

    def follow_path(self):
        """Move along the current path"""
        if not self.path:
            return
        next_cell = self.path[0]
        target_pos = (
            next_cell[0] * CELL_SIZE + CELL_SIZE // 2,
            next_cell[1] * CELL_SIZE + CELL_SIZE // 2
        )
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < 5:
            self.path.pop(0)
        else:
            if distance > 0:
                dx, dy = dx / distance, dy / distance
            self.position = (
                self.position[0] + dx * self.speed,
                self.position[1] + dy * self.speed
            )

    def find_quadrant_target(self, current_cell):
        """Find target based on assigned quadrant"""
        cols, rows = self.mother.maze.cols, self.mother.maze.rows
        x, y = current_cell

        # Define quadrant boundaries
        if self.exploration_quadrant == 0:  # Top-left
            min_x, min_y, max_x, max_y = 0, 0, cols//2, rows//2
        elif self.exploration_quadrant == 1:  # Top-right
            min_x, min_y, max_x, max_y = cols//2, 0, cols, rows//2
        elif self.exploration_quadrant == 2:  # Bottom-left
            min_x, min_y, max_x, max_y = 0, rows//2, cols//2, rows
        elif self.exploration_quadrant == 3:  # Bottom-right
            min_x, min_y, max_x, max_y = cols//2, rows//2, cols, rows
        else:  # No quadrant assigned
            return None

        # Find closest unexplored cell in quadrant
        closest = None
        min_dist = float('inf')

        for tx in range(min_x, max_x):
            for ty in range(min_y, max_y):
                if (tx, ty) not in self.mother.explored_cells:
                    dist = abs(tx - x) + abs(ty - y)
                    if dist < min_dist:
                        min_dist = dist
                        closest = (tx, ty)

        return closest
    def find_closest_valid_cell(self):
        """Find closest valid cell when outside bounds"""
        current_x = int(self.position[0] // CELL_SIZE)
        current_y = int(self.position[1] // CELL_SIZE)
        
        # Search in expanding radius
        for radius in range(1, 5):
            for dx in range(-radius, radius+1):
                for dy in range(-radius, radius+1):
                    x, y = current_x + dx, current_y + dy
                    if (0 <= x < self.mother.maze.cols and 
                        0 <= y < self.mother.maze.rows):
                        return (x, y)
        return None

    def find_distant_unexplored_cell(self, current_cell):
        """Improved target selection with larger search radius"""
        unexplored = []
        cols, rows = self.mother.maze.cols, self.mother.maze.rows
        
        # Search in expanding concentric squares
        for radius in range(5, max(cols, rows), 5):
            min_x = max(0, current_cell[0] - radius)
            max_x = min(cols, current_cell[0] + radius)
            min_y = max(0, current_cell[1] - radius)
            max_y = min(rows, current_cell[1] + radius)
            
            for x in range(min_x, max_x):
                for y in range(min_y, max_y):
                    if (x,y) not in self.mother.explored_cells:
                        distance = abs(x - current_cell[0]) + abs(y - current_cell[1])
                        unexplored.append((distance, (x,y)))
            
            if unexplored:
                # Prioritize furthest unexplored cells
                unexplored.sort(reverse=True)
                return unexplored[0][1]
        
        return None
    
    def report_to_mother(self):
        """Improved reporting with path verification and debug output"""
        print(f"Child attempting to report (State: {self.state})")  # Debug
        
        mother_cell = (
            int(self.mother.position[0] // CELL_SIZE),
            int(self.mother.position[1] // CELL_SIZE)
        )
        current_cell = (
            int(self.position[0] // CELL_SIZE),
            int(self.position[1] // CELL_SIZE)
        )
        
        # Debug current positions
        print(f"Child at {current_cell}, Mother at {mother_cell}")
        
        # Check if we've reached mother
        if current_cell == mother_cell:
            print("Reached mother - sharing knowledge")  # Debug
            self.share_knowledge()
            self.state = "returning" if self.found_exit else "exploring"
            self.path = []
            return
        
        # If no path or invalid path, find new one
        if not self.path or not self.is_path_valid(self.path):
            print("Calculating new path to mother")  # Debug
            self.path = self.find_path(current_cell, mother_cell)
            
            # If still no path, try adjacent cells
            if not self.path:
                print("Trying adjacent cells to mother")  # Debug
                for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                    nx, ny = mother_cell[0]+dx, mother_cell[1]+dy
                    if (0 <= nx < self.mother.maze.cols and 
                        0 <= ny < self.mother.maze.rows):
                        self.path = self.find_path(current_cell, (nx, ny))
                        if self.path:
                            break
        
        # Follow path if available
        if self.path:
            print(f"Following path of length {len(self.path)}")  # Debug
            self.follow_path()
        else:
            print("No valid path - moving randomly toward mother")  # Debug
            self.move_randomly_toward_mother()
    
    def find_path_to_valid_cell(self, target_cell):
        """Find path back to valid area when outside bounds"""
        current_x = int(self.position[0] // CELL_SIZE)
        current_y = int(self.position[1] // CELL_SIZE)
        
        # Find nearest valid cell
        for radius in range(1, 5):
            for dx in range(-radius, radius+1):
                for dy in range(-radius, radius+1):
                    x, y = current_x + dx, current_y + dy
                    if (0 <= x < self.mother.maze.cols and 
                        0 <= y < self.mother.maze.rows):
                        path = self.find_path((x,y), target_cell)
                        if path:
                            return path
        return None

    def is_path_valid(self, path):
        """Check if all cells in path are valid"""
        for cell in path:
            if not (0 <= cell[0] < self.mother.maze.cols and 
                    0 <= cell[1] < self.mother.maze.rows):
                return False
        return True

    def move_randomly_toward_mother(self):
        """Fallback movement when pathfinding fails"""
        mother_pos = self.mother.position
        dx = mother_pos[0] - self.position[0]
        dy = mother_pos[1] - self.position[1]
        distance = (dx**2 + dy**0.5)
        
        if distance > 0:
            dx, dy = dx/distance, dy/distance
            self.position = (
                self.position[0] + dx * self.speed,
                self.position[1] + dy * self.speed
            )

    def share_knowledge(self):
        """Share knowledge instantly without physical return"""
        # Share all knowledge
        for trap in self.knowledge["traps"]:
            self.mother.knowledge["traps"].add(trap)
        for teleport in self.knowledge["teleports"]:
            self.mother.knowledge["teleports"].add(teleport)
        for button in self.knowledge["buttons"]:
            self.mother.knowledge["buttons"].add(button)
        
        # Special handling for exit
        if self.knowledge["exit"]:
            self.mother.knowledge["exit"] = self.knowledge["exit"]
            self.mother.found_exit = True
            # Force mother to calculate path to exit
            current_pos = (int(self.mother.position[0] // CELL_SIZE),
                        int(self.mother.position[1] // CELL_SIZE))
            self.mother.exit_path = self.mother.find_path(current_pos, 
                                                        self.knowledge["exit"])

    def update(self, current_time):
        """Improved update with state verification"""
        # Debug current state
        if random.random() < 0.01:  # Occasionally print state
            print(f"Child state: {self.state}, Exit found: {self.found_exit}")
        
        # Share knowledge periodically
        if current_time - self.last_knowledge_share > self.knowledge_sharing_interval:
            self.share_knowledge()
            self.last_knowledge_share = current_time
        
        # Update explored cells
        current_cell = (
            int(self.position[0] // CELL_SIZE),
            int(self.position[1] // CELL_SIZE)
        )
        if (0 <= current_cell[0] < self.mother.maze.cols and 
            0 <= current_cell[1] < self.mother.maze.rows):
            self.mother.explored_cells.add(current_cell)
        
        # State handling with priority to reporting
        if self.state == "reporting":
            self.report_to_mother()
        elif self.state == "exploring":
            self.explore()
        elif self.state == "returning":
            if not self.found_exit:  # Only return if we haven't found exit yet
                self.report_to_mother()
    
    def find_new_exploration_target(self):
        """Find a new area to explore"""
        current_cell = (int(self.position[0] // CELL_SIZE), int(self.position[1] // CELL_SIZE))
        target = self.find_distant_unexplored_cell(current_cell)
        if target:
            self.path = self.find_path(current_cell, target)
    
    def draw(self, screen, camera):
        """Draw with enhanced state visualization"""
        adjusted_pos = camera.apply_pos(self.position)
        
        # Main body
        pygame.draw.circle(screen, self.color, adjusted_pos, self.radius)
        
        # State indicator (larger and more visible)
        state_colors = {
            "exploring": (100, 255, 100),  # Bright green
            "reporting": (255, 100, 100),  # Bright red
            "returning": (100, 100, 255)   # Bright blue
        }
        state_pos = (int(adjusted_pos[0]), int(adjusted_pos[1] - 15))
        pygame.draw.circle(screen, state_colors.get(self.state, (200, 200, 200)),
                        state_pos, 5)
        
        # Path visualization (if in reporting state)
        if self.state == "reporting" and self.path:
            path_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            for i, cell in enumerate(self.path):
                pos = camera.apply_pos((
                    cell[0] * CELL_SIZE + CELL_SIZE//2,
                    cell[1] * CELL_SIZE + CELL_SIZE//2
                ))
                pygame.draw.circle(path_surface, (255, 0, 0, 150), 
                                (int(pos[0]), int(pos[1])), 
                                3 + (i % 3))  # Varying size for visibility
            screen.blit(path_surface, (0, 0))

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
        self.speed = 0.5
        self.follow_mode = True
        self.exploration_path = []
        self.exploration_mode = False
        self.explored_cells = set()
        self.last_exploration_update = 0
        self.exploration_interval = 80
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
            "traps": set(),
            "teleports": set(),
            "buttons": set(),
            "exit": None
        }
        self.last_path_update = 0
        self.path_update_interval = 300
        self.smooth_position = None
        self.child_bots = []
        self.max_children = 4  # Number of child bots
        self.last_child_spawn = 0
        self.child_spawn_interval = 2000  # Spawn children every 2 seconds
        self.exit_path = None

    def spawn_children(self, current_time):
        """Spawn child bots if in exploration mode"""
        if (current_time - self.last_child_spawn < self.child_spawn_interval or 
            len(self.child_bots) >= self.max_children or 
            not self.exploration_mode):
            return
            
        self.last_child_spawn = current_time
        
        # Get valid spawn positions around mother
        valid_spawns = []
        current_cell = (int(self.position[0] // CELL_SIZE), 
                    int(self.position[1] // CELL_SIZE))
        
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = current_cell[0]+dx, current_cell[1]+dy
            if (0 <= nx < self.maze.cols and 
                0 <= ny < self.maze.rows and
                not self.maze.grid[current_cell[0]][current_cell[1]].walls[
                    'right' if dx==1 else 'left' if dx==-1 else
                    'bottom' if dy==1 else 'top']):
                valid_spawns.append((
                    nx * CELL_SIZE + CELL_SIZE//2,
                    ny * CELL_SIZE + CELL_SIZE//2
                ))
        
        # Spawn children at valid positions
        for i in range(min(self.max_children - len(self.child_bots), len(valid_spawns))):
            spawn_pos = valid_spawns[i]
            child = ChildBot(self, spawn_pos, exploration_quadrant=i)
            self.child_bots.append(child)
    
    def toggle_follow_mode(self):
        """Toggle between follow mode and exploration mode"""
        if not self.follow_mode:
            # Switching to follow mode - recall all children
            self.follow_mode = True
            self.exploration_mode = False
            self.child_bots = []
        else:
            # Switching to exploration mode
            self.follow_mode = False
            self.exploration_mode = True
            self.explored_cells = set()
            player_cell = (int(self.position[0] // CELL_SIZE), int(self.position[1] // CELL_SIZE))
            self.explored_cells.add(player_cell)
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
            self.knowledge["traps"].add((x, y))
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
        if not self.visible:
            return
            
        self.check_for_enemies(current_time)
        player_cell = (player_pos[0] // CELL_SIZE, player_pos[1] // CELL_SIZE)
        self.update_knowledge(player_cell)
        
        # Spawn child bots if in exploration mode
        self.spawn_children(current_time)
        
        # Add this line right here:
        if self.exploration_mode:  # Only update explored cells in exploration mode
            self.update_explored_cells(current_time)
        
        if self.follow_mode:
            # Follow mode - stay behind player
            target_pos = self.calculate_follow_position(player_pos, player_direction)
            
            if self.smooth_position is None:
                self.smooth_position = self.position
                
            dx = target_pos[0] - self.smooth_position[0]
            dy = target_pos[1] - self.smooth_position[1]
            
            self.smooth_position = (
                self.smooth_position[0] + dx * 0.2,
                self.smooth_position[1] + dy * 0.2
            )
            
            self.position = self.smooth_position
            
        elif self.exploration_mode:
            # Mother stays near player while children explore
            target_pos = self.calculate_follow_position(player_pos, player_direction)
            
            if self.smooth_position is None:
                self.smooth_position = self.position
                
            dx = target_pos[0] - self.smooth_position[0]
            dy = target_pos[1] - self.smooth_position[1]
            
            self.smooth_position = (
                self.smooth_position[0] + dx * 0.2,
                self.smooth_position[1] + dy * 0.2
            )
            
            self.position = self.smooth_position
            
            # Periodically reassign quadrants for better exploration
            if current_time - self.last_child_spawn > self.child_spawn_interval * 2:  # Every 2 spawn cycles
                self.reassign_quadrants()
            
            # Update children
            for child in self.child_bots[:]:
                child.update(current_time)
                
                # Remove children that are too far away
                if (abs(child.position[0] - self.position[0]) > self.maze.cols * CELL_SIZE or 
                    abs(child.position[1] - self.position[1]) > self.maze.rows * CELL_SIZE):
                    self.child_bots.remove(child)
            
            # Handle exit path if found
            if self.found_exit:
                current_cell = (int(self.position[0] // CELL_SIZE), 
                            int(self.position[1] // CELL_SIZE))
                
                # Only regenerate path if needed
                if not self.exit_path or current_cell not in self.exit_path:
                    raw_path = self.find_path(current_cell, self.knowledge["exit"])
                    if raw_path:
                        self.exit_path = self.smooth_path(raw_path)
                
                # Follow the path if we have one
                if self.exit_path and len(self.exit_path) > 1:
                    next_cell = self.exit_path[0]
                    # Skip if we're already at next cell
                    if next_cell == current_cell and len(self.exit_path) > 1:
                        next_cell = self.exit_path[1]
                        self.exit_path.pop(0)
                    
                    target_pos = (
                        next_cell[0] * CELL_SIZE + CELL_SIZE//2,
                        next_cell[1] * CELL_SIZE + CELL_SIZE//2
                    )
                    
                    dx = target_pos[0] - self.position[0]
                    dy = target_pos[1] - self.position[1]
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance < 5:  # Reached cell
                        self.exit_path.pop(0)
                    else:
                        if distance > 0:
                            dx, dy = dx/distance, dy/distance
                        self.position = (
                            self.position[0] + dx * self.speed * 1.5,
                            self.position[1] + dy * self.speed * 1.5
                        )

            # Update special cell color indicator
            self.update_special_cell_color()

    def update_special_cell_color(self):
        """Change color if near special cells"""
        current_cell = (
            int(self.position[0] // CELL_SIZE),
            int(self.position[1] // CELL_SIZE)
        )
        
        # Check if near any known special cells
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                x, y = current_cell[0] + dx, current_cell[1] + dy
                if (x, y) in self.knowledge["traps"]:
                    self.current_color = (255, 100, 100)  # Light red for trap
                    return
                elif (x, y) in self.knowledge["teleports"]:
                    self.current_color = (100, 100, 255)  # Light blue for teleport
                    return
                elif (x, y) in self.knowledge["buttons"]:
                    self.current_color = (255, 255, 100)  # Light yellow for button
                    return
                elif self.knowledge["exit"] and (x, y) == self.knowledge["exit"]:
                    self.current_color = (100, 255, 100)  # Light green for exit
                    return
        
        # Default color
        self.current_color = self.normal_color
    
    def draw(self, screen, camera):
        """Draw navigator and its information with exploration visualization"""
        if not self.visible or not self.position:
            return
            
        # Draw exploration progress (semi-transparent blue dots)
        if self.exploration_mode:
            explored_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            
            for x in range(self.maze.cols):
                for y in range(self.maze.rows):
                    if (x,y) in self.explored_cells:
                        center = camera.apply_pos((
                            x * CELL_SIZE + CELL_SIZE//2,
                            y * CELL_SIZE + CELL_SIZE//2
                        ))
                        if (0 <= center[0] < screen.get_width() and 
                            0 <= center[1] < screen.get_height()):
                            radius = max(1, int(2 * camera.zoom))
                            # Different color intensity based on how recently explored
                            pygame.draw.circle(explored_surface, (100, 100, 255, 100), 
                                            (int(center[0]), int(center[1])), radius)
            
            screen.blit(explored_surface, (0, 0))

        # Draw mother bot
        adjusted_pos = camera.apply_pos(self.position)
        pygame.draw.circle(screen, self.current_color, adjusted_pos, 10)
        
        # Draw children
        for child in self.child_bots:
            child.draw(screen, camera)
        
        # Draw path to exit if found (thicker green line)
        if not self.follow_mode and self.found_exit and self.exit_path:
            if len(self.exit_path) > 1:
                # Create a surface for the path with transparency
                path_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                
                for i in range(len(self.exit_path)-1):
                    start = camera.apply_pos((
                        self.exit_path[i][0] * CELL_SIZE + CELL_SIZE//2,
                        self.exit_path[i][1] * CELL_SIZE + CELL_SIZE//2
                    ))
                    end = camera.apply_pos((
                        self.exit_path[i+1][0] * CELL_SIZE + CELL_SIZE//2,
                        self.exit_path[i+1][1] * CELL_SIZE + CELL_SIZE//2
                    ))
                    # Only draw if visible
                    if (0 <= start[0] < screen.get_width() and 0 <= start[1] < screen.get_height() or
                        0 <= end[0] < screen.get_width() and 0 <= end[1] < screen.get_height()):
                        pygame.draw.line(path_surface, (0, 255, 0, 150), 
                                      (int(start[0]), int(start[1])),
                                      (int(end[0]), int(end[1])), 
                                      max(2, int(3 * camera.zoom)))
                
                screen.blit(path_surface, (0, 0))

        # Draw known special cells (optimized to only draw visible ones)
        visible_rect = camera.get_visible_rect()  # Assuming camera has this method
        for cell_type, info in self.special_cell_info.items():
            cells = []
            if cell_type == CellType.TRAP:
                cells = self.knowledge["traps"]
            elif cell_type == CellType.TELEPORT:
                cells = self.knowledge["teleports"]
            elif cell_type == CellType.BUTTON:
                cells = self.knowledge["buttons"]
            elif cell_type == CellType.EXIT and self.knowledge["exit"]:
                cells = [self.knowledge["exit"]]
            
            for x, y in cells:
                cell_rect = pygame.Rect(
                    x * CELL_SIZE,
                    y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                if visible_rect.colliderect(cell_rect):
                    self.draw_special_cell(screen, camera, (x, y), info["color"])

    def draw_special_cell(self, screen, camera, pos, color):
        """Optimized special cell drawing with zoom consideration"""
        x, y = pos
        center = camera.apply_pos((
            x * CELL_SIZE + CELL_SIZE//2,
            y * CELL_SIZE + CELL_SIZE//2
        ))
        radius = max(3, int(6 * camera.zoom))  # Minimum 3 pixels, scales with zoom
        pygame.draw.circle(screen, color, (int(center[0]), int(center[1])), radius)
        # Add a subtle border for better visibility
        pygame.draw.circle(screen, (0, 0, 0), (int(center[0]), int(center[1])), radius, 1)

    def get_unexplored_cells(self):
        """Return set of all unexplored cells"""
        all_cells = set((x,y) for x in range(self.maze.cols) for y in range(self.maze.rows))
        return all_cells - self.explored_cells
    
    # def find_quadrant_target(self, current_cell):
    #     """Find target based on assigned quadrant"""
    #     cols, rows = self.mother.maze.cols, self.mother.maze.rows
        
    #     # Define quadrant boundaries
    #     if self.exploration_quadrant == 0:  # Top-left
    #         target_area = (0, 0, cols//2, rows//2)
    #     elif self.exploration_quadrant == 1:  # Top-right
    #         target_area = (cols//2, 0, cols, rows//2)
    #     elif self.exploration_quadrant == 2:  # Bottom-left
    #         target_area = (0, rows//2, cols//2, rows)
    #     elif self.exploration_quadrant == 3:  # Bottom-right
    #         target_area = (cols//2, rows//2, cols, rows)
    #     else:
    #         target_area = (0, 0, cols, rows)

    def reassign_quadrants(self):
        """Dynamically reassign quadrants based on exploration progress"""
        quadrant_exploration = [0, 0, 0, 0]  # Track exploration in each quadrant
        cols, rows = self.maze.cols, self.maze.rows
        
        # Calculate exploration percentage per quadrant
        for x in range(cols):
            for y in range(rows):
                if (x,y) in self.explored_cells:
                    if x < cols//2 and y < rows//2: quadrant_exploration[0] += 1
                    elif x >= cols//2 and y < rows//2: quadrant_exploration[1] += 1
                    elif x < cols//2 and y >= rows//2: quadrant_exploration[2] += 1
                    else: quadrant_exploration[3] += 1
        
        # Reassign bots to least explored quadrants
        for i, child in enumerate(self.child_bots):
            least_explored = quadrant_exploration.index(min(quadrant_exploration))
            child.exploration_quadrant = least_explored
            quadrant_exploration[least_explored] = float('inf')  # Prevent duplicate assignments

    def smooth_path(self, path):
        """Remove unnecessary waypoints from path"""
        if len(path) < 3:
            return path
        
        smoothed = [path[0]]
        for i in range(1, len(path)-1):
            prev = smoothed[-1]
            next_p = path[i+1]
            # Check if movement from prev to next_p is possible without i
            if not self.is_straight_line_clear(prev, next_p):
                smoothed.append(path[i])
        smoothed.append(path[-1])
        return smoothed

    def is_straight_line_clear(self, start, end):
        """Check if straight path between two cells is walkable using Bresenham's algorithm"""
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        
        while True:
            # Check if current cell blocks movement
            if not self.is_cell_accessible(x0, y0):
                return False
            
            if x0 == x1 and y0 == y1:
                break
                
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
        
        return True

    def update_explored_cells(self, current_time):
        """Update explored cells based on current position and child bots"""
        if current_time - self.last_exploration_update < self.exploration_interval:
            return
        
        self.last_exploration_update = current_time
        
        # Update based on mother's position
        mother_cell = (
            int(self.position[0] // CELL_SIZE),  # Fixed missing parenthesis
            int(self.position[1] // CELL_SIZE)   # Fixed missing parenthesis
        )
        self.explored_cells.add(mother_cell)
        
        # Update based on children's positions
        for child in self.child_bots:
            child_cell = (
                int(child.position[0] // CELL_SIZE),  # Fixed missing parenthesis
                int(child.position[1] // CELL_SIZE)   # Fixed missing parenthesis
            )
            if (0 <= child_cell[0] < self.maze.cols and 
                0 <= child_cell[1] < self.maze.rows):
                self.explored_cells.add(child_cell)
        
        # Add visible neighboring cells (within 2 cells)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                x, y = mother_cell[0] + dx, mother_cell[1] + dy
                if (0 <= x < self.maze.cols and 0 <= y < self.maze.rows):
                    self.explored_cells.add((x, y))

