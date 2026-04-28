import pygame
import random
import math


class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, life=30, size=3, gravity=0, shrink=True, glow=False):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity
        self.shrink = shrink
        self.glow = glow

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        alpha = self.life / self.max_life
        cur_size = max(1, int(self.size * alpha)) if self.shrink else self.size
        r = min(255, int(self.color[0] * alpha + 50 * (1 - alpha)))
        g = min(255, int(self.color[1] * alpha))
        b = min(255, int(self.color[2] * alpha))
        if self.glow and cur_size > 2:
            glow_surf = pygame.Surface((cur_size * 4, cur_size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (r, g, b, int(40 * alpha)), (cur_size * 2, cur_size * 2), cur_size * 2)
            surface.blit(glow_surf, (int(self.x - cur_size * 2), int(self.y - cur_size * 2)))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), cur_size)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add(self, particle):
        self.particles.append(particle)

    def emit_burst(self, x, y, color, count=10, speed=3, life=20, size=3, gravity=0, glow=False):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(0.5, speed)
            self.particles.append(Particle(
                x, y, color,
                vx=math.cos(angle) * spd,
                vy=math.sin(angle) * spd,
                life=random.randint(life // 2, life),
                size=random.randint(max(1, size - 1), size + 1),
                gravity=gravity, glow=glow
            ))

    def emit_jetpack(self, x, y, energy_pct):
        if energy_pct > 0.5:
            color = (255, 200, 50)
        elif energy_pct > 0.2:
            color = (255, 140, 30)
        else:
            color = (255, 60, 20)
        for _ in range(3):
            self.particles.append(Particle(
                x + random.randint(-4, 4), y,
                color,
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(1, 3),
                life=random.randint(8, 18),
                size=random.randint(2, 4),
                glow=True
            ))

    def emit_trail(self, x, y, color, count=2):
        for _ in range(count):
            self.particles.append(Particle(
                x + random.randint(-2, 2), y + random.randint(-2, 2),
                color,
                vx=random.uniform(-0.3, 0.3),
                vy=random.uniform(-0.3, 0.3),
                life=random.randint(5, 12),
                size=random.randint(1, 2)
            ))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
