# menu.py
import pygame
import sys
from pygame.locals import *

class GameMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.state = "main"
        self.selected_algorithm = None
        self.selected_difficulty = "Medium"
        self.algorithm_type = "search"  # "search" or "non-search"
        
        # Colors
        self.colors = {
            "title": (0, 200, 200),
            "normal": (255, 255, 255),
            "highlight": (0, 255, 0),
            "background": (20, 20, 40)
        }
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 48)
        self.menu_font = pygame.font.SysFont('Arial', 36)
        self.submenu_font = pygame.font.SysFont('Arial', 28)
        
        # Menu options
        self.options = {
            "main": ["Start Game", "Select Algorithm", "Select Difficulty", "Quit"],
            "algorithm_type": ["Search-Based", "Non-Search-Based"],
            "search_algorithms": ["DFS", "BFS", "A*", "Dijkstra"],
            "non_search_algorithms": ["Wall-Follower", "Random Walk", "Potential Fields", "Genetic"],
            "difficulty": ["Easy", "Medium", "Hard"]
        }
        
        # Cursor positions
        self.cursor_pos = {
            "main": 0,
            "algorithm_type": 0,
            "search_algorithms": 0,
            "non_search_algorithms": 0,
            "difficulty": 1  # Default to Medium
        }
        
        # Algorithm descriptions
        self.algorithm_descriptions = {
            "DFS": "Depth-First Search: Explores deep paths first",
            "BFS": "Breadth-First Search: Finds shortest path",
            "A*": "A* Search: Optimal path with heuristics",
            "Dijkstra": "Dijkstra: Handles weighted paths",
            "Wall-Follower": "Follows walls (right-hand rule)",
            "Random Walk": "Moves randomly with slight bias",
            "Potential Fields": "Attracted to goal, repelled by walls",
            "Genetic": "Evolutionary pathfinding approach"
        }
        
        # Difficulty settings
        self.difficulty_settings = {
            "Easy": {"enemies": 3, "maze_size": (15, 15), "trap_damage": 10},
            "Medium": {"enemies": 5, "maze_size": (20, 20), "trap_damage": 20},
            "Hard": {"enemies": 8, "maze_size": (25, 25), "trap_damage": 30}
        }

    def draw_text(self, text, font, color, y_offset=0, x_offset=0):
        text_surface = font.render(text, True, color)
        x = self.width // 2 - text_surface.get_width() // 2 + x_offset
        y = self.height // 3 + y_offset
        self.screen.blit(text_surface, (x, y))
        return text_surface.get_rect(topleft=(x, y))

    def draw_menu(self):
        self.screen.fill(self.colors["background"])
        
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
                
        elif self.state in ["search_algorithms", "non_search_algorithms"]:
            algo_type = "Search-Based" if self.state == "search_algorithms" else "Non-Search-Based"
            self.draw_text(algo_type, self.menu_font, self.colors["title"], 50)
            
            algorithms = self.options[self.state]
            for i, algo in enumerate(algorithms):
                color = self.colors["highlight"] if i == self.cursor_pos[self.state] else self.colors["normal"]
                self.draw_text(algo, self.submenu_font, color, 120 + i * 40)
                
                # Draw description
                desc = self.algorithm_descriptions[algo]
                self.draw_text(desc, self.submenu_font, self.colors["normal"], 120 + i * 40, 200)
                
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
        elif self.state == "search_algorithms":
            self.cursor_pos["search_algorithms"] = (self.cursor_pos["search_algorithms"] + direction) % len(self.options["search_algorithms"])
        elif self.state == "non_search_algorithms":
            self.cursor_pos["non_search_algorithms"] = (self.cursor_pos["non_search_algorithms"] + direction) % len(self.options["non_search_algorithms"])
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
            if self.cursor_pos["algorithm_type"] == 0:  # Search-Based
                self.state = "search_algorithms"
                self.algorithm_type = "search"
            else:  # Non-Search-Based
                self.state = "non_search_algorithms"
                self.algorithm_type = "non-search"
                
        elif self.state == "search_algorithms":
            self.selected_algorithm = self.options["search_algorithms"][self.cursor_pos["search_algorithms"]]
            self.state = "main"
            
        elif self.state == "non_search_algorithms":
            self.selected_algorithm = self.options["non_search_algorithms"][self.cursor_pos["non_search_algorithms"]]
            self.state = "main"
            
        elif self.state == "difficulty":
            self.selected_difficulty = self.options["difficulty"][self.cursor_pos["difficulty"]]
            self.state = "main"
            
        return None

    def get_game_settings(self):
        """Returns the selected settings for game initialization"""
        return {
            "algorithm": self.selected_algorithm.lower().replace("*", "star").replace("-", "_"),
            "difficulty": self.selected_difficulty.lower(),
            "enemy_count": self.difficulty_settings[self.selected_difficulty]["enemies"],
            "maze_size": self.difficulty_settings[self.selected_difficulty]["maze_size"],
            "trap_damage": self.difficulty_settings[self.selected_difficulty]["trap_damage"]
        }

    def run(self):
        """Main menu loop - returns when game should start"""
        while True:
            self.draw_menu()
            result = self.handle_input()
            if result == "start_game":
                return self.get_game_settings()