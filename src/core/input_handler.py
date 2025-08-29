"""
Input handling system for keyboard and special keys.
"""

import sys
from OpenGL.GLUT import *
from core.state_manager import MAIN_MENU, OPTIONS_MENU, GAME_MODE_SELECTION, GAME_3D
from core.settings import game_settings

class InputHandler:
    """Handles all input events and routes them to appropriate handlers"""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.menu_selections = {
            MAIN_MENU: 0,
            OPTIONS_MENU: 0,
            GAME_MODE_SELECTION: 0
        }
    
    def keyboard(self, key, x, y):
        """Handle keyboard input"""
        current_state = self.state_manager.get_current_state()
        
        # Handle game input for 3D screen
        if current_state == GAME_3D:
            screen = self.state_manager.screens.get(GAME_3D)
            if screen:
                if key == b'\x1b':  # ESC key
                    self._play_sound_effect("menu_back")
                    self.state_manager.start_transition(MAIN_MENU, -1)
                else:
                    # Pass key to game screen
                    try:
                        char = key.decode('utf-8')
                        screen.handle_key_press(char)
                    except UnicodeDecodeError:
                        pass
            return
        
        if key == b'\x1b':  # ESC key
            self._handle_escape_key(current_state)
        elif key == b'\r':  # Enter key
            self._handle_enter_key(current_state)
    
    def keyboard_up(self, key, x, y):
        """Handle keyboard release input"""
        current_state = self.state_manager.get_current_state()
        
        # Handle game input for 3D screen
        if current_state == GAME_3D:
            screen = self.state_manager.screens.get(GAME_3D)
            if screen:
                try:
                    char = key.decode('utf-8')
                    screen.handle_key_release(char)
                except UnicodeDecodeError:
                    pass
    
    def special_keys(self, key, x, y):
        """Handle special keys (arrows)"""
        current_state = self.state_manager.get_current_state()
        
        if current_state == GAME_3D:
            screen = self.state_manager.screens.get(GAME_3D)
            if screen:
                # Forward arrow key presses to game screen (Player 2 controls)
                try:
                    screen.handle_special_key_press(key)
                except Exception:
                    pass
            return
        
        if current_state == MAIN_MENU:
            self._handle_main_menu_navigation(key)
        elif current_state == OPTIONS_MENU:
            self._handle_options_menu_navigation(key)
        elif current_state == GAME_MODE_SELECTION:
            self._handle_game_mode_navigation(key)

    def special_keys_up(self, key, x, y):
        """Handle special keys release (arrows)"""
        current_state = self.state_manager.get_current_state()
        
        if current_state == GAME_3D:
            screen = self.state_manager.screens.get(GAME_3D)
            if screen:
                try:
                    screen.handle_special_key_release(key)
                except Exception:
                    pass
            return
    
    def _handle_escape_key(self, current_state):
        """Handle ESC key for different states"""
        if current_state == GAME_3D:
            self._play_sound_effect("menu_back")
            self.state_manager.start_transition(MAIN_MENU, -1)
        elif current_state == OPTIONS_MENU:
            self._play_sound_effect("menu_back")
            self.state_manager.start_transition(MAIN_MENU, -1)
        elif current_state == GAME_MODE_SELECTION:
            self._play_sound_effect("menu_back")
            self.state_manager.start_transition(MAIN_MENU, -1)
        elif current_state == MAIN_MENU:
            print("Thanks for playing Marble Run!")
            self._safe_exit()
    
    def _handle_enter_key(self, current_state):
        """Handle Enter key for different states"""
        if current_state == MAIN_MENU:
            self._handle_main_menu_enter()
        elif current_state == OPTIONS_MENU:
            self._handle_options_menu_enter()
        elif current_state == GAME_MODE_SELECTION:
            self._handle_game_mode_enter()
    
    def _handle_main_menu_enter(self):
        """Handle Enter key in main menu"""
        selection = self.menu_selections[MAIN_MENU]
        self._play_sound_effect("menu_confirm")
        
        if selection == 0:  # Start Game
            self.state_manager.start_transition(GAME_MODE_SELECTION)
            print("Selecting game mode...")
        elif selection == 1:  # Options
            self.state_manager.start_transition(OPTIONS_MENU)
            self.menu_selections[OPTIONS_MENU] = 0
        elif selection == 2:  # Quit
            print("Thanks for playing Marble Run!")
            self._safe_exit()
    
    def _handle_options_menu_enter(self):
        """Handle Enter key in options menu"""
        selection = self.menu_selections[OPTIONS_MENU]
        
        if selection == 3:  # Back to Main Menu
            self._play_sound_effect("menu_back")
            self.state_manager.start_transition(MAIN_MENU, -1)
        else:
            self._play_sound_effect("menu_confirm")
    
    def _handle_game_mode_enter(self):
        """Handle Enter key in game mode selection"""
        selection = self.menu_selections[GAME_MODE_SELECTION]
        self._play_sound_effect("menu_confirm")
        
        if selection == 0:  # Single Player
            game_settings.set_game_mode(0)
            self.state_manager.start_transition(GAME_3D)
            print("Starting single player game...")
        elif selection == 1:  # Two Player
            game_settings.set_game_mode(1)
            self.state_manager.start_transition(GAME_3D)
            print("Starting two player game...")
    
    def _handle_main_menu_navigation(self, key):
        """Handle navigation in main menu"""
        if key == GLUT_KEY_UP:
            self.menu_selections[MAIN_MENU] = (self.menu_selections[MAIN_MENU] - 1) % 3
            self._play_sound_effect("menu_select")
        elif key == GLUT_KEY_DOWN:
            self.menu_selections[MAIN_MENU] = (self.menu_selections[MAIN_MENU] + 1) % 3
            self._play_sound_effect("menu_select")
    
    def _handle_options_menu_navigation(self, key):
        """Handle navigation in options menu"""
        selection = self.menu_selections[OPTIONS_MENU]
        
        if key == GLUT_KEY_UP:
            self.menu_selections[OPTIONS_MENU] = (selection - 1) % 4
            self._play_sound_effect("menu_select")
        elif key == GLUT_KEY_DOWN:
            self.menu_selections[OPTIONS_MENU] = (selection + 1) % 4
            self._play_sound_effect("menu_select")
        elif key == GLUT_KEY_LEFT:
            self._adjust_option(-1, selection)
        elif key == GLUT_KEY_RIGHT:
            self._adjust_option(1, selection)
    
    def _handle_game_mode_navigation(self, key):
        """Handle navigation in game mode selection"""
        if key == GLUT_KEY_UP:
            self.menu_selections[GAME_MODE_SELECTION] = (self.menu_selections[GAME_MODE_SELECTION] - 1) % 2
            self._play_sound_effect("menu_select")
        elif key == GLUT_KEY_DOWN:
            self.menu_selections[GAME_MODE_SELECTION] = (self.menu_selections[GAME_MODE_SELECTION] + 1) % 2
            self._play_sound_effect("menu_select")
    
    def _adjust_option(self, direction, selection):
        """Adjust option values"""
        if selection == 0:  # Sound Volume
            current_volume = game_settings.get_sound_volume()
            new_volume = max(0, min(100, current_volume + direction * 10))
            game_settings.set_sound_volume(new_volume)
        elif selection == 1:  # Text Size
            current_size = game_settings.get_text_size()
            new_size = max(0.5, min(2.0, round(current_size + direction * 0.1, 1)))
            game_settings.set_text_size(new_size)
        elif selection == 2:  # Difficulty
            current_difficulty = game_settings.get_difficulty()
            new_difficulty = (current_difficulty + direction) % 3
            game_settings.set_difficulty(new_difficulty)
        
        self._play_sound_effect("menu_confirm")
    
    def _play_sound_effect(self, effect_type):
        """Placeholder for sound effects"""
        volume = game_settings.get_sound_volume()
        if volume > 0:
            if effect_type == "menu_select":
                print(f"♪ Menu selection sound (Volume: {volume}%)")
            elif effect_type == "menu_confirm":
                print(f"♪ Menu confirm sound (Volume: {volume}%)")
            elif effect_type == "menu_back":
                print(f"♪ Menu back sound (Volume: {volume}%)")
    
    def _safe_exit(self):
        """Safely exit the application"""
        try:
            glutLeaveMainLoop()  # Modern GLUT way to exit
        except:
            # Fallback for older GLUT versions
            sys.exit(0)
    
    def get_menu_selection(self, state):
        """Get current menu selection for a state"""
        return self.menu_selections.get(state, 0)
