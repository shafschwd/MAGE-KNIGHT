import pygame
from utils.utils import load_image, get_file_path, FILETYPE

class HealthBar:
    def __init__(self, max_health):
        self.max_health = max_health
        self.health = max_health

        # Load health bar images with proper path handling
        # Fix paths to use forward slashes and get_file_path for cross-platform compatibility
        try:
            self.health_bar_image = get_file_path("healthbar/bar1.jpeg", FILETYPE.IMAGE)
            self.health_face_image = get_file_path("healthbar/face.jpeg", FILETYPE.IMAGE)
            
            if self.health_bar_image:
                self.health_bar_image = load_image(self.health_bar_image)
            if self.health_face_image:
                self.health_face_image = load_image(self.health_face_image)
                
            # Handle image loading errors
            if self.health_bar_image is None:
                # Create a fallback bar image
                self.health_bar_image = self._create_fallback_bar()
                print("Using fallback health bar image")
                
            if self.health_face_image is None:
                # Create a fallback face image
                self.health_face_image = self._create_fallback_face()
                print("Using fallback face image")
                
            # Scale down the face image for display
            self.health_face_image_small = pygame.transform.scale(self.health_face_image, (15, 15))
            self.health_face_image_large = pygame.transform.scale(self.health_face_image, (25, 25))  # First face is larger
            
        except Exception as e:
            print(f"Error loading health bar assets: {e}")
            # Create fallback assets
            self.health_bar_image = self._create_fallback_bar()
            self.health_face_image = self._create_fallback_face()
            self.health_face_image_small = pygame.transform.scale(self.health_face_image, (15, 15))
            self.health_face_image_large = pygame.transform.scale(self.health_face_image, (25, 25))

    def _create_fallback_bar(self):
        """Create a simple bar image as fallback"""
        bar = pygame.Surface((200, 30), pygame.SRCALPHA)
        bar.fill((50, 50, 50, 180))  # Dark gray semi-transparent
        pygame.draw.rect(bar, (100, 100, 100), bar.get_rect(), 2)  # Border
        return bar
        
    def _create_fallback_face(self):
        """Create a simple face icon as fallback"""
        face = pygame.Surface((30, 30), pygame.SRCALPHA)
        face.fill((200, 0, 0))  # Red background
        pygame.draw.circle(face, (255, 255, 0), (15, 15), 12)  # Yellow circle
        pygame.draw.arc(face, (0, 0, 0), (8, 8, 14, 14), 0, 3.14, 2)  # Smile
        return face

    def update_health(self, health):
        self.health = health

    def take_damage(self, amount=1):
        """Reduces health by the specified amount (default 1) and prevents negative health."""
        self.health = max(self.health - amount, 0)

    def draw(self, surface):
        """Draw the health bar using images."""
        bar_x = 10
        bar_y = 10
        bar_width = self.health_bar_image.get_width()
        bar_height = self.health_bar_image.get_height()
        face_width_small = self.health_face_image_small.get_width()
        face_height_small = self.health_face_image_small.get_height()
        face_width_large = self.health_face_image_large.get_width()
        face_height_large = self.health_face_image_large.get_height()

        # Draw the health bar background
        surface.blit(self.health_bar_image, (bar_x, bar_y))

        # Calculate the number of faces to draw based on current health
        # Each face represents one health unit.
        num_faces = self.health  # Assuming health is an integer (e.g., max_health = 5)

        # Draw the first face larger if at least one health unit remains
        if num_faces > 0:
            surface.blit(self.health_face_image_large, (bar_x + 20, bar_y + (bar_height - face_height_large) // 2))
        
        # Draw remaining faces as smaller icons
        for i in range(1, num_faces):
            face_x = bar_x + 20 + face_width_large + 25 + (face_width_small + 5) * (i - 1)
            surface.blit(self.health_face_image_small, (face_x, bar_y + (bar_height - face_height_small) // 2))

        # Draw the health text below the health bar
        font = pygame.font.Font(None, 24)
        health_text = font.render(f'Health: {self.health}/{self.max_health}', True, (255, 255, 255))
        text_rect = health_text.get_rect(topleft=(bar_x, bar_y + bar_height + 5))
        surface.blit(health_text, text_rect)
