import pygame
import sys
import os
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Educational FPS Game")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Load assets function
def load_image(directory, filename):
    return pygame.image.load(os.path.join(directory, filename)).convert_alpha()

# Load Font
font_path = os.path.join('boxy-bold.ttf')
game_font = pygame.font.Font(font_path, 24)

# Load Tile Images (from 'crawl tiles/')
dungeon_floor = load_image('crawl tiles', 'dungeon_floor.png')
dungeon_wall = load_image('crawl tiles', 'dungeon_wall.png')
# Add more tile images as needed

# Load Interface Images (from 'crawl interface/')
minimap = load_image('crawl interface', 'minimap.png')
minimap_cursor = load_image('crawl interface', 'minimap_cursor.png')
# Add more interface images as needed

# Load Weapon Images (from 'crawl interface/')
weapon_images = {
    1: load_image('crawl interface', 'bone_shield.png'),
    2: load_image('crawl interface', 'weapon_upgrade1.png'),
    3: load_image('crawl interface', 'weapon_upgrade2.png'),
    4: load_image('crawl interface', 'weapon_upgrade3.png'),
}

# Load Enemy Images (from 'crawl enemies/')
enemy_images = {
    'death_speaker': load_image('crawl enemies', 'death_speaker.png'),
    'druid': load_image('crawl enemies', 'druid.png'),
    'imp': load_image('crawl enemies', 'imp.png'),
    'mimic': load_image('crawl enemies', 'mimic.png'),
    'shadow_soul': load_image('crawl enemies', 'shadow_soul.png'),
    'skeleton': load_image('crawl enemies', 'skeleton.png'),
    'zombie': load_image('crawl enemies', 'zombie.png'),
    # Add more enemy images as needed
}

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.weapon_level = 1
        self.image = weapon_images[self.weapon_level]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.health = 100
        self.score = 0
        self.speed = 5

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys_pressed[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys_pressed[pygame.K_DOWN]:
            self.rect.y += self.speed
        # Keep player on screen
        self.rect.clamp_ip(screen.get_rect())

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def display_health(self, surface):
        health_text = game_font.render(f'Health: {self.health}', True, (255, 255, 255))
        surface.blit(health_text, (10, 10))

    def display_score(self, surface):
        score_text = game_font.render(f'Score: {self.score}', True, (255, 255, 255))
        surface.blit(score_text, (10, 40))

# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.health = 50
        self.speed = 2

    def update(self, player):
        # Move towards player
        direction = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        if direction.length() != 0:
            direction = direction.normalize()
            self.rect.center += direction * self.speed

# Bullet Class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=pos)
        self.velocity = direction * 10

    def update(self):
        self.rect.center += self.velocity
        # Remove bullet if it goes off-screen
        if not screen.get_rect().collidepoint(self.rect.center):
            self.kill()

# Function to ask a question and return True if answered correctly
def ask_question():
    # Simple list of questions and answers
    questions = [
        ("What is 5 + 7?", "12"),
        ("What is the capital of France?", "Paris"),
        ("Solve for x: 2x = 10", "5"),
        ("What is the largest planet?", "Jupiter"),
    ]
    question, correct_answer = random.choice(questions)
    player_answer = ""
    asking = True
    while asking:
        screen.fill((0, 0, 0))
        question_text = game_font.render(question, True, (255, 255, 255))
        answer_text = game_font.render(f'Your Answer: {player_answer}', True, (255, 255, 255))
        instruction_text = game_font.render('Type your answer and press Enter:', True, (255, 255, 255))
        screen.blit(question_text, (50, 200))
        screen.blit(answer_text, (50, 250))
        screen.blit(instruction_text, (50, 150))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Check the answer
                    if player_answer.strip().lower() == correct_answer.lower():
                        return True
                    else:
                        return False
                elif event.key == pygame.K_BACKSPACE:
                    player_answer = player_answer[:-1]
                else:
                    player_answer += event.unicode
    return False

# Function to draw the game environment
def draw_environment():
    # Fill the screen with the dungeon floor
    screen.blit(dungeon_floor, (0, 0))
    # Additional tiles can be drawn here if needed

# Initialize player and sprite groups
player = Player()
player_group = pygame.sprite.Group(player)
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

# Spawn initial enemies
def spawn_enemies(num_enemies):
    for _ in range(num_enemies):
        enemy_type = random.choice(list(enemy_images.keys()))
        enemy_image = enemy_images[enemy_type]
        enemy_pos = (
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT),
        )
        enemy = Enemy(enemy_image, enemy_pos)
        enemy_group.add(enemy)

spawn_enemies(5)

# Main game loop
running = True
while running:
    clock.tick(60)  # Maintain 60 FPS
    keys_pressed = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Shooting mechanics
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Shoot a bullet upwards
                direction = pygame.math.Vector2(0, -1)
                bullet = Bullet(player.rect.center, direction)
                bullet_group.add(bullet)

    # Update player and sprites
    player.update(keys_pressed)
    enemy_group.update(player)
    bullet_group.update()

    # Collision detection between bullets and enemies
    for bullet in bullet_group:
        hit_enemies = pygame.sprite.spritecollide(bullet, enemy_group, False)
        for enemy in hit_enemies:
            bullet.kill()
            enemy.health -= 25
            if enemy.health <= 0:
                enemy.kill()
                player.score += 10
                # Pause the game and ask a question
                correct = ask_question()
                if correct:
                    # Upgrade the player's weapon if answered correctly
                    if player.weapon_level < len(weapon_images):
                        player.weapon_level += 1
                        player.image = weapon_images[player.weapon_level]
                        print("Correct! Weapon upgraded.")
                    else:
                        print("Correct! Maximum weapon level reached.")
                else:
                    # Reduce player's health if answered incorrectly
                    player.health -= 20
                    print("Incorrect! Health reduced.")

    # Collision detection between player and enemies
    if pygame.sprite.spritecollide(player, enemy_group, False):
        player.health -= 1  # Reduce health if collided with enemy

    # Check for game over
    if player.health <= 0:
        print("Game Over!")
        running = False

    # Draw everything
    draw_environment()
    player_group.draw(screen)
    enemy_group.draw(screen)
    bullet_group.draw(screen)
    player.display_health(screen)
    player.display_score(screen)
    # Update the display
    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()
