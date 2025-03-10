import pygame
import sys

# Import our modules
from player import Player
from background import Background
from tile import Tile
from utils import load_level
from camera import Camera
from controls import Controls

# --------------------------------------------------------------------------------
# CONFIG & LEVEL
# --------------------------------------------------------------------------------

# Screen dimensions and tile size
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TILE_SIZE = 32

# A much wider level map to enable continuous movement
# This level is wider than the screen, so we need a camera to follow the player
LEVEL_MAP = [
    "......................................................................................",
    "......................................................................................",
    "......................................................................................",
    "......................................................................................",
    "..............####.......#######............................####......................",
    ".......S..............................................................................",
    "......####........................######.............................................",
    "......................................................................................",
    "..............#####...........................................####....................",
    "......................................................................................",
    "#####..............................####...............................................",
    "######............................####...............................................",
    "#######################.............###############........##########################",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
]

# Calculate level dimensions based on the map
LEVEL_WIDTH = len(LEVEL_MAP[0]) * TILE_SIZE
LEVEL_HEIGHT = len(LEVEL_MAP) * TILE_SIZE

# --------------------------------------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("MAGE-KNIGHT")
    clock = pygame.time.Clock()
    
    # Create control system
    controls = Controls()
    
    # Create background
    background = Background(LEVEL_WIDTH, LEVEL_HEIGHT)
    
    # Load level data including tiles, death zones and spawn point
    tiles, death_zones, spawn_point = load_level(LEVEL_MAP, TILE_SIZE, Tile)
    spawn_x, spawn_y = spawn_point
    
    # Create a player at the spawn point
    player = Player(spawn_x, spawn_y)
    
    # Create a camera system
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, LEVEL_WIDTH, LEVEL_HEIGHT)
    
    # Font for displaying controls
    font = pygame.font.SysFont('Arial', 14)
    
    running = True
    while running:
        # 1. Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    # Toggle between control schemes when F1 is pressed
                    controls.toggle_control_scheme()
        
        # Update control states for this frame
        controls.update()
        
        # 2. Update game objects
        player.update(tiles, controls, LEVEL_HEIGHT, death_zones)
        
        # 3. Update camera to follow player - only if player is alive
        if not player.is_dead:
            camera.update(player)
        
        # 4. Draw everything
        # Clear the screen
        screen.fill((0, 0, 0))
        
        # Draw background - adjusted for camera
        bg_rect = pygame.Rect(camera.x, camera.y, SCREEN_WIDTH, SCREEN_HEIGHT)
        background.draw_section(screen, bg_rect)
        
        # Draw the level tiles - with camera offset
        for tile in tiles:
            tile_rect = camera.apply(tile)
            if tile_rect.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)):
                tile.draw(screen, camera.x, camera.y)
        
        # Draw death zones (if you want them visible)
        for zone in death_zones:
            zone_rect = pygame.Rect(
                zone.x - camera.x,
                zone.y - camera.y,
                zone.width,
                zone.height
            )
            if zone_rect.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)):
                pygame.draw.rect(screen, (255, 0, 0), zone_rect)
        
        # Draw the player - with camera offset
        if not player.is_dead:
            player_rect = camera.apply(player)
            screen.blit(player.image, player_rect)
        
        # Draw control information
        control_text = f"Controls: {controls.get_key_name('move_left')}/{controls.get_key_name('move_right')} to move, {controls.get_key_name('jump')} to jump. Press F1 to change control scheme."
        text_surface = font.render(control_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        # If player is dead, show respawn message
        if player.is_dead:
            respawn_text = f"Respawning in {(player.RESPAWN_DELAY - player.respawn_timer) // 10 + 1}..."
            respawn_surface = font.render(respawn_text, True, (255, 0, 0))
            text_rect = respawn_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(respawn_surface, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
