import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 700, 700

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Educational Game")

# Load background images
background1 = pygame.image.load("level1-1.png")
background2 = pygame.image.load("level1-2.png")

# Load player images
player_idle = pygame.image.load("Idle.png")
player_attack1 = pygame.image.load("Attack1.png")
player_attack2 = pygame.image.load("Attack2.png")
player_attack3 = pygame.image.load("Attack3.png")
player_attack4 = pygame.image.load("Attack4.png")
player_bullet = pygame.image.load("Bullet.png")
player_death = pygame.image.load("Death.png")
player_hurt = pygame.image.load("Hurt.png")
player_sneer = pygame.image.load("Sneer.png")
player_walk = pygame.image.load("Walk.png")

# Define player settings
player = {
    'image': player_idle,  # Start with the idle image
    'x': 50,
    'y': 600,
    'width': player_idle.get_width(),
    'height': player_idle.get_height(),
    'speed': 5,
    'is_alive': True
}

# Define scrolling settings
background_width = background1.get_width()
scroll_x = 0

# Define gravity and player falling
gravity = 1
fall_speed = 0
ground_level = SCREEN_HEIGHT - player['height']

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle player input (walking)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player['is_alive']:
        player['image'] = player_walk
        player['x'] -= player['speed']
        scroll_x += player['speed']
    if keys[pygame.K_RIGHT] and player['is_alive']:
        player['image'] = player_walk
        player['x'] += player['speed']
        scroll_x -= player['speed']
    if keys[pygame.K_UP] and player['is_alive']:
        player['image'] = player_walk
        player['y'] -= player['speed']
    if keys[pygame.K_DOWN] and player['is_alive']:
        player['image'] = player_walk
        player['y'] += player['speed']

    # Apply gravity
    if player['y'] < ground_level and player['is_alive']:
        fall_speed += gravity
        player['y'] += fall_speed
    else:
        fall_speed = 0

    # Check if player falls off the map
    if player['y'] > ground_level:
        player['image'] = player_death
        player['is_alive'] = False

    # Scroll the background images
    screen.blit(background1, (scroll_x % background_width, 0))
    screen.blit(background2, ((scroll_x % background_width) + background_width, 0))

    # Draw the player
    screen.blit(player['image'], (player['x'], player['y']))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
