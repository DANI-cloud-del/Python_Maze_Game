import pygame
import os

def slice_sprite_sheet(sheet_path, columns, rows, resize_to=None):
    """
    Slices a sprite sheet into frames by grid layout.
    Returns: frames[row][col] where each row is a direction, and each col is a frame.
    """
    try:
        if not os.path.exists(sheet_path):
            raise FileNotFoundError(f"Sprite sheet not found at: {sheet_path}")
        
        sheet = pygame.image.load(sheet_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        frame_width = sheet_width // columns
        frame_height = sheet_height // rows

        print("\n=== Sprite Sheet Info ===")
        print(f"📂 Path: {sheet_path}")
        print(f"📐 Size: {sheet_width}x{sheet_height}")
        print(f"🔢 Grid: {columns} cols × {rows} rows")
        print(f"🖼️ Frame: {frame_width}x{frame_height}")
        if resize_to:
            print(f"⚖️ Resize: {resize_to[0]}x{resize_to[1]}")

        frames = []
        for row in range(rows):
            row_frames = []
            for col in range(columns):
                rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                frame = sheet.subsurface(rect)
                if resize_to:
                    frame = pygame.transform.scale(frame, resize_to)
                row_frames.append(frame)
            frames.append(row_frames)

        print(f"✅ Loaded {len(frames)} directions with {len(frames[0])} frames each")
        return frames

    except Exception as e:
        print(f"❌ Failed to load sprite sheet: {e}")
        raise
