import pygame
import sys

# ตั้งค่าหน้าจอและตาราง
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 40
ROWS, COLS = 15, 20
LASER_RANGE = 15

# สี
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# เริ่มต้น Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laser Block Program")
clock = pygame.time.Clock()

# ทิศทาง
DIRECTIONS = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}

# บล็อกทั้งหมด
blocks = []

# บล็อกที่เลือก
selected_block = None

class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 'UP'

    def draw(self, screen):
        rect = pygame.Rect(self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, BLUE, rect)
        if self == selected_block:
            pygame.draw.rect(screen, RED, rect, 3)

    def rotate_left(self):
        directions = list(DIRECTIONS.keys())
        index = (directions.index(self.direction) - 1) % len(directions)
        self.direction = directions[index]

    def rotate_right(self):
        directions = list(DIRECTIONS.keys())
        index = (directions.index(self.direction) + 1) % len(directions)
        self.direction = directions[index]

    def fire_laser(self):
        laser_path = []
        dx, dy = DIRECTIONS[self.direction]
        for step in range(1, LASER_RANGE + 1):
            nx, ny = self.x + dx * step, self.y + dy * step
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                if any(block.x == nx and block.y == ny for block in blocks):
                    break
                laser_path.append((nx, ny))
            else:
                break
        return laser_path

# ฟังก์ชันวาดตาราง
def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

# ฟังก์ชันวาดเลเซอร์
def draw_laser(path):
    for x, y in path:
        rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, YELLOW, rect)

# Main loop
running = True
while running:
    screen.fill(WHITE)
    draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            grid_x, grid_y = mx // GRID_SIZE, my // GRID_SIZE

            # คลิกเพื่อเลือกหรือเพิ่มบล็อก
            for block in blocks:
                if block.x == grid_x and block.y == grid_y:
                    selected_block = block
                    break
            else:
                new_block = Block(grid_x, grid_y)
                blocks.append(new_block)
                selected_block = new_block

        elif event.type == pygame.KEYDOWN:
            if selected_block:
                if event.key == pygame.K_LEFT:  # หมุนซ้าย
                    selected_block.rotate_left()
                elif event.key == pygame.K_RIGHT:  # หมุนขวา
                    selected_block.rotate_right()
                elif event.key == pygame.K_SPACE:  # ยิงเลเซอร์
                    laser_path = selected_block.fire_laser()

    # วาดบล็อกทั้งหมด
    for block in blocks:
        block.draw(screen)

    # วาดเลเซอร์ถ้ายิง
    if selected_block and 'laser_path' in locals():
        draw_laser(laser_path)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
