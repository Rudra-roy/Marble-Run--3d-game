"""
OpenGL initialization and management.
"""

from PIL import Image
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class OpenGLManager:
    """Manages OpenGL initialization and settings"""
    
    def __init__(self):
        self.background_texture = None
    
    def initialize(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glClearColor(0.1, 0.1, 0.2, 1.0)  # Dark blue background
        glShadeModel(GL_SMOOTH)
        glEnable(GL_TEXTURE_2D)
        self.load_background_texture()
    
    def load_background_texture(self):
        """Load background image as texture"""
        try:
            # Try to load from assets folder
            import os
            possible_paths = [
                "assets/bg_1.png",  # From marble_run root
                "../assets/bg_1.png",  # From src/
                "../../assets/bg_1.png",  # From src/core/
                "../../../bg_1.png",  # Back to original location
                "bg_1.png"  # Direct path fallback
            ]
            
            image_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    image_path = path
                    break
            
            if not image_path:
                print("Background image not found, using gradient background")
                self.background_texture = None
                return
            
            # Load image using PIL
            image = Image.open(image_path)
            image = image.convert("RGB")
            img_data = image.tobytes()
            
            # Generate texture
            self.background_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.background_texture)
            
            # Set texture parameters
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            
            # Load texture data
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
            
            print(f"Background texture loaded successfully from: {image_path}")
        except Exception as e:
            print(f"Failed to load background texture: {e}")
            self.background_texture = None
    
    def setup_2d_projection(self):
        """Setup 2D projection for UI rendering"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT), 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
    
    def setup_3d_projection(self):
        """Setup 3D projection for game rendering"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, glutGet(GLUT_WINDOW_WIDTH)/glutGet(GLUT_WINDOW_HEIGHT), 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
    
    def get_background_texture(self):
        """Get the background texture ID"""
        return self.background_texture
