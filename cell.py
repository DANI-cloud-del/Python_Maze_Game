from enum import Enum

class CellType(Enum):
    NORMAL = 0
    TRAP = 1
    TELEPORT = 2
    BUTTON = 3
    EXIT = 4

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False
        self.type = CellType.NORMAL
        self.linked_teleport = None
        self.triggered = False
        self.visible = False