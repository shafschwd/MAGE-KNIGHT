import pygame
import os

def load_image(filename, use_alpha=True):
    """
    Helper function to load images with proper error handling.
    Returns the loaded image or None if loading failed.
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, 'assets', filename)
        
        if use_alpha:
            return pygame.image.load(filepath).convert_alpha()
        else:
            return pygame.image.load(filepath).convert()
    except (pygame.error, FileNotFoundError) as e:
        print(f"Could not load image {filename}: {e}")
        return None

def load_level(level_data, tile_size, tile_class):
    """
    Given a list of strings, return level objects and spawn point.
    
    Level symbols:
    '#' - solid platform
    'S' - spawn point
    'X' - death zone (spikes, lava, etc.)
    """
    tiles = []
    death_zones = []
    spawn_x, spawn_y = None, None
    
    for row_index, row in enumerate(level_data):
        for col_index, char in enumerate(row):
            x = col_index * tile_size
            y = row_index * tile_size
            
            if char == '#':
                tile = tile_class(x, y, tile_size, tile_size)
                tiles.append(tile)
            elif char == 'S':
                spawn_x = x
                spawn_y = y
            elif char == 'X':
                # Create a death zone rect
                death_zone = pygame.Rect(x, y, tile_size, tile_size)
                death_zones.append(death_zone)
    
    # Return a default spawn point if none was found
    if spawn_x is None:
        spawn_x, spawn_y = 50, 50
        
    return tiles, death_zones, (spawn_x, spawn_y)
