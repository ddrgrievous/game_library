import pygame
import random
import math

# Initialize Pygame
pygame.init()
pygame.font.init()

# Constants
WINDOW_WIDTH = 1600  # Made screen wider
WINDOW_HEIGHT = 600
CASTLE_WIDTH = 200
ENEMY_SIZE = 30
SPAWN_RATE = 2500  # milliseconds between spawns at start (reduced from 3000)
MIN_SPAWN_RATE = 400  # fastest possible spawn rate (reduced from 500)
LEVEL_DURATION = 30  # seconds
HEALTH_UPGRADE_COST = 10  # points per health point

# Game States
PLAYING = 0
UPGRADING = 1
GAME_OVER = 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
DARKGRAY = (64, 64, 64)

# Initialize screen
screen = None

def init_display():
    global screen
    if screen is None:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Castle Defense")

class Bullet:
    def __init__(self, x, y, enemies):
        self.x = x
        self.y = y
        self.speed = 7
        self.radius = 5
        self.alive = True
        self.enemies = enemies  # Store reference to all enemies
        self.target = None
        self.creation_time = pygame.time.get_ticks()
        self.max_lifetime = 5000  # Bullets despawn after 5 seconds
        self.find_nearest_target()

    def find_nearest_target(self):
        # Find nearest living enemy that's on screen
        nearest_dist = float('inf')
        self.target = None
        
        # Quick check to avoid list comprehension if no valid targets exist
        has_valid_target = False
        for enemy in self.enemies:
            if enemy.alive and enemy.x > 0:
                has_valid_target = True
                break
                
        if not has_valid_target:
            return False
            
        # Find nearest target using squared distance (faster than hypot)
        for enemy in self.enemies:
            if enemy.alive and enemy.x > 0:
                # Using squared distance to avoid square root calculation
                dist_sq = (enemy.x - self.x)**2 + (enemy.y - self.y)**2
                if dist_sq < nearest_dist:
                    nearest_dist = dist_sq
                    self.target = enemy
                
        return self.target is not None

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Check bullet lifetime
        if current_time - self.creation_time > self.max_lifetime:
            self.alive = False
            return
            
        # Check if current target is invalid
        if self.target is None or not self.target.alive or self.target.x <= 0:
            # Try to find a new target
            if not self.find_nearest_target():
                self.alive = False
                return
            
        # Calculate direction to target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
            
        # Normalize and apply speed
        dx = dx / dist * self.speed
        dy = dy / dist * self.speed
        
        # Store last direction for continuing momentum
        self.last_dx = dx
        self.last_dy = dy
        
        # Update position
        self.x += dx
        self.y += dy
        
        # Check for collision with target
        if math.hypot(self.x - self.target.x, self.y - self.target.y) < self.target.radius:
            # Calculate damage considering armor
            damage = 1
            if self.target.enemy_type == "boss" and hasattr(self.target, "damage_reduction"):
                damage *= (1 - self.target.damage_reduction)
            
            self.target.health = round(self.target.health - damage, 1)  # Round to 1 decimal
            if self.target.enemy_type == "boss":
                self.target.health = round(self.target.health)  # Round to whole number for bosses
            # Always destroy bullet on hit
            self.alive = False
            
            if self.target.health <= 0:
                # Handle boss death effects
                if self.target.enemy_type == "boss" and "splitting" in self.target.traits:
                    # Spawn smaller enemies
                    for _ in range(3):
                        new_enemy = Enemy(
                            self.target.level, 
                            "scout",
                            {'health': 0.5, 'speed': 1.2}  # Weaker but faster
                        )
                        new_enemy.x = self.target.x
                        new_enemy.y = self.target.y + random.randint(-30, 30)
                        self.enemies.append(new_enemy)
                
                self.target.alive = False
                return

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

class Turret:
    def __init__(self, x, y, game=None):
        self.x = x
        self.y = y
        self.radius = 15
        self.level = 1
        self.base_fire_rate = 2000  # Base milliseconds between shots
        self.fire_rate = self.base_fire_rate  # Current fire rate
        self.last_shot = 0
        self.bullets = []
        self.game = game  # Store reference to game
        
    def get_upgrade_cost(self):
        # Cost increases exponentially with level
        return 15 * (self.level * 2)  # 15, 30, 60, 120, etc.
        
    def upgrade(self):
        self.level += 1
        # Improve fire rate by 20% per level
        self.fire_rate = int(self.base_fire_rate * (0.8 ** (self.level - 1)))
        
    def get_rect(self):
        # Return a rect for click detection
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                         self.radius * 2, self.radius * 2)

    def update(self, enemies):
        current_time = pygame.time.get_ticks()
        
        # Update existing bullets
        self.bullets = [b for b in self.bullets if b.alive]
        for bullet in self.bullets:
            bullet.update()
            
        # Fire at nearest enemy if time elapsed
        if current_time - self.last_shot > self.fire_rate and enemies:
            # Check if there are any living enemies
            living_enemies = [e for e in enemies if e.alive]
            if living_enemies:
                self.bullets.append(Bullet(self.x, self.y, enemies))
                self.last_shot = current_time

    def draw(self, show_upgrade_info=False):
        # Draw turret base
        pygame.draw.circle(screen, GRAY, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        
        # Draw level number
        small_font = pygame.font.Font(None, 20)
        level_text = small_font.render(str(self.level), True, BLACK)
        level_rect = level_text.get_rect(center=(self.x, self.y))
        screen.blit(level_text, level_rect)
        
        # Always show upgrade cost during upgrade phase
        if self.game and self.game.game_state == UPGRADING:
            cost = self.get_upgrade_cost()
            cost_font = pygame.font.Font(None, 24)  # Slightly larger font
            cost_text = cost_font.render(f"⬆ {cost}p", True, WHITE)
            
            # Draw black outline for better visibility
            outline_color = BLACK
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                outline = cost_font.render(f"⬆ {cost}p", True, outline_color)
                outline_rect = outline.get_rect(centerx=self.x + dx, bottom=self.y - self.radius - 5 + dy)
                screen.blit(outline, outline_rect)
            
            # Draw main text on top
            cost_rect = cost_text.get_rect(centerx=self.x, bottom=self.y - self.radius - 5)
            screen.blit(cost_text, cost_rect)
        
        # Draw detailed upgrade info on hover
        if show_upgrade_info:
            info_font = pygame.font.Font(None, 24)
            cost = self.get_upgrade_cost()
            current_rate = self.fire_rate / 1000  # Convert to seconds
            next_rate = self.base_fire_rate * (0.8 ** self.level) / 1000
            
            # Create info box
            info_lines = [
                f"Level {self.level} Turret",
                f"Current Rate: {current_rate:.1f}s",
                f"Next Level: {next_rate:.1f}s",
                f"Speed Boost: +20%"
            ]
            
            # Calculate box size
            line_height = 25
            box_width = 200
            box_height = len(info_lines) * line_height + 20
            
            # Position box above turret
            box_x = max(10, min(self.x - box_width//2, WINDOW_WIDTH - box_width - 10))
            box_y = max(10, self.y - box_height - 30)
            
            # Draw info box background
            pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 2)
            
            # Draw info text
            for i, line in enumerate(info_lines):
                text = info_font.render(line, True, WHITE)
                text_rect = text.get_rect(centerx=box_x + box_width//2,
                                        y=box_y + 10 + i*line_height)
                screen.blit(text, text_rect)
        
        # Draw all bullets
        for bullet in self.bullets:
            bullet.draw()

class Castle:
    def __init__(self):
        self.health = 100
        self.x = 0
        self.width = CASTLE_WIDTH
        self.height = WINDOW_HEIGHT
        self.towers = [
            {"x": CASTLE_WIDTH - 40, "y": WINDOW_HEIGHT // 4, "height": 150},
            {"x": CASTLE_WIDTH - 40, "y": (WINDOW_HEIGHT * 3) // 4, "height": 150}
        ]
        self.turrets = []
    
    def draw(self):
        # Draw main castle wall
        pygame.draw.rect(screen, GRAY, (self.x, 0, self.width, self.height))
        
        # Draw castle details (bricks)
        for y in range(0, WINDOW_HEIGHT, 30):
            for x in range(0, CASTLE_WIDTH, 60):
                pygame.draw.rect(screen, BLACK, (x, y, 58, 28), 1)
        
        # Draw towers
        for tower in self.towers:
            pygame.draw.rect(screen, BROWN, 
                           (tower["x"], tower["y"] - tower["height"]//2, 
                            40, tower["height"]))
            # Draw tower top
            pygame.draw.polygon(screen, RED,
                              [(tower["x"], tower["y"] - tower["height"]//2),
                               (tower["x"] + 20, tower["y"] - tower["height"]//2 - 20),
                               (tower["x"] + 40, tower["y"] - tower["height"]//2)])
        
        # Draw turrets (with upgrade info if needed)
        mouse_pos = pygame.mouse.get_pos()
        for turret in self.turrets:
            show_info = False
            if hasattr(self, 'game') and self.game.game_state == UPGRADING:
                show_info = turret.get_rect().collidepoint(mouse_pos)
            turret.draw(show_info)
        
        # Draw health
        font = pygame.font.Font(None, 48)
        color = RED if self.health < 10 else GREEN
        health_text = font.render(f"Castle Health: {self.health:3d}", True, color)  # Width of 3 ensures 100 displays properly
        screen.blit(health_text, (WINDOW_WIDTH - 300, 20))

class Enemy:
    def __init__(self, level, enemy_type="regular", difficulty_multipliers=None):
        if difficulty_multipliers is None:
            difficulty_multipliers = {'health': 1.0, 'speed': 1.0}
        self.radius = ENEMY_SIZE // 2
        self.x = WINDOW_WIDTH + self.radius
        self.y = random.randint(self.radius, WINDOW_HEIGHT - self.radius)
        self.enemy_type = enemy_type
        self.alive = True
        self.points_awarded = False  # Track if points have been awarded for this enemy
        
        # Apply difficulty multipliers to base stats
        health_mult = difficulty_multipliers['health']
        speed_mult = difficulty_multipliers['speed']

        if enemy_type == "scout":
            # Scouts are faster but weaker
            self.speed = (3 + (level * 0.7)) * speed_mult
            self.health = max(1, round(1 * health_mult))  # Minimum 1 health
            self.color = (0, 191, 255)  # Deep Sky Blue
            self.radius = int(ENEMY_SIZE // 2.5)  # Smaller size
        elif enemy_type == "boss":
            # Boss enemies are extremely tough
            self.speed = (0.8 + (level * 0.15)) * speed_mult  # Slightly slower but steady
            # Exponential health scaling with level
            base_health = 30  # Higher base health
            level_scaling = level * 10  # Much more health per level
            bonus_health = (level // 3) * 15  # Additional health every 3 levels
            self.health = round((base_health + level_scaling + bonus_health) * health_mult)
            
            # Random color variations
            base_colors = [
                (148, 0, 211),  # Purple
                (178, 34, 34),  # Firebrick Red
                (0, 100, 0),    # Dark Green
                (25, 25, 112),  # Midnight Blue
                (139, 69, 19)   # Saddle Brown
            ]
            self.base_color = random.choice(base_colors)
            self.color = self.base_color
            self.radius = int(ENEMY_SIZE * 1.5)  # Larger size
            
            # Random boss traits
            self.traits = random.sample([
                "armored",    # Takes less damage from bullets
                "regenerating",  # Slowly heals
                "rage",      # Gets faster at low health
                "splitting", # Splits into smaller enemies on death
                "aura"      # Glowing effect
            ], k=2)  # Each boss gets 2 random traits
            
            # Initialize trait-specific properties
            self.regen_rate = 0.05 if "regenerating" in self.traits else 0
            self.damage_reduction = 0.5 if "armored" in self.traits else 0
            self.base_speed = self.speed  # Store original speed for rage trait
            self.rage_threshold = self.health * 0.3  # 30% health triggers rage
            self.last_regen = pygame.time.get_ticks()
        elif enemy_type == "zigzagger":
            # Zigzagger enemies move in a pattern
            self.speed = (2 + (level * 0.4)) * speed_mult
            self.health = max(1, round(2 * health_mult))
            self.color = (255, 165, 0)  # Orange
            self.radius = int(ENEMY_SIZE // 1.5)  # Slightly smaller
            # Zigzag movement parameters
            self.amplitude = 100  # How far up/down it moves
            self.frequency = 0.02  # How fast it zigzags
            self.original_y = self.y  # Store original y position
            self.distance_traveled = 0  # Track distance for zigzag pattern
        else:
            # Regular enemies are slower but tougher
            self.speed = (1.5 + (level * 0.3)) * speed_mult
            self.health = max(1, round(min(5, 1 + level // 3) * health_mult))
            self.color = RED
            
        self.initial_health = self.health  # Store initial health for scoring
        
    def draw(self):
        if not self.alive:
            return
            
        # Draw enemy body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw enemy health number
        font_size = 20 if self.enemy_type == "scout" else 24
        font = pygame.font.Font(None, font_size)
        # Display whole numbers for all enemies (especially bosses)
        health_text = font.render(str(round(self.health)), True, WHITE)
        text_rect = health_text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(health_text, text_rect)
        
        if self.enemy_type == "boss":
            # Draw special effects based on traits
            if "aura" in self.traits:
                # Draw glowing aura
                for radius in range(int(self.radius * 1.5), int(self.radius), -2):
                    alpha = int(128 * (radius - self.radius) / (self.radius * 0.5))
                    aura_color = (*self.base_color, alpha)
                    aura_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(aura_surface, aura_color, 
                                    (radius, radius), radius)
                    screen.blit(aura_surface, 
                              (int(self.x - radius), int(self.y - radius)))
            
            # Draw boss crown with color matching base
            crown_points = [
                (int(self.x - self.radius * 0.8), int(self.y - self.radius * 0.8)),
                (int(self.x - self.radius * 0.4), int(self.y - self.radius * 1.2)),
                (int(self.x), int(self.y - self.radius * 0.8)),
                (int(self.x + self.radius * 0.4), int(self.y - self.radius * 1.2)),
                (int(self.x + self.radius * 0.8), int(self.y - self.radius * 0.8))
            ]
            # Draw crown outline
            pygame.draw.polygon(screen, BLACK, crown_points, 3)
            # Fill crown with slightly lighter version of base color
            crown_color = tuple(min(255, c + 50) for c in self.base_color)
            pygame.draw.polygon(screen, crown_color, crown_points)
            
            # Draw trait indicators
            if "armored" in self.traits:
                # Draw armor plates
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    x1 = self.x + math.cos(rad) * (self.radius * 0.7)
                    y1 = self.y + math.sin(rad) * (self.radius * 0.7)
                    x2 = self.x + math.cos(rad) * self.radius
                    y2 = self.y + math.sin(rad) * self.radius
                    pygame.draw.line(screen, WHITE, (int(x1), int(y1)), 
                                   (int(x2), int(y2)), 3)
            
            if "regenerating" in self.traits:
                # Draw healing symbols
                green_glow = (0, 255, 0, 128)
                glow_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, green_glow, (10, 10), 5)
                screen.blit(glow_surface, (int(self.x - 10), int(self.y - self.radius - 15)))
            
            if "rage" in self.traits:
                # Draw rage indicators (red when active)
                rage_color = RED if self.health <= self.rage_threshold else DARKGRAY
                pygame.draw.line(screen, rage_color, 
                               (int(self.x - 15), int(self.y - 5)),
                               (int(self.x - 5), int(self.y + 5)), 3)
                pygame.draw.line(screen, rage_color,
                               (int(self.x + 15), int(self.y - 5)),
                               (int(self.x + 5), int(self.y + 5)), 3)
            
            # Angry eyes (always present)
            pygame.draw.line(screen, BLACK, 
                           (int(self.x - 10), int(self.y - 5)),
                           (int(self.x - 5), int(self.y)), 3)
            pygame.draw.line(screen, BLACK,
                           (int(self.x + 10), int(self.y - 5)),
                           (int(self.x + 5), int(self.y)), 3)
            
            # Fierce mouth
            pygame.draw.line(screen, BLACK,
                           (int(self.x - 8), int(self.y + 8)),
                           (int(self.x + 8), int(self.y + 8)), 3)
                           
        elif self.enemy_type == "scout":
            # Scout details - sleeker look
            eye_offset = 3
            pygame.draw.circle(screen, BLACK, (int(self.x - 3), int(self.y - 8)), 2)
            pygame.draw.circle(screen, BLACK, (int(self.x + 3), int(self.y - 8)), 2)
            # Pointy mouth for scouts
            pygame.draw.polygon(screen, BLACK, [
                (int(self.x - 5), int(self.y + 3)),
                (int(self.x + 5), int(self.y + 3)),
                (int(self.x), int(self.y + 7))
            ])
        else:
            # Regular enemy details
            pygame.draw.circle(screen, BLACK, (int(self.x - 5), int(self.y - 12)), 3)
            pygame.draw.circle(screen, BLACK, (int(self.x + 5), int(self.y - 12)), 3)
            pygame.draw.line(screen, BLACK, 
                           (int(self.x - 8), int(self.y + 5)),
                           (int(self.x + 8), int(self.y + 5)), 2)
    
    def update(self):
        if not self.alive:
            return
        
        current_time = pygame.time.get_ticks()
        
        if self.enemy_type == "boss":
            # Boss-specific trait updates
            if "regenerating" in self.traits:
                # Regenerate health every second
                if current_time - self.last_regen >= 1000:  # 1000ms = 1 second
                    self.health = round(min(self.initial_health, self.health + self.regen_rate * self.initial_health))
                    self.last_regen = current_time
                    
            if "rage" in self.traits and self.health <= self.rage_threshold:
                # Speed up when health is low
                self.speed = self.base_speed * 1.5
            
            self.x -= self.speed
            
        elif self.enemy_type == "zigzagger":
            # Update horizontal position
            self.x -= self.speed
            # Update distance traveled for zigzag calculation
            self.distance_traveled += self.speed
            # Calculate new y position using sine wave
            self.y = self.original_y + math.sin(self.distance_traveled * self.frequency) * self.amplitude
            # Keep within screen bounds
            self.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.y))
        else:
            self.x -= self.speed
    
    def check_castle_collision(self, castle):
        return self.x - self.radius <= CASTLE_WIDTH
    
    def check_click(self, pos):
        if not self.alive:
            return False
        distance = math.hypot(pos[0] - self.x, pos[1] - self.y)
        return distance <= self.radius

class ClickEffect:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.creation_time = pygame.time.get_ticks()
        self.alpha = 255  # Start fully opaque

    def update(self, current_time, duration):
        time_alive = current_time - self.creation_time
        if time_alive >= duration:
            return False
        # Fade out over time
        self.alpha = int(255 * (1 - (time_alive / duration)))
        return True

    def draw(self):
        # Create a surface for the click effect with transparency
        surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        # Draw expanding circles with decreasing opacity
        for r in range(self.radius, 0, -4):
            alpha = int((r / self.radius) * self.alpha)
            pygame.draw.circle(surface, (255, 255, 255, alpha), 
                             (self.radius, self.radius), r)
        # Draw the surface onto the screen
        screen.blit(surface, 
                   (self.x - self.radius, self.y - self.radius))

    def check_enemy_collision(self, enemy):
        distance = math.hypot(self.x - enemy.x, self.y - enemy.y)
        return distance <= self.radius + enemy.radius

class Game:
    def __init__(self, start_level=1, start_points=0, start_in_store=False, difficulty='normal'):
        # Set difficulty multipliers
        self.difficulty = difficulty
        if difficulty == 'easy':
            self.enemy_health_multiplier = 0.7  # Enemies have 30% less health
            self.enemy_speed_multiplier = 0.8   # Enemies are 20% slower
            self.spawn_rate_multiplier = 1.3    # 30% slower spawn rate
            self.castle_health_bonus = 50       # Extra starting health
            self.point_multiplier = 1.2         # 20% more points
        elif difficulty == 'hard':
            self.enemy_health_multiplier = 1.3  # Enemies have 30% more health
            self.enemy_speed_multiplier = 1.2   # Enemies are 20% faster
            self.spawn_rate_multiplier = 0.8    # 20% faster spawn rate
            self.castle_health_bonus = 0        # No health bonus
            self.point_multiplier = 0.8         # 20% fewer points
        else:  # normal
            self.enemy_health_multiplier = 1.0
            self.enemy_speed_multiplier = 1.0
            self.spawn_rate_multiplier = 1.0
            self.castle_health_bonus = 0
            self.point_multiplier = 1.0

        self.castle = Castle()
        self.castle.health += self.castle_health_bonus  # Apply health bonus
        self.enemies = []
        self.level = start_level
        self.score = start_points
        self.last_spawn = pygame.time.get_ticks()
        self.level_start_time = pygame.time.get_ticks()
        self.game_state = UPGRADING if start_in_store else PLAYING
        self.boss_spawned = False  # Initialize boss spawn flag
        # Click effect system
        self.click_effects = []  # List to store active click effects
        self.CLICK_RADIUS = 20  # Size of the click effect circle
        self.CLICK_DURATION = 150  # How long the click effect lasts (milliseconds)
        
        # Debug info for testing mode
        if start_level > 1 or start_points > 0 or start_in_store:
            print(f"Testing Mode Active:")
            print(f"Starting Level: {start_level}")
            print(f"Starting Points: {start_points}")
            print(f"Difficulty: {difficulty}")
            if start_in_store:
                print("Starting in Upgrade Store")
        # More aggressive spawn delay reduction at higher levels
        base_reduction = 300 + (self.level * 100)  # Increases reduction with level
        self.spawn_delay = max(MIN_SPAWN_RATE, SPAWN_RATE - base_reduction)
        self.upgrade_button_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 80, 200, 50)
        # Error message system
        self.error_message = None
        self.error_time = 0
        self.error_duration = 2000  # Error message lasts 2 seconds
        # Turret system
        self.placing_turret = False
        self.TURRET_COST = 30
        
        # Debug info for testing mode
        if start_level > 1 or start_points > 0 or start_in_store:
            print(f"Testing Mode Active:")
            print(f"Starting Level: {start_level}")
            print(f"Starting Points: {start_points}")
            if start_in_store:
                print("Starting in Upgrade Store")
    
    def spawn_enemy(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn > (self.spawn_delay * self.spawn_rate_multiplier):
            # Calculate number of enemies to spawn based on level
            max_group_size = min(1 + self.level // 2, 5)  # Max 5 enemies at once
            num_enemies = random.randint(1, max_group_size)
            
            # Set up enemy type chances based on level
            SCOUT_INTRO_LEVEL = 3
            ZIGZAGGER_INTRO_LEVEL = 2
            
            can_spawn_scouts = self.level >= SCOUT_INTRO_LEVEL
            can_spawn_zigzaggers = self.level >= ZIGZAGGER_INTRO_LEVEL
            
            # Calculate spawn chances
            scout_chance = min(0.1 + ((self.level - SCOUT_INTRO_LEVEL) * 0.05), 0.4) if can_spawn_scouts else 0
            zigzagger_chance = min(0.15 + ((self.level - ZIGZAGGER_INTRO_LEVEL) * 0.04), 0.3) if can_spawn_zigzaggers else 0
            
            # Show warning messages for new enemy types
            if can_spawn_scouts and not hasattr(self, 'scouts_introduced') and self.game_state == PLAYING:
                self.error_message = "Warning: Fast scout enemies have appeared!"
                self.error_time = pygame.time.get_ticks()
                self.scouts_introduced = True
                
            if can_spawn_zigzaggers and not hasattr(self, 'zigzaggers_introduced') and self.game_state == PLAYING:
                self.error_message = "Warning: Zigzagging enemies approaching!"
                self.error_time = pygame.time.get_ticks()
                self.zigzaggers_introduced = True
            
            # Spawn group of enemies with slight position variations
            for _ in range(num_enemies):
                    # Determine enemy type based on chances
                rand = random.random()
                if rand < scout_chance:
                    enemy_type = "scout"
                elif rand < (scout_chance + zigzagger_chance):
                    enemy_type = "zigzagger"
                else:
                    enemy_type = "regular"
                difficulty_multipliers = {
                    'health': self.enemy_health_multiplier,
                    'speed': self.enemy_speed_multiplier
                }
                enemy = Enemy(self.level, enemy_type, difficulty_multipliers)
                
                # Vary vertical position slightly within group
                enemy.y += random.randint(-30, 30)
                # Keep within screen bounds
                enemy.y = max(enemy.radius, min(WINDOW_HEIGHT - enemy.radius, enemy.y))
                # Vary horizontal position slightly for group
                # Scouts appear slightly further back
                if enemy_type == "scout":
                    enemy.x += random.randint(50, 100)
                else:
                    enemy.x += random.randint(0, 50)
                self.enemies.append(enemy)
            
            # Vary next spawn delay
            base_delay = self.spawn_delay
            self.spawn_delay = random.randint(
                int(base_delay * 0.7),  # 30% faster than base delay
                int(base_delay * 1.3)   # 30% slower than base delay
            )
            self.last_spawn = current_time
    
    def update(self):
        if self.game_state == GAME_OVER:
            return
        
        # Update click effects and remove expired ones
        current_time = pygame.time.get_ticks()
        self.click_effects = [effect for effect in self.click_effects 
                            if effect.update(current_time, self.CLICK_DURATION)]
            
        if self.game_state == PLAYING:
            # Check if level time is up
            current_time = pygame.time.get_ticks()
            elapsed_seconds = (current_time - self.level_start_time) // 1000
            
            # Debug boss spawn conditions
            if self.level % 5 == 0:  # Every 5th level
                if elapsed_seconds == 1:  # At start of level
                    print(f"This is a boss level (level {self.level})")
                if elapsed_seconds == 14:  # Just before spawn time
                    print(f"Boss spawn imminent. Level: {self.level}, Time: {elapsed_seconds}")
                
                # Check for boss spawn at 15 seconds
                if elapsed_seconds == 15:
                    if not hasattr(self, 'boss_spawned') or not self.boss_spawned:
                        print(f"Spawning boss! Level: {self.level}")
                        # Spawn boss
                        boss = Enemy(self.level, "boss")
                        boss.y = WINDOW_HEIGHT // 2  # Spawn in middle of screen
                        boss.x = WINDOW_WIDTH + boss.radius  # Make sure it starts off screen
                        self.enemies.append(boss)
                        self.boss_spawned = True
                        # Warning message
                        self.error_message = "WARNING: Boss Enemy Approaching!"
                        self.error_time = current_time
                        self.error_duration = 3000  # Show warning for 3 seconds
            
            if (current_time - self.level_start_time) >= LEVEL_DURATION * 1000:
                self.game_state = UPGRADING
                self.boss_spawned = False  # Reset boss spawn flag for next level
                return
            
            # Spawn regular enemies
            self.spawn_enemy()
            
            # Update enemies
            for enemy in self.enemies:
                enemy.update()
                if enemy.alive and enemy.check_castle_collision(self.castle):
                    enemy.alive = False
                    self.castle.health -= enemy.health
                    if self.castle.health <= 0:
                        self.castle.health = 0
                        self.game_state = GAME_OVER
            
            # Update turrets
            for turret in self.castle.turrets:
                turret.update(self.enemies)
        
        # Handle dead enemies and update score
        # Remove enemies that are off-screen to the left
        self.enemies = [enemy for enemy in self.enemies if enemy.x + enemy.radius > 0]
        
        # Handle dead enemies and award points
        for enemy in self.enemies:
            if not enemy.alive and not enemy.points_awarded:
                self.score += enemy.initial_health
                enemy.points_awarded = True
                
        # Keep only relevant enemies
        self.enemies = [enemy for enemy in self.enemies if enemy.alive or not enemy.points_awarded]
        
        # Remove this auto-level up based on score as levels now progress through the upgrade screen
    
    def draw(self):
        # Fill background
        screen.fill(BLACK)
        
        # Draw castle
        self.castle.draw()
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw()
        
        # Draw click effects
        for effect in self.click_effects:
            effect.draw()
        
        # Draw score and level
        font = pygame.font.Font(None, 28)  # Smaller font size
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        # Position text after the castle wall
        screen.blit(score_text, (CASTLE_WIDTH + 20, 10))
        screen.blit(level_text, (CASTLE_WIDTH + 20, 40))
        
        # Draw timer
        if self.game_state == PLAYING:
            time_left = LEVEL_DURATION - ((pygame.time.get_ticks() - self.level_start_time) // 1000)
            time_text = font.render(f"Time: {time_left:2d}", True, WHITE)
            screen.blit(time_text, (WINDOW_WIDTH - 300, 60))
            
        # Draw upgrade screen
        elif self.game_state == UPGRADING:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            
            # Draw upgrade options
            title_font = pygame.font.Font(None, 48)
            title = title_font.render(f"Level {self.level} Complete!", True, WHITE)
            screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//4))
            
            # Draw available points
            points_text = font.render(f"Available Points: {self.score}", True, WHITE)
            screen.blit(points_text, (WINDOW_WIDTH//2 - points_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
            
            # Draw health upgrade option
            health_cost = HEALTH_UPGRADE_COST
            health_text = font.render(f"Buy 1 Health ({health_cost} points)", True, WHITE)
            health_rect = health_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(health_text, health_rect)
            
            # Draw turret upgrade option
            turret_text = font.render(f"Buy Turret ({self.TURRET_COST} points)", True, WHITE)
            self.turret_rect = turret_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))
            screen.blit(turret_text, self.turret_rect)
            
            # Draw continue button
            pygame.draw.rect(screen, GREEN, self.upgrade_button_rect)
            continue_text = font.render("Continue to Next Level", True, BLACK)
            text_rect = continue_text.get_rect(center=self.upgrade_button_rect.center)
            screen.blit(continue_text, text_rect)
            
            # Draw error message if it exists
            if self.error_message:
                current_time = pygame.time.get_ticks()
                if current_time - self.error_time < self.error_duration:
                    # Calculate alpha based on time remaining
                    alpha = 255 * (1 - (current_time - self.error_time) / self.error_duration)
                    error_font = pygame.font.Font(None, 36)
                    error_text = error_font.render(self.error_message, True, RED)
                    error_text.set_alpha(alpha)
                    error_rect = error_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
                    screen.blit(error_text, error_rect)
                else:
                    self.error_message = None
        
        # Draw game over
        if self.game_state == GAME_OVER:
            font = pygame.font.Font(None, 74)
            game_over_text = font.render("GAME OVER", True, RED)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over_text, 
                       (WINDOW_WIDTH//2 - game_over_text.get_width()//2, 
                        WINDOW_HEIGHT//2 - 50))
            screen.blit(restart_text, 
                       (WINDOW_WIDTH//2 - restart_text.get_width()//2, 
                        WINDOW_HEIGHT//2 + 50))
    
    def handle_click(self, pos):
        if self.game_state == GAME_OVER:
            return
            
        if self.game_state == PLAYING:
            # Create click effect
            click_effect = ClickEffect(pos[0], pos[1], self.CLICK_RADIUS)
            self.click_effects.append(click_effect)
            
            # Check for enemies in the click radius
            damaged_enemies = False
            for enemy in self.enemies:
                if click_effect.check_enemy_collision(enemy):
                    damaged_enemies = True
                    enemy.health -= 1
                    if enemy.health <= 0:
                        enemy.alive = False
                        if not enemy.points_awarded:
                            self.score += enemy.initial_health
                            enemy.points_awarded = True
                            
        elif self.game_state == UPGRADING:
            if self.placing_turret:
                # Only allow placement on castle
                if pos[0] <= CASTLE_WIDTH:
                    # Check distance to other turrets
                    min_spacing = 40  # Minimum pixels between turret centers
                    too_close = False
                    for turret in self.castle.turrets:
                        distance = math.hypot(pos[0] - turret.x, pos[1] - turret.y)
                        if distance < min_spacing:
                            too_close = True
                            self.error_message = "Turrets must be spaced further apart!"
                            self.error_time = pygame.time.get_ticks()
                            break
                    
                    if not too_close:
                        new_turret = Turret(pos[0], pos[1], self)
                        self.castle.turrets.append(new_turret)
                        self.score -= self.TURRET_COST
                        self.placing_turret = False
                return
            
            # Check for turret upgrades first
            for turret in self.castle.turrets:
                if turret.get_rect().collidepoint(pos):
                    upgrade_cost = turret.get_upgrade_cost()
                    if self.score >= upgrade_cost:
                        self.score -= upgrade_cost
                        turret.upgrade()
                        self.error_message = f"Turret upgraded to level {turret.level}!"
                        self.error_time = pygame.time.get_ticks()
                    else:
                        self.error_message = f"Not enough points! Need {upgrade_cost} points."
                        self.error_time = pygame.time.get_ticks()
                    return
                
            # Check for health upgrade click
            health_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 15, 200, 30)
            if health_rect.collidepoint(pos):
                if self.score >= HEALTH_UPGRADE_COST:
                    self.castle.health += 1
                    self.score -= HEALTH_UPGRADE_COST
                else:
                    self.error_message = f"Not enough points! Need {HEALTH_UPGRADE_COST} points."
                    self.error_time = pygame.time.get_ticks()
            
            # Check for turret purchase click
            elif self.turret_rect.collidepoint(pos):
                if self.score >= self.TURRET_COST:
                    self.placing_turret = True
                    self.error_message = "Click on the castle to place the turret"
                    self.error_time = pygame.time.get_ticks()
                else:
                    self.error_message = f"Not enough points! Need {self.TURRET_COST} points."
                    self.error_time = pygame.time.get_ticks()
                
            # Check for continue button click
            elif self.upgrade_button_rect.collidepoint(pos):
                if self.placing_turret:
                    self.placing_turret = False
                else:
                    if not hasattr(self, 'first_level'):
                        # If starting from upgrade store, don't increment level first time
                        self.first_level = True
                    else:
                        self.level += 1
                    print(f"Starting level {self.level}")
                    self.level_start_time = pygame.time.get_ticks()
                    self.spawn_delay = max(MIN_SPAWN_RATE, SPAWN_RATE - (self.level * 200))
                    self.game_state = PLAYING
                    self.boss_spawned = False  # Reset boss spawn flag

class DifficultySelector:
    def __init__(self):
        # Calculate initial positions
        option_width = 300
        option_height = 400
        total_width = 3 * (option_width + 50)  # 3 options
        start_x = (WINDOW_WIDTH - total_width) // 2
        
        self.options = [
            {
                'name': 'Easy',
                'description': [
                    'Recommended for young players',
                    '• Weaker enemies',
                    '• Extra castle health',
                    '• More points earned',
                    '• Slower enemy spawns'
                ],
                'color': (0, 255, 0),  # Green
                'rect': pygame.Rect(
                    start_x - 10,
                    190,  # 200 - 10 for padding
                    option_width + 20,
                    option_height + 20
                )
            },
            {
                'name': 'Normal',
                'description': [
                    'Standard game balance',
                    '• Regular enemy strength',
                    '• Normal spawn rates',
                    '• Standard scoring'
                ],
                'color': (255, 255, 0),  # Yellow
                'rect': pygame.Rect(
                    start_x + (option_width + 50) - 10,
                    190,
                    option_width + 20,
                    option_height + 20
                )
            },
            {
                'name': 'Hard',
                'description': [
                    'For experienced players',
                    '• Tougher enemies',
                    '• Faster enemy movement',
                    '• Rapid spawns',
                    '• Lower scoring'
                ],
                'color': (255, 0, 0),  # Red
                'rect': pygame.Rect(
                    start_x + 2 * (option_width + 50) - 10,
                    190,
                    option_width + 20,
                    option_height + 20
                )
            }
        ]
        self.selected = 1  # Default to Normal
        self.hovered = None  # Track which option is being hovered
        self.title_font = pygame.font.Font(None, 74)
        self.option_font = pygame.font.Font(None, 48)
        self.desc_font = pygame.font.Font(None, 32)

    def draw(self, screen):
        screen.fill(BLACK)
        
        # Draw title
        title = self.title_font.render("Select Difficulty", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        # Draw each option
        option_width = 300
        option_height = 400
        total_width = len(self.options) * (option_width + 50)
        start_x = (WINDOW_WIDTH - total_width) // 2
        
        # Get current mouse position for hover effect
        mouse_pos = pygame.mouse.get_pos()
        
        for i, option in enumerate(self.options):
            x = start_x + i * (option_width + 50)
            y = 200
            
            # Update the rectangle position (in case window was resized)
            option['rect'].x = x-10
            option['rect'].y = y-10
            
            # Check if mouse is hovering over this option
            is_hovered = option['rect'].collidepoint(mouse_pos)
            is_selected = i == self.selected
            
            # Draw option background with hover effect
            if is_hovered or is_selected:
                # Draw outer glow effect
                for offset in range(6, 0, -1):
                    alpha = 100 if is_selected else 50
                    if is_hovered:
                        alpha = min(255, alpha + 100)
                    glow_surface = pygame.Surface((option_width+20+offset*2, option_height+20+offset*2), pygame.SRCALPHA)
                    glow_color = (*option['color'], alpha // offset)
                    pygame.draw.rect(glow_surface, glow_color, 
                                   (0, 0, option_width+20+offset*2, option_height+20+offset*2))
                    screen.blit(glow_surface, 
                              (x-10-offset, y-10-offset))
            
            # Draw the main option box
            pygame.draw.rect(screen, (*option['color'], 40), 
                           option['rect'])
            pygame.draw.rect(screen, option['color'], 
                           option['rect'], 3)
            
            # Draw difficulty name
            name_text = self.option_font.render(option['name'], True, option['color'])
            name_rect = name_text.get_rect(center=(x + option_width//2, y + 40))
            screen.blit(name_text, name_rect)
            
            # Draw description lines
            for j, line in enumerate(option['description']):
                desc_text = self.desc_font.render(line, True, DARKGRAY)
                desc_rect = desc_text.get_rect(center=(x + option_width//2, y + 120 + j*40))
                screen.blit(desc_text, desc_rect)
        
        # Draw instructions
        instructions = [
            "Click to select difficulty",
            "Press ESC to quit"
        ]
        for i, instruction in enumerate(instructions):
            inst_text = self.desc_font.render(instruction, True, GRAY)
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80 + i*30))
            screen.blit(inst_text, inst_rect)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if click was on any option
            for i, option in enumerate(self.options):
                if option['rect'].collidepoint(event.pos):
                    return option['name'].lower()
        elif event.type == pygame.MOUSEMOTION:
            # Update selected based on hover
            for i, option in enumerate(self.options):
                if option['rect'].collidepoint(event.pos):
                    self.selected = i
                    break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected = max(0, self.selected - 1)
            elif event.key == pygame.K_RIGHT:
                self.selected = min(len(self.options) - 1, self.selected)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected]['name'].lower()
        return None

def main():
    # Add command line argument parsing
    import argparse
    parser = argparse.ArgumentParser(description='Castle Defense Game')
    parser.add_argument('--level', type=int, default=1, help='Starting level (default: 1)')
    parser.add_argument('--points', type=int, default=0, help='Starting points (default: 0)')
    parser.add_argument('--upgrade-store', action='store_true', help='Start in upgrade store')
    parser.add_argument('--difficulty', type=str, choices=['easy', 'normal', 'hard'], 
                      help='Game difficulty (default: show selection screen)')
    args = parser.parse_args()
    
    # Initialize display
    init_display()
    
    difficulty = args.difficulty
    if difficulty is None:
        # Show difficulty selection screen
        selector = DifficultySelector()
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
                
                result = selector.handle_input(event)
                if result is not None:
                    difficulty = result
                    running = False
            
            selector.draw(screen)
            pygame.display.flip()
            clock.tick(60)
    
    if difficulty is None:  # User closed the window during difficulty selection
        return
        
    # Create game with custom starting values
    game = Game(start_level=args.level, start_points=args.points, 
                start_in_store=args.upgrade_store, difficulty=difficulty)
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.game_state == GAME_OVER:
                    game = Game()  # Reset the game
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
