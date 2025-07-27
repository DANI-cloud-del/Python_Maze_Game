import pygame
import sys
import random
from maze import Maze
from player import Player, PlayerState
from camera import Camera
from utils.settings import *
from collision import Collision
from navigator import Navigator
from menu import GameMenu
from enum import Enum
from special_effects import SpecialEffects
from doors import DoorSystem

class GameState(Enum):
    RUNNING = 0
    GAME_OVER = 1
    VICTORY = 2

class Game:
    def __init__(self, settings=None):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Horror Maze")
        self.clock = pygame.time.Clock()
        self.settings = settings if settings else self.get_default_settings()
        self.reset_game()
        self.door_system = DoorSystem(self.maze)
        
    def get_default_settings(self):
        return {
            "algorithm": "a_star",
            "difficulty": "medium",
            "enemy_count": 5,
            "maze_size": (20, 20),
            "trap_damage": 20
        }
        
    def reset_game(self):
        # Use settings from menu
        self.maze = Maze(
            cols=self.settings["maze_size"][0],
            rows=self.settings["maze_size"][1],
            enemy_count=self.settings["enemy_count"],
            trap_damage=self.settings["trap_damage"]
        )
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
        self.navigator = Navigator(self.maze)
        self.navigator.set_algorithm(self.settings["algorithm"])
        self.show_navigator = False
        self.current_algorithm = self.settings["algorithm"]
        
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
                elif event.key == pygame.K_n:  # Toggle navigator
                    self.show_navigator = not self.show_navigator
                    self.navigator.visible = self.show_navigator
                    if self.show_navigator:
                        self.navigator.update(
                            (self.player.rect.centerx, self.player.rect.centery),
                            self.player.direction,
                            pygame.time.get_ticks()
                        )
                elif event.key == pygame.K_f:  # Toggle follow mode
                    if self.show_navigator:
                        self.navigator.toggle_follow_mode()
                elif event.key == pygame.K_SPACE:  # Jump
                    if self.player.state == PlayerState.NORMAL:
                        self.player.jump()
                elif event.key == pygame.K_1:  # Switch to DFS
                    self.current_algorithm = "dfs"
                    if self.show_navigator:
                        self.navigator.set_algorithm("dfs")
                        self.navigator.update(
                            (self.player.rect.centerx, self.player.rect.centery),
                            self.player.direction,
                            True
                        )
                elif event.key == pygame.K_2:  # Switch to BFS
                    self.current_algorithm = "bfs"
                    if self.show_navigator:
                        self.navigator.set_algorithm("bfs")
                        self.navigator.update(
                            (self.player.rect.centerx, self.player.rect.centery),
                            self.player.direction,
                            True
                        )
                elif event.key == pygame.K_3:  # Switch to A*
                    self.current_algorithm = "a_star"
                    if self.show_navigator:
                        self.navigator.set_algorithm("a_star")
                        self.navigator.update(
                            (self.player.rect.centerx, self.player.rect.centery),
                            self.player.direction,
                            True
                        )
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                mouse_pos = pygame.mouse.get_pos()
                # Convert mouse position to world coordinates
                world_mouse_pos = (
                    mouse_pos[0] / self.camera.zoom + self.camera.display_offset.x,
                    mouse_pos[1] / self.camera.zoom + self.camera.display_offset.y
                )
                self.player.handle_mouse(world_mouse_pos, True, pygame.time.get_ticks())

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
        
        # Update door system
        self.door_system.update(pygame.time.get_ticks())
        
        # Check door collisions
        if self.door_system.check_collision(self.player.rect):
            # Player hits a closed door
            self.player.take_damage(10)
        
        # Check for special cell effects
        cell_effect = self.maze.special_effects.check_special_cells(self.player.rect)
        if cell_effect:
            if cell_effect == "trap":
                if not self.player.jumping:  # Only take damage if not jumping over trap
                    self.player.take_damage(self.maze.trap_damage)
                    self.player.state = PlayerState.TRAPPED
                    self.player.state_timer = pygame.time.get_ticks()
                
            elif cell_effect == "battery":
                self.player.torch_battery = min(100, self.player.torch_battery + 30)
                
            elif cell_effect == "ammo":
                self.player.shooting_system.ammo = min(self.player.shooting_system.max_ammo, 
                                                    self.player.shooting_system.ammo + 5)
                
            elif isinstance(cell_effect, tuple) and cell_effect[0] == "teleport":
                self.player.state = PlayerState.TELEPORTING
                self.player.state_timer = pygame.time.get_ticks()
                
                # Update player position to the teleport target
                tele_x_px, tele_y_px = cell_effect[1]
                tele_x, tele_y = cell_effect[2]
                
                # Ensure player doesn't get stuck in walls
                if self.check_collision_at_position(tele_x_px, tele_y_px):
                    tele_x_px, tele_y_px = self.find_safe_teleport_position(tele_x, tele_y)
                
                self.player.rect.x = tele_x_px
                self.player.rect.y = tele_y_px
                self.camera.follow(self.player)
                self.visited_cells.add((tele_x, tele_y))
                
            elif isinstance(cell_effect, tuple) and cell_effect[0] == "maze_reset":
                button_x, button_y = cell_effect[1]
                self.maze.reset_maze((button_x, button_y))
                
                player_cell_x = self.player.rect.centerx // CELL_SIZE
                player_cell_y = self.player.rect.centery // CELL_SIZE
                safe_x, safe_y = self.find_nearest_valid_position(player_cell_x, player_cell_y)
                self.player.rect.x = safe_x * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
                self.player.rect.y = safe_y * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
                self.camera.follow(self.player)
                self.visited_cells.add((safe_x, safe_y))
                
            elif cell_effect == "exit":
                self.state = GameState.VICTORY

        # Update enemies
        player_cell_x = self.player.rect.centerx // CELL_SIZE
        player_cell_y = self.player.rect.centery // CELL_SIZE
        
        for enemy in self.maze.enemies:
            enemy.update_visibility(
                player_cell_x, 
                player_cell_y,
                self.player.direction,
                self.player.light_on
            )
            
            if not enemy.visible or random.random() > 0.8:
                enemy.move_toward_player(
                    player_cell_x,
                    player_cell_y,
                    self.maze
                )
            
            if (enemy.x == player_cell_x and enemy.y == player_cell_y and 
                not self.player.light_on):
                if self.player.take_damage(30):
                    pass
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER

        # Update navigator
        if self.show_navigator:
            self.navigator.update(
                (self.player.rect.centerx, self.player.rect.centery),
                self.player.direction,
                pygame.time.get_ticks()
            )
        
        # Update shooting system
        self.player.shooting_system.update(self.maze.enemies)

    def check_collision_at_position(self, x, y):
        """Check if a position would cause collision with walls"""
        test_rect = pygame.Rect(
            x,
            y,
            PLAYER_SIZE,
            PLAYER_SIZE
        )
        return self.maze.check_collision(test_rect)

    def find_safe_teleport_position(self, tele_x, tele_y):
        """Find a safe position near the teleport target"""
        # Try center first
        center_x = tele_x * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
        center_y = tele_y * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
        
        if not self.check_collision_at_position(center_x, center_y):
            return center_x, center_y
        
        # Try positions around the center in a spiral pattern
        for radius in range(1, 3):
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                        
                    test_x = center_x + dx * (PATH_WIDTH//2)
                    test_y = center_y + dy * (PATH_WIDTH//2)
                    
                    if not self.check_collision_at_position(test_x, test_y):
                        return test_x, test_y
        
        # Fallback to start position if no safe position found
        start_x, start_y = self.maze.start_pos
        return (
            start_x * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2,
            start_y * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
        )

    def find_nearest_valid_position(self, start_x, start_y):
        """Find nearest cell where player won't collide with walls"""
        for radius in range(0, 5):  # Check current cell first, then expand outward
            for dx in range(-radius, radius+1):
                for dy in range(-radius, radius+1):
                    x, y = start_x + dx, start_y + dy
                    if 0 <= x < self.maze.cols and 0 <= y < self.maze.rows:
                        # Create test rect for this cell
                        test_rect = pygame.Rect(
                            x * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2,
                            y * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2,
                            PLAYER_SIZE,
                            PLAYER_SIZE
                        )
                        if not Collision.check_player_wall_collision(test_rect, self.maze):
                            return x, y
        return self.maze.start_pos  # Fallback to start position if no valid cell found
    
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
            
            # Draw doors
            self.door_system.draw(self.screen, self.camera)
            
            # Draw navigator path if active
            if self.show_navigator:
                self.navigator.draw(self.screen, self.camera)
            
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
        
        # Battery bar
        battery_width = 200
        battery_height = 10
        battery_pos = (20, 45)
        
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (battery_pos[0], battery_pos[1], battery_width, battery_height))
        battery_color = (0, 255, 0) if self.player.torch_battery > 30 else (255, 165, 0) if self.player.torch_battery > 10 else (255, 0, 0)
        pygame.draw.rect(self.screen, battery_color, 
                        (battery_pos[0], battery_pos[1], battery_width * (self.player.torch_battery/100), battery_height))
        
        # Ammo counter
        ammo_text = pygame.font.SysFont(None, 24).render(
            f"Ammo: {self.player.shooting_system.ammo}/{self.player.shooting_system.max_ammo}", 
            True, (200, 200, 200)
        )
        self.screen.blit(ammo_text, (20, 60))
        
        # Time
        time_text = pygame.font.SysFont(None, 36).render(
            f"Time: {self.game_time//1000}s", True, (255, 255, 255))
        self.screen.blit(time_text, (SCREEN_WIDTH - 150, 20))
        
        # Instructions
        font_small = pygame.font.SysFont(None, 24)
        controls = [
            "F: Toggle Light | N: Navigator | SPACE: Jump",
            "1-3: Algorithms | LMB: Shoot | F: Toggle Follow Mode"
        ]
        
        for i, text in enumerate(controls):
            control_text = font_small.render(text, True, (200, 200, 200))
            self.screen.blit(control_text, (20, SCREEN_HEIGHT - 60 - i*30))
        
        # Algorithm and follow mode info
        if self.show_navigator:
            algo_text = font_small.render(
                f"Algorithm: {self.current_algorithm.upper()} | Follow: {'ON' if self.navigator.follow_mode else 'OFF'}", 
                True, (200, 200, 200))
            self.screen.blit(algo_text, (20, SCREEN_HEIGHT - 30))
    
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Horror Maze")
    
    # Show menu first
    menu = GameMenu(screen)
    settings = menu.run()
    
    if settings:  # User didn't quit
        game = Game(settings)
        game.run()

if __name__ == "__main__":
    main()