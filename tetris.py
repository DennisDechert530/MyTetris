import pygame
import random
import os

# Initialisiere Pygame
pygame.init()

# Spielfeld-Dimensionen
SCREEN_WIDTH = 450
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Farben definieren
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (30, 30, 30)
COLORS = [
    (0, 255, 255),  # Cyan (I-Stein)
    (0, 0, 255),    # Blau (J-Stein)
    (255, 165, 0),  # Orange (L-Stein)
    (255, 255, 0),  # Gelb (O-Stein)
    (0, 255, 0),    # Grün (S-Stein)
    (128, 0, 128),  # Lila (T-Stein)
    (255, 0, 0)     # Rot (Z-Stein)
]

# Tetris-Formen und Rotationen
SHAPES = [
    [[1, 5, 9, 13], [4, 5, 6, 7]], # I
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]], # J
    [[1, 2, 6, 10], [5, 6, 7, 4], [2, 6, 10, 11], [6, 5, 4, 8]], # L
    [[1, 2, 5, 6]], # O
    [[1, 2, 4, 5], [1, 5, 6, 10]], # S
    [[1, 4, 5, 6], [1, 5, 9, 6], [4, 5, 6, 9], [1, 4, 5, 9]], # T
    [[0, 1, 5, 6], [2, 5, 6, 9]] # Z
]

HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_highscore(score):
    current_high = load_highscore()
    if score > current_high:
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(score))
        except:
            pass

class Tetris:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.score = 0
        self.lines_cleared = 0  # NEU: Zählt die geräumten Linien
        self.highscore = load_highscore()
        self.game_over = False
        
        self.next_shape_idx = random.randint(0, len(SHAPES) - 1)
        self.next_color_idx = self.next_shape_idx + 1
        
        self.spawn_piece()

    def spawn_piece(self):
        self.shape_idx = self.next_shape_idx
        self.color_idx = self.next_color_idx
        self.rotation = 0
        self.x = 3
        self.y = 0
        
        self.next_shape_idx = random.randint(0, len(SHAPES) - 1)
        self.next_color_idx = self.next_shape_idx + 1

        if self.check_collision():
            self.game_over = True
            save_highscore(self.score)

    def image(self):
        return SHAPES[self.shape_idx][self.rotation]

    def next_image(self):
        return SHAPES[self.next_shape_idx][0]

    def check_collision(self):
        for i in self.image():
            row = i // 4 + self.y
            col = i % 4 + self.x
            if row >= self.height or col < 0 or col >= self.width or (row >= 0 and self.grid[row][col] > 0):
                return True
        return False

    def freeze(self, sound_effect=None):
        for i in self.image():
            row = i // 4 + self.y
            col = i % 4 + self.x
            if row >= 0:
                self.grid[row][col] = self.color_idx
        
        if sound_effect:
            sound_effect.play()
            
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        lines_to_clear = []
        for row in range(self.height):
            if all(self.grid[row][col] > 0 for col in range(self.width)):
                lines_to_clear.append(row)
        
        for row in lines_to_clear:
            del self.grid[row]
            self.grid.insert(0, [0 for _ in range(self.width)])
            self.score += 100
            self.lines_cleared += 1  # Linienzähler erhöhen
        
        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

    def move_horizontally(self, dx):
        self.x += dx
        if self.check_collision():
            self.x -= dx

    def move_down(self, sound_effect=None):
        self.y += 1
        if self.check_collision():
            self.y -= 1
            self.freeze(sound_effect)

    def rotate(self):
        old_rotation = self.rotation
        self.rotation = (self.rotation + 1) % len(SHAPES[self.shape_idx])
        if self.check_collision():
            self.rotation = old_rotation

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris - Dynamischer Schwierigkeitsgrad")
    clock = pygame.time.Clock()
    fps = 30

    try:
        pygame.mixer.music.load("background.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.4)
    except pygame.error:
        pass

    plop_sound = None
    try:
        plop_sound = pygame.mixer.Sound("plop.wav")
        plop_sound.set_volume(0.6)
    except pygame.error:
        pass

    game = Tetris(GRID_HEIGHT, GRID_WIDTH)
    counter = 0

    font = pygame.font.SysFont("Arial", 18)
    font_bold = pygame.font.SysFont("Arial", 22, bold=True)

    running = True
    while running:
        # --- DYNAMISCHE GESCHWINDIGKEIT BERECHNEN ---
        # Startet bei 15 Frames pro Fall. Alle 3 geräumten Linien wird der Wert um 2 kleiner (= schneller).
        # Maximales Tempo stoppt bei 3 Frames, damit es spielbar bleibt.
        fall_speed = max(3, 15 - (game.lines_cleared // 3) * 2)
        current_level = (game.lines_cleared // 3) + 1

        counter += 1
        if counter >= fall_speed and not game.game_over:
            game.move_down(plop_sound)
            counter = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_r:
                        game = Tetris(GRID_HEIGHT, GRID_WIDTH)
                else:
                    if event.key == pygame.K_LEFT:
                        game.move_horizontally(-1)
                    elif event.key == pygame.K_RIGHT:
                        game.move_horizontally(1)
                    elif event.key == pygame.K_DOWN:
                        game.move_down(plop_sound)
                    elif event.key == pygame.K_UP:
                        game.rotate()

        screen.fill(BLACK)

        # Spielfeld zeichnen
        for row in range(game.height):
            for col in range(game.width):
                if game.grid[row][col] > 0:
                    color = COLORS[game.grid[row][col] - 1]
                    pygame.draw.rect(screen, color, (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Aktiven Stein zeichnen
        if not game.game_over:
            for i in game.image():
                row = i // 4 + game.y
                col = i % 4 + game.x
                if row >= 0:
                    color = COLORS[game.color_idx - 1]
                    pygame.draw.rect(screen, color, (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # --- SEITENLEISTE (Level, Highscore, Punkte & Vorschau) ---
        pygame.draw.rect(screen, DARK_GRAY, (300, 0, 150, SCREEN_HEIGHT))
        
        # Level anzeigen
        level_label = font.render("Level:", True, WHITE)
        level_val = font_bold.render(str(current_level), True, (0, 255, 255)) # Cyan
        screen.blit(level_label, (315, 15))
        screen.blit(level_val, (315, 40))

        # Highscore anzeigen
        high_label = font.render("Highscore:", True, WHITE)
        high_val = font_bold.render(str(game.highscore), True, (255, 215, 0))
        screen.blit(high_label, (315, 80))
        screen.blit(high_val, (315, 110))

        # Aktuelle Punkte anzeigen
        score_label = font.render("Punkte:", True, WHITE)
        score_val = font_bold.render(str(game.score), True, (0, 255, 0))
        screen.blit(score_label, (315, 150))
        screen.blit(score_val, (315, 180))

        # Nächster Stein
        next_label = font.render("Nächster:", True, WHITE)
        screen.blit(next_label, (315, 230))

        next_color = COLORS[game.next_color_idx - 1]
        for i in game.next_image():
            r = i // 4
            c = i % 4
            pygame.draw.rect(screen, next_color, (325 + c * 20, 270 + r * 20, 19, 19))

        # --- GAME OVER BILDSCHIRM ---
        if game.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(220)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            go_text = font_bold.render("GAME OVER", True, (255, 0, 0))
            score_text = font.render(f"Punkte: {game.score}", True, WHITE)
            high_text = font.render(f"Highscore: {game.highscore}", True, (255, 215, 0))
            restart_text = font.render("Drücke 'R' zum Neustarten", True, GRAY)

            screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            screen.blit(high_text, (SCREEN_WIDTH // 2 - high_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(fps)

    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()