import pygame
from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT, CAMERA_ZOOM, CAMERA_SMOOTHNESS

class Camera:
    def __init__(self):
        self.true_offset = pygame.Vector2(0, 0)
        self.display_offset = pygame.Vector2(0, 0)
        self.zoom = CAMERA_ZOOM
        
    def follow(self, target):
        # Calculate target position centered on screen
        target_x = target.rect.centerx - SCREEN_WIDTH // (2 * self.zoom)
        target_y = target.rect.centery - SCREEN_HEIGHT // (2 * self.zoom)
        
        # Smooth camera movement
        self.true_offset.x += (target_x - self.true_offset.x) * CAMERA_SMOOTHNESS
        self.true_offset.y += (target_y - self.true_offset.y) * CAMERA_SMOOTHNESS
        
        # Update display offset for rendering
        self.display_offset.x = int(self.true_offset.x)
        self.display_offset.y = int(self.true_offset.y)
        
    def apply(self, rect):
        """Apply camera offset and zoom to a rectangle"""
        scaled_rect = pygame.Rect(
            (rect.x - self.display_offset.x) * self.zoom,
            (rect.y - self.display_offset.y) * self.zoom,
            rect.width * self.zoom,
            rect.height * self.zoom
        )
        return scaled_rect
        
    def apply_pos(self, pos):
        """Apply camera offset and zoom to a position"""
        return (
            (pos[0] - self.display_offset.x) * self.zoom,
            (pos[1] - self.display_offset.y) * self.zoom
        )