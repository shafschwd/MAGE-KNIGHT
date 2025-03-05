import pygame
from utils import load_image

class Player:
    def __init__(self, x, y):
        # Store initial position as spawn point
        self.spawn_x = x
        self.spawn_y = y
        
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
        self.JUMP_SPEED = -15
        
        # Death and respawn
        self.is_dead = False
        self.respawn_timer = 0
        self.RESPAWN_DELAY = 60  # frames to wait before respawning (1 second at 60 FPS)

    def handle_input(self, controls):
        """Check input using the controls system."""
        self.vx = 0
        
        # Horizontal movement
        if controls.is_pressed('move_left'):
            self.vx = -self.SPEED
        if controls.is_pressed('move_right'):
            self.vx = self.SPEED

        # Jump - using just_pressed to avoid holding jump
        if controls.is_pressed('jump') and self.on_ground:
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
    
    def check_death(self, level_height, death_zones=None):
        """Check if player has died from falling or hitting a death zone."""
        # Die if fallen off the level
        if self.rect.y > level_height:
            self.die()
        
        # Check for collision with death zones if provided
        if death_zones:
            for zone in death_zones:
                if self.rect.colliderect(zone):
                    self.die()
    
    def die(self):
        """Handle player death."""
        if not self.is_dead:
            self.is_dead = True
            self.respawn_timer = 0
            # You could add sound effects or death animation here
    
    def respawn(self):
        """Reset player to spawn position."""
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.vx = 0
        self.vy = 0
        self.is_dead = False
        # You could add spawn animation or invulnerability frames here
    
    def update(self, tiles, controls, level_height, death_zones=None):
        # Check for respawn if dead
        if self.is_dead:
            self.respawn_timer += 1
            if self.respawn_timer >= self.RESPAWN_DELAY:
                self.respawn()
            return  # Skip normal updates if dead
            
        # 1. Handle keyboard input (movement, jump)
        self.handle_input(controls)

        # 2. Gravity
        self.apply_gravity()

        # 3. Move and collide
        self.move_and_collide(tiles)
        
        # 4. Check if player has fallen off the level
        self.check_death(level_height, death_zones)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
