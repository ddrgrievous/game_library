import pygame
import random
import math
from .leaderboard import Leaderboard

# Initialize Pygame
pygame.init()
pygame.font.init()

# Constants
WIDTH = 800
HEIGHT = 600
GRID_SIZE = 40  # Size of each grid cell

# Initialize display (but wait until main() to create window)
screen = None

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)

class Mouse:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = GRID_SIZE - 4
        self.speed = GRID_SIZE
        self.moving = False
        self.move_progress = 0
        self.target_x = x
        self.target_y = y
        self.color = GRAY  # Default color for mouse
    
    def move(self, dx, dy, blocks):
        if self.moving:
            return False

        new_x = self.x + dx * GRID_SIZE
        new_y = self.y + dy * GRID_SIZE

        # Check bounds
        if new_x < 0 or new_x >= WIDTH or new_y < 0 or new_y >= HEIGHT:
            return False

        # Check collision with blocks and try to push them
        for block in blocks:
            if block.x == new_x and block.y == new_y:
                # Try to push the block
                block_new_x = block.x + dx * GRID_SIZE
                block_new_y = block.y + dy * GRID_SIZE
                
                # Check if block can be pushed (bounds and other blocks)
                if (block_new_x < 0 or block_new_x >= WIDTH or 
                    block_new_y < 0 or block_new_y >= HEIGHT):
                    return False
                    
                # Check collision with other blocks
                for other_block in blocks:
                    if other_block != block:
                        if (other_block.x == block_new_x and 
                            other_block.y == block_new_y):
                            return False
                
                # Push the block
                block.x = block_new_x
                block.y = block_new_y
                
        self.target_x = new_x
        self.target_y = new_y
        self.moving = True
        return True

    def update(self):
        if self.moving:
            move_speed = 0.2  # Adjust for smoother movement
            self.move_progress += move_speed
            if self.move_progress >= 1:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
                self.move_progress = 0
            else:
                self.x = self.x + (self.target_x - self.x) * move_speed
                self.y = self.y + (self.target_y - self.y) * move_speed

    def draw(self):
        # Convert float positions to integers for drawing
        draw_x = int(self.x)
        draw_y = int(self.y)
        
        # Draw body
        pygame.draw.circle(screen, self.color, 
                         (draw_x + GRID_SIZE//2, draw_y + GRID_SIZE//2), 
                         self.size//2)
        # Draw ears
        pygame.draw.circle(screen, PINK, 
                         (draw_x + GRID_SIZE//3, draw_y + GRID_SIZE//3), 
                         self.size//4)
        pygame.draw.circle(screen, PINK, 
                         (draw_x + 2*GRID_SIZE//3, draw_y + GRID_SIZE//3), 
                         self.size//4)
        # Draw nose
        pygame.draw.circle(screen, PINK, 
                         (draw_x + GRID_SIZE//2, draw_y + 2*GRID_SIZE//3), 3)
        # Draw tail
        pygame.draw.line(screen, self.color, 
                        (draw_x + GRID_SIZE//2, draw_y + GRID_SIZE - 5),
                        (draw_x + GRID_SIZE//2, draw_y + GRID_SIZE + 10), 3)

class Dog:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = GRID_SIZE - 2  # Slightly bigger than mouse
        self.speed = GRID_SIZE
        self.moving = False
        self.move_progress = 0
        self.target_x = x
        self.target_y = y
        self.color = BROWN
        self.stun_power = True  # Can stun cats

    def move(self, dx, dy, blocks):
        if self.moving:
            return False

        new_x = self.x + dx * GRID_SIZE
        new_y = self.y + dy * GRID_SIZE

        # Check bounds
        if new_x < 0 or new_x >= WIDTH or new_y < 0 or new_y >= HEIGHT:
            return False

        # Check collision with blocks
        for block in blocks:
            if block.x == new_x and block.y == new_y:
                return False

        self.target_x = new_x
        self.target_y = new_y
        self.moving = True
        return True
        
    def update(self):
        if self.moving:
            move_speed = 0.2  # Adjust for smoother movement
            self.move_progress += move_speed
            if self.move_progress >= 1:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
                self.move_progress = 0
            else:
                self.x = self.x + (self.target_x - self.x) * move_speed
                self.y = self.y + (self.target_y - self.y) * move_speed

    def update(self):
        if self.moving:
            move_speed = 0.2
            self.move_progress += move_speed
            if self.move_progress >= 1:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
                self.move_progress = 0
            else:
                self.x = self.x + (self.target_x - self.x) * move_speed
                self.y = self.y + (self.target_y - self.y) * move_speed

    def draw(self):
        # Convert float positions to integers for drawing
        draw_x = int(self.x)
        draw_y = int(self.y)
        
        # Draw body
        pygame.draw.circle(screen, self.color, 
                         (draw_x + GRID_SIZE//2, draw_y + GRID_SIZE//2), 
                         self.size//2)
        # Draw ears (floppy dog ears)
        pygame.draw.ellipse(screen, self.color,
                          (draw_x + GRID_SIZE//4, draw_y + GRID_SIZE//4,
                           GRID_SIZE//4, GRID_SIZE//2))
        pygame.draw.ellipse(screen, self.color,
                          (draw_x + GRID_SIZE//2, draw_y + GRID_SIZE//4,
                           GRID_SIZE//4, GRID_SIZE//2))
        # Draw nose
        pygame.draw.circle(screen, BLACK, 
                         (draw_x + GRID_SIZE//2, draw_y + 2*GRID_SIZE//3), 4)
        # Draw eyes
        pygame.draw.circle(screen, BLACK, 
                         (draw_x + GRID_SIZE//3, draw_y + GRID_SIZE//2), 3)
        pygame.draw.circle(screen, BLACK, 
                         (draw_x + 2*GRID_SIZE//3, draw_y + GRID_SIZE//2), 3)

    def draw(self):
        # Convert float positions to integers for drawing
        draw_x = int(self.x)
        draw_y = int(self.y)
        
        # Draw body
        pygame.draw.circle(screen, self.color, 
                         (draw_x + GRID_SIZE//2, draw_y + GRID_SIZE//2), 
                         self.size//2)
        # Draw ears
        pygame.draw.circle(screen, PINK, 
                         (draw_x + GRID_SIZE//3, draw_y + GRID_SIZE//3), 
                         self.size//4)
        pygame.draw.circle(screen, PINK, 
                         (draw_x + 2*GRID_SIZE//3, draw_y + GRID_SIZE//3), 
                         self.size//4)
        # Draw nose
        pygame.draw.circle(screen, PINK, 
                         (draw_x + GRID_SIZE//2, draw_y + 2*GRID_SIZE//3), 3)
        # Draw tail
        pygame.draw.line(screen, self.color, 
                        (draw_x + GRID_SIZE//2, draw_y + GRID_SIZE - 5),
                        (draw_x + GRID_SIZE//2, draw_y + GRID_SIZE + 10), 3)

    def move(self, dx, dy, blocks):
        if self.moving:
            return False

        new_x = self.x + dx * GRID_SIZE
        new_y = self.y + dy * GRID_SIZE

        # Check bounds
        if new_x < 0 or new_x >= WIDTH or new_y < 0 or new_y >= HEIGHT:
            return False

        # Check collision with blocks and try to push them
        for block in blocks:
            if block.x == new_x and block.y == new_y:
                # Try to push the block
                block_new_x = block.x + dx * GRID_SIZE
                block_new_y = block.y + dy * GRID_SIZE
                
                # Check if block can be pushed (bounds and other blocks)
                if (block_new_x < 0 or block_new_x >= WIDTH or 
                    block_new_y < 0 or block_new_y >= HEIGHT):
                    return False
                    
                # Check collision with other blocks
                for other_block in blocks:
                    if other_block != block:
                        if (other_block.x == block_new_x and 
                            other_block.y == block_new_y):
                            return False
                
                # Push the block
                block.x = block_new_x
                block.y = block_new_y
                
        self.target_x = new_x
        self.target_y = new_y
        self.moving = True
        return True

    def update(self):
        if self.moving:
            move_speed = 0.2  # Adjust for smoother movement
            self.move_progress += move_speed
            if self.move_progress >= 1:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
                self.move_progress = 0
            else:
                self.x = self.x + (self.target_x - self.x) * move_speed
                self.y = self.y + (self.target_y - self.y) * move_speed

class Cat:
    DIFFICULTY_SETTINGS = {
        'easy': {'speed': 0.05, 'delay': 30, 'stun_time': 180},  # 3 seconds at 60 FPS
        'medium': {'speed': 0.15, 'delay': 15, 'stun_time': 120},  # 2 seconds
        'hard': {'speed': 0.2, 'delay': 10, 'stun_time': 60}  # 1 second
    }
    
    def __init__(self, x, y, target_player, difficulty='medium'):
        self.x = x
        self.y = y
        self.size = GRID_SIZE - 4
        self.speed = GRID_SIZE
        self.moving = False
        self.move_progress = 0
        self.target_x = x
        self.target_y = y
        self.difficulty = difficulty
        settings = self.DIFFICULTY_SETTINGS[difficulty]
        self.move_speed = settings['speed']
        self.move_delay = settings['delay']
        self.stun_time = settings['stun_time']
        self.move_timer = 0
        self.stunned_timer = 0
        self.target_player = target_player  # Which player this cat chases (0 or 1)
        self.path = []  # Store the planned path
        self.color = ORANGE
        self.is_stunned = False

    def draw(self):
        # Convert float positions to integers for drawing
        draw_x = int(self.x)
        draw_y = int(self.y)
        
        # Draw body
        pygame.draw.circle(screen, self.color, 
                         (draw_x + GRID_SIZE//2, draw_y + GRID_SIZE//2), 
                         self.size//2)
        # Draw ears (triangles)
        pygame.draw.polygon(screen, self.color, [
            (draw_x + GRID_SIZE//4, draw_y + GRID_SIZE//3),
            (draw_x + GRID_SIZE//2, draw_y),
            (draw_x + 3*GRID_SIZE//4, draw_y + GRID_SIZE//3)
        ])
        # Draw eyes
        pygame.draw.circle(screen, BLACK, 
                         (draw_x + GRID_SIZE//3, draw_y + GRID_SIZE//2), 4)
        pygame.draw.circle(screen, BLACK, 
                         (draw_x + 2*GRID_SIZE//3, draw_y + GRID_SIZE//2), 4)
        
        # Change color based on target player
        self.color = (255, 165, 0) if self.target_player == 0 else (255, 100, 0)  # Different orange for each target

    def find_path(self, mice, blocks):
        # Get the target mouse based on this cat's assignment
        mouse = mice[self.target_player if self.target_player < len(mice) else 0]
        
        # Convert positions to grid coordinates
        start = (self.x // GRID_SIZE, self.y // GRID_SIZE)
        goal = (mouse.x // GRID_SIZE, mouse.y // GRID_SIZE)
        
        # If we're already adjacent to the mouse, don't need to pathfind
        if (abs(self.x - mouse.x) <= GRID_SIZE and abs(self.y - mouse.y) <= GRID_SIZE):
            dx = 1 if mouse.x > self.x else -1 if mouse.x < self.x else 0
            dy = 1 if mouse.y > self.y else -1 if mouse.y < self.y else 0
            if self.try_move(dx * GRID_SIZE, dy * GRID_SIZE, blocks):
                return True
            return False
        
        # Create a set of blocked positions
        blocked = {(block.x // GRID_SIZE, block.y // GRID_SIZE) for block in blocks}
        
        # BFS queue and visited set
        queue = [(start, [])]
        visited = {start}
        
        # Directions to check (up, right, down, left)
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        while queue:
            (x, y), path = queue.pop(0)
            
            # Check all four directions
            random.shuffle(directions)  # Add some randomness to movement
            for dx, dy in directions:
                next_x, next_y = x + dx, y + dy
                next_pos = (next_x, next_y)
                
                # Check if this position is valid
                if (next_x < 0 or next_x >= WIDTH // GRID_SIZE or 
                    next_y < 0 or next_y >= HEIGHT // GRID_SIZE or 
                    next_pos in blocked or next_pos in visited):
                    continue
                
                new_path = path + [(dx, dy)]
                
                # If we've found the goal
                if next_pos == goal:
                    if new_path:
                        # Try to move in the direction of the first step
                        dx, dy = new_path[0]
                        if self.try_move(dx * GRID_SIZE, dy * GRID_SIZE, blocks):
                            self.path = new_path[1:]  # Save the rest of the path
                            return True
                    return False
                
                # Add the new position to the queue and mark as visited
                queue.append((next_pos, new_path))
                visited.add(next_pos)
        
        # If no path found, try to move in any valid direction
        random.shuffle(directions)
        for dx, dy in directions:
            if self.try_move(dx * GRID_SIZE, dy * GRID_SIZE, blocks):
                return True
        
        return False

    def try_move(self, dx, dy, blocks):
        if self.moving:
            return False

        new_x = self.x + dx
        new_y = self.y + dy

        # Check bounds
        if new_x < 0 or new_x >= WIDTH or new_y < 0 or new_y >= HEIGHT:
            return False

        # Check collision with blocks
        for block in blocks:
            if block.x == new_x and block.y == new_y:
                return False

        self.target_x = new_x
        self.target_y = new_y
        self.moving = True
        return True

    def update(self, players, blocks):
        # Update stun timer if stunned
        if self.is_stunned:
            self.stunned_timer -= 1
            if self.stunned_timer <= 0:
                self.is_stunned = False
                self.color = ORANGE
            else:
                self.color = (150, 150, 150)  # Grayed out when stunned
            return
        
        if self.moving:
            self.move_progress += self.move_speed
            if self.move_progress >= 1:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
                self.move_progress = 0
            else:
                self.x = self.x + (self.target_x - self.x) * self.move_speed
                self.y = self.y + (self.target_y - self.y) * self.move_speed
        elif self.move_timer <= 0:
            # Only chase the mouse (first player)
            if self.find_path([players[0]], blocks):
                self.move_timer = self.move_delay
        else:
            self.move_timer -= 1
            
    def get_stunned(self):
        if not self.is_stunned:
            self.is_stunned = True
            self.stunned_timer = self.stun_time
            self.moving = False  # Stop current movement

class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = GRID_SIZE
        self.selected = False

    def draw(self):
        color = YELLOW if self.selected else BROWN
        pygame.draw.rect(screen, color, 
                        (self.x, self.y, self.size, self.size))
        pygame.draw.rect(screen, BLACK, 
                        (self.x, self.y, self.size, self.size), 2)

class Cheese:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = GRID_SIZE - 10

    def draw(self):
        # Draw cheese wedge
        pygame.draw.polygon(screen, YELLOW, [
            (self.x + 5, self.y + GRID_SIZE - 5),
            (self.x + GRID_SIZE - 5, self.y + GRID_SIZE - 5),
            (self.x + GRID_SIZE//2, self.y + 5)
        ])
        # Draw holes
        pygame.draw.circle(screen, BROWN, 
                         (self.x + GRID_SIZE//3, self.y + 2*GRID_SIZE//3), 3)
        pygame.draw.circle(screen, BROWN, 
                         (self.x + 2*GRID_SIZE//3, self.y + GRID_SIZE//2), 3)

def create_level(level_num, mice, difficulty='medium'):
    blocks = []
    cats = []
    
    # Number of blocks and cats increases with level
    num_blocks = 10 + level_num * 5
    num_cats = level_num
    
    # Create random blocks
    available_positions = [(x, y) for x in range(0, WIDTH, GRID_SIZE) 
                         for y in range(0, HEIGHT, GRID_SIZE)]
    
    # Reserve positions for mice
    for mouse in mice:
        mouse_pos = (mouse.x, mouse.y)
        if mouse_pos in available_positions:
            available_positions.remove(mouse_pos)
    
    # Choose random position for cheese
    cheese_pos = random.choice(available_positions)
    available_positions.remove(cheese_pos)
    
    # Place blocks randomly
    for _ in range(num_blocks):
        if available_positions:
            pos = random.choice(available_positions)
            blocks.append(Block(pos[0], pos[1]))
            available_positions.remove(pos)
    
    # Place cats randomly and assign targets, ensuring minimum distance from mice
    min_distance = 6 * GRID_SIZE  # Minimum distance in pixels between cats and mice
    
    for i in range(num_cats):
        if available_positions:
            # Filter positions that are too close to any mouse
            safe_positions = [pos for pos in available_positions if all(
                math.sqrt((pos[0] - mouse.x)**2 + (pos[1] - mouse.y)**2) >= min_distance 
                for mouse in mice
            )]
            
            # If no safe positions found, increase distance gradually
            while not safe_positions and min_distance > GRID_SIZE:
                min_distance -= GRID_SIZE
                safe_positions = [pos for pos in available_positions if all(
                    math.sqrt((pos[0] - mouse.x)**2 + (pos[1] - mouse.y)**2) >= min_distance 
                    for mouse in mice
                )]
            
            # If still no safe positions, use any available position
            if not safe_positions:
                safe_positions = available_positions
            
            # Choose a position and create the cat
            pos = random.choice(safe_positions)
            # Alternate cats between targeting player 1 and 2 in multiplayer
            if len(mice) > 1:
                target_player = i % 2  # Evenly distribute cats between players
            else:
                target_player = 0  # All cats chase player 1 in single player
            cats.append(Cat(pos[0], pos[1], target_player, difficulty))
            available_positions.remove(pos)
    
    return (cats,  # List of cats
            Cheese(cheese_pos[0], cheese_pos[1]),  # Cheese position
            blocks)
    # Add more levels here

def show_leaderboard(difficulty):
    font = pygame.font.Font(None, 24)  # Smaller font size
    leaderboard = LEADERBOARD.get_leaderboard(difficulty)
    
    # Position in top right corner with padding
    x_pos = WIDTH - 10  # 10 pixels from right edge
    y_pos = 10  # 10 pixels from top
    
    # Draw title
    title = font.render(f'{difficulty.capitalize()} Leaderboard', True, WHITE)
    title_rect = title.get_rect(topright=(x_pos, y_pos))
    screen.blit(title, title_rect)
    
    if not leaderboard:
        text = font.render('No scores yet!', True, WHITE)
        text_rect = text.get_rect(topright=(x_pos, y_pos + 25))
        screen.blit(text, text_rect)
    else:
        for i, score in enumerate(leaderboard):
            text = font.render(f'{i+1}. {score["name"]}: Level {score["level"]}', True, WHITE)
            text_rect = text.get_rect(topright=(x_pos, y_pos + (i+1)*25))
            screen.blit(text, text_rect)

def get_player_name():
    name = ""
    entering_name = True
    font = pygame.font.Font(None, 48)
    
    while entering_name:
        screen.fill(BLACK)
        
        # Draw prompt
        title = font.render('New High Score!', True, WHITE)
        title_rect = title.get_rect(center=(WIDTH/2, HEIGHT/3))
        screen.blit(title, title_rect)
        
        # Draw current name
        name_text = font.render(f'Enter Name: {name}', True, WHITE)
        name_rect = name_text.get_rect(center=(WIDTH/2, HEIGHT/2))
        screen.blit(name_text, name_rect)
        
        # Draw instructions
        inst_font = pygame.font.Font(None, 36)
        inst = inst_font.render('Press Enter when done', True, WHITE)
        inst_rect = inst.get_rect(center=(WIDTH/2, HEIGHT*2/3))
        screen.blit(inst, inst_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key != pygame.K_RETURN and len(name) < 10:
                    if event.unicode.isalnum():
                        name += event.unicode
    
    return None

def show_menu():
    menu_running = True
    num_players = 1
    difficulty = 'medium'  # Default difficulty
    
    difficulties = ['easy', 'medium', 'hard']
    difficulty_idx = 1  # Start with medium
    
    while menu_running:
        screen.fill(BLACK)
        
        # Draw title
        font = pygame.font.Font(None, 74)
        title = font.render('Cat and Mouse', True, WHITE)
        title_rect = title.get_rect(center=(WIDTH/2, HEIGHT/4))
        screen.blit(title, title_rect)
        
        # Draw player selection
        font = pygame.font.Font(None, 48)
        players_text = font.render(f'Players: {num_players}', True, WHITE)
        players_rect = players_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
        screen.blit(players_text, players_rect)
        
        # Draw difficulty selection
        diff_text = font.render(f'Difficulty: {difficulty.capitalize()}', True, WHITE)
        diff_rect = diff_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))
        screen.blit(diff_text, diff_rect)
        
        # Show leaderboard for current difficulty
        show_leaderboard(difficulty)
        
        # Draw instructions
        font = pygame.font.Font(None, 36)
        instructions = [
            'Space - Change number of players',
            'D - Change difficulty',
            'Enter - Start Game',
            'ESC - Quit'
        ]
        for i, text in enumerate(instructions):
            inst = font.render(text, True, WHITE)
            inst_rect = inst.get_rect(center=(WIDTH/2, HEIGHT*4/5 + i*30))
            screen.blit(inst, inst_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    num_players = 2 if num_players == 1 else 1
                elif event.key == pygame.K_d:
                    difficulty_idx = (difficulty_idx + 1) % len(difficulties)
                    difficulty = difficulties[difficulty_idx]
                elif event.key == pygame.K_RETURN:
                    return num_players, difficulty
                elif event.key == pygame.K_ESCAPE:
                    return None, None
    
    return None, None

def game_loop(num_players, difficulty, clock):
    level = 1
    high_score_handled = False  # Add flag to track if high score has been handled
    # Initialize players
    mouse = Mouse(GRID_SIZE, GRID_SIZE)
    dog = Dog(WIDTH - 2*GRID_SIZE, GRID_SIZE) if num_players == 2 else None
    
    # Create lists for both players and mice
    players = [mouse]  # All players (mouse and dog)
    mice = [mouse]     # Just the mouse players
    
    if dog:
        players.append(dog)
    
    # Set colors for mouse
    mouse.color = GRAY
    
    cats, cheese, blocks = create_level(level, mice, difficulty)
    selected_block = None
    game_over = False
    won = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Return to main menu
                
                elif event.key == pygame.K_r:
                    # Reset level
                    return game_loop(num_players, difficulty, clock)
            
            if not game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if clicking a block
                    for block in blocks:
                        if (block.x <= mouse_pos[0] <= block.x + GRID_SIZE and
                            block.y <= mouse_pos[1] <= block.y + GRID_SIZE):
                            selected_block = block
                            block.selected = True
                            break
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if selected_block:
                        mouse_pos = pygame.mouse.get_pos()
                        # Snap to grid
                        new_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
                        new_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
                        
                        # Check if new position is valid
                        valid_move = True
                        if (new_x < 0 or new_x >= WIDTH or 
                            new_y < 0 or new_y >= HEIGHT):
                            valid_move = False
                        
                        # Check collision with other blocks
                        for block in blocks:
                            if block != selected_block:
                                if block.x == new_x and block.y == new_y:
                                    valid_move = False
                                    break
                        
                        if valid_move:
                            selected_block.x = new_x
                            selected_block.y = new_y
                        
                        selected_block.selected = False
                        selected_block = None
        
        if not game_over:
            # Handle continuous key presses for movement
            keys = pygame.key.get_pressed()
            
            # Player 1 controls (Arrow keys) - Mouse
            if not players[0].moving:
                if keys[pygame.K_LEFT]:
                    players[0].move(-1, 0, blocks)
                elif keys[pygame.K_RIGHT]:
                    players[0].move(1, 0, blocks)
                elif keys[pygame.K_UP]:
                    players[0].move(0, -1, blocks)
                elif keys[pygame.K_DOWN]:
                    players[0].move(0, 1, blocks)
            
            # Player 2 controls (WASD) - Dog
            if len(players) > 1 and not players[1].moving:
                if keys[pygame.K_a]:
                    players[1].move(-1, 0, blocks)
                elif keys[pygame.K_d]:
                    players[1].move(1, 0, blocks)
                elif keys[pygame.K_w]:
                    players[1].move(0, -1, blocks)
                elif keys[pygame.K_s]:
                    players[1].move(0, 1, blocks)
            
            # Update game objects
            for player in players:
                player.update()
            
            # Each cat follows its assigned target
            for cat in cats:
                cat.update(mice, blocks)
            
            # Handle cat collisions
            mouse = players[0]  # First player is always the mouse
            
            # Check for cat collisions with mouse (game over)
            for cat in cats:
                if not cat.is_stunned and (abs(mouse.x - cat.x) < GRID_SIZE and 
                    abs(mouse.y - cat.y) < GRID_SIZE):
                    game_over = True
                    break
            
            # Check for dog stunning cats
            if len(players) > 1:
                dog = players[1]
                for cat in cats:
                    if (abs(dog.x - cat.x) < GRID_SIZE and 
                        abs(dog.y - cat.y) < GRID_SIZE):
                        cat.get_stunned()
            
            # Check for win (only mouse can get cheese)
            if (abs(mouse.x - cheese.x) < GRID_SIZE and 
                abs(mouse.y - cheese.y) < GRID_SIZE):
                # Advance to next level
                level += 1
                high_score_handled = False  # Reset high score flag for new level
                # Keep player positions but create new level layout
                cats, cheese, blocks = create_level(level, players, difficulty)
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw grid
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y), 1)
        
        # Draw game objects first
        cheese.draw()
        for block in blocks:
            block.draw()
        for player in players:
            player.draw()
        for cat in cats:
            cat.draw()
            
        # Draw UI elements on top
        font = pygame.font.Font(None, 36)
        level_text = font.render(f'Level: {level} - {difficulty.capitalize()}', True, WHITE)
        text_rect = level_text.get_rect(topleft=(10, 10))
        # Draw a semi-transparent background for better visibility
        pygame.draw.rect(screen, (0, 0, 0, 128), text_rect.inflate(20, 10))
        screen.blit(level_text, (10, 10))
        
        if game_over:
            # Draw game over message and handle high scores
            font = pygame.font.Font(None, 74)
            text = font.render('GAME OVER', True, WHITE)
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/3))
            screen.blit(text, text_rect)
            
            font = pygame.font.Font(None, 48)
            level_text = font.render(f'You reached Level {level}', True, WHITE)
            level_rect = level_text.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(level_text, level_rect)
            
            # Check for high score
            if LEADERBOARD.is_high_score(difficulty, level):
                name = get_player_name()
                if name:
                    LEADERBOARD.add_score(difficulty, name, level)
            
            # Show leaderboard
            show_leaderboard(difficulty)
            
            font = pygame.font.Font(None, 36)
            text = font.render('Press R to Restart or ESC for Menu', True, WHITE)
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT*4/5))
            screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)

def main():
    # Initialize the game window
    global screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cat and Mouse")
    
    clock = pygame.time.Clock()
    global LEADERBOARD
    LEADERBOARD = Leaderboard()
    
    while True:
        # Show menu and get number of players and difficulty
        num_players, difficulty = show_menu()
        if num_players is None:
            return
            
        # Start the game loop
        game_loop(num_players, difficulty, clock)
    
    cats, cheese, blocks = create_level(level, mice)
    selected_block = None
    game_over = False
    won = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if not game_over:
                if event.type == pygame.KEYDOWN:
                    # Player 1 controls (Arrow keys)
                    if not mice[0].moving:
                        if event.key == pygame.K_LEFT:
                            mice[0].move(-1, 0, blocks)
                        elif event.key == pygame.K_RIGHT:
                            mice[0].move(1, 0, blocks)
                        elif event.key == pygame.K_UP:
                            mice[0].move(0, -1, blocks)
                        elif event.key == pygame.K_DOWN:
                            mice[0].move(0, 1, blocks)
                    
                    # Player 2 controls (WASD)
                    if len(mice) > 1 and not mice[1].moving:
                        if event.key == pygame.K_a:
                            mice[1].move(-1, 0, blocks)
                        elif event.key == pygame.K_d:
                            mice[1].move(1, 0, blocks)
                        elif event.key == pygame.K_w:
                            mice[1].move(0, -1, blocks)
                        elif event.key == pygame.K_s:
                            mice[1].move(0, 1, blocks)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if clicking a block
                    for block in blocks:
                        if (block.x <= mouse_pos[0] <= block.x + GRID_SIZE and
                            block.y <= mouse_pos[1] <= block.y + GRID_SIZE):
                            selected_block = block
                            block.selected = True
                            break
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if selected_block:
                        mouse_pos = pygame.mouse.get_pos()
                        # Snap to grid
                        new_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
                        new_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
                        
                        # Check if new position is valid
                        valid_move = True
                        if (new_x < 0 or new_x >= WIDTH or 
                            new_y < 0 or new_y >= HEIGHT):
                            valid_move = False
                        
                        # Check collision with other blocks
                        for block in blocks:
                            if block != selected_block:
                                if block.x == new_x and block.y == new_y:
                                    valid_move = False
                                    break
                        
                        if valid_move:
                            selected_block.x = new_x
                            selected_block.y = new_y
                        
                        selected_block.selected = False
                        selected_block = None
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Reset level
                level = 1
                # Reset mice to starting positions
                mice = []
                if num_players == 1:
                    mice.append(Mouse(GRID_SIZE, GRID_SIZE))
                else:
                    mice.append(Mouse(GRID_SIZE, GRID_SIZE))
                    mice.append(Mouse(WIDTH - 2*GRID_SIZE, GRID_SIZE))
                
                # Reset mice colors
                for i, mouse in enumerate(mice):
                    mouse.color = GRAY if i == 0 else (200, 200, 255)
                
                cats, cheese, blocks = create_level(level, mice)
                game_over = False
                won = False

        if not game_over:
            # Update game objects
            for mouse in mice:
                mouse.update()
            
            # Each cat follows its assigned target
            for cat in cats:
                cat.update(mice, blocks)
            
            # Check for collisions with any cat
            for mouse in mice:
                for cat in cats:
                    if (abs(mouse.x - cat.x) < GRID_SIZE and 
                        abs(mouse.y - cat.y) < GRID_SIZE):
                        game_over = True
                        break
                if game_over:
                    break
            
            # Check for win (any mouse reaching cheese)
            for mouse in mice:
                if (abs(mouse.x - cheese.x) < GRID_SIZE and 
                    abs(mouse.y - cheese.y) < GRID_SIZE):
                    # Advance to next level
                    level += 1
                    # Keep mice positions but create new level layout
                    cats, cheese, blocks = create_level(level, mice)
                    break

        # Draw everything
        screen.fill(BLACK)
        
        # Draw grid
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y), 1)
        
            # Draw game objects
            cheese.draw()
            for block in blocks:
                block.draw()
            for mouse in mice:
                mouse.draw()
            for cat in cats:
                cat.draw()        # Draw level indicator
        font = pygame.font.Font(None, 36)
        level_text = font.render(f'Level: {level}', True, WHITE)
        screen.blit(level_text, (10, 10))
        
        # Draw game over/win message
        if game_over:
            # Draw game over message and handle high scores
            font = pygame.font.Font(None, 74)
            text = font.render('GAME OVER', True, WHITE)
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/3))
            screen.blit(text, text_rect)
            
            font = pygame.font.Font(None, 48)
            level_text = font.render(f'You reached Level {level}', True, WHITE)
            level_rect = level_text.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(level_text, level_rect)
            
            # Check for high score
            if LEADERBOARD.is_high_score(difficulty, level):
                name = get_player_name()
                if name:
                    LEADERBOARD.add_score(difficulty, name, level)
            
            # Show leaderboard
            show_leaderboard(difficulty)
            
            font = pygame.font.Font(None, 36)
            text = font.render('Press R to Restart or ESC for Menu', True, WHITE)
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT*4/5))
            screen.blit(text, text_rect)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()