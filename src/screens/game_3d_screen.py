"""
Simple Marble Run Game - Infinite Platform
Just a ball on an infinite platform that can be controlled with WASD and spacebar.
"""

import time
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from screens.base_screen import BaseScreen

class Game3DScreen(BaseScreen):
    """Simple 3D game with ball on infinite platform"""
    
    def __init__(self, state_manager, opengl_manager, input_handler):
        super().__init__(state_manager, opengl_manager, input_handler)
        
        # Ball properties
        self.ball_x = 0.0
        self.ball_y = 1.0  # Start above the platform
        self.ball_z = 0.0
        self.ball_vel_x = 0.0
        self.ball_vel_y = 0.0
        self.ball_vel_z = 0.0
        self.ball_radius = 0.5
        
        # Platform properties - Fall Guys style platforms
        self.platforms = self._create_platforms()
        
        # Game state
        self.game_over = False
        self.death_y = -20.0  # If ball falls below this, game over
        
        # Physics constants
        self.gravity = -15.0
        self.ground_friction = 0.85
        self.air_friction = 0.98
        self.move_speed = 8.0
        self.jump_force = 10.0
        
        # Camera
        self.camera_distance = 10.0
        self.camera_height = 5.0
        
        # Input state
        self.keys_pressed = {
            'w': False, 'a': False, 's': False, 'd': False,
            ' ': False  # Spacebar for jumping
        }
        
        # Timing
        self.last_time = time.time()
        
    def _create_platforms(self):
        """Create Fall Guys style platforms"""
        platforms = []
        
        # Starting platform
        platforms.append({
            'x': 0, 'y': 0, 'z': 0,
            'width': 8, 'height': 0.5, 'depth': 8,
            'color': (0.2, 0.8, 0.2)  # Green
        })
        
        # Platform 2 - jump forward
        platforms.append({
            'x': 0, 'y': 0, 'z': -12,
            'width': 6, 'height': 0.5, 'depth': 6,
            'color': (0.8, 0.2, 0.2)  # Red
        })
        
        # Platform 3 - higher up
        platforms.append({
            'x': -5, 'y': 2, 'z': -20,
            'width': 4, 'height': 0.5, 'depth': 4,
            'color': (0.2, 0.2, 0.8)  # Blue
        })
        
        # Platform 4 - to the right
        platforms.append({
            'x': 3, 'y': 3, 'z': -28,
            'width': 5, 'height': 0.5, 'depth': 5,
            'color': (0.8, 0.8, 0.2)  # Yellow
        })
        
        # Platform 5 - final platform
        platforms.append({
            'x': 0, 'y': 5, 'z': -38,
            'width': 6, 'height': 0.5, 'depth': 6,
            'color': (0.8, 0.2, 0.8)  # Magenta
        })
        
        return platforms
        
    def render(self):
        """Render the 3D game space"""
        current_time = time.time()
        dt = min(current_time - self.last_time, 0.1)  # Cap delta time
        self.last_time = current_time
        
        # Update game logic
        self._update_game(dt)
        
        # Setup 3D rendering
        self.opengl_manager.setup_3d_projection()
        self._setup_lighting()
        
        # Clear background
        glClearColor(0.3, 0.6, 1.0, 1.0)  # Sky blue
        
        # Update camera to follow ball
        self._update_camera()
        
        # Render game objects
        self._render_scene()
        
        # Render UI overlays in 2D
        self.opengl_manager.setup_2d_projection()
        self._render_ui()
        
    def _update_game(self, dt):
        """Update game physics and logic"""
        # Handle input
        self._handle_input(dt)
        
        # Apply physics
        self._update_physics(dt)
        
    def _handle_input(self, dt):
        """Handle player input"""
        # Movement forces
        if self.keys_pressed['w']:
            self.ball_vel_z -= self.move_speed * dt
        if self.keys_pressed['s']:
            self.ball_vel_z += self.move_speed * dt
        if self.keys_pressed['a']:
            self.ball_vel_x -= self.move_speed * dt
        if self.keys_pressed['d']:
            self.ball_vel_x += self.move_speed * dt
            
        # Jumping
        if self.keys_pressed[' '] and self._is_on_ground():
            self.ball_vel_y = self.jump_force
            
    def _update_physics(self, dt):
        """Update ball physics"""
        if self.game_over:
            return
            
        # Apply gravity
        self.ball_vel_y += self.gravity * dt
        
        # Apply friction
        if self._is_on_ground():
            self.ball_vel_x *= self.ground_friction
            self.ball_vel_z *= self.ground_friction
        else:
            self.ball_vel_x *= self.air_friction
            self.ball_vel_z *= self.air_friction
            
        # Update position
        self.ball_x += self.ball_vel_x * dt
        self.ball_y += self.ball_vel_y * dt
        self.ball_z += self.ball_vel_z * dt
        
        # Platform collision
        self._handle_platform_collision()
        
        # Check for death (falling off platforms)
        if self.ball_y < self.death_y:
            self.game_over = True
            print("Game Over! Ball fell off the platforms!")
            
    def _handle_platform_collision(self):
        """Handle collision with platforms"""
        for platform in self.platforms:
            # Check if ball is above platform
            px, py, pz = platform['x'], platform['y'], platform['z']
            pw, ph, pd = platform['width'], platform['height'], platform['depth']
            
            # Check if ball is within platform bounds horizontally
            if (px - pw/2 <= self.ball_x <= px + pw/2 and
                pz - pd/2 <= self.ball_z <= pz + pd/2):
                
                # Check if ball is colliding from above
                platform_top = py + ph/2
                ball_bottom = self.ball_y - self.ball_radius
                
                if (ball_bottom <= platform_top and 
                    ball_bottom >= platform_top - 1.0 and  # Some tolerance
                    self.ball_vel_y <= 0):  # Only when falling
                    
                    self.ball_y = platform_top + self.ball_radius
                    self.ball_vel_y = 0
                    return  # Stop checking other platforms
                
    def _is_on_ground(self):
        """Check if ball is on any platform"""
        for platform in self.platforms:
            px, py, pz = platform['x'], platform['y'], platform['z']
            pw, ph, pd = platform['width'], platform['height'], platform['depth']
            
            # Check if ball is within platform bounds horizontally
            if (px - pw/2 <= self.ball_x <= px + pw/2 and
                pz - pd/2 <= self.ball_z <= pz + pd/2):
                
                # Check if ball is on top of platform
                platform_top = py + ph/2
                ball_bottom = self.ball_y - self.ball_radius
                
                if abs(ball_bottom - platform_top) < 0.1:
                    return True
        return False
        
    def _update_camera(self):
        """Update camera to follow the ball"""
        glLoadIdentity()
        
        # Camera follows ball
        camera_x = self.ball_x
        camera_y = self.ball_y + self.camera_height
        camera_z = self.ball_z + self.camera_distance
        
        gluLookAt(camera_x, camera_y, camera_z,  # Camera position
                  self.ball_x, self.ball_y, self.ball_z,  # Look at ball
                  0, 1, 0)  # Up vector
                  
    def _setup_lighting(self):
        """Setup basic lighting"""
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        
        # Light position
        light_pos = [10.0, 10.0, 10.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        
        # Light properties
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        
    def _render_scene(self):
        """Render the 3D scene"""
        # Draw the infinite platform
        self._draw_platform()
        
        # Draw the ball
        self._draw_ball()
        
    def _draw_platform(self):
        """Draw Fall Guys style platforms"""
        glEnable(GL_LIGHTING)
        
        # Draw all platforms
        for i, platform in enumerate(self.platforms):
            px, py, pz = platform['x'], platform['y'], platform['z']
            pw, ph, pd = platform['width'], platform['height'], platform['depth']
            color = platform['color']
            
            glPushMatrix()
            glTranslatef(px, py, pz)
            
            # Set platform material
            glMaterialfv(GL_FRONT, GL_AMBIENT, [color[0]*0.3, color[1]*0.3, color[2]*0.3, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [color[0], color[1], color[2], 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 20.0)
            
            # Draw platform as a box
            glScalef(pw, ph, pd)
            self._draw_cube()
            
            glPopMatrix()
            
    def _draw_cube(self):
        """Draw a unit cube"""
        glBegin(GL_QUADS)
        
        # Front face
        glNormal3f(0, 0, 1)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        
        # Back face
        glNormal3f(0, 0, -1)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        
        # Top face
        glNormal3f(0, 1, 0)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        
        # Bottom face
        glNormal3f(0, -1, 0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        # Right face
        glNormal3f(1, 0, 0)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        
        # Left face
        glNormal3f(-1, 0, 0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        
        glEnd()
        
    def _draw_ball(self):
        """Draw the ball"""
        glPushMatrix()
        glTranslatef(self.ball_x, self.ball_y, self.ball_z)
        
        # Set ball material
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.8, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.4, 0.4, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.8, 0.8, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
        
        # Draw sphere
        quadric = gluNewQuadric()
        gluSphere(quadric, self.ball_radius, 20, 20)
        gluDeleteQuadric(quadric)
        
        glPopMatrix()
        
    def _render_ui(self):
        """Render UI elements"""
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        
        if self.game_over:
            # Game Over screen
            glColor3f(1.0, 0.0, 0.0)  # Red
            game_over_text = "GAME OVER!"
            glRasterPos2f(window_width//2 - 50, window_height//2)
            for char in game_over_text:
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
                
            glColor3f(1.0, 1.0, 1.0)  # White
            restart_text = "Press R to restart, ESC to quit"
            glRasterPos2f(window_width//2 - 100, window_height//2 - 30)
            for char in restart_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
        else:
            # Normal game UI
            glColor3f(1.0, 1.0, 1.0)
            controls_text = "Controls: WASD to move, SPACE to jump, ESC to quit"
            glRasterPos2f(20, window_height - 20)
            for char in controls_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
                
            # Draw ball position
            pos_text = f"Position: X={self.ball_x:.1f}, Y={self.ball_y:.1f}, Z={self.ball_z:.1f}"
            glRasterPos2f(20, window_height - 40)
            for char in pos_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
            
    def handle_key_press(self, key):
        """Handle key press events"""
        key = key.lower()
        
        # Handle restart
        if key == 'r' and self.game_over:
            self._restart_game()
            return
            
        if key in self.keys_pressed and not self.game_over:
            self.keys_pressed[key] = True
            
    def handle_key_release(self, key):
        """Handle key release events"""
        key = key.lower()
        if key in self.keys_pressed and not self.game_over:
            self.keys_pressed[key] = False
            
    def _restart_game(self):
        """Restart the game"""
        self.ball_x = 0.0
        self.ball_y = 1.0
        self.ball_z = 0.0
        self.ball_vel_x = 0.0
        self.ball_vel_y = 0.0
        self.ball_vel_z = 0.0
        self.game_over = False
        print("Game restarted!")
