"""
Core game engine for Marble Run.
Manages game states, initialization, and main loop.
"""

import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from core.state_manager import StateManager, LOADING_SCREEN, MAIN_MENU, OPTIONS_MENU, GAME_MODE_SELECTION, GAME_3D
from core.opengl_manager import OpenGLManager
from core.input_handler import InputHandler
from core.settings import GameSettings
from screens.loading_screen import LoadingScreen
from screens.main_menu_screen import MainMenuScreen
from screens.options_menu_screen import OptionsMenuScreen
from screens.game_mode_selection_screen import GameModeSelectionScreen
from screens.game_3d_screen import Game3DScreen

class GameEngine:
    """Main game engine that orchestrates all game systems"""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.opengl_manager = OpenGLManager()
        self.input_handler = InputHandler(self.state_manager)
        self.settings = GameSettings()
        self.loading_start_time = 0
        
        # Initialize screens
        self.screens = {}
        self._initialize_screens()
        
    def _initialize_screens(self):
        """Initialize all game screens"""
        self.screens[LOADING_SCREEN] = LoadingScreen(
            self.state_manager, self.opengl_manager, self.input_handler)
        self.screens[MAIN_MENU] = MainMenuScreen(
            self.state_manager, self.opengl_manager, self.input_handler)
        self.screens[OPTIONS_MENU] = OptionsMenuScreen(
            self.state_manager, self.opengl_manager, self.input_handler)
        self.screens[GAME_MODE_SELECTION] = GameModeSelectionScreen(
            self.state_manager, self.opengl_manager, self.input_handler)
        self.screens[GAME_3D] = Game3DScreen(
            self.state_manager, self.opengl_manager, self.input_handler)
        
        # Set screens in state manager
        self.state_manager.set_screens(self.screens)
        
    def initialize(self):
        """Initialize the game engine and all subsystems"""
        # Initialize GLUT
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(1024, 768)
        glutInitWindowPosition(100, 100)
        glutCreateWindow(b"Marble Run")
        
        # Initialize OpenGL
        self.opengl_manager.initialize()
        
        # Set loading start time
        self.loading_start_time = time.time()
        self.state_manager.set_loading_start_time(self.loading_start_time)
        
        # Register callbacks
        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshape)
        glutKeyboardFunc(self.input_handler.keyboard)
        glutKeyboardUpFunc(self.input_handler.keyboard_up)
        glutSpecialFunc(self.input_handler.special_keys)
        try:
            # Register special key release if available
            glutSpecialUpFunc(self.input_handler.special_keys_up)
        except Exception:
            pass
        glutTimerFunc(0, self.timer, 0)
        
        print("Marble Run initialized successfully!")
        print("Loading screen will show for 3 seconds...")
    
    def display(self):
        """Main display function"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Update and render current state
        self.state_manager.update()
        self.state_manager.render()
        
        glutSwapBuffers()
    
    def reshape(self, width, height):
        """Handle window reshape"""
        glViewport(0, 0, width, height)
    
    def timer(self, value):
        """Timer function for animation"""
        glutPostRedisplay()
        glutTimerFunc(16, self.timer, 0)  # ~60 FPS
    
    def run(self):
        """Start the game engine"""
        self.initialize()
        glutMainLoop()
