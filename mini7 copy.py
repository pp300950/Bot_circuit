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
pygame.init()  # เริ่มต้นการทำงานของโมดูล pygame
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # สร้างหน้าต่างสำหรับแสดงผลตามขนาดที่กำหนด
pygame.display.set_caption("Laser Block Program")  # ตั้งชื่อหน้าต่างเป็น "Laser Block Program"
clock = pygame.time.Clock()  # สร้างนาฬิกาเพื่อควบคุมอัตราเฟรมของเกม

# ทิศทางสำหรับบล็อก
DIRECTIONS = ['UP', 'RIGHT', 'DOWN', 'LEFT']  # กำหนดทิศทาง 4 ด้านสำหรับบล็อก
ARROW_OFFSETS = {
    'UP': (0.5, 0.2),  # ตำแหน่งลูกศรเมื่อบล็อกหันขึ้น
    'RIGHT': (0.8, 0.5),  # ตำแหน่งลูกศรเมื่อบล็อกหันขวา
    'DOWN': (0.5, 0.8),  # ตำแหน่งลูกศรเมื่อบล็อกหันลง
    'LEFT': (0.2, 0.5),  # ตำแหน่งลูกศรเมื่อบล็อกหันซ้าย
}

blocks = []  # ลิสต์สำหรับเก็บบล็อกทั้งหมดในเกม
selected_block = None  # เก็บบล็อกที่ถูกเลือก
menu_active = False  # สถานะเมนู
menu_rects = []  # เก็บพื้นที่ของเมนู
zoom_level = 1  # ระดับซูมเริ่มต้น
offset_x, offset_y = 0, 0  # ค่าเริ่มต้นของการเลื่อนตาราง

class Block:
    def __init__(self, x, y):
        self.x = x  # ตำแหน่งแกน x ของบล็อกในกริด
        self.y = y  # ตำแหน่งแกน y ของบล็อกในกริด
        self.direction = 'UP'  # ทิศทางเริ่มต้นของบล็อก

    def draw(self, screen):
        rect = pygame.Rect(
            self.x * GRID_SIZE + offset_x,
            self.y * GRID_SIZE + offset_y,
            GRID_SIZE,
            GRID_SIZE,
        )  # กำหนดพื้นที่สี่เหลี่ยมที่บล็อกครอบคลุม
        pygame.draw.rect(screen, BLUE, rect)  # วาดบล็อกด้วยสีฟ้า
        if self == selected_block:  # ถ้าบล็อกนี้ถูกเลือก
            pygame.draw.rect(screen, RED, rect, 3)  # วาดขอบสีแดงรอบบล็อก
        arrow_x = self.x + ARROW_OFFSETS[self.direction][0]  # คำนวณตำแหน่งลูกศรแกน x
        arrow_y = self.y + ARROW_OFFSETS[self.direction][1]  # คำนวณตำแหน่งลูกศรแกน y
        pygame.draw.circle(
            screen,
            BLACK,
            (
                int(arrow_x * GRID_SIZE + offset_x),
                int(arrow_y * GRID_SIZE + offset_y),
            ),
            5,  # ขนาดของจุดลูกศร
        )

    def rotate_left(self):
        current_index = DIRECTIONS.index(self.direction)  # หาอินเด็กซ์ของทิศทางปัจจุบัน
        self.direction = DIRECTIONS[(current_index - 1) % len(DIRECTIONS)]  # หมุนไปทางซ้าย

    def rotate_right(self):
        current_index = DIRECTIONS.index(self.direction)  # หาอินเด็กซ์ของทิศทางปัจจุบัน
        self.direction = DIRECTIONS[(current_index + 1) % len(DIRECTIONS)]  # หมุนไปทางขวา

    def fire_laser(self):
        laser_path = []  # เก็บเส้นทางของเลเซอร์
        dx, dy = {
            'UP': (0, -1),
            'RIGHT': (1, 0),
            'DOWN': (0, 1),
            'LEFT': (-1, 0)
        }[self.direction]  # กำหนดการเคลื่อนที่ตามทิศทางปัจจุบัน
        for step in range(1, LASER_RANGE + 1):
            nx, ny = self.x + dx * step, self.y + dy * step  # คำนวณตำแหน่งถัดไป
            if 0 <= nx < COLS and 0 <= ny < ROWS:  # ตรวจสอบว่าตำแหน่งอยู่ในขอบเขต
                if any(block.x == nx and block.y == ny for block in blocks):  # ถ้าพบบล็อกขวางทาง
                    break  # หยุดเลเซอร์
                laser_path.append((nx, ny))  # เพิ่มตำแหน่งไปยังเส้นทางเลเซอร์
            else:
                break  # หยุดถ้าเกินขอบเขต
        return laser_path  # คืนค่าเส้นทางเลเซอร์

# ฟังก์ชันวาดกริด

def draw_grid():
    for row in range(ROWS):  # วนลูปตามจำนวนแถว
        for col in range(COLS):  # วนลูปตามจำนวนคอลัมน์
            rect = pygame.Rect(
                col * GRID_SIZE + offset_x,
                row * GRID_SIZE + offset_y,
                GRID_SIZE,
                GRID_SIZE,
            )  # สร้างสี่เหลี่ยมในตำแหน่งกริด
            pygame.draw.rect(screen, GRAY, rect, 1)  # วาดเส้นขอบสี่เหลี่ยมด้วยสีเทา

# ฟังก์ชันวาดเลเซอร์

def draw_laser(path):
    font = pygame.font.SysFont(None, 24)  # สร้างฟอนต์
    for i in range(len(path)):
        x, y = path[i]  # ตำแหน่งปัจจุบันของเลเซอร์
        center_x = x * GRID_SIZE + GRID_SIZE // 2 + offset_x  # ตำแหน่งศูนย์กลางแกน x
        center_y = y * GRID_SIZE + GRID_SIZE // 2 + offset_y  # ตำแหน่งศูนย์กลางแกน y
        if i < len(path) - 1:
            next_x, next_y = path[i + 1]  # ตำแหน่งถัดไป
            next_center_x = next_x * GRID_SIZE + GRID_SIZE // 2 + offset_x
            next_center_y = next_y * GRID_SIZE + GRID_SIZE // 2 + offset_y
            pygame.draw.line(screen, YELLOW, (center_x, center_y), (next_center_x, next_center_y), 5)  # วาดเส้นเลเซอร์
        text = font.render("15", True, BLACK)  # วาดข้อความที่ตำแหน่งเลเซอร์
        screen.blit(text, (center_x - 10, center_y - 10))

# ฟังก์ชันวาดเมนู

def draw_menu(x, y):
    global menu_rects
    menu_rects = []  # เคลียร์เมนูก่อนวาดใหม่
    options = ['Rotate Left', 'Rotate Right', 'Delete']  # ตัวเลือกในเมนู
    for i, option in enumerate(options):
        rect = pygame.Rect(x, y + i * 30, 100, 30)  # สร้างพื้นที่สี่เหลี่ยมสำหรับแต่ละตัวเลือก
        pygame.draw.rect(screen, LIGHT_GRAY, rect)  # วาดพื้นหลังเมนู
        pygame.draw.rect(screen, BLACK, rect, 2)  # วาดขอบเมนู
        text = pygame.font.SysFont(None, 20).render(option, True, BLACK)  # สร้างข้อความเมนู
        screen.blit(text, (x + 5, y + 5 + i * 30))  # แสดงข้อความในเมนู
        menu_rects.append((rect, option))  # เก็บพื้นที่ของเมนูสำหรับตรวจสอบการคลิก

def adjust_zoom(mouse_x, mouse_y, zoom_in):  
    # ฟังก์ชันสำหรับปรับการซูม โดยใช้ตำแหน่งเมาส์และทิศทางการซูม (เข้า/ออก)  
    global GRID_SIZE, offset_x, offset_y  # ประกาศตัวแปรที่ใช้ในระดับ global  

    grid_mouse_x = (mouse_x - offset_x) / GRID_SIZE  
    # คำนวณตำแหน่ง X ของเมาส์ในกริด หลังจากหักลบการชดเชยตำแหน่ง (offset)  
    grid_mouse_y = (mouse_y - offset_y) / GRID_SIZE  
    # คำนวณตำแหน่ง Y ของเมาส์ในกริด  

    if zoom_in:  
        new_grid_size = min(60, GRID_SIZE + 2)  
        # ถ้าซูมเข้า ให้เพิ่มขนาดกริด แต่ไม่เกิน 60  
    else:  
        new_grid_size = max(10, GRID_SIZE - 2)  
        # ถ้าซูมออก ให้ลดขนาดกริด แต่ไม่ต่ำกว่า 10  

    if new_grid_size != GRID_SIZE:  
        # หากขนาดกริดใหม่แตกต่างจากขนาดปัจจุบัน  
        offset_x = mouse_x - grid_mouse_x * new_grid_size  
        # คำนวณตำแหน่งชดเชยใหม่สำหรับแกน X  
        offset_y = mouse_y - grid_mouse_y * new_grid_size  
        # คำนวณตำแหน่งชดเชยใหม่สำหรับแกน Y  
        GRID_SIZE = new_grid_size  
        # ปรับขนาดกริดให้เป็นค่าขนาดใหม่  

# เพิ่มตัวเลือกสีพื้นหลัง
background_color = WHITE  # กำหนดสีพื้นหลังเริ่มต้นเป็นสีขาว  
color_options = [WHITE, GRAY, LIGHT_GRAY, YELLOW]  
# รายการตัวเลือกสีพื้นหลังที่มีให้เลือก  

def draw_settings_menu():  
    # ฟังก์ชันสำหรับวาดเมนูตั้งค่า  
    menu_x = WIDTH - 100  # ตำแหน่งแกน X ของเมนูด้านขวา  
    menu_y = 10  # ตำแหน่งแกน Y ของเมนู  
    option_height = 40  # ความสูงของแต่ละตัวเลือกในเมนู  

    font = pygame.font.SysFont(None, 24)  
    # กำหนดฟอนต์และขนาดของตัวอักษร  
    for i, color in enumerate(color_options):  
        # ลูปเพื่อวาดตัวเลือกแต่ละสีในเมนู  
        rect = pygame.Rect(menu_x, menu_y + i * (option_height + 10), 80, option_height)  
        # กำหนดพื้นที่สี่เหลี่ยมสำหรับตัวเลือก  
        pygame.draw.rect(screen, color, rect)  
        # วาดสี่เหลี่ยมสีสำหรับตัวเลือก  
        pygame.draw.rect(screen, BLACK, rect, 2)  
        # วาดขอบสี่เหลี่ยมสีดำรอบตัวเลือก  
        text = font.render(f"Color {i + 1}", True, BLACK if color != BLACK else WHITE)  
        # สร้างข้อความสำหรับชื่อสี โดยใช้สีข้อความตรงข้ามกับสีพื้นหลัง  
        screen.blit(text, (menu_x + 5, menu_y + i * (option_height + 10) + 10))  
        # แสดงข้อความในตำแหน่งที่กำหนด  

def check_menu_click(mx, my):  
    # ฟังก์ชันเพื่อตรวจสอบว่าคลิกเมนูตรงจุดใด  
    menu_x = WIDTH - 120  # ตำแหน่ง X ของเมนู  
    menu_y = 10  # ตำแหน่ง Y ของเมนู  
    option_height = 40  # ความสูงของแต่ละตัวเลือก  
    for i, color in enumerate(color_options):  
        # ลูปเพื่อตรวจสอบแต่ละตัวเลือกสี  
        rect = pygame.Rect(menu_x, menu_y + i * (option_height + 10), 100, option_height)  
        # กำหนดพื้นที่สี่เหลี่ยมสำหรับตัวเลือก  
        if rect.collidepoint(mx, my):  
            # หากตำแหน่งคลิกตรงกับตัวเลือกสี  
            return color  # คืนค่าตัวเลือกสีนั้น  
    return None  # หากไม่ตรงกับตัวเลือกใดเลย คืนค่า None  


running = True
dragging_block = None  # ตัวแปรสำหรับเก็บบล็อกที่กำลังถูกเลื่อน

while running:  # วนลูปหลักของโปรแกรมเมื่อ running เป็น True
    screen.fill(background_color)  # เติมสีพื้นหลังด้วยค่าสีที่ตั้งไว้
    draw_grid()  # วาดเส้นตารางบนหน้าจอ
    draw_settings_menu()  # วาดเมนูการตั้งค่าที่ขอบจอ

    for block in blocks:  # วนซ้ำแต่ละบล็อกในลิสต์ blocks
        laser_path = block.fire_laser()  # คำนวณเส้นทางเลเซอร์จากบล็อก
        draw_laser(laser_path)  # วาดเลเซอร์บนหน้าจอตามเส้นทางที่คำนวณได้

    for event in pygame.event.get():  # ตรวจสอบเหตุการณ์ที่เกิดขึ้นใน pygame
        if event.type == pygame.QUIT:  # ถ้ามีการคลิกปิดหน้าต่าง
            running = False  # หยุดลูปหลักเพื่อออกจากโปรแกรม

        elif event.type == pygame.MOUSEBUTTONDOWN:  # ถ้ามีการคลิกเมาส์
            keys = pygame.key.get_pressed()  # ตรวจสอบปุ่มที่ถูกกด
            mx, my = pygame.mouse.get_pos()  # รับตำแหน่งของเมาส์

            if event.button == 1:  # ถ้าเป็นคลิกซ้าย
                # ตรวจสอบว่าคลิกบนบล็อกเพื่อเริ่มลาก
                for block in blocks:  # วนซ้ำแต่ละบล็อกในลิสต์
                    rect = pygame.Rect(
                        block.x * GRID_SIZE + offset_x,
                        block.y * GRID_SIZE + offset_y,
                        GRID_SIZE,
                        GRID_SIZE,
                    )  # สร้างพื้นที่สี่เหลี่ยมสำหรับแต่ละบล็อก
                    if rect.collidepoint(mx, my):  # ถ้าคลิกในพื้นที่ของบล็อก
                        dragging_block = block  # กำหนดบล็อกที่กำลังลาก
                        break

                if not dragging_block:  # ถ้าไม่ได้คลิกบนบล็อก
                    if not (keys[pygame.K_LALT] or keys[pygame.K_RALT]):  # ตรวจสอบว่าปุ่ม Alt ไม่ได้ถูกกด
                        selected_color = check_menu_click(mx, my)  # ตรวจสอบว่าคลิกในเมนูหรือไม่
                        if selected_color:  # ถ้ามีสีที่เลือกจากเมนู
                            background_color = selected_color  # เปลี่ยนสีพื้นหลัง
                        elif menu_active:  # ถ้าเมนูเปิดอยู่
                            clicked_menu = False  # ตั้งค่าสถานะเมนูที่คลิก
                            for rect, option in menu_rects:  # วนซ้ำในตัวเลือกเมนู
                                if rect.collidepoint((mx, my)):  # ถ้าคลิกในเมนู
                                    clicked_menu = True  # กำหนดสถานะว่าเมนูถูกคลิก
                                    if option == 'Rotate Left' and selected_block:  # ถ้าคลิกหมุนซ้าย
                                        selected_block.rotate_left()  # หมุนบล็อกไปทางซ้าย
                                    elif option == 'Rotate Right' and selected_block:  # ถ้าคลิกหมุนขวา
                                        selected_block.rotate_right()  # หมุนบล็อกไปทางขวา
                                    elif option == 'Delete' and selected_block:  # ถ้าคลิกลบบล็อก
                                        blocks.remove(selected_block)  # ลบบล็อกออกจากลิสต์
                                        selected_block = None  # รีเซ็ตบล็อกที่เลือก
                                    menu_active = False  # ปิดเมนู
                                    break
                            if not clicked_menu:  # ถ้าไม่ได้คลิกในเมนู
                                menu_active = False  # ปิดเมนู
                            continue  # ข้ามส่วนที่เหลือในลูปเมื่อคลิกเมนู
                        else:  # ถ้าไม่ใช่เมนูหรือบล็อก
                            grid_x = (mx - offset_x) // GRID_SIZE  # คำนวณตำแหน่งกริดแนวนอน
                            grid_y = (my - offset_y) // GRID_SIZE  # คำนวณตำแหน่งกริดแนวตั้ง

                            for block in blocks:  # วนซ้ำบล็อกทั้งหมด
                                if block.x == grid_x and block.y == grid_y:  # ถ้าพบตำแหน่งบล็อกที่ตรงกัน
                                    selected_block = block  # กำหนดบล็อกที่เลือก
                                    menu_active = True  # เปิดเมนู
                                    menu_x, menu_y = mx, my  # ตั้งตำแหน่งเมนู
                                    break
                            else:  # ถ้าไม่พบบล็อกในตำแหน่งนั้น
                                new_block = Block(grid_x, grid_y)  # สร้างบล็อกใหม่
                                blocks.append(new_block)  # เพิ่มบล็อกใหม่ในลิสต์
                                selected_block = new_block  # กำหนดบล็อกที่เลือกเป็นบล็อกใหม่
                                menu_active = False  # ปิดเมนู

            elif event.button == 3:  # ถ้าเป็นคลิกขวา
                for block in blocks:  # วนซ้ำแต่ละบล็อก
                    rect = pygame.Rect(
                        block.x * GRID_SIZE + offset_x,
                        block.y * GRID_SIZE + offset_y,
                        GRID_SIZE,
                        GRID_SIZE,
                    )  # สร้างพื้นที่สี่เหลี่ยมสำหรับแต่ละบล็อก
                    if rect.collidepoint(mx, my):  # ถ้าคลิกในพื้นที่ของบล็อก
                        selected_block = block  # กำหนดบล็อกที่เลือก
                        menu_active = True  # เปิดเมนู
                        menu_x, menu_y = mx, my  # ตั้งตำแหน่งเมนู
                        break

        elif event.type == pygame.MOUSEWHEEL:  # ถ้ามีการเลื่อนล้อเมาส์
            keys = pygame.key.get_pressed()  # ตรวจสอบปุ่มที่ถูกกด
            if keys[pygame.K_LALT] or keys[pygame.K_RALT]:  # ถ้า Alt ซ้ายหรือขวาถูกกด
                mx, my = pygame.mouse.get_pos()  # รับตำแหน่งเมาส์
                if event.y > 0:  # ถ้าเลื่อนล้อขึ้น
                    adjust_zoom(mx, my, zoom_in=True)  # ซูมเข้า
                elif event.y < 0:  # ถ้าเลื่อนล้อลง
                    adjust_zoom(mx, my, zoom_in=False)  # ซูมออก

        elif event.type == pygame.MOUSEMOTION:  # ถ้ามีการเคลื่อนไหวเมาส์
            if dragging_block:  # ถ้ามีบล็อกที่กำลังถูกลาก
                mx, my = pygame.mouse.get_pos()  # รับตำแหน่งเมาส์ปัจจุบัน
                grid_x = (mx - offset_x) // GRID_SIZE  # คำนวณตำแหน่งกริดแนวนอนใหม่
                grid_y = (my - offset_y) // GRID_SIZE  # คำนวณตำแหน่งกริดแนวตั้งใหม่
                dragging_block.x = grid_x  # อัปเดตตำแหน่งแนวนอนของบล็อก
                dragging_block.y = grid_y  # อัปเดตตำแหน่งแนวตั้งของบล็อก

        elif event.type == pygame.MOUSEBUTTONUP:  # ถ้าปล่อยปุ่มเมาส์
            if dragging_block:  # ถ้ามีบล็อกที่ถูกลาก
                dragging_block = None  # ปล่อยบล็อก

    for block in blocks:  # วนซ้ำแต่ละบล็อกเพื่อวาดบนหน้าจอ
        block.draw(screen)  # วาดบล็อก

    if menu_active:  # ถ้าเมนูเปิดอยู่
        draw_menu(menu_x, menu_y)  # วาดเมนูที่ตำแหน่งที่กำหนด

    pygame.display.flip()  # อัปเดตหน้าจอ
    clock.tick(60)  # จำกัดเฟรมเรตที่ 60 FPS

pygame.quit()  # ปิดโปรแกรม pygame
sys.exit()  # ออกจากโปรแกรม
