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
        self.light_radius = 150
        self.light_surface = self.create_light_surface()
        self.algorithm = "a_star"  # Default algorithm
        
    def create_light_surface(self):
        surface = pygame.Surface((self.light_radius*2, self.light_radius*2), pygame.SRCALPHA)
        for radius in range(self.light_radius, 0, -10):
            alpha = int(200 * (radius/self.light_radius))
            pygame.draw.circle(surface, (255, 255, 255, alpha), 
                             (self.light_radius, self.light_radius), radius)
        return surface
        
    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
        
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
    
    def update(self, player_pos, player_direction, force_recalculate=False):
        if not self.visible:
            return
            
        player_cell = (player_pos[0] // CELL_SIZE, player_pos[1] // CELL_SIZE)
        
        # If player is following the bot or we need to recalculate
        if force_recalculate or not self.path or player_cell == self.path[0]:
            self.path = self.find_path(player_cell, self.maze.exit_pos)
            if self.path and len(self.path) > 1:
                self.current_target = self.path[1]  # Next cell to move to
                self.path = self.path[1:]  # Remove current position
            else:
                self.current_target = None
        
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
            
        # Draw glowing light
        light_pos = (
            self.position[0] - self.light_radius,
            self.position[1] - self.light_radius
        )
        screen.blit(self.light_surface, camera.apply_pos(light_pos))
        
        # Draw bot (simple circle)
        adjusted_pos = camera.apply_pos(self.position)
        pygame.draw.circle(screen, (255, 255, 255), adjusted_pos, 10)
        
        # Draw path (optional)
        if self.path:
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