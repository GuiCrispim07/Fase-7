import pygame
import math

# Screen
WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "ODS 7 - Energia Limpa e Acessível"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BG = (12, 12, 30)
CAVE_DARK = (20, 18, 35)
CAVE_WALL = (45, 40, 60)
CAVE_ACCENT = (65, 55, 80)

# Player colors
HOPE_BODY = (0, 160, 160)
HOPE_HELMET = (0, 220, 220)
HOPE_VISOR = (100, 255, 255)
HOPE_SKIN = (210, 180, 140)
JETPACK_GRAY = (80, 80, 100)

# Solar / Energy colors
SOLAR_GOLD = (255, 215, 0)
SOLAR_ORANGE = (255, 165, 0)
SOLAR_BRIGHT = (255, 255, 100)
ENERGY_CYAN = (0, 230, 255)
ENERGY_BEAM = (150, 255, 255)

# Enemy colors
UMAN_DARK = (60, 20, 80)
UMAN_RED = (200, 30, 30)
UMAN_TOXIC = (100, 255, 50)
UMAN_PURPLE = (120, 40, 160)
UMAN_ELITE = (180, 0, 0)
BOSS_COLOR = (100, 0, 130)
BOSS_ACCENT = (200, 0, 50)

# Trap colors
TRAP_WARNING = (255, 50, 50)
TOXIC_GREEN = (50, 200, 30)
FAKE_ORB = (200, 200, 0)

# Destroyed world
RUIN_GRAY = (60, 55, 50)
RUIN_ORANGE = (180, 80, 20)
SKY_DARK = (30, 20, 40)
FIRE_COLOR = (255, 100, 20)

# Game settings
PLAYER_SPEED = 5
PLAYER_MAX_HP = 5
PLAYER_MAX_ENERGY = 100
ENERGY_DRAIN_RATE = 0.08
ENERGY_ORB_VALUE = 30
SHOOT_COOLDOWN = 10
BULLET_SPEED = 8
INVINCIBLE_FRAMES = 60

# Enemy settings
ENEMY_CONFIGS = {
    "drone": {
        "hp": 1, "speed": 2, "score": 100,
        "shoot_rate": 90, "size": (24, 24),
        "color": UMAN_DARK, "accent": UMAN_RED
    },
    "bomber": {
        "hp": 2, "speed": 1.5, "score": 200,
        "shoot_rate": 120, "size": (32, 28),
        "color": UMAN_PURPLE, "accent": UMAN_TOXIC
    },
    "elite": {
        "hp": 3, "speed": 3.5, "score": 350,
        "shoot_rate": 45, "size": (28, 28),
        "color": UMAN_ELITE, "accent": (255, 100, 0)
    }
}

BOSS_HP = 60
BOSS_SIZE = (90, 70)
BOSS_SPEED = 2

# Wave definitions: list of (enemy_type, count, delay_between_spawns)
WAVES = [
    # Wave 1 - easy
    [("drone", 5, 55), ("bomber", 1, 80)],
    # Wave 2 - medium
    [("drone", 4, 45), ("bomber", 2, 60), ("elite", 1, 80)],
    # Wave 3 - hard
    [("drone", 4, 35), ("bomber", 3, 50), ("elite", 3, 55)],
    # Wave 4 - BOSS
    [("boss", 1, 0)],
]

# Max solar orbs on screen at once
MAX_SOLAR_ORBS = 3

# Trap types
TRAP_INVERSION = "inversion"
TRAP_FALLING = "falling"
TRAP_FAKE_ORB = "fake_orb"
TRAP_TOXIC_ZONE = "toxic_zone"
TRAP_SCREEN_GLITCH = "glitch"

# Cutscene
FONT_NAME = None  # Use default pygame font
CUTSCENE_SPEED = 2  # text chars per frame
