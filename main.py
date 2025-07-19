import pygame
import sys
from maze import Maze
from player import Player, PlayerState  # Added PlayerState import
from camera import Camera
from utils.settings import *
from enum import Enum

class GameState(Enum):
    RUNNING = 0
    GAME_OVER = 1
    VICTORY = 2

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Horror Maze")
        self.clock = pygame.time.Clock()
        
        self.reset_game()
        
    def reset_game(self):
        self.maze = Maze()
        self.camera = Camera()
        
        # Start player at maze start position
        start_x, start_y = self.maze.start_pos
        start_px = start_x * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
        start_py = start_y * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
        self.player = Player(start_px, start_py)
        
        self.visited_cells = set()
        self.update_visited_cells()
        self.state = GameState.RUNNING
        self.game_time = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif self.state != GameState.RUNNING and event.key == pygame.K_r:
                    self.reset_game()
                
    def update(self):
        if self.state != GameState.RUNNING:
            return
            
        self.game_time += self.clock.get_time()
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.move(self.maze)
        self.player.update_state()
        self.update_visited_cells()
        self.camera.follow(self.player)
        
        # Check for special cell effects
        cell_effect = self.maze.check_special_cells(self.player.rect)
        if cell_effect:
            if cell_effect == "trap":
                self.player.take_damage(20)
                self.player.state = PlayerState.TRAPPED
                self.player.state_timer = pygame.time.get_ticks()
                
            elif isinstance(cell_effect, tuple) and cell_effect[0] == "teleport":
                self.player.state = PlayerState.TELEPORTING
                self.player.state_timer = pygame.time.get_ticks()
                tele_x, tele_y = cell_effect[1]
                self.player.rect.x = tele_x * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
                self.player.rect.y = tele_y * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
                
            elif cell_effect == "maze_reset":
                pass  # Maze already reset by check_special_cells
                
            elif cell_effect == "exit":
                self.state = GameState.VICTORY
        
        # Update enemies
        self.maze.update_enemies(
            (self.player.rect.centerx, self.player.rect.centery),
            self.player.direction,
            self.player.light_on
        )
        
        # Check for enemy collisions
        player_cell_x = self.player.rect.centerx // CELL_SIZE
        player_cell_y = self.player.rect.centery // CELL_SIZE
        
        for enemy in self.maze.enemies:
            if (enemy.x == player_cell_x and enemy.y == player_cell_y and 
                not self.player.light_on):
                if self.player.take_damage(30):
                    pass
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER
    
    def update_visited_cells(self):
        cell_x = self.player.rect.centerx // CELL_SIZE
        cell_y = self.player.rect.centery // CELL_SIZE
        
        for dx in range(-VISIBLE_RADIUS, VISIBLE_RADIUS+1):
            for dy in range(-VISIBLE_RADIUS, VISIBLE_RADIUS+1):
                if (0 <= cell_x + dx < self.maze.cols and 
                    0 <= cell_y + dy < self.maze.rows):
                    self.visited_cells.add((cell_x + dx, cell_y + dy))
        
    def draw(self):
        self.screen.fill(FOG_COLOR)
        
        if self.state == GameState.RUNNING:
            # Draw visited maze areas
            self.maze.draw(
                self.screen, 
                self.camera, 
                self.visited_cells,
                self.player.direction,
                (self.player.rect.centerx, self.player.rect.centery)
            )
            
            # Draw player
            self.player.draw(self.screen, self.camera)
            
            # Apply lighting effect if light is on
            if self.player.light_on:
                self.player.draw_light(self.screen, self.camera)
            
            # Draw HUD
            self.draw_hud()
            
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.VICTORY:
            self.draw_victory()
        
        pygame.display.flip()
        
    def draw_hud(self):
        # Health bar
        health_width = 200
        health_height = 20
        health_pos = (20, 20)
        
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (health_pos[0], health_pos[1], health_width, health_height))
        pygame.draw.rect(self.screen, (255, 0, 0), 
                        (health_pos[0], health_pos[1], health_width * (self.player.health/100), health_height))
        
        # Time
        font = pygame.font.SysFont(None, 36)
        time_text = font.render(f"Time: {self.game_time//1000}s", True, (255, 255, 255))
        self.screen.blit(time_text, (SCREEN_WIDTH - 150, 20))
        
        # Instructions
        font_small = pygame.font.SysFont(None, 24)
        light_text = font_small.render("F: Toggle Light", True, (200, 200, 200))
        self.screen.blit(light_text, (20, SCREEN_HEIGHT - 30))
    
    def draw_game_over(self):
        font_large = pygame.font.SysFont(None, 72)
        font_small = pygame.font.SysFont(None, 36)
        
        game_over_text = font_large.render("GAME OVER", True, (255, 0, 0))
        restart_text = font_small.render("Press R to restart", True, (200, 200, 200))
        
        self.screen.blit(game_over_text, 
                        (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 
                         SCREEN_HEIGHT//2 - 50))
        self.screen.blit(restart_text,
                        (SCREEN_WIDTH//2 - restart_text.get_width()//2,
                         SCREEN_HEIGHT//2 + 20))
    
    def draw_victory(self):
        font_large = pygame.font.SysFont(None, 72)
        font_small = pygame.font.SysFont(None, 36)
        
        victory_text = font_large.render("ESCAPED!", True, (0, 255, 0))
        time_text = font_large.render(f"Time: {self.game_time//1000}s", True, (255, 255, 255))
        restart_text = font_small.render("Press R to restart", True, (200, 200, 200))
        
        self.screen.blit(victory_text, 
                        (SCREEN_WIDTH//2 - victory_text.get_width()//2, 
                         SCREEN_HEIGHT//2 - 100))
        self.screen.blit(time_text,
                        (SCREEN_WIDTH//2 - time_text.get_width()//2,
                         SCREEN_HEIGHT//2))
        self.screen.blit(restart_text,
                        (SCREEN_WIDTH//2 - restart_text.get_width()//2,
                         SCREEN_HEIGHT//2 + 70))
        
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()