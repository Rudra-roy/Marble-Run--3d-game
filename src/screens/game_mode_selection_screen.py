"""
Game mode selection screen implementation.
"""

import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from screens.base_screen import BaseScreen
from ui.renderer import UIRenderer
from core.settings import game_settings
from core.state_manager import GAME_MODE_SELECTION

class GameModeSelectionScreen(BaseScreen):
    """Game mode selection screen"""
    
    def render(self):
        """Render the game mode selection screen"""
        self.opengl_manager.setup_2d_projection()
        
        # Draw animated background
        UIRenderer.draw_menu_background()
        
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        center_x = window_width // 2
        center_y = window_height // 2
        
        # Apply transition animation
        offset_x = self.get_animation_offset()
        
        # Game mode title
        title_text = "SELECT GAME MODE"
        title_width = UIRenderer.get_text_width(title_text, GLUT_BITMAP_TIMES_ROMAN_24)
        glColor3f(0.2, 1.0, 0.8)  # Cyan-green color
        glRasterPos2f(center_x - title_width//2 + offset_x, center_y - 150)
        for char in title_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        
        # Game mode items with descriptions
        mode_items = ["Single Player", "Two Player Mode"]
        mode_descriptions = ["Play solo adventure", "Play with a friend"]
        
        item_spacing = 80
        start_y = center_y - 40
        
        # Get current selection from input handler
        current_selection = self.input_handler.get_menu_selection(GAME_MODE_SELECTION)
        
        for i, (item, description) in enumerate(zip(mode_items, mode_descriptions)):
            # Main mode text
            item_width = UIRenderer.get_text_width(item, GLUT_BITMAP_HELVETICA_18)
            x = center_x - item_width//2 + offset_x
            y = start_y + i * item_spacing
            
            UIRenderer.draw_menu_item(item, x, y, selected=(i == current_selection), 
                                    scale=game_settings.get_text_size())
            
            # Description text
            if i == current_selection:
                glColor3f(0.9, 0.9, 1.0)  # Light blue for selected description
            else:
                glColor3f(0.6, 0.7, 0.8)  # Dimmer for unselected
            
            desc_width = UIRenderer.get_text_width(description, GLUT_BITMAP_HELVETICA_12)
            desc_x = center_x - desc_width//2 + offset_x
            desc_y = y + 25
            
            glRasterPos2f(desc_x, desc_y)
            for char in description:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
        
        # Instructions
        glColor3f(0.6, 0.7, 0.8)
        instructions = "Use Arrow Keys to Navigate, Enter to Select, ESC to Go Back"
        inst_width = UIRenderer.get_text_width(instructions, GLUT_BITMAP_HELVETICA_12)
        glRasterPos2f(center_x - inst_width//2 + offset_x, window_height - 50)
        for char in instructions:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
        
        # Draw mode icons/indicators
        self._draw_mode_icons(center_x, start_y, offset_x, item_spacing)
    
    def _draw_mode_icons(self, center_x, start_y, offset_x, item_spacing):
        """Draw decorative icons for game modes"""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for i in range(2):
            icon_x = center_x - 150 + offset_x
            icon_y = start_y + i * item_spacing - 10
            
            if i == 0:  # Single player icon
                glColor4f(0.2, 0.8, 1.0, 0.6)
                # Draw single circle
                glBegin(GL_TRIANGLE_FAN)
                glVertex2f(icon_x, icon_y)
                for j in range(16):
                    angle = j * 2 * math.pi / 16
                    glVertex2f(icon_x + 8 * math.cos(angle), icon_y + 8 * math.sin(angle))
                glEnd()
            else:  # Two player icon
                glColor4f(1.0, 0.6, 0.2, 0.6)
                # Draw two circles
                for offset in [-6, 6]:
                    glBegin(GL_TRIANGLE_FAN)
                    glVertex2f(icon_x + offset, icon_y)
                    for j in range(16):
                        angle = j * 2 * math.pi / 16
                        glVertex2f(icon_x + offset + 6 * math.cos(angle), icon_y + 6 * math.sin(angle))
                    glEnd()
        
        glDisable(GL_BLEND)
