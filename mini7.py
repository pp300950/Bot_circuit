import pygame
import sys

# ตั้งค่าหน้าจอและตาราง
WIDTH, HEIGHT = 1120, 800  # เพิ่มความกว้างสำหรับพื้นที่เมนู

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

zoom_level = 1  # ระดับการซูมเริ่มต้น
offset_x, offset_y = 0, 0  # ตัวแปรสำหรับการเลื่อนตาราง


class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 'UP'

    def draw(self, screen):
        rect = pygame.Rect(
            self.x * GRID_SIZE + offset_x,
            self.y * GRID_SIZE + offset_y,
            GRID_SIZE,
            GRID_SIZE,
        )
        pygame.draw.rect(screen, BLUE, rect)
        if self == selected_block:
            pygame.draw.rect(screen, RED, rect, 3)
        arrow_x = self.x + ARROW_OFFSETS[self.direction][0]
        arrow_y = self.y + ARROW_OFFSETS[self.direction][1]
        pygame.draw.circle(
            screen,
            BLACK,
            (
                int(arrow_x * GRID_SIZE + offset_x),
                int(arrow_y * GRID_SIZE + offset_y),
            ),
            5,
        )

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
            rect = pygame.Rect(
                col * GRID_SIZE + offset_x,
                row * GRID_SIZE + offset_y,
                GRID_SIZE,
                GRID_SIZE,
            )
            pygame.draw.rect(screen, GRAY, rect, 1)


def draw_laser(path):
    font = pygame.font.SysFont(None, 24)
    for i in range(len(path)):
        x, y = path[i]
        center_x = x * GRID_SIZE + GRID_SIZE // 2 + offset_x
        center_y = y * GRID_SIZE + GRID_SIZE // 2 + offset_y
        if i < len(path) - 1:
            next_x, next_y = path[i + 1]
            next_center_x = next_x * GRID_SIZE + GRID_SIZE // 2 + offset_x
            next_center_y = next_y * GRID_SIZE + GRID_SIZE // 2 + offset_y
            pygame.draw.line(screen, YELLOW, (center_x, center_y), (next_center_x, next_center_y), 5)
        text = font.render("15", True, BLACK)
        screen.blit(text, (center_x - 10, center_y - 10))


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


def adjust_zoom(mouse_x, mouse_y, zoom_in):
    global GRID_SIZE, offset_x, offset_y

    grid_mouse_x = (mouse_x - offset_x) / GRID_SIZE
    grid_mouse_y = (mouse_y - offset_y) / GRID_SIZE

    if zoom_in:
        new_grid_size = min(60, GRID_SIZE + 2)
    else:
        new_grid_size = max(10, GRID_SIZE - 2)

    if new_grid_size != GRID_SIZE:
        offset_x = mouse_x - grid_mouse_x * new_grid_size
        offset_y = mouse_y - grid_mouse_y * new_grid_size
        GRID_SIZE = new_grid_size

# เพิ่มตัวเลือกสีพื้นหลัง
background_color = WHITE  # ค่าเริ่มต้น
color_options = [WHITE, GRAY, LIGHT_GRAY, YELLOW]

def draw_settings_menu():
    menu_x = WIDTH - 100  # ตำแหน่งเมนูที่ชิดขอบขวา
    menu_y = 10
    option_height = 40

    font = pygame.font.SysFont(None, 24)
    for i, color in enumerate(color_options):
        rect = pygame.Rect(menu_x, menu_y + i * (option_height + 10), 80, option_height)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        text = font.render(f"Color {i + 1}", True, BLACK if color != BLACK else WHITE)
        screen.blit(text, (menu_x + 5, menu_y + i * (option_height + 10) + 10))

def check_menu_click(mx, my):
    menu_x = WIDTH - 120
    menu_y = 10
    option_height = 40
    for i, color in enumerate(color_options):
        rect = pygame.Rect(menu_x, menu_y + i * (option_height + 10), 100, option_height)
        if rect.collidepoint(mx, my):
            return color
    return None

running = True


while running:
    screen.fill(background_color)  # ใช้สีพื้นหลังแบบปรับแต่งได้
    draw_grid()
    draw_settings_menu()  # วาดเมนูการตั้งค่าที่ขอบจอ

    for block in blocks:
        laser_path = block.fire_laser()
        draw_laser(laser_path)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            keys = pygame.key.get_pressed()
            if not (keys[pygame.K_LALT] or keys[pygame.K_RALT]):  # ป้องกันการวางบล็อกเมื่อ Alt ถูกกด
                mx, my = pygame.mouse.get_pos()
                selected_color = check_menu_click(mx, my)
                if selected_color:  # ถ้าคลิกที่เมนู
                    background_color = selected_color
                elif menu_active:
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
                    continue  # ข้ามส่วนอื่นเมื่อคลิกเมนู
                else:
                    grid_x = (mx - offset_x) // GRID_SIZE
                    grid_y = (my - offset_y) // GRID_SIZE

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

        elif event.type == pygame.MOUSEWHEEL:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LALT] or keys[pygame.K_RALT]:
                mx, my = pygame.mouse.get_pos()
                if event.y > 0:
                    adjust_zoom(mx, my, zoom_in=True)
                elif event.y < 0:
                    adjust_zoom(mx, my, zoom_in=False)

    for block in blocks:
        block.draw(screen)

    if menu_active:
        draw_menu(menu_x, menu_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
