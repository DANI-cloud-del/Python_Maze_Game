import pygame
import sys
import random
import math
from pygame.locals import *

class VortexParticle:
    def __init__(self, center):
        self.angle = random.uniform(0, 2 * math.pi)
        self.radius = random.uniform(50, 150)

        # 🔻 Slow movement — really subtle now
        self.speed = random.uniform(0.0008, 0.0025)

        self.base_size = random.uniform(1.5, 3.0)
        self.size = self.base_size
        self.center = center
        self.color = (150, 200, 255)

        # ✨ Optional pulsing
        self.pulse_speed = random.uniform(0.008, 0.015)
        self.pulse_range = random.uniform(0.3, 1.0)
        self.phase_offset = random.uniform(0, math.pi * 2)

    def update(self):
        self.angle += self.speed
        time = pygame.time.get_ticks()
        self.size = self.base_size + math.sin(time * self.pulse_speed + self.phase_offset) * self.pulse_range

    def draw(self, surface):
        x = self.center[0] + math.cos(self.angle) * self.radius
        y = self.center[1] + math.sin(self.angle) * self.radius

        # Optional glow
        glow = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 60), (int(self.size * 2), int(self.size * 2)), int(self.size * 2))
        surface.blit(glow, (x - self.size * 2, y - self.size * 2))

        # Core dot
        pygame.draw.circle(surface, self.color, (int(x), int(y)), max(1, int(self.size)))


class GameMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.state = "main"
        self.selected_algorithm = None
        self.selected_difficulty = "Medium"
        self.algorithm_type = "search"  # "search" or "non-search"
        
        # Initialize vortex particles
        self.center = (self.width // 2, self.height // 2)
        self.vortex_particles = [VortexParticle(self.center) for _ in range(80)]
        
        # Colors
        self.colors = {
            "title": (0, 200, 200),
            "normal": (255, 255, 255),
            "highlight": (0, 255, 0),
            "background": (10, 10, 20)  # Darker background to match vortex
        }
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 48)
        self.menu_font = pygame.font.SysFont('Arial', 36)
        self.submenu_font = pygame.font.SysFont('Arial', 28)
        
        # Menu options
        self.options = {
            "main": ["Start Game", "Select Algorithm", "Select Difficulty", "Quit"],
            "algorithm_type": ["Informed Search", "Uninformed Search"],
            "informed_search": ["BFS", "DFS"],
            "uninformed_search": ["A*", "Greedy Best-First"],
            "difficulty": ["Easy", "Medium", "Hard"]
        }

        # Update the cursor_pos dictionary:
        self.cursor_pos = {
            "main": 0,
            "algorithm_type": 0,
            "informed_search": 0,
            "uninformed_search": 0,
            "difficulty": 1
        }
        
        # Difficulty settings
        self.difficulty_settings = {
            "Easy": {"enemies": 3, "maze_size": (15, 15), "trap_damage": 10},
            "Medium": {"enemies": 5, "maze_size": (20, 20), "trap_damage": 20},
            "Hard": {"enemies": 8, "maze_size": (25, 25), "trap_damage": 30}
        }

    def update_vortex(self):
        for particle in self.vortex_particles:
            particle.update()

    def draw_vortex(self):
        # Create a semi-transparent surface for the vortex
        vortex_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        vortex_surface.fill((10, 10, 20, 200))  # Semi-transparent dark background
        
        # Draw particles
        for particle in self.vortex_particles:
            particle.draw(vortex_surface)
        
        # Blit the vortex surface onto the screen
        self.screen.blit(vortex_surface, (0, 0))

    def draw_text(self, text, font, color, y_offset=0, x_offset=0):
        text_surface = font.render(text, True, color)
        x = self.width // 2 - text_surface.get_width() // 2 + x_offset
        y = self.height // 3 + y_offset
        self.screen.blit(text_surface, (x, y))
        return text_surface.get_rect(topleft=(x, y))

    def draw_menu(self):
        # Draw vortex background
        self.update_vortex()
        self.draw_vortex()
        
        # Draw title
        self.draw_text("Maze Solving Game", self.title_font, self.colors["title"], -100)
        
        # Draw current selections
        if self.selected_algorithm:
            algo_text = f"Algorithm: {self.selected_algorithm}"
            self.draw_text(algo_text, self.submenu_font, self.colors["normal"], -30)
        
        diff_text = f"Difficulty: {self.selected_difficulty}"
        self.draw_text(diff_text, self.submenu_font, self.colors["normal"], 10)
        
        # Draw current menu options
        if self.state == "main":
            for i, option in enumerate(self.options["main"]):
                color = self.colors["highlight"] if i == self.cursor_pos["main"] else self.colors["normal"]
                self.draw_text(option, self.menu_font, color, 80 + i * 50)
                
        elif self.state == "algorithm_type":
            for i, option in enumerate(self.options["algorithm_type"]):
                color = self.colors["highlight"] if i == self.cursor_pos["algorithm_type"] else self.colors["normal"]
                self.draw_text(option, self.menu_font, color, 80 + i * 50)
                
        elif self.state in ["informed_search", "uninformed_search"]:
            algo_type = "Informed Search" if self.state == "informed_search" else "Uninformed Search"
            self.draw_text(algo_type, self.menu_font, self.colors["title"], 50)
            
            algorithms = self.options[self.state]
            for i, algo in enumerate(algorithms):
                color = self.colors["highlight"] if i == self.cursor_pos[self.state] else self.colors["normal"]
                self.draw_text(algo, self.submenu_font, color, 120 + i * 40)

                
        elif self.state == "difficulty":
            for i, option in enumerate(self.options["difficulty"]):
                color = self.colors["highlight"] if i == self.cursor_pos["difficulty"] else self.colors["normal"]
                self.draw_text(option, self.menu_font, color, 80 + i * 50)
                
                # Draw difficulty settings
                settings = self.difficulty_settings[option]
                settings_text = f"Enemies: {settings['enemies']} | Maze: {settings['maze_size'][0]}x{settings['maze_size'][1]} | Trap Damage: {settings['trap_damage']}"
                self.draw_text(settings_text, self.submenu_font, self.colors["normal"], 80 + i * 50 + 30)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.state == "main":
                        pygame.quit()
                        sys.exit()
                    else:
                        self.state = "main"
                        
                elif event.key == K_DOWN:
                    self.move_cursor(1)
                    
                elif event.key == K_UP:
                    self.move_cursor(-1)
                    
                elif event.key == K_RETURN:
                    self.select_option()
                    
        pygame.display.update()

    def move_cursor(self, direction):
        if self.state == "main":
            self.cursor_pos["main"] = (self.cursor_pos["main"] + direction) % len(self.options["main"])
        elif self.state == "algorithm_type":
            self.cursor_pos["algorithm_type"] = (self.cursor_pos["algorithm_type"] + direction) % len(self.options["algorithm_type"])
        elif self.state == "informed_search":
            self.cursor_pos["informed_search"] = (self.cursor_pos["informed_search"] + direction) % len(self.options["informed_search"])
        elif self.state == "uninformed_search":
            self.cursor_pos["uninformed_search"] = (self.cursor_pos["uninformed_search"] + direction) % len(self.options["uninformed_search"])
        elif self.state == "difficulty":
            self.cursor_pos["difficulty"] = (self.cursor_pos["difficulty"] + direction) % len(self.options["difficulty"])

    def select_option(self):
        if self.state == "main":
            if self.cursor_pos["main"] == 0:  # Start Game
                if self.selected_algorithm:
                    return "start_game"
            elif self.cursor_pos["main"] == 1:  # Select Algorithm
                self.state = "algorithm_type"
            elif self.cursor_pos["main"] == 2:  # Select Difficulty
                self.state = "difficulty"
            elif self.cursor_pos["main"] == 3:  # Quit
                pygame.quit()
                sys.exit()
                
        elif self.state == "algorithm_type":
            if self.cursor_pos["algorithm_type"] == 0:  # Informed Search
                self.state = "informed_search"
                self.algorithm_type = "informed"
            else:  # Uninformed Search
                self.state = "uninformed_search"
                self.algorithm_type = "uninformed"
                
        elif self.state == "informed_search":
            self.selected_algorithm = self.options["informed_search"][self.cursor_pos["informed_search"]]
            self.state = "main"
            
        elif self.state == "uninformed_search":
            self.selected_algorithm = self.options["uninformed_search"][self.cursor_pos["uninformed_search"]]
            self.state = "main"
            
        elif self.state == "difficulty":
            self.selected_difficulty = self.options["difficulty"][self.cursor_pos["difficulty"]]
            self.state = "main"
            
        return None

    def get_game_settings(self):
        """Returns the selected settings for game initialization"""
        algorithm_map = {
            "BFS": "bfs",
            "DFS": "dfs",
            "A*": "a_star",
            "Greedy Best-First": "greedy",
        }
        
        return {
            "algorithm": algorithm_map.get(self.selected_algorithm, "a_star"),
            "difficulty": self.selected_difficulty.lower(),
            "enemy_count": self.difficulty_settings[self.selected_difficulty]["enemies"],
            "maze_size": self.difficulty_settings[self.selected_difficulty]["maze_size"],
            "trap_damage": self.difficulty_settings[self.selected_difficulty]["trap_damage"]
        }

    def run(self):
        """Main menu loop - returns when game should start"""
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        if self.state == "main":
                            return None  # Return None if user quits
                        else:
                            self.state = "main"
                            
                    elif event.key == K_DOWN:
                        self.move_cursor(1)
                        
                    elif event.key == K_UP:
                        self.move_cursor(-1)
                        
                    elif event.key == K_RETURN:
                        result = self.select_option()
                        if result == "start_game":
                            return self.get_game_settings()
            
            self.draw_menu()
            pygame.display.update()