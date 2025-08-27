"""
Game state management system.
"""

import time
from OpenGL.GLUT import *

# Game states
LOADING_SCREEN = 0
MAIN_MENU = 1
OPTIONS_MENU = 2
GAME_MODE_SELECTION = 3
GAME_3D = 4

class StateManager:
    """Manages game states and transitions"""
    
    def __init__(self):
        self.current_state = LOADING_SCREEN
        self.loading_start_time = 0
        
        # Transition system
        self.transitioning = False
        self.transition_direction = 0  # 1 for forward, -1 for backward
        self.menu_transition_time = 0
        self.menu_animation_offset = 0
        
        # Initialize screens (will be set by game engine)
        self.screens = {}
    
    def set_screens(self, screens):
        """Set the screen instances"""
        self.screens = screens
    
    def set_loading_start_time(self, start_time):
        """Set the loading start time"""
        self.loading_start_time = start_time
    
    def get_current_state(self):
        """Get the current game state"""
        return self.current_state
    
    def start_transition(self, new_state, direction=1):
        """Start a smooth transition between states"""
        self.transitioning = True
        self.transition_direction = direction
        self.menu_transition_time = time.time()
        self.current_state = new_state
    
    def update(self):
        """Update state logic"""
        current_time = time.time()
        
        # Handle transitions
        if self.transitioning:
            transition_progress = (current_time - self.menu_transition_time) * 4.0  # 0.25 second transition
            if transition_progress >= 1.0:
                self.transitioning = False
                self.menu_animation_offset = 0
            else:
                # Smooth easing function
                ease_progress = 1 - (1 - transition_progress) ** 3
                self.menu_animation_offset = self.transition_direction * (1 - ease_progress) * glutGet(GLUT_WINDOW_WIDTH)
        
        # Handle loading screen auto-transition
        if self.current_state == LOADING_SCREEN:
            if current_time - self.loading_start_time >= 3.0:
                self.start_transition(MAIN_MENU)
                print("Loading complete! Entering main menu...")
    
    def render(self):
        """Render the current state"""
        if self.current_state in self.screens:
            screen = self.screens[self.current_state]
            screen.render()
    
    def get_animation_offset(self):
        """Get current menu animation offset"""
        return self.menu_animation_offset
    
    def is_transitioning(self):
        """Check if currently transitioning"""
        return self.transitioning
