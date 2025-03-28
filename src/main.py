import pygame
import sys
import os
import pygame.gfxdraw  # Add import for anti-aliased graphics

# Fix import to use relative imports within the same package
from entities.player import Player
from fx.particlesystems.fog import FogManager
from utils.controls import Controls
from entities.background import Background, draw_overlay
from entities.tile import Tile
# ======================= IMPROVED MAP GENERATION IMPORT =======================
from utils.utils import parse_map, get_file_path, FILETYPE
# ===============================================================================
from utils.audioplayer import play_background_music
from fx.particlesystems.fireflies import FireflyParticleSystem
from camera import Camera  # Add camera import

# ======================= PLAYER KNOCKBACK IMPLEMENTATION - NEW IMPORT =======================
# Import the player extension to add the knockback method
import entities.player_extension  # This adds the apply_knockback method to Player class
# ===============================================================================

# ======================= ENEMY IMPLEMENTATION - FIXED IMPORT =======================
# Correct import path for Enemy class
from entities.enemy import Enemy  # Import from entities package without src prefix
from entities.enemy1 import Enemy1  # Import the flying enemy class
# ===============================================================================

# ======================= HIT EFFECT IMPLEMENTATION - NEW IMPORT =======================
# Import the HitEffect class
from fx.hiteffect import HitEffect
# ===============================================================================

# ======================= ASSET VALIDATION IMPORTS =======================
from utils.utils import get_file_path, FILETYPE
# ===============================================================================

# --------------------------------------------------------------------------------
# CONFIG & LEVEL
# --------------------------------------------------------------------------------

# Screen dimensions and tile size
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TILE_SIZE = 32

# ======================= UPDATED MAP CONFIGURATION WITH FLYING ENEMIES =======================
# A much wider level map with specific entity markers
# S = Player spawn point
# E = Enemy spawn point (now placed properly on platforms)
# F = Flying enemy spawn point (doesn't need to be on platforms)
# X = Death zone (causes player to die on contact)
# # = Platform/solid tile
LEVEL_MAP = [
    "....................................................................................................",
    "....................................................................................................",
    "....................................................................................................",
    "..............................####....#####......F................F.................................",
    "...................F................................................................................",
    ".......................####................................E...............E....E........F..........",
    "....................................E.........#####......####.##.........####.####..................",
    ".................####............######.............................................................",
    ".................................................F....................F............F................",
    "....................................................................................................",
    "......##.....###......##..#####.........######..........E............E...................E..........",
    "S.##..##......##......##.............................##########################################.....",
    "..##..##......##EEEEEE##.............................##########################################.....",
    "########......##########.............................##########################################.....",
    "########XXXXXX##########XXXXXXXXXXXXXXXXXXXXXXXXXXXXX##########################################XXXXX",
]
# ===============================================================================

# Calculate level dimensions based on the map
LEVEL_WIDTH = len(LEVEL_MAP[0]) * TILE_SIZE
LEVEL_HEIGHT = len(LEVEL_MAP) * TILE_SIZE

# --------------------------------------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------------------------------------

def main():
    pygame.init()
    
    pygame.mixer.init()
    pygame.mixer.set_num_channels(16)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("MAGE-KNIGHT")
    clock = pygame.time.Clock()

    # Initialize camera
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, LEVEL_WIDTH, LEVEL_HEIGHT)

    # Initialize controls system
    controls = Controls()

    firefly_particle_system = FireflyParticleSystem(SCREEN_WIDTH, SCREEN_HEIGHT, 10, camera)
    fog_manager = FogManager(SCREEN_WIDTH, SCREEN_HEIGHT, 20)
    # Create background
    background = Background(SCREEN_WIDTH, SCREEN_HEIGHT)

    # ======================= IMPROVED MAP LOADING WITH FLYING ENEMIES =======================
    # Parse level map to get tiles, spawn positions, and death zones
    tiles, player_spawn, enemy_spawns, flying_enemy_spawns, death_zones = parse_map(LEVEL_MAP, TILE_SIZE, Tile)
    # ===============================================================================
    
    # ======================= FIXED ENEMY CREATION AND POSITIONING =======================
    # Create enemies at spawn positions with varying patrol distances
    enemies = []
    patrol_distances = [150, 200, 250]  # Different patrol distances for variety
    
    # Calculate proper Y offset to ensure enemies are properly placed on the platforms
    enemy_height = 64  # Default enemy height
    enemy_y_offset = -enemy_height  # Place enemies so their feet touch the platform
    
    for i, spawn in enumerate(enemy_spawns):
        patrol = patrol_distances[i % len(patrol_distances)]  # Cycle through patrol distances
        # Position the enemy on top of the platform by offsetting y position
        enemies.append(Enemy(spawn[0], spawn[1] + enemy_y_offset, patrol_distance=patrol))
        print(f"Created enemy at ({spawn[0]}, {spawn[1] + enemy_y_offset})")
    # ===============================================================================
    
    # ======================= FLYING ENEMY CREATION =======================
    # Create flying enemies at spawn positions
    flying_enemies = []
    for spawn in flying_enemy_spawns:
        flying_enemies.append(Enemy1(spawn[0], spawn[1]))
        print(f"Created flying enemy at ({spawn[0]}, {spawn[1]})")
    
    # Store initial flying enemy positions for respawning
    flying_enemy_spawns_info = []
    for spawn in flying_enemy_spawns:
        flying_enemy_spawns_info.append({
            'x': spawn[0],
            'y': spawn[1]
        })
    # ===============================================================================
    
    # ======================= IMPROVED ENEMY RESPAWN TRACKING =======================
    # Store initial enemy positions and properties for respawning
    enemy_spawns_info = []
    for i, spawn in enumerate(enemy_spawns):
        patrol = patrol_distances[i % len(patrol_distances)]
        enemy_spawns_info.append({
            'x': spawn[0],
            'y': spawn[1] + enemy_y_offset,  # Using the adjusted Y position
            'patrol': patrol
        })
    # ===============================================================================
    
    all_enemies = flying_enemies + enemies
    # Create player at spawn position or default position if no spawn point defined
    if player_spawn:
        player = Player(player_spawn[0], player_spawn[1], controls, camera, 5, all_enemies)
    else:
        # Default spawn position if no 'S' marker in map
        player = Player(50, 50, controls, camera, 5, all_enemies)

    # Load and play background music
    play_background_music(get_file_path("background.mp3", FILETYPE.AUDIO))

    # ======================= KNOCKBACK IMPLEMENTATION - NEW VARIABLE =======================
    # Variable to track player invulnerability after being hit
    invulnerable_timer = 0
    invulnerable_duration = 60  # Frames of invulnerability after being hit (1 second at 60 FPS)
    # ===============================================================================

    # ======================= HIT EFFECT IMPLEMENTATION - NEW VARIABLE =======================
    # List to store active hit effects
    hit_effects = []
    # ===============================================================================

    running = True
    while running:
        # 1. Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    controls.toggle_control_scheme()  # Allow toggling controls with Tab key
        
        # Update control states
        controls.update()
        
        # 2. Update game objects
        player.update(tiles)
        # Update camera to follow player
        camera.update(player)
        
        # ======================= IMPROVED DEATH ZONE COLLISION DETECTION =======================
        # Check if player is in a death zone
        player_rect = player.rect
        player_died = False
        
        for death_zone in death_zones:
            # Check if player's feet touch the death zone
            # This is more lenient and makes more sense for platformers
            feet_rect = pygame.Rect(
                player_rect.x + player_rect.width * 0.25,
                player_rect.y + player_rect.height * 0.8,
                player_rect.width * 0.5,  # Only check the center 50% of the player width
                player_rect.height * 0.2   # Only check the bottom 20% of the player height
            )
            
            if feet_rect.colliderect(death_zone):
                player.health = 0
                player_died = True
                print("Player hit a death zone!")
                break  # Exit loop once death is detected
                
        # Check if enemies are in death zones and remove them if they are
        for enemy in enemies[:]:  # Create a copy of the list for safe removal

            if enemy.is_dead:
                enemies.remove(enemy)
                print("Enemy is dead")
                continue
            
            for death_zone in death_zones:
                # Create a feet rect for the enemy similar to the player
                enemy_feet_rect = pygame.Rect(
                    enemy.rect.x + enemy.rect.width * 0.25,
                    enemy.rect.y + enemy.rect.height * 0.8,
                    enemy.rect.width * 0.5,
                    enemy.rect.height * 0.2
                )
                
                if enemy_feet_rect.colliderect(death_zone):
                    enemies.remove(enemy)
                    print(f"Enemy fell into death zone at ({enemy.rect.x}, {enemy.rect.y})")
                    break  # Exit inner loop once this enemy is removed
                    
        # Check for flying enemies in death zones as well
        for enemy in flying_enemies[:]:
            for death_zone in death_zones:
                enemy_feet_rect = pygame.Rect(
                    enemy.rect.x + enemy.rect.width * 0.25,
                    enemy.rect.y + enemy.rect.height * 0.8,
                    enemy.rect.width * 0.5,
                    enemy.rect.height * 0.2
                )
                
                if enemy_feet_rect.colliderect(death_zone):
                    flying_enemies.remove(enemy)
                    print(f"Flying enemy hit death zone at ({enemy.rect.x}, {enemy.rect.y})")
                    break
        # ===============================================================================
        
        # Reset player and enemies if player died
        if player_died:
            # Reset player to spawn position
            if player_spawn:
                player.rect.x = player_spawn[0]
                player.rect.y = player_spawn[1]
            
            # Reset player velocity
            player.vx = 0
            player.vy = 0
            
            # Reset player health to maximum
            player.health = 5  # Reset health to default/maximum value
            
            # Respawn all enemies to their original positions
            enemies = []
            for spawn_info in enemy_spawns_info:
                enemies.append(Enemy(
                    spawn_info['x'],
                    spawn_info['y'],
                    patrol_distance=spawn_info['patrol']
                ))
                
            # Respawn flying enemies too
            flying_enemies = []
            for spawn_info in flying_enemy_spawns_info:
                flying_enemies.append(Enemy1(
                    spawn_info['x'],
                    spawn_info['y']
                ))
            print("Respawned all enemies!")
        # ===============================================================================
        
        # ======================= KNOCKBACK IMPLEMENTATION - UPDATED COLLISION =======================
        # Update invulnerability timer
        if invulnerable_timer > 0:
            invulnerable_timer -= 1
        
        # ======================= UPDATED ENEMY PROCESSING =======================
        # Update all enemies and pass the player parameter for detection
        for enemy in enemies[:]:  # Use copy to allow safe removal
            # Update returns False if enemy should be removed (fell out of bounds)
            if not enemy.update(tiles, player):
                enemies.remove(enemy)
                
            # Check for player-enemy collision only if player is not invulnerable
            if invulnerable_timer <= 0 and enemy.check_player_collision(player):
                # Calculate knockback direction (away from enemy)
                knockback_dir = 1 if player.rect.centerx > enemy.rect.centerx else -1
                
                # Apply stronger knockback if enemy is attacking
                knockback_force = 15 if enemy.state == "attacking" else 10
                vertical_force = -10 if enemy.state == "attacking" else -8
                
                # Apply knockback to player
                player.apply_knockback(knockback_dir, knockback_force, vertical_force)
                
                # Start invulnerability period
                invulnerable_timer = invulnerable_duration
                
                # Decrease player health (more damage if enemy is charging)
                #damage = 1  # Each hit reduces health by 1
                player.take_damage(1)

                # Create hit effect at the point of collision
                hit_x = (player.rect.centerx + enemy.rect.centerx) / 2
                hit_y = (player.rect.centery + enemy.rect.centery) / 2
                
                # Different colors based on attack strength
                hit_color = (255, 50, 50) if enemy.state == "attacking" else (255, 100, 100)
                
                # Add new hit effect
                hit_effects.append(HitEffect(hit_x, hit_y, hit_color))
                
                # Try to play hit sound if the function exists
                try:
                    from utils.audioplayer import play_hit_sound
                    play_hit_sound()
                except (ImportError, AttributeError):
                    # Fallback if hit sound function isn't available
                    pass
                
                if player.health <= 0:
                    player.die()
                
                # Optional: Display hit effect or play sound
                #print(f"Player knocked back by enemy! Damage: {damage}")
        # ===============================================================================
                
        # ======================= FLYING ENEMY PROCESSING - IMPROVED =======================
        # Update all flying enemies and pass the player parameter for detection
        for enemy in flying_enemies[:]:  # Use copy to allow safe removal
            # Update returns False if enemy should be removed
            if not enemy.update(tiles, player):
                flying_enemies.remove(enemy)
                
            # Check for player-enemy collision only if player is not invulnerable
            if invulnerable_timer <= 0 and enemy.check_player_collision(player):
                # Calculate knockback direction (away from enemy)
                knockback_dir = 1 if player.rect.centerx > enemy.rect.centerx else -1
                
                # Flying enemies have stronger vertical knockback
                knockback_force = 12
                vertical_force = -12
                
                # Apply knockback to player
                player.apply_knockback(knockback_dir, knockback_force, vertical_force)
                
                # Start invulnerability period
                invulnerable_timer = invulnerable_duration
                
                # Flying enemies deal 2 damage
                player.take_damage(2)
                
                # Create hit effect at the point of collision
                hit_x = (player.rect.centerx + enemy.rect.centerx) / 2
                hit_y = (player.rect.centery + enemy.rect.centery) / 2
                hit_color = (0, 255, 100)  # Green color for flying enemy hits (matching projectiles)
                hit_effects.append(HitEffect(hit_x, hit_y, hit_color))
                
                # Try to play hit sound
                try:
                    from utils.audioplayer import play_hit_sound
                    play_hit_sound()
                except (ImportError, AttributeError):
                    pass
                
                if player.health <= 0:
                    player.die()
                
                #print(f"Player hit by flying enemy or projectile! Damage: {damage}")
        # ===============================================================================
        
        # ======================= HIT EFFECT IMPLEMENTATION - UPDATE EFFECTS =======================
        # Update and remove finished hit effects
        for effect in hit_effects[:]:
            effect.update()
            if effect.is_finished():
                hit_effects.remove(effect)
        # ===============================================================================
        
        fog_manager.update()
        firefly_particle_system.update()

        # 3. Draw everything
        # Draw background
        background.draw(screen, player_rect=player.rect)

        # Draw the level tiles with camera offset
        for tile in tiles:
            # Apply camera offset to each tile
            tile_rect = camera.apply(tile)
            screen.blit(tile.image, tile_rect)

        # ======================= ENEMY IMPLEMENTATION - DRAW ALL ENEMIES =======================
        # Draw all enemies with camera offset
        for enemy in enemies:
            enemy.draw(screen, camera)
            
        # Draw all flying enemies
        for enemy in flying_enemies:
            enemy.draw(screen, camera)
        # ===============================================================================
            
        fog_manager.draw(screen)
        player_render_rect = camera.apply(player)
        draw_overlay(SCREEN_WIDTH, SCREEN_HEIGHT, screen, player_rect=player_render_rect)
        
        # ======================= KNOCKBACK IMPLEMENTATION - VISUAL INDICATOR =======================
        # Optional: Flash the player sprite when invulnerable
        visible = True
        if invulnerable_timer > 0:
            # Make player flash by alternating visibility every 5 frames
            visible = (invulnerable_timer // 5) % 2 == 0
        
        # Draw the player only if visible
        if visible:
            player.draw(screen)
        # ===============================================================================
        
        # Draw any footstep particles with camera offset
        for particle in player.footstep_particles:
            particle.update()
            # Draw at camera-adjusted position
            adjusted_x = particle.x - camera.x
            adjusted_y = particle.y - camera.y
            pygame.draw.circle(screen, particle.color, (int(adjusted_x), int(adjusted_y)), int(particle.size))
        
        # ======================= HIT EFFECT IMPLEMENTATION - DRAW EFFECTS =======================
        # Draw all active hit effects
        for effect in hit_effects:
            effect.draw(screen, camera)
        # ===============================================================================
        
        firefly_particle_system.draw(screen)

        # ======================= FIXED DEATH ZONE VISUALIZATION (DEBUG ONLY) =======================
        # Uncomment to visualize death zones during debugging
        # for death_zone in death_zones:
        #     # Apply camera offset
        #     adjusted_rect = pygame.Rect(
        #         death_zone.x - camera.x, 
        #         death_zone.y - camera.y,
        #         death_zone.width, 
        #         death_zone.height
        #     )
        #     pygame.draw.rect(screen, (255, 0, 0), adjusted_rect, 1)
        # ===============================================================================
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
