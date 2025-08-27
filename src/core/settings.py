"""
Game settings and configuration management.
"""

class GameSettings:
    """Manages all game settings and configuration"""
    
    def __init__(self):
        # Initialize default settings
        self._settings = {
            'sound_volume': 50,
            'text_size': 1.0,  # multiplier for text size
            'difficulty': 1,   # 0=Easy, 1=Medium, 2=Hard
            'difficulty_names': ['Easy', 'Medium', 'Hard'],
            'game_mode': 0,    # 0=Single Player, 1=Two Player
            'mode_names': ['Single Player', 'Two Player']
        }
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self._settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self._settings[key] = value
    
    def get_sound_volume(self):
        """Get current sound volume"""
        return self._settings['sound_volume']
    
    def set_sound_volume(self, volume):
        """Set sound volume (0-100)"""
        self._settings['sound_volume'] = max(0, min(100, volume))
    
    def get_text_size(self):
        """Get current text size multiplier"""
        return self._settings['text_size']
    
    def set_text_size(self, size):
        """Set text size multiplier (0.5-2.0)"""
        self._settings['text_size'] = max(0.5, min(2.0, size))
    
    def get_difficulty(self):
        """Get current difficulty level"""
        return self._settings['difficulty']
    
    def set_difficulty(self, difficulty):
        """Set difficulty level (0-2)"""
        self._settings['difficulty'] = max(0, min(2, difficulty))
    
    def get_difficulty_name(self):
        """Get current difficulty name"""
        return self._settings['difficulty_names'][self._settings['difficulty']]
    
    def get_game_mode(self):
        """Get current game mode"""
        return self._settings['game_mode']
    
    def set_game_mode(self, mode):
        """Set game mode (0-1)"""
        self._settings['game_mode'] = max(0, min(1, mode))
    
    def get_game_mode_name(self):
        """Get current game mode name"""
        return self._settings['mode_names'][self._settings['game_mode']]
    
    def get_all_settings(self):
        """Get a copy of all settings"""
        return self._settings.copy()

# Global settings instance
game_settings = GameSettings()
