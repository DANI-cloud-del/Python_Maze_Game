import pygame
from utils.settings import *
from enum import Enum

class PlayerState(Enum):
    NORMAL = 0
    TRAPPED = 1
    TELEPORTING = 2

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(
            x + (PATH_WIDTH - PLAYER_SIZE)//2,
            y + (PATH_WIDTH - PLAYER_SIZE)//2,
            PLAYER_SIZE,
            PLAYER_SIZE
        )
        self.direction = pygame.Vector2(0, -1)
        self.speed = 4
        self.light_mask = self.create_light_mask()
        self.health = 100
        self.state = PlayerState.NORMAL
        self.state_timer = 0
        self.light_on = True
        self.torch_battery = 100
        self.last_damage_time = 0
        self.invulnerable_time = 1000  # ms after taking damage
    
    def create_light_mask(self):
        mask = pygame.Surface((LIGHT_RADIUS*2, LIGHT_RADIUS*2), pygame.SRCALPHA)
        for radius in range(LIGHT_RADIUS, 0, -1):
            alpha = int(LIGHT_INTENSITY * (radius/LIGHT_RADIUS))
            pygame.draw.circle(mask, (*FOG_COLOR, alpha), 
                             (LIGHT_RADIUS, LIGHT_RADIUS), radius)
        return mask
        
    def handle_input(self, keys):
        if self.state != PlayerState.NORMAL:
            return
            
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = pygame.Vector2(-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = pygame.Vector2(1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = pygame.Vector2(0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = pygame.Vector2(0, 1)
        
        # Toggle light
        if keys[pygame.K_f] and self.torch_battery > 0:
            self.light_on = not self.light_on
        
    def move(self, maze):
        if self.state != PlayerState.NORMAL:
            return
            
        new_rect = self.rect.copy()
        new_rect.x += self.direction.x * self.speed
        new_rect.y += self.direction.y * self.speed
        
        if not self.check_collision(new_rect, maze):
            self.rect = new_rect
        
        # Update torch battery
        if self.light_on:
            self.torch_battery = max(0, self.torch_battery - 0.1)
            if self.torch_battery <= 0:
                self.light_on = False
        else:
            self.torch_battery = min(100, self.torch_battery + 0.05)
            
    def check_collision(self, rect, maze):
        grid_x = rect.centerx // CELL_SIZE
        grid_y = rect.centery // CELL_SIZE
        
        if not (0 <= grid_x < maze.cols and 0 <= grid_y < maze.rows):
            return True
            
        cell = maze.grid[grid_x][grid_y]
        
        margin = (CELL_SIZE - PATH_WIDTH)//2
        if (cell.walls['left'] and rect.left < grid_x * CELL_SIZE + margin) or \
           (cell.walls['right'] and rect.right > (grid_x+1) * CELL_SIZE - margin) or \
           (cell.walls['top'] and rect.top < grid_y * CELL_SIZE + margin) or \
           (cell.walls['bottom'] and rect.bottom > (grid_y+1) * CELL_SIZE - margin):
            return True
            
        return False
        
    def take_damage(self, amount):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time > self.invulnerable_time:
            self.health = max(0, self.health - amount)
            self.last_damage_time = current_time
            return True
        return False
        
    def update_state(self):
        current_time = pygame.time.get_ticks()
        if self.state == PlayerState.TRAPPED and current_time - self.state_timer > 1000:
            self.state = PlayerState.NORMAL
        elif self.state == PlayerState.TELEPORTING and current_time - self.state_timer > 500:
            self.state = PlayerState.NORMAL
    
    def draw(self, screen, camera):
        adjusted_pos = camera.apply_pos(self.rect.center)
        
        # Draw player with state indication
        if self.state == PlayerState.TRAPPED:
            color = (255, 100, 100)  # Hurt color
        elif self.state == PlayerState.TELEPORTING:
            color = (100, 255, 255)  # Teleporting color
        else:
            color = (255, 215, 0)  # Normal gold color
            
        pygame.draw.circle(screen, color, 
                         adjusted_pos, 
                         PLAYER_SIZE//2 * camera.zoom)
        
        # Draw direction indicator
        direction_pos = (
            adjusted_pos[0] + self.direction.x * PLAYER_SIZE//2 * camera.zoom,
            adjusted_pos[1] + self.direction.y * PLAYER_SIZE//2 * camera.zoom
        )
        pygame.draw.circle(screen, (255, 100, 0), direction_pos, PLAYER_SIZE//4 * camera.zoom)
        
        # Draw battery indicator
        battery_width = 30 * camera.zoom
        battery_height = 5 * camera.zoom
        battery_pos = (adjusted_pos[0] - battery_width//2, adjusted_pos[1] - 20 * camera.zoom)
        
        # Battery outline
        pygame.draw.rect(screen, (200, 200, 200), 
                        (battery_pos[0], battery_pos[1], battery_width, battery_height), 1)
        
        # Battery level
        fill_width = max(0, (battery_width-2) * self.torch_battery / 100)
        battery_color = (0, 255, 0) if self.torch_battery > 30 else (255, 0, 0)
        pygame.draw.rect(screen, battery_color,
                        (battery_pos[0]+1, battery_pos[1]+1, fill_width, battery_height-2))
        
    def draw_light(self, screen, camera):
        if not self.light_on:
            return
            
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