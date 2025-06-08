import pygame
import sys
from logic import GameLogic, Ball
import random

# --- Настройки ---
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 30
START_BALLS = 70
INVENTORY_SIZE = 5
DELETE_ZONE = (WIDTH - 120, HEIGHT - 120, 100, 100)  # x, y, w, h
FPS = 60

# --- Цвета ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 80, 80)

# --- Инициализация ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Шарики: игра")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# --- Логика ---
game = GameLogic(WIDTH, HEIGHT, DELETE_ZONE)

# Случайные цвета для стартовых шариков
def random_color():
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

for _ in range(START_BALLS):
    x = random.randint(BALL_RADIUS, WIDTH - BALL_RADIUS - 130)
    y = random.randint(BALL_RADIUS, HEIGHT - BALL_RADIUS - 130)
    game.spawn_ball(x, y, BALL_RADIUS, random_color())

# --- Вспомогательные функции ---
def draw_ball(ball: Ball):
    pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), int(ball.radius))
    pygame.draw.circle(screen, BLACK, (int(ball.x), int(ball.y)), int(ball.radius), 2)

def draw_inventory(inv, selected_idx=None):
    inv_x, inv_y = 20, HEIGHT - 80
    cell_size = 60
    for i in range(INVENTORY_SIZE):
        rect = pygame.Rect(inv_x + i*cell_size, inv_y, cell_size, cell_size)
        pygame.draw.rect(screen, GRAY if i != selected_idx else RED, rect, 3)
        if i < len(inv.balls):
            b = inv.balls[i]
            pygame.draw.circle(screen, b.color, rect.center, int(b.radius*0.7))
            pygame.draw.circle(screen, BLACK, rect.center, int(b.radius*0.7), 2)
    txt = font.render("Инвентарь", True, BLACK)
    screen.blit(txt, (inv_x, inv_y - 28))

def draw_delete_zone():
    x, y, w, h = DELETE_ZONE
    pygame.draw.rect(screen, (255, 180, 180), (x, y, w, h))
    pygame.draw.rect(screen, RED, (x, y, w, h), 3)
    txt = font.render("Удалить", True, RED)
    screen.blit(txt, (x + 10, y + h//2 - 12))

if __name__ == "__main__":
    # --- Основной цикл ---
    selected_inv_idx = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Проверка нажатия на инвентарь
                inv_x, inv_y = 20, HEIGHT - 80
                cell_size = 60
                for i in range(INVENTORY_SIZE):
                    rect = pygame.Rect(inv_x + i*cell_size, inv_y, cell_size, cell_size)
                    if rect.collidepoint(mx, my):
                        if i < len(game.inventory.balls):
                            selected_inv_idx = i
                        else:
                            selected_inv_idx = None
                        break
                else:
                    # Если выбран шарик в инвентаре и клик вне инвентаря — выплюнуть
                    if selected_inv_idx is not None:
                        ball = game.try_eject_ball(selected_inv_idx, mx, my)
                        selected_inv_idx = None
                    else:
                        # Попробовать всосать шарик
                        game.try_absorb_ball(mx, my)

        # --- Логика ---
        game.update()

        # --- Рендер ---
        screen.fill(WHITE)
        # Зона удаления
        draw_delete_zone()
        # Шарики
        for ball in game.balls:
            if not ball.in_inventory:
                draw_ball(ball)
        # Инвентарь
        draw_inventory(game.inventory, selected_inv_idx)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

