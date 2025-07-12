from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Camera:
    def __init__(self):
        self.offset = 0, 0

    def follow(self, target):
        x = target.rect.centerx - SCREEN_WIDTH // 2
        y = target.rect.centery - SCREEN_HEIGHT // 2
        self.offset = x, y

    def apply(self, rect):
        return rect.move(-self.offset[0], -self.offset[1])
