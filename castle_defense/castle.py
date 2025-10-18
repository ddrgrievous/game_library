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
        self.switch_time = 0  # Time when we can switch targets
        self.switch_delay = 50  # Milliseconds to wait before switching targets
        self.find_nearest_target()

    def find_nearest_target(self):
        # Find nearest living enemy that's on screen
        nearest_dist = float('inf')
        self.target = None
        living_enemies = [e for e in self.enemies if e.alive and e.x > 0]
        
        if not living_enemies:
            return False
            
        for enemy in living_enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist < nearest_dist:
                nearest_dist = dist
                self.target = enemy
                
        return True  # We know we found a target because we checked living_enemies

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Check if current target is invalid and enough time has passed to switch
        if (self.target is None or not self.target.alive or self.target.x <= 0) and current_time >= self.switch_time:
            # Try to find a new target
            if not self.find_nearest_target():
                self.alive = False
                return
        
        # If we have an invalid target but haven't waited long enough, keep moving in the same direction
        if self.target is None or not self.target.alive or self.target.x <= 0:
            # Keep moving in current direction
            if hasattr(self, 'last_dx') and hasattr(self, 'last_dy'):
                self.x += self.last_dx
                self.y += self.last_dy
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
            self.target.health -= 1
            if self.target.health <= 0:
                # Target died, set switch time before looking for new target
                self.target.alive = False
                self.switch_time = current_time + self.switch_delay
                # Keep moving in current direction until switch_time
                return
            # If target survived, bullet disappears
            self.alive = False

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

class Turret:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.fire_rate = 2000  # milliseconds between shots
        self.last_shot = 0
        self.bullets = []

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

    def draw(self):
        # Draw turret base
        pygame.draw.circle(screen, GRAY, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        
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
        
        # Draw turrets
        for turret in self.turrets:
            turret.draw()
        
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
            # Boss enemies are tough and moderately fast
            self.speed = (1.0 + (level * 0.2)) * speed_mult
            self.health = round((10 + (level // 5) * 5) * health_mult)
            self.color = (148, 0, 211)  # Purple
            self.radius = int(ENEMY_SIZE * 1.5)  # Larger size
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
        health_text = font.render(str(self.health), True, WHITE)
        text_rect = health_text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(health_text, text_rect)
        
        if self.enemy_type == "boss":
            # Boss details - crown and angry eyes
            # Draw crown
            crown_points = [
                (int(self.x - self.radius * 0.8), int(self.y - self.radius * 0.8)),
                (int(self.x - self.radius * 0.4), int(self.y - self.radius * 1.2)),
                (int(self.x), int(self.y - self.radius * 0.8)),
                (int(self.x + self.radius * 0.4), int(self.y - self.radius * 1.2)),
                (int(self.x + self.radius * 0.8), int(self.y - self.radius * 0.8))
            ]
            pygame.draw.polygon(screen, (255, 215, 0), crown_points)  # Gold crown
            
            # Angry eyes
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
        
        if self.enemy_type == "zigzagger":
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
        current_enemies = []
        for enemy in self.enemies:
            if not enemy.alive and not enemy.points_awarded:  # Award points for turret kills
                self.score += enemy.initial_health
                enemy.points_awarded = True
            if enemy.alive or enemy.x > 0:
                current_enemies.append(enemy)
        self.enemies = current_enemies
        
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
                            self.score += round(enemy.initial_health * self.point_multiplier)
                            enemy.points_awarded = True
                    
        elif self.game_state == UPGRADING:
            if self.placing_turret:
                # Only allow placement on castle
                if pos[0] <= CASTLE_WIDTH:
                    self.castle.turrets.append(Turret(pos[0], pos[1]))
                    self.score -= self.TURRET_COST
                    self.placing_turret = False
                return
                
            # Check for health upgrade click
            mouse_x, mouse_y = pos
            health_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 15, 200, 30)
            if health_rect.collidepoint(pos):
                if self.score >= HEALTH_UPGRADE_COST:
                    self.castle.health += 1
                    self.score -= HEALTH_UPGRADE_COST
                else:
                    self.error_message = f"Not enough points! Need {HEALTH_UPGRADE_COST} points."
                    self.error_time = pygame.time.get_ticks()
            
            # Check for turret upgrade click
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
