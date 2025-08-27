"""
Main menu screen implementation.
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from screens.base_screen import BaseScreen
from ui.renderer import UIRenderer
from core.settings import game_settings
from core.state_manager import MAIN_MENU

class MainMenuScreen(BaseScreen):
    """Main menu screen with navigation"""
    
    def render(self):
        """Render the main menu"""
        self.opengl_manager.setup_2d_projection()
        
        # Draw animated background
        UIRenderer.draw_menu_background()
        
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        center_x = window_width // 2
        center_y = window_height // 2
        
        # Apply transition animation
        offset_x = self.get_animation_offset()
        
        # Game title
        title_text = "MARBLE RUN"
        title_width = UIRenderer.get_text_width(title_text, GLUT_BITMAP_TIMES_ROMAN_24)
        glColor3f(1.0, 0.8, 0.2)
        glRasterPos2f(center_x - title_width//2 + offset_x, center_y - 150)
        for char in title_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        
        # Menu items
        menu_items = ["Start Game", "Options", "Quit"]
        item_spacing = 60
        start_y = center_y - 30
        
        # Get current selection from input handler
        current_selection = self.input_handler.get_menu_selection(MAIN_MENU)
        
        for i, item in enumerate(menu_items):
            item_width = UIRenderer.get_text_width(item, GLUT_BITMAP_HELVETICA_18)
            x = center_x - item_width//2 + offset_x
            y = start_y + i * item_spacing
            
            UIRenderer.draw_menu_item(item, x, y, selected=(i == current_selection), 
                                    scale=game_settings.get_text_size())
        
        # Instructions
        glColor3f(0.6, 0.7, 0.8)
        instructions = "Use Arrow Keys to Navigate, Enter to Select"
        inst_width = UIRenderer.get_text_width(instructions, GLUT_BITMAP_HELVETICA_12)
        glRasterPos2f(center_x - inst_width//2 + offset_x, window_height - 50)
        for char in instructions:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
