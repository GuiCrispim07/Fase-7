import pygame
import math
import random
from constants import *


class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.w = 28
        self.h = 36
        self.hp = PLAYER_MAX_HP
        self.energy = PLAYER_MAX_ENERGY
        self.speed = PLAYER_SPEED
        self.shoot_timer = 0
        self.invincible = 0
        self.inverted = False
        self.score = 0
        self.surface = self._create_surface()
        self.flash_timer = 0

    def _create_surface(self):
        s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        # Jetpack thrusters
        pygame.draw.rect(s, JETPACK_GRAY, (1, 16, 6, 14))
        pygame.draw.rect(s, JETPACK_GRAY, (self.w - 7, 16, 6, 14))
        # Solar panels on jetpack
        pygame.draw.rect(s, SOLAR_GOLD, (2, 18, 4, 8))
        pygame.draw.rect(s, SOLAR_GOLD, (self.w - 6, 18, 4, 8))
        # Body
        pygame.draw.rect(s, HOPE_BODY, (7, 12, 14, 18))
        # Belt
        pygame.draw.rect(s, SOLAR_ORANGE, (7, 22, 14, 3))
        # Head
        pygame.draw.circle(s, HOPE_SKIN, (self.w // 2, 9), 7)
        # Helmet
        pygame.draw.circle(s, HOPE_HELMET, (self.w // 2, 9), 7, 2)
        # Visor
        pygame.draw.rect(s, HOPE_VISOR, (self.w // 2 - 4, 6, 8, 4))
        # Weapon barrel on top
        pygame.draw.rect(s, ENERGY_CYAN, (self.w // 2 - 2, 0, 4, 7))
        return s

    def update(self, keys, particles):
        # Movement with potential inversion
        dx, dy = 0, 0
        mult = -1 if self.inverted else 1

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed * mult
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed * mult
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed * mult
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed * mult

        self.x = max(self.w // 2, min(WIDTH - self.w // 2, self.x + dx))
        self.y = max(self.h // 2, min(HEIGHT - self.h // 2, self.y + dy))

        # Energy drain
        self.energy = max(0, self.energy - ENERGY_DRAIN_RATE)

        # Shoot cooldown
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        # Invincibility frames
        if self.invincible > 0:
            self.invincible -= 1

        if self.flash_timer > 0:
            self.flash_timer -= 1

        # Jetpack particles
        if self.energy > 0:
            particles.emit_jetpack(self.x, self.y + self.h // 2, self.energy / PLAYER_MAX_ENERGY)

    def shoot(self):
        if self.shoot_timer <= 0 and self.energy > 2:
            self.shoot_timer = SHOOT_COOLDOWN
            self.energy -= 0.8
            return Bullet(self.x, self.y - self.h // 2)
        return None

    def take_damage(self, amount=1):
        if self.invincible <= 0:
            self.hp -= amount
            self.invincible = INVINCIBLE_FRAMES
            self.flash_timer = 15
            return True
        return False

    def collect_energy(self, amount):
        self.energy = min(PLAYER_MAX_ENERGY, self.energy + amount)

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2 + 4, self.y - self.h // 2 + 4, self.w - 8, self.h - 8)

    def draw(self, surface):
        if self.invincible > 0 and self.invincible % 6 < 3:
            return
        # Glow based on energy
        energy_pct = self.energy / PLAYER_MAX_ENERGY
        if energy_pct > 0.3:
            glow = pygame.Surface((self.w + 20, self.h + 20), pygame.SRCALPHA)
            alpha = int(30 * energy_pct)
            pygame.draw.ellipse(glow, (*SOLAR_GOLD, alpha), (0, 0, self.w + 20, self.h + 20))
            surface.blit(glow, (self.x - self.w // 2 - 10, self.y - self.h // 2 - 10))

        if self.flash_timer > 0:
            flash_surf = self.surface.copy()
            flash_surf.fill((255, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(flash_surf, (self.x - self.w // 2, self.y - self.h // 2))
        else:
            surface.blit(self.surface, (self.x - self.w // 2, self.y - self.h // 2))


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = BULLET_SPEED
        self.w = 4
        self.h = 12
        self.alive = True

    def update(self, particles):
        self.y -= self.speed
        if self.y < -10:
            self.alive = False
        particles.emit_trail(self.x, self.y + 6, ENERGY_CYAN, 1)

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def draw(self, surface):
        # Beam glow
        glow = pygame.Surface((16, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*ENERGY_CYAN, 40), (0, 0, 16, 20))
        surface.blit(glow, (self.x - 8, self.y - 10))
        pygame.draw.rect(surface, ENERGY_BEAM, (self.x - 2, self.y - 6, 4, 12))
        pygame.draw.rect(surface, WHITE, (self.x - 1, self.y - 5, 2, 10))


class EnemyBullet:
    def __init__(self, x, y, vx=0, vy=3, toxic=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = 6 if toxic else 4
        self.alive = True
        self.toxic = toxic
        self.color = UMAN_TOXIC if toxic else UMAN_RED

    def update(self, particles):
        self.x += self.vx
        self.y += self.vy
        if self.y > HEIGHT + 10 or self.y < -10 or self.x < -10 or self.x > WIDTH + 10:
            self.alive = False
        if self.toxic and random.random() < 0.3:
            particles.emit_trail(self.x, self.y, UMAN_TOXIC, 1)

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        if self.toxic:
            pygame.draw.circle(surface, (150, 255, 100), (int(self.x), int(self.y)), self.size - 2)
