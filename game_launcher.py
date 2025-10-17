import pygame
import sys
import os
import importlib.util

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = (800, 600)
BUTTON_SIZE = (300, 60)
BUTTON_SPACING = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
HIGHLIGHT = (100, 100, 255)

# Initialize window
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Game Launcher")

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, surface):
        color = HIGHLIGHT if self.is_hovered else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class GameLauncher:
    def __init__(self):
        self.running = True
        self.games = self.find_games()
        self.buttons = self.create_buttons()
        self.title_font = pygame.font.Font(None, 74)
        
    def find_games(self):
        """Find all available games in the workspace."""
        games = []
        
        # Define known games and their entry points
        known_games = {
            'Cat and Mouse': {
                'path': 'cat_game/cat_and_mouse.py',
                'module': 'cat_and_mouse',
                'function': 'main'
            },
            'Asteroids': {
                'path': 'astroids/game.py',
                'module': 'game',
                'function': 'main'
            },
            'Maze Runner': {
                'path': 'maze_runner/maze_game.py',
                'module': 'maze_game',
                'function': 'main'
            }
        }
        
        # Check which games are available
        for name, info in known_games.items():
            if os.path.exists(info['path']):
                games.append({
                    'name': name,
                    'path': info['path'],
                    'module': info['module'],
                    'function': info['function']
                })
        
        return games
        
    def create_buttons(self):
        buttons = []
        total_height = len(self.games) * (BUTTON_SIZE[1] + BUTTON_SPACING)
        start_y = (WINDOW_SIZE[1] - total_height) // 2
        
        for i, game in enumerate(self.games):
            x = (WINDOW_SIZE[0] - BUTTON_SIZE[0]) // 2
            y = start_y + i * (BUTTON_SIZE[1] + BUTTON_SPACING)
            buttons.append({
                'button': Button(x, y, BUTTON_SIZE[0], BUTTON_SIZE[1], game['name']),
                'game': game
            })
        
        # Add quit button
        quit_y = start_y + len(self.games) * (BUTTON_SIZE[1] + BUTTON_SPACING)
        buttons.append({
            'button': Button(
                (WINDOW_SIZE[0] - BUTTON_SIZE[0]) // 2,
                quit_y,
                BUTTON_SIZE[0],
                BUTTON_SIZE[1],
                "Quit"
            ),
            'game': None
        })
        
        return buttons
    
    def launch_game(self, game_info):
        """Launch a game module."""
        try:
            # Get the absolute path
            abs_path = os.path.abspath(game_info['path'])
            
            # Import the module
            spec = importlib.util.spec_from_file_location(
                game_info['module'],
                abs_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Call the main function
            main_func = getattr(module, game_info['function'])
            
            # Temporarily hide the launcher window
            pygame.display.set_mode((1, 1))
            
            # Run the game
            main_func()
            
            # Restore the launcher window
            pygame.display.set_mode(WINDOW_SIZE)
            pygame.display.set_caption("Game Launcher")
            
        except Exception as e:
            print(f"Error launching {game_info['name']}: {str(e)}")
    
    def run(self):
        while self.running:
            screen.fill(BLACK)
            
            # Draw title
            title = self.title_font.render("Game Launcher", True, WHITE)
            title_rect = title.get_rect(
                centerx=WINDOW_SIZE[0] // 2,
                y=50
            )
            screen.blit(title, title_rect)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                for button_info in self.buttons:
                    if button_info['button'].handle_event(event):
                        if button_info['game'] is None:  # Quit button
                            self.running = False
                        else:
                            self.launch_game(button_info['game'])
            
            # Draw buttons
            for button_info in self.buttons:
                button_info['button'].draw(screen)
            
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    launcher = GameLauncher()
    launcher.run()