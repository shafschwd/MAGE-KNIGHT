import pygame
import random
import math
import sys
import os
from utils.audioplayer import play_audio_clip

# Fix imports to work correctly within the project structure
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from utils.utils import load_image, get_file_path, FILETYPE
else:
    from utils.utils import load_image, get_file_path, FILETYPE

from utils.animationplayer import AnimationPlayer

class EnemyProjectile:
    """A gooey slime projectile fired by flying enemies"""
    def __init__(self, x, y, vx, vy, size=8):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.base_size = size
        self.size = size
        self.lifetime = 120  # 2 seconds at 60fps
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
        
        # Slime properties
        self.wobble_time = 0
        self.wobble_speed = 0.2
        self.stretch_x = 1.0
        self.stretch_y = 1.0
        self.trail = []  # Stores positions for slime trail
        self.trail_timer = 0
        self.color = (80, 230, 100)  # Slime green
        
    def update(self):
        # Previous position for trail
        prev_x, prev_y = self.x, self.y
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Apply slight gravity
        self.vy += 0.1
        
        # Calculate stretch based on velocity (makes it look like it stretches when moving)
        speed = math.sqrt(self.vx**2 + self.vy**2)
        self.stretch_x = 1.0 + abs(self.vx) * 0.05
        self.stretch_y = 1.0 + abs(self.vy) * 0.05
        
        # Add wobble effect
        self.wobble_time += self.wobble_speed
        wobble = math.sin(self.wobble_time) * 0.2
        self.stretch_x += wobble
        self.stretch_y -= wobble
        
        # Add trail droplets occasionally
        self.trail_timer += 1
        if self.trail_timer >= 5:  # Every 5 frames
            self.trail_timer = 0
            # Add small droplet at current position with random offset
            if random.random() < 0.3:  # 30% chance to drop
                offset_x = random.uniform(-3, 3)
                offset_y = random.uniform(-3, 3)
                self.trail.append({
                    'x': self.x + offset_x,
                    'y': self.y + offset_y,
                    'size': self.base_size * random.uniform(0.2, 0.4),
                    'lifetime': 45  # Trail lasts less than the projectile
                })
                
        # Update trail droplets
        for droplet in self.trail[:]:
            droplet['lifetime'] -= 1
            if droplet['lifetime'] <= 0:
                self.trail.remove(droplet)
        
        # Update rect position
        actual_size = self.base_size * max(self.stretch_x, self.stretch_y)
        self.rect.x = int(self.x - actual_size//2)
        self.rect.y = int(self.y - actual_size//2)
        self.rect.width = self.rect.height = int(actual_size)
        
        # Reduce lifetime
        self.lifetime -= 1
        
        # Return True if the projectile is still active
        return self.lifetime > 0
        
    def draw(self, surface, camera):
        # Draw trail first (behind the main blob)
        for droplet in self.trail:
            # Calculate position with camera offset
            screen_x = int(droplet['x'] - camera.x)
            screen_y = int(droplet['y'] - camera.y)
            
            # Fade out trail droplets based on remaining lifetime
            alpha = int(255 * (droplet['lifetime'] / 45))
            
            # Draw trail droplet
            glow = pygame.Surface((droplet['size']*2, droplet['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color, alpha), 
                    (droplet['size'], droplet['size']), 
                    droplet['size'])
            surface.blit(glow, (screen_x - droplet['size'], screen_y - droplet['size']))
        
        # Calculate position with camera offset
        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)
        
        # Get stretched dimensions for the slime
        width = int(self.base_size * self.stretch_x * 2)
        height = int(self.base_size * self.stretch_y * 2)
        
        # Create a surface for the slime with transparency
        slime_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw the slime with an ellipse shape
        ellipse_rect = pygame.Rect(0, 0, width, height)
        
        # Draw outer glow for slimy effect
        glow_color = (self.color[0], self.color[1], self.color[2], 100)
        pygame.draw.ellipse(slime_surface, glow_color, 
                           pygame.Rect(-2, -2, width+4, height+4))
        
        # Draw main slime body
        pygame.draw.ellipse(slime_surface, self.color, ellipse_rect)
        
        # Draw highlight to make it look wet/shiny
        highlight_size = min(width, height) // 3
        highlight_pos = (width // 4, height // 4)
        pygame.draw.ellipse(slime_surface, 
                           (220, 255, 220, 150),  # Lighter green with transparency
                           pygame.Rect(highlight_pos[0], highlight_pos[1], 
                                      highlight_size, highlight_size))
        
        # Draw slime on main surface
        surface.blit(slime_surface, (screen_x - width//2, screen_y - height//2))

class Enemy1:
    """
    Flying enemy class that moves in a hovering pattern and shoots energy projectiles.
    This enemy doesn't follow regular platform physics and can fly freely.
    """
    def __init__(self, x, y, width=80, height=80):
        """Initialize a new flying enemy"""
        # Position and dimensions
        self.rect = pygame.Rect(x, y, width, height)
        self.spawn_x = x
        self.spawn_y = y
        
        # Movement variables - smoother flying
        self.direction = 1  # 1 for right, -1 for left
        self.speed = 1.2
        self.is_facing_right = False
        self.health = 2
        
        # Smoothed position tracking (for less jittery movement)
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.target_y = y
        
        # Flying movement pattern
        self.hover_offset = random.random() * math.pi * 2  # Random start phase
        self.hover_speed = 0.03
        self.hover_amplitude = 15
        
        # Physics variables - limited for flying enemy
        self.vx = 0
        self.vy = 0
        
        # State variables
        self.state = "idle"  # Can be "idle", "pursuing", "attacking", "retreating"
        self.detection_range = 250  # Range to detect the player
        self.attack_cooldown = 0  # Frames until next attack is allowed
        self.cooldown_duration = 90  # Frames between attacks
        self.fire_delay = 0  # Delay before firing projectile
        self.is_dead = False
        self.is_charge_audio_playing = False
        
        # Projectiles list
        self.projectiles = []
        
        # Animation setup
        self.animation_player = AnimationPlayer()
        
        # Load idle animation
        self.animation_player.load_aseprite_animation(
            image_path="images/Enemy/Enemy1/enemy1_idle.png",
            json_path="images/Enemy/Enemy1/enemy1_idle.json",
            animation_name="idle"
        )
        
        # Set scale to match desired dimensions
        self.animation_player.set_scale(width / 80, height / 108)
        
        # Set initial animation
        self.animation_player.play("idle")
    
    def take_damage(self, damage):
        """Reduce health by 1 and check if enemy is defeated"""
        self.health -= damage
        if self.health <= 0:
            self.is_dead = True
            play_audio_clip(get_file_path("hit.mp3", FILETYPE.AUDIO), 5)

    def update(self, tiles, player=None):
        """Update flying enemy position, animation, and handle player interaction"""
        # Update hover effect for natural flying movement
        if not self.is_dead:
            self.hover_offset += self.hover_speed
            hover_y = math.sin(self.hover_offset) * self.hover_amplitude
            
            # Handle state and movement based on player position
            if player:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                distance = math.sqrt(dx*dx + dy*dy)  # More accurate distance calculation
                
                # Determine facing direction based on player position
                self.is_facing_right = dx > 0
                
                # Handle specific state behaviors
                if self.state == "idle":
                    # Patrol back and forth with smoother motion
                    self.vx = self.speed * self.direction
                    self.target_y = self.spawn_y + hover_y
                    
                    # Patrol limits - reverse direction at boundaries
                    if self.rect.x > self.spawn_x + 200:
                        self.direction = -1
                        self.is_facing_right = False
                    elif self.rect.x < self.spawn_x - 200:
                        self.direction = 1
                        self.is_facing_right = True
                        
                    # Check if player is close enough to pursue
                    if distance < self.detection_range and self.attack_cooldown <= 0:
                        self.state = "pursuing"
                        
                elif self.state == "pursuing":
                    # Move toward player but maintain distance
                    target_distance = 150  # Optimal attack distance
                    
                    if distance > target_distance + 20:
                        # Move closer to player
                        self.vx = self.speed * 1.5 * (1 if dx > 0 else -1)
                    elif distance < target_distance - 20:
                        # Back up if too close
                        self.vx = -self.speed * (1 if dx > 0 else -1)
                    else:
                        # Hold position to attack
                        self.vx = 0
                        
                    # Hover above player with offset
                    self.target_y = player.rect.y - 70 + hover_y
                    
                    # If in good position, switch to attacking
                    if abs(distance - target_distance) < 30 and self.attack_cooldown <= 0:
                        self.state = "attacking"
                        self.fire_delay = 20  # Delay before firing (wind up animation)
                        
                    # If player moves too far away, return to idle
                    if distance > self.detection_range * 1.2:
                        self.state = "idle"
                        
                elif self.state == "attacking":
                    # Hold position and prepare to fire
                    self.vx = 0
                    self.target_y = self.pos_y  # Maintain height
                    
                    # Count down to firing
                    if self.fire_delay > 0:
                        if not self.is_charge_audio_playing:
                            self.is_charge_audio_playing = True
                            play_audio_clip(get_file_path("enemies/flying-enemy/charge.wav", FILETYPE.AUDIO), 7)
                        self.fire_delay -= 1
                        # Slight bobbing while charging
                        self.target_y += math.sin(self.fire_delay * 0.2) * 2
                    else:
                        # Fire projectile
                        self.fire_projectile(player)
                        self.state = "retreating"
                        self.attack_cooldown = self.cooldown_duration
                        
                elif self.state == "retreating":
                    # Move away from player briefly
                    self.vx = -self.speed * (1 if dx > 0 else -1)
                    self.target_y = self.spawn_y - 50 + hover_y
                    
                    # Return to idle after short retreat
                    if self.attack_cooldown < self.cooldown_duration - 30:
                        self.state = "idle"
            else:
                # Default behavior when no player is provided
                self.vx = self.speed * self.direction
                self.target_y = self.spawn_y + hover_y
            
            # Update position with smooth vertical movement
            self.pos_x += self.vx
            self.pos_y += (self.target_y - self.pos_y) * 0.05  # Smooth vertical motion
            
            # Update rectangle position from floating point position
            self.rect.x = int(self.pos_x)
            self.rect.y = int(self.pos_y)
            
            # Update attack cooldown
            if self.attack_cooldown > 0:
                self.attack_cooldown -= 1
            
            # Simple collision handling - just bounce off tiles
            for tile in tiles:
                if self.rect.colliderect(tile.rect):
                    # Change direction if we hit something
                    self.direction *= -1
                    self.is_facing_right = not self.is_facing_right
                    
                    # Push outside of collision
                    if self.vx > 0:
                        self.rect.right = tile.rect.left
                        self.pos_x = self.rect.x
                    elif self.vx < 0:
                        self.rect.left = tile.rect.right
                        self.pos_x = self.rect.x
                        
                    if self.target_y > self.pos_y:
                        self.rect.bottom = tile.rect.top
                        self.pos_y = self.rect.y
                    elif self.target_y < self.pos_y:
                        self.rect.top = tile.rect.bottom
                        self.pos_y = self.rect.y
                    break
            
            # Update animation
            self.animation_player.set_flip(flip_x=not self.is_facing_right)
            self.animation_player.update()
            
            # Update projectiles
            for projectile in self.projectiles[:]:
                if not projectile.update():
                    self.projectiles.remove(projectile)
                else:
                    # Check for tile collisions
                    for tile in tiles:
                        if projectile.rect.colliderect(tile.rect):
                            self.projectiles.remove(projectile)
                            break
            
            # Check for out of bounds
            if self.rect.y > 2000:
                return False  # Signal that this enemy should be removed
                
            return True  # Enemy is still valid
    
    def fire_projectile(self, player):
        self.is_charge_audio_playing = False
        play_audio_clip(get_file_path("enemies/flying-enemy/projectiles.wav", FILETYPE.AUDIO), 7)
        """Fire a slime projectile toward the player"""
        # Calculate direction vector to player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        
        # Normalize the vector
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx = dx / length
            dy = dy / length
        
        # Add slight randomness to make it look more organic
        dx += random.uniform(-0.1, 0.1)
        dy += random.uniform(-0.1, 0.1)
        
        # Create projectile from center of enemy with slightly random size
        projectile = EnemyProjectile(
            self.rect.centerx,
            self.rect.centery,
            dx * 4,  # Speed in x direction (slightly slower)
            dy * 4,  # Speed in y direction (slightly slower)
            size=random.randint(7, 10)  # Random size for variety
        )
        
        # Add to projectiles list
        self.projectiles.append(projectile)
    
    def check_player_collision(self, player):
        """Check if enemy or its projectiles collide with player"""
        # Create a slightly smaller hitbox for body collisions
        hitbox = pygame.Rect(
            self.rect.x + self.rect.width * 0.2,
            self.rect.y + self.rect.height * 0.2,
            self.rect.width * 0.6,
            self.rect.height * 0.6
        )
        
        # Check body collision
        if hitbox.colliderect(player.rect):
            return True
            
        # Check projectile collisions
        for projectile in self.projectiles[:]:
            if projectile.rect.colliderect(player.rect):
                self.projectiles.remove(projectile)
                return True
                
        return False
    
    def draw(self, surface, camera):
        if not self.is_dead:
            """Draw the enemy and its projectiles with camera offset"""
            # Get camera-adjusted position
            enemy_rect = camera.apply(self)
            
            # Draw using animation player
            self.animation_player.draw(surface, enemy_rect.topleft)
            
            # Draw all projectiles
            for projectile in self.projectiles:
                projectile.draw(surface, camera)
                
            # Visual indicator for attack charging (optional)
            if self.state == "attacking" and self.fire_delay > 0:
                # Draw charging effect
                charge_radius = 10 + (20 - self.fire_delay) // 2
                center_x = enemy_rect.centerx
                center_y = enemy_rect.centery
                
                # Create transparent surface for the glow
                glow = pygame.Surface((charge_radius*2, charge_radius*2), pygame.SRCALPHA)
                alpha = min(255, (20 - self.fire_delay) * 12)
                pygame.draw.circle(glow, (0, 255, 0, alpha), (charge_radius, charge_radius), charge_radius)
                surface.blit(glow, (center_x - charge_radius, center_y - charge_radius))
