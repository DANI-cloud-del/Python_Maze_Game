class LevelManager:
    def __init__(self):
        self.score = 0
        self.level = 1

    def update_score(self, points):
        self.score += points
        if self.score >= self.level * 100:
            self.level += 1
            return True  # trigger maze regeneration
        return False
