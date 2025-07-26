import pygame
import sys
import math
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Watching Eyes")
clock = pygame.time.Clock()

class WatchingEyes:
    def __init__(self, center):
        self.center = pygame.Vector2(center)
        self.offset = 60
        self.base_radius = 12
        self.current_radius = 12
        self.alpha = 0
        self.fade_in = True
        self.timer = 0
        self.pulse_phase = 0
        self.glare_alpha = 0
        self.eye_color = (200, 0, 0)  # Darker red
        self.pupil_offset = pygame.Vector2(0, 0)
        self.blood_veins = []
        self.init_blood_veins()
        self.blink_timer = random.randint(100, 300)
        self.blinking = False
        self.blink_progress = 0
        self.eye_twitch_timer = 0
        self.eye_twitch_offset = pygame.Vector2(0, 0)
        self.breathing_speed = 0.03
        self.distortion_timer = 0

    def init_blood_veins(self):
        # Create blood vein patterns for each eye
        for _ in range(8):
            self.blood_veins.append({
                'start_angle': random.uniform(0, math.pi*2),
                'length': random.uniform(0.3, 0.8),
                'thickness': random.uniform(1, 2),
                'pulse_phase': random.uniform(0, math.pi*2)
            })

    def update(self):
        self.timer += 1
        self.pulse_phase += self.breathing_speed
        self.distortion_timer += 1

        # Random eye twitching
        if self.eye_twitch_timer <= 0:
            self.eye_twitch_offset = pygame.Vector2(
                random.uniform(-3, 3),
                random.uniform(-3, 3)
            )
            self.eye_twitch_timer = random.randint(10, 60)
        else:
            self.eye_twitch_timer -= 1
            self.eye_twitch_offset *= 0.9  # Dampen the twitch

        # Pulsing effect with occasional irregular heartbeat
        if random.random() < 0.005:  # 0.5% chance per frame
            self.breathing_speed = random.uniform(0.1, 0.3)  # Fast pulse
        else:
            self.breathing_speed = 0.03  # Normal speed
            
        pulse = 1 + math.sin(self.pulse_phase) * 0.3
        self.current_radius = int(self.base_radius * pulse)

        # Blinking behavior
        if self.blink_timer <= 0:
            self.blinking = True
            self.blink_timer = random.randint(100, 300)
        else:
            self.blink_timer -= 1

        if self.blinking:
            self.blink_progress += 0.1
            if self.blink_progress >= math.pi:
                self.blinking = False
                self.blink_progress = 0
                # Occasionally stay closed longer
                if random.random() < 0.3:
                    self.blink_timer = random.randint(30, 90)

        # Fade logic with random interruptions
        if random.random() < 0.002:  # 0.2% chance per frame to interrupt fade
            self.fade_in = not self.fade_in

        if self.fade_in:
            self.alpha = min(255, self.alpha + 3)
            if self.alpha >= 255 and self.timer > 100:
                self.fade_in = False
        else:
            self.alpha = max(0, self.alpha - 3)
            if self.alpha <= 0:
                self.timer = 0
                self.fade_in = True
                # Random chance to reappear somewhere else
                if random.random() < 0.2:
                    self.center = pygame.Vector2(
                        random.randint(200, 600),
                        random.randint(150, 450))

        # Glare effect with occasional flashes
        if random.random() < 0.01:  # 1% chance per frame for flash
            self.glare_alpha = random.randint(150, 220)
        else:
            self.glare_alpha = int(50 + 30 * math.sin(pygame.time.get_ticks() * 0.003))

        # Track mouse position for pupil movement (creepy following effect)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        direction = mouse_pos - self.center
        if direction.length() > 0:
            direction = direction.normalize() * min(8, direction.length()/50)
        self.pupil_offset = direction * 0.5 + self.pupil_offset * 0.5  # Smooth follow

    def draw_blood_veins(self, surface, eye_pos):
        for vein in self.blood_veins:
            vein_pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.002 + vein['pulse_phase'])
            end_pos = (
                eye_pos[0] + math.cos(vein['start_angle']) * self.current_radius * vein['length'] * vein_pulse,
                eye_pos[1] + math.sin(vein['start_angle']) * self.current_radius * vein['length'] * vein_pulse
            )
            pygame.draw.line(
                surface, 
                (150, 0, 0, self.alpha), 
                eye_pos, 
                end_pos, 
                int(vein['thickness'] * vein_pulse)
            )

    def draw(self, surface):
        if self.alpha <= 0:
            return

        # Create eye surface with per-pixel alpha
        eye_surface = pygame.Surface((self.offset * 3, self.offset * 2), pygame.SRCALPHA)
        left_eye_pos = (self.offset, self.offset)
        right_eye_pos = (self.offset * 2, self.offset)

        # Apply blinking effect
        blink_scale = 1.0
        if self.blinking:
            blink_scale = abs(math.sin(self.blink_progress))

        # Draw blood veins
        self.draw_blood_veins(eye_surface, left_eye_pos)
        self.draw_blood_veins(eye_surface, right_eye_pos)

        # Draw eye whites (only visible when not fully blinked)
        if blink_scale > 0.2:
            white_alpha = min(40, self.alpha)
            pygame.draw.circle(eye_surface, (255, 255, 255, white_alpha), left_eye_pos, int(self.current_radius * blink_scale))
            pygame.draw.circle(eye_surface, (255, 255, 255, white_alpha), right_eye_pos, int(self.current_radius * blink_scale))

        # Draw main eye color
        eye_color = (*self.eye_color, self.alpha)
        pygame.draw.circle(eye_surface, eye_color, left_eye_pos, int(self.current_radius * blink_scale))
        pygame.draw.circle(eye_surface, eye_color, right_eye_pos, int(self.current_radius * blink_scale))

        # Draw pupils with offset (creepy following effect)
        if blink_scale > 0.5:  # Don't draw pupils when mostly blinked
            pupil_radius = max(2, self.current_radius // 2)
            pygame.draw.circle(
                eye_surface, (0, 0, 0, self.alpha),
                (int(left_eye_pos[0] + self.pupil_offset.x), int(left_eye_pos[1] + self.pupil_offset.y)),
                pupil_radius
            )
            pygame.draw.circle(
                eye_surface, (0, 0, 0, self.alpha),
                (int(right_eye_pos[0] + self.pupil_offset.x), int(right_eye_pos[1] + self.pupil_offset.y)),
                pupil_radius
            )

        # Draw glare (only when not blinked)
        if blink_scale > 0.7:
            glare_color = (255, 255, 255, int(self.glare_alpha * blink_scale))
            glare_size = max(2, self.current_radius // 3)
            pygame.draw.circle(
                eye_surface, glare_color,
                (int(left_eye_pos[0] - 3 + self.pupil_offset.x*0.3), int(left_eye_pos[1] - 4 + self.pupil_offset.y*0.3)),
                glare_size
            )
            pygame.draw.circle(
                eye_surface, glare_color,
                (int(right_eye_pos[0] - 3 + self.pupil_offset.x*0.3), int(right_eye_pos[1] - 4 + self.pupil_offset.y*0.3)),
                glare_size
            )

        # Apply distortion effect occasionally
        if self.distortion_timer % 200 < 10:  # Brief distortion every ~3 seconds
            distortion = pygame.Surface((self.offset * 3, self.offset * 2), pygame.SRCALPHA)
            distortion.blit(eye_surface, (0, 0))
            for i in range(5):  # Create multiple offset copies for distortion
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
                distortion.blit(
                    eye_surface, 
                    (offset_x, offset_y), 
                    special_flags=pygame.BLEND_ADD
                )
            eye_surface = distortion

        # Apply twitch offset
        blit_pos = (
            self.center.x - self.offset * 1.5 + self.eye_twitch_offset.x,
            self.center.y - self.offset + self.eye_twitch_offset.y
        )
        surface.blit(eye_surface, blit_pos)

# Initialize eyes
eyes = WatchingEyes(center=(400, 300))
flicker_timer = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    # Dark background with subtle flickering
    flicker_timer += 1
    flicker = 0
    if random.random() < 0.05:  # 5% chance per frame for flicker
        flicker = random.randint(-10, 5)
    bg_color = max(5, min(25, 15 + flicker))
    screen.fill((bg_color, bg_color, bg_color))

    # Draw faint circular vignette
    vignette = pygame.Surface((800, 600), pygame.SRCALPHA)
    pygame.draw.circle(
        vignette, (0, 0, 0, 180),
        (400, 300), 450
    )
    screen.blit(vignette, (0, 0))

    # Update and draw eyes
    eyes.update()
    eyes.draw(screen)

    # Occasionally draw faint afterimage
    if random.random() < 0.02:  # 2% chance per frame
        afterimage = pygame.Surface((800, 600), pygame.SRCALPHA)
        eyes.draw(afterimage)
        afterimage.set_alpha(30)
        screen.blit(afterimage, (0, 0))

    pygame.display.flip()
    clock.tick(60)