import sys, math, random
import os
import pygame

def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and PyInstaller build."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)  # PyInstaller temp folder
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# Get the directory of the current script and ensure assets path is correct
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Base directory of Game.py
ASSETS_DIR = BASE_DIR  # Ensure ASSETS_DIR directly refers to the folder containing assets

pygame.init()
pygame.mixer.init()

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)

# SCREEN & CLOCK
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Question Blasters by Cristo")
CLOCK = pygame.time.Clock()

# GLOBALS
score = 0
game_over = False
ATTACK_DELAY = 500
last_attack_time = 0
mobs_killed = 0
level = 1

mobs_target = 4
boss_phase = False
player = None
heart_dropped_this_round = False
question_type = "Math"
volume = 0.5

print(f"Base directory: {BASE_DIR}")
print(f"Assets directory: {ASSETS_DIR}")

# Function to load sounds with error checking
def load_sound(filename):
    filepath = resource_path(filename)  # Use resource_path for sound files
    if not os.path.isfile(filepath):
        print(f"Sound file not found: {filepath}")
        raise FileNotFoundError(f"Sound file not found: {filepath}")
    return pygame.mixer.Sound(filepath)

# --- SOUND SETUP ---
try:
    SND_QUESTION_RIGHT = load_sound("question.ogg")
    SND_DEAD = load_sound("dead.ogg")
    SND_MOB_DIE = load_sound("mobdie.ogg")
    SND_COLLECT_HEART = load_sound("collectheart.ogg")

    SND_QUESTION_RIGHT.set_volume(0.7)
    SND_DEAD.set_volume(0.7)
    SND_MOB_DIE.set_volume(0.7)
    SND_COLLECT_HEART.set_volume(0.7)

    pygame.mixer.music.load(resource_path("music.ogg"))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

except FileNotFoundError as e:
    print(e)

# --- UTILITY FUNCTIONS ---
def load_animation_frames(directory, prefix, num_frames, filename_template="{prefix}_{i}.png", scale=1.0):
    frames = []
    for i in range(1, num_frames + 1):
        filename = filename_template.format(prefix=prefix, i=i)
        filepath = os.path.join(resource_path(directory), filename)
        if not os.path.isfile(filepath):
            print(f"Error: {filepath} not found.")
            sys.exit()
        img = pygame.image.load(filepath).convert_alpha()
        if scale != 1.0:
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
        frames.append(img)
    return frames

def load_spritesheet(path, num_frames, scale=1.0):
    filepath = resource_path(path)  # Consistent path handling for spritesheets
    if not os.path.isfile(filepath):
        print(f"Error: {filepath} not found.")
        sys.exit()
    sheet = pygame.image.load(filepath).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // num_frames
    frames = []
    for i in range(num_frames):
        rect = pygame.Rect(i * frame_width, 0, frame_width, sheet_height)
        frame = sheet.subsurface(rect).copy()
        if scale != 1.0:
            new_w = int(frame.get_width() * scale)
            new_h = int(frame.get_height() * scale)
            frame = pygame.transform.scale(frame, (new_w, new_h))
        frames.append(frame)
    return frames

def draw_text(surface, text, pos, color, font=None):
    if font is None:
        font = ASSETS['font']
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_hearts(surface, hp):
    heart_img = ASSETS['heart']
    gap = 5
    for i in range(10):
        x = 10 + i * (heart_img.get_width() + gap)
        y = 10
        if hp >= (i + 1) * 10:
            surface.blit(heart_img, (x, y))
        else:
            pygame.draw.rect(surface, BLACK, (x, y, heart_img.get_width(), heart_img.get_height()), 1)

def draw_boss_health_bar(boss, index=0, total=1):
    bar_width = 300
    bar_height = 20
    y_offset = 40 + index * (bar_height + 10)
    x = (SCREEN_WIDTH - bar_width) // 2
    y = SCREEN_HEIGHT - y_offset
    pygame.draw.rect(SCREEN, BLACK, (x, y, bar_width, bar_height))
    health_percentage = boss.health / boss.initial_health
    fill_width = int(bar_width * health_percentage)
    pygame.draw.rect(SCREEN, (255, 0, 0), (x, y, fill_width, bar_height))
    pygame.draw.rect(SCREEN, WHITE, (x, y, bar_width, bar_height), 2)

def display_fact():
    facts = [
        "GET READY FOR NEXT ROUND"
    ]
    fact = random.choice(facts)
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 3000:
        SCREEN.fill(WHITE)
        text = ASSETS['font'].render(fact, True, BLACK)
        SCREEN.blit(text, ((SCREEN_WIDTH - text.get_width()) // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        CLOCK.tick(60)

# --- ASSET LOADING ---
def load_assets():
    assets = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Base directory for assets

    # Load player animations
    assets['player_animations'] = {
        'idle': load_animation_frames(os.path.join(base_dir, 'idle'), 'idle', 12),
        'run': load_animation_frames(os.path.join(base_dir, 'run'), 'run', 10),
        '1_atk': load_animation_frames(os.path.join(base_dir, '1_atk'), '1_atk', 10)
    }

    # Load soldier animations from spritesheets
    assets['soldier_animations'] = {
        'idle': load_spritesheet(os.path.join(base_dir, 'Soldier-Idle.png'), 6, scale=1.0),
        'walk': load_spritesheet(os.path.join(base_dir, 'Soldier-Walk.png'), 8, scale=1.0)
    }

    # Load orc animations from spritesheets
    assets['orc_animations'] = {
        'idle': load_spritesheet(os.path.join(base_dir, 'Orc-Idle.png'), 6, scale=1.0),
        'walk': load_spritesheet(os.path.join(base_dir, 'Orc-Walk.png'), 8, scale=1.0)
    }

    # Load background images
    assets['level1_bg'] = pygame.image.load(os.path.join(base_dir, 'level1bg.png')).convert()
    assets['level2_bg'] = pygame.image.load(os.path.join(base_dir, 'level2bg.png')).convert()
    assets['level3_bg'] = pygame.image.load(os.path.join(base_dir, 'level3bg.png')).convert()

    # Load other assets
    assets['background'] = pygame.image.load(os.path.join(base_dir, 'background.png')).convert()
    assets['heart'] = pygame.image.load(os.path.join(base_dir, 'heart.png')).convert_alpha()

    # Load font
    font_path = os.path.join(base_dir, 'boxy-bold.ttf')
    if os.path.isfile(font_path):
        assets['font'] = pygame.font.Font(font_path, 16)
    else:
        assets['font'] = pygame.font.SysFont("Arial", 16)

    return assets

ASSETS = load_assets()

# --- DAMAGE INDICATOR CLASS ---
class DamageIndicator(pygame.sprite.Sprite):
    def __init__(self, pos, text="-10"):
        super().__init__()
        self.image = ASSETS['font'].render(text, True, (255,0,0))
        self.rect = self.image.get_rect(center=pos)
        self.timer = 1000  
    def update(self, dt, *args):
        self.timer -= dt
        self.rect.y -= 1 
        if self.timer <= 0:
            self.kill()

# --- HEART PICKUP CLASS ---
class HeartPickup(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = ASSETS['heart']
        self.rect = self.image.get_rect(center=pos)
    def update(self, dt, *args):
        pass

# --- QUESTION BOX FUNCTIONS ---
def draw_question_box(question_text, answer_text, timer_text):
    box_width = 600
    box_height = 130
    box_x = (SCREEN_WIDTH - box_width) // 2
    box_y = SCREEN_HEIGHT - box_height - 60
    pygame.draw.rect(SCREEN, WHITE, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(SCREEN, BLACK, (box_x, box_y, box_width, box_height), 2)
    q_surf = ASSETS['font'].render(question_text, True, BLACK)
    a_surf = ASSETS['font'].render("Answer: " + answer_text, True, BLACK)
    t_surf = ASSETS['font'].render("Time left: " + timer_text, True, BLACK)
    SCREEN.blit(q_surf, (box_x + (box_width - q_surf.get_width()) // 2, box_y + 10))
    SCREEN.blit(a_surf, (box_x + (box_width - a_surf.get_width()) // 2, box_y + 50))
    SCREEN.blit(t_surf, (box_x + (box_width - t_surf.get_width()) // 2, box_y + 90))

def ask_question():
    global question_type
    if question_type == "Math":
        a = random.randint(1, 10 + level*2)
        b = random.randint(1, 10 + level*2)
        op = random.choice(["+", "-"])
        correct = a + b if op=="+" else a - b
        question_text = f"What is {a} {op} {b}?"
    elif question_type == "General Knowledge":
        qas = [("What is capital of France?", "Paris"),
               ("What is largest ocean on Earth?", "Pacific"),
               ("What is capital of Italy?", "Rome"),
               ("Continent with largest area?", "Asia"),
               ("First planet in Solar System?", "Mercury"),
               ("What currency is used in Japan?", "Yen"),
               ("What is capital of Canada?", "Ottawa")]
        question_text, correct = random.choice(qas)
    elif question_type == "Science":
        qas = [("What planet is known as the Red Planet?", "Mars"),
               ("What is H2O commonly known as?", "Water"),
               ("What do plants absorb from atmosphere?", "C02"),
               ("What is chemical symbol for water?", "H2O"),
               ("What process do plants use to make food?", "Photosynthesis"),
               ("What force keeps us on the ground?", "Gravity"),
               ("What is boiling point of water in Celsius?", "100"),
               ("What is main gas found in air we breathe?", "Nitrogen"),
               ("How many planets are in our solar system?", "8"),
               ("What is the center of an atom called?", "Nucleus")]
        question_text, correct = random.choice(qas)
    elif question_type == "History":
        qas = [("First President of US?", "Washington"),
               ("In which year did World War II end?", "1945"),
               ("Who built the pyramids?", "Egyptians"),
               ("Who discovered America in 1492?", "Columbus")]
        question_text, correct = random.choice(qas)
    elif question_type == "Geography":
        qas = [("Longest river in the world?", "Nile"),
              ("Which country largest population?", "China"),
              ("Capital of Australia?", "Canberra"),
              ("Largest desert in the world?", "Antarctica"),  
              ("What ocean is the largest?", "Pacific"),
              ("Country that is an island and continent?", "Australia"),
              ("Which river flows through Paris?", "Seine"),
              ("What is the capital of Spain?", "Madrid")]
        question_text, correct = random.choice(qas)
    elif question_type == "English":
        qas = [("Who wrote 'Romeo and Juliet'?", "Shakespeare"),
              ("What is a synonym of 'happy'?", "joyful"),
              ("What is the plural of 'child'?", "children"),
              ("What is an antonym of 'difficult'?", "Easy"),
              ("Who wrote the novel '1984'?", "George Orwell"),
              ("What does the word 'benevolent' mean?", "Kind"),
              ("What is a homophone for 'pair'?", "Pear"),
              ("What does the prefix 'un-' mean in words like 'unhappy'?", "Not"),
              ("What is the past tense of 'run'?", "Ran"),
              ("Adjective in the sentence: 'The quick brown fox jumps over the lazy dog.'", "Quick"),
              ("What is a synonym for 'brave'?", "Courageous")]
        question_text, correct = random.choice(qas)
    answer = ""
    allowed_time = max(10 - (level - 1), 3)
    start_time = pygame.time.get_ticks()
    asking = True
    failed = False
    while asking:
        elapsed = (pygame.time.get_ticks() - start_time) / 1000.0
        remaining = allowed_time - elapsed
        if remaining <= 0:
            failed = True
            asking = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if answer.strip().lower() == str(correct).lower():
                        asking = False
                        SND_QUESTION_RIGHT.play()
                    else:
                        answer = ""
                        SND_DEAD.play()
                elif event.key == pygame.K_BACKSPACE:
                    answer = answer[:-1]
                else:
                    answer += event.unicode
        draw_question_box(question_text, answer, str(int(remaining)))
        pygame.display.flip()
        CLOCK.tick(30)
    if failed:
        player.take_damage(20)
        SND_DEAD.play()
        return False
    return True

def ask_question_hard():
    global question_type
    if question_type == "Math":
        if random.random() < 0.5:
            a = random.randint(5, 20)
            b = random.randint(5, 20)
            correct = a * b
            question_text = f"What is {a} x {b}?"
        else:
            divisor = random.randint(2, 30)
            quotient = random.randint(2, 30)
            dividend = divisor * quotient
            correct = quotient
            question_text = f"What is {dividend} / {divisor}?"
        allowed_time = max(7 - (level - 1), 3)
    else:
        return ask_question()
    answer = ""
    start_time = pygame.time.get_ticks()
    asking = True
    failed = False
    while asking:
        elapsed = (pygame.time.get_ticks() - start_time) / 1000.0
        remaining = allowed_time - elapsed
        if remaining <= 0:
            failed = True
            asking = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if answer.strip().lower() == str(correct).lower():
                        asking = False
                        SND_QUESTION_RIGHT.play()
                    else:
                        answer = ""
                        SND_DEAD.play()
                elif event.key == pygame.K_BACKSPACE:
                    answer = answer[:-1]
                else:
                    answer += event.unicode
        draw_question_box(question_text, answer, str(int(remaining)))
        pygame.display.flip()
        CLOCK.tick(30)
    if failed:
        return False
    return True

# --- PLAYER CLASS ---
class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.animations = {}
        for state, frames in ASSETS['player_animations'].items():
            self.animations[state] = [pygame.transform.scale(frame, (int(frame.get_width()*1.4), int(frame.get_height()*1.4))) for frame in frames]
        self.state = 'idle'
        self.current_frames = self.animations[self.state]
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.current_frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.position = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(0,0)
        self.health = 100
        self.score = 0
        self.is_attacking_flag = False

    @property
    def is_dead(self):
        return self.health <= 0

    def update(self, dt, keys):
        if self.health <= 0:
            self.state = 'idle'
        self.velocity = pygame.Vector2(0,0)
        if keys[pygame.K_w]:
            self.velocity.y = -1
        if keys[pygame.K_s]:
            self.velocity.y = 1
        if keys[pygame.K_a]:
            self.velocity.x = -1
        if keys[pygame.K_d]:
            self.velocity.x = 1
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize() * 200
            self.state = 'run'
        else:
            self.state = 'idle'
        self.position += self.velocity * (dt/1000)
        self.position.x = max(0, min(self.position.x, SCREEN_WIDTH))
        self.position.y = max(0, min(self.position.y, SCREEN_HEIGHT))
        self.rect.center = self.position
        if self.is_attacking():
            self.state = '1_atk'
        self.current_frames = self.animations[self.state]
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.current_frames):
            self.frame_index = 0
            if self.state == '1_atk':
                self.attack_end()
        self.image = self.current_frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.position)
        self.mask = pygame.mask.from_surface(self.image)

    def is_attacking(self):
        return self.is_attacking_flag

    def attack(self):
        global last_attack_time
        now = pygame.time.get_ticks()
        if now - last_attack_time >= ATTACK_DELAY:
            last_attack_time = now
            self.is_attacking_flag = True
            self.state = "1_atk"
            self.frame_index = 0
            mouse_pos = pygame.mouse.get_pos()
            direction = pygame.Vector2(mouse_pos) - self.position
            if direction.length() == 0:
                direction = pygame.Vector2(1,0)
            else:
                direction = direction.normalize()
            proj = Projectile(self.position, direction)
            projectile_group.add(proj)
            all_sprites.add(proj)

    def attack_end(self):
        self.is_attacking_flag = False

    def take_damage(self, dmg):
        self.health -= dmg

        # damage indicator
        indicator = DamageIndicator(self.rect.midtop, text=f"-{dmg}")
        all_sprites.add(indicator)
        if self.health < 0:
            self.health = 0
            SND_DEAD.play()

# --- ENEMY CLASS (mobs: "small" and "medium") ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, enemy_type, variant="medium"):
        super().__init__()
        self.enemy_type = enemy_type
        self.variant = variant
        self.position = pygame.Vector2(pos)

        # Base attributes for enemy type
        if enemy_type == "soldier":
            base_speed = random.uniform(120, 160) * 0.7
            base_health = 50
            base_scale = 2.0  # Increased base scale for better visibility
        else:  # Orc
            base_speed = random.uniform(60, 80) * 0.9
            base_health = 80
            base_scale = 2.5  # Slightly larger orcs

        # Adjust attributes based on variant
        if variant == "small":
            self.scale = base_scale * 0.8  # 80% of the base size
            self.health = int(base_health * 0.6)  # Reduced health for small variant
            self.speed = base_speed * 1.3  # Increased speed for small variant
        else:  # Default to "medium" size
            self.scale = base_scale
            self.health = base_health
            self.speed = base_speed

        # Load animations based on enemy type
        if enemy_type == "soldier":
            base_anim = ASSETS['soldier_animations']
        else:
            base_anim = ASSETS['orc_animations']

        # Scale animations based on calculated scale factor
        self.animations = {
            'idle': [pygame.transform.scale(frame, (int(frame.get_width() * self.scale), int(frame.get_height() * self.scale))) for frame in base_anim['idle']],
            'walk': [pygame.transform.scale(frame, (int(frame.get_width() * self.scale), int(frame.get_height() * self.scale))) for frame in base_anim['walk']]
        }

        # Set initial state and animation
        self.state = "walk"
        self.frame_index = 0
        self.animation_speed = 0.2  # Adjust animation speed as needed
        self.current_frames = self.animations[self.state]
        self.image = self.current_frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.last_hit_time = 0
        self.shot_cooldown = 0

    def update(self, dt, *args):
        # Move towards the player
        if player and not player.is_dead:
            direction = pygame.Vector2(player.rect.center) - self.position
            if direction.length() > 0:
                direction = direction.normalize()
                self.position += direction * self.speed * (dt / 1000)

                # Ensure the enemy stays within screen bounds
                self.position.x = max(0, min(self.position.x, SCREEN_WIDTH))
                self.position.y = max(0, min(self.position.y, SCREEN_HEIGHT))
                self.rect.center = self.position

        # Update animation
        self.current_frames = self.animations[self.state]
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.current_frames):
            self.frame_index = 0
        self.image = self.current_frames[int(self.frame_index)]

        # Update position and collision mask
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            self.health = 0
            SND_MOB_DIE.play()
            self.kill()


# --- PROJECTILE CLASS (Player's bullet) ---
class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, attack_type="default"):
        super().__init__()
        self.damage = 25
        self.image = pygame.Surface((15,5), pygame.SRCALPHA)
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=pos)
        self.velocity = direction * 250
        angle = math.degrees(math.atan2(-direction.y, direction.x))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=pos)
    def update(self, dt, *args):
        movement = self.velocity * (dt/1000)
        self.rect.centerx += movement.x
        self.rect.centery += movement.y
        if not SCREEN.get_rect().colliderect(self.rect):
            self.kill()

class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, damage=10):
        super().__init__()
        self.damage = damage
        self.image = pygame.Surface((15,5), pygame.SRCALPHA)
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(center=pos)
        self.velocity = direction * 200
        angle = math.degrees(math.atan2(-direction.y, direction.x))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=pos)
    def update(self, dt, *args):
        movement = self.velocity * (dt/1000)
        self.rect.centerx += movement.x
        self.rect.centery += movement.y
        if not SCREEN.get_rect().colliderect(self.rect):
            self.kill()

class FireballProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super().__init__()
        # Load the fireball image using resource_path
        self.image = pygame.image.load(resource_path("fireball.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))  # Scale fireball to 50x50
        angle = math.degrees(math.atan2(-direction.y, direction.x))
        self.image = pygame.transform.rotate(self.image, angle)  # Rotate fireball based on direction
        self.rect = self.image.get_rect(center=pos)

        # Set velocity and damage
        self.velocity = direction * 150  # Fireball speed (adjust as needed)
        self.damage = 40

    def update(self, dt, *args):
        # Update fireball position based on velocity and delta time
        movement = self.velocity * (dt / 1000)  # Scale movement to time elapsed
        self.rect.centerx += movement.x
        self.rect.centery += movement.y

        # Remove fireball if it moves outside the screen boundaries
        if not SCREEN.get_rect().colliderect(self.rect):
            self.kill()


# --- FINAL BOSS CLASS ---
class FinalBoss(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load(resource_path("idleboss.png")).convert_alpha()
        print(resource_path("idleboss.png"))
        self.image = pygame.transform.scale(self.image, (500, 500))
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.position = pygame.Vector2(pos)
        self.health = 500
        self.initial_health = self.health
        self.speed = 20
        self.fireball_timer = 4000
        self.hit_count = 2
        self.questions_asked_count = 6
        self.last_hit_time = 20
        
    def update(self, dt, *args):
        if player and not player.is_dead:
            direction = pygame.Vector2(player.rect.center) - self.position
            if direction.length() > 0:
                direction = direction.normalize()
                self.position += direction * self.speed * (dt/1000)
                self.position.x = max(0, min(self.position.x, SCREEN_WIDTH))
                self.position.y = max(0, min(self.position.y, SCREEN_HEIGHT))
                self.rect.center = self.position
        self.fireball_timer -= dt
        if self.fireball_timer <= 0:
            if player and not player.is_dead:
                direction = pygame.Vector2(player.rect.center) - self.position
                if direction.length() != 0:
                    direction = direction.normalize()
                    fireball = FireballProjectile(self.position, direction)
                    projectile_group.add(fireball)
                    all_sprites.add(fireball)
            self.fireball_timer = 2000
        
# --- MINIBOSS CLASS (for levels < 4) ---
class Miniboss(Enemy):
    def __init__(self, pos, enemy_type):
        self.scale = 10.0
        super().__init__(pos, enemy_type, variant="big")
        if enemy_type == "soldier":
            self.health = 200
            self.speed = 50
        elif enemy_type == "orc":
            self.health = 300
            self.speed = 30
            self.orc_attack_timer = 0
        self.initial_health = self.health
        self.boss = True
        self.shot_timer = 0
        self.orc_attack_timer = 0
        self.question_thresholds = [0.75, 0.50, 0.25]
        self.questions_asked = [False, False, False]
    def update(self, dt, *args):
        if player and not player.is_dead:
            direction = pygame.Vector2(player.rect.center) - self.position
            if direction.length() > 0:
                direction = direction.normalize()
                self.position += direction * self.speed * (dt/1000)
                self.position.x = max(0, min(self.position.x, SCREEN_WIDTH))
                self.position.y = max(0, min(self.position.y, SCREEN_HEIGHT))
                self.rect.center = self.position
        self.current_frames = self.animations[self.state]
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.current_frames):
            self.frame_index = 0
        self.image = self.current_frames[int(self.frame_index)]
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.mask = pygame.mask.from_surface(self.image)
        if self.enemy_type == "soldier":
            if self.shot_timer <= 0:
                self.shoot_spread()
                self.shot_timer = 3000
            else:
                self.shot_timer -= dt
        elif self.enemy_type == "orc":
            if self.orc_attack_timer <= 0:
                self.shoot_ring()
                self.orc_attack_timer = 4000
            else:
                self.orc_attack_timer -= dt
        for i, threshold in enumerate(self.question_thresholds):
            if not self.questions_asked[i] and self.health <= self.initial_health*threshold:
                if not ask_question_hard():
                    player.take_damage(20)
                self.questions_asked[i] = True
    def shoot_spread(self):
        base_direction = pygame.Vector2(player.rect.center) - self.position
        if base_direction.length() == 0:
            base_direction = pygame.Vector2(1,0)
        else:
            base_direction = base_direction.normalize()
        for angle in [-15, 0, 15]:
            rad = math.radians(angle)
            rotated = pygame.Vector2(
                base_direction.x*math.cos(rad) - base_direction.y*math.sin(rad),
                base_direction.x*math.sin(rad) + base_direction.y*math.cos(rad)
            )
            bullet = EnemyProjectile(self.position, rotated, damage=15)
            all_sprites.add(bullet)
            projectile_group.add(bullet)
    def shoot_ring(self):
        for i in range(8):
            angle = math.radians(i*45)
            direction = pygame.Vector2(math.cos(angle), math.sin(angle))
            bullet = EnemyProjectile(self.position, direction, damage=20)
            all_sprites.add(bullet)
            projectile_group.add(bullet)

# --- BACKGROUND HANDLING ---
def get_background():
    if level == 1:
        return ASSETS['level1_bg']
    elif level == 2:
        return ASSETS['level2_bg']    
    elif level == 3:
        return ASSETS['level3_bg']
    else:
        return ASSETS['level1_bg']

# --- MAIN MENU WITH OPTIONS ---
def main_menu():
    global question_type, volume
    base_dir = os.path.dirname(__file__)
    menu_path = os.path.join(base_dir, "menu.png")
    if os.path.isfile(menu_path):
        menu_bg = pygame.image.load(menu_path).convert()
        menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        menu_bg = None

    state = "main"  # "main", "guide", "options", "qtype"
    selection = 0
    options_main = ["Start Game", "Guide", "Options", "Quit"]
    options_qtype = ["Math", "General Knowledge", "Science", "History", "Geography", "English"]
    while True:
        SCREEN.fill(BLACK)
        if menu_bg:
            SCREEN.blit(menu_bg, (0,0))
        if state == "main":
            title = ASSETS['font'].render("Question Blasters By Cristo", True, WHITE)
            SCREEN.blit(title, ((SCREEN_WIDTH-title.get_width())//2, 50))
            for i, opt in enumerate(options_main):
                color = WHITE if i==selection else (150,150,150)
                text = ASSETS['font'].render(opt, True, color)
                SCREEN.blit(text, ((SCREEN_WIDTH-text.get_width())//2, 150+i*50))
        elif state == "guide":
            guide_text = [
                "Guide - How to Play:",
                "Move: WASD",
                "Shoot: Click mouse or press on screen",
                "Answer questions in the box at bottom center.",
                "W/S: Navigate, Enter: Submit answer.",
                "Collect hearts to replenish health.",
                "",
                "Press space to return."
            ]
            for i, line in enumerate(guide_text):
                text = ASSETS['font'].render(line, True, WHITE)
                SCREEN.blit(text, (50, 100+i*30))
        elif state == "options":
            opt_text = "Volume: " + str(int(volume*100)) + "%"
            text = ASSETS['font'].render(opt_text, True, WHITE)
            SCREEN.blit(text, ((SCREEN_WIDTH-text.get_width())//2, 150))
            bar_width = 300
            bar_height = 20
            bar_x = (SCREEN_WIDTH-bar_width)//2
            bar_y = 200
            pygame.draw.rect(SCREEN, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
            fill_width = int(bar_width*volume)
            pygame.draw.rect(SCREEN, WHITE, (bar_x, bar_y, fill_width, bar_height))
            prompt = ASSETS['font'].render("Use LEFT/RIGHT to adjust. Space to return.", True, WHITE)
            SCREEN.blit(prompt, ((SCREEN_WIDTH-prompt.get_width())//2, 250))
        elif state == "qtype":
            title = ASSETS['font'].render("Select Question Type:", True, WHITE)
            SCREEN.blit(title, ((SCREEN_WIDTH-title.get_width())//2, 100))
            for i, opt in enumerate(options_qtype):
                color = WHITE if i==selection else (150,150,150)
                text = ASSETS['font'].render(opt, True, color)
                SCREEN.blit(text, ((SCREEN_WIDTH-text.get_width())//2, 200+i*50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if state in ["main", "qtype"]:
                    if event.key == pygame.K_w:
                        if state == "main":
                            selection = (selection - 1) % len(options_main)
                        else:
                            selection = (selection - 1) % len(options_qtype)
                    elif event.key == pygame.K_s:
                        if state == "main":
                            selection = (selection + 1) % len(options_main)
                        else:
                            selection = (selection + 1) % len(options_qtype)
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if state == "main":
                            chosen = options_main[selection]
                            if chosen == "Start Game":
                                state = "qtype"
                                selection = 0
                            elif chosen == "Guide":
                                state = "guide"
                            elif chosen == "Options":
                                state = "options"
                            elif chosen == "Quit":
                                input("Press Enter to exit...")
                                pygame.quit(); sys.exit()
                        elif state == "qtype":
                            question_type = options_qtype[selection]
                            return
                elif state == "guide":
                    if event.key == pygame.K_SPACE:
                        state = "main"
                        selection = 0
                elif state == "options":
                    if event.key == pygame.K_LEFT:
                        volume = max(0.0, volume - 0.1)
                        pygame.mixer.music.set_volume(volume*0.6)
                    elif event.key == pygame.K_RIGHT:
                        volume = min(1.0, volume + 0.1)
                        pygame.mixer.music.set_volume(volume*0.6)
                    elif event.key == pygame.K_SPACE:
                        state = "main"
                        selection = 0
        CLOCK.tick(30)

# --- MAIN GAME LOOP ---
def main():
    global all_sprites, enemy_group, projectile_group, boss_group, heart_pickup_group
    global score, game_over, mobs_killed, last_attack_time, player, level, mobs_target, boss_phase, heart_dropped_this_round, question_type
    score = 0
    game_over = False
    mobs_killed = 0
    level = 1
    mod = level % 3
    if mod == 1:
        mobs_target = 2
    elif mod == 2:
        mobs_target = 3
    else:
        mobs_target = 4
    boss_phase = False
    heart_dropped_this_round = False
    last_attack_time = 0

    all_sprites = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    projectile_group = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    heart_pickup_group = pygame.sprite.Group()

    player = Player((SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    all_sprites.add(player)
    last_spawn_time = pygame.time.get_ticks()

    while True:
        dt = CLOCK.tick(60)
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_over:
                    player.attack()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (player.is_dead or game_over):
                    main()

        keys = pygame.key.get_pressed()
        player.update(dt, keys)
        enemy_group.update(dt, keys)
        projectile_group.update(dt, keys)
        boss_group.update(dt, keys)
        heart_pickup_group.update(dt, keys)
        all_sprites.update(dt, keys)

        # Spawn normal enemies (small and medium)
        if not boss_phase:
            spawn_interval = max(3000 - (level-1)*200, 800)
            if current_time - last_spawn_time >= spawn_interval:
                side = random.choice(['top','right','bottom','left'])
                if side == 'top':
                    x = random.randint(0, SCREEN_WIDTH)
                    y = -50
                elif side == 'right':
                    x = SCREEN_WIDTH+50
                    y = random.randint(0, SCREEN_HEIGHT)
                elif side == 'bottom':
                    x = random.randint(0, SCREEN_WIDTH)
                    y = SCREEN_HEIGHT+50
                else:
                    x = -50
                    y = random.randint(0, SCREEN_HEIGHT)
                if level == 1:
                    enemy_type = "soldier"
                elif level == 2:
                    enemy_type = "orc"
                else:
                    enemy_type = random.choice(["soldier", "orc"])
                rnd = random.random()
                if rnd < 0.3:
                    variant = "small"
                else:
                    variant = "medium"
                enemy = Enemy((x,y), enemy_type, variant)
                enemy_group.add(enemy)
                all_sprites.add(enemy)
                last_spawn_time = current_time

        for enemy in enemy_group.copy():
            for proj in projectile_group.copy():
                if pygame.sprite.collide_mask(enemy, proj):
                    enemy.take_damage(proj.damage)
                    proj.kill()
                    if enemy.health <= 0:
                        if boss_phase:
                            enemy.kill()
                            mobs_killed += 1
                            score += 10
                            if random.random() < 0.3:
                                heart = HeartPickup(enemy.rect.center)
                                heart_pickup_group.add(heart)
                                all_sprites.add(heart)
                                SND_MOB_DIE.play()
                        else:
                            if ask_question():
                                enemy.kill()
                                mobs_killed += 1
                                score += 10
                                SND_QUESTION_RIGHT.play()
                                if random.random() < 0.3:
                                    heart = HeartPickup(enemy.rect.center)
                                    heart_pickup_group.add(heart)
                                    all_sprites.add(heart)
                                    SND_MOB_DIE.play()
                            else:
                                enemy.health = 10

        for boss in boss_group.copy():
            # If the boss is FinalBoss, process hits differently:
            if isinstance(boss, FinalBoss):
                for proj in projectile_group.copy():
                    if pygame.sprite.collide_mask(boss, proj):
                        boss.hit_count += 1
                        proj.kill()
                        if boss.hit_count >= 2 and boss.questions_asked_count < 5:
                            if not ask_question_hard():
                                player.take_damage(20)
                            boss.hit_count = 0
                            boss.questions_asked_count += 1
                        else:
                            boss.health -= 25 
                if boss.health <= 0:
                    boss.kill()
            else:
                for proj in projectile_group.copy():
                    if pygame.sprite.collide_mask(boss, proj):
                        if ask_question():
                            boss.take_damage(proj.damage)
                            proj.kill()
                            SND_QUESTION_RIGHT.play()
                        else:
                            proj.kill()
                            SND_DEAD.play()
                if boss.health <= 0:
                    boss.kill()
        # When boss phase ends, update level.
        if boss_phase and len(boss_group) == 0:
            boss_phase = False
            mobs_killed = 0
            mod = (level+1) % 3
            if mod == 1:
                mobs_target = 8
            elif mod == 2:
                mobs_target = 4
            else:
                mobs_target = 5
            level += 1
            heart_dropped_this_round = False
            display_fact()

        # Process enemy-player collisions.
        for enemy in enemy_group:
            if pygame.sprite.collide_mask(enemy, player):
                if current_time - enemy.last_hit_time >= 500:
                    player.take_damage(5)
                    enemy.last_hit_time = current_time
        for boss in boss_group:
            if pygame.sprite.collide_mask(boss, player):
                if current_time - getattr(boss, "last_hit_time", 0) >= 6000:
                    player.take_damage(30)
                    boss.last_hit_time = current_time
        # Process heart pickup collisions.
        for heart in heart_pickup_group.copy():
            if pygame.sprite.collide_rect(heart, player):
                if player.health < 100:
                    player.health = min(100, player.health+20)
                    heart.kill()
                    SND_COLLECT_HEART.play()

        if player.is_dead:
            game_over = True

        # Trigger boss phase.
        if not boss_phase and mobs_killed >= mobs_target:
            boss_phase = True
            for enemy in enemy_group:
                enemy.kill()
            if level == 4:
                final_boss = FinalBoss((random.randint(100, SCREEN_WIDTH-100), -50))
                boss_group.add(final_boss)
                all_sprites.add(final_boss)
            else:
                round_type = level % 3
                if round_type == 1:
                    boss = Miniboss((random.randint(100, SCREEN_WIDTH-100), -50), "soldier")
                    boss_group.add(boss)
                    all_sprites.add(boss)
                elif round_type == 2:
                    boss = Miniboss((random.randint(100, SCREEN_WIDTH-100), -50), "orc")
                    boss_group.add(boss)
                    all_sprites.add(boss)
                else:
                    boss1 = Miniboss((random.randint(100, SCREEN_WIDTH-100), -50), "soldier")
                    boss2 = Miniboss((random.randint(100, SCREEN_WIDTH-100), -50), "orc")
                    boss_group.add(boss1)
                    boss_group.add(boss2)
                    all_sprites.add(boss1)
                    all_sprites.add(boss2)

        bg = get_background()
        SCREEN.blit(bg, (0,0))
        all_sprites.draw(SCREEN)
        enemy_group.draw(SCREEN)
        projectile_group.draw(SCREEN)
        boss_group.draw(SCREEN)
        heart_pickup_group.draw(SCREEN)
        draw_text(SCREEN, f"Score: {score}", (10,40), WHITE)
        draw_text(SCREEN, f"Level: {level}", (10,80), WHITE)
        draw_text(SCREEN, f"Mobs left: {max(mobs_target-mobs_killed,0)}", (SCREEN_WIDTH-170, SCREEN_HEIGHT-30), WHITE)
        if boss_phase and len(boss_group)>0:
            bosses = list(boss_group)
            if len(bosses)==1:
                draw_boss_health_bar(bosses[0])
            else:
                for idx, b in enumerate(bosses):
                    draw_boss_health_bar(b, index=idx, total=len(bosses))
        draw_hearts(SCREEN, player.health)
        pygame.display.flip()

        if game_over:
            SCREEN.fill(BLACK)
            draw_text(SCREEN, "GAME OVER", ((SCREEN_WIDTH-200)//2, SCREEN_HEIGHT//2-50), WHITE)
            draw_text(SCREEN, f"Final Score: {score}", ((SCREEN_WIDTH-200)//2, SCREEN_HEIGHT//2), WHITE)
            pygame.display.flip()
            pygame.time.delay(3000)
            main_menu()
            main()

if __name__ == "__main__":
    main_menu()
    main()