import pygame
import random
import sys
import os

# --- CONFIGURATION ---
pygame.init()
TAILLE_TILE = 100
MARGE = 10
GRID_SIZE = 4
LARGEUR = GRID_SIZE * TAILLE_TILE + (GRID_SIZE + 1) * MARGE
HAUTEUR = LARGEUR + 50  # espace pour le score
FOND = (250, 248, 239)
SCORE_COLOR = (0, 0, 0)
FONT = pygame.font.SysFont("Arial", 30, bold=True)
TITLE_FONT = pygame.font.SysFont("Arial", 24, bold=True)
BUTTON_FONT = pygame.font.SysFont("Arial", 28, bold=True)
game_difficulty = "main"


def resource_path(relative_path):
    """Récupère le chemin correct pour les fichiers embarqués PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Charger images
tile_images = {}
for value in [2,4,8,16,32,64,128,256,512,1024,2048,4096,8192]:
    path = resource_path(f"{value}.png")
    if os.path.exists(path):
        tile_images[value] = pygame.image.load(path)

screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Mazapizza")

# --- BOUTONS ---
class Button:
    def __init__(self, text, x, y, w, h, color=(205,193,180), hover=(170,170,170)):
        self.rect = pygame.Rect(x,y,w,h)
        self.text = text
        self.color = color
        self.hover = hover
    def draw(self):
        mpos = pygame.mouse.get_pos()
        col = self.hover if self.rect.collidepoint(mpos) else self.color
        pygame.draw.rect(screen, col, self.rect, border_radius=10)
        surf = BUTTON_FONT.render(self.text, True, (0,0,0))
        screen.blit(surf, surf.get_rect(center=self.rect.center))
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# --- MENU ---
def menu():
    jouer_btn = Button("Jouer", LARGEUR//2-75, 300, 150, 50)
    param_btn = Button("Paramètre", LARGEUR//2-75, 370, 150, 50)

    while True:
        screen.fill(FOND)
        lines = [
            "La vilaine Mazapizza ",
            "a décortiqué Craby",
            "pour le mettre sur sa pizza,",
            "reconstitue-le afin de le sauver ..."
        ]
        for idx, line in enumerate(lines):
            surf = TITLE_FONT.render(line, True, (119,110,101))
            screen.blit(surf, surf.get_rect(center=(LARGEUR//2, 100+idx*30)))
        
        for btn in [jouer_btn, param_btn]:
            btn.draw()
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if jouer_btn.is_clicked(event):
                game_loop()
                return
            if param_btn.is_clicked(event):
                parameters()
                return

# --- PARAMÈTRES ---
def parameters():
    global game_difficulty
    back_btn = Button("←", 10, 10, 120, 40)

    # Charger images pour la difficulté
    difficulty_images = {}
    pince_path = resource_path("pince.png")
    if os.path.exists(pince_path):
        difficulty_images["pince"] = pygame.transform.scale(pygame.image.load(pince_path), (80, 80))

    main_path = resource_path("main.png")
    if os.path.exists(main_path):
        difficulty_images["main"] = pygame.transform.scale(pygame.image.load(main_path), (80, 80))

    # Utiliser la difficulté actuelle comme sélection
    if "game_difficulty" not in globals():
        game_difficulty = "main"

    # Rectangles pour clic
    pince_rect = pygame.Rect(LARGEUR//2 - 100, 150, 80, 80)
    main_rect = pygame.Rect(LARGEUR//2 + 20, 150, 80, 80)

    while True:
        screen.fill(FOND)
        back_btn.draw()
        surf = TITLE_FONT.render("Paramètres", True, SCORE_COLOR)
        screen.blit(surf, surf.get_rect(center=(LARGEUR//2, 60)))

        # Afficher le texte "Difficulté"
        diff_text = TITLE_FONT.render("Difficulté :", True, SCORE_COLOR)
        screen.blit(diff_text, (LARGEUR//2 - 100, 120))

        # Afficher images avec bordure verte sur la sélection actuelle
        if "pince" in difficulty_images:
            screen.blit(difficulty_images["pince"], pince_rect.topleft)
            if game_difficulty == "pince":
                pygame.draw.rect(screen, (0,255,0), pince_rect, 3)
        if "main" in difficulty_images:
            screen.blit(difficulty_images["main"], main_rect.topleft)
            if game_difficulty == "main":
                pygame.draw.rect(screen, (0,255,0), main_rect, 3)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if back_btn.is_clicked(event):
                menu()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pince_rect.collidepoint(event.pos):
                    game_difficulty = "pince"
                elif main_rect.collidepoint(event.pos):
                    game_difficulty = "main"

def draw_text_outline(surface, text, font, x, y, text_color, outline_color, outline_width=2):
    base = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)

    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                surface.blit(
                    outline,
                    outline.get_rect(center=(x + dx, y + dy))
                )

    surface.blit(base, base.get_rect(center=(x, y)))

# --- JEU 2048 ---
def game_loop():
    global score
    global game_difficulty
    board = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
    score = 0
    next_tile = 2  # première tuile aléatoire

    def add_random_tile():
        nonlocal next_tile
        empty = [(i,j) for i in range(GRID_SIZE) for j in range(GRID_SIZE) if board[i][j]==0]
        if empty:
            i,j = random.choice(empty)
            board[i][j] = next_tile
            next_tile = 2 if random.random() < 0.9 else 4  # prochaine tuile

    def draw_board():
        screen.fill(FOND)
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                rect = pygame.Rect(MARGE + j*(TAILLE_TILE+MARGE),
                                   MARGE + i*(TAILLE_TILE+MARGE) + 50,
                                   TAILLE_TILE, TAILLE_TILE)
                pygame.draw.rect(screen, (205,193,180), rect, border_radius=10)
                if board[i][j] != 0 and board[i][j] in tile_images:
                    img = pygame.transform.scale(tile_images[board[i][j]], (TAILLE_TILE, TAILLE_TILE))
                    screen.blit(img, rect.topleft)
        score_surface = FONT.render(f"Score: {score}", True, SCORE_COLOR)
        screen.blit(score_surface, (MARGE, 10))

        # Afficher prochaine tuile si difficulté "pince"
        if game_difficulty == "pince":
            if next_tile in tile_images:
                img = pygame.transform.scale(tile_images[next_tile], (TAILLE_TILE//2, TAILLE_TILE//2))
                screen.blit(img, (LARGEUR - TAILLE_TILE//2 - 10, 5))
        pygame.display.update()

    def slide(row):
        global score
        new_row = [v for v in row if v != 0]
        i = 0
        while i < len(new_row)-1:
            if new_row[i] == new_row[i+1]:
                new_row[i] *= 2
                score += new_row[i]
                new_row.pop(i+1)
            i += 1
        return new_row + [0]*(GRID_SIZE - len(new_row))

    def move_left():
        changed = False
        new_board = []
        for row in board:
            new_row = slide(row)
            if new_row != row:
                changed = True
            new_board.append(new_row)
        return changed, new_board

    def move_right():
        changed = False
        new_board = []
        for row in board:
            new_row = list(reversed(slide(list(reversed(row)))))
            if new_row != row:
                changed = True
            new_board.append(new_row)
        return changed, new_board

    def move_up():
        changed = False
        new_board = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        for j in range(GRID_SIZE):
            col = slide([board[i][j] for i in range(GRID_SIZE)])
            for i in range(GRID_SIZE):
                new_board[i][j] = col[i]
            if col != [board[i][j] for i in range(GRID_SIZE)]:
                changed = True
        return changed, new_board

    def move_down():
        changed = False
        new_board = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        for j in range(GRID_SIZE):
            col = list(reversed(slide([board[i][j] for i in reversed(range(GRID_SIZE))])))
            for i in range(GRID_SIZE):
                new_board[i][j] = col[i]
            if col != [board[i][j] for i in range(GRID_SIZE)]:
                changed = True
        return changed, new_board

    def is_game_over():
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if board[i][j] == 0:
                    return False
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if i < GRID_SIZE-1 and board[i][j] == board[i+1][j]:
                    return False
                if j < GRID_SIZE-1 and board[i][j] == board[i][j+1]:
                    return False
        return True

    def end_game():
        waiting = True

        while waiting:

            draw_text_outline(screen,f"T'es nulle: {score}",TITLE_FONT,LARGEUR//2,HAUTEUR//2 - 20,SCORE_COLOR,(255, 255, 255),2)

            draw_text_outline(screen,"Appuie sur espace connasse",TITLE_FONT,LARGEUR//2,HAUTEUR//2 + 20,SCORE_COLOR,(255, 255, 255),2)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False

        menu()

    add_random_tile()
    add_random_tile()
    draw_board()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                moved = False
                if event.key == pygame.K_LEFT:
                    moved, new_board = move_left()
                elif event.key == pygame.K_RIGHT:
                    moved, new_board = move_right()
                elif event.key == pygame.K_UP:
                    moved, new_board = move_up()
                elif event.key == pygame.K_DOWN:
                    moved, new_board = move_down()
                if moved:
                    board[:] = new_board
                    add_random_tile()
                    draw_board()
                    if is_game_over():
                        end_game()

# --- LANCEMENT ---
menu()
