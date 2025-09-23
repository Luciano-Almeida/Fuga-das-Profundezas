import os
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Centraliza a janela

import math
import pgzrun
from pygame import Rect
import random
import time

# --- Tamanho da tela ---
#WIDTH = 800
#HEIGHT = 600
background = Actor('background')  # background.png
WIDTH = background.width
HEIGHT = background.height

# --- Background (ajustado ao tamanho novo) ---
#background = Actor('background', (WIDTH // 2, HEIGHT // 2))

# --- Variáveis globais ---
is_music_on = False
is_sounds_on = False
background_music = 'bolhas'  # nome da música
survive_time = 30  # segundos para passar de nível

# --- Função de colisão ---
def is_collision(a, b, radius_a=20, radius_b=20):
    dx = a.x - b.x
    dy = a.y - b.y
    distance = math.hypot(dx, dy)
    return distance < (radius_a + radius_b)

# --- Classe Plataforma Física ---
class Platform:
    def __init__(self, x, y, w=120, h=10):
        self.rect = Rect((x, y), (w, h))
        self.image = "platform"

    def draw(self):
        screen.blit(self.image, self.rect)

# --- Classe Player ---
class Player:
    def __init__(self, pos):
        self.actor = Actor('player_idle', pos)
        self.vx = 0
        self.vy = 0
        self.speed = 3
        self.gravity = 0.6
        self.jump_power = -12
        self.on_ground = False

        # Animações
        self.idle_frames = ['player_idle', 'player_run1']
        self.run_frames = ['player_run1', 'player_run2']
        self.anim_index = 0
        self.anim_timer = 0
        self.run_anim = False

    def get_rect(self):
        # Caixa de colisão do jogador
        return Rect((self.actor.left, self.actor.top), (self.actor.width, self.actor.height))

    def update(self, platforms):
        self.vx = 0
        self.run_anim = False

        if keyboard.left:
            self.vx = -self.speed
            self.run_anim = True
        elif keyboard.right:
            self.vx = self.speed
            self.run_anim = True

        # Pulo
        if keyboard.space and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False

        # Aplicar gravidade
        self.vy += self.gravity

        # Atualizar posição horizontal
        self.actor.x += self.vx

        # Atualizar posição vertical
        self.actor.y += self.vy

        self.on_ground = False
        player_rect = self.get_rect()

        # Verifica colisão com plataformas
        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                if self.vy > 0 and player_rect.bottom - self.vy <= platform.rect.top:
                    # Aterrissou na plataforma
                    self.actor.bottom = platform.rect.top
                    self.vy = 0
                    self.on_ground = True

        # Limites da tela
        if self.actor.left < 0:
            self.actor.left = 0
        if self.actor.right > WIDTH:
            self.actor.right = WIDTH
        if self.actor.bottom > HEIGHT:
            self.actor.bottom = HEIGHT
            self.vy = 0
            self.on_ground = True

        # Animação
        self.anim_timer += 1
        if self.run_anim:
            if self.anim_timer >= 5:
                self.anim_timer = 0
                self.anim_index = (self.anim_index + 1) % len(self.run_frames)
                self.actor.image = self.run_frames[self.anim_index]
        else:
            if self.anim_timer >= 10:
                self.anim_timer = 0
                self.anim_index = (self.anim_index + 1) % len(self.idle_frames)
                self.actor.image = self.idle_frames[self.anim_index]

    def draw(self):
        self.actor.draw()

# --- Classe Enemy ---
class Enemy:
    def __init__(self, pos):
        self.actor = Actor('enemy', pos)
        self.speed = random.randint(3, 6)
        self.anim_frames = ['enemy', 'enemy2']
        self.anim_index = 0
        self.anim_timer = 0

    def update(self):
        self.actor.x -= self.speed
        self.anim_timer += 1
        if self.anim_timer >= 10:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(self.anim_frames)
            self.actor.image = self.anim_frames[self.anim_index]

    def draw(self):
        self.actor.draw()

# --- Classe Button ---
class Button:
    def __init__(self, rect, color, text):
        self.rect = rect
        self.color = color
        self.text = text

    def draw(self):
        screen.draw.filled_rect(self.rect, self.color)
        screen.draw.text(self.text, center=self.rect.center, fontsize=30, color="white")

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# --- Classe Game ---
class Game:
    def __init__(self):
        self.player = Player((100, HEIGHT - 150))
        self.enemies = []
        self.game_started = False
        self.game_over = False
        self.level_complete = False
        self.start_time = 0

        # Plataformas
        self.platforms = [
            Platform(0, HEIGHT - 40, WIDTH, 40),  # chão
            Platform(150, HEIGHT - 120),
            Platform(320, HEIGHT - 200),
            Platform(500, HEIGHT - 280),
            Platform(650, HEIGHT - 350),
            Platform(450, HEIGHT - 400),
            Platform(280, HEIGHT - 430),
        ]

        # Botões
        self.start_button = Button(Rect(WIDTH // 2 - 100, HEIGHT // 2 - 75, 200, 50), (0, 255, 0), "Começar")
        self.music_button = Button(Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50), (0, 0, 255), "Música: ON")
        self.sound_button = Button(Rect(WIDTH // 2 - 100, HEIGHT // 2 + 75, 200, 50), (255, 255, 0), "Sons: OFF")
        self.exit_button = Button(Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 50), (255, 0, 0), "Sair")
        self.back_button = Button(Rect(10, 10, 120, 40), (200, 0, 0), "Menu")
        self.restart_button = Button(Rect(10, 60, 120, 40), (0, 150, 0), "Recomeçar")

    def spawn_enemy(self):
        y = random.randint(50, HEIGHT - 50)
        self.enemies.append(Enemy((WIDTH + 50, y)))


    def update(self):
        global is_sounds_on
        if self.game_started and not self.game_over and not self.level_complete:
            self.player.update(self.platforms)

            # Criar inimigos
            if random.randint(1, 100) == 1:
                self.spawn_enemy()

            # Atualizar inimigos
            for enemy in self.enemies:
                enemy.update()
            self.enemies[:] = [e for e in self.enemies if e.actor.right > 0]

            # Colisão
            for enemy in self.enemies:
                if is_collision(self.player.actor, enemy.actor, 25, 20):
                    self.game_over = True
                    if is_sounds_on:
                        sounds.hurt.play()
                    break

            # Verificar tempo sobrevivido
            elapsed = time.time() - self.start_time
            if elapsed >= survive_time:
                self.level_complete = True
                if is_sounds_on:
                    sounds.levelup.play()

    def draw(self):
        screen.clear()
        if self.game_started:
            background.draw()
            self.player.draw()
            for plat in self.platforms:
                plat.draw()
            for enemy in self.enemies:
                enemy.draw()

            # Menu no canto
            self.back_button.draw()
            self.restart_button.draw()


            # Cronômetro
            if not self.game_over and not self.level_complete:
                remaining = max(0, int(survive_time - (time.time() - self.start_time)))
                screen.draw.text(f"Falta: {remaining}s", topright=(WIDTH - 10, 10), fontsize=30, color="white")

            # Mensagens
            if self.game_over:
                screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="red")
            elif self.level_complete:
                screen.draw.text("NÍVEL COMPLETO!", center=(WIDTH//2, HEIGHT//2), fontsize=50, color="green")


        else:
            screen.fill((0, 0, 0))
            self.start_button.draw()
            self.music_button.draw()
            self.sound_button.draw()
            self.exit_button.draw()

# --- Funções auxiliares ---
def play_background_music():
    try:
        music.play(background_music)
    except Exception as e:
        print(f"Erro ao carregar a música: {e}")

# --- Instância do jogo ---
game = Game()
if is_music_on:
    play_background_music()

# --- Eventos ---
def on_mouse_down(pos, button):
    global is_music_on, is_sounds_on
    def play_click():
        if is_sounds_on:
            sounds.drum.play()

    if game.game_started:
        if game.back_button.is_clicked(pos):
            game.game_started = False
            game.game_over = False
            game.level_complete = False
            game.enemies.clear()
            play_click()

        elif game.restart_button.is_clicked(pos):
            game.__init__()  # Reinicia o jogo completamente
            game.game_started = True
            game.start_time = time.time()
            play_click()

    else:
        if game.start_button.is_clicked(pos):
            game.game_started = True
            game.game_over = False
            game.level_complete = False
            game.enemies.clear()
            game.start_time = time.time()
            play_click()
        elif game.music_button.is_clicked(pos):
            is_music_on = not is_music_on
            game.music_button.text = "Música: ON" if is_music_on else "Música: OFF"
            if is_music_on:
                play_background_music()
            else:
                music.stop()
            play_click()
        elif game.sound_button.is_clicked(pos):
            is_sounds_on = not is_sounds_on
            game.sound_button.text = "Sons: ON" if is_sounds_on else "Sons: OFF"
            play_click()
        elif game.exit_button.is_clicked(pos):
            play_click()
            exit()

# --- Loop principal ---
def update():
    game.update()

def draw():
    game.draw()

pgzrun.go()
