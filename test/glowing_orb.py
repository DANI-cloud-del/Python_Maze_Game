import pygame
import random
import math
from pygame import gfxdraw  # For smoother circles with anti-aliasing

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.SCALED | pygame.DOUBLEBUF)
pygame.display.set_caption("Glowing Orb Simulation")
clock = pygame.time.Clock()

# Color constants
BACKGROUND = (5, 5, 10)
ORB_CORE = (255, 255, 255)
PARTICLE_COLORS = [
    (255, 255, 255),  # White
    (200, 230, 255),  # Cool blue
    (255, 230, 200)   # Warm white
]

class Particle:
    def __init__(self, x, y, color_variation=True):
        self.pos = pygame.Vector2(x, y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.2, 0.8)  # Wider speed range
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.life = random.randint(80, 200)  # More variation
        self.max_life = self.life
        self.size = random.uniform(1.5, 4.5)  # Float for smoother size changes
        self.color = random.choice(PARTICLE_COLORS) if color_variation else ORB_CORE
        self.glow_size = self.size * 3  # Glow extends beyond particle
        
        # Add slight acceleration/deceleration
        self.accel = pygame.Vector2(
            random.uniform(-0.005, 0.005),
            random.uniform(-0.005, 0.005)
        )

    def update(self):
        self.vel += self.accel
        self.pos += self.vel
        self.life -= 1
        # Gradually reduce size
        self.size = max(0.5, self.size * 0.99)
        
    def draw(self, surface):
        if self.life > 0:
            # Calculate alpha with easing function for smoother fade
            life_ratio = self.life / self.max_life
            alpha = int(255 * (1 - (1 - life_ratio) ** 2))
            
            # Draw glow first (larger, more transparent)
            glow_surf = pygame.Surface((self.glow_size * 2, self.glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf, 
                (*self.color[:3], alpha // 3),  # More transparent
                (self.glow_size, self.glow_size), 
                self.glow_size
            )
            surface.blit(glow_surf, (self.pos.x - self.glow_size, self.pos.y - self.glow_size))
            
            # Draw particle core
            particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surf, 
                (*self.color[:3], alpha),
                (self.size, self.size), 
                self.size
            )
            surface.blit(particle_surf, (self.pos.x - self.size, self.pos.y - self.size))


class GlowingOrb:
    def __init__(self, x, y):
        self.center = pygame.Vector2(x, y)
        self.radius = 30
        self.particles = []
        self.pulse_timer = 0
        self.pulse_interval = 2  # seconds
        self.base_radius = 30
        self.target_radius = 35
        self.current_radius = self.base_radius
        
        # For smooth movement
        self.target_pos = pygame.Vector2(x, y)
        self.move_speed = 0.02
        
    def update(self, dt):
        # Smooth movement toward target
        self.center += (self.target_pos - self.center) * self.move_speed
        
        # Pulsing effect
        self.pulse_timer += dt
        if self.pulse_timer >= self.pulse_interval:
            self.pulse_timer = 0
            self.target_radius = self.base_radius + random.uniform(3, 7)
        
        # Smooth radius change
        self.current_radius += (self.target_radius - self.current_radius) * 0.1
        
        # Particle emission with burst during pulse
        emission_rate = 0.03
        if self.pulse_timer < 0.5:  # During pulse
            emission_rate = 0.15
            
        if random.random() < emission_rate:
            self.particles.append(Particle(self.center.x, self.center.y))
            
        # Update particles
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
                
    def set_target(self, x, y):
        self.target_pos = pygame.Vector2(x, y)
        
    def draw(self, surface):
        # Draw glow effect
        for i in range(3, 0, -1):
            glow_radius = self.current_radius * i
            alpha = 50 // i
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf, 
                (*ORB_CORE, alpha),
                (glow_radius, glow_radius), 
                glow_radius
            )
            surface.blit(
                glow_surf, 
                (self.center.x - glow_radius, self.center.y - glow_radius)
            )
        
        # Draw core with anti-aliasing
        core_surf = pygame.Surface((self.current_radius * 2, self.current_radius * 2), pygame.SRCALPHA)
        gfxdraw.aacircle(
            core_surf,
            int(self.current_radius), 
            int(self.current_radius), 
            int(self.current_radius), 
            ORB_CORE
        )
        gfxdraw.filled_circle(
            core_surf,
            int(self.current_radius), 
            int(self.current_radius), 
            int(self.current_radius), 
            ORB_CORE
        )
        surface.blit(
            core_surf, 
            (self.center.x - self.current_radius, self.center.y - self.current_radius)
        )
        
        # Draw particles
        for p in sorted(self.particles, key=lambda p: p.size):  # Sort for proper blending
            p.draw(surface)

orb = GlowingOrb(400, 300)
running = True
last_time = pygame.time.get_ticks()

while running:
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_time) / 1000.0  # Delta time in seconds
    last_time = current_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            orb.set_target(event.pos[0], event.pos[1])
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill(BACKGROUND)
    orb.update(dt)
    orb.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()