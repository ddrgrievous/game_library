import pygame
import random
import time
import math

# Constants
WINDOW_SIZE = (800, 600)
CELL_SIZE = 40
GRID_WIDTH = WINDOW_SIZE[0] // CELL_SIZE
GRID_HEIGHT = WINDOW_SIZE[1] // CELL_SIZE

# Colors
WHITE = (255, 255, 255)  # Background
WALL_COLOR = (100, 100, 100)  # Gray walls
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Initialize screen variable
screen = None

def init_display():
    global screen
    if screen is None:
        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Maze Runner")

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = CELL_SIZE - 10
        self.color = BLUE
        self.speed = 5
        self.moving = False
        self.target_x = x
        self.target_y = y
        
    def draw(self):
        # Draw body (rectangle)
        body_rect = pygame.Rect(
            self.x + 5, 
            self.y + 5, 
            self.size - 10, 
            self.size
        )
        pygame.draw.rect(screen, self.color, body_rect)
        
        # Draw head (circle)
        head_radius = (self.size - 10) // 2
        head_x = self.x + self.size // 2
        head_y = self.y + 10 + head_radius
        pygame.draw.circle(screen, self.color, (head_x, head_y), head_radius)
        
        # Draw legs (when moving, alternate their position)
        leg_time = time.time() * 10 if self.moving else 0
        leg_offset = abs(math.sin(leg_time)) * 5
        
        # Left leg
        pygame.draw.line(screen, self.color,
                        (self.x + 10, self.y + self.size),
                        (self.x + 10 - leg_offset, self.y + self.size + 10), 3)
        # Right leg
        pygame.draw.line(screen, self.color,
                        (self.x + self.size - 10, self.y + self.size),
                        (self.x + self.size - 10 + leg_offset, self.y + self.size + 10), 3)
        
    def move(self, dx, dy, maze):
        target_x = self.x + dx * self.speed
        target_y = self.y + dy * self.speed
        
        # Check boundaries
        if target_x < 0 or target_x > WINDOW_SIZE[0] - self.size:
            return False
        if target_y < 0 or target_y > WINDOW_SIZE[1] - self.size:
            return False
        
        # Check collision with maze walls
        cell_x = target_x // CELL_SIZE
        cell_y = target_y // CELL_SIZE
        
        # Check surrounding cells for walls
        for check_x in [cell_x, cell_x + 1]:
            for check_y in [cell_y, cell_y + 1]:
                if (check_x < GRID_WIDTH and check_y < GRID_HEIGHT and
                    maze.grid[check_y][check_x] == 1):
                    player_rect = pygame.Rect(target_x, target_y, self.size, self.size)
                    wall_rect = pygame.Rect(check_x * CELL_SIZE, check_y * CELL_SIZE,
                                         CELL_SIZE, CELL_SIZE)
                    if player_rect.colliderect(wall_rect):
                        return False
        
        self.x = target_x
        self.y = target_y
        self.moving = dx != 0 or dy != 0
        return True

class Maze:
    def __init__(self, level, player):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.level = level
        self.player = player  # Store reference to player
        self.change_timer = 0
        self.change_interval = max(60 - (level * 5), 20)  # Faster changes with higher levels
        self.wall_density = min(0.2 + (level * 0.05), 0.4)  # More walls with higher levels
        self.generate_maze()
        
    def find_path(self, start, end):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        def get_neighbors(pos):
            x, y = pos
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and 
                    self.grid[new_y][new_x] == 0):
                    neighbors.append((new_x, new_y))
            return neighbors
        
        # A* pathfinding
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = min(frontier, key=lambda x: x[0])[1]
            frontier = [(f, pos) for f, pos in frontier if pos != current]
            
            if current == end:
                # Path found
                return True
                
            for next_pos in get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(end, next_pos)
                    frontier.append((priority, next_pos))
                    came_from[next_pos] = current
        
        # No path found
        return False
        
    def generate_maze(self):
        # Clear the grid
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Always keep the start (top-left) and end (bottom-right) clear
        start_area = [(0, 0), (0, 1), (1, 0)]
        end_area = [(GRID_WIDTH-1, GRID_HEIGHT-1), 
                   (GRID_WIDTH-2, GRID_HEIGHT-1),
                   (GRID_WIDTH-1, GRID_HEIGHT-2)]
        
        # Generate random walls
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if (x, y) not in start_area and (x, y) not in end_area:
                    if random.random() < self.wall_density:
                        self.grid[y][x] = 1
                        
        # Ensure path exists
        if not self.find_path((0, 0), (GRID_WIDTH-1, GRID_HEIGHT-1)):
            self.ensure_path_exists()
    
    def ensure_path_exists(self):
        # Create a guaranteed path by clearing a route
        x, y = 0, 0
        end_x, end_y = GRID_WIDTH-1, GRID_HEIGHT-1
        
        while x != end_x or y != end_y:
            self.grid[y][x] = 0  # Clear current cell
            
            # Move closer to the end
            if x < end_x and random.random() < 0.7:
                x += 1
            elif y < end_y:
                y += 1
            else:
                x += 1
                
            # Clear adjacent cells to make the path wider
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT):
                    self.grid[new_y][new_x] = 0
    
    def update(self):
        self.change_timer += 1
        if self.change_timer >= self.change_interval:
            self.change_timer = 0
            self.change_walls()
    
    def change_walls(self):
        # Don't modify start and end areas
        start_area = [(0, 0), (0, 1), (1, 0)]
        end_area = [(GRID_WIDTH-1, GRID_HEIGHT-1), 
                   (GRID_WIDTH-2, GRID_HEIGHT-1),
                   (GRID_WIDTH-1, GRID_HEIGHT-2)]
        
        # Get player position in grid coordinates
        player_x = self.player.x // CELL_SIZE
        player_y = self.player.y // CELL_SIZE
        player_area = [
            (player_x, player_y),
            (player_x + 1, player_y),
            (player_x, player_y + 1),
            (player_x + 1, player_y + 1)
        ]
        
        # Randomly toggle some walls
        num_changes = self.level + 2
        attempts = 0
        changes_made = 0
        
        while changes_made < num_changes and attempts < num_changes * 3:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            # Don't change walls in start area, end area, or where player is
            if ((x, y) not in start_area and 
                (x, y) not in end_area and 
                (x, y) not in player_area):
                # Store original value
                original_value = self.grid[y][x]
                # Try to toggle the wall
                self.grid[y][x] = 1 - self.grid[y][x]
                
                # Check if there's still a valid path from player to end
                player_pos = (player_x, player_y)
                end_pos = (GRID_WIDTH-1, GRID_HEIGHT-1)
                
                if self.find_path(player_pos, end_pos):
                    changes_made += 1
                else:
                    # If no valid path, revert the change
                    self.grid[y][x] = original_value
                    
            attempts += 1
    
    def draw(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] == 1:
                    # Draw wall blocks with a darker color
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE,
                                     CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, WALL_COLOR, rect)
                    # Add a border to make walls more visible
                    pygame.draw.rect(screen, BLACK, rect, 1)
        
        # Draw start and end markers
        start_rect = pygame.Rect(0, 0, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, GREEN, start_rect, 3)
        
        end_rect = pygame.Rect((GRID_WIDTH-1) * CELL_SIZE, (GRID_HEIGHT-1) * CELL_SIZE,
                             CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, end_rect, 3)

class Game:
    def __init__(self):
        self.player = Player(10, 10)
        self.level = 1
        self.maze = Maze(self.level, self.player)
        self.timer = 60  # Starting time in seconds
        self.clock = pygame.time.Clock()
        self.game_state = "PLAYING"  # "PLAYING", "WON", "LOST"
    
    def update(self):
        if self.game_state != "PLAYING":
            return
            
        # Update timer
        self.timer -= 1/60  # Subtract one second every 60 frames
        if self.timer <= 0:
            self.game_state = "LOST"
            return
        
        # Handle continuous key presses for movement
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, self.maze)
        else:
            self.player.moving = False
        
        # Update maze
        self.maze.update()
        
        # Check for win condition
        player_cell_x = self.player.x // CELL_SIZE
        player_cell_y = self.player.y // CELL_SIZE
        if (player_cell_x == GRID_WIDTH - 1 and 
            player_cell_y == GRID_HEIGHT - 1):
            self.level += 1
            self.player.x = 10
            self.player.y = 10
            self.maze = Maze(self.level, self.player)
            self.timer = max(60 - (self.level * 5), 30)  # Less time for higher levels
    
    def draw(self):
        # Clear the screen with a light background
        screen.fill(WHITE)
        
        # Draw grid lines for better visibility
        for x in range(0, WINDOW_SIZE[0], CELL_SIZE):
            pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, WINDOW_SIZE[1]))
        for y in range(0, WINDOW_SIZE[1], CELL_SIZE):
            pygame.draw.line(screen, (200, 200, 200), (0, y), (WINDOW_SIZE[0], y))
        
        # Draw maze
        self.maze.draw()
        
        # Draw player
        self.player.draw()
        
        # Draw HUD
        font = pygame.font.Font(None, 36)
        
        # Draw level
        level_text = font.render(f"Level: {self.level}", True, BLACK)
        screen.blit(level_text, (10, 10))
        
        # Draw timer
        timer_text = font.render(f"Time: {int(self.timer)}", True, RED if self.timer < 10 else BLACK)
        screen.blit(timer_text, (WINDOW_SIZE[0] - 150, 10))
        
        if self.game_state == "LOST":
            self.draw_game_over()
    
    def draw_game_over(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface(WINDOW_SIZE)
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Draw game over text
        font = pygame.font.Font(None, 74)
        text = font.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2))
        screen.blit(text, text_rect)
        
        # Draw restart instruction
        font = pygame.font.Font(None, 36)
        restart_text = font.render("Press R to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2 + 50))
        screen.blit(restart_text, restart_rect)

def main():
    # Initialize pygame at start
    pygame.init()
    pygame.font.init()
    
    # Initialize display
    init_display()
    
    game = Game()
    running = True
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.game_state == "LOST":
                    game = Game()  # Reset the game
                elif event.key == pygame.K_ESCAPE:
                    running = False  # Return to game selector
        
        # Game logic
        game.update()
        
        # Drawing
        game.draw()
        pygame.display.flip()
        
        # Cap the frame rate
        game.clock.tick(60)
    
    # Don't quit pygame when returning to selector
    # pygame.quit()

if __name__ == "__main__":
    main()
