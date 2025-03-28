import pygame
import pygame.gfxdraw  # Add this for the anti-aliased circle drawing
from utils.utils import load_image

class Background:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Load background image
        self.image = load_image('background.jpeg', use_alpha=False)
        
        # Default background color
        self.bg_color = (30, 30, 30)  # Dark gray
        
        # Store level dimensions
        #self.level_width = level_width
        #self.level_height = level_height
        
        # If image loaded successfully
        #if self.image:
            # Scale to fit the level size - this could be a large image
        #    self.image = pygame.transform.scale(self.image, (level_width, level_height))
        
    def draw(self, surface, player_rect):
        if self.image:
            # Draw the background image
            parallax_x = -player_rect.centerx * 0.1  # Adjust the multiplier for parallax effect
            surface.blit(self.image, (parallax_x, 0))
        else:
            # Fallback to solid color
            surface.fill(self.bg_color)

        #filter = pygame.surface.Surface((self.screen_width, self.screen_height))
        #filter_color = (150, 150, 150, 0)
        #filter.fill(filter_color)
        
        #for i in range(20):
        #    radius = 150 - i * 5
        #    color_value = 75 - i * 3
        #    pygame.draw.circle(filter, (color_value, color_value, color_value, 0), (player_rect.centerx, player_rect.centery), radius)
        #for i in range(5):
            #trans = i * 30
            #pygame.draw.circle(filter, (i, i, i, 0), (player_rect.centerx, player_rect.centery), i * 40)
        #surface.blit(filter, (0, 0), special_flags=pygame.BLEND_RGB_SUB)

def draw_overlay(width, height, screen, player_rect=None):
    """Draw a dark overlay with a light circle around the player to simulate lighting."""
    # Create a semi-transparent dark surface for the overlay
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Dark overlay with alpha for transparency
    
    # If player position is provided, create a smooth light effect around them
    if player_rect:
        # Center of the light effect (player's center)
        center_x = player_rect.centerx
        center_y = player_rect.centery
        
        # Performance optimization: Use a smaller, pre-rendered light texture
        max_radius = 300  # Reduced radius for better performance
        step_size = 20    # Larger steps between circles for performance
        
        # Create a surface for the light
        light_surf = pygame.Surface((max_radius * 2, max_radius * 2), pygame.SRCALPHA)
        
        # Generate a smooth radial gradient but with fewer iterations
        # Use a quadratic falloff curve for a natural look with fewer circles
        for radius in range(max_radius, 0, -step_size):
            # Calculate alpha based on distance from center using quadratic falloff
            distance_factor = radius / max_radius
            alpha = int(255 * (1 - distance_factor) ** 2)
                
            # Skip very faint circles
            if alpha < 5:
                continue
                
            # Draw filled circle with current alpha
            pygame.gfxdraw.filled_circle(
                light_surf,
                max_radius,  # Center X
                max_radius,  # Center Y
                radius,
                (255, 255, 255, alpha)  # Use alpha calculated from position
            )
            
        # Add anti-aliasing for the outermost edge
        pygame.gfxdraw.aacircle(
            light_surf,
            max_radius,
            max_radius,
            max_radius - 1,
            (255, 255, 255, 30)
        )
        
        # Calculate position to blit the light (centered on player)
        light_pos = (center_x - max_radius, center_y - max_radius)
        
        # Blit the light onto the overlay using BLEND_RGBA_SUB to create a "hole" in the darkness
        overlay.blit(light_surf, light_pos, special_flags=pygame.BLEND_RGBA_SUB)

    # Apply the overlay to the screen
    screen.blit(overlay, (0, 0))