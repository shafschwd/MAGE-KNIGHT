import pygame
from utils import load_image

class Player:
    def __init__(self, x, y):
        # Load the player sprite from assets folder
        self.image = load_image('player.png')
        
        # Fallback if loading failed
        if self.image is None:
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 255, 255))  # White color
            
        self.rect = self.image.get_rect(topleft=(x, y))

        # Player velocity
        self.vx = 0
        self.vy = 0

        # Used to track if we're on the ground
        self.on_ground = False
        
        # Constants
        self.SPEED = 4
        self.GRAVITY = 0.5
        self.JUMP_SPEED = -10

    def handle_input(self):
        """Check which keys are pressed and adjust horizontal velocity."""
        keys = pygame.key.get_pressed()
        
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -self.SPEED
        if keys[pygame.K_RIGHT]:
            self.vx = self.SPEED

        # Jump only if on the ground
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = self.JUMP_SPEED

    def apply_gravity(self):
        """Apply gravity to vy."""
        self.vy += self.GRAVITY

    def move_and_collide(self, tiles):
        """
        Move the player by (vx, vy). Then check collision with tiles.
        We'll handle x and y axes separately for reliable collisions.
        """
        # Move horizontally
        self.rect.x += self.vx
        # Check collisions on the X axis
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vx > 0:  # moving right
                    self.rect.right = tile.rect.left
                elif self.vx < 0:  # moving left
                    self.rect.left = tile.rect.right

        # Move vertically
        self.rect.y += self.vy
        # Check collisions on the Y axis
        self.on_ground = False  # We'll set this to True if we land on something
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vy > 0:  # falling down
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:  # moving up
                    self.rect.top = tile.rect.bottom
                    self.vy = 0

    def update(self, tiles):
        # 1. Handle keyboard input (movement, jump)
        self.handle_input()

        # 2. Gravity
        self.apply_gravity()

        # 3. Move and collide
        self.move_and_collide(tiles)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
