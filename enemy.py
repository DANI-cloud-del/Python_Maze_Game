import random
import pygame
from utils.settings import CELL_SIZE 

class Enemy:
    def __init__(self, x, y, maze):  # Add maze parameter
        self.x = x
        self.y = y
        self.speed = 1
        self.aggression = 0.5
        self.detection_radius = 3
        self.visible = False
        self.maze = maze  # Store maze reference
    
    def move_toward_player(self, player_x, player_y, maze):
        dx = 1 if player_x > self.x else -1 if player_x < self.x else 0
        dy = 1 if player_y > self.y else -1 if player_y < self.y else 0
        
        if random.random() > self.aggression:
            dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        
        if maze.can_move(self.x, self.y, (dx, dy)):
            self.x += dx
            self.y += dy
    
    def update_visibility(self, player_x, player_y, player_direction, player_light_on):
        """Don't attack if player is in safe zone"""
        safe_radius = 3  # Smaller than generation radius for buffer
        distance_to_start = abs(player_x - self.maze.start_pos[0]) + abs(player_y - self.maze.start_pos[1])
        
        if distance_to_start <= safe_radius:
            self.visible = False  # Won't attack in safe zone
            return
            
        # Original visibility logic
        self.visible = (...)
    
    def draw(self, screen, camera, player_direction, player_pos):
        if not self.visible:
            return
            
        player_cell_x, player_cell_y = player_pos
        rel_x, rel_y = self.x - player_cell_x, self.y - player_cell_y
        dot_product = player_direction.x * rel_x + player_direction.y * rel_y
        
        if dot_product < 0:
            return
            
        cx = self.x * CELL_SIZE + CELL_SIZE//2
        cy = self.y * CELL_SIZE + CELL_SIZE//2
        adjusted_pos = camera.apply_pos((cx, cy))
        radius = int(CELL_SIZE * 0.3 * camera.zoom)
        
        visibility = 0.3 + 0.7 * dot_product / (abs(rel_x) + abs(rel_y) + 0.1)
        alpha = min(255, max(50, int(255 * visibility)))
        
        enemy_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(enemy_surface, (255, 0, 0, alpha), (radius, radius), radius)
        screen.blit(enemy_surface, (adjusted_pos[0]-radius, adjusted_pos[1]-radius))