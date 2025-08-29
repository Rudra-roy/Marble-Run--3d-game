
import math
import time
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# GAME CONSTANTS AND SETTINGS


# Game States
LOADING_SCREEN = 0
MAIN_MENU = 1
HIGH_SCORE = 2
GAME_MODE_SELECTION = 3
GAME_3D = 4

# Physics Constants
GRAVITY = -15.0
MAX_SPEED = 10.0
ACCELERATION = 18.0
JUMP_FORCE = 8.0
GROUND_FRICTION = 0.85
AIR_FRICTION = 0.98
BALL_RADIUS = 0.5
DEATH_Y = -20.0

# Platform Generation
SINGLE_PLAYER_PLATFORMS = 30
MULTIPLAYER_PLATFORMS = 20

# Colors
PLATFORM_COLORS = [
    (0.8, 0.2, 0.2),  # Red
    (0.2, 0.2, 0.8),  # Blue
    (0.8, 0.8, 0.2),  # Yellow
    (0.8, 0.2, 0.8),  # Magenta
    (0.2, 0.8, 0.8),  # Cyan
    (0.8, 0.5, 0.2),  # Orange
]

MOVEMENT_TYPES = ['horizontal', 'tilt', 'forward_back', 'rotate_tilt']


# UTILITY CLASSES

class GameSettings:
    """Game configuration and settings management"""
    
    def __init__(self):
        self.game_mode = 0  # 0 = single player, 1 = multiplayer
        self.sound_volume = 50
        self.text_size = 1.0
        
    def get_game_mode(self):
        return self.game_mode
        
    def set_game_mode(self, mode):
        self.game_mode = mode
        
    def get_sound_volume(self):
        return self.sound_volume
        
    def get_text_size(self):
        return self.text_size

class Vector3:
    """Simple 3D vector class for position and velocity"""
    
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z
        
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
        
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            self.x /= mag
            self.y /= mag
            self.z /= mag


# GAME ENGINE COMPONENTS


class StateManager:
    """Manages game states and transitions between screens"""
    
    def __init__(self):
        self.current_state = LOADING_SCREEN
        self.previous_state = None
        self.transition_start_time = 0
        self.is_transitioning = False
        
    def start_transition(self, new_state, direction=1):
        """Start transition to new state"""
        if not self.is_transitioning:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.transition_start_time = time.time()
            self.is_transitioning = True
            print(f"Transitioning from state {self.previous_state} to {new_state}")
            
    def update(self):
        """Update transition state"""
        if self.is_transitioning:
            elapsed = time.time() - self.transition_start_time
            if elapsed > 0.5:  # Transition duration
                self.is_transitioning = False

class OpenGLManager:
    """Manages OpenGL initialization and rendering setup"""
    
    def __init__(self):
        self.window_width = 1024
        self.window_height = 768
        self.initialized = False
        
    def initialize(self):
        """Initialize OpenGL context and settings"""
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.window_width, self.window_height)
        glutCreateWindow(b"Marble Run - 3D Platformer")
        
        # Enable depth testing and lighting
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        
        # Set lighting parameters
        glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 10.0, 5.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        
        self.initialized = True
        
    def setup_3d_projection(self):
        """Setup 3D projection matrix"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.window_width/self.window_height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
    def setup_2d_projection(self):
        """Setup 2D projection for UI rendering"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.window_width, self.window_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    def setup_viewport_projection(self, width, height):
        """Setup projection for specific viewport"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width/height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

class InputHandler:
    """Handles keyboard input and menu navigation"""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.menu_selections = {
            MAIN_MENU: 0,
            HIGH_SCORE: 0,
            GAME_MODE_SELECTION: 0
        }
        self.keys_pressed = {
            'w': False, 'a': False, 's': False, 'd': False, ' ': False
        }
        self.keys_pressed_p2 = {
            'up': False, 'down': False, 'left': False, 'right': False, 'enter': False
        }
        
    def handle_keyboard(self, key, x, y):
        """Handle regular key presses"""
        key = key.decode('utf-8').lower() if isinstance(key, bytes) else key.lower()
        
        current_state = self.state_manager.current_state
        
        if key == '\x1b':  # ESC key
            self._handle_escape_key(current_state)
        elif key == '\r':  # Enter key
            self._handle_enter_key(current_state)
        elif current_state == GAME_3D:
            if key in self.keys_pressed:
                self.keys_pressed[key] = True
                
    def handle_keyboard_up(self, key, x, y):
        """Handle key releases"""
        key = key.decode('utf-8').lower() if isinstance(key, bytes) else key.lower()
        
        if self.state_manager.current_state == GAME_3D:
            if key in self.keys_pressed:
                self.keys_pressed[key] = False
                
    def handle_special_keys(self, key, x, y):
        """Handle special keys (arrows, function keys)"""
        current_state = self.state_manager.current_state
        
        if current_state in [MAIN_MENU, HIGH_SCORE, GAME_MODE_SELECTION]:
            self._handle_menu_navigation(key, current_state)
        elif current_state == GAME_3D:
            self._handle_game_special_keys(key)
            
    def _handle_escape_key(self, current_state):
        """Handle ESC key for different states"""
        if current_state == GAME_3D:
            self.state_manager.start_transition(MAIN_MENU)
        elif current_state in [HIGH_SCORE, GAME_MODE_SELECTION]:
            self.state_manager.start_transition(MAIN_MENU)
        elif current_state == MAIN_MENU:
            sys.exit(0)
            
    def _handle_enter_key(self, current_state):
        """Handle Enter key for different states"""
        if current_state == MAIN_MENU:
            self._handle_main_menu_enter()
        elif current_state == GAME_MODE_SELECTION:
            self._handle_game_mode_enter()
            
    def _handle_main_menu_enter(self):
        """Handle Enter key in main menu"""
        selection = self.menu_selections[MAIN_MENU]
        
        if selection == 0:  # Start Game
            self.state_manager.start_transition(GAME_MODE_SELECTION)
        elif selection == 1:  # High Score
            self.state_manager.start_transition(HIGH_SCORE)
        elif selection == 2:  # Quit
            sys.exit(0)
            
    def _handle_game_mode_enter(self):
        """Handle Enter key in game mode selection"""
        selection = self.menu_selections[GAME_MODE_SELECTION]
        game_settings.set_game_mode(selection)
        self.state_manager.start_transition(GAME_3D)
        
    def _handle_menu_navigation(self, key, current_state):
        """Handle arrow key navigation in menus"""
        if key == GLUT_KEY_UP:
            if current_state == MAIN_MENU:
                self.menu_selections[MAIN_MENU] = (self.menu_selections[MAIN_MENU] - 1) % 3
            elif current_state == GAME_MODE_SELECTION:
                self.menu_selections[GAME_MODE_SELECTION] = (self.menu_selections[GAME_MODE_SELECTION] - 1) % 2
        elif key == GLUT_KEY_DOWN:
            if current_state == MAIN_MENU:
                self.menu_selections[MAIN_MENU] = (self.menu_selections[MAIN_MENU] + 1) % 3
            elif current_state == GAME_MODE_SELECTION:
                self.menu_selections[GAME_MODE_SELECTION] = (self.menu_selections[GAME_MODE_SELECTION] + 1) % 2
                
    def _handle_game_special_keys(self, key):
        """Handle special keys during gameplay"""
        # Player 2 controls (arrow keys)
        if key == GLUT_KEY_UP:
            self.keys_pressed_p2['up'] = True
        elif key == GLUT_KEY_DOWN:
            self.keys_pressed_p2['down'] = True
        elif key == GLUT_KEY_LEFT:
            self.keys_pressed_p2['left'] = True
        elif key == GLUT_KEY_RIGHT:
            self.keys_pressed_p2['right'] = True


# PLATFORM SYSTEM


class Platform:
    """Represents a single platform with movement and physics"""
    
    def __init__(self, x, y, z, width, height, depth, color, movement_type='static'):
        self.position = Vector3(x, y, z)
        self.base_position = Vector3(x, y, z)
        self.velocity = Vector3(0, 0, 0)
        self.width = width
        self.height = height
        self.depth = depth
        self.color = color
        self.movement_type = movement_type
        
        # Movement-specific properties
        self.move_range = 3.0
        self.move_speed = 1.0
        self.tilt_angle = 0.0
        self.tilt_speed = 1.5
        self.tilt_x = 0.0
        self.tilt_z = 0.0
        
    def update(self, dt, current_time):
        """Update platform movement and position"""
        prev_x = self.position.x
        prev_z = self.position.z
        
        if self.movement_type == 'horizontal':
            # Move side to side
            offset = math.sin(current_time * self.move_speed) * self.move_range
            self.position.x = self.base_position.x + offset
            
        elif self.movement_type == 'forward_back':
            # Move forward and back
            offset = math.sin(current_time * self.move_speed) * self.move_range
            self.position.z = self.base_position.z + offset
            
        elif self.movement_type == 'tilt':
            # Tilt platform
            self.tilt_angle = math.sin(current_time * self.tilt_speed) * 0.3
            
        elif self.movement_type == 'rotate_tilt':
            # Complex tilting on multiple axes
            self.tilt_x = math.sin(current_time * self.tilt_speed) * 0.2
            self.tilt_z = math.cos(current_time * self.tilt_speed * 0.7) * 0.2
            
        # Calculate velocity for ball coupling
        if dt > 0:
            self.velocity.x = (self.position.x - prev_x) / dt
            self.velocity.z = (self.position.z - prev_z) / dt
        else:
            self.velocity.x = 0
            self.velocity.z = 0
            
    def render(self):
        """Render the platform"""
        glPushMatrix()
        
        # Apply position
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Apply tilting
        if self.movement_type in ['tilt', 'rotate_tilt']:
            if hasattr(self, 'tilt_angle'):
                glRotatef(math.degrees(self.tilt_angle), 1, 0, 0)
            if hasattr(self, 'tilt_x') and hasattr(self, 'tilt_z'):
                glRotatef(math.degrees(self.tilt_x), 1, 0, 0)
                glRotatef(math.degrees(self.tilt_z), 0, 0, 1)
        
        # Set color
        glColor3f(*self.color)
        
        # Render cube
        glScalef(self.width, self.height, self.depth)
        glutSolidCube(1.0)
        
        glPopMatrix()
        
    def check_collision(self, ball_x, ball_y, ball_z, ball_radius):
        """Check if ball is colliding with platform"""
        # Simple bounding box collision
        ball_bottom = ball_y - ball_radius
        platform_top = self.position.y + self.height / 2
        
        # Check if ball is within platform bounds and touching top
        if (self.position.x - self.width/2 <= ball_x <= self.position.x + self.width/2 and
            self.position.z - self.depth/2 <= ball_z <= self.position.z + self.depth/2 and
            abs(ball_bottom - platform_top) < 0.1):
            return True
        return False

class PlatformManager:
    """Manages all platforms in the game"""
    
    def __init__(self, is_multiplayer=False):
        self.platforms = []
        self.is_multiplayer = is_multiplayer
        self._generate_platforms()
        
    def _generate_platforms(self):
        """Generate platforms based on game mode"""
        num_platforms = MULTIPLAYER_PLATFORMS if self.is_multiplayer else SINGLE_PLAYER_PLATFORMS
        
        # Starting platform (always static and green)
        start_platform = Platform(0, 0, 0, 8, 0.5, 8, (0.2, 0.8, 0.2), 'static')
        self.platforms.append(start_platform)
        
        # Generate remaining platforms
        for i in range(1, num_platforms + 1):
            # Calculate position
            z_pos = -6 * i
            x_pos = (-1) ** i * (i % 3) * 2
            y_pos = (i // 3) * 0.5
            
            # Choose movement type and color
            movement_type = MOVEMENT_TYPES[(i - 1) % len(MOVEMENT_TYPES)]
            color = PLATFORM_COLORS[(i - 1) % len(PLATFORM_COLORS)]
            
            # Determine size based on difficulty
            if i <= 5:
                width, depth = 6, 6
            elif i <= 15:
                width, depth = 5, 5
            else:
                width, depth = 4, 4
                
            platform = Platform(x_pos, y_pos, z_pos, width, 0.5, depth, color, movement_type)
            
            # Adjust movement parameters based on difficulty
            platform.move_range = 3.0 + (i * 0.1)
            platform.move_speed = 1.0 + (i * 0.05)
            platform.tilt_speed = 1.5 + (i * 0.05)
            
            self.platforms.append(platform)
            
    def update(self, dt):
        """Update all platforms"""
        current_time = time.time()
        for platform in self.platforms:
            platform.update(dt, current_time)
            
    def render(self):
        """Render all platforms"""
        for platform in self.platforms:
            platform.render()
            
    def check_collisions(self, ball_x, ball_y, ball_z, ball_radius):
        """Check collisions with all platforms"""
        for i, platform in enumerate(self.platforms):
            if platform.check_collision(ball_x, ball_y, ball_z, ball_radius):
                return i, platform
        return None, None


# PLAYER SYSTEM

class Player:
    """Represents a player ball with physics"""
    
    def __init__(self, start_x=0, start_y=1, start_z=0):
        self.position = Vector3(start_x, start_y, start_z)
        self.velocity = Vector3(0, 0, 0)
        self.radius = BALL_RADIUS
        self.on_ground = False
        self.score = 0
        self.platforms_reached = set()
        self.game_over = False
        
    def update_physics(self, dt, input_handler, keys_dict):
        """Update player physics"""
        if self.game_over:
            return
            
        # Apply gravity
        self.velocity.y += GRAVITY * dt
        
        # Handle input
        if keys_dict.get('w', False):
            self.velocity.z -= ACCELERATION * dt
        if keys_dict.get('s', False):
            self.velocity.z += ACCELERATION * dt
        if keys_dict.get('a', False):
            self.velocity.x -= ACCELERATION * dt
        if keys_dict.get('d', False):
            self.velocity.x += ACCELERATION * dt
            
        # Jumping
        if keys_dict.get(' ', False) and self.on_ground:
            self.velocity.y = JUMP_FORCE
            self.on_ground = False
            
        # Apply friction
        if self.on_ground:
            self.velocity.x *= GROUND_FRICTION
            self.velocity.z *= GROUND_FRICTION
        else:
            self.velocity.x *= AIR_FRICTION
            self.velocity.z *= AIR_FRICTION
            
        # Limit horizontal speed
        horizontal_speed = math.sqrt(self.velocity.x**2 + self.velocity.z**2)
        if horizontal_speed > MAX_SPEED:
            scale = MAX_SPEED / horizontal_speed
            self.velocity.x *= scale
            self.velocity.z *= scale
            
        # Update position
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt
        self.position.z += self.velocity.z * dt
        
        # Check for death
        if self.position.y < DEATH_Y:
            self.game_over = True
            
    def handle_platform_collision(self, platform_manager):
        """Handle collision with platforms"""
        platform_index, platform = platform_manager.check_collisions(
            self.position.x, self.position.y, self.position.z, self.radius
        )
        
        if platform is not None:
            # Land on platform
            self.position.y = platform.position.y + platform.height/2 + self.radius
            if self.velocity.y < 0:
                self.velocity.y = 0
            self.on_ground = True
            
            # Apply platform movement (80% coupling)
            self.position.x += platform.velocity.x * 0.8 * (1/60)  # Assuming 60 FPS
            self.position.z += platform.velocity.z * 0.8 * (1/60)
            
            # Update score
            if platform_index not in self.platforms_reached:
                self.platforms_reached.add(platform_index)
                points = (platform_index + 1) * 100
                self.score += points
                
                # Check for completion bonus
                if len(self.platforms_reached) == len(platform_manager.platforms):
                    self.score += 1000  # Completion bonus
        else:
            self.on_ground = False
            
    def render(self):
        """Render the player ball"""
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glColor3f(1.0, 1.0, 1.0)  # White ball
        glutSolidSphere(self.radius, 16, 16)
        glPopMatrix()


# SCREEN CLASSES


class Screen:
    """Base screen class"""
    
    def __init__(self, state_manager, opengl_manager, input_handler):
        self.state_manager = state_manager
        self.opengl_manager = opengl_manager
        self.input_handler = input_handler
        
    def render(self):
        """Render the screen - to be overridden"""
        pass
        
    def update(self, dt):
        """Update screen logic - to be overridden"""
        pass

class LoadingScreen(Screen):
    """Loading screen with progress animation"""
    
    def render(self):
        self.opengl_manager.setup_2d_projection()
        glClearColor(0.1, 0.1, 0.2, 1.0)
        
        # Simple loading text
        glColor3f(1.0, 1.0, 1.0)
        text = "Loading..."
        glRasterPos2f(400, 300)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
            
        # After 2 seconds, transition to main menu
        if time.time() > 2:
            self.state_manager.start_transition(MAIN_MENU)

class MainMenuScreen(Screen):
    """Main menu with navigation"""
    
    def render(self):
        self.opengl_manager.setup_2d_projection()
        glClearColor(0.2, 0.3, 0.5, 1.0)
        
        # Title
        glColor3f(1.0, 0.8, 0.2)
        title = "MARBLE RUN"
        glRasterPos2f(400, 200)
        for char in title:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
            
        # Menu items
        menu_items = ["Start Game", "High Score", "Quit"]
        selection = self.input_handler.menu_selections[MAIN_MENU]
        
        for i, item in enumerate(menu_items):
            if i == selection:
                glColor3f(1.0, 1.0, 0.0)  # Yellow for selected
            else:
                glColor3f(0.8, 0.8, 0.8)  # Gray for unselected
                
            glRasterPos2f(400, 300 + i * 40)
            for char in item:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

class HighScoreScreen(Screen):
    """High score display screen"""
    
    def render(self):
        self.opengl_manager.setup_2d_projection()
        glClearColor(0.2, 0.3, 0.5, 1.0)
        
        # Title
        glColor3f(1.0, 0.8, 0.2)
        title = "HIGH SCORES"
        glRasterPos2f(400, 200)
        for char in title:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
            
        # Display placeholder scores
        glColor3f(0.9, 0.9, 0.9)
        scores = [
            "Single Player High: 0",
            "Multiplayer P1 High: 0",
            "Multiplayer P2 High: 0",
            "",
            "Press ESC to go back"
        ]
        
        for i, score_line in enumerate(scores):
            glRasterPos2f(350, 300 + i * 30)
            for char in score_line:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

class GameModeSelectionScreen(Screen):
    """Game mode selection screen"""
    
    def render(self):
        self.opengl_manager.setup_2d_projection()
        glClearColor(0.2, 0.3, 0.5, 1.0)
        
        # Title
        glColor3f(1.0, 0.8, 0.2)
        title = "SELECT GAME MODE"
        glRasterPos2f(400, 200)
        for char in title:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
            
        # Mode options
        modes = ["Single Player (30 Platforms)", "Multiplayer VS (20 Platforms)"]
        selection = self.input_handler.menu_selections[GAME_MODE_SELECTION]
        
        for i, mode in enumerate(modes):
            if i == selection:
                glColor3f(1.0, 1.0, 0.0)  # Yellow for selected
            else:
                glColor3f(0.8, 0.8, 0.8)  # Gray for unselected
                
            glRasterPos2f(300, 300 + i * 50)
            for char in mode:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

class Game3DScreen(Screen):
    """Main 3D gameplay screen"""
    
    def __init__(self, state_manager, opengl_manager, input_handler):
        super().__init__(state_manager, opengl_manager, input_handler)
        self.is_multiplayer = False
        self.platform_manager = None
        self.player1 = Player(0, 1, 0)
        self.player2 = Player(0, 1, 0)
        self.camera_distance = 15.0
        self.camera_height = 8.0
        self.game_ended = False
        self.winner = 0
        self.winner_reason = ""
        self.last_time = time.time()
        
    def initialize_game(self):
        """Initialize/reset game state"""
        self.is_multiplayer = (game_settings.get_game_mode() == 1)
        self.platform_manager = PlatformManager(self.is_multiplayer)
        self.player1 = Player(0, 1, 0)
        self.player2 = Player(0, 1, 0)
        self.game_ended = False
        self.winner = 0
        self.winner_reason = ""
        
    def update(self, dt):
        """Update game logic"""
        if not self.platform_manager:
            self.initialize_game()
            
        # Update platforms
        self.platform_manager.update(dt)
        
        # Update players
        if not self.game_ended:
            # Player 1 controls
            self.player1.update_physics(dt, self.input_handler, self.input_handler.keys_pressed)
            self.player1.handle_platform_collision(self.platform_manager)
            
            # Player 2 controls (if multiplayer)
            if self.is_multiplayer:
                # Convert arrow keys to WASD format for player 2
                p2_keys = {
                    'w': self.input_handler.keys_pressed_p2.get('up', False),
                    's': self.input_handler.keys_pressed_p2.get('down', False),
                    'a': self.input_handler.keys_pressed_p2.get('left', False),
                    'd': self.input_handler.keys_pressed_p2.get('right', False),
                    ' ': self.input_handler.keys_pressed_p2.get('enter', False)
                }
                self.player2.update_physics(dt, self.input_handler, p2_keys)
                self.player2.handle_platform_collision(self.platform_manager)
                
                # Check for VS game end
                if self.player1.game_over or self.player2.game_over:
                    self._determine_vs_winner()
                    
    def _determine_vs_winner(self):
        """Determine winner in VS mode"""
        if self.game_ended:
            return
            
        self.game_ended = True
        score_diff = abs(self.player1.score - self.player2.score)
        
        if self.player1.game_over:
            # Player 1 fell
            if self.player1.score > self.player2.score and score_diff > 100:
                self.winner = 1
                self.winner_reason = f"P1 WINS! Fell with {score_diff} point lead!"
            else:
                self.winner = 2
                self.winner_reason = f"P2 WINS! P1 fell (score diff: {score_diff})"
        else:
            # Player 2 fell
            if self.player2.score > self.player1.score and score_diff > 100:
                self.winner = 2
                self.winner_reason = f"P2 WINS! Fell with {score_diff} point lead!"
            else:
                self.winner = 1
                self.winner_reason = f"P1 WINS! P2 fell (score diff: {score_diff})"
        
    def render(self):
        """Render the 3D game"""
        glClearColor(0.3, 0.6, 1.0, 1.0)  # Sky blue
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if not self.platform_manager:
            return
            
        if not self.is_multiplayer:
            self._render_single_player()
        else:
            self._render_multiplayer()
            
    def _render_single_player(self):
        """Render single player view"""
        self.opengl_manager.setup_3d_projection()
        
        # Setup camera
        glLoadIdentity()
        camera_x = self.player1.position.x
        camera_y = self.player1.position.y + self.camera_height
        camera_z = self.player1.position.z + self.camera_distance
        
        gluLookAt(camera_x, camera_y, camera_z,
                  self.player1.position.x, self.player1.position.y, self.player1.position.z,
                  0, 1, 0)
        
        # Render scene
        self.platform_manager.render()
        self.player1.render()
        
        # Render UI
        self._render_ui_single()
        
    def _render_multiplayer(self):
        """Render split-screen multiplayer"""
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        half_width = window_width // 2
        
        # Player 1 viewport (left)
        glViewport(0, 0, half_width, window_height)
        self.opengl_manager.setup_viewport_projection(half_width, window_height)
        self._render_player_view(self.player1)
        
        # Player 2 viewport (right)
        glViewport(half_width, 0, half_width, window_height)
        self.opengl_manager.setup_viewport_projection(half_width, window_height)
        self._render_player_view(self.player2)
        
        # Render divider
        self._render_multiplayer_divider(window_width, window_height)
        
    def _render_player_view(self, player):
        """Render view for specific player"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Setup camera for this player
        camera_x = player.position.x
        camera_y = player.position.y + self.camera_height
        camera_z = player.position.z + self.camera_distance
        
        gluLookAt(camera_x, camera_y, camera_z,
                  player.position.x, player.position.y, player.position.z,
                  0, 1, 0)
        
        # Render scene
        self.platform_manager.render()
        self.player1.render()
        if self.is_multiplayer:
            self.player2.render()
            
    def _render_multiplayer_divider(self, window_width, window_height):
        """Render divider between player views"""
        glViewport(0, 0, window_width, window_height)
        self.opengl_manager.setup_2d_projection()
        
        # Draw divider line
        divider_x = window_width // 2
        glColor3f(1.0, 1.0, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(divider_x - 2, 0)
        glVertex2f(divider_x + 2, 0)
        glVertex2f(divider_x + 2, window_height)
        glVertex2f(divider_x - 2, window_height)
        glEnd()
        
        # VS text
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(divider_x - 10, window_height // 2)
        for char in "VS":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
            
    def _render_ui_single(self):
        """Render single player UI"""
        self.opengl_manager.setup_2d_projection()
        
        # Score
        glColor3f(1.0, 1.0, 0.0)
        score_text = f"Score: {self.player1.score}"
        glRasterPos2f(20, 30)
        for char in score_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
            
        # Controls
        glColor3f(1.0, 1.0, 1.0)
        controls_text = "WASD: Move, Space: Jump, R: Restart, ESC: Menu"
        glRasterPos2f(20, glutGet(GLUT_WINDOW_HEIGHT) - 30)
        for char in controls_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(char))
            
        # Game over
        if self.player1.game_over:
            glColor3f(1.0, 0.2, 0.2)
            game_over_text = "GAME OVER! Press R to restart"
            glRasterPos2f(300, 300)
            for char in game_over_text:
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))


# MAIN GAME ENGINE


class GameEngine:
    """Main game engine that orchestrates everything"""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.opengl_manager = OpenGLManager()
        self.input_handler = InputHandler(self.state_manager)
        
        # Initialize screens
        self.screens = {
            LOADING_SCREEN: LoadingScreen(self.state_manager, self.opengl_manager, self.input_handler),
            MAIN_MENU: MainMenuScreen(self.state_manager, self.opengl_manager, self.input_handler),
            HIGH_SCORE: HighScoreScreen(self.state_manager, self.opengl_manager, self.input_handler),
            GAME_MODE_SELECTION: GameModeSelectionScreen(self.state_manager, self.opengl_manager, self.input_handler),
            GAME_3D: Game3DScreen(self.state_manager, self.opengl_manager, self.input_handler)
        }
        
        self.last_time = time.time()
        
    def initialize(self):
        """Initialize the game engine"""
        self.opengl_manager.initialize()
        
        # Set GLUT callbacks
        glutDisplayFunc(self.render)
        glutIdleFunc(self.update)
        glutKeyboardFunc(self.input_handler.handle_keyboard)
        glutKeyboardUpFunc(self.input_handler.handle_keyboard_up)
        glutSpecialFunc(self.input_handler.handle_special_keys)
        
    def update(self):
        """Main update loop"""
        current_time = time.time()
        dt = min(current_time - self.last_time, 0.1)  # Cap delta time
        self.last_time = current_time
        
        # Update state manager
        self.state_manager.update()
        
        # Update current screen
        current_screen = self.screens.get(self.state_manager.current_state)
        if current_screen and hasattr(current_screen, 'update'):
            current_screen.update(dt)
            
        # Trigger redraw
        glutPostRedisplay()
        
    def render(self):
        """Main render function"""
        # Render current screen
        current_screen = self.screens.get(self.state_manager.current_state)
        if current_screen:
            current_screen.render()
            
        # Swap buffers
        glutSwapBuffers()
        
    def run(self):
        """Start the main game loop"""
        print("Starting Marble Run...")
        print("Controls: WASD + Space (Player 1), Arrow Keys + Enter (Player 2)")
        print("Navigate menus with arrow keys, Enter to select, ESC to go back")
        
        self.initialize()
        glutMainLoop()


# Global game settings instance
game_settings = GameSettings()

def main():
    """Main entry point"""
    try:
        # Create and run game engine
        game_engine = GameEngine()
        game_engine.run()
        
    except Exception as e:
        print(f"Error starting game: {e}")
        print("Make sure you have PyOpenGL installed: pip install PyOpenGL PyOpenGL-accelerate")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
