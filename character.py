import pygame
from animator import Animator
from loader import slice_sprite_sheet
from utils.settings import (
    CELL_SIZE, PLAYER_SIZE, LIGHT_RADIUS, LIGHT_INTENSITY,
    FOG_COLOR, PATH_WIDTH
)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(
            x + (PATH_WIDTH - PLAYER_SIZE) // 2,
            y + (PATH_WIDTH - PLAYER_SIZE) // 2,
            PLAYER_SIZE,
            PLAYER_SIZE
        )
        self.speed = 4
        self.direction = pygame.Vector2(0, 0)
        self.animations = self.load_animations()
        self.animator = Animator(self.animations)
        self.light_mask = self.create_light_mask()

    def load_animations(self):
        # 🧠 Smart slicing with auto resize
        frames = slice_sprite_sheet(
            "assets/sprites/character/character.png",
            columns=4, rows=4,
            resize_to=(PLAYER_SIZE, PLAYER_SIZE)
        )

        # 🧬 Mapping frame rows to directions
        return {
            "walk_up": frames[0],
            "walk_down": frames[1],
            "walk_left": frames[2],
            "walk_right": frames[3],
            "idle_up": [frames[0][0]],
            "idle_down": [frames[1][0]],
            "idle_left": [frames[2][0]],
            "idle_right": [frames[3][0]],
        }

    def create_light_mask(self):
        surface = pygame.Surface((LIGHT_RADIUS * 2, LIGHT_RADIUS * 2), pygame.SRCALPHA)
        for r in range(LIGHT_RADIUS, 0, -1):
            alpha = int(LIGHT_INTENSITY * (r / LIGHT_RADIUS))
            pygame.draw.circle(surface, (*FOG_COLOR, alpha), (LIGHT_RADIUS, LIGHT_RADIUS), r)
        return surface

    def handle_input(self, keys):
        self.direction = pygame.Vector2(0, 0)
        state = ""

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
            state = "walk_up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
            state = "walk_down"
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            state = "walk_left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            state = "walk_right"
        else:
            state = f"idle_{self.get_facing()}"

        self.animator.set_state(state)

    def get_facing(self):
        if self.direction.y < 0: return "up"
        if self.direction.y > 0: return "down"
        if self.direction.x < 0: return "left"
        if self.direction.x > 0: return "right"
        return "down"

    def move(self, maze):
        new_rect = self.rect.move(self.direction.x * self.speed, self.direction.y * self.speed)
        # TODO: Add collision with maze walls
        self.rect = new_rect

    def update(self):
        self.animator.update()

    def draw(self, screen, camera):
        frame = self.animator.get_current_frame()
        screen.blit(frame, camera.apply(self.rect))

    def draw_light(self, screen, camera):
        light_pos = camera.apply_pos(self.rect.center)
        offset = LIGHT_RADIUS * camera.zoom
        light_area = pygame.transform.scale(
            self.light_mask,
            (int(offset * 2), int(offset * 2))
        )
        screen.blit(light_area, (light_pos[0] - offset, light_pos[1] - offset))
