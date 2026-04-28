import pygame
import math
import random
from constants import *
from particles import Particle


class SolarOrb:
    def __init__(self, x=None, y=None):
        self.x = x or random.randint(50, WIDTH - 50)
        self.y = y or random.randint(-200, -30)
        self.radius = 10
        self.speed = 1.2
        self.alive = True
        self.timer = 0
        self.value = ENERGY_ORB_VALUE

    def update(self):
        self.y += self.speed
        self.timer += 1
        if self.y > HEIGHT + 20:
            self.alive = False

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface):
        pulse = math.sin(self.timer * 0.1) * 3
        r = int(self.radius + pulse)
        # Outer glow
        glow = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*SOLAR_GOLD, 30), (r * 3, r * 3), r * 3)
        pygame.draw.circle(glow, (*SOLAR_ORANGE, 50), (r * 3, r * 3), r * 2)
        surface.blit(glow, (int(self.x - r * 3), int(self.y - r * 3)))
        # Core
        pygame.draw.circle(surface, SOLAR_GOLD, (int(self.x), int(self.y)), r)
        pygame.draw.circle(surface, SOLAR_BRIGHT, (int(self.x), int(self.y)), r // 2)
        # Rays
        for i in range(6):
            angle = self.timer * 0.05 + i * math.pi / 3
            ex = int(self.x + math.cos(angle) * (r + 5))
            ey = int(self.y + math.sin(angle) * (r + 5))
            pygame.draw.line(surface, SOLAR_GOLD, (int(self.x), int(self.y)), (ex, ey), 1)


class FallingDebris:
    """Rocks/stalactites that fall rapidly from above"""
    def __init__(self):
        self.x = random.randint(30, WIDTH - 30)
        self.y = -40
        self.w = random.randint(12, 25)
        self.h = random.randint(25, 50)
        self.speed = random.uniform(5, 9)
        self.alive = True
        self.warned = False
        self.warn_timer = 45  # frames of warning before falling
        self.falling = False
        self.color = CAVE_WALL

    def update(self):
        if not self.falling:
            self.warn_timer -= 1
            if self.warn_timer <= 0:
                self.falling = True
            return
        self.y += self.speed
        if self.y > HEIGHT + 60:
            self.alive = False

    def get_rect(self):
        if not self.falling:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def draw(self, surface):
        if not self.falling:
            # Warning indicator
            alpha = int(abs(math.sin(self.warn_timer * 0.2)) * 200)
            warn_surf = pygame.Surface((self.w + 20, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(warn_surf, (255, 50, 50, min(40, alpha // 3)), (0, 0, self.w + 20, HEIGHT))
            surface.blit(warn_surf, (self.x - self.w // 2 - 10, 0))
            # Arrow at top
            arrow_y = 10 + int(math.sin(self.warn_timer * 0.3) * 5)
            pygame.draw.polygon(surface, TRAP_WARNING, [
                (self.x, arrow_y + 15),
                (self.x - 8, arrow_y),
                (self.x + 8, arrow_y)
            ])
        else:
            # Stalactite shape
            points = [
                (self.x - self.w // 2, self.y - self.h // 2),
                (self.x + self.w // 2, self.y - self.h // 2),
                (self.x + self.w // 3, self.y + self.h // 2 - 5),
                (self.x, self.y + self.h // 2),
                (self.x - self.w // 3, self.y + self.h // 2 - 5),
            ]
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, CAVE_ACCENT, points, 2)


class FakeOrb:
    """Looks like a solar orb but explodes on contact"""
    def __init__(self):
        self.x = random.randint(60, WIDTH - 60)
        self.y = random.randint(-150, -30)
        self.radius = 10
        self.speed = 1.0
        self.alive = True
        self.timer = 0
        self.exploded = False

    def update(self):
        self.y += self.speed
        self.timer += 1
        if self.y > HEIGHT + 20:
            self.alive = False

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface):
        pulse = math.sin(self.timer * 0.1) * 3
        r = int(self.radius + pulse)
        # Looks similar to solar orb but slightly different hue
        glow = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*FAKE_ORB, 25), (r * 3, r * 3), r * 3)
        surface.blit(glow, (int(self.x - r * 3), int(self.y - r * 3)))
        pygame.draw.circle(surface, FAKE_ORB, (int(self.x), int(self.y)), r)
        # Subtle skull-like pattern (two dots and line) - hard to notice
        pygame.draw.circle(surface, (180, 180, 0), (int(self.x) - 2, int(self.y) - 2), 1)
        pygame.draw.circle(surface, (180, 180, 0), (int(self.x) + 2, int(self.y) - 2), 1)


class ToxicZone:
    """Area that damages the player if they stay in it"""
    def __init__(self, x=None, y_target=None):
        self.x = x or random.randint(100, WIDTH - 100)
        self.y = y_target or random.randint(150, HEIGHT - 150)
        self.radius = random.randint(50, 90)
        self.alive = True
        self.timer = 0
        self.duration = 300  # 5 seconds
        self.alpha_dir = 1
        self.alpha = 0

    def update(self):
        self.timer += 1
        self.alpha += self.alpha_dir * 2
        if self.alpha >= 80:
            self.alpha_dir = -1
        elif self.alpha <= 30:
            self.alpha_dir = 1
        if self.timer > self.duration:
            self.alive = False

    def contains(self, rect):
        cx = rect.centerx
        cy = rect.centery
        dist = math.sqrt((cx - self.x) ** 2 + (cy - self.y) ** 2)
        return dist < self.radius

    def draw(self, surface):
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*UMAN_TOXIC, int(self.alpha)), (self.radius, self.radius), self.radius)
        pygame.draw.circle(s, (*TOXIC_GREEN, int(self.alpha * 0.6)), (self.radius, self.radius), self.radius, 2)
        surface.blit(s, (self.x - self.radius, self.y - self.radius))
        # Hazard symbol
        if self.timer % 40 < 20:
            font = pygame.font.Font(None, 20)
            txt = font.render("☠", True, UMAN_TOXIC)
            surface.blit(txt, (self.x - txt.get_width() // 2, self.y - txt.get_height() // 2))


class TrapManager:
    """Manages Level Devil style traps"""
    def __init__(self):
        self.debris_list = []
        self.fake_orbs = []
        self.toxic_zones = []
        self.inversion_active = False
        self.inversion_timer = 0
        self.inversion_duration = 0
        self.glitch_active = False
        self.glitch_timer = 0
        self.glitch_duration = 0
        self.spawn_timers = {
            "debris": 0,
            "fake_orb": 0,
            "toxic": 0,
            "inversion": 0,
            "glitch": 0
        }
        self.wave_difficulty = 0  # increases with waves
        self.warning_text = ""
        self.warning_timer = 0

    def set_difficulty(self, wave_num):
        self.wave_difficulty = wave_num

    def show_warning(self, text):
        self.warning_text = text
        self.warning_timer = 90

    def update(self, player):
        # Update timers
        for k in self.spawn_timers:
            if self.spawn_timers[k] > 0:
                self.spawn_timers[k] -= 1

        if self.warning_timer > 0:
            self.warning_timer -= 1

        # Spawn traps based on difficulty
        if self.wave_difficulty >= 1 and self.spawn_timers["debris"] <= 0:
            interval = max(30, 90 - self.wave_difficulty * 10)
            if random.random() < 0.02 + self.wave_difficulty * 0.008:
                count = min(4, 1 + self.wave_difficulty // 2)
                for _ in range(count):
                    self.debris_list.append(FallingDebris())
                self.spawn_timers["debris"] = interval

        if self.wave_difficulty >= 2 and self.spawn_timers["fake_orb"] <= 0:
            if random.random() < 0.005 + self.wave_difficulty * 0.003:
                self.fake_orbs.append(FakeOrb())
                self.spawn_timers["fake_orb"] = 180

        if self.wave_difficulty >= 3 and self.spawn_timers["toxic"] <= 0:
            if random.random() < 0.003 + self.wave_difficulty * 0.002:
                self.toxic_zones.append(ToxicZone())
                self.spawn_timers["toxic"] = 300

        if self.wave_difficulty >= 2 and self.spawn_timers["inversion"] <= 0:
            if random.random() < 0.001 + self.wave_difficulty * 0.001:
                self.inversion_active = True
                self.inversion_duration = 120 + self.wave_difficulty * 30
                self.inversion_timer = self.inversion_duration
                self.spawn_timers["inversion"] = 600
                self.show_warning("CONTROLES INVERTIDOS!")

        if self.wave_difficulty >= 4 and self.spawn_timers["glitch"] <= 0:
            if random.random() < 0.002:
                self.glitch_active = True
                self.glitch_duration = 90
                self.glitch_timer = self.glitch_duration
                self.spawn_timers["glitch"] = 500
                self.show_warning("INTERFERÊNCIA DE GLITCH!")

        # Update inversion
        if self.inversion_active:
            self.inversion_timer -= 1
            player.inverted = True
            if self.inversion_timer <= 0:
                self.inversion_active = False
                player.inverted = False

        # Update glitch
        if self.glitch_active:
            self.glitch_timer -= 1
            if self.glitch_timer <= 0:
                self.glitch_active = False

        # Update debris
        for d in self.debris_list:
            d.update()
        self.debris_list = [d for d in self.debris_list if d.alive]

        # Update fake orbs
        for fo in self.fake_orbs:
            fo.update()
        self.fake_orbs = [fo for fo in self.fake_orbs if fo.alive]

        # Update toxic zones
        for tz in self.toxic_zones:
            tz.update()
        self.toxic_zones = [tz for tz in self.toxic_zones if tz.alive]

        # Check collisions with player
        damage_dealt = False
        p_rect = player.get_rect()

        for d in self.debris_list:
            if d.falling and d.get_rect().colliderect(p_rect):
                if player.take_damage():
                    damage_dealt = True
                d.alive = False

        for fo in self.fake_orbs:
            if fo.get_rect().colliderect(p_rect):
                if player.take_damage(2):
                    damage_dealt = True
                fo.alive = False
                fo.exploded = True

        for tz in self.toxic_zones:
            if tz.contains(p_rect) and random.random() < 0.02:
                player.energy = max(0, player.energy - 3)

        return damage_dealt

    def draw(self, surface):
        for tz in self.toxic_zones:
            tz.draw(surface)
        for d in self.debris_list:
            d.draw(surface)
        for fo in self.fake_orbs:
            fo.draw(surface)

        # Inversion warning overlay
        if self.inversion_active:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = int(abs(math.sin(self.inversion_timer * 0.1)) * 25)
            overlay.fill((255, 0, 100, alpha))
            surface.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 28)
            remaining = max(0, self.inversion_timer // 60)
            txt = font.render(f"CONTROLES INVERTIDOS! {remaining + 1}s", True, TRAP_WARNING)
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 50))

        # Glitch effect
        if self.glitch_active:
            for _ in range(5):
                y = random.randint(0, HEIGHT)
                h = random.randint(2, 8)
                offset = random.randint(-15, 15)
                strip = surface.subsurface(pygame.Rect(0, max(0, y), WIDTH, min(h, HEIGHT - y))).copy()
                surface.blit(strip, (offset, y))

        # Warning text
        if self.warning_timer > 0:
            font = pygame.font.Font(None, 42)
            alpha = min(255, self.warning_timer * 5)
            txt = font.render(self.warning_text, True, TRAP_WARNING)
            txt.set_alpha(alpha)
            y = HEIGHT // 2 - 80 + int(math.sin(self.warning_timer * 0.15) * 5)
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y))
