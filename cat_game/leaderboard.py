import json
import os

class Leaderboard:
    def __init__(self):
        self.leaderboards = {
            'easy': [],
            'medium': [],
            'hard': []
        }
        self.load_leaderboard()
    
    def load_leaderboard(self):
        try:
            if os.path.exists('leaderboard.json'):
                with open('leaderboard.json', 'r') as f:
                    self.leaderboards = json.load(f)
        except:
            self.leaderboards = {'easy': [], 'medium': [], 'hard': []}
    
    def save_leaderboard(self):
        with open('leaderboard.json', 'w') as f:
            json.dump(self.leaderboards, f)
    
    def add_score(self, difficulty, name, level):
        if difficulty not in self.leaderboards:
            return False
            
        # First, check if this score would make it to top score
        if not self.is_high_score(difficulty, level):
            return False
            
        # Replace the scores with just this one
        self.leaderboards[difficulty] = [{'name': name, 'level': level}]
        self.save_leaderboard()
        return True
        
    def is_high_score(self, difficulty, level):
        if difficulty not in self.leaderboards:
            return False
            
        scores = self.leaderboards[difficulty]
        # If no scores yet, it's a high score
        if len(scores) == 0:
            return True
            
        # Only one score to check now
        return level > scores[0]['level']
    
    def get_leaderboard(self, difficulty):
        if difficulty not in self.leaderboards:
            return []
        return self.leaderboards[difficulty]