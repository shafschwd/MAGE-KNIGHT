import pygame
from utils import load_image

class Background:
    def __init__(self, level_width, level_height):
        # Load background image
        self.image = load_image('background.jpeg', use_alpha=False)
        
        # Default background color
        self.bg_color = (30, 30, 30)  # Dark gray
        
        # Store level dimensions
        self.level_width = level_width
        self.level_height = level_height
        
        # If image loaded successfully
        if self.image:
            # Scale to fit the level size - this could be a large image
            self.image = pygame.transform.scale(self.image, (level_width, level_height))
        
    def draw(self, surface):
        """Draw full background on surface."""
        if self.image:
            # Draw the background image
            surface.blit(self.image, (0, 0))
        else:
            # Fallback to solid color
            surface.fill(self.bg_color)
            
    def draw_section(self, surface, view_rect):
        """Draw only the portion of the background visible in view_rect."""
        if self.image:
            # Draw a portion of the background image
            surface.blit(self.image, (0, 0), view_rect)
        else:
            # Fallback to solid color
            surface.fill(self.bg_color)
