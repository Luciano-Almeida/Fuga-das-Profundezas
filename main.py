import math
import pgzrun
from pygame import Rect
import random
import time

# --- Tamanho da tela ---
background = Actor('background')  # background.png
WIDTH = background.width
HEIGHT = background.height

# --- Variáveis globais ---
is_music_on = True
is_sounds_on = False
background_music = 'bolhas'  # nome da música
survive_time = 30  # segundos para passar de nível

# --- Função de colisão ---
def is_collision(a, b, radius_a=20, radius_b=20):
    dx = a.x - b.x
    dy = a.y - b.y
    distance = math.hypot(dx, dy)
    return distance < (radius_a + radius_b)

# --- Classe Player ---
class Player:
    def __init__(self, pos):
        self.actor = Actor('player_idle', pos)
        self.vx = 0
        self.vy = 0
        self.speed = 5
        self.idle_frames = ['player_idle', 'player_run1']
        self.run_frames = ['player_run1', 'player_run2']
        self.anim_index = 0
        self.anim_timer = 0
        self.run_anim = False

    def update(self):
        self.vx = self.vy = 0
        self.run_anim = False

        if keyboard.left:
            self.vx = -self.speed
            self.run_anim = True
        elif keyboard.right:
            self.vx = self.speed
            self.run_anim = True

        if keyboard.up:
            self.vy = -self.speed
        elif keyboard.down:
            self.vy = self.speed

        self.actor.x += self.vx
        self.actor.y += self.vy

        # Limites da tela
        self.actor.left = max(self.actor.left, 0)
        self.actor.right = min(self.actor.right, WIDTH)
        self.actor.top = max(self.actor.top, 0)
        self.actor.bottom = min(self.actor.bottom, HEIGHT)

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
        self.player = Player((WIDTH // 2, HEIGHT // 2))
        self.enemies = []
        self.game_started = False
        self.game_over = False
        self.level_complete = False
        self.start_time = 0

        # Botões
        self.start_button = Button(Rect(WIDTH // 2 - 100, HEIGHT // 2 - 75, 200, 50), (0, 255, 0), "Começar")
        self.music_button = Button(Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50), (0, 0, 255), "Música: ON")
        self.sound_button = Button(Rect(WIDTH // 2 - 100, HEIGHT // 2 + 75, 200, 50), (255, 255, 0), "Sons: OFF")
        self.exit_button = Button(Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 50), (255, 0, 0), "Sair")
        self.back_button = Button(Rect(10, 10, 120, 40), (200, 0, 0), "Menu")

    def spawn_enemy(self):
        y = random.randint(50, HEIGHT - 50)
        self.enemies.append(Enemy((WIDTH + 50, y)))

    def update(self):
        global is_sounds_on
        if self.game_started and not self.game_over and not self.level_complete:
            self.player.update()

            # Criar inimigos
            if random.randint(1, 50) == 1:
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
            for enemy in self.enemies:
                enemy.draw()

            # Menu no canto
            self.back_button.draw()

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

def update():
    game.update()

def draw():
    game.draw()

pgzrun.go()
