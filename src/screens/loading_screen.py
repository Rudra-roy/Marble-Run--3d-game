"""
Loading screen implementation.
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from screens.base_screen import BaseScreen
from ui.renderer import UIRenderer

class LoadingScreen(BaseScreen):
    """Loading screen with animated elements"""
    
    _animation_angle = 0  # Class variable for animation
    
    def __init__(self, state_manager, opengl_manager, input_handler):
        super().__init__(state_manager, opengl_manager, input_handler)
    
    @classmethod
    def get_animation_angle(cls):
        """Get current animation angle"""
        return cls._animation_angle
    
    def render(self):
        """Render the loading screen with title and animation"""
        self.opengl_manager.setup_2d_projection()
        
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        
        # Draw background image if available, otherwise gradient
        background_texture = self.opengl_manager.get_background_texture()
        if background_texture:
            self._draw_background_texture(background_texture, window_width, window_height)
        else:
            self._draw_gradient_background(window_width, window_height)
        
        # Calculate centered positions
        center_y = window_height // 2
        
        # Add title glow effect
        self._draw_title_glow(window_width, center_y)
        
        # Title "MARBLE RUN" - Large and centered
        title_text = "MARBLE RUN"
        UIRenderer.draw_centered_text(title_text, center_y - 120, GLUT_BITMAP_TIMES_ROMAN_24, (1.0, 1.0, 0.3))
        
        # Subtitle - Medium and centered
        subtitle_text = "A Rolling Ball Adventure"
        UIRenderer.draw_centered_text(subtitle_text, center_y - 85, GLUT_BITMAP_HELVETICA_18, (0.9, 0.95, 1.0))
        
        # Loading animation - centered and bigger
        animation_x = window_width // 2
        animation_y = center_y + 30
        UIRenderer.draw_loading_animation(animation_x, animation_y, 45)
        
        # Loading text - Large and centered
        loading_text = "Loading..."
        UIRenderer.draw_centered_text(loading_text, animation_y + 110, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
        
        # Progress indicator with animated dots
        dots = "." * (1 + int(LoadingScreen._animation_angle / 60) % 3)
        progress_text = f"Please wait{dots}"
        UIRenderer.draw_centered_text(progress_text, animation_y + 140, GLUT_BITMAP_HELVETICA_12, (0.8, 0.8, 0.8))
        
        # Update animation
        LoadingScreen._animation_angle += 5.0  # Faster, smoother animation
        if LoadingScreen._animation_angle >= 360:
            LoadingScreen._animation_angle = 0
    
    def _draw_background_texture(self, texture, window_width, window_height):
        """Draw background texture"""
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor3f(1.0, 1.0, 1.0)  # White to show texture as-is
        
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0); glVertex2f(0, 0)
        glTexCoord2f(1.0, 0.0); glVertex2f(window_width, 0)
        glTexCoord2f(1.0, 1.0); glVertex2f(window_width, window_height)
        glTexCoord2f(0.0, 1.0); glVertex2f(0, window_height)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        
        # Add semi-transparent overlay for better text visibility
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, 0.5)  # Slightly more opaque overlay
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(window_width, 0)
        glVertex2f(window_width, window_height)
        glVertex2f(0, window_height)
        glEnd()
        glDisable(GL_BLEND)
    
    def _draw_gradient_background(self, window_width, window_height):
        """Draw fallback gradient background"""
        glBegin(GL_QUADS)
        glColor3f(0.05, 0.05, 0.15)  # Dark blue top
        glVertex2f(0, 0)
        glVertex2f(window_width, 0)
        glColor3f(0.15, 0.1, 0.25)   # Purple bottom
        glVertex2f(window_width, window_height)
        glVertex2f(0, window_height)
        glEnd()
    
    def _draw_title_glow(self, window_width, center_y):
        """Draw glow effect behind title"""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Title glow effect
        for offset in range(3, 0, -1):
            alpha = 0.1 * (4 - offset)
            title_text = "MARBLE RUN"
            title_width = UIRenderer.get_text_width(title_text, GLUT_BITMAP_TIMES_ROMAN_24)
            title_x = (window_width - title_width) // 2
            
            glColor4f(1.0, 1.0, 0.2, alpha)
            for dx in [-offset, 0, offset]:
                for dy in [-offset, 0, offset]:
                    if dx != 0 or dy != 0:
                        glRasterPos2f(title_x + dx, center_y - 120 + dy)
                        for char in title_text:
                            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        
        glDisable(GL_BLEND)
