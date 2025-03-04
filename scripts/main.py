import pygame
import sys

# Import our modules
from player import Player
from background import Background
from tile import Tile
from utils import load_level

# --------------------------------------------------------------------------------
# CONFIG & LEVEL
# --------------------------------------------------------------------------------

# Screen dimensions and tile size
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TILE_SIZE = 32

# A simple tile map using symbols:
#  '.' means empty space
#  '#' means a solid platform
LEVEL_MAP = [
    "........................",
    "........................",
    "........................",
    "..............####.......",
    "........................",
    ".......####..............",
    "........................",
    "..............#####......",
    "........................",
    "#####....................",
    "........................",
    "#######################",
]

# --------------------------------------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("MAGE-KNIGHT")
    clock = pygame.time.Clock()

    # Create background
    background = Background(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Load level geometry (list of Tile objects)
    tiles = load_level(LEVEL_MAP, TILE_SIZE, Tile)

    # Create a player at x=50, y=50
    player = Player(50, 50)

    running = True
    while running:
        # 1. Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Update game objects
        player.update(tiles)

        # 3. Draw everything
        # Draw background
        background.draw(screen)

        # Draw the level tiles
        for tile in tiles:
            tile.draw(screen)

        # Draw the player
        player.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
