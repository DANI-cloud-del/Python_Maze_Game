import pygame
import os

def load_character_sheet(sheet_path):
    """
    Loads any-size sprite sheet using a 4x4 grid layout.
    Maps directions as:
    Row 0 → down
    Row 1 → left
    Row 2 → right
    Row 3 → up
    """
    if not os.path.exists(sheet_path):
        raise FileNotFoundError(f"Sprite sheet not found: {sheet_path}")

    sheet = pygame.image.load(sheet_path).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()

    COLS = 4
    ROWS = 4
    FRAME_WIDTH = sheet_width // COLS
    FRAME_HEIGHT = sheet_height // ROWS
    FRAME_SIZE = (FRAME_WIDTH, FRAME_HEIGHT)

    # Revised animation layout
    ANIMATIONS = {
        "walk_down":  {'row': 0, 'frames': 4},
        "walk_left":  {'row': 1, 'frames': 4},
        "walk_right": {'row': 2, 'frames': 4},
        "walk_up":    {'row': 3, 'frames': 4},

        "idle_down":  {'row': 0, 'frames': 1},
        "idle_left":  {'row': 1, 'frames': 1},
        "idle_right": {'row': 2, 'frames': 1},
        "idle_up":    {'row': 3, 'frames': 1}
    }

    frames = {}
    for name, data in ANIMATIONS.items():
        row_frames = []
        y = data['row'] * FRAME_HEIGHT
        for col in range(data['frames']):
            x = col * FRAME_WIDTH
            frame = sheet.subsurface(pygame.Rect(x, y, FRAME_WIDTH, FRAME_HEIGHT))
            row_frames.append(frame)
        frames[name] = row_frames

    return {
        "sheet": sheet,
        "frames": frames,
        "metadata": {
            "frame_size": FRAME_SIZE,
            "grid": (COLS, ROWS),
            "animations": ANIMATIONS,
            "anchor_point": (FRAME_WIDTH // 2, int(FRAME_HEIGHT * 0.9))
        }
    }
