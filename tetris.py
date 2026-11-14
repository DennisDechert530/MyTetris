import pygame
import random

# Initialisiere Pygame
pygame.init()

# Spielfeld-Dimensionen (etwas breiter für die Seitenleiste der Vorschau)
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

class Tetris:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.score = 0
        self.game_over = False
        
        # Nächsten Stein vorbereiten
        self.next_shape_idx = random.randint(0, len(SHAPES) - 1)
        self.next_color_idx = self.next_shape_idx + 1
        
        self.spawn_piece()

    def spawn_piece(self):
        """Bringt den nächsten Stein ins Spiel und generiert einen neuen Vorschau-Stein"""
        self.shape_idx = self.next_shape_idx
        self.color_idx = self.next_color_idx
        self.rotation = 0
        self.x = 3
        self.y = 0
        
        # Neuen nächsten Stein bestimmen
        self.next_shape_idx = random.randint(0, len(SHAPES) - 1)
        self.next_color_idx = self.next_shape_idx + 1

        if self.check_collision():
            self.game_over = True

    def image(self):
        return SHAPES[self.shape_idx][self.rotation]

    def next_image(self):
        """Gibt die Form für die Vorschau zurück"""
        return SHAPES[self.next_shape_idx][0]

    def check_collision(self):
        for i in self.image():
            row = i // 4 + self.y
            col = i % 4 + self.x
            if row >= self.height or col < 0 or col >= self.width or (row >= 0 and self.grid[row][col] > 0):
                return True
        return False

    def freeze(self, sound_effect=None):
        """Lässt den Stein festrosten, spielt Sound und prüft Zeilen"""
        for i in self.image():
            row = i // 4 + self.y
            col = i % 4 + self.x
            if row >= 0:
                self.grid[row][col] = self.color_idx
        
        # Soundeffekt abspielen, falls vorhanden
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
    pygame.display.set_caption("Mein Tetris - Feature Update")
    clock = pygame.time.Clock()
    fps = 30

    # Hintergrundmusik laden
    try:
        pygame.mixer.music.load("background.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.4)
    except pygame.error:
        pass

    # Soundeffekt (Plopp) laden
    plop_sound = None
    try:
        plop_sound = pygame.mixer.Sound("plop.wav")
        plop_sound.set_volume(0.6)
    except pygame.error:
        print("Hinweis: 'plop.wav' nicht gefunden. Spiel läuft ohne Soundeffekt.")

    game = Tetris(GRID_HEIGHT, GRID_WIDTH)
    counter = 0
    fall_speed = 15

    # Fonts für UI
    font = pygame.font.SysFont("Arial", 18)
    font_bold = pygame.font.SysFont("Arial", 22, bold=True)

    running = True
    while running:
        counter += 1
        if counter >= fall_speed and not game.game_over:
            game.move_down(plop_sound)
            counter = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_RKEY if hasattr(pygame, 'K_RKEY') else event.key == pygame.K_r:
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

        # Spielfeld-Blöcke zeichnen
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

        # --- SEITENLEISTE (Vorschau & Punkte) ---
        pygame.draw.rect(screen, DARK_GRAY, (300, 0, 150, SCREEN_HEIGHT))
        
        # Punktestand anzeigen
        score_label = font.render("Punkte:", True, WHITE)
        score_val = font_bold.render(str(game.score), True, (0, 255, 0))
        screen.blit(score_label, (315, 30))
        screen.blit(score_val, (315, 60))

        # Nächsten Stein anzeigen
        next_label = font.render("Nächster:", True, WHITE)
        screen.blit(next_label, (315, 130))

        next_color = COLORS[game.next_color_idx - 1]
        for i in game.next_image():
            r = i // 4
            c = i % 4
            pygame.draw.rect(screen, next_color, (325 + c * 20, 170 + r * 20, 19, 19))

        # --- GAME OVER BILDSCHIRM ---
        if game.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(220)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            go_text = font_bold.render("GAME OVER", True, (255, 0, 0))
            score_text = font.render(f"Punkte: {game.score}", True, WHITE)
            restart_text = font.render("Drücke 'R' zum Neustarten", True, GRAY)

            screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

        pygame.display.flip()
        clock.tick(fps)

    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()