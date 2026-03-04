import pygame
import cv2
import mediapipe as mp
import sys
import time
import random
import os
import math

# ================= INIT =================
# Pre-initialize the mixer for lower latency and better reliability
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neo-Dino: Multi-Gesture Edition")

clock = pygame.time.Clock()

# ================= THEME COLORS =================
DAY_SKY = (180, 220, 245)
NIGHT_SKY = (15, 20, 45)
DAY_GROUND = (230, 230, 210)
NIGHT_GROUND = (40, 40, 60)
ACCENT_GREEN = (60, 140, 60)
SHADOW_GREEN = (40, 90, 40)
HIGHLIGHT_GREEN = (100, 180, 100)
ACCENT_NIGHT = (80, 100, 180)
WHITE = (255, 255, 255)
BLACK = (33, 33, 33)

# ================= SOUNDS =================
jump_sound = None
# Attempt to load sound files from the current working directory
try:
    # Look for files in the root directory as per recent request
    if os.path.exists("bg_music.wav"):
        pygame.mixer.music.load("bg_music.wav")
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1) # Loop indefinitely
    else:
        print("Warning: bg_music.wav not found in the current directory.")

    if os.path.exists("jump.wav"):
        jump_sound = pygame.mixer.Sound("jump.wav")
        jump_sound.set_volume(0.6)
    else:
        print("Warning: jump.wav not found in the current directory.")
except Exception as e:
    print(f"Detailed Audio Error: {e}")

# ================= FONTS =================
try:
    font_main = pygame.font.SysFont("Segoe UI", 22, bold=True)
    font_large = pygame.font.SysFont("Segoe UI", 48, bold=True)
    font_ui = pygame.font.SysFont("Consolas", 18)
except:
    font_main = pygame.font.SysFont("Arial", 22, bold=True)
    font_large = pygame.font.SysFont("Arial", 48, bold=True)
    font_ui = pygame.font.SysFont("monospace", 18)

# ================= ASSET GENERATION =================
def draw_cloud(surf, x, y, color):
    pygame.draw.circle(surf, color, (x, y), 20)
    pygame.draw.circle(surf, color, (x + 20, y - 5), 25)
    pygame.draw.circle(surf, color, (x + 45, y), 20)
    pygame.draw.circle(surf, color, (x + 25, y + 10), 20)

def draw_cactus_pro(surf, x, y, is_night):
    color = (40, 90, 40) if not is_night else (20, 40, 30)
    pygame.draw.rect(surf, color, (x, y - 50, 15, 50), border_radius=5)
    pygame.draw.rect(surf, color, (x - 12, y - 35, 12, 8), border_radius=3)
    pygame.draw.rect(surf, color, (x - 12, y - 45, 8, 15), border_radius=3)
    pygame.draw.rect(surf, color, (x + 15, y - 25, 12, 8), border_radius=3)
    pygame.draw.rect(surf, color, (x + 19, y - 40, 8, 20), border_radius=3)

def draw_bird_pro(surf, x, y, is_night):
    color = (60, 60, 60) if not is_night else (180, 180, 200)
    wing_color = (40, 40, 40) if not is_night else (150, 150, 170)
    ticks = pygame.time.get_ticks()
    wing_pos = math.sin(ticks * 0.02) * 20
    pygame.draw.ellipse(surf, color, (x, y, 40, 15))
    pygame.draw.circle(surf, color, (x, y + 5), 8)
    pygame.draw.polygon(surf, (255, 165, 0), [(x-8, y+5), (x-18, y+8), (x-8, y+10)])
    pygame.draw.line(surf, wing_color, (x + 20, y + 7), (x + 10, y + 7 - wing_pos), 4)
    pygame.draw.line(surf, wing_color, (x + 20, y + 7), (x + 30, y + 7 - wing_pos), 4)

def draw_dino_realistic(surf, x, y, is_night, is_jumping):
    base_color = ACCENT_GREEN if not is_night else ACCENT_NIGHT
    shadow_color = SHADOW_GREEN if not is_night else (30, 40, 80)
    highlight = HIGHLIGHT_GREEN if not is_night else (120, 140, 220)
    ticks = pygame.time.get_ticks()
    bob = math.sin(ticks * 0.01) * 2 if not is_jumping else 0
    y += bob
    tail_pts = [(x + 5, y + 15), (x - 25, y + 20 + bob), (x + 5, y + 30)]
    pygame.draw.polygon(surf, base_color, tail_pts)
    pygame.draw.ellipse(surf, shadow_color, (x - 2, y + 2, 54, 38))
    pygame.draw.ellipse(surf, base_color, (x, y, 50, 35))
    pygame.draw.ellipse(surf, highlight, (x + 5, y + 5, 30, 10))
    for i in range(4):
        sx = x + 5 + (i * 8)
        sy = y + 2
        pygame.draw.polygon(surf, shadow_color, [(sx, sy), (sx + 4, sy - 8), (sx + 8, sy)])
    pygame.draw.rect(surf, base_color, (x + 35, y - 20, 18, 30), border_radius=4)
    pygame.draw.rect(surf, base_color, (x + 35, y - 35, 35, 18), border_radius=5)
    pygame.draw.line(surf, shadow_color, (x + 45, y - 22), (x + 65, y - 22), 2)
    eye_open = (ticks % 3000) > 150
    eye_color = WHITE if is_night else BLACK
    if eye_open: pygame.draw.circle(surf, eye_color, (x + 58, y - 28), 3)
    else: pygame.draw.line(surf, eye_color, (x + 55, y - 28), (x + 61, y - 28), 2)
    pygame.draw.line(surf, shadow_color, (x + 40, y + 10), (x + 48, y + 15), 3)
    pygame.draw.line(surf, shadow_color, (x + 48, y + 15), (x + 52, y + 12), 3)
    leg_swing = math.sin(ticks * 0.015) * 10 if not is_jumping else 0
    pygame.draw.rect(surf, shadow_color, (x + 10 - leg_swing//2, y + 30, 12, 18), border_radius=4)
    pygame.draw.rect(surf, base_color, (x + 28 + leg_swing//2, y + 30, 12, 20), border_radius=4)

# ================= DATA LOAD/SAVE =================
HIGHSCORE_FILE = "dino_highscore.txt"
high_score = 0
if os.path.exists(HIGHSCORE_FILE):
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            high_score = int(f.read())
    except: pass

def save_highscore():
    global high_score
    if score > high_score:
        high_score = score
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(high_score))

# ================= GAME STATE =================
GROUND_Y = 350
dino_x, dino_y = 100, GROUND_Y - 50
jump, velocity = False, 14
score, speed = 0, 15
game_running, game_over = False, False
is_night = False
clouds = [[random.randint(0, WIDTH), random.randint(50, 150), random.uniform(0.3, 0.8)] for _ in range(6)]
stars = [(random.randint(0, WIDTH), random.randint(0, 220)) for _ in range(60)]
cactus_x = WIDTH
bird_x = -100
bird_y = GROUND_Y - 100
obstacle_type = "cactus"

# ================= MEDIAPIPE GESTURES =================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
last_jump_time = 0
JUMP_COOLDOWN = 0.5

def detect_gestures(lm):
    # ☝️ Index Up: Index tip above PIP, others closed
    index_up = (lm[8].y < lm[6].y and lm[12].y > lm[10].y and lm[16].y > lm[14].y and lm[20].y > lm[18].y)
    # ✊ Fist: All fingers folded (same as jump logic in previous versions)
    fist = (lm[8].y > lm[6].y and lm[12].y > lm[10].y and lm[16].y > lm[14].y and lm[20].y > lm[18].y)
    # 🤙 Shaka: Thumb and Pinky out, middle 3 closed
    thumb_extended = abs(lm[4].x - lm[2].x) > 0.06
    pinky_up = lm[20].y < lm[18].y
    mids_closed = (lm[12].y > lm[10].y and lm[16].y > lm[14].y)
    shaka = thumb_extended and pinky_up and mids_closed
    return index_up, fist, shaka

def reset_game():
    global score, cactus_x, bird_x, game_running, game_over, is_night, speed, velocity, dino_y, obstacle_type
    score = 0
    speed = 15
    cactus_x = WIDTH
    bird_x = -200
    obstacle_type = "cactus"
    game_running = True
    game_over = False
    is_night = False
    velocity = 14
    dino_y = GROUND_Y - 50

# ================= MAIN LOOP =================
while True:
    current_time = time.time()
    sky_color = NIGHT_SKY if is_night else DAY_SKY
    ground_color = NIGHT_GROUND if is_night else DAY_GROUND
    screen.fill(sky_color)
    if is_night:
        for s in stars: pygame.draw.circle(screen, (220, 220, 255), s, random.randint(1, 2))
        pygame.draw.circle(screen, (240, 240, 255), (WIDTH - 120, 80), 40)
        pygame.draw.circle(screen, sky_color, (WIDTH - 140, 80), 40)
    else:
        pygame.draw.circle(screen, (255, 255, 200), (WIDTH - 120, 80), 45)
        for cloud in clouds:
            draw_cloud(screen, int(cloud[0]), cloud[1], (255, 255, 255, 180))
            if game_running and not game_over:
                cloud[0] -= cloud[2]
                if cloud[0] < -100: cloud[0] = WIDTH + 50
    pygame.draw.rect(screen, ground_color, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.line(screen, (0,0,0,30), (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_highscore()
            cap.release()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: speed = min(25, speed + 1)
            if event.key == pygame.K_DOWN: speed = max(3, speed - 1)

    success, frame = cap.read()
    g_up, g_fist, g_shaka = False, False, False
    if success:
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            lm = results.multi_hand_landmarks[0].landmark
            g_up, g_fist, g_shaka = detect_gestures(lm)
            
            # Start logic
            if g_up and not game_running: reset_game()
            
            # Jump logic
            if g_fist and game_running and not game_over and not jump:
                if current_time - last_jump_time > JUMP_COOLDOWN:
                    jump = True
                    last_jump_time = current_time
                    if jump_sound: 
                        # Using a channel play to prevent mixer contention
                        pygame.mixer.find_channel().play(jump_sound)
            
            # Restart logic
            if g_shaka and game_over: reset_game()
            
            mp_draw.draw_landmarks(frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
        
        frame = cv2.resize(frame, (160, 120))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cam_surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        screen.blit(cam_surf, (WIDTH - 180, HEIGHT - 140))
        pygame.draw.rect(screen, WHITE, (WIDTH - 180, HEIGHT - 140, 160, 120), 2)
        
        # UI Status Indicators
        if g_up: pygame.draw.circle(screen, (0, 255, 255), (WIDTH - 170, HEIGHT - 130), 6)
        if g_fist: pygame.draw.circle(screen, (255, 255, 0), (WIDTH - 155, HEIGHT - 130), 6)
        if g_shaka: pygame.draw.circle(screen, (255, 0, 255), (WIDTH - 140, HEIGHT - 130), 6)

    if game_running and not game_over:
        if obstacle_type == "cactus":
            cactus_x -= speed
            if cactus_x < -50:
                score += 1
                if random.random() < 0.3 and score > 5:
                    obstacle_type = "bird"
                    bird_x, bird_y = WIDTH, GROUND_Y - random.choice([50, 110])
                else: cactus_x = WIDTH
        else:
            bird_x -= (speed + 2)
            if bird_x < -50:
                score += 1
                obstacle_type = "cactus"
                cactus_x = WIDTH
        
        if score > 0 and score % 10 == 0: is_night = not is_night
        
        if jump:
            dino_y -= velocity
            velocity -= 1
            if velocity < -14:
                jump, velocity = False, 14
                dino_y = GROUND_Y - 50
        
        dino_rect = pygame.Rect(dino_x + 15, dino_y - 10, 40, 60)
        if obstacle_type == "cactus":
            if dino_rect.colliderect(pygame.Rect(cactus_x + 3, GROUND_Y - 45, 10, 45)):
                game_over = True
                save_highscore()
        else:
            if dino_rect.colliderect(pygame.Rect(bird_x, bird_y, 40, 15)):
                game_over = True
                save_highscore()

    if obstacle_type == "cactus": draw_cactus_pro(screen, cactus_x, GROUND_Y, is_night)
    else: draw_bird_pro(screen, bird_x, bird_y, is_night)
    draw_dino_realistic(screen, dino_x, dino_y, is_night, jump)

    text_color = WHITE if is_night else BLACK
    screen.blit(font_main.render(f"SCORE: {score:04d}", True, text_color), (30, 30))
    screen.blit(font_ui.render(f"BEST: {high_score:04d}", True, text_color), (30, 60))
    screen.blit(font_ui.render(f"SPEED: {speed:.1f} (UP/DOWN)", True, text_color), (30, 85))
    
    if not game_running:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0,0))
        msg = font_large.render("☝️ INDEX UP TO START", True, WHITE)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 40))
    
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((150, 0, 0, 90))
        screen.blit(overlay, (0,0))
        msg = font_large.render("GAME OVER", True, WHITE)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 40))
        btn = font_main.render("🤙 SHAKA TO RESTART", True, WHITE)
        screen.blit(btn, (WIDTH//2 - btn.get_width()//2, HEIGHT//2 + 30))
    
    pygame.display.flip()
    clock.tick(60)