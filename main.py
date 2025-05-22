import pygame
import sys
import time
import random
import os
import math

# Initialize Pygame and its modules
pygame.init()
pygame.mixer.init()  # Initialize the mixer for audio support

# Game constants - these define the game's basic parameters
GRID_WIDTH = 15      # Number of grid cells horizontally
GRID_HEIGHT = 13     # Number of grid cells vertically
TILE_SIZE = 50       # Size of each grid cell in pixels
WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE    # Total window width
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE  # Total window height
FPS = 60             # Frames per second (controls game speed)
PLAYER_SPEED = 5     # Player movement speed
BOMB_TIMER = 2       # Seconds before a bomb explodes
DESTRUCTIBLE_BLOCK_CHANCE = 0.4  # 40% chance for a destructible block to appear
ENEMY_MOVE_INTERVAL = 1.0  # Seconds between enemy movements
GAME_OVER_DELAY = 2.0  # Seconds to wait after game over before allowing restart
GATE_VISIBLE_PULSE_SPEED = 0.1  # Speed of gate pulsing animation
CURRENT_LEVEL = 1    # Starting level number

# Colors used throughout the game
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (76, 187, 23)  # Classic Bomberman green for grass
BLUE = (0, 0, 255)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BROWN = (165, 42, 42)
PURPLE = (128, 0, 128)

# Create the game window with the calculated dimensions
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Bomberman Game")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Load fonts for text display
pygame.font.init()
font_large = pygame.font.SysFont('Arial', 64, bold=True)  # For main titles
font_medium = pygame.font.SysFont('Arial', 36)            # For UI elements

# Asset paths - where to find game resources
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# Create assets directory if it doesn't exist
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

# Sound effects dictionary - will be populated if sound files are found
sounds = {
    'background': None,
    'bomb_placed': None,
    'explosion': None,
    'enemy_death': None,
    'player_death': None
}

# Load or initialize sounds
def load_sounds():
    """
    Attempt to load sound files from the assets directory.
    Returns True if successful, False otherwise.
    """
    try:
        # Background music
        pygame.mixer.music.load(os.path.join(ASSETS_DIR, 'background_music.mp3'))
        pygame.mixer.music.set_volume(0.5)
        
        # Sound effects
        sounds['bomb_placed'] = pygame.mixer.Sound(os.path.join(ASSETS_DIR, 'bomb_placed.wav'))
        sounds['explosion'] = pygame.mixer.Sound(os.path.join(ASSETS_DIR, 'explosion.wav'))
        sounds['enemy_death'] = pygame.mixer.Sound(os.path.join(ASSETS_DIR, 'enemy_death.wav'))
        sounds['player_death'] = pygame.mixer.Sound(os.path.join(ASSETS_DIR, 'player_death.wav'))
        
        print("Sounds loaded successfully")
        return True
    except Exception as e:
        print(f"Error loading sounds: {e}")
        print("Game will continue without sound")
        return False

# Try to load sounds, but continue if files don't exist
sound_enabled = False
try:
    sound_enabled = load_sounds()
    if sound_enabled:
        pygame.mixer.music.play(-1)  # Loop background music indefinitely
except Exception as e:
    print(f"Sound initialization error: {e}")
    sound_enabled = False

# Function to create simple sprite images programmatically
def create_sprite_images():
    """
    Create all game sprites programmatically or load from files.
    Returns a dictionary containing all game sprites.
    """
    # Step 1: Create player sprite (classic Bomberman style)
    player_img = pygame.Surface((TILE_SIZE - 10, TILE_SIZE - 10), pygame.SRCALPHA)
    
    # White body (main part)
    body_height = int((TILE_SIZE - 10) * 0.7)
    body_width = int((TILE_SIZE - 10) * 0.8)
    body_x = ((TILE_SIZE - 10) - body_width) // 2
    body_y = ((TILE_SIZE - 10) - body_height) // 2 + 2  # Slightly lower
    pygame.draw.rect(player_img, WHITE, (body_x, body_y, body_width, body_height))
    
    # Pink helmet/head
    head_height = int((TILE_SIZE - 10) * 0.4)
    head_width = int((TILE_SIZE - 10) * 0.7)
    head_x = ((TILE_SIZE - 10) - head_width) // 2
    head_y = body_y - head_height // 2
    pygame.draw.rect(player_img, (255, 105, 180), (head_x, head_y, head_width, head_height))
    
    # Cyan arms
    arm_width = int((TILE_SIZE - 10) * 0.2)
    arm_height = int((TILE_SIZE - 10) * 0.4)
    # Left arm
    pygame.draw.rect(player_img, (0, 255, 255), 
                    (body_x - arm_width + 2, body_y + body_height // 4, arm_width, arm_height))
    # Right arm
    pygame.draw.rect(player_img, (0, 255, 255), 
                    (body_x + body_width - 2, body_y + body_height // 4, arm_width, arm_height))
    
    # Face details (simple eyes)
    eye_size = max(2, int((TILE_SIZE - 10) * 0.1))
    eye_y = head_y + head_height // 3
    # Left eye
    pygame.draw.rect(player_img, BLACK, 
                    (head_x + head_width // 3 - eye_size // 2, eye_y, eye_size, eye_size))
    # Right eye
    pygame.draw.rect(player_img, BLACK, 
                    (head_x + 2 * head_width // 3 - eye_size // 2, eye_y, eye_size, eye_size))
    
    # Create player sprites for different directions
    player_sprites = {
        'up': player_img,
        'down': player_img.copy(),
        'left': pygame.transform.flip(player_img, True, False),
        'right': player_img.copy()
    }
    
    # Step 2: Create enemy sprites - try to load from files first, or create fallback sprites
    enemy_sprites = []
    try:
        # Try to load enemy sprites from files
        for i in range(1, 4):  # Assuming we have 3 different enemy sprites
            enemy_img = pygame.image.load(os.path.join(ASSETS_DIR, f'enemy{i}.png'))
            enemy_img = pygame.transform.scale(enemy_img, (TILE_SIZE - 10, TILE_SIZE - 10))
            enemy_sprites.append(enemy_img)
        print("Loaded enemy sprites from files")
    except:
        # Create fallback enemy sprites with more character and BETTER VISIBILITY (not green)
        print("Creating fallback enemy sprites")
        # Enemy 1 - Ghost-like (Purple/Pink)
        enemy1 = pygame.Surface((TILE_SIZE - 10, TILE_SIZE - 10), pygame.SRCALPHA)
        pygame.draw.circle(enemy1, (220, 0, 220), (TILE_SIZE // 2 - 5, TILE_SIZE // 2 - 5), TILE_SIZE // 3)
        pygame.draw.circle(enemy1, (255, 255, 255), (TILE_SIZE // 3 - 5, TILE_SIZE // 3 - 5), TILE_SIZE // 10)
        pygame.draw.circle(enemy1, (255, 255, 255), (2 * TILE_SIZE // 3 - 5, TILE_SIZE // 3 - 5), TILE_SIZE // 10)
        pygame.draw.circle(enemy1, (0, 0, 0), (TILE_SIZE // 3 - 5, TILE_SIZE // 3 - 5), TILE_SIZE // 20)
        pygame.draw.circle(enemy1, (0, 0, 0), (2 * TILE_SIZE // 3 - 5, TILE_SIZE // 3 - 5), TILE_SIZE // 20)
        
        # Enemy 2 - Robot-like (Blue/Red)
        enemy2 = pygame.Surface((TILE_SIZE - 10, TILE_SIZE - 10), pygame.SRCALPHA)
        pygame.draw.rect(enemy2, (50, 50, 220), (0, 0, TILE_SIZE - 10, TILE_SIZE - 10))
        pygame.draw.rect(enemy2, (30, 30, 30), (TILE_SIZE // 4 - 5, TILE_SIZE // 4 - 5, TILE_SIZE // 2, TILE_SIZE // 8))
        pygame.draw.rect(enemy2, (255, 0, 0), (TILE_SIZE // 3 - 5, TILE_SIZE // 2 - 5, TILE_SIZE // 8, TILE_SIZE // 8))
        pygame.draw.rect(enemy2, (255, 0, 0), (2 * TILE_SIZE // 3 - 10, TILE_SIZE // 2 - 5, TILE_SIZE // 8, TILE_SIZE // 8))
        
        # Enemy 3 - Slime-like (Red/Orange instead of green)
        enemy3 = pygame.Surface((TILE_SIZE - 10, TILE_SIZE - 10), pygame.SRCALPHA)
        pygame.draw.ellipse(enemy3, (220, 60, 0), (0, TILE_SIZE // 4 - 5, TILE_SIZE - 10, 3 * TILE_SIZE // 4))
        pygame.draw.circle(enemy3, (255, 255, 255), (TILE_SIZE // 3 - 5, TILE_SIZE // 3), TILE_SIZE // 12)
        pygame.draw.circle(enemy3, (255, 255, 255), (2 * TILE_SIZE // 3 - 5, TILE_SIZE // 3), TILE_SIZE // 12)
        pygame.draw.circle(enemy3, (0, 0, 0), (TILE_SIZE // 3 - 5, TILE_SIZE // 3), TILE_SIZE // 24)
        pygame.draw.circle(enemy3, (0, 0, 0), (2 * TILE_SIZE // 3 - 5, TILE_SIZE // 3), TILE_SIZE // 24)
        
        enemy_sprites = [enemy1, enemy2, enemy3]
    
    # Create wall sprite with better texture
    wall_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    wall_img.fill((80, 80, 80))
    # Add stone texture pattern
    for i in range(0, TILE_SIZE, 10):
        for j in range(0, TILE_SIZE, 10):
            if (i + j) % 20 == 0:
                pygame.draw.rect(wall_img, (60, 60, 60), (i, j, 10, 10))
            elif (i + j + 10) % 20 == 0:
                pygame.draw.rect(wall_img, (100, 100, 100), (i, j, 10, 10))
    
    # Create destructible block sprite with better texture
    block_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    block_img.fill((165, 42, 42))  # Base brown color
    # Add brick texture
    for i in range(0, TILE_SIZE, 10):
        pygame.draw.line(block_img, (139, 69, 19), (0, i), (TILE_SIZE, i), 2)
    for i in range(0, TILE_SIZE, 10):
        pygame.draw.line(block_img, (139, 69, 19), (i, 0), (i, TILE_SIZE), 2)
    # Add highlights
    for i in range(5, TILE_SIZE, 10):
        for j in range(5, TILE_SIZE, 10):
            pygame.draw.rect(block_img, (185, 62, 62), (i, j, 3, 3))
    
    # Create ground tile with texture
    ground_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    ground_img.fill((76, 187, 23))  # Base green
    # Add texture details
    for i in range(0, TILE_SIZE, 8):
        for j in range(0, TILE_SIZE, 8):
            if random.random() < 0.2:  # 20% chance for a grass detail
                detail_color = (66, 177, 13) if random.random() < 0.5 else (86, 197, 33)
                pygame.draw.rect(ground_img, detail_color, (i, j, 4, 4))
    
    # Create exit gate sprite
    gate_img = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # Gate frame
    pygame.draw.rect(gate_img, (200, 200, 0), (0, 0, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(gate_img, (0, 0, 0), (2, 2, TILE_SIZE-4, TILE_SIZE-4))
    # Gate details
    pygame.draw.rect(gate_img, (200, 200, 0), (TILE_SIZE//4, TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2))
    pygame.draw.rect(gate_img, (255, 255, 100), (TILE_SIZE//4+4, TILE_SIZE//4+4, TILE_SIZE//2-8, TILE_SIZE//2-8))
    # Add glow effect
    for i in range(3):
        pygame.draw.rect(gate_img, (255, 255, 100, 50), 
                        (-5+i*5, -5+i*5, TILE_SIZE+10-i*10, TILE_SIZE+10-i*10), 2)
    
    # Create bomb sprite
    bomb_img = pygame.Surface((TILE_SIZE - 10, TILE_SIZE - 10), pygame.SRCALPHA)
    pygame.draw.circle(bomb_img, BLACK, (TILE_SIZE // 2 - 5, TILE_SIZE // 2 - 5), TILE_SIZE // 2 - 8)
    # Add fuse
    pygame.draw.line(bomb_img, ORANGE, 
                    (TILE_SIZE // 2 - 5, TILE_SIZE // 4 - 5), 
                    (TILE_SIZE // 2 + 5, TILE_SIZE // 8 - 5), 3)
    # Add highlight
    pygame.draw.circle(bomb_img, (50, 50, 50), 
                      (TILE_SIZE // 2 - 5 - TILE_SIZE // 8, TILE_SIZE // 2 - 5 - TILE_SIZE // 8), 
                      TILE_SIZE // 10)
    
    # Create explosion sprites (center, horizontal, vertical)
    explosion_center = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(explosion_center, RED, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 2)
    pygame.draw.circle(explosion_center, YELLOW, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3)
    
    explosion_horizontal = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(explosion_horizontal, RED, (0, TILE_SIZE // 3, TILE_SIZE, TILE_SIZE // 3))
    pygame.draw.rect(explosion_horizontal, YELLOW, (0, TILE_SIZE // 3 + 5, TILE_SIZE, TILE_SIZE // 3 - 10))
    
    explosion_vertical = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(explosion_vertical, RED, (TILE_SIZE // 3, 0, TILE_SIZE // 3, TILE_SIZE))
    pygame.draw.rect(explosion_vertical, YELLOW, (TILE_SIZE // 3 + 5, 0, TILE_SIZE // 3 - 10, TILE_SIZE))
    
    explosion_end = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(explosion_end, RED, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3)
    pygame.draw.circle(explosion_end, YELLOW, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 4)
    
    # Return all created sprites
    return {
        'player': player_sprites,  # Now a dictionary of directional sprites
        'enemies': enemy_sprites,  # List of enemy sprites
        'wall': wall_img,
        'block': block_img,
        'ground': ground_img,  # New ground tile
        'gate': gate_img,      # New exit gate
        'bomb': bomb_img,
        'explosion_center': explosion_center,
        'explosion_horizontal': explosion_horizontal,
        'explosion_vertical': explosion_vertical,
        'explosion_end': explosion_end
    }

# Load or create sprites
sprites = create_sprite_images()

# Create the grid
# 0 = empty space, 1 = indestructible wall, 2 = destructible block, 3 = hidden gate
def create_grid():
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    # Set borders as indestructible walls
    for x in range(GRID_WIDTH):
        grid[0][x] = 1  # Top border
        grid[GRID_HEIGHT-1][x] = 1  # Bottom border
    
    for y in range(GRID_HEIGHT):
        grid[y][0] = 1  # Left border
        grid[y][GRID_WIDTH-1] = 1  # Right border
    
    # Set every second cell as indestructible wall
    for y in range(2, GRID_HEIGHT-1, 2):
        for x in range(2, GRID_WIDTH-1, 2):
            grid[y][x] = 1
    
    # Add destructible blocks randomly
    for y in range(1, GRID_HEIGHT):
        for x in range(1, GRID_WIDTH):
            # Skip indestructible walls
            if grid[y][x] == 1:
                continue
                
            # Keep starting area clear (3x3 area from top-left)
            if (x <= 2 and y <= 2):
                continue
                
            # Random chance to place a destructible block
            if random.random() < DESTRUCTIBLE_BLOCK_CHANCE:
                grid[y][x] = 2
    
    # Place a hidden gate under one of the destructible blocks
    # Choose a random destructible block
    gate_placed = False
    while not gate_placed:
        gate_x = random.randint(1, GRID_WIDTH-2)
        gate_y = random.randint(1, GRID_HEIGHT-2)
        
        # Make sure it's a destructible block and not in the starting area
        if grid[gate_y][gate_x] == 2 and not (gate_x <= 2 and gate_y <= 2):
            grid[gate_y][gate_x] = 3  # Mark as hidden gate (covered by destructible block)
            gate_placed = True
    
    return grid

# Global grid variable
grid = create_grid()

# Enemy class
class Enemy:
    def __init__(self, grid_x, grid_y):
        """
        Initialize an enemy at the specified grid position.
        
        Args:
            grid_x: X position on the grid
            grid_y: Y position on the grid
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        # Calculate pixel position from grid position
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2 - (TILE_SIZE - 10) // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2 - (TILE_SIZE - 10) // 2
        self.width = TILE_SIZE - 10  # Slightly smaller than tile
        self.height = TILE_SIZE - 10
        self.last_move_time = time.time()
        self.directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Up, Down, Left, Right
        # Choose a random enemy sprite from available ones
        self.sprite_index = random.randint(0, len(sprites['enemies']) - 1)
        # Animation properties
        self.animation_frame = 0
        self.animation_speed = 0.2  # Seconds per frame
        self.last_animation_time = time.time()
    
    def update(self):
        """Update enemy position and animation"""
        current_time = time.time()
        # Move the enemy at regular intervals
        if current_time - self.last_move_time >= ENEMY_MOVE_INTERVAL:
            self.move_randomly()
            self.last_move_time = current_time
        
        # Update animation frame
        if current_time - self.last_animation_time >= self.animation_speed:
            self.animation_frame = (self.animation_frame + 1) % 2  # Simple 2-frame animation
            self.last_animation_time = current_time
    
    def move_randomly(self):
        """Move the enemy in a random valid direction"""
        # Try all directions in random order
        directions = self.directions.copy()
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_grid_x = self.grid_x + dx
            new_grid_y = self.grid_y + dy
            
            # Check if the new position is valid (within bounds and not a wall)
            if (0 <= new_grid_x < GRID_WIDTH and 0 <= new_grid_y < GRID_HEIGHT and 
                grid[new_grid_y][new_grid_x] == 0):
                # Update grid position
                self.grid_x = new_grid_x
                self.grid_y = new_grid_y
                
                # Update pixel position
                self.x = self.grid_x * TILE_SIZE + TILE_SIZE // 2 - self.width // 2
                self.y = self.grid_y * TILE_SIZE + TILE_SIZE // 2 - self.height // 2
                break
    
    def draw(self):
        """Draw the enemy on the screen with animation"""
        # Get the appropriate enemy sprite
        enemy_sprite = sprites['enemies'][self.sprite_index]
        
        # Apply a simple bounce effect for animation
        bounce_offset = 0
        if self.animation_frame == 1:
            bounce_offset = 2  # Move up 2 pixels in second frame
        
        window.blit(enemy_sprite, (self.x, self.y - bounce_offset))
    
    def is_in_explosion(self, affected_tiles):
        """
        Check if the enemy is in the explosion area
        
        Args:
            affected_tiles: List of (x,y) grid positions affected by explosion
            
        Returns:
            True if enemy is in explosion area, False otherwise
        """
        for x, y in affected_tiles:
            if x == self.grid_x and y == self.grid_y:
                return True
        return False
    
    def get_rect(self):
        """Get the enemy's collision rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Bomb class
class Bomb:
    def __init__(self, grid_x, grid_y):
        """
        Initialize a bomb at the specified grid position
        
        Args:
            grid_x: X position on the grid
            grid_y: Y position on the grid
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        # Calculate pixel position from grid position
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2 - (TILE_SIZE - 10) // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2 - (TILE_SIZE - 10) // 2
        self.placed_time = time.time()
        self.exploded = False
        self.explosion_time = 0
        self.explosion_duration = 0.5  # seconds
        self.affected_tiles = []  # Store tiles affected by explosion
        self.explosion_frames = 0  # For animation
        
        # Play bomb placed sound if enabled
        if sound_enabled:
            sounds['bomb_placed'].play()
    
    def update(self, enemies, player):
        current_time = time.time()
        # Check if bomb should explode
        if not self.exploded and current_time - self.placed_time >= BOMB_TIMER:
            self.exploded = True
            self.explosion_time = current_time
            self.calculate_explosion_area()
            self.destroy_blocks()
            
            # Play explosion sound
            if sound_enabled:
                sounds['explosion'].play()
            
            # Check for enemies in explosion
            enemies_to_remove = []
            for enemy in enemies:
                if enemy.is_in_explosion(self.affected_tiles):
                    enemies_to_remove.append(enemy)
                    # Play enemy death sound
                    if sound_enabled:
                        sounds['enemy_death'].play()
            
            # Check if player is in explosion
            player_hit = False
            player_grid_x, player_grid_y = player.get_grid_position()
            for x, y in self.affected_tiles:
                if x == player_grid_x and y == player_grid_y:
                    player_hit = True
                    # Play player death sound
                    if sound_enabled:
                        sounds['player_death'].play()
                    break
            
            # Return list of enemies to remove and player hit status
            return enemies_to_remove, player_hit
        
        # Animate explosion
        if self.exploded:
            self.explosion_frames += 1
            
        return [], False
    
    def calculate_explosion_area(self):
        # Add center tile
        self.affected_tiles.append((self.grid_x, self.grid_y))
        
        # Check in four directions
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in directions:
            # Check each direction up to 3 tiles
            for i in range(1, 4):  # Explosion range of 3 tiles
                x = self.grid_x + dx * i
                y = self.grid_y + dy * i
                
                # Check if position is within grid bounds
                if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
                    break  # Stop this direction if out of bounds
                
                # Check if there's an indestructible wall
                if grid[y][x] == 1:
                    break  # Stop this direction if it hits an indestructible wall
                
                # Add to affected tiles
                self.affected_tiles.append((x, y))
                
                # Stop this direction if it hits a destructible block or hidden gate
                # (but include the destructible block in the affected tiles)
                if grid[y][x] in [2, 3]:
                    break
    
    def destroy_blocks(self):
        global grid
        # Check all affected tiles and destroy destructible blocks
        for x, y in self.affected_tiles:
            if grid[y][x] == 2:  # Destructible block
                grid[y][x] = 0  # Convert to empty space
            elif grid[y][x] == 3:  # Hidden gate
                grid[y][x] = 4  # Reveal the gate
    
    def draw(self):
        if not self.exploded:
            # Calculate bomb pulsing effect based on time remaining
            time_ratio = (time.time() - self.placed_time) / BOMB_TIMER
            scale_factor = 1.0 + abs(math.sin(time_ratio * 10)) * 0.2
            
            # Scale the bomb sprite for pulsing effect
            scaled_size = int((TILE_SIZE - 10) * scale_factor)
            scaled_bomb = pygame.transform.scale(sprites['bomb'], (scaled_size, scaled_size))
            
            # Center the scaled bomb
            offset = (scaled_size - (TILE_SIZE - 10)) // 2
            window.blit(scaled_bomb, (self.x - offset, self.y - offset))
        else:
            # Don't draw anything if explosion is over
            if time.time() - self.explosion_time > self.explosion_duration:
                return
            
            # Draw explosion
            self.draw_explosion()
    
    def draw_explosion(self):
        # Draw center explosion
        window.blit(sprites['explosion_center'], 
                   (self.grid_x * TILE_SIZE, self.grid_y * TILE_SIZE))
        
        # Draw explosion in four directions
        directions = [(0, -1, 'vertical'), (0, 1, 'vertical'), 
                     (-1, 0, 'horizontal'), (1, 0, 'horizontal')]
        
        for dx, dy, sprite_type in directions:
            # Check each direction
            for i in range(1, 4):  # Explosion range of 3 tiles
                x = self.grid_x + dx * i
                y = self.grid_y + dy * i
                
                # Check if position is within affected tiles
                if (x, y) not in self.affected_tiles:
                    break
                
                # Draw explosion segment
                if i == 3 or (x + dx, y + dy) not in self.affected_tiles:  # End of explosion
                    window.blit(sprites['explosion_end'], 
                               (x * TILE_SIZE, y * TILE_SIZE))
                else:  # Middle of explosion
                    window.blit(sprites[f'explosion_{sprite_type}'], 
                               (x * TILE_SIZE, y * TILE_SIZE))
                
                # Stop if this is a destructible block (it will be destroyed but stops the explosion)
                if grid[y][x] == 2:
                    break
    
    def is_finished(self):
        return self.exploded and time.time() - self.explosion_time > self.explosion_duration

# Player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE - 10  # Slightly smaller than tile
        self.height = TILE_SIZE - 10
        self.vel = PLAYER_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.can_place_bomb = True
        self.direction = 'down'  # Default direction
        self.grid_x = (self.x + self.width // 2) // TILE_SIZE
        self.grid_y = (self.y + self.height // 2) // TILE_SIZE
        self.target_x = self.x
        self.target_y = self.y
        self.moving = False
        self.is_dead = False
        self.death_time = 0
    
    def draw(self):
        # Center the player in the tile
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # If player is dead, draw with transparency effect
        if self.is_dead:
            # Create a copy of the sprite with transparency
            alpha = max(0, 255 - int((time.time() - self.death_time) * 255))
            sprite_copy = sprites['player'][self.direction].copy()
            sprite_copy.set_alpha(alpha)
            window.blit(sprite_copy, (self.x, self.y))
        else:
            window.blit(sprites['player'][self.direction], (self.x, self.y))
    
    def move(self, dx, dy, grid):
        # Don't move if dead
        if self.is_dead:
            return
            
        # Set direction based on movement
        if dx < 0:
            self.direction = 'left'
        elif dx > 0:
            self.direction = 'right'
        elif dy < 0:
            self.direction = 'up'
        elif dy > 0:
            self.direction = 'down'
        
        # If already moving, continue current movement
        if self.moving:
            return
        
        # Calculate new position
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Calculate target grid position
        if dx != 0 or dy != 0:
            # Calculate the target grid position
            target_grid_x = self.grid_x
            target_grid_y = self.grid_y
            
            if dx < 0:
                target_grid_x -= 1
            elif dx > 0:
                target_grid_x += 1
            elif dy < 0:
                target_grid_y -= 1
            elif dy > 0:
                target_grid_y += 1
            
            # Check if target position is valid (empty space or gate)
            if (0 <= target_grid_x < GRID_WIDTH and 0 <= target_grid_y < GRID_HEIGHT and 
                (grid[target_grid_y][target_grid_x] == 0 or grid[target_grid_y][target_grid_x] == 4)):
                # Set target pixel position (center of the target tile)
                self.target_x = target_grid_x * TILE_SIZE + (TILE_SIZE - self.width) // 2
                self.target_y = target_grid_y * TILE_SIZE + (TILE_SIZE - self.height) // 2
                self.grid_x = target_grid_x
                self.grid_y = target_grid_y
                self.moving = True
    
    def update(self):
        # If moving, continue movement toward target position
        if self.moving:
            # Calculate direction to target
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            
            # Calculate distance to move this frame
            distance = min(self.vel, max(abs(dx), abs(dy)))
            
            # Move toward target
            if abs(dx) > 0:
                self.x += (dx / abs(dx)) * distance
            if abs(dy) > 0:
                self.y += (dy / abs(dy)) * distance
            
            # Check if we've reached the target
            if abs(self.x - self.target_x) < self.vel and abs(self.y - self.target_y) < self.vel:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
    
    def check_collision(self, rect, grid):
        # Get the grid cells that the player might be colliding with
        grid_x1 = max(0, rect.left // TILE_SIZE)
        grid_y1 = max(0, rect.top // TILE_SIZE)
        grid_x2 = min(GRID_WIDTH - 1, rect.right // TILE_SIZE)
        grid_y2 = min(GRID_HEIGHT - 1, rect.bottom // TILE_SIZE)
        
        # Check each potential grid cell for collision
        for y in range(grid_y1, grid_y2 + 1):
            for x in range(grid_x1, grid_x2 + 1):
                if grid[y][x] in [1, 2]:  # Wall or destructible block
                    wall_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if rect.colliderect(wall_rect):
                        return True
        return False
    
    def get_grid_position(self):
        # Return the current grid position
        return self.grid_x, self.grid_y
    
    def check_enemy_collision(self, enemies):
        # Don't check collisions if already dead
        if self.is_dead:
            return False
            
        for enemy in enemies:
            enemy_rect = enemy.get_rect()
            if self.rect.colliderect(enemy_rect):
                self.is_dead = True
                self.death_time = time.time()
                # Play death sound
                if sound_enabled:
                    sounds['player_death'].play()
                return True
        return False

# Find a valid position for an enemy (empty space)
def find_enemy_position():
    while True:
        x = random.randint(1, GRID_WIDTH - 2)
        y = random.randint(1, GRID_HEIGHT - 2)
        
        # Check if position is empty and not near the player start
        if grid[y][x] == 0 and not (x <= 3 and y <= 3):
            return x, y

# Draw the grid
def draw_grid(grid):
    # Draw green background first
    window.fill(GREEN)
    
    # Draw ground tiles
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            window.blit(sprites['ground'], (x * TILE_SIZE, y * TILE_SIZE))
    
    # Get current time for gate animation
    current_time = time.time()
    pulse = (math.sin(current_time * 8) + 1) / 2  # Value between 0 and 1
            
    # Draw walls, blocks and gate
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == 1:  # Indestructible wall
                window.blit(sprites['wall'], (x * TILE_SIZE, y * TILE_SIZE))
            elif grid[y][x] == 2:  # Destructible block
                window.blit(sprites['block'], (x * TILE_SIZE, y * TILE_SIZE))
            elif grid[y][x] == 3:  # Hidden gate (covered by destructible block)
                window.blit(sprites['block'], (x * TILE_SIZE, y * TILE_SIZE))
            elif grid[y][x] == 4:  # Visible gate
                # Apply pulsing effect to make gate more noticeable
                scale = 1.0 + pulse * 0.1  # Scale between 1.0 and 1.1
                
                # Create a scaled copy of the gate sprite
                gate_size = int(TILE_SIZE * scale)
                scaled_gate = pygame.transform.scale(sprites['gate'], (gate_size, gate_size))
                
                # Center the scaled gate in the tile
                offset = (gate_size - TILE_SIZE) // 2
                window.blit(scaled_gate, (x * TILE_SIZE - offset, y * TILE_SIZE - offset))

# Draw game over screen
def draw_game_over():
    # Semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
    window.blit(overlay, (0, 0))
    
    # Game Over text
    text = font_large.render("GAME OVER", True, RED)
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
    window.blit(text, text_rect)
    
    # Restart instructions
    restart_text = font_medium.render("Press R to Restart", True, WHITE)
    restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
    window.blit(restart_text, restart_rect)

# Draw level complete screen
def draw_level_complete():
    # Semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
    window.blit(overlay, (0, 0))
    
    # Level complete text
    text = font_large.render(f"LEVEL {CURRENT_LEVEL} COMPLETE!", True, YELLOW)
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
    window.blit(text, text_rect)
    
    # Next level instructions
    next_level_text = font_medium.render("Press I to continue to next level", True, WHITE)
    next_level_rect = next_level_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
    window.blit(next_level_text, next_level_rect)

# Main game loop
def main():
    """
    Main game loop - handles initialization, input, updates, and rendering
    """
    global CURRENT_LEVEL
    running = True
    game_over = False
    win = False
    gate_found = False
    next_level = False
    game_over_time = 0
    
    # Initialize game function - called at start and when moving to next level
    def init_game(new_level=False):
        """
        Initialize or reset the game state
        
        Args:
            new_level: If True, increment level counter
            
        Returns:
            Tuple of (player, enemies, bombs) objects
        """
        nonlocal game_over, win, gate_found, next_level, game_over_time
        global grid
        
        # Reset game state
        game_over = False
        win = False
        gate_found = False
        next_level = False
        game_over_time = 0
        
        # Increment level if starting a new level
        global CURRENT_LEVEL
        if new_level:
            CURRENT_LEVEL += 1
        
        # Create a new grid layout
        grid = create_grid()
        
        # Create player at position (1, 1) - first open cell
        # Position player exactly in the center of the tile
        player_x = TILE_SIZE + (TILE_SIZE - (TILE_SIZE - 10)) // 2
        player_y = TILE_SIZE + (TILE_SIZE - (TILE_SIZE - 10)) // 2
        player = Player(player_x, player_y)
        
        # Create enemies (more enemies on higher levels)
        enemies = []
        num_enemies = 3 + CURRENT_LEVEL - 1  # 3 enemies on level 1, 4 on level 2, etc.
        for _ in range(num_enemies):
            enemy_x, enemy_y = find_enemy_position()
            enemies.append(Enemy(enemy_x, enemy_y))
        
        # List to store active bombs
        bombs = []
        
        # Restart background music if it was stopped
        if sound_enabled:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)  # Loop indefinitely
        
        return player, enemies, bombs
    
    # Initialize game objects
    player, enemies, bombs = init_game()
    
    # Main game loop
    while running:
        # ===== EVENT HANDLING =====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and (game_over or win):
                    # Only allow restart after delay if game over
                    if not game_over or (time.time() - game_over_time >= GAME_OVER_DELAY):
                        # Restart the game
                        player, enemies, bombs = init_game()
                elif event.key == pygame.K_i and gate_found:
                    # Press I to move to next level when on the gate
                    next_level = True
                    print("Moving to next level!")  # Debug message
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_x:
                    player.can_place_bomb = True
        
        # ===== GAME LOGIC =====
        if not game_over and not win and not next_level:
            # Handle player movement
            keys = pygame.key.get_pressed()
            
            # Only process movement input if player is not already moving and not dead
            if not player.moving and not player.is_dead:
                if keys[pygame.K_LEFT]:
                    player.move(-player.vel, 0, grid)
                elif keys[pygame.K_RIGHT]:
                    player.move(player.vel, 0, grid)
                elif keys[pygame.K_UP]:
                    player.move(0, -player.vel, grid)
                elif keys[pygame.K_DOWN]:
                    player.move(0, player.vel, grid)
            
            # Update player position (smooth movement)
            player.update()
            
            # Check for player collision with enemies
            if player.check_enemy_collision(enemies):
                game_over = True
                game_over_time = time.time()
                # Stop background music on game over
                if sound_enabled:
                    pygame.mixer.music.stop()
            
            # Check if player is on the gate and all enemies are defeated
            player_grid_x, player_grid_y = player.get_grid_position()
            if grid[player_grid_y][player_grid_x] == 4 and len(enemies) == 0:  # Visible gate and all enemies defeated
                gate_found = True
                # Don't automatically go to next level - wait for 'I' key press
            else:
                gate_found = False  # Reset if player moves off the gate or if enemies still exist
            
            # Update enemies
            for enemy in enemies:
                enemy.update()
            
            # Handle bomb placement with keyboard state
            keys = pygame.key.get_pressed()
            if keys[pygame.K_x] and player.can_place_bomb and not player.is_dead:
                grid_x, grid_y = player.get_grid_position()
                
                # Check if there's already a bomb at this position
                bomb_exists = False
                for bomb in bombs:
                    if bomb.grid_x == grid_x and bomb.grid_y == grid_y:
                        bomb_exists = True
                        break
                
                if not bomb_exists:
                    bombs.append(Bomb(grid_x, grid_y))
                    player.can_place_bomb = False
            
            # Reset bomb placement ability when X key is released
            if not keys[pygame.K_x]:
                player.can_place_bomb = True
            
            # Update bombs
            for bomb in bombs[:]:
                enemies_to_remove, player_hit = bomb.update(enemies, player)
                
                # Check if player was hit
                if player_hit and not player.is_dead:
                    player.is_dead = True
                    player.death_time = time.time()
                    game_over = True
                    game_over_time = time.time()
                    # Stop background music on game over
                    if sound_enabled:
                        pygame.mixer.music.stop()
                
                # Remove enemies caught in explosion
                for enemy in enemies_to_remove:
                    if enemy in enemies:
                        enemies.remove(enemy)
                
                if bomb.is_finished():
                    bombs.remove(bomb)
        
        # Draw the grid
        draw_grid(grid)
        
        # Draw bombs
        for bomb in bombs:
            bomb.draw()
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw()
        
        # Draw the player
        player.draw()
        
        # Draw game over screen if needed
        if game_over:
            draw_game_over()
        
        # Draw gate found message if on gate and all enemies are defeated
        if gate_found:
            # Draw a message to press I to enter the gate
            overlay = pygame.Surface((WINDOW_WIDTH, 60), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Semi-transparent black
            window.blit(overlay, (0, WINDOW_HEIGHT - 60))
            
            gate_text = font_medium.render("Press I to enter the gate", True, YELLOW)
            gate_rect = gate_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
            window.blit(gate_text, gate_rect)
        
        # Handle next level transition
        if next_level:
            # Short delay before starting next level
            pygame.time.delay(1000)
            player, enemies, bombs = init_game(new_level=True)
            next_level = False
        
        # Draw status panel at the top
        status_height = 40
        status_panel = pygame.Surface((WINDOW_WIDTH, status_height), pygame.SRCALPHA)
        status_panel.fill((0, 0, 0, 180))  # Semi-transparent black
        window.blit(status_panel, (0, 0))
        
        # Draw level indicator with better styling
        level_text = font_medium.render(f"LEVEL: {CURRENT_LEVEL}", True, (255, 215, 0))  # Gold color
        level_rect = level_text.get_rect(midleft=(20, status_height // 2))
        window.blit(level_text, level_rect)
        
        # Draw enemies remaining indicator with color based on count
        enemy_count = len(enemies)
        enemy_color = (0, 255, 0) if enemy_count == 0 else (255, 100, 100)  # Green if all defeated, red otherwise
        enemies_text = font_medium.render(f"ENEMIES: {enemy_count}", True, enemy_color)
        enemies_rect = enemies_text.get_rect(midright=(WINDOW_WIDTH - 20, status_height // 2))
        window.blit(enemies_text, enemies_rect)
        
        # Update the display
        pygame.display.flip()
        
        # Control the frame rate
        clock.tick(FPS)

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
