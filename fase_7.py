import pygame
import sys
import math
import random

# ===================== INICIALIZAÇÃO =====================
pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fase 7 — ODS 7: Energia Limpa e Acessível")
clock = pygame.time.Clock()
FPS = 60

# ===================== CORES =====================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CAVE_BG = (18, 12, 22)
CAVE_WALL_1 = (40, 30, 35)
CAVE_WALL_2 = (55, 42, 48)
CAVE_ROCK = (70, 55, 60)

HOPE_BODY = (60, 180, 160)
HOPE_VISOR = (180, 240, 255)
HOPE_JETPACK = (80, 80, 100)

FLAME_ORANGE = (255, 160, 40)
FLAME_BLUE = (80, 160, 255)
FLAME_WHITE = (255, 240, 200)

SOLAR_ORB = (255, 220, 60)

BULLET_COLOR = (120, 255, 180)
BULLET_GLOW = (60, 200, 120)

DRONE_COLOR = (130, 130, 140)
ZIGZAG_COLOR = (140, 70, 180)
DIVER_COLOR = (200, 50, 50)
TANK_COLOR = (180, 160, 60)
TANK_BULLET = (220, 180, 40)

CRYSTAL_COLORS = [(100, 200, 255), (180, 100, 255), (100, 255, 180), (255, 180, 100)]


ENERGY_BAR_BG = (30, 30, 40)
ENERGY_BAR_FILL = (255, 210, 50)
ENERGY_BAR_LOW = (255, 80, 60)
HEART_COLOR = (255, 60, 80)

VICTORY_COLOR = (100, 255, 160)
DEFEAT_COLOR = (255, 60, 60)

# ===================== FONTES =====================
font_large = pygame.font.SysFont('arial', 70, True)
font_medium = pygame.font.SysFont('arial', 40, True)
font_small = pygame.font.SysFont('arial', 26)
font_tiny = pygame.font.SysFont('arial', 20)

class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, life=20, size=4, gravity=0.0, shrink=True):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity
        self.shrink = shrink

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        ratio = self.life / self.max_life
        sz = max(1, int(self.size * ratio)) if self.shrink else self.size
        r = min(255, int(self.color[0] * ratio + 30 * (1 - ratio)))
        g = min(255, int(self.color[1] * ratio))
        b = min(255, int(self.color[2] * ratio))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), sz)


class Hope:
    def __init__(self):
        self.width = 40
        self.height = 55
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 120
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 6
        self.lives = 3
        self.max_lives = 5
        self.hit_timer = 0

        self.energy = 100.0
        self.max_energy = 100.0
        self.energy_drain = 0.08
        self.jetpack_on = True

        self.shoot_cooldown = 0
        self.shoot_rate = 10

        self.anim_timer = 0
        self.flame_particles = []

    def update(self, keys):
        self.anim_timer += 1


        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed

        cave_margin = 80
        if self.x < cave_margin:
            self.x = cave_margin
        if self.x + self.width > WIDTH - cave_margin:
            self.x = WIDTH - cave_margin - self.width


        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed * 0.6
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed * 0.6


        if self.y < HEIGHT * 0.15:
            self.y = HEIGHT * 0.15

        if self.jetpack_on and self.y + self.height > HEIGHT - 30:
            self.y = HEIGHT - 30 - self.height

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)


        self.energy -= self.energy_drain
        if self.energy <= 0:
            self.energy = 0
            self.jetpack_on = False
            # Sem energia, Hope cai
            self.y += 4.0
        else:
            self.jetpack_on = True


        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


        if self.hit_timer > 0:
            self.hit_timer -= 1


        if self.jetpack_on:
            for _ in range(2):
                fx = self.x + self.width // 2 + random.uniform(-8, 8)
                fy = self.y + self.height + random.uniform(0, 5)
                color = random.choice([FLAME_ORANGE, FLAME_BLUE, FLAME_WHITE])
                p = Particle(fx, fy, color,
                             vx=random.uniform(-1.5, 1.5),
                             vy=random.uniform(2, 5),
                             life=random.randint(8, 16),
                             size=random.randint(3, 6),
                             gravity=0.1)
                self.flame_particles.append(p)
        else:

            if self.anim_timer % 4 == 0:
                fx = self.x + self.width // 2 + random.uniform(-5, 5)
                fy = self.y + self.height
                p = Particle(fx, fy, (80, 80, 80),
                             vx=random.uniform(-0.5, 0.5),
                             vy=random.uniform(1, 3),
                             life=10, size=3, gravity=0.05)
                self.flame_particles.append(p)


        for p in self.flame_particles:
            p.update()
        self.flame_particles = [p for p in self.flame_particles if p.life > 0]

    def shoot(self):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_rate
            bx = self.x + self.width // 2
            by = self.y - 5
            return Bullet(bx, by)
        return None

    def take_hit(self):
        if self.hit_timer > 0:
            return False
        self.lives -= 1
        self.hit_timer = 90
        return True

    def collect_energy(self, amount=30):
        self.energy = min(self.max_energy, self.energy + amount)

    def draw(self, surface):
        if self.hit_timer > 0 and (self.hit_timer // 5) % 2 == 0:
            return


        for p in self.flame_particles:
            p.draw(surface)

        x, y = int(self.x), int(self.y)

        pygame.draw.rect(surface, HOPE_BODY, (x + 5, y + 18, 30, 35), border_radius=4)
        pygame.draw.ellipse(surface, HOPE_BODY, (x + 6, y, 28, 24))
        pygame.draw.ellipse(surface, HOPE_VISOR, (x + 10, y + 4, 20, 14))
        pygame.draw.ellipse(surface, (220, 250, 255), (x + 13, y + 6, 6, 4))
        pygame.draw.rect(surface, HOPE_JETPACK, (x + 2, y + 22, 8, 20), border_radius=2)
        pygame.draw.rect(surface, HOPE_JETPACK, (x + 30, y + 22, 8, 20), border_radius=2)
        pygame.draw.rect(surface, HOPE_BODY, (x, y + 22, 7, 16), border_radius=3)
        pygame.draw.rect(surface, HOPE_BODY, (x + 33, y + 22, 7, 16), border_radius=3)
        pygame.draw.rect(surface, HOPE_BODY, (x + 10, y + 50, 9, 10), border_radius=2)
        pygame.draw.rect(surface, HOPE_BODY, (x + 22, y + 50, 9, 10), border_radius=2)
        if self.energy > 50:
            ga = int((self.energy / 100) * 40)
            gs = pygame.Surface((60, 75), pygame.SRCALPHA)
            pygame.draw.ellipse(gs, (255, 220, 60, ga), (0, 0, 60, 75))
            surface.blit(gs, (x - 10, y - 10))


class Bullet:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.speed = -12
        self.width = 6
        self.height = 18
        self.rect = pygame.Rect(int(x) - 3, int(y), self.width, self.height)
        self.alive = True
        self.trail = []

    def update(self):
        self.y += self.speed
        self.rect.y = int(self.y)
        self.rect.x = int(self.x) - 3
        if self.y < -20:
            self.alive = False

        self.trail.append((self.x, self.y + 10))
        if len(self.trail) > 6:
            self.trail.pop(0)

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = (i + 1) / len(self.trail)
            sz = max(1, int(3 * alpha))
            c = (int(BULLET_GLOW[0] * alpha), int(BULLET_GLOW[1] * alpha), int(BULLET_GLOW[2] * alpha))
            pygame.draw.circle(surface, c, (int(tx), int(ty)), sz)

        pygame.draw.rect(surface, BULLET_COLOR, (int(self.x) - 3, int(self.y), 6, 18), border_radius=3)
        g = pygame.Surface((16, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(g, (120, 255, 180, 60), (0, 0, 16, 28))
        surface.blit(g, (int(self.x) - 8, int(self.y) - 5))


class EnemyBullet:
    def __init__(self, x, y, speed=5):
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.rect = pygame.Rect(int(x) - 4, int(y), 8, 12)
        self.alive = True

    def update(self):
        self.y += self.speed
        self.rect.y = int(self.y)
        self.rect.x = int(self.x) - 4
        if self.y > HEIGHT + 20:
            self.alive = False

    def draw(self, surface):
        pygame.draw.rect(surface, TANK_BULLET, (int(self.x) - 4, int(self.y), 8, 12), border_radius=2)
        glow = pygame.Surface((18, 22), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (220, 180, 40, 50), (0, 0, 18, 22))
        surface.blit(glow, (int(self.x) - 9, int(self.y) - 5))


class SolarOrb:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(x) - 15, int(y) - 15, 30, 30)
        self.alive = True
        self.timer = random.uniform(0, math.pi * 2)
        self.speed = 1.5

    def update(self):
        self.y += self.speed
        self.timer += 0.08
        self.rect.x = int(self.x) - 15
        self.rect.y = int(self.y) - 15
        if self.y > HEIGHT + 30:
            self.alive = False

    def draw(self, surface):
        pulse = math.sin(self.timer) * 0.3 + 0.7
        glow_size = int(28 * pulse)
        glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 220, 60, int(50 * pulse)), (glow_size, glow_size), glow_size)
        surface.blit(glow, (int(self.x) - glow_size, int(self.y) - glow_size))

        pygame.draw.circle(surface, SOLAR_ORB, (int(self.x), int(self.y)), 12)
        pygame.draw.circle(surface, (255, 250, 200), (int(self.x) - 3, int(self.y) - 3), 5)


        for angle_offset in range(0, 360, 45):
            angle = math.radians(angle_offset + self.timer * 30)
            rx = int(self.x + math.cos(angle) * 18 * pulse)
            ry = int(self.y + math.sin(angle) * 18 * pulse)
            pygame.draw.line(surface, (255, 240, 100), (int(self.x), int(self.y)), (rx, ry), 1)


class UmanDrone:

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.width = 58
        self.height = 48
        self.rect = pygame.Rect(int(x), int(y), self.width, self.height)
        self.speed = 3.0
        self.hp = 1
        self.alive = True
        self.score = 1

    def update(self, hope):
        self.y += self.speed
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.y > HEIGHT + 40:
            self.alive = False
        return None

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        pygame.draw.rect(surface, DRONE_COLOR, (x, y + 10, 58, 28), border_radius=6)
        wing_off = math.sin(pygame.time.get_ticks() * 0.015) * 6
        pygame.draw.line(surface, (180, 180, 190), (x - 8, y + 16 + wing_off), (x + 12, y + 16), 4)
        pygame.draw.line(surface, (180, 180, 190), (x + 66, y + 16 + wing_off), (x + 46, y + 16), 4)
        pygame.draw.circle(surface, (255, 50, 50), (x + 29, y + 22), 6)

class UmanZigzag:

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.base_x = float(x)
        self.width = 54
        self.height = 54
        self.rect = pygame.Rect(int(x), int(y), self.width, self.height)
        self.speed = 2.5
        self.hp = 1
        self.alive = True
        self.timer = random.uniform(0, math.pi * 2)
        self.amplitude = 100
        self.score = 1

    def update(self, hope):
        self.timer += 0.04
        self.y += self.speed
        self.x = self.base_x + math.sin(self.timer) * self.amplitude
        if self.x < 85: self.x = 85
        if self.x + self.width > WIDTH - 85: self.x = WIDTH - 85 - self.width
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.y > HEIGHT + 40:
            self.alive = False
        return None

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        points = [(x + 27, y), (x, y + 54), (x + 54, y + 54)]
        pygame.draw.polygon(surface, ZIGZAG_COLOR, points)
        pygame.draw.polygon(surface, (180, 100, 220), points, 2)
        pygame.draw.circle(surface, (255, 200, 255), (x + 18, y + 28), 6)
        pygame.draw.circle(surface, (255, 200, 255), (x + 36, y + 28), 6)
        pygame.draw.circle(surface, (60, 0, 80), (x + 18, y + 28), 3)
        pygame.draw.circle(surface, (60, 0, 80), (x + 36, y + 28), 3)

class UmanDiver:

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.width = 60
        self.height = 60
        self.rect = pygame.Rect(int(x), int(y), self.width, self.height)
        self.speed = 2.0
        self.dive_speed = 6.0
        self.hp = 2
        self.alive = True
        self.phase = "approach"
        self.aim_timer = 0
        self.vx = 0
        self.vy = 0
        self.score = 2

    def update(self, hope):
        if self.phase == "approach":
            self.y += self.speed
            if self.y > HEIGHT * 0.25:
                self.phase = "aim"
                self.aim_timer = 40

        elif self.phase == "aim":
            self.aim_timer -= 1
            self.x += random.uniform(-2, 2)
            if self.aim_timer <= 0:
                self.phase = "dive"
                dx = (hope.x + hope.width / 2) - (self.x + self.width / 2)
                dy = (hope.y + hope.height / 2) - (self.y + self.height / 2)
                dist = max(1, math.sqrt(dx * dx + dy * dy))
                self.vx = (dx / dist) * self.dive_speed
                self.vy = (dy / dist) * self.dive_speed

        elif self.phase == "dive":
            self.x += self.vx
            self.y += self.vy

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.y > HEIGHT + 50 or self.x < -50 or self.x > WIDTH + 50:
            self.alive = False
        return None

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        # Corpo aerodinâmico
        pygame.draw.ellipse(surface, DIVER_COLOR, (x, y, 60, 60))
        pygame.draw.ellipse(surface, (240, 80, 80), (x + 3, y + 3, 54, 54), 2)
        # Olhos furiosos
        pygame.draw.rect(surface, (255, 200, 200), (x + 15, y + 20, 12, 7))
        pygame.draw.rect(surface, (255, 200, 200), (x + 35, y + 20, 12, 7))
        pygame.draw.rect(surface, (80, 0, 0), (x + 18, y + 21, 6, 5))
        pygame.draw.rect(surface, (80, 0, 0), (x + 38, y + 21, 6, 5))
        # Indicador de mira
        if self.phase == "aim":
            pygame.draw.circle(surface, (255, 255, 0, 100), (x + 30, y + 30), 36, 2)

class UmanTank:

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.width = 66
        self.height = 66
        self.rect = pygame.Rect(int(x), int(y), self.width, self.height)
        self.speed = 1.5
        self.hp = 3
        self.alive = True
        self.shoot_timer = 0
        self.shoot_rate = 80
        self.score = 2

    def update(self, hope):
        self.y += self.speed
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.y > HEIGHT + 50:
            self.alive = False

        # Atirar
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_rate:
            self.shoot_timer = 0
            return EnemyBullet(self.x + self.width // 2, self.y + self.height)
        return None

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        pygame.draw.rect(surface, TANK_COLOR, (x + 6, y, 54, 66), border_radius=8)
        pygame.draw.rect(surface, (200, 180, 80), (x + 6, y, 54, 66), 3, border_radius=8)
        pygame.draw.rect(surface, (160, 140, 40), (x + 14, y + 8, 38, 16), border_radius=3)
        pygame.draw.circle(surface, (255, 100, 100), (x + 33, y + 36), 9)
        pygame.draw.circle(surface, (255, 200, 200), (x + 33, y + 36), 5)
        pygame.draw.rect(surface, (120, 100, 30), (x + 28, y + 56, 12, 14))


class Stalactite:

    def __init__(self, x):
        self.x = float(x)
        self.y = -60.0
        self.width = 28
        self.height = 55
        self.rect = pygame.Rect(int(x), int(self.y), self.width, self.height)
        self.speed = 0.0
        self.falling = False
        self.warning_timer = 3  # quase instantâneo
        self.alive = True

    def update(self):
        if self.warning_timer > 0:
            self.warning_timer -= 1
            if self.warning_timer <= 0:
                self.falling = True
        
        if self.falling:
            self.speed += 0.5  # aceleração
            self.y += self.speed
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        if self.y > HEIGHT + 60:
            self.alive = False

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        pts = [(x + 14, y + 55), (x, y + 10), (x + 6, y), (x + 22, y), (x + 28, y + 10)]
        pygame.draw.polygon(surface, (90, 70, 65), pts)
        pygame.draw.polygon(surface, (120, 95, 85), pts, 2)
        pygame.draw.line(surface, (140, 120, 110), (x + 10, y + 5), (x + 14, y + 35), 2)

class FakeOrb:

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(x) - 15, int(y) - 15, 30, 30)
        self.alive = True
        self.timer = random.uniform(0, math.pi * 2)
        self.speed = 1.5
        self.exploded = False

    def update(self):
        if self.exploded:
            return
        self.y += self.speed
        self.timer += 0.08
        self.rect.x = int(self.x) - 15
        self.rect.y = int(self.y) - 15
        if self.y > HEIGHT + 30:
            self.alive = False

    def draw(self, surface):
        if self.exploded:
            return
        # Parece QUASE igual a uma orbe solar, mas com leve diferença
        pulse = math.sin(self.timer) * 0.3 + 0.7
        glow_size = int(28 * pulse)
        glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 200, 60, int(50 * pulse)), (glow_size, glow_size), glow_size)
        surface.blit(glow, (int(self.x) - glow_size, int(self.y) - glow_size))

        # Orbe — cor levemente diferente (mais esverdeada, quase imperceptível)
        pygame.draw.circle(surface, (240, 220, 50), (int(self.x), int(self.y)), 12)
        pygame.draw.circle(surface, (255, 250, 180), (int(self.x) - 3, int(self.y) - 3), 5)

        # Raios (igual)
        for angle_offset in range(0, 360, 45):
            angle = math.radians(angle_offset + self.timer * 30)
            rx = int(self.x + math.cos(angle) * 18 * pulse)
            ry = int(self.y + math.sin(angle) * 18 * pulse)
            pygame.draw.line(surface, (255, 230, 90), (int(self.x), int(self.y)), (rx, ry), 1)


class GlitchText:
    """Texto de alerta do Glitch que aparece na tela"""
    def __init__(self, text, duration=90):
        self.text = text
        self.duration = duration
        self.max_duration = duration
        self.alive = True

    def update(self):
        self.duration -= 1
        if self.duration <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        ratio = self.duration / self.max_duration
        # Aparece com efeito glitch
        alpha = int(200 * ratio)
        
        # Renderizar com offset aleatório para efeito glitch
        ox = random.randint(-3, 3) if ratio > 0.3 else 0
        oy = random.randint(-2, 2) if ratio > 0.3 else 0
        
        text_surf = font_medium.render(self.text, True, (255, 50, 50))
        # Sombra/duplicata glitch
        shadow = font_medium.render(self.text, True, (0, 255, 255))
        
        cx = WIDTH // 2 - text_surf.get_width() // 2
        cy = HEIGHT // 2 - 50
        
        surface.blit(shadow, (cx + random.randint(-5, 5), cy + random.randint(-3, 3)))
        surface.blit(text_surf, (cx + ox, cy + oy))

class TrapSystem:

    def __init__(self):
        # Armadilhas programadas por altitude (em metros)
        # Cada trap é ativada UMA vez
        self.traps_triggered = set()
        self.active_stalactites = []
        self.active_fake_orbs = []
        self.glitch_texts = []
        
        # Estado de squeeze (paredes fechando)
        self.squeeze_active = False
        self.squeeze_timer = 0
        self.squeeze_amount = 0.0  # 0 = normal, 1 = máximo
        self.squeeze_target = 0.0
        
        # Inversão de controles
        self.invert_controls = False
        self.invert_timer = 0
        
        # Apagão
        self.blackout_active = False
        self.blackout_timer = 0
        self.blackout_alpha = 0

    def check_traps(self, altitude_m, hope, particles, shake):
        
        # ====== 40m — Primeira stalactite (susto do nada!) ======
        if altitude_m >= 40 and 'stalk_60' not in self.traps_triggered:
            self.traps_triggered.add('stalk_60')
            # Cai exatamente onde Hope está — sem aviso nenhum
            self.active_stalactites.append(Stalactite(hope.x + hope.width // 2 - 14))

        # ====== 75m — Fake orb (parece boa mas...) ======
        if altitude_m >= 75 and 'fake_120' not in self.traps_triggered:
            self.traps_triggered.add('fake_120')
            self.active_fake_orbs.append(FakeOrb(WIDTH // 2, -20))

        # ====== 110m — 3 stalactites rápidas ======
        if altitude_m >= 110 and 'stalk_180' not in self.traps_triggered:
            self.traps_triggered.add('stalk_180')
            for i in range(3):
                s = Stalactite(random.randint(100, WIDTH - 130))
                s.warning_timer = 3 + i * 8  # quase instantâneas, em sequência rápida
                self.active_stalactites.append(s)

        # ====== 140m — Paredes fechando sem aviso! ======
        if altitude_m >= 140 and 'squeeze_220' not in self.traps_triggered:
            self.traps_triggered.add('squeeze_220')
            self.squeeze_active = True
            self.squeeze_timer = 200
            self.squeeze_target = 0.5

        # ====== 175m — Inversão de controles (sem aviso!) ======
        if altitude_m >= 175 and 'invert_280' not in self.traps_triggered:
            self.traps_triggered.add('invert_280')
            self.invert_controls = True
            self.invert_timer = 180
            shake.trigger(8, 3)

        # ====== 210m — Chuva de stalactites ======
        if altitude_m >= 210 and 'stalk_330' not in self.traps_triggered:
            self.traps_triggered.add('stalk_330')
            for i in range(4):
                s = Stalactite(120 + i * 170)
                s.warning_timer = 2 + i * 6
                self.active_stalactites.append(s)

        # ====== 235m — Fake orb + apagão surpresa ======
        if altitude_m >= 235 and 'blackout_370' not in self.traps_triggered:
            self.traps_triggered.add('blackout_370')
            self.blackout_active = True
            self.blackout_timer = 120
            self.active_fake_orbs.append(FakeOrb(hope.x + 60, -20))

        # ====== 260m — Squeeze + stalactites combo ======
        if altitude_m >= 260 and 'combo_410' not in self.traps_triggered:
            self.traps_triggered.add('combo_410')
            self.squeeze_active = True
            self.squeeze_timer = 150
            self.squeeze_target = 0.4
            for i in range(2):
                s = Stalactite(250 + i * 250)
                s.warning_timer = 3 + i * 10
                self.active_stalactites.append(s)

        # ====== 280m — Inversão + stalactites finais ======
        if altitude_m >= 280 and 'final_460' not in self.traps_triggered:
            self.traps_triggered.add('final_460')
            self.invert_controls = True
            self.invert_timer = 150
            for i in range(3):
                s = Stalactite(hope.x + random.randint(-80, 80))
                s.warning_timer = 3 + i * 8
                self.active_stalactites.append(s)
            shake.trigger(10, 4)

    def update(self, hope, particles, shake):
        
        # Stalactites
        for s in self.active_stalactites:
            s.update()
            # Colisão com Hope
            if s.falling and s.alive and hope.hit_timer <= 0 and s.rect.colliderect(hope.rect):
                if hope.take_hit():
                    shake.trigger(15, 8)
                    s.alive = False
                    for _ in range(12):
                        particles.append(Particle(
                            s.x + s.width // 2, s.y + s.height // 2,
                            (120, 100, 80),
                            vx=random.uniform(-5, 5),
                            vy=random.uniform(-3, 5),
                            life=20, size=5, gravity=0.2
                        ))
        self.active_stalactites = [s for s in self.active_stalactites if s.alive]

        # Fake orbs
        for fo in self.active_fake_orbs:
            fo.update()
            if not fo.exploded and fo.alive and fo.rect.colliderect(hope.rect):
                fo.exploded = True
                fo.alive = False
                # DRENA energia em vez de dar!
                hope.energy = max(0, hope.energy - 35)
                shake.trigger(20, 8)
                self.glitch_texts.append(GlitchText("HAHA! FALSA!", 50))
                # Explosão vermelha
                for _ in range(20):
                    particles.append(Particle(
                        fo.x, fo.y,
                        random.choice([(255, 50, 50), (255, 100, 0), (200, 0, 0)]),
                        vx=random.uniform(-7, 7),
                        vy=random.uniform(-7, 7),
                        life=25, size=6, gravity=0.1
                    ))
        self.active_fake_orbs = [fo for fo in self.active_fake_orbs if fo.alive]

        # Squeeze (paredes fechando)
        if self.squeeze_active:
            self.squeeze_timer -= 1
            if self.squeeze_timer > 60:
                # Fechando
                self.squeeze_amount += (self.squeeze_target - self.squeeze_amount) * 0.05
            else:
                # Abrindo de volta
                self.squeeze_amount *= 0.95
            
            if self.squeeze_timer <= 0:
                self.squeeze_active = False
                self.squeeze_amount = 0.0

        # Inversão de controles
        if self.invert_controls:
            self.invert_timer -= 1
            if self.invert_timer <= 0:
                self.invert_controls = False

        # Apagão
        if self.blackout_active:
            self.blackout_timer -= 1
            if self.blackout_timer > 120:
                self.blackout_alpha = min(200, self.blackout_alpha + 8)
            elif self.blackout_timer < 30:
                self.blackout_alpha = max(0, self.blackout_alpha - 8)
            if self.blackout_timer <= 0:
                self.blackout_active = False
                self.blackout_alpha = 0

        # Glitch texts
        for gt in self.glitch_texts:
            gt.update()
        self.glitch_texts = [gt for gt in self.glitch_texts if gt.alive]

    def get_squeeze_margin(self):
        return int(self.squeeze_amount * 120)

    def draw(self, surface):
        # Stalactites
        for s in self.active_stalactites:
            s.draw(surface)

        # Fake orbs
        for fo in self.active_fake_orbs:
            fo.draw(surface)

        # Squeeze — paredes extras
        if self.squeeze_amount > 0.01:
            extra = self.get_squeeze_margin()
            # Parede esquerda extra
            squeeze_surf = pygame.Surface((extra, HEIGHT), pygame.SRCALPHA)
            squeeze_surf.fill((60, 45, 50, 200))
            surface.blit(squeeze_surf, (80, 0))
            # Parede direita extra
            surface.blit(squeeze_surf, (WIDTH - 80 - extra, 0))
            # Bordas com espinhos/rochas
            for i in range(0, HEIGHT, 40):
                pygame.draw.circle(surface, (80, 60, 55), (80 + extra, i + 20), 6)
                pygame.draw.circle(surface, (80, 60, 55), (WIDTH - 80 - extra, i + 20), 6)

        # Apagão
        if self.blackout_alpha > 0:
            dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, self.blackout_alpha))
            surface.blit(dark, (0, 0))

        # Glitch texts
        for gt in self.glitch_texts:
            gt.draw(surface)

        # Indicador de controle invertido
        if self.invert_controls:
            blink = (pygame.time.get_ticks() // 200) % 2 == 0
            if blink:
                inv_text = font_tiny.render("⚠ CONTROLES INVERTIDOS ⚠", True, (255, 80, 80))
                surface.blit(inv_text, (WIDTH // 2 - inv_text.get_width() // 2, HEIGHT - 40))


class Crystal:
    def __init__(self, x, y, side):
        self.x = x
        self.y = y
        self.side = side
        self.color = random.choice(CRYSTAL_COLORS)
        self.size = random.randint(8, 18)
        self.glow_timer = random.uniform(0, math.pi * 2)

    def draw(self, surface, screen_y):
        sy = int(screen_y)
        if sy < -30 or sy > HEIGHT + 30:
            return
        self.glow_timer += 0.03
        pulse = math.sin(self.glow_timer) * 0.3 + 0.7

        # Glow
        glow_size = int(self.size * 1.8 * pulse)
        glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, int(35 * pulse)), (glow_size, glow_size), glow_size)
        surface.blit(glow, (self.x - glow_size, sy - glow_size))

        # Cristal (losango)
        cx, cy = self.x, sy
        s = self.size
        points = [(cx, cy - s), (cx + s // 2, cy), (cx, cy + s // 2), (cx - s // 2, cy)]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, WHITE, points, 1)


class CaveBackground:
    def __init__(self):
        self.crystals = []
        self.speed_lines = []
        # Gerar cristais ao longo de toda a caverna (500m = 7500px internos)
        total_height = 8000
        for i in range(120):
            y = random.randint(0, total_height)
            side = random.choice(['left', 'right'])
            if side == 'left':
                x = random.randint(10, 70)
            else:
                x = random.randint(WIDTH - 70, WIDTH - 10)
            self.crystals.append(Crystal(x, y, side))

    def draw(self, surface, altitude_pixels, progress_ratio):
        # Cor de fundo escurece/clareia conforme sobe
        # Mais escuro embaixo, mais claro perto do topo
        r = int(18 + progress_ratio * 25)
        g = int(12 + progress_ratio * 20)
        b = int(22 + progress_ratio * 35)
        surface.fill((r, g, b))

        # Paredes da caverna — camada traseira (parallax lento)
        wall_offset_1 = altitude_pixels * 0.2
        for i in range(-1, HEIGHT // 60 + 2):
            y = i * 60 + (wall_offset_1 % 60)
            # Esquerda
            w = 65 + int(math.sin(y * 0.02 + 1) * 20)
            pygame.draw.rect(surface, CAVE_WALL_1, (0, y, w, 62))
            # Direita
            w2 = 65 + int(math.sin(y * 0.025 + 3) * 20)
            pygame.draw.rect(surface, CAVE_WALL_1, (WIDTH - w2, y, w2, 62))

        # Paredes — camada frontal (parallax rápido)
        wall_offset_2 = altitude_pixels * 0.5
        for i in range(-1, HEIGHT // 50 + 2):
            y = i * 50 + (wall_offset_2 % 50)
            # Esquerda
            w = 50 + int(math.sin(y * 0.03 + 2) * 18)
            pygame.draw.rect(surface, CAVE_WALL_2, (0, y, w, 52))
            # Rochas decorativas
            if i % 3 == 0:
                pygame.draw.circle(surface, CAVE_ROCK, (w - 5, int(y + 25)), 8)
            # Direita
            w2 = 50 + int(math.sin(y * 0.028 + 5) * 18)
            pygame.draw.rect(surface, CAVE_WALL_2, (WIDTH - w2, y, w2, 52))
            if i % 3 == 1:
                pygame.draw.circle(surface, CAVE_ROCK, (WIDTH - w2 + 5, int(y + 25)), 8)

        # Cristais
        for crystal in self.crystals:
            screen_y = crystal.y - altitude_pixels * 0.4
            # Loop para visibilidade contínua
            screen_y_mod = screen_y % 2000 - 200
            crystal.draw(surface, screen_y_mod)

        # Linhas de velocidade (estrias)
        if len(self.speed_lines) < 8:
            self.speed_lines.append({
                'x': random.randint(90, WIDTH - 90),
                'y': random.randint(-50, -10),
                'speed': random.uniform(8, 16),
                'length': random.randint(20, 60),
                'alpha': random.randint(30, 80)
            })

        for line in self.speed_lines:
            line['y'] += line['speed']
            a = min(255, line['alpha'])
            pygame.draw.line(surface, (200, 200, 220), 
                             (line['x'], int(line['y'])),
                             (line['x'], int(line['y'] + line['length'])), 1)

        self.speed_lines = [l for l in self.speed_lines if l['y'] < HEIGHT + 70]

        # Luz do topo nos últimos 30m (progress > 0.9)
        if progress_ratio > 0.9:
            light_intensity = (progress_ratio - 0.9) / 0.1  # 0 a 1
            light_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            # Gradiente de luz vindo de cima
            for ly in range(min(300, int(300 * light_intensity))):
                alpha = int((1 - ly / 300) * 60 * light_intensity)
                pygame.draw.rect(light_surf, (255, 250, 200, alpha), (0, ly, WIDTH, 2))
            surface.blit(light_surf, (0, 0))


class ScreenShake:
    def __init__(self):
        self.duration = 0
        self.intensity = 0
        self.offset_x = 0
        self.offset_y = 0

    def trigger(self, duration=10, intensity=5):
        self.duration = duration
        self.intensity = intensity

    def update(self):
        if self.duration > 0:
            self.duration -= 1
            self.offset_x = random.randint(-self.intensity, self.intensity)
            self.offset_y = random.randint(-self.intensity, self.intensity)
        else:
            self.offset_x = 0
            self.offset_y = 0


class WaveSpawner:
    def __init__(self):
        self.timer = 0
        self.wave_num = 0
        self.cave_margin = 80

    def get_random_x(self):
        return random.randint(self.cave_margin + 10, WIDTH - self.cave_margin - 50)

    def update(self, altitude_m, enemies):
        self.timer += 1

        # Spawn baseado na altitude (progressão) — menos inimigos, maiores
        if altitude_m < 80:
            # Setor 1: Só drones, spawn lento
            if self.timer % 90 == 0:
                enemies.append(UmanDrone(self.get_random_x(), -50))
            if self.timer % 200 == 0:
                # Spawn de par
                x1 = self.get_random_x()
                enemies.append(UmanDrone(x1, -50))
                enemies.append(UmanDrone(x1 + 100, -80))

        elif altitude_m < 160:
            # Setor 2: Drones + Zigzags
            if self.timer % 75 == 0:
                enemies.append(UmanDrone(self.get_random_x(), -50))
            if self.timer % 120 == 0:
                enemies.append(UmanZigzag(self.get_random_x(), -55))
            if self.timer % 250 == 0:
                # Wave de 2 drones
                base_x = self.get_random_x()
                for i in range(2):
                    enemies.append(UmanDrone(base_x + i * 80, -50 - i * 40))

        elif altitude_m < 240:
            # Setor 3: + Mergulhadores
            if self.timer % 65 == 0:
                enemies.append(UmanDrone(self.get_random_x(), -50))
            if self.timer % 100 == 0:
                enemies.append(UmanZigzag(self.get_random_x(), -55))
            if self.timer % 150 == 0:
                enemies.append(UmanDiver(self.get_random_x(), -65))
            if self.timer % 220 == 0:
                # Wave mista
                enemies.append(UmanDrone(self.get_random_x(), -50))
                enemies.append(UmanZigzag(self.get_random_x(), -80))

        else:
            # Setor 4: TUDO + Blindados
            if self.timer % 55 == 0:
                enemies.append(UmanDrone(self.get_random_x(), -50))
            if self.timer % 90 == 0:
                enemies.append(UmanZigzag(self.get_random_x(), -55))
            if self.timer % 120 == 0:
                enemies.append(UmanDiver(self.get_random_x(), -65))
            if self.timer % 170 == 0:
                enemies.append(UmanTank(self.get_random_x(), -70))


def draw_hud(surface, hope, altitude_m, score=0):
    # Fundo semi-transparente do HUD
    hud_surf = pygame.Surface((WIDTH, 45), pygame.SRCALPHA)
    hud_surf.fill((0, 0, 0, 120))
    surface.blit(hud_surf, (0, 0))

    # Barra de energia solar
    bar_x, bar_y = 15, 12
    bar_w, bar_h = 150, 20

    pygame.draw.rect(surface, ENERGY_BAR_BG, (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), border_radius=4)
    fill_ratio = hope.energy / hope.max_energy
    fill_color = ENERGY_BAR_FILL if fill_ratio > 0.25 else ENERGY_BAR_LOW
    pygame.draw.rect(surface, fill_color, (bar_x, bar_y, int(bar_w * fill_ratio), bar_h), border_radius=3)

    # Ícone de sol
    pygame.draw.circle(surface, SOLAR_ORB, (bar_x + bar_w + 18, bar_y + 10), 8)
    energy_text = font_tiny.render(f"{int(hope.energy)}%", True, WHITE)
    surface.blit(energy_text, (bar_x + bar_w + 32, bar_y))

    # Pontuação
    score_text = font_small.render(f"PTS: {score}", True, (255, 220, 80))
    surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

    # Vidas (corações)
    for i in range(hope.lives):
        hx = WIDTH - 45 - i * 35
        hy = 12
        pygame.draw.circle(surface, HEART_COLOR, (hx, hy + 5), 7)
        pygame.draw.circle(surface, HEART_COLOR, (hx + 10, hy + 5), 7)
        pygame.draw.polygon(surface, HEART_COLOR, [(hx - 6, hy + 8), (hx + 5, hy + 20), (hx + 16, hy + 8)])


# ===================== CUTSCENE FINAL (VITÓRIA) =====================
class EndCutscene:
    """Hope sai da caverna e vê a superfície destruída"""
    def __init__(self, final_score):
        self.timer = 0
        self.done = False
        self.final_score = final_score
        self.particles = []
        self.fade_alpha = 0
        self.shake_x = 0
        self.shake_y = 0

        # Fases (frames):
        # 0: Tela branca (flash de luz do sol) — "Hope alcançou a superfície"  (0-120)
        # 1: Hope subindo pela abertura da caverna, céu aparecendo              (120-300)
        # 2: Hope pousa na superfície, vilarejo destruído ao fundo              (300-520)
        # 3: Textos finais + pontuação                                          (520-720)
        # 4: "Continua..." + Fade                                               (720-860)

        self.hope_x = WIDTH // 2 - 20.0
        self.hope_y = HEIGHT + 60.0  # começa fora da tela por baixo
        self.hope_landed = False

        self.ground_y = 450

        # Nuvens
        self.clouds = []
        for _ in range(6):
            self.clouds.append({
                'x': random.randint(-50, WIDTH + 50),
                'y': random.randint(30, 180),
                'w': random.randint(80, 180),
                'h': random.randint(25, 45),
                'speed': random.uniform(0.2, 0.6),
            })

        # Ruínas do vilarejo
        self.ruins = []
        for i in range(10):
            self.ruins.append({
                'x': 40 + i * 90,
                'h': random.randint(30, 100),
                'w': random.randint(25, 55),
                'broken': random.randint(5, 20),
                'has_window': random.random() > 0.3,
            })

        # Árvores mortas
        self.trees = []
        for i in range(5):
            self.trees.append({
                'x': random.randint(80, WIDTH - 80),
                'h': random.randint(40, 80),
            })

        self.sun_glow = 0.0

        self.texts = [
            {"text": "Hope alcançou a superfície.", "start": 10, "end": 110, "y": HEIGHT // 2 - 20, "color": (255, 255, 240), "font": "medium"},
            {"text": "Pela primeira vez em anos... o céu.", "start": 180, "end": 290, "y": 60, "color": (180, 210, 255), "font": "small"},
            {"text": "Mas o que os Umans fizeram...", "start": 320, "end": 450, "y": 60, "color": (200, 150, 130), "font": "small"},
            {"text": "O vilarejo estava em ruínas.", "start": 380, "end": 510, "y": 95, "color": (180, 130, 110), "font": "small"},
            {"text": "HOPE ESCAPOU!", "start": 530, "end": 700, "y": HEIGHT // 2 - 100, "color": VICTORY_COLOR, "font": "large"},
            {"text": f"Pontuação: {final_score}", "start": 560, "end": 700, "y": HEIGHT // 2 - 30, "color": (255, 220, 80), "font": "medium"},
            {"text": "A energia solar iluminou o caminho.", "start": 590, "end": 700, "y": HEIGHT // 2 + 30, "color": (200, 255, 220), "font": "small"},
            {"text": "ODS 7 — Energia Limpa e Acessível", "start": 610, "end": 700, "y": HEIGHT // 2 + 70, "color": SOLAR_ORB, "font": "small"},
            {"text": "Mas a luta não acabou...", "start": 730, "end": 840, "y": HEIGHT // 2 - 20, "color": (200, 180, 160), "font": "medium"},
            {"text": "Continua...", "start": 770, "end": 850, "y": HEIGHT // 2 + 30, "color": (160, 160, 180), "font": "small"},
        ]

    def get_phase(self):
        if self.timer < 120: return 0
        if self.timer < 300: return 1
        if self.timer < 520: return 2
        if self.timer < 720: return 3
        return 4

    def update(self):
        self.timer += 1
        phase = self.get_phase()

        # Fase 0: Flash branco diminuindo
        if phase == 0:
            self.sun_glow = max(0, 1.0 - self.timer / 120.0)

        # Fase 1: Hope subindo de baixo
        elif phase == 1:
            if self.hope_y > 250:
                self.hope_y -= 3.0
            # Partículas de jetpack
            if self.timer % 2 == 0:
                for _ in range(2):
                    self.particles.append(Particle(
                        self.hope_x + 20 + random.uniform(-6, 6),
                        self.hope_y + 55,
                        random.choice([FLAME_ORANGE, FLAME_BLUE, FLAME_WHITE]),
                        vx=random.uniform(-1.5, 1.5),
                        vy=random.uniform(3, 6),
                        life=random.randint(10, 18),
                        size=random.randint(3, 5),
                        gravity=0.1
                    ))

        # Fase 2: Hope aterrissa
        elif phase == 2:
            if not self.hope_landed:
                if self.hope_y < self.ground_y - 60:
                    self.hope_y += 1.0
                    # Jetpack diminuindo
                    if self.timer % 3 == 0:
                        self.particles.append(Particle(
                            self.hope_x + 20, self.hope_y + 55,
                            random.choice([FLAME_ORANGE, (80, 80, 80)]),
                            vx=random.uniform(-1, 1),
                            vy=random.uniform(1, 3),
                            life=10, size=3, gravity=0.1
                        ))
                else:
                    self.hope_landed = True
                    # Poeira ao pousar
                    for _ in range(15):
                        self.particles.append(Particle(
                            self.hope_x + 20, self.ground_y - 5,
                            (140, 120, 100),
                            vx=random.uniform(-4, 4),
                            vy=random.uniform(-2, 0),
                            life=random.randint(15, 30),
                            size=random.randint(2, 5),
                            gravity=0.1
                        ))
                    self.shake_x = random.randint(-3, 3)
                    self.shake_y = random.randint(-2, 2)

            if self.shake_x != 0 or self.shake_y != 0:
                self.shake_x = int(self.shake_x * 0.85)
                self.shake_y = int(self.shake_y * 0.85)

        # Fase 4: Fade
        elif phase == 4:
            self.fade_alpha = min(255, self.fade_alpha + 3)
            if self.timer > 860:
                self.done = True

        # Nuvens em movimento
        for cloud in self.clouds:
            cloud['x'] += cloud['speed']
            if cloud['x'] > WIDTH + 100:
                cloud['x'] = -cloud['w'] - 20

        # Partículas
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw_sky(self, render):
        """Céu degradê — amanhecer"""
        for y in range(self.ground_y):
            ratio = y / self.ground_y
            r = int(40 + 130 * (1 - ratio))  # azul escuro → laranja
            g = int(60 + 120 * (1 - ratio))
            b = int(140 + 60 * ratio)
            pygame.draw.line(render, (min(255, r), min(255, g), min(255, b)), (0, y), (WIDTH, y))

        # Sol nascendo
        sun_x, sun_y = WIDTH - 160, 100
        # Raios
        for i in range(12):
            angle = math.radians(i * 30 + self.timer * 0.3)
            rx = sun_x + int(math.cos(angle) * 80)
            ry = sun_y + int(math.sin(angle) * 80)
            pygame.draw.line(render, (255, 240, 180), (sun_x, sun_y), (rx, ry), 2)
        # Glow
        glow = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 220, 100, 30), (100, 100), 100)
        pygame.draw.circle(glow, (255, 230, 120, 50), (100, 100), 60)
        render.blit(glow, (sun_x - 100, sun_y - 100))
        # Sol
        pygame.draw.circle(render, (255, 240, 180), (sun_x, sun_y), 30)
        pygame.draw.circle(render, (255, 250, 220), (sun_x - 5, sun_y - 5), 15)

    def draw_clouds(self, render):
        for cloud in self.clouds:
            # Nuvem com múltiplos círculos
            cx, cy = int(cloud['x']), int(cloud['y'])
            cw, ch = cloud['w'], cloud['h']
            for i in range(4):
                ox = cx + i * (cw // 4)
                oy = cy + random.randint(-3, 3)
                sz = ch // 2 + random.randint(-5, 5)
                pygame.draw.circle(render, (220, 225, 235), (ox, oy), max(8, sz))
            # Base da nuvem
            pygame.draw.ellipse(render, (210, 215, 225), (cx - 10, cy - 5, cw, ch))

    def draw_village(self, render):
        """Vilarejo destruído"""
        # Chão (terra desolada)
        pygame.draw.rect(render, (80, 65, 50), (0, self.ground_y, WIDTH, HEIGHT - self.ground_y))
        # Grama seca
        for i in range(0, WIDTH, 8):
            gh = random.randint(3, 10)
            pygame.draw.line(render, (100, 85, 50), (i, self.ground_y), (i + random.randint(-3, 3), self.ground_y - gh), 1)

        # Ruínas
        for ruin in self.ruins:
            rx = ruin['x']
            rh = ruin['h']
            rw = ruin['w']
            by = self.ground_y - rh
            bt = ruin['broken']

            # Prédio/casa destruída
            pygame.draw.rect(render, (70, 60, 55), (rx, by, rw, rh))
            # Topo quebrado
            pygame.draw.polygon(render, (80, 65, 50), [
                (rx, by), (rx + bt, by - 10),
                (rx + rw - bt, by - 6), (rx + rw, by)
            ])
            # Janelas quebradas
            if ruin['has_window'] and rh > 40:
                wy = by + 15
                pygame.draw.rect(render, (30, 25, 25), (rx + 6, wy, 12, 14))
                # Vidro quebrado (X)
                pygame.draw.line(render, (90, 80, 70), (rx + 6, wy), (rx + 18, wy + 14), 1)
                pygame.draw.line(render, (90, 80, 70), (rx + 18, wy), (rx + 6, wy + 14), 1)
            # Rachaduras
            pygame.draw.line(render, (55, 45, 40), (rx + rw // 2, by + 5),
                             (rx + rw // 2 + 8, by + rh - 5), 1)

        # Árvores mortas
        for tree in self.trees:
            tx = tree['x']
            th = tree['h']
            ty = self.ground_y
            # Tronco
            pygame.draw.line(render, (60, 45, 35), (tx, ty), (tx, ty - th), 3)
            # Galhos secos
            pygame.draw.line(render, (60, 45, 35), (tx, ty - th + 10), (tx - 15, ty - th - 10), 2)
            pygame.draw.line(render, (60, 45, 35), (tx, ty - th + 15), (tx + 18, ty - th - 5), 2)
            pygame.draw.line(render, (60, 45, 35), (tx, ty - th + 25), (tx - 10, ty - th + 10), 2)

        # Fumaça saindo de uma ruína
        if self.timer % 6 == 0:
            smoke_x = self.ruins[2]['x'] + self.ruins[2]['w'] // 2
            smoke_y = self.ground_y - self.ruins[2]['h'] - 5
            self.particles.append(Particle(
                smoke_x, smoke_y, (100, 100, 110),
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(-1.5, -0.5),
                life=random.randint(40, 70),
                size=random.randint(3, 6),
                shrink=False
            ))

    def draw_cave_opening(self, render):
        """Abertura da caverna no chão"""
        cx = WIDTH // 2
        cy = self.ground_y
        # Buraco
        pygame.draw.ellipse(render, (15, 10, 18), (cx - 50, cy - 15, 100, 35))
        # Borda rochosa
        pygame.draw.ellipse(render, (90, 75, 65), (cx - 50, cy - 15, 100, 35), 3)
        # Escuridão interior
        pygame.draw.ellipse(render, (5, 2, 8), (cx - 40, cy - 10, 80, 25))

    def draw_hope(self, render, hx, hy):
        """Hope na cutscene final"""
        pygame.draw.rect(render, HOPE_BODY, (hx + 5, hy + 18, 30, 35), border_radius=4)
        pygame.draw.ellipse(render, HOPE_BODY, (hx + 6, hy, 28, 24))
        pygame.draw.ellipse(render, HOPE_VISOR, (hx + 10, hy + 4, 20, 14))
        pygame.draw.ellipse(render, (220, 250, 255), (hx + 13, hy + 6, 6, 4))
        pygame.draw.rect(render, HOPE_JETPACK, (hx + 2, hy + 22, 8, 20), border_radius=2)
        pygame.draw.rect(render, HOPE_JETPACK, (hx + 30, hy + 22, 8, 20), border_radius=2)
        pygame.draw.rect(render, HOPE_BODY, (hx, hy + 22, 7, 16), border_radius=3)
        pygame.draw.rect(render, HOPE_BODY, (hx + 33, hy + 22, 7, 16), border_radius=3)
        pygame.draw.rect(render, HOPE_BODY, (hx + 10, hy + 50, 9, 10), border_radius=2)
        pygame.draw.rect(render, HOPE_BODY, (hx + 22, hy + 50, 9, 10), border_radius=2)

    def draw(self, surface):
        phase = self.get_phase()
        render = pygame.Surface((WIDTH, HEIGHT))

        if phase == 0:
            # Flash branco diminuindo → céu aparece
            self.draw_sky(render)
            self.draw_clouds(render)
            self.draw_village(render)
            self.draw_cave_opening(render)

            # White flash overlay
            flash = pygame.Surface((WIDTH, HEIGHT))
            flash.fill((255, 255, 240))
            flash.set_alpha(int(self.sun_glow * 255))
            render.blit(flash, (0, 0))

        elif phase >= 1:
            self.draw_sky(render)
            self.draw_clouds(render)
            self.draw_village(render)

            # Partículas
            for p in self.particles:
                p.draw(render)

            # Abertura da caverna
            self.draw_cave_opening(render)

            # Hope
            self.draw_hope(render, int(self.hope_x), int(self.hope_y))

            # Jetpack chama (se ainda voando)
            if not self.hope_landed:
                for _ in range(3):
                    fx = int(self.hope_x) + 20 + random.randint(-6, 6)
                    fy = int(self.hope_y) + 58 + random.randint(0, 8)
                    color = random.choice([FLAME_ORANGE, FLAME_BLUE])
                    pygame.draw.circle(render, color, (fx, fy), random.randint(2, 5))

        # Textos
        for txt in self.texts:
            if txt['start'] <= self.timer <= txt['end']:
                fade_in = 25
                fade_out = 20
                elapsed = self.timer - txt['start']
                remaining = txt['end'] - self.timer
                if elapsed < fade_in:
                    alpha = int((elapsed / fade_in) * 255)
                elif remaining < fade_out:
                    alpha = int((remaining / fade_out) * 255)
                else:
                    alpha = 255
                alpha = max(0, min(255, alpha))
                base = txt['color']
                r = min(255, int(base[0] * alpha / 255))
                g = min(255, int(base[1] * alpha / 255))
                b = min(255, int(base[2] * alpha / 255))
                if txt['font'] == 'large':
                    f = font_large
                elif txt['font'] == 'medium':
                    f = font_medium
                else:
                    f = font_small
                text_surf = f.render(txt['text'], True, (r, g, b))
                render.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, txt['y']))

        # Barras cinemáticas
        bar_h = 50
        pygame.draw.rect(render, BLACK, (0, 0, WIDTH, bar_h))
        pygame.draw.rect(render, BLACK, (0, HEIGHT - bar_h, WIDTH, bar_h))

        # Prompt de restart (fase 3+)
        if phase >= 3 and self.timer > 550:
            if (self.timer // 35) % 2 == 0:
                restart = font_tiny.render("Pressione R para jogar novamente", True, (150, 150, 160))
                render.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT - bar_h + 15))

        # Fade final
        if self.fade_alpha > 0:
            fade = pygame.Surface((WIDTH, HEIGHT))
            fade.fill(BLACK)
            fade.set_alpha(self.fade_alpha)
            render.blit(fade, (0, 0))

        surface.fill(BLACK)
        surface.blit(render, (self.shake_x, self.shake_y))


def draw_defeat_screen(surface, altitude_m, score=0):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    title = font_large.render("HOPE CAIU...", True, DEFEAT_COLOR)
    sub = font_small.render(f"Altitude alcançada: {int(altitude_m)}m", True, WHITE)
    score_txt = font_medium.render(f"Pontuação: {score}", True, (255, 220, 80))
    restart = font_tiny.render("Pressione R para tentar novamente", True, WHITE)

    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 10))
    surface.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, HEIGHT // 2 + 35))
    surface.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 90))


def draw_start_screen(surface, anim_timer):
    surface.fill(CAVE_BG)

    # Paredes decorativas
    for i in range(HEIGHT // 50 + 1):
        y = i * 50
        w1 = 50 + int(math.sin(y * 0.03) * 15)
        w2 = 50 + int(math.sin(y * 0.025 + 3) * 15)
        pygame.draw.rect(surface, CAVE_WALL_2, (0, y, w1, 52))
        pygame.draw.rect(surface, CAVE_WALL_2, (WIDTH - w2, y, w2, 52))

    # Título
    pulse = math.sin(anim_timer * 0.05) * 0.15 + 1.0
    title = font_large.render("FASE 7", True, SOLAR_ORB)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

    sub = font_medium.render("ODS 7 — Energia Limpa", True, HOPE_VISOR)
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 210))

    # Instruções
    instructions = [
        "← → ou A/D — Mover",
        "↑ ↓ ou W/S — Subir/Descer",
        "SPACE ou E — Atirar",
        "",
        "Colete orbes solares para recarregar o jetpack!",
        "Fuja da caverna subindo 300m!"
    ]
    for i, line in enumerate(instructions):
        color = (180, 220, 200) if line else WHITE
        text = font_tiny.render(line, True, color)
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 320 + i * 32))

    # Prompt
    blink = (anim_timer // 30) % 2 == 0
    if blink:
        start_text = font_small.render("Pressione ENTER para começar", True, WHITE)
        surface.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 560))

    # Hope desenhada na tela inicial
    hope_x = WIDTH // 2 - 20
    hope_y = 440 + int(math.sin(anim_timer * 0.04) * 8)
    pygame.draw.rect(surface, HOPE_BODY, (hope_x + 5, hope_y + 18, 30, 35), border_radius=4)
    pygame.draw.ellipse(surface, HOPE_BODY, (hope_x + 6, hope_y, 28, 24))
    pygame.draw.ellipse(surface, HOPE_VISOR, (hope_x + 10, hope_y + 4, 20, 14))

    # Chama animada
    for _ in range(3):
        fx = hope_x + 20 + random.randint(-6, 6)
        fy = hope_y + 55 + random.randint(0, 10)
        color = random.choice([FLAME_ORANGE, FLAME_BLUE])
        pygame.draw.circle(surface, color, (fx, fy), random.randint(3, 6))


# ===================== CUTSCENE (INTRODUÇÃO ANIMADA) =====================
class Cutscene:
    """Cutscene dentro da caverna — Hope salva prisioneiros e recebe jetpack"""
    def __init__(self):
        self.timer = 0
        self.done = False
        self.particles = []
        self.shake_x = 0
        self.shake_y = 0

        # Fases (frames, 60fps):
        # 0: Tela escura — "Nas profundezas da caverna..."         (0-150)
        # 1: Hope andando pela caverna, cristais brilhando          (150-350)
        # 2: Hope encontra cela com cientista preso                 (350-520)
        # 3: Cientista entrega jetpack — diálogo                    (520-700)
        # 4: Jetpack liga! Explosão de partículas, Hope sobe        (700-840)
        # 5: Fade out                                               (840-920)

        self.hope_x = -60.0
        self.hope_y = 470.0
        self.hope_walking = False
        self.walk_frame = 0

        self.ground_y = 530

        # Cristais na parede da caverna
        self.crystals = []
        for _ in range(15):
            self.crystals.append({
                'x': random.randint(10, WIDTH - 10),
                'y': random.randint(80, self.ground_y - 40),
                'side': random.choice(['left', 'right']),
                'color': random.choice(CRYSTAL_COLORS),
                'size': random.randint(5, 14),
                'phase': random.uniform(0, math.pi * 2),
            })
        # Filtrar pra ficar nas paredes
        for c in self.crystals:
            if c['side'] == 'left':
                c['x'] = random.randint(15, 80)
            else:
                c['x'] = random.randint(WIDTH - 80, WIDTH - 15)

        # Posição da cela do cientista
        self.cell_x = 550

        # Textos narrativos
        self.texts = [
            {"text": "Nas profundezas da caverna...", "start": 20, "end": 140, "y": HEIGHT // 2 - 30, "color": (160, 160, 180), "font": "medium"},
            {"text": "Hope resgatava os prisioneiros dos Umans.", "start": 60, "end": 140, "y": HEIGHT // 2 + 20, "color": (120, 120, 140), "font": "small"},
            {"text": "Mais uma cela adiante...", "start": 170, "end": 340, "y": 70, "color": (140, 200, 180), "font": "small"},
            {"text": "Um cientista!", "start": 360, "end": 500, "y": 70, "color": (200, 200, 140), "font": "medium"},
            {"text": '"Pegue... meu último protótipo."', "start": 530, "end": 640, "y": 70, "color": (180, 220, 255), "font": "small"},
            {"text": '"Um jetpack movido a energia solar."', "start": 580, "end": 680, "y": 105, "color": (180, 220, 255), "font": "small"},
            {"text": '"Alcance a superfície e salve nosso vilarejo!"', "start": 640, "end": 695, "y": 140, "color": (255, 220, 100), "font": "small"},
            {"text": "JETPACK SOLAR: ATIVADO", "start": 715, "end": 830, "y": 90, "color": (120, 255, 180), "font": "medium"},
            {"text": "ODS 7 — Energia Limpa e Acessível", "start": 760, "end": 830, "y": 135, "color": (255, 200, 60), "font": "tiny"},
        ]

        self.jetpack_on = False
        self.screen_flash = 0
        self.fade_alpha = 0

    def get_phase(self):
        if self.timer < 150: return 0
        if self.timer < 350: return 1
        if self.timer < 520: return 2
        if self.timer < 700: return 3
        if self.timer < 840: return 4
        return 5

    def update(self):
        self.timer += 1
        phase = self.get_phase()

        if phase == 0:
            pass

        elif phase == 1:
            self.hope_walking = True
            if self.hope_x < 300:
                self.hope_x += 1.6
            self.walk_frame += 1

        elif phase == 2:
            self.hope_walking = True
            if self.hope_x < self.cell_x - 90:
                self.hope_x += 1.4
            else:
                self.hope_walking = False
            self.walk_frame += 1

        elif phase == 3:
            self.hope_walking = False

        elif phase == 4:
            if not self.jetpack_on:
                self.jetpack_on = True
                self.screen_flash = 20
                for _ in range(45):
                    self.particles.append(Particle(
                        self.hope_x + 20, self.hope_y + 55,
                        random.choice([FLAME_ORANGE, FLAME_BLUE, FLAME_WHITE, (255, 255, 200)]),
                        vx=random.uniform(-8, 8),
                        vy=random.uniform(-2, 10),
                        life=random.randint(20, 50),
                        size=random.randint(3, 8),
                        gravity=0.2
                    ))
                self.shake_x = random.randint(-6, 6)
                self.shake_y = random.randint(-6, 6)

            self.hope_y -= 2.8

            if self.timer % 2 == 0:
                for _ in range(3):
                    self.particles.append(Particle(
                        self.hope_x + 20 + random.uniform(-8, 8),
                        self.hope_y + 55,
                        random.choice([FLAME_ORANGE, FLAME_BLUE, FLAME_WHITE]),
                        vx=random.uniform(-2, 2),
                        vy=random.uniform(3, 7),
                        life=random.randint(10, 20),
                        size=random.randint(3, 6),
                        gravity=0.1
                    ))

            if self.screen_flash > 0:
                self.screen_flash -= 1
                self.shake_x = random.randint(-3, 3)
                self.shake_y = random.randint(-3, 3)
            else:
                self.shake_x = int(self.shake_x * 0.9)
                self.shake_y = int(self.shake_y * 0.9)

        elif phase == 5:
            self.fade_alpha = min(255, self.fade_alpha + 4)
            if self.timer > 920:
                self.done = True

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        # Gotículas de água caindo
        if phase >= 1 and phase <= 3 and self.timer % 12 == 0:
            self.particles.append(Particle(
                random.randint(90, WIDTH - 90), random.randint(-5, 0),
                (80, 120, 160),
                vx=0, vy=random.uniform(1.5, 3),
                life=random.randint(40, 80),
                size=2, shrink=False
            ))

    def draw_cave_bg(self, render):
        """Desenha o interior da caverna"""
        render.fill(CAVE_BG)

        # Paredes da caverna
        for i in range(-1, HEIGHT // 50 + 2):
            y = i * 50
            w_left = 55 + int(math.sin(y * 0.03 + 1) * 18)
            w_right = 55 + int(math.sin(y * 0.025 + 3) * 18)
            pygame.draw.rect(render, CAVE_WALL_1, (0, y, w_left + 15, 52))
            pygame.draw.rect(render, CAVE_WALL_1, (WIDTH - w_right - 15, y, w_right + 15, 52))
            pygame.draw.rect(render, CAVE_WALL_2, (0, y, w_left, 52))
            pygame.draw.rect(render, CAVE_WALL_2, (WIDTH - w_right, y, w_right, 52))
            # Rochas decorativas
            if i % 3 == 0:
                pygame.draw.circle(render, CAVE_ROCK, (w_left - 3, y + 25), 6)
                pygame.draw.circle(render, CAVE_ROCK, (WIDTH - w_right + 3, y + 25), 6)

        # Chão da caverna
        pygame.draw.rect(render, CAVE_WALL_2, (0, self.ground_y, WIDTH, HEIGHT - self.ground_y))
        pygame.draw.rect(render, CAVE_WALL_1, (0, self.ground_y, WIDTH, 5))
        for i in range(0, WIDTH, 40):
            pygame.draw.circle(render, CAVE_ROCK, (i + random.randint(0, 10), self.ground_y + 2), 4)

        # Teto
        pygame.draw.rect(render, CAVE_WALL_2, (0, 0, WIDTH, 55))
        pygame.draw.rect(render, CAVE_WALL_1, (0, 50, WIDTH, 8))

        # Cristais brilhantes nas paredes
        for c in self.crystals:
            pulse = math.sin(c['phase'] + self.timer * 0.04) * 0.4 + 0.6
            sz = c['size']
            # Glow
            glow_sz = int(sz * 2 * pulse)
            glow = pygame.Surface((glow_sz * 2, glow_sz * 2), pygame.SRCALPHA)
            r, g, b = c['color']
            pygame.draw.circle(glow, (r, g, b, int(30 * pulse)), (glow_sz, glow_sz), glow_sz)
            render.blit(glow, (c['x'] - glow_sz, c['y'] - glow_sz))
            # Cristal (losango)
            pts = [(c['x'], c['y'] - sz), (c['x'] + sz // 2, c['y']),
                   (c['x'], c['y'] + sz // 2), (c['x'] - sz // 2, c['y'])]
            pygame.draw.polygon(render, c['color'], pts)

        # Tochas na parede (iluminação fraca)
        torch_positions = [120, 350, 600]
        for tx in torch_positions:
            ty = self.ground_y - 60
            # Suporte
            pygame.draw.rect(render, (90, 70, 50), (tx - 2, ty, 6, 25))
            # Chama
            flame_flicker = random.randint(-2, 2)
            pygame.draw.circle(render, (255, 160, 40), (tx + 1 + flame_flicker, ty - 4), 6)
            pygame.draw.circle(render, (255, 220, 80), (tx + 1, ty - 3), 3)
            # Glow da tocha
            glow = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 150, 40, 15), (40, 40), 40)
            render.blit(glow, (tx - 39, ty - 44))

    def draw_scientist(self, render, x, y):
        """Desenha o cientista preso"""
        # Jaleco branco
        pygame.draw.rect(render, (200, 200, 210), (x + 5, y + 16, 26, 35), border_radius=3)
        # Cabeça
        pygame.draw.ellipse(render, (220, 190, 170), (x + 7, y, 22, 20))
        # Óculos
        pygame.draw.circle(render, (180, 200, 255), (x + 13, y + 8), 5, 1)
        pygame.draw.circle(render, (180, 200, 255), (x + 23, y + 8), 5, 1)
        pygame.draw.line(render, (180, 200, 255), (x + 18, y + 8), (x + 18, y + 8), 1)
        # Cabelo (grisalho)
        pygame.draw.ellipse(render, (160, 160, 170), (x + 8, y - 2, 20, 10))
        # Pernas
        pygame.draw.rect(render, (60, 60, 80), (x + 10, y + 48, 8, 10), border_radius=2)
        pygame.draw.rect(render, (60, 60, 80), (x + 19, y + 48, 8, 10), border_radius=2)

    def draw_cell_bars(self, render, x, y):
        """Grades da cela — algumas já quebradas"""
        bar_color = (100, 90, 80)
        for i in range(6):
            bx = x + i * 14
            if i == 2 or i == 3:
                # Grades quebradas (Hope já abriu)
                pygame.draw.line(render, bar_color, (bx, y), (bx + 5, y + 30), 3)
                pygame.draw.line(render, bar_color, (bx + 3, y + 50), (bx, y + 80), 3)
            else:
                pygame.draw.line(render, bar_color, (bx, y), (bx, y + 80), 3)
        # Barra horizontal
        pygame.draw.line(render, bar_color, (x, y + 25), (x + 70, y + 25), 2)
        pygame.draw.line(render, bar_color, (x, y + 55), (x + 70, y + 55), 2)

    def draw_hope(self, render, hx, hy):
        """Desenha Hope animada"""
        pygame.draw.rect(render, HOPE_BODY, (hx + 5, hy + 18, 30, 35), border_radius=4)
        pygame.draw.ellipse(render, HOPE_BODY, (hx + 6, hy, 28, 24))
        pygame.draw.ellipse(render, HOPE_VISOR, (hx + 10, hy + 4, 20, 14))
        pygame.draw.ellipse(render, (220, 250, 255), (hx + 13, hy + 6, 6, 4))
        pygame.draw.rect(render, HOPE_JETPACK, (hx + 2, hy + 22, 8, 20), border_radius=2)
        pygame.draw.rect(render, HOPE_JETPACK, (hx + 30, hy + 22, 8, 20), border_radius=2)
        pygame.draw.rect(render, HOPE_BODY, (hx, hy + 22, 7, 16), border_radius=3)
        pygame.draw.rect(render, HOPE_BODY, (hx + 33, hy + 22, 7, 16), border_radius=3)

        if self.hope_walking:
            leg_off = int(math.sin(self.walk_frame * 0.15) * 5)
            pygame.draw.rect(render, HOPE_BODY, (hx + 10, hy + 50 + leg_off, 9, 10), border_radius=2)
            pygame.draw.rect(render, HOPE_BODY, (hx + 22, hy + 50 - leg_off, 9, 10), border_radius=2)
        else:
            pygame.draw.rect(render, HOPE_BODY, (hx + 10, hy + 50, 9, 10), border_radius=2)
            pygame.draw.rect(render, HOPE_BODY, (hx + 22, hy + 50, 9, 10), border_radius=2)

        if self.jetpack_on:
            for _ in range(4):
                fx = hx + 20 + random.randint(-8, 8)
                fy = hy + 58 + random.randint(0, 12)
                color = random.choice([FLAME_ORANGE, FLAME_BLUE, FLAME_WHITE])
                pygame.draw.circle(render, color, (fx, fy), random.randint(3, 7))
            glow_surf = pygame.Surface((80, 90), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (255, 200, 60, 35), (0, 0, 80, 90))
            render.blit(glow_surf, (hx - 20, hy - 15))

    def draw(self, surface):
        phase = self.get_phase()
        render = pygame.Surface((WIDTH, HEIGHT))

        if phase == 0:
            render.fill((5, 3, 8))
            # Gotículas sutis
            for p in self.particles:
                p.draw(render)

        elif phase >= 1:
            self.draw_cave_bg(render)

            # Cela do cientista (aparece a partir da fase 2)
            if phase >= 2:
                cx = self.cell_x
                cy = self.ground_y - 80
                # Fundo da cela (buraco na parede)
                pygame.draw.rect(render, (12, 8, 15), (cx - 10, cy, 90, 85))
                # Grades
                self.draw_cell_bars(render, cx - 5, cy)
                # Cientista dentro
                self.draw_scientist(render, cx + 20, cy + 18)

                # Jetpack no chão (fase 3 — cientista entrega)
                if phase >= 3 and not self.jetpack_on:
                    # Jetpack brilhando no chão entre Hope e cientista
                    jp_x = int(self.hope_x + 60)
                    jp_y = self.ground_y - 28
                    # Glow
                    pulse = math.sin(self.timer * 0.1) * 0.3 + 0.7
                    glow = pygame.Surface((40, 40), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (255, 220, 60, int(50 * pulse)), (20, 20), 20)
                    render.blit(glow, (jp_x - 10, jp_y - 15))
                    # Jetpack item
                    pygame.draw.rect(render, HOPE_JETPACK, (jp_x, jp_y, 12, 18), border_radius=2)
                    pygame.draw.rect(render, HOPE_JETPACK, (jp_x + 8, jp_y, 12, 18), border_radius=2)
                    pygame.draw.circle(render, SOLAR_ORB, (jp_x + 10, jp_y + 5), 5)

            # Partículas
            for p in self.particles:
                p.draw(render)

            # Hope
            self.draw_hope(render, int(self.hope_x), int(self.hope_y))

        # ---- TEXTOS ----
        for txt in self.texts:
            if txt['start'] <= self.timer <= txt['end']:
                fade_in = 25
                fade_out = 20
                elapsed = self.timer - txt['start']
                remaining = txt['end'] - self.timer
                if elapsed < fade_in:
                    alpha = int((elapsed / fade_in) * 255)
                elif remaining < fade_out:
                    alpha = int((remaining / fade_out) * 255)
                else:
                    alpha = 255
                alpha = max(0, min(255, alpha))
                base = txt['color']
                r = min(255, int(base[0] * alpha / 255))
                g = min(255, int(base[1] * alpha / 255))
                b = min(255, int(base[2] * alpha / 255))
                f = font_medium if txt['font'] == 'medium' else font_tiny if txt['font'] == 'tiny' else font_small
                text_surf = f.render(txt['text'], True, (r, g, b))
                render.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, txt['y']))

        # Flash
        if self.screen_flash > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 240, 200, int((self.screen_flash / 20) * 150)))
            render.blit(flash, (0, 0))

        # Barras cinemáticas
        bar_h = 50
        pygame.draw.rect(render, BLACK, (0, 0, WIDTH, bar_h))
        pygame.draw.rect(render, BLACK, (0, HEIGHT - bar_h, WIDTH, bar_h))

        # Indicador de pular
        if self.timer > 60 and (self.timer // 40) % 2 == 0:
            skip = font_tiny.render("ENTER para pular", True, (90, 90, 100))
            render.blit(skip, (WIDTH - skip.get_width() - 20, HEIGHT - bar_h + 15))

        # Fade final
        if self.fade_alpha > 0:
            fade = pygame.Surface((WIDTH, HEIGHT))
            fade.fill(BLACK)
            fade.set_alpha(self.fade_alpha)
            render.blit(fade, (0, 0))

        surface.fill(BLACK)
        surface.blit(render, (self.shake_x, self.shake_y))


# ===================== GAME LOOP =====================
def main():
    state = "INTRO"  # INTRO, START, PLAYING, VICTORY_CUTSCENE, DEFEAT
    anim_timer = 0
    cutscene = Cutscene()

    # Variáveis do jogo (inicializadas no START → PLAYING)
    hope = None
    bullets = []
    enemies = []
    enemy_bullets = []
    orbs = []
    particles = []
    spawner = None
    cave_bg = None
    shake = None
    altitude_px = 0.0
    altitude_speed = 2.0  # pixels/frame base
    orb_timer = 0
    trap_system = None
    score = 0
    end_cutscene = None

    def start_game():
        nonlocal hope, bullets, enemies, enemy_bullets, orbs, particles
        nonlocal spawner, cave_bg, shake, altitude_px, orb_timer, trap_system, score, end_cutscene
        hope = Hope()
        bullets = []
        enemies = []
        enemy_bullets = []
        orbs = []
        particles = []
        spawner = WaveSpawner()
        cave_bg = CaveBackground()
        shake = ScreenShake()
        trap_system = TrapSystem()
        altitude_px = 0.0
        orb_timer = 0
        score = 0
        end_cutscene = None

    running = True
    while running:
        # ---- EVENTOS ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if state == "INTRO":
                    if event.key == pygame.K_RETURN:
                        state = "START"

                elif state == "START":
                    if event.key == pygame.K_RETURN:
                        start_game()
                        state = "PLAYING"

                elif state == "PLAYING":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_e:
                        b = hope.shoot()
                        if b:
                            bullets.append(b)

                elif state in ("VICTORY_CUTSCENE", "DEFEAT"):
                    if event.key == pygame.K_r:
                        start_game()
                        state = "PLAYING"

        anim_timer += 1

        # ---- INTRO (CUTSCENE) ----
        if state == "INTRO":
            cutscene.update()
            if cutscene.done:
                state = "START"
            cutscene.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # ---- START SCREEN ----
        if state == "START":
            draw_start_screen(screen, anim_timer)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # ---- PLAYING ----
        if state == "PLAYING":
            keys = pygame.key.get_pressed()

            # Tiro contínuo segurando SPACE/E
            if keys[pygame.K_SPACE] or keys[pygame.K_e]:
                b = hope.shoot()
                if b:
                    bullets.append(b)

            # Aplicar inversão de controles (Level Devil!)
            if trap_system and trap_system.invert_controls:
                # Cria um mapeamento invertido
                class FakeKeys:
                    def __init__(self, real_keys):
                        self._real = real_keys
                    def __getitem__(self, key):
                        if key == pygame.K_LEFT:
                            return self._real[pygame.K_RIGHT]
                        elif key == pygame.K_RIGHT:
                            return self._real[pygame.K_LEFT]
                        elif key == pygame.K_UP or key == pygame.K_w:
                            return self._real[pygame.K_DOWN] or self._real[pygame.K_s]
                        elif key == pygame.K_DOWN or key == pygame.K_s:
                            return self._real[pygame.K_UP] or self._real[pygame.K_w]
                        elif key == pygame.K_a:
                            return self._real[pygame.K_d]
                        elif key == pygame.K_d:
                            return self._real[pygame.K_a]
                        return self._real[key]
                keys = FakeKeys(keys)

            hope.update(keys)

            # Aplicar squeeze nas margens da Hope
            if trap_system and trap_system.squeeze_amount > 0.01:
                extra_margin = trap_system.get_squeeze_margin()
                total_margin = 80 + extra_margin
                if hope.x < total_margin:
                    hope.x = total_margin
                if hope.x + hope.width > WIDTH - total_margin:
                    hope.x = WIDTH - total_margin - hope.width
                hope.rect.x = int(hope.x)

            # Progredir altitude
            altitude_px += altitude_speed
            altitude_m = altitude_px / 15.0  # 15px = 1m
            progress_ratio = min(1.0, altitude_m / 300.0)

            # Spawner
            spawner.update(altitude_m, enemies)

            # Orbe solar a cada ~4 segundos
            orb_timer += 1
            orb_interval = 190 if altitude_m < 200 else 200 if altitude_m < 400 else 260
            if orb_timer >= orb_interval:
                orb_timer = 0
                ox = random.randint(100, WIDTH - 100)
                orbs.append(SolarOrb(ox, -30))

            # Sistema de armadilhas Level Devil
            trap_system.check_traps(altitude_m, hope, particles, shake)
            trap_system.update(hope, particles, shake)

            # Atualizar balas
            for b in bullets:
                b.update()
            bullets = [b for b in bullets if b.alive]

            # Atualizar inimigos
            for e in enemies:
                result = e.update(hope)
                if result and isinstance(result, EnemyBullet):
                    enemy_bullets.append(result)
            enemies = [e for e in enemies if e.alive]

            # Atualizar balas inimigas
            for eb in enemy_bullets:
                eb.update()
            enemy_bullets = [eb for eb in enemy_bullets if eb.alive]

            # Atualizar orbes
            for orb in orbs:
                orb.update()
            orbs = [o for o in orbs if o.alive]

            # ---- COLISÕES ----

            # Balas de Hope → Inimigos
            for b in list(bullets):
                if not b.alive:
                    continue
                for e in enemies:
                    if not e.alive:
                        continue
                    if b.rect.colliderect(e.rect):
                        e.hp -= 1
                        b.alive = False
                        # Partículas de hit
                        for _ in range(6):
                            particles.append(Particle(
                                e.x + e.width // 2, e.y + e.height // 2,
                                (255, 200, 100),
                                vx=random.uniform(-4, 4),
                                vy=random.uniform(-4, 4),
                                life=15, size=4
                            ))
                        if e.hp <= 0:
                            e.alive = False
                            score += e.score
                            shake.trigger(6, 3)
                            # Explosão
                            for _ in range(15):
                                particles.append(Particle(
                                    e.x + e.width // 2, e.y + e.height // 2,
                                    random.choice([(255, 160, 40), (255, 100, 30), (255, 220, 80)]),
                                    vx=random.uniform(-6, 6),
                                    vy=random.uniform(-6, 6),
                                    life=random.randint(15, 30),
                                    size=random.randint(3, 7),
                                    gravity=0.15
                                ))
                        break

            # Inimigos → Hope
            for e in enemies:
                if e.alive and hope.hit_timer <= 0 and e.rect.colliderect(hope.rect):
                    if hope.take_hit():
                        shake.trigger(12, 6)
                        for _ in range(10):
                            particles.append(Particle(
                                hope.x + hope.width // 2, hope.y + hope.height // 2,
                                (255, 80, 80),
                                vx=random.uniform(-5, 5),
                                vy=random.uniform(-5, 5),
                                life=20, size=5
                            ))
                        if hope.lives <= 0:
                            state = "DEFEAT"

            # Balas inimigas → Hope
            for eb in list(enemy_bullets):
                if eb.alive and hope.hit_timer <= 0 and eb.rect.colliderect(hope.rect):
                    eb.alive = False
                    if hope.take_hit():
                        shake.trigger(10, 5)
                        if hope.lives <= 0:
                            state = "DEFEAT"

            # Orbes → Hope
            for orb in orbs:
                if orb.alive and orb.rect.colliderect(hope.rect):
                    orb.alive = False
                    hope.collect_energy(25)
                    # Partículas de coleta
                    for _ in range(12):
                        particles.append(Particle(
                            orb.x, orb.y,
                            (255, 230, 80),
                            vx=random.uniform(-5, 5),
                            vy=random.uniform(-5, 5),
                            life=20, size=4, gravity=-0.1
                        ))

            # Game over se cair muito (sem energia e saiu da tela)
            if hope.y + hope.height > HEIGHT + 10:
                state = "DEFEAT"

            # Vitória! → Cutscene final
            if altitude_m >= 300:
                end_cutscene = EndCutscene(score)
                state = "VICTORY_CUTSCENE"

            # Checar se Hope morreu por armadilha
            if hope.lives <= 0:
                state = "DEFEAT"

            # Shake
            shake.update()

            # Partículas
            for p in particles:
                p.update()
            particles = [p for p in particles if p.life > 0]

        # ---- VICTORY CUTSCENE ----
        if state == "VICTORY_CUTSCENE":
            end_cutscene.update()
            end_cutscene.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # ---- RENDERING ----
        render_surface = pygame.Surface((WIDTH, HEIGHT))

        if state in ("PLAYING", "DEFEAT"):
            altitude_m = altitude_px / 15.0
            progress_ratio = min(1.0, altitude_m / 300.0)

            cave_bg.draw(render_surface, altitude_px, progress_ratio)

            # Orbes
            for orb in orbs:
                if orb.alive:
                    orb.draw(render_surface)

            # Balas inimigas
            for eb in enemy_bullets:
                if eb.alive:
                    eb.draw(render_surface)

            # Inimigos
            for e in enemies:
                if e.alive:
                    e.draw(render_surface)

            # Balas de Hope
            for b in bullets:
                if b.alive:
                    b.draw(render_surface)

            # Partículas
            for p in particles:
                p.draw(render_surface)

            # Armadilhas (Level Devil)
            if trap_system:
                trap_system.draw(render_surface)

            # Hope
            hope.draw(render_surface)

            # HUD
            draw_hud(render_surface, hope, altitude_m, score)

            # Tela de derrota
            if state == "DEFEAT":
                draw_defeat_screen(render_surface, altitude_m, score)

        # Aplicar shake
        if state in ("PLAYING",) and shake and shake.duration > 0:
            screen.fill(BLACK)
            screen.blit(render_surface, (shake.offset_x, shake.offset_y))
        else:
            screen.blit(render_surface, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
