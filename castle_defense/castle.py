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
    def __init__(self, level, enemy_type="regular"):
        self.radius = ENEMY_SIZE // 2
        self.x = WINDOW_WIDTH + self.radius
        self.y = random.randint(self.radius, WINDOW_HEIGHT - self.radius)
        self.enemy_type = enemy_type
        self.alive = True
        self.points_awarded = False  # Track if points have been awarded for this enemy
        
        if enemy_type == "scout":
            # Scouts are faster but weaker
            self.speed = 3 + (level * 0.7)  # Higher base speed and scaling
            self.health = 1  # Always 1 health
            self.color = (0, 191, 255)  # Deep Sky Blue
            self.radius = int(ENEMY_SIZE // 2.5)  # Smaller size
        else:
            # Regular enemies are slower but tougher
            self.speed = 1.5 + (level * 0.3)  # Reduced base speed and scaling
            self.health = min(5, 1 + level // 3)
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
        
        if self.enemy_type == "scout":
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
        self.x -= self.speed
    
    def check_castle_collision(self, castle):
        return self.x - self.radius <= CASTLE_WIDTH
    
    def check_click(self, pos):
        if not self.alive:
            return False
        distance = math.hypot(pos[0] - self.x, pos[1] - self.y)
        return distance <= self.radius

class Game:
    def __init__(self, start_level=1, start_points=0, start_in_store=False):
        self.castle = Castle()
        self.enemies = []
        self.level = start_level
        self.score = start_points
        self.last_spawn = pygame.time.get_ticks()
        self.level_start_time = pygame.time.get_ticks()
        self.game_state = UPGRADING if start_in_store else PLAYING
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
        self.TURRET_COST = 10
        
        # Debug info for testing mode
        if start_level > 1 or start_points > 0 or start_in_store:
            print(f"Testing Mode Active:")
            print(f"Starting Level: {start_level}")
            print(f"Starting Points: {start_points}")
            if start_in_store:
                print("Starting in Upgrade Store")
    
    def spawn_enemy(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn > self.spawn_delay:
            # Calculate number of enemies to spawn based on level
            max_group_size = min(1 + self.level // 2, 5)  # Max 5 enemies at once
            num_enemies = random.randint(1, max_group_size)
            
            # Scouts only appear from level 3 onwards
            SCOUT_INTRO_LEVEL = 3
            can_spawn_scouts = self.level >= SCOUT_INTRO_LEVEL
            
            if can_spawn_scouts:
                # Scout chance increases with level, starting at 10% at level 3
                # +5% per level after that, maxing at 40%
                scout_chance = min(0.1 + ((self.level - SCOUT_INTRO_LEVEL) * 0.05), 0.4)
                
                # Show warning message on first scout encounter
                if not hasattr(self, 'scouts_introduced') and self.game_state == PLAYING:
                    self.error_message = "Warning: Fast scout enemies have appeared!"
                    self.error_time = pygame.time.get_ticks()
                    self.scouts_introduced = True
            else:
                scout_chance = 0
            
            # Spawn group of enemies with slight position variations
            for _ in range(num_enemies):
                # Decide if this enemy should be a scout
                enemy_type = "scout" if random.random() < scout_chance else "regular"
                enemy = Enemy(self.level, enemy_type)
                
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
            
        if self.game_state == PLAYING:
            # Check if level time is up
            current_time = pygame.time.get_ticks()
            if (current_time - self.level_start_time) >= LEVEL_DURATION * 1000:
                self.game_state = UPGRADING
                return
            
            # Spawn enemies
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
            for enemy in self.enemies:
                if enemy.check_click(pos):
                    enemy.health -= 1
                    if enemy.health <= 0:
                        enemy.alive = False
                        if not enemy.points_awarded:
                            self.score += enemy.initial_health
                            enemy.points_awarded = True
                    return
                    
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
                    self.level += 1
                    self.level_start_time = pygame.time.get_ticks()
                    self.spawn_delay = max(MIN_SPAWN_RATE, SPAWN_RATE - (self.level * 200))
                    self.game_state = PLAYING

def main():
    # Add command line argument parsing
    import argparse
    parser = argparse.ArgumentParser(description='Castle Defense Game')
    parser.add_argument('--level', type=int, default=1, help='Starting level (default: 1)')
    parser.add_argument('--points', type=int, default=0, help='Starting points (default: 0)')
    parser.add_argument('--upgrade-store', action='store_true', help='Start in upgrade store')
    args = parser.parse_args()
    
    # Initialize display
    init_display()
    
    # Create game with custom starting values
    game = Game(start_level=args.level, start_points=args.points, start_in_store=args.upgrade_store)
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
