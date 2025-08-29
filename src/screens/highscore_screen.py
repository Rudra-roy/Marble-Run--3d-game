"""
High Score screen implementation.
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from screens.base_screen import BaseScreen
from ui.renderer import UIRenderer
from core.state_manager import MAIN_MENU

class HighScoreScreen(BaseScreen):
    """High Score screen displaying session records"""
    
    def __init__(self, state_manager, opengl_manager, input_handler):
        super().__init__(state_manager, opengl_manager, input_handler)
    
    def render(self):
        """Render the high score screen"""
        self.opengl_manager.setup_2d_projection()
        
        # Draw animated background
        UIRenderer.draw_menu_background()
        
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        center_x = window_width // 2
        center_y = window_height // 2
        
        # Apply transition animation
        offset_x = self.get_animation_offset()
        
        # Title
        title_text = "HIGH SCORES"
        title_width = UIRenderer.get_text_width(title_text, GLUT_BITMAP_TIMES_ROMAN_24)
        glColor3f(1.0, 0.8, 0.2)
        glRasterPos2f(center_x - title_width//2 + offset_x, center_y - 150)
        for char in title_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        
        # Get high scores from game screen (we'll need to pass these in)
        # For now, display placeholder text
        glColor3f(0.9, 0.9, 0.9)
        
        # Single Player High Scores
        sp_title = "SINGLE PLAYER"
        sp_width = UIRenderer.get_text_width(sp_title, GLUT_BITMAP_HELVETICA_18)
        glRasterPos2f(center_x - sp_width//2 + offset_x, center_y - 80)
        for char in sp_title:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        
        # Placeholder scores
        single_scores = [
            "High Score: 0 points",
            "Best Time: No completion yet"
        ]
        
        for i, score_line in enumerate(single_scores):
            score_width = UIRenderer.get_text_width(score_line, GLUT_BITMAP_HELVETICA_12)
            glRasterPos2f(center_x - score_width//2 + offset_x, center_y - 40 + i * 25)
            for char in score_line:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
        
        # Multiplayer High Scores
        mp_title = "MULTIPLAYER"
        mp_width = UIRenderer.get_text_width(mp_title, GLUT_BITMAP_HELVETICA_18)
        glRasterPos2f(center_x - mp_width//2 + offset_x, center_y + 30)
        for char in mp_title:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        
        multiplayer_scores = [
            "Player 1 High Score: 0 points",
            "Player 2 High Score: 0 points"
        ]
        
        for i, score_line in enumerate(multiplayer_scores):
            score_width = UIRenderer.get_text_width(score_line, GLUT_BITMAP_HELVETICA_12)
            glRasterPos2f(center_x - score_width//2 + offset_x, center_y + 70 + i * 25)
            for char in score_line:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
        
        # Back instruction
        glColor3f(0.6, 0.7, 0.8)
        back_text = "Press ESC to go back"
        back_width = UIRenderer.get_text_width(back_text, GLUT_BITMAP_HELVETICA_12)
        glRasterPos2f(center_x - back_width//2 + offset_x, window_height - 50)
        for char in back_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
    
    def handle_key_press(self, key):
        """Handle key press events"""
        if key == '\x1b':  # ESC key
            self.state_manager.start_transition(MAIN_MENU)
