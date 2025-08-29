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
from core.settings import game_settings

# Ensure font constants are available
try:
    from OpenGL.GLUT import (GLUT_BITMAP_HELVETICA_10, GLUT_BITMAP_HELVETICA_12, 
                             GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_TIMES_ROMAN_24,
                             GLUT_BITMAP_8_BY_13, GLUT_BITMAP_9_BY_15)
except ImportError:
    # Fallback if specific constants are not available
    pass

class Game3DScreen(BaseScreen):
    """Simple 3D game with ball on infinite platform"""
    
    def __init__(self, state_manager, opengl_manager, input_handler):
        super().__init__(state_manager, opengl_manager, input_handler)
        
        # Mode selection
        self.is_multiplayer = (game_settings.get_game_mode() == 1)

        # Ball properties
        self.ball_x = 0.0
        self.ball_y = 1.0  # Start above the platform
        self.ball_z = 0.0
        self.ball_vel_x = 0.0
        self.ball_vel_y = 0.0
        self.ball_vel_z = 0.0
        self.ball_radius = 0.5
        
        # Player 2 properties
        self.ball2_x = 0.0
        self.ball2_y = 1.0
        self.ball2_z = 0.0
        self.ball2_vel_x = 0.0
        self.ball2_vel_y = 0.0
        self.ball2_vel_z = 0.0
        self.ball2_radius = 0.5
        
        # Platform properties - Fall Guys style platforms
        self.platforms = self._create_platforms()
        
        # Game state
        self.game_over = False
        self.game_over_p1 = False
        self.game_over_p2 = False
        self.death_y = -20.0  # If ball falls below this, game over
        
        # Multiplayer VS game state
        self.game_ended = False  # True when VS game has ended
        self.winner = 0  # 0 = no winner, 1 = player 1 wins, 2 = player 2 wins
        self.winner_reason = ""  # Reason for winning
        
        # Score and timer system
        self.score = 0
        self.platforms_reached = set()  # Track which platforms have been reached
        self.start_time = time.time()
        self.game_time = 0.0
        self.best_time = float('inf')  # Best completion time
        self.high_score = 0  # Highest score achieved
        
        # Player 2 scoring
        self.score_p2 = 0
        self.platforms_reached_p2 = set()
        self.best_time_p2 = float('inf')
        self.high_score_p2 = 0
        
        # Physics constants
        self.gravity = -15.0
        self.ground_friction = 0.85
        self.air_friction = 0.98
        self.move_speed = 8.0  # Reduced from 12.0
        self.jump_force = 8.0  # Reduced from 12.0
        
        # Simple physics properties
        self.max_speed = 10.0  # Reduced from 15.0
        self.acceleration = 18.0  # Reduced from 25.0
        self.bounce_damping = 0.6  # How much energy is lost on bounce
        self.rolling_resistance = 0.02  # Slight resistance when rolling
        
        # Camera
        self.camera_distance = 10.0
        self.camera_height = 5.0
        
        # Input state
        self.keys_pressed = {
            'w': False, 'a': False, 's': False, 'd': False,
            ' ': False  # Spacebar for jumping
        }
        # Player 2 keys (arrow keys + Enter)
        self.keys_pressed_p2 = {
            'up': False, 'down': False, 'left': False, 'right': False,
            'enter': False
        }
        
        # Timing
        self.last_time = time.time()
        self._screen_just_entered = True  # Flag to detect when we enter this screen
        
    def _create_platforms(self):
        """Create Fall Guys style platforms with movement"""
        platforms = []
        
        # Determine number of platforms based on mode
        if self.is_multiplayer:
            num_platforms = 20
        else:
            num_platforms = 30
        
        # Starting platform - always static
        platforms.append({
            'x': 0, 'y': 0, 'z': 0,
            'width': 8, 'height': 0.5, 'depth': 8,
            'color': (0.2, 0.8, 0.2),  # Green
            'movement_type': 'static',
            'base_x': 0, 'base_y': 0, 'base_z': 0
        })
        
        # Generate platforms dynamically
        colors = [
            (0.8, 0.2, 0.2),  # Red
            (0.2, 0.2, 0.8),  # Blue
            (0.8, 0.8, 0.2),  # Yellow
            (0.8, 0.2, 0.8),  # Magenta
            (0.2, 0.8, 0.8),  # Cyan
            (0.8, 0.5, 0.2),  # Orange
        ]
        
        movement_types = ['horizontal', 'tilt', 'forward_back', 'rotate_tilt']
        
        for i in range(1, num_platforms + 1):
            # Calculate position (spreading them out more)
            z_pos = -6 * i  # Increased spacing
            x_pos = (-1) ** i * (i % 3) * 2  # Alternate sides with some variety
            y_pos = (i // 3) * 0.5  # Gradual height increase
            
            # Choose movement type (cycle through types)
            movement_type = movement_types[(i - 1) % len(movement_types)]
            
            # Choose color (cycle through colors)
            color = colors[(i - 1) % len(colors)]
            
            # Vary platform size based on difficulty
            if i <= 5:
                width, depth = 6, 6  # Larger platforms early on
            elif i <= 15:
                width, depth = 5, 5  # Medium platforms
            else:
                width, depth = 4, 4  # Smaller platforms for end game
            
            platform = {
                'x': x_pos, 'y': y_pos, 'z': z_pos,
                'width': width, 'height': 0.5, 'depth': depth,
                'color': color,
                'movement_type': movement_type,
                'base_x': x_pos, 'base_y': y_pos, 'base_z': z_pos
            }
            
            # Add movement-specific properties
            if movement_type == 'horizontal':
                platform.update({
                    'move_range': 3.0 + (i * 0.1),  # Increase range with level
                    'move_speed': 1.0 + (i * 0.05)   # Increase speed with level
                })
            elif movement_type == 'tilt':
                platform.update({
                    'tilt_angle': 0.0,
                    'tilt_speed': 1.5 + (i * 0.05)
                })
            elif movement_type == 'forward_back':
                platform.update({
                    'move_range': 2.5 + (i * 0.08),
                    'move_speed': 0.8 + (i * 0.04)
                })
            elif movement_type == 'rotate_tilt':
                platform.update({
                    'tilt_x': 0.0,
                    'tilt_z': 0.0,
                    'tilt_speed': 1.2 + (i * 0.03)
                })
            
            platforms.append(platform)
        
        return platforms
        
    def render(self):
        """Render the 3D game space"""
        # Reset game when first entering this screen if game was over
        if self._screen_just_entered:
            self._screen_just_entered = False
            if self.game_over:
                print("Resetting game state after returning from menu...")
                self.reset_game_state()
        
        # Ensure mode reflects latest selection (Single vs Two Player)
        self.is_multiplayer = (game_settings.get_game_mode() == 1)
            
        current_time = time.time()
        dt = min(current_time - self.last_time, 0.1)  # Cap delta time
        self.last_time = current_time
        
        # Update game logic
        self._update_game(dt)
        
        # Clear background
        glClearColor(0.3, 0.6, 1.0, 1.0)  # Sky blue
        
        if not self.is_multiplayer:
            # Single player rendering path
            self.opengl_manager.setup_3d_projection()
            self._setup_lighting()
            self._update_camera()
            self._render_scene()
            self.opengl_manager.setup_2d_projection()
            self._render_ui()
            return
        
        # Multiplayer split screen
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        half_width = max(1, window_width // 2)
        
        # Left viewport (P1)
        glViewport(0, 0, half_width, window_height)
        self._setup_perspective_for_viewport(half_width, window_height)
        self._setup_lighting()
        self._update_camera_for_player(1)
        self._render_scene_for_player(1)
        self._render_ui_for_player(1, half_width, window_height)
        
        # Clear depth buffer before rendering the second viewport
        glClear(GL_DEPTH_BUFFER_BIT)
        
        # Right viewport (P2)
        glViewport(half_width, 0, window_width - half_width, window_height)
        self._setup_perspective_for_viewport(window_width - half_width, window_height)
        self._setup_lighting()
        self._update_camera_for_player(2)
        self._render_scene_for_player(2)
        self._render_ui_for_player(2, window_width - half_width, window_height)
        
        # Render the divider line between the two viewports
        self._render_multiplayer_divider(window_width, window_height)
        
    def _update_game(self, dt):
        """Update game physics and logic"""
        # Update platform movements
        self._update_platform_movements(dt)
        
        if not self.is_multiplayer:
            self._handle_input(dt)
            self._update_physics(dt)
            return
        
        # Multiplayer: update both players
        self._handle_input(dt)
        self._handle_input_p2(dt)
        self._update_physics(dt)
        self._update_physics_p2(dt)
        
    def _update_platform_movements(self, dt):
        """Update moving and tilting platforms"""
        current_time = time.time()
        
        for platform in self.platforms:
            movement_type = platform.get('movement_type', 'static')
            
            # Store previous position for velocity calculation
            prev_x = platform.get('x', 0)
            prev_z = platform.get('z', 0)
            
            if movement_type == 'horizontal':
                # Move side to side
                move_range = platform['move_range']
                move_speed = platform['move_speed']
                base_x = platform['base_x']
                
                offset = math.sin(current_time * move_speed) * move_range
                platform['x'] = base_x + offset
                
                # Calculate velocity
                platform['vel_x'] = (platform['x'] - prev_x) / dt if dt > 0 else 0
                platform['vel_z'] = 0
                
            elif movement_type == 'forward_back':
                # Move forward and back
                move_range = platform['move_range']
                move_speed = platform['move_speed']
                base_z = platform['base_z']
                
                offset = math.sin(current_time * move_speed) * move_range
                platform['z'] = base_z + offset
                
                # Calculate velocity
                platform['vel_x'] = 0
                platform['vel_z'] = (platform['z'] - prev_z) / dt if dt > 0 else 0
                
            elif movement_type == 'tilt':
                # Tilt back and forth
                tilt_speed = platform['tilt_speed']
                platform['tilt_angle'] = math.sin(current_time * tilt_speed) * 0.3  # Max 0.3 radians (about 17 degrees)
                platform['vel_x'] = 0
                platform['vel_z'] = 0
                
            elif movement_type == 'rotate_tilt':
                # Complex tilting in multiple directions
                tilt_speed = platform['tilt_speed']
                platform['tilt_x'] = math.sin(current_time * tilt_speed) * 0.25
                platform['tilt_z'] = math.cos(current_time * tilt_speed * 0.7) * 0.25
                platform['vel_x'] = 0
                platform['vel_z'] = 0
            else:
                # Static platform
                platform['vel_x'] = 0
                platform['vel_z'] = 0
        
    def _handle_input(self, dt):
        """Handle player input with acceleration"""
        # Don't handle input if VS game has ended
        if self.is_multiplayer and self.game_ended:
            return
            
        # Movement forces using acceleration
        if self.keys_pressed['w']:
            self.ball_vel_z -= self.acceleration * dt
        if self.keys_pressed['s']:
            self.ball_vel_z += self.acceleration * dt
        if self.keys_pressed['a']:
            self.ball_vel_x -= self.acceleration * dt
        if self.keys_pressed['d']:
            self.ball_vel_x += self.acceleration * dt
            
        # Limit maximum horizontal speed
        horizontal_speed = math.sqrt(self.ball_vel_x**2 + self.ball_vel_z**2)
        if horizontal_speed > self.max_speed:
            scale = self.max_speed / horizontal_speed
            self.ball_vel_x *= scale
            self.ball_vel_z *= scale
            
        # Jumping
        if self.keys_pressed[' '] and self._is_on_ground():
            self.ball_vel_y = self.jump_force
    
    def _handle_input_p2(self, dt):
        """Handle Player 2 input with acceleration"""
        if not self.is_multiplayer:
            return
        
        # Don't handle input if VS game has ended
        if self.game_ended:
            return
            
        if self.keys_pressed_p2['up']:
            self.ball2_vel_z -= self.acceleration * dt
        if self.keys_pressed_p2['down']:
            self.ball2_vel_z += self.acceleration * dt
        if self.keys_pressed_p2['left']:
            self.ball2_vel_x -= self.acceleration * dt
        if self.keys_pressed_p2['right']:
            self.ball2_vel_x += self.acceleration * dt
        
        horizontal_speed = math.sqrt(self.ball2_vel_x**2 + self.ball2_vel_z**2)
        if horizontal_speed > self.max_speed:
            scale = self.max_speed / horizontal_speed
            self.ball2_vel_x *= scale
            self.ball2_vel_z *= scale
        
        if self.keys_pressed_p2['enter'] and self._is_on_ground_p2():
            self.ball2_vel_y = self.jump_force
            
    def _update_physics(self, dt):
        """Update ball physics with enhanced properties"""
        if self.game_over or (self.is_multiplayer and self.game_ended):
            return
            
        # Update game timer
        self.game_time = time.time() - self.start_time
            
        # Apply gravity
        self.ball_vel_y += self.gravity * dt
        
        # Apply friction and rolling resistance
        if self._is_on_ground():
            # Ground friction
            self.ball_vel_x *= self.ground_friction
            self.ball_vel_z *= self.ground_friction
            
            # Rolling resistance (simulates ball rolling on surface)
            speed = math.sqrt(self.ball_vel_x**2 + self.ball_vel_z**2)
            if speed > 0:
                resistance_force = self.rolling_resistance * dt
                resistance_scale = max(0, 1 - resistance_force / speed)
                self.ball_vel_x *= resistance_scale
                self.ball_vel_z *= resistance_scale
        else:
            # Air friction
            self.ball_vel_x *= self.air_friction
            self.ball_vel_z *= self.air_friction
            
        # Update position
        self.ball_x += self.ball_vel_x * dt
        self.ball_y += self.ball_vel_y * dt
        self.ball_z += self.ball_vel_z * dt
        
        # Platform collision
        self._handle_platform_collision()
        
        # Apply platform movement to ball if on a moving platform
        self._apply_platform_movement(dt)
        
        # Update score based on platform reached
        self._update_score()
        
        # Check for death (falling off platforms)
        if self.ball_y < self.death_y:
            self.game_over = True
            self.game_over_p1 = True
            # Update high score if needed
            if self.score > self.high_score:
                self.high_score = self.score
                print(f"New High Score: {self.high_score}!")
            print("Game Over! Ball fell off the platforms!")
            
            # In multiplayer VS mode, determine winner when a player falls
            if self.is_multiplayer and not self.game_ended:
                self._determine_vs_winner(1)  # Player 1 fell

    def _update_physics_p2(self, dt):
        """Update Player 2 physics"""
        if not self.is_multiplayer or self.game_over_p2 or self.game_ended:
            return
        
        self.game_time = time.time() - self.start_time
        self.ball2_vel_y += self.gravity * dt
        if self._is_on_ground_p2():
            self.ball2_vel_x *= self.ground_friction
            self.ball2_vel_z *= self.ground_friction
            speed = math.sqrt(self.ball2_vel_x**2 + self.ball2_vel_z**2)
            if speed > 0:
                resistance_force = self.rolling_resistance * dt
                resistance_scale = max(0, 1 - resistance_force / speed)
                self.ball2_vel_x *= resistance_scale
                self.ball2_vel_z *= resistance_scale
        else:
            self.ball2_vel_x *= self.air_friction
            self.ball2_vel_z *= self.air_friction
        
        self.ball2_x += self.ball2_vel_x * dt
        self.ball2_y += self.ball2_vel_y * dt
        self.ball2_z += self.ball2_vel_z * dt
        
        self._handle_platform_collision_p2()
        self._apply_platform_movement_p2(dt)
        self._update_score_p2()
        
        if self.ball2_y < self.death_y:
            self.game_over_p2 = True
            if self.score_p2 > self.high_score_p2:
                self.high_score_p2 = self.score_p2
                print(f"P2 New High Score: {self.high_score_p2}!")
            print("P2 Game Over! Ball fell off the platforms!")
            
            # In multiplayer VS mode, determine winner when a player falls
            if self.is_multiplayer and not self.game_ended:
                self._determine_vs_winner(2)  # Player 2 fell
    
    def _determine_vs_winner(self, falling_player):
        """Determine winner in VS mode when a player falls"""
        if self.game_ended:
            return
            
        self.game_ended = True
        self.game_over = True
        self.game_over_p1 = True
        self.game_over_p2 = True
        
        # Get scores
        p1_score = self.score
        p2_score = self.score_p2
        score_diff = abs(p1_score - p2_score)
        
        if falling_player == 1:
            # Player 1 fell
            if p1_score > p2_score and score_diff > 100:
                # Falling player wins if they have more than 100 point lead
                self.winner = 1
                self.winner_reason = f"P1 WINS! Fell with {score_diff} point lead!"
            else:
                # Remaining player wins
                self.winner = 2
                self.winner_reason = f"P2 WINS! P1 fell (score diff: {score_diff})"
        else:
            # Player 2 fell
            if p2_score > p1_score and score_diff > 100:
                # Falling player wins if they have more than 100 point lead
                self.winner = 2
                self.winner_reason = f"P2 WINS! Fell with {score_diff} point lead!"
            else:
                # Remaining player wins
                self.winner = 1
                self.winner_reason = f"P1 WINS! P2 fell (score diff: {score_diff})"
        
        print(self.winner_reason)
            
    def _handle_platform_collision(self):
        """Handle collision with platforms with bounce physics"""
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
                    
                    # Add bounce effect if falling fast enough
                    if self.ball_vel_y < -2.0:  # Only bounce if falling fast
                        self.ball_vel_y = -self.ball_vel_y * self.bounce_damping
                    else:
                        self.ball_vel_y = 0
                    
                    return  # Stop checking other platforms
    
    def _handle_platform_collision_p2(self):
        """Handle collision for P2 with bounce physics"""
        for platform in self.platforms:
            px, py, pz = platform['x'], platform['y'], platform['z']
            pw, ph, pd = platform['width'], platform['height'], platform['depth']
            if (px - pw/2 <= self.ball2_x <= px + pw/2 and
                pz - pd/2 <= self.ball2_z <= pz + pd/2):
                platform_top = py + ph/2
                ball_bottom = self.ball2_y - self.ball2_radius
                if (ball_bottom <= platform_top and
                    ball_bottom >= platform_top - 1.0 and
                    self.ball2_vel_y <= 0):
                    self.ball2_y = platform_top + self.ball2_radius
                    if self.ball2_vel_y < -2.0:
                        self.ball2_vel_y = -self.ball2_vel_y * self.bounce_damping
                    else:
                        self.ball2_vel_y = 0
                    return
                
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
    
    def _is_on_ground_p2(self):
        """Check if P2 ball is on any platform"""
        for platform in self.platforms:
            px, py, pz = platform['x'], platform['y'], platform['z']
            pw, ph, pd = platform['width'], platform['height'], platform['depth']
            if (px - pw/2 <= self.ball2_x <= px + pw/2 and
                pz - pd/2 <= self.ball2_z <= pz + pd/2):
                platform_top = py + ph/2
                ball_bottom = self.ball2_y - self.ball2_radius
                if abs(ball_bottom - platform_top) < 0.1:
                    return True
        return False
        
    def _update_score(self):
        """Update score based on platforms reached"""
        for i, platform in enumerate(self.platforms):
            px, py, pz = platform['x'], platform['y'], platform['z']
            pw, ph, pd = platform['width'], platform['height'], platform['depth']
            
            # Check if ball is on this platform
            if (px - pw/2 <= self.ball_x <= px + pw/2 and
                pz - pd/2 <= self.ball_z <= pz + pd/2 and
                self._is_on_ground()):
                
                # If this platform hasn't been reached before, award points
                if i not in self.platforms_reached:
                    self.platforms_reached.add(i)
                    points = (i + 1) * 100  # More points for later platforms
                    self.score += points
                    print(f"Platform {i+1} reached! +{points} points (Total: {self.score})")
                    
                    # Check if all platforms completed
                    if len(self.platforms_reached) == len(self.platforms):
                        completion_bonus = 1000
                        self.score += completion_bonus
                        completion_time = self.game_time
                        
                        # Update best time
                        if completion_time < self.best_time:
                            self.best_time = completion_time
                            print(f"New Best Time: {self.best_time:.1f}s!")
                        
                        print(f"All platforms completed! +{completion_bonus} bonus points!")
                        print(f"Final Score: {self.score} | Time: {completion_time:.1f}s")
    
    def _update_score_p2(self):
        """Update P2 score based on platforms reached"""
        for i, platform in enumerate(self.platforms):
            px, py, pz = platform['x'], platform['y'], platform['z']
            pw, ph, pd = platform['width'], platform['height'], platform['depth']
            if (px - pw/2 <= self.ball2_x <= px + pw/2 and
                pz - pd/2 <= self.ball2_z <= pz + pd/2 and
                self._is_on_ground_p2()):
                if i not in self.platforms_reached_p2:
                    self.platforms_reached_p2.add(i)
                    points = (i + 1) * 100
                    self.score_p2 += points
                    print(f"[P2] Platform {i+1} reached! +{points} points (Total: {self.score_p2})")
                    if len(self.platforms_reached_p2) == len(self.platforms):
                        completion_bonus = 1000
                        self.score_p2 += completion_bonus
                        completion_time = self.game_time
                        if completion_time < self.best_time_p2:
                            self.best_time_p2 = completion_time
                            print(f"[P2] New Best Time: {self.best_time_p2:.1f}s!")
                        print(f"[P2] All platforms completed! +{completion_bonus} bonus points!")
                        print(f"[P2] Final Score: {self.score_p2} | Time: {completion_time:.1f}s")
        
    def _apply_platform_movement(self, dt):
        """Apply platform movement to ball when standing on a moving platform"""
        if not self._is_on_ground():
            return
            
        # Find which platform the ball is on
        for platform in self.platforms:
            px, py, pz = platform['x'], platform['y'], platform['z']
            pw, ph, pd = platform['width'], platform['height'], platform['depth']
            
            # Check if ball is on this platform
            if (px - pw/2 <= self.ball_x <= px + pw/2 and
                pz - pd/2 <= self.ball_z <= pz + pd/2):
                
                # Check if ball is on top of platform
                platform_top = py + ph/2
                ball_bottom = self.ball_y - self.ball_radius
                
                if abs(ball_bottom - platform_top) < 0.1:
                    # Apply platform velocity to ball
                    platform_vel_x = platform.get('vel_x', 0)
                    platform_vel_z = platform.get('vel_z', 0)
                    
                    # Move ball with platform (with some resistance to feel natural)
                    self.ball_x += platform_vel_x * dt * 0.8  # 80% coupling
                    self.ball_z += platform_vel_z * dt * 0.8
                    
                    return  # Only apply movement from one platform
    
    def _apply_platform_movement_p2(self, dt):
        """Apply platform movement to P2 ball"""
        if not self._is_on_ground_p2():
            return
        for platform in self.platforms:
            px, py, pz = platform['x'], platform['y'], platform['z']
            pw, ph, pd = platform['width'], platform['height'], platform['depth']
            if (px - pw/2 <= self.ball2_x <= px + pw/2 and
                pz - pd/2 <= self.ball2_z <= pz + pd/2):
                platform_top = py + ph/2
                ball_bottom = self.ball2_y - self.ball2_radius
                if abs(ball_bottom - platform_top) < 0.1:
                    platform_vel_x = platform.get('vel_x', 0)
                    platform_vel_z = platform.get('vel_z', 0)
                    self.ball2_x += platform_vel_x * dt * 0.8
                    self.ball2_z += platform_vel_z * dt * 0.8
                    return
        
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

    def _render_scene_for_player(self, player_index):
        """Render scene for specified player (platforms + that player's ball)"""
        self._draw_platform()
        if player_index == 1:
            self._draw_ball()
        else:
            glPushMatrix()
            glTranslatef(self.ball2_x, self.ball2_y, self.ball2_z)
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.8, 0.2, 0.2, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 0.4, 0.4, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 0.8, 0.8, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
            quadric = gluNewQuadric()
            gluSphere(quadric, self.ball2_radius, 20, 20)
            gluDeleteQuadric(quadric)
            glPopMatrix()

    def _setup_perspective_for_viewport(self, width, height):
        """Set perspective according to viewport size"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = float(max(1, width)) / float(max(1, height))
        gluPerspective(45, aspect, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def _update_camera_for_player(self, player_index):
        """Update camera for specific player"""
        glLoadIdentity()
        if player_index == 1:
            cx, cy, cz = self.ball_x, self.ball_y, self.ball_z
        else:
            cx, cy, cz = self.ball2_x, self.ball2_y, self.ball2_z
        camera_x = cx
        camera_y = cy + self.camera_height
        camera_z = cz + self.camera_distance
        gluLookAt(camera_x, camera_y, camera_z,
                  cx, cy, cz,
                  0, 1, 0)
        
    def _draw_platform(self):
        """Draw Fall Guys style platforms with movement and tilting"""
        glEnable(GL_LIGHTING)
        
        # Draw all platforms
        for i, platform in enumerate(self.platforms):
            px, py, pz = platform['x'], platform['y'], platform['z']
            pw, ph, pd = platform['width'], platform['height'], platform['depth']
            color = platform['color']
            movement_type = platform.get('movement_type', 'static')
            
            glPushMatrix()
            glTranslatef(px, py, pz)
            
            # Apply tilting rotations
            if movement_type == 'tilt':
                tilt_angle = platform.get('tilt_angle', 0.0)
                glRotatef(math.degrees(tilt_angle), 0, 0, 1)  # Tilt around Z axis
                
            elif movement_type == 'rotate_tilt':
                tilt_x = platform.get('tilt_x', 0.0)
                tilt_z = platform.get('tilt_z', 0.0)
                glRotatef(math.degrees(tilt_x), 1, 0, 0)  # Tilt around X axis
                glRotatef(math.degrees(tilt_z), 0, 0, 1)  # Tilt around Z axis
            
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
        
    def _draw_score_card(self, window_width, window_height):
        """Draw a score card with score, timer, and stats"""
        # Disable depth testing and lighting for UI
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Score card background
        card_width = 220
        card_height = 100
        card_x = window_width - card_width - 20
        card_y = window_height - card_height - 20
        
        # Draw semi-transparent background
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, 0.8)  # Semi-transparent black
        glBegin(GL_QUADS)
        glVertex2f(card_x, card_y)
        glVertex2f(card_x + card_width, card_y)
        glVertex2f(card_x + card_width, card_y + card_height)
        glVertex2f(card_x, card_y + card_height)
        glEnd()
        
        # Draw border
        glDisable(GL_BLEND)
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(card_x, card_y)
        glVertex2f(card_x + card_width, card_y)
        glVertex2f(card_x + card_width, card_y + card_height)
        glVertex2f(card_x, card_y + card_height)
        glEnd()
        
        # Text content using simple fonts
        text_x = card_x + 10
        text_y = card_y + card_height - 20
        
        # Score
        glColor3f(1.0, 1.0, 0.0)  # Yellow
        score_text = f"SCORE: {self.score}"
        glRasterPos2f(text_x, text_y)
        for char in score_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
        
        # Timer
        text_y -= 20
        glColor3f(0.0, 1.0, 1.0)  # Cyan
        timer_text = f"TIME: {self.game_time:.1f}s"
        glRasterPos2f(text_x, text_y)
        for char in timer_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
        
        # Platform progress
        text_y -= 20
        glColor3f(0.0, 1.0, 0.0)  # Green
        platform_text = f"PLATFORMS: {len(self.platforms_reached)}/{len(self.platforms)}"
        glRasterPos2f(text_x, text_y)
        for char in platform_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(char))
        
        # High score and best time (if available)
        if self.high_score > 0 or self.best_time < float('inf'):
            text_y -= 15
            glColor3f(1.0, 0.5, 0.0)  # Orange
            stats_text = f"HIGH: {self.high_score}"
            if self.best_time < float('inf'):
                stats_text += f" | BEST: {self.best_time:.1f}s"
            glRasterPos2f(text_x, text_y)
            for char in stats_text:
                glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(char))
        
        # Restore OpenGL state
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
    def _render_ui(self):
        """Render UI elements"""
        window_width = glutGet(GLUT_WINDOW_WIDTH)
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        
        if self.game_over:
            # Game Over screen with eye-catching colors
            glColor3f(1.0, 0.2, 0.2)  # Bright red with slight orange tint
            game_over_text = "GAME OVER!"
            glRasterPos2f(window_width//2 - 50, window_height//2)
            for char in game_over_text:
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
                
            glColor3f(1.0, 1.0, 0.0)  # Bright yellow for instructions
            restart_text = "Press R to restart, ESC to quit"
            glRasterPos2f(window_width//2 - 100, window_height//2 - 30)
            for char in restart_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
        else:
            # Draw score card
            self._draw_score_card(window_width, window_height)
            
            # Normal game UI
            glColor3f(1.0, 1.0, 1.0)
            controls_text = "Controls: WASD to move, SPACE to jump, ESC to quit"
            glRasterPos2f(20, window_height - 20)
            for char in controls_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
                
            # Draw ball position and velocity
            pos_text = f"Position: X={self.ball_x:.1f}, Y={self.ball_y:.1f}, Z={self.ball_z:.1f}"
            glRasterPos2f(20, window_height - 40)
            for char in pos_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
                
            # Show velocity for physics feedback
            speed = math.sqrt(self.ball_vel_x**2 + self.ball_vel_z**2)
            vel_text = f"Speed: {speed:.1f} | Velocity: X={self.ball_vel_x:.1f}, Y={self.ball_vel_y:.1f}, Z={self.ball_vel_z:.1f}"
            glRasterPos2f(20, window_height - 60)
            for char in vel_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(char))

    def _render_ui_for_player(self, player_index, vp_width, vp_height):
        """Render per-player UI for current viewport"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, vp_width, vp_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        if player_index == 1:
            score = self.score
            over = self.game_over_p1
            vx, vy, vz = self.ball_vel_x, self.ball_vel_y, self.ball_vel_z
            bx, by, bz = self.ball_x, self.ball_y, self.ball_z
            controls = "P1: WASD move, SPACE jump"
        else:
            score = self.score_p2
            over = self.game_over_p2
            vx, vy, vz = self.ball2_vel_x, self.ball2_vel_y, self.ball2_vel_z
            bx, by, bz = self.ball2_x, self.ball2_y, self.ball2_z
            controls = "P2: Arrows move, ENTER jump"
        
        if over:
            # In multiplayer VS mode, show winner information
            if self.is_multiplayer and self.game_ended and self.winner > 0:
                if self.winner == player_index:
                    glColor3f(0.0, 1.0, 0.3)  # Bright green with slight cyan tint for winner
                    text = "YOU WIN!"
                else:
                    glColor3f(1.0, 0.2, 0.4)  # Bright red-pink for loser
                    text = "YOU LOSE"
                
                glRasterPos2f(vp_width//2 - 50, vp_height//2 - 30)
                for ch in text:
                    glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
                
                # Show winner reason with bright yellow
                glColor3f(1.0, 1.0, 0.2)  # Bright yellow for reason text
                reason_lines = self.winner_reason.split('!')
                for i, line in enumerate(reason_lines):
                    if line.strip():
                        glRasterPos2f(vp_width//2 - 80, vp_height//2 + 10 + i * 20)
                        for ch in line.strip():
                            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
            else:
                glColor3f(1.0, 0.2, 0.2)  # Bright red with orange tint
                text = "GAME OVER"
                glRasterPos2f(vp_width//2 - 50, vp_height//2)
                for ch in text:
                    glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
        else:
            glColor3f(1.0, 1.0, 0.0)
            s = f"SCORE: {score}"
            glRasterPos2f(10, 20)
            for ch in s:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
            glColor3f(1.0, 1.0, 1.0)
            glRasterPos2f(10, 40)
            for ch in controls:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
            glColor3f(0.8, 0.9, 1.0)
            pos = f"Pos X={bx:.1f} Y={by:.1f} Z={bz:.1f}"
            glRasterPos2f(10, 60)
            for ch in pos:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
            speed = math.sqrt(vx*vx + vz*vz)
            vel = f"Speed {speed:.1f} | Vx={vx:.1f} Vy={vy:.1f} Vz={vz:.1f}"
            glRasterPos2f(10, 80)
            for ch in vel:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def _render_multiplayer_divider(self, window_width, window_height):
        """Render a visible divider line between the two player viewports"""
        # Set up 2D rendering for the full screen
        glViewport(0, 0, window_width, window_height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, window_width, window_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Disable lighting and depth testing for 2D overlay
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Enable blending for semi-transparent effects
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Calculate divider position (middle of screen)
        divider_x = window_width // 2
        divider_width = 4  # Width of the divider line
        
        # Draw the main divider line (bright white/yellow)
        glColor4f(1.0, 1.0, 0.8, 0.9)  # Light yellow with high opacity
        glBegin(GL_QUADS)
        glVertex2f(divider_x - divider_width//2, 0)
        glVertex2f(divider_x + divider_width//2, 0)
        glVertex2f(divider_x + divider_width//2, window_height)
        glVertex2f(divider_x - divider_width//2, window_height)
        glEnd()
        
        # Draw subtle shadow/border on both sides for better visibility
        shadow_width = 1
        glColor4f(0.0, 0.0, 0.0, 0.4)  # Dark shadow
        
        # Left shadow
        glBegin(GL_QUADS)
        glVertex2f(divider_x - divider_width//2 - shadow_width, 0)
        glVertex2f(divider_x - divider_width//2, 0)
        glVertex2f(divider_x - divider_width//2, window_height)
        glVertex2f(divider_x - divider_width//2 - shadow_width, window_height)
        glEnd()
        
        # Right shadow
        glBegin(GL_QUADS)
        glVertex2f(divider_x + divider_width//2, 0)
        glVertex2f(divider_x + divider_width//2 + shadow_width, 0)
        glVertex2f(divider_x + divider_width//2 + shadow_width, window_height)
        glVertex2f(divider_x + divider_width//2, window_height)
        glEnd()
        
        # Add "VS" text in the middle for a game-like feel
        text = "VS"
        text_y = window_height // 2 - 10
        text_x = divider_x - 10  # Center the text
        
        glColor4f(0.0, 0.0, 0.0, 0.8)  # Dark background for text
        glBegin(GL_QUADS)
        glVertex2f(text_x - 15, text_y - 8)
        glVertex2f(text_x + 15, text_y - 8)
        glVertex2f(text_x + 15, text_y + 12)
        glVertex2f(text_x - 15, text_y + 12)
        glEnd()
        
        glColor3f(1.0, 1.0, 1.0)  # White text
        glRasterPos2f(text_x, text_y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        
        # Restore OpenGL state
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
            
    def handle_key_press(self, key):
        """Handle key press events"""
        key = key.lower()
        
        # Handle restart (single or two player)
        is_any_game_over = self.game_over or (self.is_multiplayer and (self.game_over_p1 or self.game_over_p2))
        if key == 'r' and is_any_game_over:
            self._restart_game()
            return
            
        if key in self.keys_pressed and not self.game_over:
            self.keys_pressed[key] = True
        
        # P2 jump via Enter
        if self.is_multiplayer and not self.game_over_p2:
            if key == '\r':
                self.keys_pressed_p2['enter'] = True
            
    def handle_key_release(self, key):
        """Handle key release events"""
        key = key.lower()
        if key in self.keys_pressed and not self.game_over:
            self.keys_pressed[key] = False
        if self.is_multiplayer:
            if key == '\r':
                self.keys_pressed_p2['enter'] = False

    def handle_special_key_press(self, key):
        """Handle Arrow keys for P2"""
        if not self.is_multiplayer or self.game_over_p2:
            return
        if key == GLUT_KEY_UP:
            self.keys_pressed_p2['up'] = True
        elif key == GLUT_KEY_DOWN:
            self.keys_pressed_p2['down'] = True
        elif key == GLUT_KEY_LEFT:
            self.keys_pressed_p2['left'] = True
        elif key == GLUT_KEY_RIGHT:
            self.keys_pressed_p2['right'] = True
    
    def handle_special_key_release(self, key):
        """Handle Arrow key releases for P2"""
        if not self.is_multiplayer:
            return
        if key == GLUT_KEY_UP:
            self.keys_pressed_p2['up'] = False
        elif key == GLUT_KEY_DOWN:
            self.keys_pressed_p2['down'] = False
        elif key == GLUT_KEY_LEFT:
            self.keys_pressed_p2['left'] = False
        elif key == GLUT_KEY_RIGHT:
            self.keys_pressed_p2['right'] = False
            
    def _restart_game(self):
        """Restart the game"""
        self.ball_x = 0.0
        self.ball_y = 1.0
        self.ball_z = 0.0
        self.ball_vel_x = 0.0
        self.ball_vel_y = 0.0
        self.ball_vel_z = 0.0
        self.game_over = False
        self.game_over_p1 = False
        self.game_over_p2 = False
        
        # Reset VS game state
        self.game_ended = False
        self.winner = 0
        self.winner_reason = ""
        
        # Reset score and timer
        self.score = 0
        self.platforms_reached = set()
        self.start_time = time.time()
        self.game_time = 0.0
        
        # Reset Player 2 state when in multiplayer
        self.ball2_x = 0.0
        self.ball2_y = 1.0
        self.ball2_z = 0.0
        self.ball2_vel_x = 0.0
        self.ball2_vel_y = 0.0
        self.ball2_vel_z = 0.0
        self.score_p2 = 0
        self.platforms_reached_p2 = set()
        
        # Clear pressed keys
        for k in list(self.keys_pressed.keys()):
            self.keys_pressed[k] = False
        for k in list(self.keys_pressed_p2.keys()):
            self.keys_pressed_p2[k] = False
        print("Game restarted!")
        
    def reset_game_state(self):
        """Reset game state when leaving/entering the screen"""
        self._restart_game()
        
    def on_screen_enter(self):
        """Called when this screen becomes active"""
        print("Game3D screen entered")
        # Sync mode with current selection and reset when coming in
        self.is_multiplayer = (game_settings.get_game_mode() == 1)
        if self.game_over:
            print("Game was over, resetting state...")
            self.reset_game_state()
            
    def on_screen_exit(self):
        """Called when leaving this screen"""
        print("Game3D screen exiting")
        # Mark that we'll need to reset when we come back
        self._screen_just_entered = True
