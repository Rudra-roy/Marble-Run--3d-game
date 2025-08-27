"""
3D rendering utilities for the game.
"""

import math
from OpenGL.GL import *
from OpenGL.GLU import *

class Renderer3D:
    """3D rendering utilities"""
    
    @staticmethod
    def draw_sphere(x, y, z, radius, color=(1.0, 0.2, 0.2), segments=16):
        """Draw a sphere at the given position"""
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Create a sphere using triangular strips
        for i in range(segments):
            lat1 = math.pi * (-0.5 + float(i) / segments)
            lat2 = math.pi * (-0.5 + float(i + 1) / segments)
            
            glBegin(GL_TRIANGLE_STRIP)
            for j in range(segments + 1):
                lon = 2 * math.pi * float(j) / segments
                
                # First vertex
                x1 = radius * math.cos(lat1) * math.cos(lon)
                y1 = radius * math.sin(lat1)
                z1 = radius * math.cos(lat1) * math.sin(lon)
                glNormal3f(x1/radius, y1/radius, z1/radius)
                glVertex3f(x1, y1, z1)
                
                # Second vertex
                x2 = radius * math.cos(lat2) * math.cos(lon)
                y2 = radius * math.sin(lat2)
                z2 = radius * math.cos(lat2) * math.sin(lon)
                glNormal3f(x2/radius, y2/radius, z2/radius)
                glVertex3f(x2, y2, z2)
            glEnd()
        
        glPopMatrix()
    
    @staticmethod
    def setup_lighting():
        """Setup basic lighting for 3D scene"""
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Light position
        light_pos = [5.0, 10.0, 5.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        
        # Light properties
        light_ambient = [0.2, 0.2, 0.2, 1.0]
        light_diffuse = [0.8, 0.8, 0.8, 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]
        
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    
    @staticmethod
    def disable_lighting():
        """Disable lighting for UI rendering"""
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
    
    @staticmethod
    def draw_skybox():
        """Draw a simple skybox"""
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Simple gradient background
        glBegin(GL_QUADS)
        
        # Create a large background quad with gradient
        glColor3f(0.3, 0.6, 1.0)  # Sky blue at top
        glVertex3f(-100, 50, -100)
        glVertex3f(100, 50, -100)
        glVertex3f(100, 50, 100)
        glVertex3f(-100, 50, 100)
        
        # Bottom face - lighter
        glColor3f(0.7, 0.9, 1.0)  # Lighter blue
        glVertex3f(-100, -20, -100)
        glVertex3f(-100, -20, 100)
        glVertex3f(100, -20, 100)
        glVertex3f(100, -20, -100)
        
        glEnd()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    @staticmethod
    def draw_score_card(score, window_width, window_height):
        """Draw score card in corner"""
        from ui.renderer import UIRenderer
        
        # Switch to 2D mode
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, window_width, window_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Card background
        card_width = 150
        card_height = 80
        card_x = window_width - card_width - 20
        card_y = 20
        
        # Draw card background with rounded corners effect
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Shadow
        glColor4f(0.0, 0.0, 0.0, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(card_x + 3, card_y + 3)
        glVertex2f(card_x + card_width + 3, card_y + 3)
        glVertex2f(card_x + card_width + 3, card_y + card_height + 3)
        glVertex2f(card_x + 3, card_y + card_height + 3)
        glEnd()
        
        # Main card
        glColor4f(0.1, 0.1, 0.2, 0.9)
        glBegin(GL_QUADS)
        glVertex2f(card_x, card_y)
        glVertex2f(card_x + card_width, card_y)
        glVertex2f(card_x + card_width, card_y + card_height)
        glVertex2f(card_x, card_y + card_height)
        glEnd()
        
        # Card border
        glColor4f(0.4, 0.6, 1.0, 0.8)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(card_x, card_y)
        glVertex2f(card_x + card_width, card_y)
        glVertex2f(card_x + card_width, card_y + card_height)
        glVertex2f(card_x, card_y + card_height)
        glEnd()
        glLineWidth(1.0)
        
        glDisable(GL_BLEND)
        
        # Score text
        glColor3f(1.0, 1.0, 1.0)
        score_title = "SCORE"
        try:
            from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_12
            title_width = UIRenderer.get_text_width(score_title, GLUT_BITMAP_HELVETICA_12)
            title_x = card_x + (card_width - title_width) // 2
            UIRenderer.draw_text(score_title, title_x, card_y + 25, GLUT_BITMAP_HELVETICA_12)
        except ImportError:
            # Fallback text rendering
            title_x = card_x + 50
            glRasterPos2f(title_x, card_y + 25)
            for char in score_title:
                pass  # Skip text if fonts not available
        
        # Score value
        score_text = str(score)
        try:
            from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_12
            score_width = UIRenderer.get_text_width(score_text, GLUT_BITMAP_HELVETICA_12) * 1.5
            score_x = card_x + (card_width - score_width) // 2
            
            # Make score number larger and more prominent
            glColor3f(1.0, 0.8, 0.2)
            glRasterPos2f(score_x, card_y + 55)
            for char in score_text:
                from OpenGL.GLUT import glutBitmapCharacter, GLUT_BITMAP_TIMES_ROMAN_24
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        except ImportError:
            # Fallback if GLUT fonts not available
            glColor3f(1.0, 0.8, 0.2)
            glRasterPos2f(card_x + 70, card_y + 55)
            # Skip rendering if fonts not available
        
        # Restore 3D mode
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    @staticmethod
    def draw_game_over_screen(score, window_width, window_height):
        """Draw game over screen"""
        from ui.renderer import UIRenderer
        
        # Switch to 2D mode
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, window_width, window_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Semi-transparent overlay
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(window_width, 0)
        glVertex2f(window_width, window_height)
        glVertex2f(0, window_height)
        glEnd()
        glDisable(GL_BLEND)
        
        # Game Over text
        center_y = window_height // 2
        
        try:
            from OpenGL.GLUT import GLUT_BITMAP_TIMES_ROMAN_24, GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_HELVETICA_12
            glColor3f(1.0, 0.2, 0.2)
            game_over_text = "GAME OVER"
            UIRenderer.draw_centered_text(game_over_text, center_y - 60, GLUT_BITMAP_TIMES_ROMAN_24, (1.0, 0.2, 0.2))
            
            # Final score
            glColor3f(1.0, 1.0, 0.2)
            final_score_text = f"Final Score: {score}"
            UIRenderer.draw_centered_text(final_score_text, center_y - 20, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 0.2))
            
            # Instructions
            glColor3f(0.8, 0.8, 0.8)
            restart_text = "Press R to Restart or ESC to Return to Menu"
            UIRenderer.draw_centered_text(restart_text, center_y + 20, GLUT_BITMAP_HELVETICA_12, (0.8, 0.8, 0.8))
        except ImportError:
            # Fallback if fonts not available - just show basic colored rectangles
            glColor3f(1.0, 0.2, 0.2)
            glBegin(GL_QUADS)
            glVertex2f(window_width//2 - 100, center_y - 70)
            glVertex2f(window_width//2 + 100, center_y - 70)
            glVertex2f(window_width//2 + 100, center_y - 50)
            glVertex2f(window_width//2 - 100, center_y - 50)
            glEnd()
        
        # Restore 3D mode
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
