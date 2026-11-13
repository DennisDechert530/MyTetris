import pygame
import random

# Initialisiere Pygame (startet die Spiel-Engine)
pygame.init()

# Spielfeld-Dimensionen und Blockgröße
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Farben definieren (RGB-Farbwerte)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # Cyan (I-Stein)
    (0, 0, 255),    # Blau (J-Stein)
    (255, 165, 0),  # Orange (L-Stein)
    (255, 255, 0),  # Gelb (O-Stein)
    (0, 255, 0),    # Grün (S-Stein)
    (128, 0, 128),  # Lila (T-Stein)
    (255, 0, 0)     # Rot (Z-Stein)
]

# Die verschiedenen Tetris-Formen und ihre Rotationen
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
        # Erstellt ein leeres Spielfeld (Matrix voller Nullen)
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.score = 0
        self.game_over = False
        self.spawn_piece()

    def spawn_piece(self):
        """Erschafft einen neuen zufälligen Spielstein oben in der Mitte"""
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.color_idx = self.shape_idx + 1
        self.rotation = 0
        self.x = 3
        self.y = 0
        # Wenn direkt beim Erscheinen kein Platz mehr ist, ist das Spiel vorbei
        if self.check_collision():
            self.game_over = True

    def image(self):
        """Gibt die aktuelle Form und Rotation des Steins zurück"""
        return SHAPES[self.shape_idx][self.rotation]

    def check_collision(self):
        """Prüft, ob der aktuelle Stein mit Wänden oder anderen Blöcken kollidiert"""
        for i in self.image():
            row = i // 4 + self.y
            col = i % 4 + self.x
            if row >= self.height or col < 0 or col >= self.width or (row >= 0 and self.grid[row][col] > 0):
                return True
        return False

    def freeze(self):
        """Lässt den Stein am Boden festrosten und prüft volle Reihen"""
        for i in self.image():
            row = i // 4 + self.y
            col = i % 4 + self.x
            if row >= 0:
                self.grid[row][col] = self.color_idx
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        """Löscht volle Reihen und erhöht den Punktestand"""
        lines_to_clear = []
        for row in range(self.height):
            if all(self.grid[row][col] > 0 for col in range(self.width)):
                lines_to_clear.append(row)
        
        for row in lines_to_clear:
            del self.grid[row]
            self.grid.insert(0, [0 for _ in range(self.width)])
            self.score += 100

    def move_horizontally(self, dx):
        """Bewegt den Stein nach links oder rechts"""
        self.x += dx
        if self.check_collision():
            self.x -= dx

    def move_down(self):
        """Lässt den Stein einen Schritt nach unten fallen"""
        self.y += 1
        if self.check_collision():
            self.y -= 1
            self.freeze()

    def rotate(self):
        """Dreht den Spielstein"""
        old_rotation = self.rotation
        self.rotation = (self.rotation + 1) % len(SHAPES[self.shape_idx])
        if self.check_collision():
            self.rotation = old_rotation

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mein erstes Tetris")
    clock = pygame.time.Clock()
    fps = 30

    try:
        pygame.mixer.music.load("background_music.wav")
        pygame.mixer.music.play(-1)  # Das '-1' sorgt dafür, dass die Musik in einer Endlosschleife läuft
        pygame.mixer.music.set_volume(0.5)  # Lautstärke auf 50% setzen (Wert von 0.0 bis 1.0)
    except pygame.error:
        print("Hinweis: 'background_music.wav' wurde nicht gefunden. Das Spiel läuft ohne Musik.")



    game = Tetris(GRID_HEIGHT, GRID_WIDTH)
    counter = 0
    fall_speed = 15 # Steuert die Fallgeschwindigkeit (höher = langsamer)

    running = True
    while running:
        counter += 1
        if counter >= fall_speed and not game.game_over:
            game.move_down()
            counter = 0

        # Tastatur-Eingaben verarbeiten
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and not game.game_over:
                if event.key == pygame.K_LEFT:
                    game.move_horizontally(-1)
                elif event.key == pygame.K_RIGHT:
                    game.move_horizontally(1)
                elif event.key == pygame.K_DOWN:
                    game.move_down()
                elif event.key == pygame.K_UP:
                    game.rotate()

        screen.fill(BLACK)

        # Festgeklebte Blöcke auf dem Spielfeld zeichnen
        for row in range(game.height):
            for col in range(game.width):
                if game.grid[row][col] > 0:
                    color = COLORS[game.grid[row][col] - 1]
                    pygame.draw.rect(screen, color, (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Aktuell fallenden Stein zeichnen
        if not game.game_over:
            for i in game.image():
                row = i // 4 + game.y
                col = i % 4 + game.x
                if row >= 0:
                    color = COLORS[game.color_idx - 1]
                    pygame.draw.rect(screen, color, (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        pygame.display.flip()
        clock.tick(fps)
    # Wenn die While-Schleife endet (Spieler schließt das Fenster):
    pygame.mixer.music.stop() # Musik stoppen
    pygame.quit()

if __name__ == "__main__":
    main()