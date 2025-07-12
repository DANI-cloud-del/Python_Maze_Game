import pygame
import sys
from maze import Maze
from player import Player
from camera import Camera
from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CELL_SIZE

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Maze Light Explorer")
    clock = pygame.time.Clock()

    maze = Maze()
    camera = Camera()

    px = CELL_SIZE + (CELL_SIZE - 20) // 2
    py = CELL_SIZE + (CELL_SIZE - 20) // 2
    player = Player(px, py)

    visited_cells = set()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.move(maze)

        cell_x = player.rect.centerx // CELL_SIZE
        cell_y = player.rect.centery // CELL_SIZE
        visited_cells.add((cell_x, cell_y))

        camera.follow(player)

        screen.fill((0, 0, 0))

        maze.draw(screen, camera, visited_cells)
        player.draw(screen, camera)

        # 🔦 Lighting Mask
        fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        fog.fill((0, 0, 0, 220))
        pygame.draw.circle(fog, (0, 0, 0, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 120)
        screen.blit(fog, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
