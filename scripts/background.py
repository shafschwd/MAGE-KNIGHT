import pygame
from utils import load_image

class Background:
    def __init__(self, screen_width, screen_height):
        # Load background image
        self.image = load_image('background.jpeg', use_alpha=False)
        
        # Default background color
        self.bg_color = (30, 30, 30)  # Dark gray
        
        # If image loaded successfully
        if self.image:
            # Scale to fit screen if needed
            self.image = pygame.transform.scale(self.image, (screen_width, screen_height))
        
    def draw(self, surface):
        if self.image:
            # Draw the background image
            surface.blit(self.image, (0, 0))
        else:
            # Fallback to solid color
            surface.fill(self.bg_color)
