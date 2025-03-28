import pygame
import sys
import subprocess

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Fonts
pygame.font.init()
FONT = pygame.font.Font(None, 50)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Menu")

# Button dimensions
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50

# Button positions
play_button_rect = pygame.Rect((SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200), (BUTTON_WIDTH, BUTTON_HEIGHT))
quit_button_rect = pygame.Rect((SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 300), (BUTTON_WIDTH, BUTTON_HEIGHT))

def draw_button(rect, text):
    pygame.draw.rect(screen, GRAY, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    text_surface = FONT.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def main_menu():
    while True:
        screen.fill(BLACK)
        # Flashing "Mage Knight" text
        if pygame.time.get_ticks() // 500 % 2 == 0:  # Toggle visibility every 500ms
            title_surface = FONT.render("Mage Knight", True, WHITE)
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
            screen.blit(title_surface, title_rect)

        # Draw buttons
        draw_button(play_button_rect, "Play Game")
        draw_button(quit_button_rect, "Quit")

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button_rect.collidepoint(event.pos):
                    # Launch main.py
                    subprocess.run(["python3", "src/main.py"])
                elif quit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()