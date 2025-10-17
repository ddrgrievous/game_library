import pygame
import random
import math

# Constants
WIDTH, HEIGHT = 800, 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 191, 255)
PURPLE = (147, 0, 211)
YELLOW = (255, 255, 0)

# Global variables
screen = None
ship = None
asteroids = []
bullets = []
score = 0
high_score = 0

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2

def init_display():
    global screen
    if screen is None:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Asteroids")

def draw_text(text, size, x, y):
    font = pygame.font.Font(None, size)
    surface = font.render(text, True, WHITE)
    rect = surface.get_rect()
    rect.midtop = (x, y)
    screen.blit(surface, rect)

def collide(obj1, obj2):
    dist = math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)
    return dist < obj1.radius + obj2.radius

class Menu:
    def __init__(self):
        self.options = ["Easy", "Medium", "Hard"]
        self.selected = 0
        
    def draw(self):
        # Draw title
        draw_text("ASTEROIDS", 64, WIDTH // 2, HEIGHT // 4)
        
        # Draw difficulty options
        for i, option in enumerate(self.options):
            color = GREEN if i == self.selected else WHITE
            y_pos = HEIGHT // 2 + i * 60
            draw_text(option, 48, WIDTH // 2, y_pos)
        
        # Draw instructions
        draw_text("Use UP/DOWN arrows to select, SPACE to start", 30, WIDTH // 2, HEIGHT * 3 // 4)

    def draw(self):
        if not self.active:
            return
            
        # Draw spinning hexagon
        self.angle += 1
        points = []
        for i in range(6):
            angle = math.radians(self.angle + i * 60)
            px = self.x + math.cos(angle) * self.radius
            py = self.y + math.sin(angle) * self.radius
            points.append((px, py))
        
        # Draw hexagon
        pygame.draw.polygon(screen, self.color, points, 2)
        
        # Draw symbol
        font = pygame.font.Font(None, 24)
        text = font.render(self.symbol, True, self.color)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False

# Difficulty Settings
EASY = 0
MEDIUM = 1
HARD = 2

# Ship class
class Ship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed = 0
        self.radius = 15
        self.invulnerable = 0
        self.lives = 3
        
        # Power-up states
        self.multi_shot = 0  # Timer for multi-shot
        self.laser_shot = 0  # Timer for laser shot
        self.shield = 0      # Timer for shield
        self.big_bullets = 0 # Timer for big bullets
        self.power_up_duration = 30 * 60  # 30 seconds at 60 FPS

    def draw(self):
        # Draw shield if active
        if self.shield > 0:
            shield_points = []
            num_points = 16
            for i in range(num_points):
                angle = math.radians(i * (360/num_points) + pygame.time.get_ticks() / 10)
                shield_x = self.x + math.cos(angle) * (self.radius + 10)
                shield_y = self.y + math.sin(angle) * (self.radius + 10)
                shield_points.append((shield_x, shield_y))
            pygame.draw.polygon(screen, GREEN, shield_points, 2)

        if self.invulnerable == 0 or pygame.time.get_ticks() % 200 < 100:
            # Draw ship
            points = []
            for i in [0, 140, 220]:
                ang = math.radians(self.angle + i)
                px = self.x + math.cos(ang) * self.radius
                py = self.y + math.sin(ang) * self.radius
                points.append((px, py))
            
            # Change ship color based on active power-up
            ship_color = WHITE
            if self.multi_shot > 0:
                ship_color = BLUE
            elif self.laser_shot > 0:
                ship_color = RED
            elif self.big_bullets > 0:
                ship_color = YELLOW
                
            pygame.draw.polygon(screen, ship_color, points, 2)
            
            # Draw thrust flame when accelerating
            if self.speed > 0:
                flame_points = []
                for i in [-20, 0, 20]:
                    ang = math.radians(self.angle + 180 + i)
                    px = self.x + math.cos(ang) * (self.radius + 5)
                    py = self.y + math.sin(ang) * (self.radius + 5)
                    flame_points.append((px, py))
                pygame.draw.polygon(screen, ship_color, flame_points, 1)

    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        self.x %= WIDTH
        self.y %= HEIGHT
        if self.invulnerable > 0:
            self.invulnerable -= 1
            
        # Update power-up timers
        if self.multi_shot > 0:
            self.multi_shot -= 1
        if self.laser_shot > 0:
            self.laser_shot -= 1
        if self.shield > 0:
            self.shield -= 1
        if self.big_bullets > 0:
            self.big_bullets -= 1

    def apply_power_up(self, power_type):
        if power_type == MULTI_SHOT:
            self.multi_shot = self.power_up_duration
        elif power_type == LASER_SHOT:
            self.laser_shot = self.power_up_duration
        elif power_type == SHIELD:
            self.shield = self.power_up_duration
        elif power_type == BIG_BULLETS:
            self.big_bullets = self.power_up_duration

    def shoot(self):
        bullets = []
        if self.multi_shot > 0:
            # Triple shot spread pattern
            for angle_offset in [-20, 0, 20]:
                bullets.append(Bullet(self.x, self.y, self.angle + angle_offset, 
                                   big=self.big_bullets > 0,
                                   laser=self.laser_shot > 0))
        else:
            bullets.append(Bullet(self.x, self.y, self.angle,
                                big=self.big_bullets > 0,
                                laser=self.laser_shot > 0))
        return bullets

# Asteroid class
class Asteroid:
    def __init__(self, x=None, y=None, size=3):
        self.size = size
        self.radius = size * 15
        if x is None or y is None:
            # Spawn at random edge of screen
            if random.random() < 0.5:
                self.x = random.choice([0, WIDTH])
                self.y = random.randint(0, HEIGHT)
            else:
                self.x = random.randint(0, WIDTH)
                self.y = random.choice([0, HEIGHT])
        else:
            self.x = x
            self.y = y
        self.angle = random.uniform(0, 360)
        self.speed = random.uniform(1, 3) * (4 - size) / 2
        self.vertices = []
        for _ in range(8):  # Create irregular polygon
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(0.8, 1.2) * self.radius
            self.vertices.append((math.cos(angle) * dist, math.sin(angle) * dist))

    def draw(self):
        points = []
        for vx, vy in self.vertices:
            points.append((int(self.x + vx), int(self.y + vy)))
        pygame.draw.polygon(screen, WHITE, points, 2)

    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        self.x %= WIDTH
        self.y %= HEIGHT

    def split(self):
        if self.size > 1:
            return [
                Asteroid(self.x, self.y, self.size - 1),
                Asteroid(self.x, self.y, self.size - 1)
            ]
        return []

# Bullet class
class Bullet:
    def __init__(self, x, y, angle, alien=False, cat=False, big=False, laser=False):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 8 if cat else 10
        self.radius = 4 if big else 2
        self.lifetime = 45 if cat else 60
        self.alien = alien
        self.cat = cat
        self.big = big
        self.laser = laser
        
        # For laser shots
        if laser or cat:
            self.laser_length = 20 if laser else 15
            self.laser_width = 3 if laser else 2
            self.laser_color = RED
            self.glow_color = ORANGE if cat else YELLOW
            # Track the tail position for smooth laser movement
            angle_rad = math.radians(self.angle)
            self.tail_x = self.x - math.cos(angle_rad) * self.laser_length
            self.tail_y = self.y - math.sin(angle_rad) * self.laser_length

    def draw(self):
        if self.laser or self.cat:
            # Calculate head and tail positions
            angle_rad = math.radians(self.angle)
            head_x = self.x + math.cos(angle_rad) * (self.laser_length / 2)
            head_y = self.y + math.sin(angle_rad) * (self.laser_length / 2)
            tail_x = self.x - math.cos(angle_rad) * (self.laser_length / 2)
            tail_y = self.y - math.sin(angle_rad) * (self.laser_length / 2)
            
            # Draw outer glow
            pygame.draw.line(screen, self.glow_color, 
                           (tail_x, tail_y), (head_x, head_y), 
                           self.laser_width + 2)
            # Draw inner laser
            pygame.draw.line(screen, self.laser_color, 
                           (tail_x, tail_y), (head_x, head_y), 
                           self.laser_width)
        else:
            color = GREEN if self.alien else WHITE
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)

    def update(self):
        # Calculate new position
        new_x = self.x + math.cos(math.radians(self.angle)) * self.speed
        new_y = self.y + math.sin(math.radians(self.angle)) * self.speed

        # Handle screen wrapping for laser differently
        if self.cat:
            # If the laser goes off screen, start reducing its lifetime faster
            if (new_x < 0 or new_x > WIDTH or new_y < 0 or new_y > HEIGHT):
                self.lifetime -= 2  # Fade out faster when off screen
        else:
            # Normal wrapping for regular bullets
            new_x = new_x % WIDTH
            new_y = new_y % HEIGHT

        self.x = new_x
        self.y = new_y
        self.lifetime -= 1

class EvilCat:
    def __init__(self):
        # Spawn at random edge of screen
        if random.random() < 0.5:
            self.x = random.choice([0, WIDTH])
            self.y = random.randint(0, HEIGHT)
        else:
            self.x = random.randint(0, WIDTH)
            self.y = random.choice([0, HEIGHT])
        self.angle = random.uniform(0, 360)
        self.speed = 2  # Reduced speed for smoother movement
        self.max_speed = 2.5
        self.min_speed = 1.5
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.05  # Gradual acceleration
        self.radius = 25
        self.shoot_delay = random.randint(120, 180)  # Slightly longer delay between shots
        self.shoot_timer = 0
        self.change_direction_timer = random.randint(90, 150)  # Longer time between direction changes
        self.laser_width = 3
        self.laser_length = 20
        self.eye_color = RED
        self.ear_angle = 0
        self.ear_wobble_speed = random.uniform(0.05, 0.1)
        self.target_angle = self.angle

    def draw(self):
        # Draw collision circle for debugging
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.radius, 1)
        
        # Draw cat head (circle)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        
        # Draw triangular ears that wobble
        self.ear_angle += self.ear_wobble_speed
        ear_offset = math.sin(self.ear_angle) * 5
        
        # Left ear
        left_ear_points = [
            (self.x - self.radius//2, self.y - self.radius),
            (self.x - self.radius, self.y - self.radius - 15 + ear_offset),
            (self.x - self.radius*1.2, self.y - self.radius)
        ]
        pygame.draw.polygon(screen, WHITE, left_ear_points, 2)
        
        # Right ear
        right_ear_points = [
            (self.x + self.radius//2, self.y - self.radius),
            (self.x + self.radius, self.y - self.radius - 15 - ear_offset),
            (self.x + self.radius*1.2, self.y - self.radius)
        ]
        pygame.draw.polygon(screen, WHITE, right_ear_points, 2)
        
        # Draw center point for debugging
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 2)
        
        # Draw evil glowing eyes
        pygame.draw.circle(screen, self.eye_color, 
                         (int(self.x - self.radius//3), int(self.y - self.radius//4)), 4)
        pygame.draw.circle(screen, self.eye_color, 
                         (int(self.x + self.radius//3), int(self.y - self.radius//4)), 4)
        
        # Draw whiskers
        whisker_length = self.radius * 0.8
        for angle_offset in [-20, 0, 20]:
            # Left whiskers
            start_x = self.x - self.radius//2
            start_y = self.y + self.radius//4
            end_x = start_x - math.cos(math.radians(angle_offset)) * whisker_length
            end_y = start_y + math.sin(math.radians(angle_offset)) * whisker_length
            pygame.draw.line(screen, WHITE, (start_x, start_y), (end_x, end_y), 1)
            
            # Right whiskers
            start_x = self.x + self.radius//2
            end_x = start_x + math.cos(math.radians(angle_offset)) * whisker_length
            pygame.draw.line(screen, WHITE, (start_x, start_y), (end_x, end_y), 1)

    def update(self, target_x, target_y):
        # Calculate shortest path to player considering screen wrapping
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Adjust for screen wrapping
        if abs(dx) > WIDTH/2:
            dx = -math.copysign(WIDTH - abs(dx), dx)
        if abs(dy) > HEIGHT/2:
            dy = -math.copysign(HEIGHT - abs(dy), dy)
        
        # Update direction timer and calculate new target angle
        self.change_direction_timer -= 1
        if self.change_direction_timer <= 0:
            self.target_angle = math.degrees(math.atan2(dy, dx))
            self.target_angle += random.uniform(-20, 20)  # Slight randomness
            self.change_direction_timer = random.randint(90, 150)

        # Smoothly rotate towards target angle
        angle_diff = (self.target_angle - self.angle) % 360
        if angle_diff > 180:
            angle_diff -= 360
        self.angle += angle_diff * 0.02  # Gradual rotation

        # Calculate new velocities with smooth acceleration
        target_vel_x = math.cos(math.radians(self.angle)) * self.max_speed
        target_vel_y = math.sin(math.radians(self.angle)) * self.max_speed
        
        # Smoothly adjust velocity
        self.velocity_x += (target_vel_x - self.velocity_x) * self.acceleration
        self.velocity_y += (target_vel_y - self.velocity_y) * self.acceleration

        # Update position
        new_x = self.x + self.velocity_x
        new_y = self.y + self.velocity_y

        # Smooth screen wrapping with transition zone
        wrap_margin = self.radius * 2
        
        if new_x < -wrap_margin:
            new_x = WIDTH + self.radius
            # Reset velocity for smooth entry
            self.velocity_x *= 0.5
        elif new_x > WIDTH + wrap_margin:
            new_x = -self.radius
            self.velocity_x *= 0.5
        
        if new_y < -wrap_margin:
            new_y = HEIGHT + self.radius
            self.velocity_y *= 0.5
        elif new_y > HEIGHT + wrap_margin:
            new_y = -self.radius
            self.velocity_y *= 0.5

        self.x = new_x
        self.y = new_y

        # Update shoot timer
        self.shoot_timer -= 1
        return self.try_shoot(target_x, target_y)

    def try_shoot(self, target_x, target_y):
        if self.shoot_timer <= 0:
            # Calculate shortest path to target considering screen wrapping
            dx = target_x - self.x
            dy = target_y - self.y
            
            # Adjust for screen wrapping
            if abs(dx) > WIDTH/2:
                dx = -math.copysign(WIDTH - abs(dx), dx)
            if abs(dy) > HEIGHT/2:
                dy = -math.copysign(HEIGHT - abs(dy), dy)
            
            # Calculate angle and add slight randomness
            angle = math.degrees(math.atan2(dy, dx))
            angle += random.uniform(-5, 5)  # Reduced randomness for more accurate shots
            
            self.shoot_timer = self.shoot_delay
            # Create a laser bullet with current position and calculated angle
            return Bullet(self.x, self.y, angle, cat=True)
        return None

class Alien:
    def __init__(self):
        # Spawn at random edge of screen
        if random.random() < 0.5:
            self.x = random.choice([0, WIDTH])
            self.y = random.randint(0, HEIGHT)
        else:
            self.x = random.randint(0, WIDTH)
            self.y = random.choice([0, HEIGHT])
        self.angle = random.uniform(0, 360)
        self.speed = 2
        self.radius = 20
        self.shoot_delay = random.randint(60, 120)  # Frames between shots
        self.shoot_timer = 0
        self.change_direction_timer = random.randint(60, 180)  # Random direction changes

    def draw(self):
        # Draw alien ship (UFO shape)
        pygame.draw.ellipse(screen, GREEN, (self.x - self.radius, self.y - self.radius//2, 
                                          self.radius * 2, self.radius), 2)
        pygame.draw.rect(screen, GREEN, (self.x - self.radius//2, self.y - self.radius//4, 
                                       self.radius, self.radius//2), 2)

    def update(self, target_x, target_y):
        # Update position
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        self.x %= WIDTH
        self.y %= HEIGHT

        # Change direction periodically
        self.change_direction_timer -= 1
        if self.change_direction_timer <= 0:
            self.angle = random.uniform(0, 360)
            self.change_direction_timer = random.randint(60, 180)

        # Update shoot timer
        self.shoot_timer -= 1
        
        # Calculate angle to player for shooting
        return self.try_shoot(target_x, target_y)

    def try_shoot(self, target_x, target_y):
        if self.shoot_timer <= 0:
            # Calculate angle to player
            dx = target_x - self.x
            dy = target_y - self.y
            angle = math.degrees(math.atan2(dy, dx))
            # Add some randomness to make it less accurate
            angle += random.uniform(-20, 20)
            self.shoot_timer = self.shoot_delay
            return Bullet(self.x, self.y, angle, alien=True)
        return None

def collide(obj1, obj2):
    dist = math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)
    return dist < obj1.radius + obj2.radius

def draw_text(text, size, x, y):
    font = pygame.font.Font(None, size)
    surface = font.render(text, True, WHITE)
    rect = surface.get_rect()
    rect.midtop = (x, y)
    screen.blit(surface, rect)

# Menu class
class Menu:
    def __init__(self):
        self.options = ["Easy", "Medium", "Hard"]
        self.selected = 0

def main():
    global ship, asteroids, bullets, aliens, evil_cats, power_ups, power_up_timer, score, high_score, screen
    
    # Initialize pygame and create window
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Asteroids")
    
    # Initialize game
    menu = Menu()
    clock = pygame.time.Clock()
    running = True
    game_state = MENU
    score = 0
    high_score = 0
    difficulty = EASY
    ship = None
    asteroids = []
    bullets = []
    aliens = []
    evil_cats = []
    power_ups = []
    power_up_timer = 0

    # Start game loop
    while running:
        screen.fill(BLACK)
        
    def draw(self):
        title_size = 64
        option_size = 48
        
        # Draw title
        draw_text("ASTEROIDS", title_size, WIDTH // 2, HEIGHT // 4)
        
        # Draw difficulty options
        for i, option in enumerate(self.options):
            color = GREEN if i == self.selected else WHITE
            y_pos = HEIGHT // 2 + i * 60
            font = pygame.font.Font(None, option_size)
            surface = font.render(option, True, color)
            rect = surface.get_rect()
            rect.midtop = (WIDTH // 2, y_pos)
            screen.blit(surface, rect)
            
        # Draw instructions
        draw_text("Use UP/DOWN arrows to select, SPACE to start", 30, WIDTH // 2, HEIGHT * 3 // 4)

# Game setup
def reset_game(difficulty):
    global ship, asteroids, bullets, aliens, evil_cats, power_ups, score, power_up_timer
    ship = Ship()
    num_asteroids = 3 if difficulty == EASY else 4 if difficulty == MEDIUM else 5
    asteroids = [Asteroid() for _ in range(num_asteroids)]
    bullets = []
    aliens = [] if difficulty != HARD else [Alien()]
    evil_cats = [] if difficulty != MEDIUM else [EvilCat()]
    power_ups = []
    power_up_timer = 0
    score = 0

def spawn_power_up():
    # Spawn power-up away from edges and player
    margin = 100
    while True:
        x = random.randint(margin, WIDTH - margin)
        y = random.randint(margin, HEIGHT - margin)
        # Make sure it's not too close to the player
        if ship and math.hypot(x - ship.x, y - ship.y) > 150:
            break
    
    # Randomly choose power-up type
    power_type = random.choice([MULTI_SHOT, LASER_SHOT, SHIELD, BIG_BULLETS])
    return PowerUp(x, y, power_type)

def reset_game(difficulty):
    global ship, asteroids, bullets, score
    ship = Ship()
    num_asteroids = 3 if difficulty == 0 else 4 if difficulty == 1 else 5
    asteroids = [Asteroid() for _ in range(num_asteroids)]
    bullets = []
    score = 0

def main():
    global ship, asteroids, bullets, score, high_score, screen
    
    # Initialize pygame
    pygame.init()
    pygame.font.init()
    
    # Initialize display
    init_display()
    
    # Initialize game
    menu = Menu()
    clock = pygame.time.Clock()
    running = True
    game_state = MENU

    # Main loop
    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # Return to game selector
                
            if game_state == MENU:
                if event.key == pygame.K_UP:
                    menu.selected = (menu.selected - 1) % len(menu.options)
                elif event.key == pygame.K_DOWN:
                    menu.selected = (menu.selected + 1) % len(menu.options)
                elif event.key == pygame.K_SPACE:
                    game_state = PLAYING
                    difficulty = menu.selected
                    reset_game(difficulty)
            elif game_state == PLAYING:
                if event.key == pygame.K_SPACE:
                    if len(bullets) < (10 if ship.multi_shot > 0 else 5):  # Higher limit for multi-shot
                        new_bullets = ship.shoot()
                        bullets.extend(new_bullets)
            elif game_state == GAME_OVER:
                if event.key == pygame.K_r:
                    game_state = MENU
                elif event.key == pygame.K_SPACE:
                    game_state = PLAYING
                    reset_game(difficulty)

    if game_state == MENU:
        menu.draw()
    elif game_state == PLAYING:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            ship.angle -= 5
        if keys[pygame.K_RIGHT]:
            ship.angle += 5
        if keys[pygame.K_UP]:
            ship.speed = min(ship.speed + 0.25, 7)
        else:
            ship.speed = max(ship.speed - 0.1, 0)

        ship.update()
        ship.draw()

        # Update and draw asteroids
        for asteroid in asteroids[:]:
            asteroid.update()
            asteroid.draw()
            if ship.invulnerable == 0 and collide(ship, asteroid):
                ship.lives -= 1
                if ship.lives <= 0:
                    game_state = GAME_OVER
                    if score > high_score:
                        high_score = score
                else:
                    ship.invulnerable = 120  # 2 seconds of invulnerability
                    ship.x = WIDTH // 2
                    ship.y = HEIGHT // 2
                    ship.speed = 0

        # Update and draw evil cats (Medium difficulty)
        if difficulty == MEDIUM:
            for cat in evil_cats[:]:
                # Try to shoot
                new_bullet = cat.update(ship.x, ship.y)
                if new_bullet:
                    bullets.append(new_bullet)
                
                cat.draw()
                
                # Debug: Just make player invulnerable on collision
                if ship.invulnerable == 0 and collide(ship, cat):
                    ship.invulnerable = 120
                    print(f"Player collision at x:{cat.x:.2f}, y:{cat.y:.2f}")
                    print(f"Player position x:{ship.x:.2f}, y:{ship.y:.2f}")
                    print(f"Distance: {math.hypot(cat.x - ship.x, cat.y - ship.y):.2f}")

            # Only spawn a new cat if there are none
            if len(evil_cats) == 0:
                evil_cats.append(EvilCat())

        # Update and draw aliens (Hard difficulty)
        if difficulty == HARD:
            for alien in aliens[:]:
                # Try to shoot
                new_bullet = alien.update(ship.x, ship.y)
                if new_bullet:
                    bullets.append(new_bullet)
                
                alien.draw()
                
                # Check for collision with player
                if ship.invulnerable == 0 and collide(ship, alien):
                    ship.lives -= 1
                    aliens.remove(alien)
                    if ship.lives <= 0:
                        game_state = GAME_OVER
                        if score > high_score:
                            high_score = score
                    else:
                        ship.invulnerable = 120
                        ship.x = WIDTH // 2
                        ship.y = HEIGHT // 2
                        ship.speed = 0

            # Spawn new aliens periodically in hard mode
            if len(aliens) < 1 + score // 5000:  # More aliens as score increases
                aliens.append(Alien())

        # Update and draw bullets
        for bullet in bullets[:]:
            bullet.update()
            if bullet.lifetime <= 0:
                bullets.remove(bullet)
                continue
            bullet.draw()
            
            # Check bullet collisions with asteroids
            for asteroid in asteroids[:]:
                if collide(bullet, asteroid):
                    score += (4 - asteroid.size) * 100
                    asteroids.remove(asteroid)
                    if bullet in bullets:  # Check if bullet still exists
                        bullets.remove(bullet)
                    asteroids.extend(asteroid.split())
                    break
            
            # Check bullet collisions with aliens and player
            if bullet in bullets:  # Make sure bullet wasn't already removed
                if bullet.alien:  # Alien bullet hitting player
                    if ship.invulnerable == 0 and collide(bullet, ship):
                        ship.lives -= 1
                        bullets.remove(bullet)
                        if ship.lives <= 0:
                            game_state = GAME_OVER
                            if score > high_score:
                                high_score = score
                        else:
                            ship.invulnerable = 120
                            ship.x = WIDTH // 2
                            ship.y = HEIGHT // 2
                            ship.speed = 0
                else:  # Player bullet hitting enemies
                    # Check collision with aliens
                    for alien in aliens[:]:
                        if collide(bullet, alien):
                            score += 500  # Points for destroying alien
                            aliens.remove(alien)
                            bullets.remove(bullet)
                            break
                    
                    # For debugging: Cat just deflects bullets
                    if bullet in bullets:
                        for cat in evil_cats:  # Don't use [:] since we're not removing cats
                            if collide(bullet, cat):
                                # Just remove the bullet, cat stays
                                if bullet in bullets:
                                    bullets.remove(bullet)
                                # Print collision coordinates for debugging
                                print(f"Collision at x:{cat.x:.2f}, y:{cat.y:.2f}")
                                break

        # Respawn asteroids
        min_asteroids = 3 if difficulty == EASY else 4 if difficulty == MEDIUM else 5
        if len(asteroids) == 0:
            for _ in range(min_asteroids):
                asteroids.append(Asteroid())

        # Handle power-ups
        power_up_timer -= 1
        if power_up_timer <= 0 and len(power_ups) < 2:  # Limit to 2 power-ups at a time
            power_ups.append(spawn_power_up())
            power_up_timer = random.randint(300, 600)  # 5-10 seconds between spawns

        # Update and draw power-ups
        for power_up in power_ups[:]:
            power_up.update()
            if not power_up.active:
                power_ups.remove(power_up)
                continue
            
            power_up.draw()
            
            # Check for collection by player
            if collide(ship, power_up):
                ship.apply_power_up(power_up.type)
                power_ups.remove(power_up)
                score += 200  # Bonus points for collecting power-up
            
            # Check for shooting power-up
            for bullet in bullets[:]:
                if bullet in bullets and not (bullet.alien or bullet.cat):
                    if collide(bullet, power_up):
                        ship.apply_power_up(power_up.type)
                        power_ups.remove(power_up)
                        bullets.remove(bullet)
                        score += 200  # Bonus points for collecting power-up
                        break

        # Draw HUD
        draw_text(f"Score: {score}", 30, 100, 10)
        draw_text(f"Lives: {ship.lives}", 30, WIDTH - 100, 10)
        difficulty_text = ["Easy", "Medium", "Hard"][difficulty]
        draw_text(f"Difficulty: {difficulty_text}", 30, WIDTH // 2, 10)
        
        # Draw power-up timers
        y_offset = 40
        if ship.multi_shot > 0:
            draw_text("Multi-Shot!", 20, 100, y_offset)
            y_offset += 25
        if ship.laser_shot > 0:
            draw_text("Laser Shot!", 20, 100, y_offset)
            y_offset += 25
        if ship.shield > 0:
            draw_text("Shield Active!", 20, 100, y_offset)
            y_offset += 25
        if ship.big_bullets > 0:
            draw_text("Big Bullets!", 20, 100, y_offset)
    elif game_state == GAME_OVER:
        # Game Over screen
        draw_text("GAME OVER", 64, WIDTH // 2, HEIGHT // 4)
        draw_text(f"Score: {score}", 48, WIDTH // 2, HEIGHT // 2)
        draw_text(f"High Score: {high_score}", 48, WIDTH // 2, HEIGHT // 2 + 50)
        draw_text("Press SPACE to Play Again", 36, WIDTH // 2, HEIGHT * 3 // 4 - 30)
        draw_text("Press R to Return to Menu", 36, WIDTH // 2, HEIGHT * 3 // 4 + 30)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            ship.angle -= 5
        if keys[pygame.K_RIGHT]:
            ship.angle += 5
        if keys[pygame.K_UP]:
            ship.speed = min(ship.speed + 0.25, 7)
        else:
            ship.speed = max(ship.speed - 0.1, 0)

        ship.update()
        ship.draw()

        # Update and draw asteroids
        for asteroid in asteroids[:]:
            asteroid.update()
            asteroid.draw()
            if ship.invulnerable == 0 and collide(ship, asteroid):
                ship.lives -= 1
                if ship.lives <= 0:
                    game_over = True
                    if score > high_score:
                        high_score = score
                else:
                    ship.invulnerable = 120  # 2 seconds of invulnerability
                    ship.x = WIDTH // 2
                    ship.y = HEIGHT // 2
                    ship.speed = 0

        # Update and draw bullets
        for bullet in bullets[:]:
            bullet.update()
            if bullet.lifetime <= 0:
                bullets.remove(bullet)
                continue
            bullet.draw()
            for asteroid in asteroids[:]:
                if collide(bullet, asteroid):
                    score += (4 - asteroid.size) * 100
                    asteroids.remove(asteroid)
                    if bullet in bullets:  # Check if bullet still exists
                        bullets.remove(bullet)
                    asteroids.extend(asteroid.split())
                    break

        # Respawn asteroids
        if len(asteroids) == 0:
            for _ in range(4):
                asteroids.append(Asteroid())

        # Draw HUD
        draw_text(f"Score: {score}", 30, 100, 10)
        draw_text(f"Lives: {ship.lives}", 30, WIDTH - 100, 10)
    else:
        # Game Over screen
        draw_text("GAME OVER", 64, WIDTH // 2, HEIGHT // 4)
        draw_text(f"Score: {score}", 48, WIDTH // 2, HEIGHT // 2)
        draw_text(f"High Score: {high_score}", 48, WIDTH // 2, HEIGHT // 2 + 50)
        draw_text("Press R to Restart", 36, WIDTH // 2, HEIGHT * 3 // 4)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()