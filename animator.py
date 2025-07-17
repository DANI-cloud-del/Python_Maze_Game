import pygame
class Animator:
    def __init__(self, sprite_data, default_anim='idle_down'):
        """
        Enhanced animator for prompt-compliant sprite sheets
        """
        self.frames = sprite_data['frames']
        self.metadata = sprite_data['metadata']
        self.current_anim = default_anim
        self.frame_index = 0
        self.anim_speed = 100  # ms per frame
        self.last_update = pygame.time.get_ticks()
        self.flipped = False

        # Validate default animation exists
        if default_anim not in self.frames:
            raise ValueError(f"Missing default animation: {default_anim}")

    def set_animation(self, name, force_reset=False):
        """Switch animations with validation"""
        if name not in self.frames:
            print(f"⚠️ Missing animation: {name}")
            return False
            
        if force_reset or name != self.current_anim:
            self.current_anim = name
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()
            return True
        return False

    def update(self, dt):
        """Progress animation"""
        self.last_update += dt
        if self.last_update >= self.anim_speed:
            self.frame_index = (self.frame_index + 1) % len(self.frames[self.current_anim])
            self.last_update = 0

    def get_current_frame(self):
        """Get frame with optional horizontal flip"""
        frame = self.frames[self.current_anim][self.frame_index]
        return pygame.transform.flip(frame, self.flipped, False)

    def get_anchor_offset(self):
        """Get drawing offset for center-bottom anchor"""
        return (
            self.metadata['anchor_point'][0],
            self.metadata['anchor_point'][1] - self.metadata['frame_size'][1]
        )