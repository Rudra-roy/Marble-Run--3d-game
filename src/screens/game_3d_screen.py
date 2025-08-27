"""
Complete Fall Guys-Style Marble Run Game
Fixed and enhanced version with all features implemented
"""

# game_3d_screen.py - COMPLETE VERSION
"""
3D game screen implementation - Fall Guys style platform game.
"""

import time
import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from screens.base_screen import BaseScreen
from ui.renderer import UIRenderer
from core.settings import game_settings
from game.physics import Ball
from game.platforms import LevelGenerator
from game.renderer import Renderer3D
from game.particles import ParticleSystem

class Game3DScreen(BaseScreen):
    """3D Fall Guys style platform game"""
    
    def __init__(self, state_manager, opengl_manager, input_handler):
        super().__init__(state_manager, opengl_manager, input_handler)
        
        # Initialize level first
        self.level_generator = LevelGenerator()
        self.level_generator.generate_starting_platform()
        
        # Get starting platform to position ball correctly
        starting_platform = self.level_generator.platforms[0]
        ball_spawn_y = starting_platform.y + starting_platform.height/2 + 0.5
        
        # Game objects - Single player ball
        self.ball = Ball(0, ball_spawn_y, 0, player_id=0)
        
        # Particle system for visual effects
        self.particle_system = ParticleSystem()
        
        # Track previous ball position for effects
        self.prev_ball_pos = self.ball.get_position()
        
        # Game state
        self.score = 0
        self.high_score = 0  # Track high score
        self.game_over = False
        self.camera_z = 8.0
        self.camera_follow_speed = 2.0
        self.game_time = 0.0
        
        # Checkpoint system
        self.last_checkpoint_z = 0
        self.checkpoint_interval = -20  # Every 20 units forward
        
        # Input state
        self.keys_pressed = {
            'w': False, 'a': False, 's': False, 'd': False,
            ' ': False  # Spacebar for jumping
        }
        
        # Timing
        self.last_time = time.time()
        
        # Generate additional platforms
        self.level_generator.generate_next_platforms(8)
        
    def render(self):
        """Render the 3D game space"""
        current_time = time.time()
        dt = min(current_time - self.last_time, 0.1)  # Cap delta time
        self.last_time = current_time
        
        # Update game logic
        self._update_game(dt)
        
        # Setup 3D rendering
        self.opengl_manager.setup_3d_projection()
        Renderer3D.setup_lighting()
        
        # Draw skybox
        try:
            Renderer3D.draw_skybox()
        except Exception as e:
            # If skybox fails, just clear with a simple color
            glClearColor(0.3, 0.6, 1.0, 1.0)
        
        # Update camera to follow ball
        self._update_camera()
        
        # Render game objects
        self._render_scene()
        
        # Render UI overlays
        Renderer3D.disable_lighting()
        self._render_ui()
    
    def _update_game(self, dt):
        """Update game logic"""
        if self.game_over:
            return
        
        self.game_time += dt
        
        # Apply input forces to ball
        force_x = 0
        force_z = 0
        
        if self.keys_pressed['w']:
            force_z -= self.ball.move_force
        if self.keys_pressed['s']:
            force_z += self.ball.move_force
        if self.keys_pressed['a']:
            force_x -= self.ball.move_force
        if self.keys_pressed['d']:
            force_x += self.ball.move_force
        
        # Handle jumping (spacebar)
        if self.keys_pressed[' ']:
            if self.ball.jump():
                # Add jump particles
                ball_pos = self.ball.get_position()
                self.particle_system.add_platform_hit(ball_pos[0], ball_pos[1] - 0.5, ball_pos[2], 
                                                      color=(0.5, 0.8, 1.0))
                # Reset spacebar to prevent continuous jumping
                self.keys_pressed[' '] = False
        
        self.ball.apply_force(force_x, force_z, dt)
        
        # Update ball physics
        platforms = self.level_generator.get_platforms()
        old_on_ground = self.ball.on_ground
        self.ball.update(dt, platforms)
        
        # Check obstacle collisions
        obstacles = self.level_generator.get_obstacles()
        for obstacle in obstacles:
            if hasattr(obstacle, 'check_collision'):
                if obstacle.check_collision(self.ball.get_position(), self.ball.radius):
                    # Different obstacle effects
                    if hasattr(obstacle, '__class__'):
                        if obstacle.__class__.__name__ == 'Hammer':
                            # Hammer knocks the ball back
                            self.ball.vx = -self.ball.vx * 2
                            self.ball.vz = -self.ball.vz * 2
                            self.ball.vy = 5.0
                            self.ball.stun(1.0)
                            self.particle_system.add_explosion(self.ball.x, self.ball.y, self.ball.z, 
                                                              color=(1.0, 0.2, 0.2))
                        elif obstacle.__class__.__name__ == 'SpinningBar':
                            # Spinning bar bounces the ball up
                            self.ball.vy = 8.0
                            self.ball.stun(0.5)
                            self.particle_system.add_explosion(self.ball.x, self.ball.y, self.ball.z, 
                                                              color=(0.8, 0.3, 0.8))
            
            # Handle push walls
            if hasattr(obstacle, '__class__') and obstacle.__class__.__name__ == 'PushWall':
                push_force = obstacle.check_collision(self.ball.get_position(), self.ball.radius)
                if push_force[0] != 0 or push_force[1] != 0:
                    self.ball.vx += push_force[0]
                    self.ball.vz += push_force[1]
        
        # Add particle effects
        ball_pos = self.ball.get_position()
        
        # Landing effect
        if not old_on_ground and self.ball.on_ground:
            self.particle_system.add_platform_hit(ball_pos[0], ball_pos[1], ball_pos[2])
        
        # Movement trail
        if self.ball.is_alive():
            speed = math.sqrt(self.ball.vx**2 + self.ball.vz**2)
            if speed > 2.0:  # Only show trail when moving fast
                self.particle_system.add_trail(ball_pos[0], ball_pos[1], ball_pos[2], 
                                               self.ball.get_color())
        
        # Update particle system
        self.particle_system.update(dt)
        
        # Update platforms (for animations and movement)
        self.level_generator.update_platforms(dt)
        
        # Check if ball died
        if not self.ball.is_alive():
            self.game_over = True
            # Update high score
            if self.score > self.high_score:
                self.high_score = self.score
        
        # Update score based on platforms passed
        ball_pos = self.ball.get_position()
        self.score = self.level_generator.check_platform_passed(ball_pos[2], self.score)
        
        # Bonus points for reaching checkpoints
        if ball_pos[2] < self.last_checkpoint_z + self.checkpoint_interval:
            self.last_checkpoint_z = ball_pos[2]
            self.score += 5  # Checkpoint bonus
            # Celebration particles
            self.particle_system.add_explosion(ball_pos[0], ball_pos[1] + 2, ball_pos[2], 
                                              color=(1.0, 1.0, 0.3), count=20)
        
        # Generate more platforms if needed
        if self.level_generator.should_generate_more(ball_pos[2]):
            self.level_generator.generate_next_platforms(5)
        
        # Cleanup distant platforms
        self.level_generator.cleanup_distant_platforms(ball_pos[2])
    
    def _update_camera(self):
        """Update camera to follow the ball"""
        ball_pos = self.ball.get_position()
        
        # Smoothly follow ball
        target_z = ball_pos[2] + 8.0
        self.camera_z += (target_z - self.camera_z) * self.camera_follow_speed * 0.016  # Assume ~60fps
        
        # Dynamic camera based on game state
        if self.ball.stunned:
            # Shake camera when stunned
            shake_x = random.uniform(-0.2, 0.2)
            shake_y = random.uniform(-0.2, 0.2)
        else:
            shake_x = shake_y = 0
        
        # Set up camera
        camera_x = ball_pos[0] * 0.3 + shake_x  # Slight horizontal following
        camera_y = 5.0 + ball_pos[1] * 0.2 + shake_y  # Slight vertical following
        
        gluLookAt(camera_x, camera_y, self.camera_z,  # Eye position
                  ball_pos[0], ball_pos[1], ball_pos[2],  # Look at ball
                  0, 1, 0)  # Up vector
    
    def _render_scene(self):
        """Render the game scene"""
        # Render platforms
        platforms = self.level_generator.get_platforms()
        for platform in platforms:
            platform.render()
        
        # Render obstacles
        obstacles = self.level_generator.get_obstacles()
        for obstacle in obstacles:
            obstacle.render()
        
        # Render player ball with shadow
        ball_pos = self.ball.get_position()
        
        # Draw shadow
        glDisable(GL_LIGHTING)
        glColor4f(0.0, 0.0, 0.0, 0.3)
        glPushMatrix()
        glTranslatef(ball_pos[0], -10, ball_pos[2])  # Project shadow on ground
        glScalef(self.ball.radius * 2, 0.01, self.ball.radius * 2)
        Renderer3D.draw_sphere(0, 0, 0, 0.5, (0.1, 0.1, 0.1), segments=8)
        glPopMatrix()
        glEnable(GL_LIGHTING)
        
        # Draw ball
        ball_color = self.ball.get_color() if self.ball.is_alive() else (0.5, 0.1, 0.1)
        Renderer3D.draw_sphere(ball_pos[0], ball_pos[1], ball_pos[2], 
                               self.ball.radius, ball_color)
        
        # Render particle effects
        self.particle_system.render()
    
    def _render_ui(self):
        """Render UI elements"""
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        
        # Draw score and time display
        self._draw_score_and_time(window_width, window_height)
        
        # Draw game over screen if needed
        if self.game_over:
            self._draw_game_over_screen(window_width, window_height)
        else:
            # Draw controls hint
            self._draw_controls_hint(window_width, window_height)
            
            # Draw progress indicator
            self._draw_progress_indicator(window_width, window_height)
            
            # Draw speed indicator
            self._draw_speed_indicator(window_width, window_height)
    
    def _draw_score_and_time(self, window_width, window_height):
        """Draw score and time display"""
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
        
        # Score card
        card_width = 180
        card_height = 100
        card_x = window_width - card_width - 20
        card_y = 20
        
        # Draw card background
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
        score_text = f"SCORE: {self.score}"
        UIRenderer.draw_text(score_text, card_x + 20, card_y + 30, GLUT_BITMAP_HELVETICA_18)
        
        # Time text
        time_text = f"TIME: {int(self.game_time)}s"
        UIRenderer.draw_text(time_text, card_x + 20, card_y + 55, GLUT_BITMAP_HELVETICA_12)
        
        # High score
        if self.high_score > 0:
            glColor3f(1.0, 0.8, 0.2)
            high_score_text = f"BEST: {self.high_score}"
            UIRenderer.draw_text(high_score_text, card_x + 20, card_y + 80, GLUT_BITMAP_HELVETICA_12)
        
        # Restore 3D mode
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def _draw_progress_indicator(self, window_width, window_height):
        """Draw progress bar showing distance traveled"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, window_width, window_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Progress bar
        bar_width = 300
        bar_height = 20
        bar_x = (window_width - bar_width) // 2
        bar_y = 40
        
        # Calculate progress (distance traveled)
        progress = min(1.0, abs(self.ball.z) / 200.0)  # 200 units = full bar
        
        # Background
        glColor3f(0.2, 0.2, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + bar_width, bar_y)
        glVertex2f(bar_x + bar_width, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()
        
        # Progress fill with gradient
        if progress > 0:
            glBegin(GL_QUADS)
            glColor3f(0.2, 0.8, 0.2)  # Green start
            glVertex2f(bar_x, bar_y)
            glVertex2f(bar_x + bar_width * progress * 0.5, bar_y)
            glColor3f(1.0, 0.8, 0.2)  # Yellow end
            glVertex2f(bar_x + bar_width * progress, bar_y + bar_height)
            glVertex2f(bar_x, bar_y + bar_height)
            glEnd()
        
        # Border
        glColor3f(0.8, 0.8, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + bar_width, bar_y)
        glVertex2f(bar_x + bar_width, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()
        glLineWidth(1.0)
        
        # Distance text
        glColor3f(1.0, 1.0, 1.0)
        distance_text = f"Distance: {abs(int(self.ball.z))}m"
        UIRenderer.draw_centered_text(distance_text, bar_y - 10, GLUT_BITMAP_HELVETICA_12)
        
        # Restore 3D mode
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def _draw_speed_indicator(self, window_width, window_height):
        """Draw speed indicator"""
        ball_speed = math.sqrt(self.ball.vx**2 + self.ball.vz**2)
        if ball_speed < 0.5:
            return  # Don't show when not moving
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, window_width, window_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Speed lines on sides of screen
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        num_lines = int(ball_speed)
        for i in range(min(num_lines, 8)):
            alpha = 0.1 + (ball_speed / self.ball.max_speed) * 0.3
            glColor4f(1.0, 1.0, 1.0, alpha)
            
            # Left side
            y_pos = window_height * 0.2 + (i * window_height * 0.1)
            glBegin(GL_LINES)
            glVertex2f(0, y_pos)
            glVertex2f(50, y_pos + 20)
            glEnd()
            
            # Right side
            glBegin(GL_LINES)
            glVertex2f(window_width, y_pos)
            glVertex2f(window_width - 50, y_pos + 20)
            glEnd()
        
        glDisable(GL_BLEND)
        
        # Restore 3D mode
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def _draw_controls_hint(self, window_width, window_height):
        """Draw controls hint"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, window_width, window_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Controls text with background
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Background bar
        glColor4f(0.0, 0.0, 0.0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(0, window_height - 40)
        glVertex2f(window_width, window_height - 40)
        glVertex2f(window_width, window_height)
        glVertex2f(0, window_height)
        glEnd()
        
        glDisable(GL_BLEND)
        
        # Controls text
        glColor3f(0.9, 0.9, 0.9)
        controls_text = "WASD: Move  |  SPACE: Jump  |  ESC: Menu"
        UIRenderer.draw_text(controls_text, 20, window_height - 20, GLUT_BITMAP_HELVETICA_12)
        
        # Status indicators
        if self.ball.stunned:
            glColor3f(1.0, 0.3, 0.3)
            UIRenderer.draw_text("STUNNED!", window_width - 100, window_height - 20, GLUT_BITMAP_HELVETICA_12)
        elif self.ball.speed_boost > 1.0:
            glColor3f(0.3, 1.0, 0.3)
            UIRenderer.draw_text("SPEED BOOST!", window_width - 120, window_height - 20, GLUT_BITMAP_HELVETICA_12)
        
        # Restore 3D mode
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def _draw_game_over_screen(self, window_width, window_height):
        """Draw game over screen"""
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
        
        # Game over panel
        panel_width = 400
        panel_height = 300
        panel_x = (window_width - panel_width) // 2
        panel_y = (window_height - panel_height) // 2
        
        # Panel background
        glColor4f(0.1, 0.1, 0.2, 0.95)
        glBegin(GL_QUADS)
        glVertex2f(panel_x, panel_y)
        glVertex2f(panel_x + panel_width, panel_y)
        glVertex2f(panel_x + panel_width, panel_y + panel_height)
        glVertex2f(panel_x, panel_y + panel_height)
        glEnd()
        
        # Panel border
        glColor4f(1.0, 0.3, 0.3, 1.0)
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(panel_x, panel_y)
        glVertex2f(panel_x + panel_width, panel_y)
        glVertex2f(panel_x + panel_width, panel_y + panel_height)
        glVertex2f(panel_x, panel_y + panel_height)
        glEnd()
        glLineWidth(1.0)
        
        glDisable(GL_BLEND)
        
        center_y = window_height // 2
        
        # Game Over text
        glColor3f(1.0, 0.2, 0.2)
        UIRenderer.draw_centered_text("GAME OVER!", center_y - 80, GLUT_BITMAP_TIMES_ROMAN_24)
        
        # Stats
        glColor3f(1.0, 1.0, 1.0)
        UIRenderer.draw_centered_text(f"Final Score: {self.score}", center_y - 30, GLUT_BITMAP_HELVETICA_18)
        UIRenderer.draw_centered_text(f"Distance: {abs(int(self.ball.z))}m", center_y, GLUT_BITMAP_HELVETICA_18)
        UIRenderer.draw_centered_text(f"Time: {int(self.game_time)}s", center_y + 30, GLUT_BITMAP_HELVETICA_18)
        
        # High score
        if self.score >= self.high_score:
            glColor3f(1.0, 1.0, 0.3)
            UIRenderer.draw_centered_text("NEW HIGH SCORE!", center_y + 70, GLUT_BITMAP_HELVETICA_18)
        else:
            glColor3f(0.8, 0.8, 0.8)
            UIRenderer.draw_centered_text(f"High Score: {self.high_score}", center_y + 70, GLUT_BITMAP_HELVETICA_12)
        
        # Instructions
        glColor3f(0.8, 0.8, 0.8)
        UIRenderer.draw_centered_text("Press R to Restart", center_y + 110, GLUT_BITMAP_HELVETICA_12)
        UIRenderer.draw_centered_text("Press ESC for Menu", center_y + 130, GLUT_BITMAP_HELVETICA_12)
        
        # Restore 3D mode
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def handle_key_press(self, key):
        """Handle key press events"""
        key_char = key.lower()
        if key_char in self.keys_pressed:
            self.keys_pressed[key_char] = True
        elif key_char == 'r' and self.game_over:
            self.restart_game()
    
    def handle_key_release(self, key):
        """Handle key release events"""
        key_char = key.lower()
        if key_char in self.keys_pressed:
            self.keys_pressed[key_char] = False
    
    def restart_game(self):
        """Restart the game"""
        # Reset level first
        self.level_generator = LevelGenerator()
        self.level_generator.generate_starting_platform()
        
        # Get starting platform to position ball correctly
        starting_platform = self.level_generator.platforms[0]
        ball_spawn_y = starting_platform.y + starting_platform.height/2 + 0.5
        
        # Reset player ball on starting platform
        self.ball.reset(0, ball_spawn_y, 0)
        
        # Clear particles
        self.particle_system.clear()
        
        # Generate more platforms
        self.level_generator.generate_next_platforms(8)
        
        # Reset game state
        self.score = 0
        self.game_over = False
        self.camera_z = 8.0
        self.game_time = 0.0
        self.last_checkpoint_z = 0
        self.last_time = time.time()
        
        # Clear key states
        for key in self.keys_pressed:
            self.keys_pressed[key] = False