import math
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game")

clock = pygame.time.Clock()

# --- The world is bigger than the window ---
WORLD_W, WORLD_H = 3000, 2000

GRASS_COLOR = (40, 160, 60)

def rounded_rect_points(rect, r, step=10):
    """Return points spaced ~step pixels apart along a rounded rectangle's outline."""
    pts = []

    def line(x1, y1, x2, y2):
        n = max(1, int(math.hypot(x2 - x1, y2 - y1) / step))
        for i in range(n):
            t = i / n
            pts.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))

    def arc(cx, cy, start, end):
        n = max(1, int(math.radians(abs(end - start)) * r / step))
        for i in range(n):
            a = math.radians(start + (end - start) * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    l, t, rt, b = rect.left, rect.top, rect.right, rect.bottom
    line(l + r, t, rt - r, t)            # top edge
    arc(rt - r, t + r, -90, 0)           # top-right corner
    line(rt, t + r, rt, b - r)           # right edge
    arc(rt - r, b - r, 0, 90)            # bottom-right corner
    line(rt - r, b, l + r, b)            # bottom edge (right to left)
    arc(l + r, b - r, 90, 180)           # bottom-left corner
    line(l, b - r, l, t + r)             # left edge
    arc(l + r, t + r, 180, 270)          # top-left corner
    return pts

def build_track():
    """Draw the whole track once onto one big picture."""
    surf = pygame.Surface((WORLD_W, WORLD_H))
    surf.fill(GRASS_COLOR)  # grass

    outer = pygame.Rect(300, 300, 2400, 1400)
    inner = pygame.Rect(700, 700, 1600, 600)

    # Gray road = big rounded rectangle, then cut a grass "island" out of the middle
    pygame.draw.rect(surf, (70, 70, 75), outer, border_radius=400)
    pygame.draw.rect(surf, GRASS_COLOR, inner, border_radius=200)

    pygame.draw.rect(surf, (240, 240, 240), inner, width=6, border_radius=200)

    # Yellow dashed center line
    middle = pygame.Rect(500, 500, 2000, 1000)
    pts = rounded_rect_points(middle, 300)
    for i in range(0, len(pts), 8):                 # every 8 points = one dash + one gap
        start = pts[i]
        end = pts[(i + 4) % len(pts)]               # dash covers 4 points (~40 px)
        pygame.draw.line(surf, (255, 210, 0), start, end, 6)

    return surf
track = build_track()




ACCEL = 250        # how fast the car speeds up (pixels/second²)
BRAKE = 400        # how hard the brakes are
FRICTION = 150     # how fast it slows down when you let go
MAX_SPEED = 450
TURN_SPEED = 160   # degrees per second at full speed
GRASS_MAX_SPEED = 150   # top speed on grass
GRASS_DRAG = 500        # how hard grass slows you when you're going faster than that

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0   # 0 means facing up; positive turns right
        self.speed = 0

        # Draw the car once on its own small surface (front is the top)
        self.image = pygame.Surface((40, 70), pygame.SRCALPHA)
        self.image.fill((200, 30, 30))                              # red body
        pygame.draw.rect(self.image, (170, 220, 255), (6, 10, 28, 14))  # windshield

    def update(self, dt, keys, on_grass):
        # Accelerate, brake, or coast
        if keys[pygame.K_UP]:
            self.speed += ACCEL * dt
        elif keys[pygame.K_DOWN]:
            self.speed -= BRAKE * dt
        else:
            if self.speed > 0:
                self.speed = max(0, self.speed - FRICTION * dt)
            elif self.speed < 0:
                self.speed = min(0, self.speed + FRICTION * dt)

        
        # Keep speed within limits (reverse is slower than forward)

                # On grass, drag pulls you down toward the grass speed limit
        if on_grass and self.speed > GRASS_MAX_SPEED:
            self.speed = max(GRASS_MAX_SPEED, self.speed - GRASS_DRAG * dt)

        # Keep speed within limits (reverse is slower than forward)
        self.speed = max(-MAX_SPEED / 2, min(MAX_SPEED, self.speed))
        self.speed = max(-MAX_SPEED / 2, min(MAX_SPEED, self.speed))

        # Steering only works in proportion to speed
        turn = TURN_SPEED * (self.speed / MAX_SPEED)
        if keys[pygame.K_LEFT]:
            self.angle -= turn * dt
        if keys[pygame.K_RIGHT]:
            self.angle += turn * dt

        # Move in the direction the car is facing
        rad = math.radians(self.angle)
        self.x += math.sin(rad) * self.speed * dt
        self.y -= math.cos(rad) * self.speed * dt

    def draw(self, screen, cam_x, cam_y):
        # pygame rotates counter-clockwise, our angle is clockwise, so use -angle
        rotated = pygame.transform.rotate(self.image, -self.angle)
        rect = rotated.get_rect(center=(self.x - cam_x, self.y - cam_y))
        screen.blit(rotated, rect)


car = Car(1500, 1500)   # on the bottom straight of the track
car.angle = 90          # 90 = facing right

running = True
while running:
    dt = clock.tick(60) / 1000  # seconds since the last frame

    # 1. INPUT: check what the player did
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()

    # 2. UPDATE: change the game state
        # 2. UPDATE: change the game state
    # Keep the car inside the world so get_at() never goes out of range
    car.x = max(0, min(WORLD_W - 1, car.x))
    car.y = max(0, min(WORLD_H - 1, car.y))

    # What is under the car's center right now?
    on_grass = track.get_at((int(car.x), int(car.y)))[:3] == GRASS_COLOR

    car.update(dt, keys, on_grass)
    

    # 3. DRAW: paint the frame
    cam_x = car.x - WIDTH / 2
    cam_y = car.y - HEIGHT / 2
    screen.blit(track, (-cam_x, -cam_y))
    car.draw(screen, cam_x, cam_y)
    pygame.display.flip()

pygame.quit()

    

