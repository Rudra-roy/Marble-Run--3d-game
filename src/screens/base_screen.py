"""
Base screen class for all game screens.
"""

from abc import ABC, abstractmethod

class BaseScreen(ABC):
    """Abstract base class for all game screens"""
    
    def __init__(self, state_manager, opengl_manager, input_handler):
        self.state_manager = state_manager
        self.opengl_manager = opengl_manager
        self.input_handler = input_handler
    
    @abstractmethod
    def render(self):
        """Render the screen - must be implemented by subclasses"""
        pass
    
    def update(self):
        """Update screen logic - can be overridden by subclasses"""
        pass
    
    def get_animation_offset(self):
        """Get current animation offset for transitions"""
        return self.state_manager.get_animation_offset()
