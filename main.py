# main.py

import pygame
import sys
from maze import Maze
from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from player import Player


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Maze Chase Game")
    clock = pygame.time.Clock()

    # 📦 Maze Initialization (outside the loop)
    maze = Maze()
    player = Player(0, 0)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            screen.fill((0, 0, 0))  # Background

            maze.draw(screen)

            keys = pygame.key.get_pressed()
            player.move(keys)
            player.draw(screen)

            pygame.display.flip()
            clock.tick(FPS)


    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
