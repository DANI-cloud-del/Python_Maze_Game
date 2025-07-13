import pygame
from utils.settings import PLAYER_SIZE, PATH_WIDTH, LIGHT_RADIUS, LIGHT_INTENSITY, FOG_COLOR, CELL_SIZE  # Added CELL_SIZE

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(
            x + (PATH_WIDTH - PLAYER_SIZE)//2,  # Center in path
            y + (PATH_WIDTH - PLAYER_SIZE)//2,
            PLAYER_SIZE,
            PLAYER_SIZE
        )
        self.direction = pygame.Vector2(0, -1)  # Initial facing direction
        self.speed = 4
        self.light_mask = self.create_light_mask()
        
    def create_light_mask(self):
        """Create a radial gradient for the light effect"""
        mask = pygame.Surface((LIGHT_RADIUS*2, LIGHT_RADIUS*2), pygame.SRCALPHA)
        for radius in range(LIGHT_RADIUS, 0, -1):
            alpha = int(LIGHT_INTENSITY * (radius/LIGHT_RADIUS))
            pygame.draw.circle(mask, (*FOG_COLOR, alpha), 
                             (LIGHT_RADIUS, LIGHT_RADIUS), radius)
        return mask
        
    def handle_input(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = pygame.Vector2(-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = pygame.Vector2(1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = pygame.Vector2(0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = pygame.Vector2(0, 1)
            
    def move(self, maze):
        new_rect = self.rect.copy()
        new_rect.x += self.direction.x * self.speed
        new_rect.y += self.direction.y * self.speed
        
        if not self.check_collision(new_rect, maze):
            self.rect = new_rect
            
    def check_collision(self, rect, maze):
        # Convert player position to grid coordinates
        grid_x = rect.centerx // CELL_SIZE
        grid_y = rect.centery // CELL_SIZE
        
        if not (0 <= grid_x < maze.cols and 0 <= grid_y < maze.rows):
            return True
            
        cell = maze.grid[grid_x][grid_y]
        
        # Check wall collisions with path width consideration
        margin = (CELL_SIZE - PATH_WIDTH)//2
        if (cell.walls['left'] and rect.left < grid_x * CELL_SIZE + margin) or \
           (cell.walls['right'] and rect.right > (grid_x+1) * CELL_SIZE - margin) or \
           (cell.walls['top'] and rect.top < grid_y * CELL_SIZE + margin) or \
           (cell.walls['bottom'] and rect.bottom > (grid_y+1) * CELL_SIZE - margin):
            return True
            
        return False
        
    def draw(self, screen, camera):
        # Draw player with direction indicator
        adjusted_pos = camera.apply_pos(self.rect.center)
        pygame.draw.circle(screen, (255, 215, 0),  # Gold color
                         adjusted_pos, 
                         PLAYER_SIZE//2 * camera.zoom)
        
        # Draw direction indicator
        direction_pos = (
            adjusted_pos[0] + self.direction.x * PLAYER_SIZE//2 * camera.zoom,
            adjusted_pos[1] + self.direction.y * PLAYER_SIZE//2 * camera.zoom
        )
        pygame.draw.circle(screen, (255, 100, 0), direction_pos, PLAYER_SIZE//4 * camera.zoom)
        
    def draw_light(self, screen, camera):
        """Draw the light effect centered on player"""
        adjusted_pos = camera.apply_pos(self.rect.center)
        light_pos = (
            adjusted_pos[0] - LIGHT_RADIUS * camera.zoom,
            adjusted_pos[1] - LIGHT_RADIUS * camera.zoom
        )
        scaled_light = pygame.transform.scale(
            self.light_mask,
            (int(LIGHT_RADIUS*2 * camera.zoom), int(LIGHT_RADIUS*2 * camera.zoom))
        )
        screen.blit(scaled_light, light_pos)