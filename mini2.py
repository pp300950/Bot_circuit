import pygame
import sys

# ตั้งค่าหน้าจอและตาราง
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 40
ROWS, COLS = 100, 100
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
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laser Block Program")
clock = pygame.time.Clock()

# ทิศทาง
DIRECTIONS = ['UP', 'RIGHT', 'DOWN', 'LEFT']

# บล็อกทั้งหมด
blocks = []
selected_block = None
menu_active = False
menu_rects = []
scroll_offset = [0, 0]
is_dragging = False
last_mouse_pos = (0, 0)

class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 'UP'

    def draw(self):
        rect = pygame.Rect(
            (self.x + scroll_offset[0]) * GRID_SIZE,
            (self.y + scroll_offset[1]) * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(screen, BLUE, rect)
        if self == selected_block:
            pygame.draw.rect(screen, RED, rect, 3)

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
    for row in range(-ROWS // 2, ROWS // 2 + 1):
        for col in range(-COLS // 2, COLS // 2 + 1):
            x = (col + scroll_offset[0]) * GRID_SIZE
            y = (row + scroll_offset[1]) * GRID_SIZE
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_laser(path):
    for x, y in path:
        rect = pygame.Rect(
            (x + scroll_offset[0]) * GRID_SIZE,
            (y + scroll_offset[1]) * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(screen, YELLOW, rect)

running = True
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
                grid_x = mx // GRID_SIZE - scroll_offset[0]
                grid_y = my // GRID_SIZE - scroll_offset[1]
                new_block = Block(grid_x, grid_y)
                blocks.append(new_block)
                selected_block = new_block
            elif event.button == 3:  # คลิกขวาเพื่อเลื่อนหน้าจอ
                is_dragging = True
                last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            is_dragging = False
        elif event.type == pygame.MOUSEMOTION and is_dragging:
            dx = (event.pos[0] - last_mouse_pos[0]) // GRID_SIZE
            dy = (event.pos[1] - last_mouse_pos[1]) // GRID_SIZE
            scroll_offset[0] += dx
            scroll_offset[1] += dy
            last_mouse_pos = event.pos

    for block in blocks:
        block.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
