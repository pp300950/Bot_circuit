import pygame
import sys

# ตั้งค่าหน้าจอและตาราง
WIDTH, HEIGHT = 1000, 800
GRID_SIZE = 30
ROWS, COLS = 25, 33
LASER_RANGE = 15

# สี
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)

# เริ่มต้น Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Laser Block Program")
clock = pygame.time.Clock()

# ทิศทาง
DIRECTIONS = ['UP', 'RIGHT', 'DOWN', 'LEFT']
ARROW_OFFSETS = {
    'UP': (0.5, 0.2),
    'RIGHT': (0.8, 0.5),
    'DOWN': (0.5, 0.8),
    'LEFT': (0.2, 0.5),
}

# บล็อกทั้งหมด
blocks = []
selected_block = None
menu_active = False
menu_rects = []
dragging_block = None

zoom = 1.0  # เริ่มต้นขนาดการซูม
offset_x, offset_y = 0, 0  # การเลื่อนหน้าจอ

class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 'UP'

    def draw(self, screen):
        rect = pygame.Rect((self.x * GRID_SIZE + offset_x) * zoom, (self.y * GRID_SIZE + offset_y) * zoom,
                           GRID_SIZE * zoom, GRID_SIZE * zoom)
        pygame.draw.rect(screen, BLUE, rect)
        if self == selected_block:
            pygame.draw.rect(screen, RED, rect, 3)

        arrow_x = (self.x + ARROW_OFFSETS[self.direction][0]) * GRID_SIZE + offset_x
        arrow_y = (self.y + ARROW_OFFSETS[self.direction][1]) * GRID_SIZE + offset_y
        pygame.draw.circle(screen, BLACK, (int(arrow_x * zoom), int(arrow_y * zoom)), int(5 * zoom))

    def rotate_left(self):
        current_index = DIRECTIONS.index(self.direction)
        self.direction = DIRECTIONS[(current_index - 1) % len(DIRECTIONS)]

    def rotate_right(self):
        current_index = DIRECTIONS.index(self.direction)
        self.direction = DIRECTIONS[(current_index + 1) % len(DIRECTIONS)]

    def fire_laser(self):
        laser_path = []
        dx, dy = {
            'UP': (0, -1),
            'RIGHT': (1, 0),
            'DOWN': (0, 1),
            'LEFT': (-1, 0)
        }[self.direction]
        for step in range(1, LASER_RANGE + 1):
            nx, ny = self.x + dx * step, self.y + dy * step
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                if any(block.x == nx and block.y == ny for block in blocks):
                    break
                laser_path.append((nx, ny))
            else:
                break
        return laser_path

def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect((col * GRID_SIZE + offset_x) * zoom, (row * GRID_SIZE + offset_y) * zoom,
                               GRID_SIZE * zoom, GRID_SIZE * zoom)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_laser(path):
    for x, y in path:
        rect = pygame.Rect((x * GRID_SIZE + offset_x) * zoom, (y * GRID_SIZE + offset_y) * zoom,
                           GRID_SIZE * zoom, GRID_SIZE * zoom)
        pygame.draw.rect(screen, YELLOW, rect)
        font = pygame.font.SysFont(None, int(24 * zoom))
        text = font.render("15", True, BLACK)
        screen.blit(text, (rect.x + GRID_SIZE * zoom // 4, rect.y + GRID_SIZE * zoom // 4))

def handle_zoom(event):
    global zoom, offset_x, offset_y
    if event.button == 4:  # ลูกล้อเลื่อนขึ้น (ซูมเข้า)
        zoom = min(2.0, zoom + 0.1)
    elif event.button == 5:  # ลูกล้อเลื่อนลง (ซูมออก)
        zoom = max(0.5, zoom - 0.1)


running = True
dragging = False
while running:
    screen.fill(WHITE)
    draw_grid()

    for block in blocks:
        laser_path = block.fire_laser()
        draw_laser(laser_path)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # คลิกซ้าย
                mx, my = event.pos
                dragging = True
                grid_x, grid_y = int((mx / zoom - offset_x) // GRID_SIZE), int((my / zoom - offset_y) // GRID_SIZE)
                for block in blocks:
                    if block.x == grid_x and block.y == grid_y:
                        dragging_block = block
                        break
                else:
                    dragging_block = None

            elif event.button == 4 or event.button == 5:  # เลื่อนเมาส์เพื่อซูม
                handle_zoom(event)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # ปล่อยเมาส์ซ้าย
                mx, my = event.pos
                if dragging and not dragging_block:
                    grid_x, grid_y = int((mx / zoom - offset_x) // GRID_SIZE), int((my / zoom - offset_y) // GRID_SIZE)
                    new_block = Block(grid_x, grid_y)
                    blocks.append(new_block)
            dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging and dragging_block:
                mx, my = event.pos
                grid_x, grid_y = int((mx / zoom - offset_x) // GRID_SIZE), int((my / zoom - offset_y) // GRID_SIZE)
                dragging_block.x, dragging_block.y = grid_x, grid_y

    for block in blocks:
        block.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
