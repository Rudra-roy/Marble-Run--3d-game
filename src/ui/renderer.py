"""
UI rendering utilities and helper functions.
"""

import math
import time
from OpenGL.GL import *
from OpenGL.GLUT import *

# Import specific font constants to avoid issues
try:
    from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_12, GLUT_BITMAP_TIMES_ROMAN_24, GLUT_BITMAP_HELVETICA_18
except ImportError:
    # Fallback if specific imports don't work
    pass

class UIRenderer:
    """Utility class for rendering UI elements"""
    
    @staticmethod
    def get_text_width(text, font):
        """Calculate approximate text width for centering"""
        try:
            if font is None:
                font = GLUT_BITMAP_HELVETICA_12
            if font == GLUT_BITMAP_TIMES_ROMAN_24:
                return len(text) * 15  # Approximate character width for large font
            elif font == GLUT_BITMAP_HELVETICA_18:
                return len(text) * 11  # Approximate character width for medium font
            else:
                return len(text) * 8   # Approximate character width for small font
        except:
            # Fallback width calculation
            return len(text) * 8
    
    @staticmethod
    def draw_centered_text(text, y, font, color=(1.0, 1.0, 1.0)):
        """Draw text centered horizontally"""
        try:
            if font is None:
                font = GLUT_BITMAP_HELVETICA_12
            window_width = glutGet(GLUT_WINDOW_WIDTH)
            text_width = UIRenderer.get_text_width(text, font)
            x = (window_width - text_width) // 2
            
            glColor3f(*color)
            glRasterPos2f(x, y)
            for char in text:
                glutBitmapCharacter(font, ord(char))
        except:
            # Fallback if fonts not available
            pass
    
    @staticmethod
    def draw_text(text, x, y, font=None):
        """Draw text at specified position"""
        try:
            if font is None:
                font = GLUT_BITMAP_HELVETICA_12
            glRasterPos2f(x, y)
            for char in text:
                glutBitmapCharacter(font, ord(char))
        except:
            # Fallback if fonts not available
            pass
    
    @staticmethod
    def draw_loading_animation(center_x, center_y, radius=30):
        """Draw rotating loading animation"""
        from screens.loading_screen import LoadingScreen
        angle = LoadingScreen.get_animation_angle()
        
        # Draw spinning outer ring
        glColor3f(0.2, 0.8, 1.0)  # Light blue
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(center_x, center_y)
        
        num_segments = 16
        for i in range(num_segments + 1):
            angle_rad = (i * 2 * math.pi / num_segments) + math.radians(angle)
            x = center_x + radius * math.cos(angle_rad)
            y = center_y + radius * math.sin(angle_rad)
            # Fade effect based on position
            alpha = 0.3 + 0.7 * (1.0 - (i / num_segments))
            glColor3f(0.2 * alpha, 0.8 * alpha, 1.0 * alpha)
            glVertex2f(x, y)
        glEnd()
        
        # Draw middle ring
        glColor3f(1.0, 0.6, 0.2)  # Orange
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(center_x, center_y)
        
        mid_radius = radius * 0.7
        for i in range(num_segments + 1):
            angle_rad = (i * 2 * math.pi / num_segments) - math.radians(angle * 1.5)
            x = center_x + mid_radius * math.cos(angle_rad)
            y = center_y + mid_radius * math.sin(angle_rad)
            alpha = 0.4 + 0.6 * (1.0 - (i / num_segments))
            glColor3f(1.0 * alpha, 0.6 * alpha, 0.2 * alpha)
            glVertex2f(x, y)
        glEnd()
        
        # Draw inner core
        glColor3f(1.0, 1.0, 0.3)  # Bright yellow
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(center_x, center_y)
        
        inner_radius = radius * 0.3
        for i in range(12):
            angle_rad = (i * 2 * math.pi / 12) + math.radians(angle * 2)
            x = center_x + inner_radius * math.cos(angle_rad)
            y = center_y + inner_radius * math.sin(angle_rad)
            glVertex2f(x, y)
        glEnd()
    
    @staticmethod
    def draw_menu_background():
        """Draw animated background for menus"""
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        
        # Animated gradient background
        time_factor = time.time() * 0.5
        
        # Create flowing gradient
        glBegin(GL_QUADS)
        # Top gradient
        r1, g1, b1 = 0.05 + 0.02 * math.sin(time_factor), 0.1 + 0.03 * math.cos(time_factor), 0.2 + 0.05 * math.sin(time_factor * 0.7)
        glColor3f(r1, g1, b1)
        glVertex2f(0, 0)
        glVertex2f(window_width, 0)
        
        # Bottom gradient
        r2, g2, b2 = 0.1 + 0.03 * math.cos(time_factor * 0.8), 0.05 + 0.02 * math.sin(time_factor * 1.2), 0.15 + 0.04 * math.cos(time_factor)
        glColor3f(r2, g2, b2)
        glVertex2f(window_width, window_height)
        glVertex2f(0, window_height)
        glEnd()
        
        # Add floating particles effect
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for i in range(20):
            particle_time = time_factor + i * 0.3
            x = (window_width * 0.1) + (window_width * 0.8) * ((i * 37) % 100) / 100.0
            y = (window_height * ((particle_time * 30 + i * 50) % 360) / 360.0) % window_height
            size = 2 + 3 * math.sin(particle_time + i)
            alpha = 0.3 + 0.2 * math.sin(particle_time * 2 + i)
            
            glColor4f(0.6, 0.8, 1.0, alpha)
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(x, y)
            for j in range(8):
                angle = j * 2 * math.pi / 8
                glVertex2f(x + size * math.cos(angle), y + size * math.sin(angle))
            glEnd()
        
        glDisable(GL_BLEND)
    
    @staticmethod
    def draw_menu_item(text, x, y, selected=False, scale=1.0):
        """Draw a menu item with selection highlighting"""
        font = GLUT_BITMAP_HELVETICA_18
        
        # Calculate text dimensions
        text_width = UIRenderer.get_text_width(text, font) * scale
        text_height = 18 * scale
        
        if selected:
            # Draw selection background with glow
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            # Outer glow
            padding = 15
            glColor4f(0.2, 0.6, 1.0, 0.3)
            glBegin(GL_QUADS)
            glVertex2f(x - padding - 5, y - text_height - 5)
            glVertex2f(x + text_width + padding + 5, y - text_height - 5)
            glVertex2f(x + text_width + padding + 5, y + 10)
            glVertex2f(x - padding - 5, y + 10)
            glEnd()
            
            # Inner background
            glColor4f(0.1, 0.4, 0.8, 0.6)
            glBegin(GL_QUADS)
            glVertex2f(x - padding, y - text_height)
            glVertex2f(x + text_width + padding, y - text_height)
            glVertex2f(x + text_width + padding, y + 5)
            glVertex2f(x - padding, y + 5)
            glEnd()
            
            glDisable(GL_BLEND)
            
            # Selected text color (bright white/yellow)
            glColor3f(1.0, 1.0, 0.8)
        else:
            # Normal text color (light blue)
            glColor3f(0.8, 0.9, 1.0)
        
        # Draw text
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(font, ord(char))
