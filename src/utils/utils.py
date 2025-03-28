import pygame
import os
from enum import Enum

class FILETYPE(Enum):
    IMAGE = 0
    AUDIO = 1

def get_file_path(filename, type: FILETYPE):
    if type == FILETYPE.IMAGE:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, '../assets', filename)
    elif type == FILETYPE.AUDIO:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, '../assets/audio', filename)

# ======================= IMPROVED IMAGE LOADING =======================
def load_image(filename, use_alpha=True):
    """
    Helper function to load images with proper error handling.
    Returns the loaded image or None if loading failed.
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, '../assets', filename)
        
        # Debug output to help identify path issues
        # print(f"Attempting to load image from: {filepath}")
        # print(f"File exists: {os.path.exists(filepath)}")
        
        if not os.path.exists(filepath):
            print(f"WARNING: Image file not found: {filepath}")
            # Check if we need to create the directory for development
            assets_dir = os.path.join(base_dir, '../assets/images/Enemy/Enemy0')
            if not os.path.exists(assets_dir):
                print(f"Note: Assets directory structure does not exist: {assets_dir}")
            return None

        if use_alpha:
            return pygame.image.load(filepath).convert_alpha()
        else:
            return pygame.image.load(filepath).convert()
    except (pygame.error, FileNotFoundError) as e:
        print(f"Could not load image {filename}: {e}")
        return None
# ===============================================================================

# ======================= FIXED MAP GENERATION LOGIC =======================
def parse_map(level_map, tile_size, tile_class):
    """Parse a level map represented as a list of strings.
    
    Args:
        level_map (list): List of strings representing the level layout.
        tile_size (int): Size of each tile in pixels.
        tile_class (class): Class to use for creating tile objects.
    
    Returns:
        tuple: Contains:
            - List of Tile objects
            - Player spawn position (x, y) or None
            - Enemy spawn positions list [(x, y), (x, y), ...]
            - Flying enemy spawn positions list [(x, y), (x, y), ...]
            - Death zone rectangles list [pygame.Rect, pygame.Rect, ...]
    """
    tiles = []
    player_spawn = None
    enemy_spawns = []
    flying_enemy_spawns = []
    death_zones = []
    
    # Process each character in the level map
    for row_index, row in enumerate(level_map):
        for col_index, cell in enumerate(row):
            x = col_index * tile_size
            y = row_index * tile_size
            
            if cell == '#':
                # Create a tile object, passing width and height arguments
                tiles.append(tile_class(x, y, tile_size, tile_size))
            elif cell == 'S':
                # Mark player spawn position
                player_spawn = (x, y)
            elif cell == 'E':
                # Mark enemy spawn position
                enemy_spawns.append((x, y))
            elif cell == 'F':
                # Mark flying enemy spawn position
                flying_enemy_spawns.append((x, y))
            elif cell == 'X':
                # Create a death zone rectangle
                death_zones.append(pygame.Rect(x, y, tile_size, tile_size))
    
    # Return the parsed map elements
    return tiles, player_spawn, enemy_spawns, flying_enemy_spawns, death_zones
# ===============================================================================

def load_level(level_data, tile_size, tile_class):
    """
    Given a list of strings, return a list of Tile objects for solid tiles.
    Each '#' in the level map is turned into a Tile with the size TILE_SIZE x TILE_SIZE.
    """
    tiles = []
    for row_index, row in enumerate(level_data):
        for col_index, char in enumerate(row):
            if char == '#':
                x = col_index * tile_size
                y = row_index * tile_size
                tile = tile_class(x, y, tile_size, tile_size)
                tiles.append(tile)
    return tiles
