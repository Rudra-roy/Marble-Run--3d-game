"""
Options menu screen implementation.
"""

import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from screens.base_screen import BaseScreen
from ui.renderer import UIRenderer
from core.settings import game_settings
from core.state_manager import OPTIONS_MENU

class OptionsMenuScreen(BaseScreen):
    """Options menu screen for game settings"""
    
    def render(self):
        """Render the options menu"""
        self.opengl_manager.setup_2d_projection()
        
        # Draw animated background
        UIRenderer.draw_menu_background()
        
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        center_x = window_width // 2
        center_y = window_height // 2
        
        # Apply transition animation
        offset_x = self.get_animation_offset()
        
        # Options title
        title_text = "OPTIONS"
        title_width = UIRenderer.get_text_width(title_text, GLUT_BITMAP_TIMES_ROMAN_24)
        glColor3f(0.8, 1.0, 0.6)
        glRasterPos2f(center_x - title_width//2 + offset_x, center_y - 150)
        for char in title_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        
        # Options items
        options_items = [
            f"Sound Volume: {game_settings.get_sound_volume()}% (Placeholder)",
            f"Text Size: {game_settings.get_text_size():.1f}x",
            f"Difficulty: {game_settings.get_difficulty_name()} (Placeholder)",
            "Back to Main Menu"
        ]
        
        item_spacing = 60
        start_y = center_y - 60
        
        # Get current selection from input handler
        current_selection = self.input_handler.get_menu_selection(OPTIONS_MENU)
        
        for i, item in enumerate(options_items):
            item_width = UIRenderer.get_text_width(item, GLUT_BITMAP_HELVETICA_18)
            x = center_x - item_width//2 + offset_x
            y = start_y + i * item_spacing
            
            UIRenderer.draw_menu_item(item, x, y, selected=(i == current_selection), 
                                    scale=game_settings.get_text_size())
        
        # Draw difficulty indicator
        self._draw_difficulty_indicator(current_selection, window_width, center_y, offset_x)
        
        # Instructions
        glColor3f(0.6, 0.7, 0.8)
        instructions = "Use Arrow Keys, Left/Right to Adjust, Enter to Select"
        inst_width = UIRenderer.get_text_width(instructions, GLUT_BITMAP_HELVETICA_12)
        glRasterPos2f(center_x - inst_width//2 + offset_x, window_height - 50)
        for char in instructions:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
    
    def _draw_difficulty_indicator(self, current_selection, window_width, center_y, offset_x):
        """Draw visual indicator for difficulty level"""
        if current_selection != 2:  # Only show for difficulty option
            return
        
        # Draw difficulty bars
        bar_width = 20
        bar_height = 8
        bar_spacing = 25
        start_x = window_width // 2 + 200 + offset_x
        start_y = center_y - 60 + 2 * 60  # Position next to difficulty option
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        colors = [(0.2, 0.8, 0.2), (1.0, 0.8, 0.2), (1.0, 0.2, 0.2)]  # Green, Yellow, Red
        
        for i in range(3):
            if i <= game_settings.get_difficulty():
                glColor4f(*colors[i], 0.8)
            else:
                glColor4f(0.3, 0.3, 0.3, 0.3)
            
            glBegin(GL_QUADS)
            glVertex2f(start_x + i * bar_spacing, start_y)
            glVertex2f(start_x + i * bar_spacing + bar_width, start_y)
            glVertex2f(start_x + i * bar_spacing + bar_width, start_y + bar_height)
            glVertex2f(start_x + i * bar_spacing, start_y + bar_height)
            glEnd()
        
        glDisable(GL_BLEND)
