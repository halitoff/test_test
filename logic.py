import random
from typing import List, Tuple, Optional

# Тип цвета: (R, G, B), значения 0-255
Color = Tuple[int, int, int]

def mix_colors(c1: Color, c2: Color) -> Color:
    """Смешивает два цвета: усредняет каждый канал RGB."""
    return tuple((a + b) // 2 for a, b in zip(c1, c2))

class Ball:
    def __init__(self, x: float, y: float, radius: float, color: Color, vx: float = 0, vy: float = 0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = vx
        self.vy = vy
        self.in_inventory = False

    def move(self, bounds: Tuple[int, int]):
        """Двигает шарик, отражая от границ экрана."""
        if self.in_inventory:
            return
        self.x += self.vx
        self.y += self.vy
        w, h = bounds
        # Отражение от границ
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = -self.vx
        if self.x + self.radius > w:
            self.x = w - self.radius
            self.vx = -self.vx
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = -self.vy
        if self.y + self.radius > h:
            self.y = h - self.radius
            self.vy = -self.vy

    def is_point_inside(self, px: float, py: float) -> bool:
        return (self.x - px) ** 2 + (self.y - py) ** 2 <= self.radius ** 2

class Inventory:
    def __init__(self, size: int = 5):
        self.size = size
        self.balls: List[Ball] = []

    def add(self, ball: Ball) -> bool:
        if len(self.balls) < self.size:
            ball.in_inventory = True
            self.balls.append(ball)
            return True
        return False

    def remove(self, ball: Ball) -> bool:
        if ball in self.balls:
            self.balls.remove(ball)
            ball.in_inventory = False
            return True
        return False

class GameLogic:
    def __init__(self, width: int, height: int, delete_zone: Tuple[int, int, int, int]):
        self.width = width
        self.height = height
        self.balls: List[Ball] = []
        self.inventory = Inventory()
        self.delete_zone = delete_zone  # (x, y, w, h)

    def spawn_ball(self, x: float, y: float, radius: float, color: Color, vx: Optional[float]=None, vy: Optional[float]=None):
        if vx is None:
            vx = random.uniform(-2, 2)
        if vy is None:
            vy = random.uniform(-2, 2)
        self.balls.append(Ball(x, y, radius, color, vx, vy))

    def move_balls(self):
        for ball in self.balls:
            ball.move((self.width, self.height))

    def try_absorb_ball(self, px: float, py: float) -> Optional[Ball]:
        """Пробует всосать шарик мышкой (по координатам)."""
        for ball in self.balls:
            if not ball.in_inventory and ball.is_point_inside(px, py):
                if self.inventory.add(ball):
                    return ball
        return None

    def try_eject_ball(self, idx: int, x: float, y: float) -> Optional[Ball]:
        """Выплёвывает шарик из инвентаря на позицию (x, y)."""
        if 0 <= idx < len(self.inventory.balls):
            ball = self.inventory.balls[idx]
            self.inventory.remove(ball)
            ball.x = x
            ball.y = y
            ball.vx = random.uniform(-2, 2)
            ball.vy = random.uniform(-2, 2)
            return ball
        return None

    def mix_colliding_balls(self):
        """Смешивает цвета шариков, которые пересекаются."""
        for i, b1 in enumerate(self.balls):
            if b1.in_inventory:
                continue
            for j in range(i + 1, len(self.balls)):
                b2 = self.balls[j]
                if b2.in_inventory:
                    continue
                if self._balls_collide(b1, b2):
                    new_color = mix_colors(b1.color, b2.color)
                    b1.color = b2.color = new_color

    def _balls_collide(self, b1: Ball, b2: Ball) -> bool:
        dx = b1.x - b2.x
        dy = b1.y - b2.y
        dist2 = dx * dx + dy * dy
        r_sum = b1.radius + b2.radius
        return dist2 < r_sum * r_sum

    def delete_balls_in_zone(self):
        """Удаляет шарики, попавшие в зону удаления."""
        x, y, w, h = self.delete_zone
        to_delete = [b for b in self.balls if not b.in_inventory and x <= b.x <= x + w and y <= b.y <= y + h]
        for b in to_delete:
            self.balls.remove(b)

    def update(self):
        """Основной шаг логики: движение, смешивание, удаление."""
        self.move_balls()
        self.mix_colliding_balls()
        self.delete_balls_in_zone() 