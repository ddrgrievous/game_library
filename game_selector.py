import pygame
import os
import sys

# Initialize Pygame
pygame.init()
pygame.font.init()  # Initialize the font module specifically

# Constants
WINDOW_SIZE = (800, 600)
BUTTON_SIZE = (300, 60)
BUTTON_SPACING = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
HIGHLIGHT = (100, 100, 255)

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        
    def draw(self, surface):
        color = HIGHLIGHT if self.is_hovered else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        return self.is_hovered and event.type == pygame.MOUSEBUTTONDOWN

class GameSelector:
    def __init__(self):
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Game Selector")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Add games here with their corresponding module paths and launch functions
        self.games = [
            {"name": "Cat and Mouse", "module": "cat_game.cat_and_mouse", "function": "main"},
            {"name": "Asteroids", "module": "astroids.game", "function": "main"},
            {"name": "Maze Runner", "module": "maze_runner.maze_game", "function": "main"}
        ]
        
        self.buttons = self.create_buttons()
        
    def create_buttons(self):
        buttons = []
        total_height = len(self.games) * (BUTTON_SIZE[1] + BUTTON_SPACING)
        start_y = (WINDOW_SIZE[1] - total_height) // 2
        
        for i, game in enumerate(self.games):
            x = (WINDOW_SIZE[0] - BUTTON_SIZE[0]) // 2
            y = start_y + i * (BUTTON_SIZE[1] + BUTTON_SPACING)
            buttons.append((Button(x, y, BUTTON_SIZE[0], BUTTON_SIZE[1], game["name"]), game))
        
        return buttons
        
    def launch_game(self, game_info):
        try:
            sys.path.insert(0, os.path.dirname(__file__))  # Add current directory to path
            module_name = game_info["module"]
            
            # Import the game module
            if module_name.count('.') > 0:
                package, module = module_name.rsplit('.', 1)
                game_module = __import__(module_name, fromlist=[module])
            else:
                game_module = __import__(module_name)
            
            # Get and call the main function
            main_func = getattr(game_module, game_info["function"])
            
            try:
                # Run the game
                main_func()
            finally:
                # Quit pygame to clean up resources
                pygame.quit()
                # Reinitialize pygame for selector
                pygame.init()
                pygame.font.init()
                self.screen = pygame.display.set_mode(WINDOW_SIZE)
                pygame.display.set_caption("Game Selector")
            
        except Exception as e:
            print(f"Error launching {game_info['name']}: {str(e)}")
            # Make sure selector window is restored even on error
            pygame.quit()
            pygame.init()
            pygame.font.init()
            self.screen = pygame.display.set_mode(WINDOW_SIZE)
            pygame.display.set_caption("Game Selector")
    
    def run(self):
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue
                    
                # Check button clicks
                for button, game in self.buttons:
                    if button.handle_event(event):
                        self.launch_game(game)
            
            # Draw
            self.screen.fill(BLACK)
            
            # Draw title
            title_font = pygame.font.Font(None, 74)
            title = title_font.render("Game Selection", True, WHITE)
            title_rect = title.get_rect(
                centerx=WINDOW_SIZE[0] // 2,
                y=50
            )
            self.screen.blit(title, title_rect)
            
            # Draw buttons
            for button, _ in self.buttons:
                button.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)

def main():
    selector = GameSelector()
    selector.run()
    pygame.quit()

if __name__ == "__main__":
    main()