import pygame
import math
import random
from constants import *
from player import EnemyBullet


class Enemy:
    def __init__(self, etype, x, y):
        cfg = ENEMY_CONFIGS[etype]
        self.etype = etype
        self.x = x
        self.y = y
        self.w, self.h = cfg["size"]
        self.hp = cfg["hp"]
        self.max_hp = cfg["hp"]
        self.speed = cfg["speed"]
        self.score = cfg["score"]
        self.shoot_rate = cfg["shoot_rate"]
        self.shoot_timer = random.randint(30, self.shoot_rate)
        self.color = cfg["color"]
        self.accent = cfg["accent"]
        self.alive = True
        self.move_timer = 0
        self.move_pattern = random.choice(["straight", "sine", "zigzag"])
        self.start_x = x
        self.phase = random.uniform(0, math.pi * 2)

    def update(self, player_x, player_y):
        self.move_timer += 1
        bullets = []

        if self.etype == "drone":
            if self.move_pattern == "sine":
                self.x = self.start_x + math.sin(self.move_timer * 0.03 + self.phase) * 80
            self.y += self.speed

        elif self.etype == "bomber":
            self.x = self.start_x + math.sin(self.move_timer * 0.02 + self.phase) * 120
            self.y += self.speed * 0.7
            if self.shoot_timer <= 0:
                self.shoot_timer = self.shoot_rate
                # Drop toxic bombs
                bullets.append(EnemyBullet(self.x, self.y + self.h // 2, 0, 2.5, toxic=True))

        elif self.etype == "elite":
            # Aggressive: track player X
            if self.x < player_x - 10:
                self.x += self.speed * 0.6
            elif self.x > player_x + 10:
                self.x -= self.speed * 0.6
            self.y += self.speed * 0.4
            if self.shoot_timer <= 0:
                self.shoot_timer = self.shoot_rate
                angle = math.atan2(player_y - self.y, player_x - self.x)
                spd = 4
                bullets.append(EnemyBullet(
                    self.x, self.y + self.h // 2,
                    math.cos(angle) * spd, math.sin(angle) * spd
                ))

        # Generic shooting for drones
        if self.etype == "drone":
            if self.shoot_timer <= 0:
                self.shoot_timer = self.shoot_rate
                bullets.append(EnemyBullet(self.x, self.y + self.h // 2, 0, 3))

        self.shoot_timer -= 1

        if self.y > HEIGHT + 50:
            self.alive = False

        return bullets

    def take_damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        hw, hh = self.w // 2, self.h // 2

        if self.etype == "drone":
            # Hexagonal drone
            points = []
            for i in range(6):
                angle = math.pi / 6 + i * math.pi / 3
                points.append((cx + int(hw * math.cos(angle)), cy + int(hh * math.sin(angle))))
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, self.accent, points, 2)
            # Eyes
            pygame.draw.circle(surface, self.accent, (cx - 4, cy - 2), 3)
            pygame.draw.circle(surface, self.accent, (cx + 4, cy - 2), 3)

        elif self.etype == "bomber":
            # Bulky bomber
            pygame.draw.rect(surface, self.color, (cx - hw, cy - hh, self.w, self.h), border_radius=4)
            pygame.draw.rect(surface, self.accent, (cx - hw + 2, cy - hh + 2, self.w - 4, self.h - 4), 2, border_radius=3)
            # Toxic container
            pygame.draw.rect(surface, UMAN_TOXIC, (cx - 5, cy + 4, 10, 8))
            pygame.draw.rect(surface, (50, 150, 30), (cx - 5, cy + 4, 10, 8), 1)
            # Eyes
            pygame.draw.circle(surface, self.accent, (cx - 6, cy - 5), 3)
            pygame.draw.circle(surface, self.accent, (cx + 6, cy - 5), 3)

        elif self.etype == "elite":
            # Sleek elite
            points = [
                (cx, cy - hh),
                (cx + hw, cy + hh // 2),
                (cx + hw - 4, cy + hh),
                (cx - hw + 4, cy + hh),
                (cx - hw, cy + hh // 2),
            ]
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, self.accent, points, 2)
            # Core
            pygame.draw.circle(surface, self.accent, (cx, cy), 5)
            pygame.draw.circle(surface, (255, 200, 50), (cx, cy), 3)

        # HP bar for enemies with more than 1 hp
        if self.max_hp > 1:
            bar_w = self.w
            bar_h = 3
            pct = self.hp / self.max_hp
            pygame.draw.rect(surface, (80, 0, 0), (cx - bar_w // 2, cy - hh - 6, bar_w, bar_h))
            pygame.draw.rect(surface, UMAN_RED, (cx - bar_w // 2, cy - hh - 6, int(bar_w * pct), bar_h))


class Boss:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = -80
        self.w, self.h = BOSS_SIZE
        self.hp = BOSS_HP
        self.max_hp = BOSS_HP
        self.speed = BOSS_SPEED
        self.alive = True
        self.phase = 0  # 0=enter, 1=fight1, 2=fight2, 3=fight3
        self.timer = 0
        self.shoot_timer = 0
        self.dir = 1
        self.entered = False
        self.score = 2000
        self.flash = 0

    def update(self, player_x, player_y):
        self.timer += 1
        bullets = []

        if not self.entered:
            self.y += 1.5
            if self.y >= 80:
                self.y = 80
                self.entered = True
                self.phase = 1
            return bullets

        # Determine phase based on HP
        hp_pct = self.hp / self.max_hp
        if hp_pct > 0.66:
            self.phase = 1
        elif hp_pct > 0.33:
            self.phase = 2
        else:
            self.phase = 3

        # Movement
        move_speed = self.speed + (3 - self.phase) * 0.5
        self.x += self.dir * move_speed
        if self.x > WIDTH - 80:
            self.dir = -1
        elif self.x < 80:
            self.dir = 1

        # Slight vertical bobbing
        self.y = 80 + math.sin(self.timer * 0.02) * 15

        # Attacks based on phase
        self.shoot_timer -= 1
        if self.phase == 1 and self.shoot_timer <= 0:
            self.shoot_timer = 40
            bullets.append(EnemyBullet(self.x - 20, self.y + 30, -1, 3, toxic=True))
            bullets.append(EnemyBullet(self.x + 20, self.y + 30, 1, 3, toxic=True))
            bullets.append(EnemyBullet(self.x, self.y + 35, 0, 4, toxic=False))

        elif self.phase == 2 and self.shoot_timer <= 0:
            self.shoot_timer = 25
            for i in range(-2, 3):
                angle = math.pi / 2 + i * 0.3
                bullets.append(EnemyBullet(
                    self.x, self.y + 35,
                    math.cos(angle) * 3, math.sin(angle) * 3, toxic=True
                ))

        elif self.phase == 3 and self.shoot_timer <= 0:
            self.shoot_timer = 15
            angle = math.atan2(player_y - self.y, player_x - self.x)
            for offset in [-0.2, 0, 0.2]:
                a = angle + offset
                bullets.append(EnemyBullet(
                    self.x, self.y + 35,
                    math.cos(a) * 4.5, math.sin(a) * 4.5, toxic=True
                ))

        if self.flash > 0:
            self.flash -= 1

        return bullets

    def take_damage(self, amount=1):
        self.hp -= amount
        self.flash = 8
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        hw, hh = self.w // 2, self.h // 2

        # Main body
        body_color = (255, 150, 150) if self.flash > 0 else BOSS_COLOR
        # Large menacing shape
        points = [
            (cx - hw, cy - hh // 2),
            (cx - hw + 15, cy - hh),
            (cx + hw - 15, cy - hh),
            (cx + hw, cy - hh // 2),
            (cx + hw - 5, cy + hh),
            (cx + 15, cy + hh + 5),
            (cx - 15, cy + hh + 5),
            (cx - hw + 5, cy + hh),
        ]
        pygame.draw.polygon(surface, body_color, points)
        pygame.draw.polygon(surface, BOSS_ACCENT, points, 3)

        # Central eye
        eye_size = 12 + int(math.sin(self.timer * 0.1) * 3)
        pygame.draw.circle(surface, (30, 0, 0), (cx, cy), eye_size + 2)
        pygame.draw.circle(surface, BOSS_ACCENT, (cx, cy), eye_size)
        pygame.draw.circle(surface, (255, 255, 100), (cx, cy), eye_size // 2)

        # Side thrusters
        for sx in [-1, 1]:
            tx = cx + sx * (hw - 8)
            pygame.draw.rect(surface, UMAN_DARK, (tx - 5, cy + hh - 10, 10, 15))
            # Thruster glow
            glow = pygame.Surface((14, 10), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (200, 50, 255, 80), (0, 0, 14, 10))
            surface.blit(glow, (tx - 7, cy + hh + 3))

        # Phase indicator lines
        for i in range(self.phase):
            pygame.draw.line(surface, BOSS_ACCENT, (cx - 25 + i * 25, cy - hh + 5), (cx - 15 + i * 25, cy - hh + 5), 3)

        # HP bar
        bar_w = self.w + 20
        bar_h = 6
        bar_x = cx - bar_w // 2
        bar_y = cy - hh - 18
        pct = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (40, 0, 0), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        if pct > 0.66:
            bar_color = BOSS_ACCENT
        elif pct > 0.33:
            bar_color = SOLAR_ORANGE
        else:
            bar_color = (255, 50, 50)
        pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_w * pct), bar_h), border_radius=3)
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)
