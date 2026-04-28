import pygame
import sys
import math
import random
from constants import *
from particles import ParticleSystem
from player import Player, Bullet
from enemies import Enemy, Boss
from traps import TrapManager, SolarOrb
from cutscenes import CutsceneManager


class Background:
    def __init__(self):
        self.scroll = 0
        self.brightness = 0  # increases as waves progress
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(40)]

    def set_brightness(self, wave_num, total_waves):
        self.brightness = int((wave_num / total_waves) * 60)

    def update(self):
        self.scroll += 0.5

    def draw(self, surface):
        b = self.brightness
        # Sky gradient
        for y in range(HEIGHT):
            pct = y / HEIGHT
            r = min(255, int(12 + b * 0.5 + pct * (15 + b * 0.3)))
            g = min(255, int(8 + b * 0.3 + pct * (10 + b * 0.2)))
            bl = min(255, int(30 + b + pct * (20 + b * 0.4)))
            pygame.draw.line(surface, (r, g, bl), (0, y), (WIDTH, y))

        # Stars (fade as brightness increases)
        star_alpha = max(0, 200 - b * 3)
        if star_alpha > 0:
            for sx, sy in self.stars:
                ty = (sy + int(self.scroll * 0.3)) % HEIGHT
                pygame.draw.circle(surface, (star_alpha, star_alpha, star_alpha), (sx, ty), 1)

        # Cave walls on sides
        wall_w = 40 + int(math.sin(self.scroll * 0.01) * 10)
        wall_color = (35 + b // 3, 30 + b // 3, 50 + b // 3)
        for y in range(0, HEIGHT, 20):
            offset = int(math.sin((y + self.scroll) * 0.03) * 15)
            lw = wall_w + offset
            rw = wall_w - offset + 5
            pygame.draw.rect(surface, wall_color, (0, y, lw, 22))
            pygame.draw.rect(surface, wall_color, (WIDTH - rw, y, rw, 22))
            # Texture
            pygame.draw.line(surface, (50 + b // 2, 45 + b // 2, 65 + b // 2),
                             (lw - 3, y), (lw - 3, y + 20), 1)
            pygame.draw.line(surface, (50 + b // 2, 45 + b // 2, 65 + b // 2),
                             (WIDTH - rw + 3, y), (WIDTH - rw + 3, y + 20), 1)

        # Sun at top (gets bigger/brighter with waves)
        if b > 10:
            sun_r = int(b * 0.8)
            sun_alpha = min(120, b * 2)
            glow = pygame.Surface((sun_r * 6, sun_r * 4), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 220, 100, sun_alpha // 3), (0, 0, sun_r * 6, sun_r * 4))
            surface.blit(glow, (WIDTH // 2 - sun_r * 3, -sun_r * 2))
            pygame.draw.circle(surface, (255, 230, 120, min(200, sun_alpha)),
                               (WIDTH // 2, 0), sun_r)


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        self.font_big = pygame.font.Font(None, 40)
        self.wave_text = ""
        self.wave_text_timer = 0

    def show_wave_text(self, text):
        self.wave_text = text
        self.wave_text_timer = 180

    def draw(self, surface, player, wave_num, total_waves):
        # HP bar
        hp_pct = player.hp / PLAYER_MAX_HP
        bar_w, bar_h = 160, 16
        bx, by = 15, 15
        pygame.draw.rect(surface, (40, 0, 0), (bx, by, bar_w, bar_h), border_radius=4)
        if hp_pct > 0.5:
            hp_color = (50, 200, 80)
        elif hp_pct > 0.25:
            hp_color = (220, 180, 30)
        else:
            hp_color = (220, 50, 30)
        pygame.draw.rect(surface, hp_color, (bx, by, int(bar_w * hp_pct), bar_h), border_radius=4)
        pygame.draw.rect(surface, WHITE, (bx, by, bar_w, bar_h), 2, border_radius=4)
        hp_txt = self.font_small.render(f"HP {player.hp}/{PLAYER_MAX_HP}", True, WHITE)
        surface.blit(hp_txt, (bx + 5, by + 1))

        # Energy bar
        en_pct = player.energy / PLAYER_MAX_ENERGY
        ey = by + bar_h + 6
        pygame.draw.rect(surface, (40, 30, 0), (bx, ey, bar_w, bar_h), border_radius=4)
        en_color = SOLAR_GOLD if en_pct > 0.3 else SOLAR_ORANGE if en_pct > 0.1 else (200, 50, 20)
        pygame.draw.rect(surface, en_color, (bx, ey, int(bar_w * en_pct), bar_h), border_radius=4)
        pygame.draw.rect(surface, SOLAR_GOLD, (bx, ey, bar_w, bar_h), 2, border_radius=4)
        en_txt = self.font_small.render(f"ENERGIA {int(player.energy)}%", True, WHITE)
        surface.blit(en_txt, (bx + 5, ey + 1))

        # Score
        score_txt = self.font.render(f"Pontos: {player.score}", True, WHITE)
        surface.blit(score_txt, (WIDTH - score_txt.get_width() - 15, 15))

        # Wave indicator
        wave_txt = self.font_small.render(f"Onda {wave_num}/{total_waves}", True, (180, 180, 200))
        surface.blit(wave_txt, (WIDTH - wave_txt.get_width() - 15, 42))

        # Wave announcement text
        if self.wave_text_timer > 0:
            self.wave_text_timer -= 1
            alpha = min(255, self.wave_text_timer * 3)
            txt = self.font_big.render(self.wave_text, True, SOLAR_GOLD)
            txt.set_alpha(alpha)
            y = HEIGHT // 2 - 120 + int(math.sin(self.wave_text_timer * 0.05) * 3)
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y))


class Game:
    STATE_INTRO = 0
    STATE_PLAYING = 1
    STATE_GAME_OVER = 2
    STATE_VICTORY = 3
    STATE_OUTRO = 4
    STATE_PAUSED = 5

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.state = self.STATE_INTRO

        self.player = Player()
        self.particles = ParticleSystem()
        self.background = Background()
        self.hud = HUD()
        self.trap_manager = TrapManager()
        self.cutscene = CutsceneManager(self.screen)
        self.cutscene.reset("intro")

        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.boss = None
        self.solar_orbs = []

        self.current_wave = 0
        self.wave_queue = []  # enemies to spawn
        self.spawn_timer = 0
        self.wave_clear = False
        self.wave_transition_timer = 0
        self.total_waves = len(WAVES)

        self.shake_timer = 0
        self.shake_intensity = 0
        self.game_over_timer = 0

        self.wave_texts = [
            "Os U.M.A.N.S te avistaram!",
            "Reforços inimigos chegando!",
            "Ataque máximo! Resistam!",
            "COMANDANTE U.M.A.N.S DETECTADO!"
        ]

    def screen_shake(self, intensity=8, duration=15):
        self.shake_timer = duration
        self.shake_intensity = intensity

    def start_wave(self, wave_idx):
        if wave_idx >= len(WAVES):
            return
        self.current_wave = wave_idx
        self.wave_queue = []
        self.background.set_brightness(wave_idx, self.total_waves)
        self.trap_manager.set_difficulty(wave_idx)

        wave_data = WAVES[wave_idx]
        for etype, count, delay in wave_data:
            if etype == "boss":
                self.boss = Boss()
            else:
                for i in range(count):
                    self.wave_queue.append((etype, delay * i + random.randint(0, 30)))

        # Sort by spawn time
        self.wave_queue.sort(key=lambda x: x[1])
        self.spawn_timer = 0

        if wave_idx < len(self.wave_texts):
            self.hud.show_wave_text(self.wave_texts[wave_idx])

    def spawn_enemies(self):
        to_remove = []
        for i, (etype, delay) in enumerate(self.wave_queue):
            if self.spawn_timer >= delay:
                x = random.randint(80, WIDTH - 80)
                self.enemies.append(Enemy(etype, x, -30))
                to_remove.append(i)
        for i in reversed(to_remove):
            self.wave_queue.pop(i)
        self.spawn_timer += 1

    def check_wave_clear(self):
        if self.boss is not None:
            return not self.boss.alive
        return len(self.wave_queue) == 0 and len(self.enemies) == 0

    def update_playing(self, events, keys):
        # Maintain exactly MAX_SOLAR_ORBS on screen
        while len(self.solar_orbs) < MAX_SOLAR_ORBS:
            # Space them apart: find positions far from existing orbs
            attempts = 0
            while attempts < 10:
                new_x = random.randint(80, WIDTH - 80)
                new_y = random.randint(-300, -50)
                too_close = False
                for existing in self.solar_orbs:
                    if abs(existing.x - new_x) < 150 and abs(existing.y - new_y) < 200:
                        too_close = True
                        break
                if not too_close:
                    break
                attempts += 1
            self.solar_orbs.append(SolarOrb(new_x, new_y))

        # Spawn wave enemies
        self.spawn_enemies()

        # Player update
        self.player.update(keys, self.particles)

        # Low energy penalty
        if self.player.energy <= 0:
            self.player.y = min(HEIGHT - 30, self.player.y + 1.5)
            if random.random() < 0.03:
                self.player.take_damage()

        # Shooting
        if keys[pygame.K_SPACE]:
            bullet = self.player.shoot()
            if bullet:
                self.bullets.append(bullet)

        # Update bullets
        for b in self.bullets:
            b.update(self.particles)
        self.bullets = [b for b in self.bullets if b.alive]

        # Update enemy bullets
        for eb in self.enemy_bullets:
            eb.update(self.particles)
        self.enemy_bullets = [eb for eb in self.enemy_bullets if eb.alive]

        # Update enemies
        for e in self.enemies:
            new_bullets = e.update(self.player.x, self.player.y)
            self.enemy_bullets.extend(new_bullets)
        self.enemies = [e for e in self.enemies if e.alive]

        # Update boss
        if self.boss and self.boss.alive:
            new_bullets = self.boss.update(self.player.x, self.player.y)
            self.enemy_bullets.extend(new_bullets)

        # Update solar orbs
        for orb in self.solar_orbs:
            orb.update()
        self.solar_orbs = [o for o in self.solar_orbs if o.alive]

        # Update traps
        self.trap_manager.update(self.player)

        # Update particles
        self.particles.update()

        # Update background
        self.background.update()

        # --- Collisions ---
        p_rect = self.player.get_rect()

        # Player bullets vs enemies
        for b in self.bullets:
            b_rect = b.get_rect()
            for e in self.enemies:
                if b_rect.colliderect(e.get_rect()):
                    b.alive = False
                    if e.take_damage():
                        self.player.score += e.score
                        self.particles.emit_burst(e.x, e.y, UMAN_RED, 15, 4, 25, 4, glow=True)
                        self.screen_shake(4, 8)
                    else:
                        self.particles.emit_burst(e.x, e.y, WHITE, 5, 2, 10, 2)
                    break
            # Bullets vs boss
            if self.boss and self.boss.alive:
                if b_rect.colliderect(self.boss.get_rect()):
                    b.alive = False
                    if self.boss.take_damage():
                        self.player.score += self.boss.score
                        self.particles.emit_burst(self.boss.x, self.boss.y, BOSS_ACCENT, 40, 6, 40, 5, glow=True)
                        self.screen_shake(15, 30)
                    else:
                        self.particles.emit_burst(self.boss.x, self.boss.y, WHITE, 3, 2, 8, 2)

        # Enemy bullets vs player
        for eb in self.enemy_bullets:
            if eb.get_rect().colliderect(p_rect):
                if self.player.take_damage():
                    self.particles.emit_burst(self.player.x, self.player.y, (255, 100, 100), 12, 3, 15, 3)
                    self.screen_shake(6, 12)
                eb.alive = False

        # Enemies touching player
        for e in self.enemies:
            if e.get_rect().colliderect(p_rect):
                if self.player.take_damage():
                    self.particles.emit_burst(self.player.x, self.player.y, (255, 100, 100), 10, 3, 15, 3)
                    self.screen_shake(5, 10)

        # Solar orbs collection
        for orb in self.solar_orbs:
            if orb.get_rect().colliderect(p_rect):
                self.player.collect_energy(orb.value)
                self.particles.emit_burst(orb.x, orb.y, SOLAR_GOLD, 10, 3, 15, 3, glow=True)
                orb.alive = False

        # Check player death
        if self.player.hp <= 0:
            self.state = self.STATE_GAME_OVER
            self.game_over_timer = 0

        # Check wave clear
        if self.check_wave_clear():
            if not self.wave_clear:
                self.wave_clear = True
                self.wave_transition_timer = 120
                if self.boss and not self.boss.alive:
                    self.boss = None
            else:
                self.wave_transition_timer -= 1
                if self.wave_transition_timer <= 0:
                    next_wave = self.current_wave + 1
                    if next_wave >= len(WAVES):
                        self.state = self.STATE_OUTRO
                        self.cutscene.reset("outro")
                    else:
                        self.wave_clear = False
                        self.start_wave(next_wave)

        # Shake
        if self.shake_timer > 0:
            self.shake_timer -= 1

    def draw_playing(self):
        render_surface = pygame.Surface((WIDTH, HEIGHT))

        self.background.draw(render_surface)
        self.trap_manager.draw(render_surface)

        for orb in self.solar_orbs:
            orb.draw(render_surface)
        for b in self.bullets:
            b.draw(render_surface)
        for eb in self.enemy_bullets:
            eb.draw(render_surface)
        for e in self.enemies:
            e.draw(render_surface)
        if self.boss and self.boss.alive:
            self.boss.draw(render_surface)

        self.player.draw(render_surface)
        self.particles.draw(render_surface)
        self.hud.draw(render_surface, self.player, self.current_wave + 1, self.total_waves)

        # Apply screen shake
        offset_x, offset_y = 0, 0
        if self.shake_timer > 0:
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)

        self.screen.fill(BLACK)
        self.screen.blit(render_surface, (offset_x, offset_y))

    def draw_game_over(self):
        self.game_over_timer += 1
        self.screen.fill(BLACK)

        # Red vignette
        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for r in range(300, 0, -5):
            alpha = max(0, 60 - r // 6)
            pygame.draw.circle(vignette, (100, 0, 0, alpha), (WIDTH // 2, HEIGHT // 2), r)
        self.screen.blit(vignette, (0, 0))

        font_big = pygame.font.Font(None, 64)
        font_med = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)

        alpha = min(255, self.game_over_timer * 4)

        txt = font_big.render("GAME OVER", True, (200, 30, 30))
        txt.set_alpha(alpha)
        self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 3))

        score_txt = font_med.render(f"Pontuação: {self.player.score}", True, WHITE)
        score_txt.set_alpha(alpha)
        self.screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, HEIGHT // 3 + 70))

        wave_txt = font_med.render(f"Onda alcançada: {self.current_wave + 1}/{self.total_waves}", True, (180, 180, 200))
        wave_txt.set_alpha(alpha)
        self.screen.blit(wave_txt, (WIDTH // 2 - wave_txt.get_width() // 2, HEIGHT // 3 + 105))

        if self.game_over_timer > 90:
            hint = font_small.render("[ENTER] Tentar novamente  |  [ESC] Sair", True, (150, 150, 150))
            hint.set_alpha(int(abs(math.sin(self.game_over_timer * 0.04)) * 255))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 80))

    def reset_game(self):
        self.player = Player()
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.enemies.clear()
        self.boss = None
        self.solar_orbs.clear()
        self.particles = ParticleSystem()
        self.trap_manager = TrapManager()
        self.wave_clear = False
        self.wave_transition_timer = 0
        self.background = Background()
        self.state = self.STATE_PLAYING
        self.start_wave(0)

    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            for e in events:
                if e.type == pygame.QUIT:
                    running = False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    if self.state == self.STATE_PLAYING:
                        self.state = self.STATE_PAUSED
                    elif self.state == self.STATE_PAUSED:
                        self.state = self.STATE_PLAYING
                    elif self.state in (self.STATE_GAME_OVER, self.STATE_OUTRO):
                        running = False

            if self.state == self.STATE_INTRO:
                self.cutscene.update_intro(events)
                if self.cutscene.finished:
                    self.state = self.STATE_PLAYING
                    self.start_wave(0)

            elif self.state == self.STATE_PLAYING:
                self.update_playing(events, keys)
                self.draw_playing()

            elif self.state == self.STATE_GAME_OVER:
                self.draw_game_over()
                for e in events:
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                        if self.game_over_timer > 90:
                            self.reset_game()

            elif self.state == self.STATE_OUTRO:
                self.cutscene.update_outro(events)
                if self.cutscene.finished:
                    running = False

            elif self.state == self.STATE_PAUSED:
                # Dim screen
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 140))
                self.screen.blit(overlay, (0, 0))
                font = pygame.font.Font(None, 52)
                txt = font.render("PAUSADO", True, WHITE)
                self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 30))
                hint = pygame.font.Font(None, 26).render("[ESC] Continuar", True, (180, 180, 180))
                self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 30))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
