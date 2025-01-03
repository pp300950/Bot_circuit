import pygame
import sys

# ตั้งค่าหน้าจอและตาราง
WIDTH, HEIGHT = 1000, 800  # เพิ่มขนาดหน้าจอ
GRID_SIZE = 30             # ลดขนาดเซลล์เพื่อเพิ่มจำนวนเซลล์
ROWS, COLS = 25, 33        # เพิ่มจำนวนเซลล์ในตาราง
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

class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 'UP'

    def draw(self, screen):
        # วาดบล็อก
        rect = pygame.Rect(self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, BLUE, rect)
        # วาดกรอบสีแดงถ้าบล็อกถูกเลือก
        if self == selected_block:
            pygame.draw.rect(screen, RED, rect, 3)
        # วาดลูกศรแสดงทิศทางด้านหน้า
        arrow_x = self.x + ARROW_OFFSETS[self.direction][0]
        arrow_y = self.y + ARROW_OFFSETS[self.direction][1]
        pygame.draw.circle(screen, BLACK, (int(arrow_x * GRID_SIZE), int(arrow_y * GRID_SIZE)), 5)

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
            rect = pygame.Rect(col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_laser(path):
    font = pygame.font.SysFont(None, 24)  # กำหนดฟอนต์สำหรับตัวเลข
    for i in range(len(path)):
        x, y = path[i]

        # คำนวณจุดกึ่งกลางของเซลล์
        center_x = x * GRID_SIZE + GRID_SIZE // 2
        center_y = y * GRID_SIZE + GRID_SIZE // 2

        # วาดเส้นเลเซอร์ระหว่างเซลล์
        if i < len(path) - 1:  # ตรวจสอบว่ามีเซลล์ถัดไปหรือไม่
            next_x, next_y = path[i + 1]
            next_center_x = next_x * GRID_SIZE + GRID_SIZE // 2
            next_center_y = next_y * GRID_SIZE + GRID_SIZE // 2
            pygame.draw.line(screen, YELLOW, (center_x, center_y), (next_center_x, next_center_y), 5)  # ความหนา 5

        # วาดตัวเลข 15 ในแต่ละเซลล์
        text = font.render("15", True, BLACK)
        screen.blit(text, (center_x - 10, center_y - 10))  # ตำแหน่งของตัวเลข


def draw_menu(x, y):
    global menu_rects
    menu_rects = []
    options = ['Rotate Left', 'Rotate Right', 'Delete']
    for i, option in enumerate(options):
        rect = pygame.Rect(x, y + i * 30, 100, 30)
        pygame.draw.rect(screen, LIGHT_GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        text = pygame.font.SysFont(None, 20).render(option, True, BLACK)
        screen.blit(text, (x + 5, y + 5 + i * 30))
        menu_rects.append((rect, option))

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
            mx, my = pygame.mouse.get_pos()
            if menu_active:
                clicked_menu = False
                for rect, option in menu_rects:
                    if rect.collidepoint((mx, my)):
                        clicked_menu = True
                        if option == 'Rotate Left' and selected_block:
                            selected_block.rotate_left()
                        elif option == 'Rotate Right' and selected_block:
                            selected_block.rotate_right()
                        elif option == 'Delete' and selected_block:
                            blocks.remove(selected_block)
                            selected_block = None
                        menu_active = False
                        break
                if not clicked_menu:
                    menu_active = False
            else:
                grid_x, grid_y = mx // GRID_SIZE, my // GRID_SIZE
                for block in blocks:
                    if block.x == grid_x and block.y == grid_y:
                        selected_block = block
                        menu_active = True
                        menu_x, menu_y = mx, my
                        break
                else:
                    new_block = Block(grid_x, grid_y)
                    blocks.append(new_block)
                    selected_block = new_block
                    menu_active = False

    for block in blocks:
        block.draw(screen)

    if menu_active:
        draw_menu(menu_x, menu_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
