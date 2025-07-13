import pygame
import sys
from maze import Maze
from player import Player
from camera import Camera
from utils.settings import *  # This imports all constants from settings

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Top-Down Maze Explorer")
        self.clock = pygame.time.Clock()
        
        self.maze = Maze()
        self.camera = Camera()
        
        # Start player at center of maze
        start_x = (self.maze.cols // 2) * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
        start_y = (self.maze.rows // 2) * CELL_SIZE + (CELL_SIZE - PATH_WIDTH)//2
        self.player = Player(start_x, start_y)
        
        self.visited_cells = set()
        self.update_visited_cells()
        
    def update_visited_cells(self):
        cell_x = self.player.rect.centerx // CELL_SIZE
        cell_y = self.player.rect.centery // CELL_SIZE
        
        # Reveal cells in a radius around player
        for dx in range(-VISIBLE_RADIUS, VISIBLE_RADIUS+1):
            for dy in range(-VISIBLE_RADIUS, VISIBLE_RADIUS+1):
                if (0 <= cell_x + dx < self.maze.cols and 
                    0 <= cell_y + dy < self.maze.rows):
                    self.visited_cells.add((cell_x + dx, cell_y + dy))
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.move(self.maze)
        self.update_visited_cells()
        self.camera.follow(self.player)
        
    def draw(self):
        # Dark background
        self.screen.fill(FOG_COLOR)
        
        # Draw visited maze areas
        self.maze.draw(self.screen, self.camera, self.visited_cells)
        
        # Draw player
        self.player.draw(self.screen, self.camera)
        
        # Apply lighting effect
        self.player.draw_light(self.screen, self.camera)
        
        pygame.display.flip()
        
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()