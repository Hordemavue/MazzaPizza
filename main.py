import pygame
import random
import sys
import os
import time

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
tile_theme = "rip"  # rip | ping | ok
game_timer_mode = "inf"  # "inf" | "1min" | "3min"


def resource_path(relative_path):
    """Récupère le chemin correct pour les fichiers embarqués PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Charger images V1
tile_images_v1 = {}
for value in [2,4,8,16,32,64,128,256,512,1024,2048,4096,8192]:
    path = resource_path(f"v1_{value}.png")
    if os.path.exists(path):
        tile_images_v1[value] = pygame.image.load(path)

# Charger images V2
tile_images_v2 = {}
for value in [2,4,8,16,32,64,128,256,512,1024,2048,4096,8192]:
    path = resource_path(f"v2_{value}.png")
    if os.path.exists(path):
        tile_images_v2[value] = pygame.image.load(path)

# Charger images V3
tile_images_v3 = {}
for value in [2,4,8,16,32,64,128,256,512,1024,2048,4096,8192]:
    path = resource_path(f"v3_{value}.png")
    if os.path.exists(path):
        tile_images_v3[value] = pygame.image.load(path)

TILE_IMAGE_SETS = {
    "rip": tile_images_v1,
    "ping": tile_images_v2,
    "ok": tile_images_v3
}

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
    jouer_btn = Button("Jouer", LARGEUR//2-85, 300, 170, 50)
    param_btn = Button("Paramètres", LARGEUR//2-85, 370, 170, 50)

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
    global tile_theme
    global game_timer_mode

    back_btn = Button("←", 10, 10, 120, 40)

    # --- Images difficulté ---
    difficulty_images = {}

    pince_path = resource_path("pince.png")
    if os.path.exists(pince_path):
        difficulty_images["pince"] = pygame.transform.scale(
            pygame.image.load(pince_path), (80, 80)
        )

    main_path = resource_path("main.png")
    if os.path.exists(main_path):
        difficulty_images["main"] = pygame.transform.scale(
            pygame.image.load(main_path), (80, 80)
        )

    # Valeurs par défaut
    if "game_difficulty" not in globals():
        game_difficulty = "main"
    if "tile_theme" not in globals():
        tile_theme = "rip"

    # --- Rectangles difficulté ---
    pince_rect = pygame.Rect(LARGEUR // 2 - 100, 150, 80, 80)
    main_rect  = pygame.Rect(LARGEUR // 2 + 20, 150, 80, 80)

    # --- Rectangles thèmes ---
    rip_rect  = pygame.Rect(LARGEUR // 2 - 140, 310, 80, 36)
    ping_rect = pygame.Rect(LARGEUR // 2 - 40,  310, 80, 36)
    ok_rect   = pygame.Rect(LARGEUR // 2 + 60,  310, 80, 36)

    # --- Rectangles timer ---
    timer_inf_rect = pygame.Rect(LARGEUR // 2 - 140, 400, 80, 36)
    timer_1_rect   = pygame.Rect(LARGEUR // 2 - 40,  400, 80, 36)
    timer_3_rect   = pygame.Rect(LARGEUR // 2 + 60,  400, 80, 36)

    def draw_option(rect, label, selected):
        color = (180, 255, 180) if selected else (205, 193, 180)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        txt = BUTTON_FONT.render(label, True, (0, 0, 0))
        screen.blit(txt, txt.get_rect(center=rect.center))

    while True:
        screen.fill(FOND)
        back_btn.draw()

        # Titre
        surf = TITLE_FONT.render("Paramètres", True, SCORE_COLOR)
        screen.blit(surf, surf.get_rect(center=(LARGEUR // 2, 60)))

        # --- Difficulté ---
        diff_text = TITLE_FONT.render("Difficulté :", True, SCORE_COLOR)
        screen.blit(diff_text, (LARGEUR // 2 - 100, 120))

        if "pince" in difficulty_images:
            screen.blit(difficulty_images["pince"], pince_rect.topleft)
            if game_difficulty == "pince":
                pygame.draw.rect(screen, (0, 255, 0), pince_rect, 3)

        if "main" in difficulty_images:
            screen.blit(difficulty_images["main"], main_rect.topleft)
            if game_difficulty == "main":
                pygame.draw.rect(screen, (0, 255, 0), main_rect, 3)

        # --- Thème des images ---
        img_text = TITLE_FONT.render("Thèmes :", True, SCORE_COLOR)
        screen.blit(img_text, (LARGEUR // 2 - 100, 270))

        draw_option(rip_rect,  "RIP",  tile_theme == "rip")
        draw_option(ping_rect, "PING", tile_theme == "ping")
        draw_option(ok_rect,   "OK",   tile_theme == "ok")


        # --- Timer ---
        timer_text = TITLE_FONT.render("Timer :", True, SCORE_COLOR)
        screen.blit(timer_text, (LARGEUR // 2 - 100, 360))

        draw_option(timer_inf_rect, "∞",   game_timer_mode == "inf")
        draw_option(timer_1_rect,   "1min", game_timer_mode == "1min")
        draw_option(timer_3_rect,   "3min", game_timer_mode == "3min")

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
                elif rip_rect.collidepoint(event.pos):
                    tile_theme = "rip"
                elif ping_rect.collidepoint(event.pos):
                    tile_theme = "ping"
                elif ok_rect.collidepoint(event.pos):
                    tile_theme = "ok"
                elif timer_inf_rect.collidepoint(event.pos):
                    game_timer_mode = "inf"
                elif timer_1_rect.collidepoint(event.pos):
                    game_timer_mode = "1min"
                elif timer_3_rect.collidepoint(event.pos):
                    game_timer_mode = "3min"

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
    global game_timer_mode

    import time

    clock = pygame.time.Clock()

    board = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
    score = 0
    next_tile = 2

    # --- TIMER ---
    timer_started = False
    timer_start_time = None

    if game_timer_mode == "1min":
        timer_duration = 60
    elif game_timer_mode == "3min":
        timer_duration = 180
    else:
        timer_duration = None  # ∞

    def add_random_tile():
        nonlocal next_tile
        empty = [(i,j) for i in range(GRID_SIZE) for j in range(GRID_SIZE) if board[i][j] == 0]
        if empty:
            i,j = random.choice(empty)
            board[i][j] = next_tile
            next_tile = 2 if random.random() < 0.9 else 4

    def draw_timer():
        if timer_duration is None or not timer_started:
            return

        elapsed = int(time.time() - timer_start_time)
        remaining = max(0, timer_duration - elapsed)

        minutes = remaining // 60
        seconds = remaining % 60

        timer_surf = FONT.render(f"{minutes:02d}:{seconds:02d}", True, SCORE_COLOR)
        screen.blit(timer_surf, (LARGEUR // 2 - 30, 10))

        if remaining <= 0:
            end_game()

    def draw_board():
        screen.fill(FOND)
        images = TILE_IMAGE_SETS.get(tile_theme, tile_images_v1)

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                rect = pygame.Rect(
                    MARGE + j * (TAILLE_TILE + MARGE),
                    MARGE + i * (TAILLE_TILE + MARGE) + 50,
                    TAILLE_TILE,
                    TAILLE_TILE
                )
                pygame.draw.rect(screen, (205, 193, 180), rect, border_radius=10)

                value = board[i][j]
                if value != 0 and value in images:
                    img = pygame.transform.scale(images[value], (TAILLE_TILE, TAILLE_TILE))
                    screen.blit(img, rect.topleft)

        score_surface = FONT.render(f"Score: {score}", True, SCORE_COLOR)
        screen.blit(score_surface, (MARGE, 10))

        if game_difficulty == "pince":
            if next_tile in images:
                img = pygame.transform.scale(images[next_tile], (TAILLE_TILE//2, TAILLE_TILE//2))
                screen.blit(img, (LARGEUR - TAILLE_TILE//2 - 10, 5))

        draw_timer()
        pygame.display.update()

    def slide(row):
        global score
        new_row = [v for v in row if v != 0]
        i = 0
        while i < len(new_row) - 1:
            if new_row[i] == new_row[i + 1]:
                new_row[i] *= 2
                score += new_row[i]
                new_row.pop(i + 1)
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
            draw_text_outline(screen, f"T'es nulle: {score}", TITLE_FONT,
                              LARGEUR//2, HAUTEUR//2 - 20, SCORE_COLOR, (255,255,255), 2)
            draw_text_outline(screen, "Appuie sur espace connasse", TITLE_FONT,
                              LARGEUR//2, HAUTEUR//2 + 20, SCORE_COLOR, (255,255,255), 2)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
        menu()

    add_random_tile()
    add_random_tile()

    # --- BOUCLE PRINCIPALE ---
    while True:
        clock.tick(60)  # 60 FPS → timer fluide

        draw_board()  # redraw permanent pour le timer

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                moved = False

                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    if not timer_started and timer_duration is not None:
                        timer_started = True
                        timer_start_time = time.time()

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
                    if is_game_over():
                        end_game()

# --- LANCEMENT ---
menu()
