import pygame
import math
import random
from constants import *


class CutsceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.Font(None, 52)
        self.font_med = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.scene_index = 0
        self.timer = 0
        self.char_index = 0
        self.finished = False
        self.skip_held = 0

    def reset(self, scene_type="intro"):
        self.scene_index = 0
        self.timer = 0
        self.char_index = 0
        self.finished = False
        self.skip_held = 0
        self.scene_type = scene_type

    def _draw_cave_bg(self, brightness=0):
        self.screen.fill((12 + brightness, 12 + brightness, 30 + brightness))
        # Cave walls
        for i in range(0, WIDTH, 40):
            h = 60 + int(math.sin(i * 0.05) * 30)
            color = (40 + brightness, 35 + brightness, 55 + brightness)
            pygame.draw.rect(self.screen, color, (i, 0, 38, h))
            pygame.draw.rect(self.screen, color, (i, HEIGHT - h + 20, 38, h))
        # Stalactites
        for i in range(50, WIDTH, 120):
            pts = [(i, 0), (i + 15, 50 + int(math.sin(i) * 20)), (i + 30, 0)]
            pygame.draw.polygon(self.screen, (55 + brightness, 50 + brightness, 70 + brightness), pts)

    def _draw_sunbeam(self, cx, width, intensity):
        beam = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(width, 0, -3):
            alpha = int((intensity / 255) * (20 - i * 0.3))
            alpha = max(0, min(80, alpha))
            pygame.draw.polygon(beam, (255, 255, 180, alpha), [
                (cx - i, 0), (cx + i, 0),
                (cx + i + 40, HEIGHT), (cx - i - 40, HEIGHT)
            ])
        self.screen.blit(beam, (0, 0))

    def _draw_prisoners(self, count=5):
        for i in range(count):
            px = 250 + i * 70
            py = HEIGHT - 120
            # Body
            pygame.draw.rect(self.screen, (120, 100, 80), (px - 5, py, 10, 20))
            # Head
            pygame.draw.circle(self.screen, (180, 150, 110), (px, py - 5), 6)
            # Chains
            pygame.draw.line(self.screen, (100, 100, 100), (px - 8, py + 5), (px - 15, py + 15), 2)
            pygame.draw.line(self.screen, (100, 100, 100), (px + 8, py + 5), (px + 15, py + 15), 2)

    def _draw_hope(self, x, y, has_jetpack=False):
        # Body
        pygame.draw.rect(self.screen, HOPE_BODY, (x - 8, y - 8, 16, 22))
        # Head
        pygame.draw.circle(self.screen, HOPE_SKIN, (x, y - 14), 8)
        # Helmet
        pygame.draw.circle(self.screen, HOPE_HELMET, (x, y - 14), 8, 2)
        pygame.draw.rect(self.screen, HOPE_VISOR, (x - 4, y - 17, 8, 4))
        if has_jetpack:
            # Jetpack
            pygame.draw.rect(self.screen, JETPACK_GRAY, (x - 13, y - 5, 6, 16))
            pygame.draw.rect(self.screen, JETPACK_GRAY, (x + 7, y - 5, 6, 16))
            pygame.draw.rect(self.screen, SOLAR_GOLD, (x - 12, y - 3, 4, 10))
            pygame.draw.rect(self.screen, SOLAR_GOLD, (x + 8, y - 3, 4, 10))

    def _draw_scientist(self, x, y):
        # Lab coat
        pygame.draw.rect(self.screen, (200, 200, 210), (x - 8, y - 6, 16, 24))
        # Head
        pygame.draw.circle(self.screen, (190, 160, 130), (x, y - 12), 7)
        # Glasses
        pygame.draw.circle(self.screen, (100, 200, 255), (x - 3, y - 13), 3, 1)
        pygame.draw.circle(self.screen, (100, 200, 255), (x + 3, y - 13), 3, 1)
        pygame.draw.line(self.screen, (100, 200, 255), (x - 6, y - 13), (x + 6, y - 13), 1)
        # Hair (wild scientist hair)
        pygame.draw.ellipse(self.screen, (200, 200, 200), (x - 9, y - 22, 18, 12))

    def _draw_umans_flying(self, count=3):
        for i in range(count):
            ux = 150 + i * 200 + int(math.sin(self.timer * 0.03 + i) * 30)
            uy = 80 + int(math.cos(self.timer * 0.02 + i * 2) * 20)
            # UMAN body
            pts = [(ux, uy - 12), (ux + 14, uy + 6), (ux - 14, uy + 6)]
            pygame.draw.polygon(self.screen, UMAN_DARK, pts)
            pygame.draw.polygon(self.screen, UMAN_RED, pts, 2)
            pygame.draw.circle(self.screen, UMAN_RED, (ux - 3, uy - 3), 2)
            pygame.draw.circle(self.screen, UMAN_RED, (ux + 3, uy - 3), 2)

    def _draw_text_box(self, text, y_pos=None):
        if y_pos is None:
            y_pos = HEIGHT - 130
        # Background box
        box = pygame.Surface((WIDTH - 80, 100), pygame.SRCALPHA)
        box.fill((0, 0, 0, 180))
        pygame.draw.rect(box, ENERGY_CYAN, (0, 0, WIDTH - 80, 100), 2, border_radius=8)
        self.screen.blit(box, (40, y_pos))
        # Typewriter text
        visible = text[:self.char_index]
        lines = self._wrap_text(visible, self.font_small, WIDTH - 120)
        for i, line in enumerate(lines):
            txt_surf = self.font_small.render(line, True, WHITE)
            self.screen.blit(txt_surf, (60, y_pos + 15 + i * 22))
        # Advance char
        if self.timer % 2 == 0 and self.char_index < len(text):
            self.char_index += 1
        # Skip hint
        if self.char_index >= len(text):
            hint = self.font_small.render("[ENTER para continuar]", True, (150, 150, 180))
            hint.set_alpha(int(abs(math.sin(self.timer * 0.05)) * 255))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, y_pos + 80))

    def _wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current = ""
        for w in words:
            test = current + (" " if current else "") + w
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines if lines else [""]

    def _draw_destroyed_world(self):
        # Dark apocalyptic sky
        for y in range(HEIGHT):
            pct = y / HEIGHT
            r = int(30 + pct * 40)
            g = int(15 + pct * 20)
            b = int(25 + pct * 15)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        # Ruined buildings
        buildings = [(100, 200), (200, 280), (350, 180), (480, 260), (600, 220), (700, 190)]
        for bx, bh in buildings:
            by = HEIGHT - bh
            bw = 60
            pygame.draw.rect(self.screen, RUIN_GRAY, (bx, by, bw, bh))
            # Broken top
            for i in range(0, bw, 8):
                rh = random.Random(bx + i).randint(5, 25)
                pygame.draw.rect(self.screen, (70, 65, 60), (bx + i, by - rh, 6, rh))
            # Windows (some broken/lit)
            for wy in range(by + 15, HEIGHT - 30, 25):
                for wx in range(bx + 8, bx + bw - 8, 15):
                    if random.Random(wx + wy + bx).random() < 0.3:
                        pygame.draw.rect(self.screen, FIRE_COLOR, (wx, wy, 8, 10))
                    else:
                        pygame.draw.rect(self.screen, (40, 35, 30), (wx, wy, 8, 10))
        # Fires
        for fx in [150, 380, 550, 680]:
            fy = HEIGHT - 40
            for _ in range(5):
                fsize = random.Random(fx + self.timer // 10).randint(3, 8)
                fo = random.Random(fx + self.timer // 5 + _).randint(-10, 10)
                color = random.Random(fx + _).choice([FIRE_COLOR, SOLAR_ORANGE, (255, 50, 20)])
                pygame.draw.circle(self.screen, color, (fx + fo, fy - random.Random(fx + self.timer // 8 + _).randint(0, 20)), fsize)
        # Ground
        pygame.draw.rect(self.screen, (45, 40, 35), (0, HEIGHT - 30, WIDTH, 30))
        # Smoke/haze
        haze = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        haze.fill((40, 30, 20, 30))
        self.screen.blit(haze, (0, 0))

    def update_intro(self, events):
        self.timer += 1
        enter_pressed = False
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                enter_pressed = True

        scenes = [
            # Scene 0: Cave with prisoners
            {
                "draw": lambda: (
                    self._draw_cave_bg(0),
                    self._draw_sunbeam(WIDTH // 2, 60, 100 + math.sin(self.timer * 0.03) * 30),
                    self._draw_prisoners(),
                    self._draw_text_box(
                        "Ao libertar os moradores, Hope descobre que eles estavam mantidos sob um enorme "
                        "buraco no teto da caverna, por onde a luz do Sol penetrava. Era tambem o local onde "
                        "os U.M.A.N.S arremessavam dejetos poluentes sobre os prisioneiros."
                    )
                )
            },
            # Scene 1: UMANs throwing waste
            {
                "draw": lambda: (
                    self._draw_cave_bg(5),
                    self._draw_sunbeam(WIDTH // 2, 80, 130),
                    self._draw_umans_flying(),
                    self._draw_prisoners(),
                    self._draw_hope(180, HEIGHT - 100),
                    self._draw_text_box(
                        "Os U.M.A.N.S, capangas de Glitch, voavam acima do buraco e lancavam residuos "
                        "toxicos para intensificar o sofrimento dos prisioneiros. Hope observa a cena "
                        "com determinacao."
                    )
                )
            },
            # Scene 2: Scientist approaches
            {
                "draw": lambda: (
                    self._draw_cave_bg(10),
                    self._draw_sunbeam(WIDTH // 2, 60, 120),
                    self._draw_hope(350, HEIGHT - 100),
                    self._draw_scientist(420, HEIGHT - 95),
                    self._draw_text_box(
                        "Um cientista da vila se aproxima e revela uma invencao criada em segredo: uma "
                        "mochila jetpack equipada com uma placa solar, capaz de transformar a energia do "
                        "Sol em propulsao."
                    )
                )
            },
            # Scene 3: Hope gets jetpack
            {
                "draw": lambda: (
                    self._draw_cave_bg(20),
                    self._draw_sunbeam(WIDTH // 2, 100, 180 + math.sin(self.timer * 0.05) * 40),
                    self._draw_hope(WIDTH // 2, HEIGHT - 100 - min(self.timer * 0.5, 80), has_jetpack=True),
                    self._jetpack_particles(),
                    self._draw_text_box(
                        "Hope veste o equipamento e sente a forca da energia limpa impulsiona-lo para "
                        "cima! Com habilidade, ela vai enfrentar os U.M.A.N.S e trazer esperanca de volta!"
                    )
                )
            },
            # Scene 4: Title card
            {
                "draw": lambda: self._draw_title_card()
            },
        ]

        if self.scene_index < len(scenes):
            scenes[self.scene_index]["draw"]()
            # Check for scene advance
            scene_texts_len = [200, 190, 190, 180, 0]
            min_time = 60
            text_done = self.char_index >= scene_texts_len[min(self.scene_index, len(scene_texts_len) - 1)]
            if enter_pressed and (text_done or self.timer > min_time):
                self.scene_index += 1
                self.timer = 0
                self.char_index = 0
            elif enter_pressed and not text_done:
                self.char_index = scene_texts_len[min(self.scene_index, len(scene_texts_len) - 1)]
        else:
            self.finished = True

    def _jetpack_particles(self):
        cx = WIDTH // 2
        cy = HEIGHT - 100 - min(self.timer * 0.5, 80) + 18
        for i in range(3):
            fx = cx + random.randint(-6, 6)
            fy = cy + random.randint(0, 8)
            color = random.choice([SOLAR_GOLD, SOLAR_ORANGE, (255, 100, 30)])
            size = random.randint(2, 5)
            pygame.draw.circle(self.screen, color, (int(fx), int(fy)), size)

    def _draw_title_card(self):
        # Gradient background
        for y in range(HEIGHT):
            pct = y / HEIGHT
            r = int(10 + pct * 20)
            g = int(5 + pct * 10)
            b = int(40 + pct * 30)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        # Sun
        sun_y = HEIGHT // 3
        sun_r = 60 + int(math.sin(self.timer * 0.03) * 5)
        glow = pygame.Surface((sun_r * 6, sun_r * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 200, 50, 20), (sun_r * 3, sun_r * 3), sun_r * 3)
        pygame.draw.circle(glow, (255, 200, 50, 40), (sun_r * 3, sun_r * 3), sun_r * 2)
        self.screen.blit(glow, (WIDTH // 2 - sun_r * 3, sun_y - sun_r * 3))
        pygame.draw.circle(self.screen, SOLAR_GOLD, (WIDTH // 2, sun_y), sun_r)
        pygame.draw.circle(self.screen, SOLAR_BRIGHT, (WIDTH // 2, sun_y), sun_r - 15)
        # Rays
        for i in range(12):
            angle = self.timer * 0.02 + i * math.pi / 6
            ex = WIDTH // 2 + int(math.cos(angle) * (sun_r + 30))
            ey = sun_y + int(math.sin(angle) * (sun_r + 30))
            pygame.draw.line(self.screen, SOLAR_GOLD, (WIDTH // 2, sun_y), (ex, ey), 2)
        # Title
        alpha = min(255, self.timer * 4)
        title1 = self.font_big.render("FASE 7", True, WHITE)
        title2 = self.font_med.render("ENERGIA LIMPA E ACESSÍVEL", True, SOLAR_GOLD)
        title1.set_alpha(alpha)
        title2.set_alpha(alpha)
        self.screen.blit(title1, (WIDTH // 2 - title1.get_width() // 2, sun_y + sun_r + 40))
        self.screen.blit(title2, (WIDTH // 2 - title2.get_width() // 2, sun_y + sun_r + 85))
        # Controls hint
        if self.timer > 90:
            hint = self.font_small.render("WASD/Setas: Mover  |  ESPACO: Atirar  |  ENTER: Começar", True, (150, 150, 180))
            hint.set_alpha(int(abs(math.sin(self.timer * 0.04)) * 200))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 60))
        if self.timer > 60:
            enter_hint = self.font_med.render("[ENTER]", True, ENERGY_CYAN)
            enter_hint.set_alpha(int(abs(math.sin(self.timer * 0.06)) * 255))
            self.screen.blit(enter_hint, (WIDTH // 2 - enter_hint.get_width() // 2, HEIGHT - 100))

    def update_outro(self, events):
        self.timer += 1
        enter_pressed = False
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                enter_pressed = True

        scenes = [
            # Scene 0: Hope exits cave
            {
                "draw": lambda: (
                    self._draw_cave_bg(30),
                    self._draw_sunbeam(WIDTH // 2, 120, 220),
                    self._draw_hope(WIDTH // 2, HEIGHT // 2 - min(self.timer * 0.8, HEIGHT // 2 - 30), has_jetpack=True),
                    self._jetpack_outro_particles(),
                    self._draw_text_box(
                        "Apos derrotar os U.M.A.N.S, Hope sobe pelo buraco da caverna impulsionada "
                        "pela forca da energia solar. A luz do sol a guia para a superficie..."
                    )
                )
            },
            # Scene 1: Destroyed world
            {
                "draw": lambda: (
                    self._draw_destroyed_world(),
                    self._draw_hope(WIDTH // 2 - 100, HEIGHT - 80, has_jetpack=True),
                    self._draw_text_box(
                        "Ao sair da caverna, Hope ve o mundo devastado por Glitch e seus capangas "
                        "U.M.A.N.S. Cidades em ruinas, ceus escurecidos pela poluicao, e o rastro "
                        "de destruicao por toda parte."
                    )
                )
            },
            # Scene 2: Hope's determination
            {
                "draw": lambda: (
                    self._draw_destroyed_world(),
                    self._draw_hope(WIDTH // 2, HEIGHT - 80, has_jetpack=True),
                    self._draw_text_box(
                        "Mas Hope nao desiste. Com o jetpack solar nas costas e a esperanca no "
                        "coracao, ela sabe que ainda pode salvar a humanidade. A luta contra "
                        "Glitch esta apenas comecando!",
                        HEIGHT - 140
                    )
                )
            },
            # Scene 3: To be continued
            {
                "draw": lambda: self._draw_tbc_screen()
            },
        ]

        if self.scene_index < len(scenes):
            scenes[self.scene_index]["draw"]()
            scene_texts_len = [170, 200, 190, 0]
            min_time = 60
            text_done = self.char_index >= scene_texts_len[min(self.scene_index, len(scene_texts_len) - 1)]
            if enter_pressed and (text_done or self.timer > min_time):
                self.scene_index += 1
                self.timer = 0
                self.char_index = 0
            elif enter_pressed and not text_done:
                self.char_index = scene_texts_len[min(self.scene_index, len(scene_texts_len) - 1)]
        else:
            self.finished = True

    def _jetpack_outro_particles(self):
        cx = WIDTH // 2
        cy = HEIGHT // 2 - min(self.timer * 0.8, HEIGHT // 2 - 30) + 18
        for i in range(4):
            fx = cx + random.randint(-6, 6)
            fy = cy + random.randint(2, 12)
            color = random.choice([SOLAR_GOLD, SOLAR_ORANGE])
            pygame.draw.circle(self.screen, color, (int(fx), int(fy)), random.randint(2, 5))

    def _draw_tbc_screen(self):
        self.screen.fill((5, 5, 15))
        # Stars
        for i in range(50):
            sx = random.Random(i * 7).randint(0, WIDTH)
            sy = random.Random(i * 13).randint(0, HEIGHT)
            bright = int(abs(math.sin(self.timer * 0.02 + i)) * 200) + 55
            pygame.draw.circle(self.screen, (bright, bright, bright), (sx, sy), 1)
        # Hope silhouette flying
        hx = WIDTH // 2 + int(math.sin(self.timer * 0.02) * 30)
        hy = HEIGHT // 2 - 50
        self._draw_hope(hx, hy, has_jetpack=True)
        # Glow behind Hope
        glow = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*SOLAR_GOLD, 30), (40, 40), 40)
        self.screen.blit(glow, (hx - 40, hy - 40))
        # Text
        alpha = min(255, self.timer * 3)
        t1 = self.font_big.render("CONTINUA...", True, SOLAR_GOLD)
        t1.set_alpha(alpha)
        self.screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 + 60))
        t2 = self.font_small.render("A jornada de Hope pela humanidade nao acabou.", True, (180, 180, 200))
        t2.set_alpha(alpha)
        self.screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + 110))
        if self.timer > 120:
            hint = self.font_small.render("[ENTER para encerrar]", True, (120, 120, 150))
            hint.set_alpha(int(abs(math.sin(self.timer * 0.05)) * 200))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))
