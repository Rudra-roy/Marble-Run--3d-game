"""
Physics system for ball movement and collision detection.
"""

import math

class Ball:
    """3D Ball with physics properties"""
    
    def __init__(self, x=0, y=2, z=0, radius=0.5, player_id=0):
        # Position
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.player_id = player_id
        
        # Velocity
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        
        # Physics constants
        self.gravity = -12.0  # Slightly stronger gravity for Fall Guys feel
        self.friction = 0.88
        self.bounce_damping = 0.6
        self.move_force = 18.0  # More responsive movement
        self.max_speed = 10.0
        self.jump_force = 14.0  # Higher jumps
        self.can_jump = True
        
        # Fall Guys style colors
        self.colors = [
            (1.0, 0.3, 0.3),  # Red
            (0.3, 0.3, 1.0),  # Blue
            (0.3, 1.0, 0.3),  # Green
            (1.0, 1.0, 0.3),  # Yellow
            (1.0, 0.3, 1.0),  # Magenta
            (0.3, 1.0, 1.0),  # Cyan
            (1.0, 0.6, 0.3),  # Orange
            (0.8, 0.3, 0.8),  # Purple
        ]
        self.color = self.colors[player_id % len(self.colors)]
        
        # Game state
        self.on_ground = True
        self.alive = True
        self.stunned = False
        self.stun_time = 0.0
        
        # Special effects
        self.speed_boost = 1.0
        self.speed_boost_time = 0.0
        
    def apply_force(self, fx, fz, dt):
        """Apply horizontal force to the ball"""
        if self.alive and not self.stunned:
            # Apply speed boost
            force_multiplier = self.speed_boost
            self.vx += fx * dt * force_multiplier
            self.vz += fz * dt * force_multiplier
            
            # Limit horizontal speed
            max_speed = self.max_speed * self.speed_boost
            speed = math.sqrt(self.vx**2 + self.vz**2)
            if speed > max_speed:
                self.vx = (self.vx / speed) * max_speed
                self.vz = (self.vz / speed) * max_speed
    
    def update(self, dt, platforms):
        """Update ball physics"""
        if not self.alive:
            return
        
        # Update special effect timers
        if self.stun_time > 0:
            self.stun_time -= dt
            if self.stun_time <= 0:
                self.stunned = False
        
        if self.speed_boost_time > 0:
            self.speed_boost_time -= dt
            if self.speed_boost_time <= 0:
                self.speed_boost = 1.0
            
        # Apply gravity
        self.vy += self.gravity * dt
        
        # Update position
        old_x, old_y, old_z = self.x, self.y, self.z
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        
        # Check platform collisions
        self.on_ground = False
        for platform in platforms:
            if self.check_platform_collision(platform):
                self.on_ground = True
                self.can_jump = True
                
                # Check for special platform effects
                self._handle_platform_effects(platform)
                break
        
        # Apply friction when on ground
        if self.on_ground:
            friction_factor = self.friction
            self.vx *= friction_factor
            self.vz *= friction_factor
        
        # Check if ball fell below platforms (game over)
        if self.y < -15:
            self.alive = False
    
    def check_platform_collision(self, platform):
        """Check collision with a platform"""
        # Simple box collision detection
        px, py, pz = platform.x, platform.y, platform.z
        pw, ph, pd = platform.width, platform.height, platform.depth
        
        # Check if ball is within platform bounds (with some tolerance)
        tolerance = 0.1
        if (px - pw/2 - tolerance <= self.x <= px + pw/2 + tolerance and
            pz - pd/2 - tolerance <= self.z <= pz + pd/2 + tolerance):
            
            # Check if ball is on top of platform
            if (self.y - self.radius <= py + ph/2 and 
                self.y - self.radius >= py + ph/2 - 1.0):
                
                self.y = py + ph/2 + self.radius
                if self.vy < 0:
                    self.vy = 0
                return True
        
        return False
    
    def _handle_platform_effects(self, platform):
        """Handle special platform effects"""
        if hasattr(platform, 'platform_type'):
            if platform.platform_type == 'speed_boost':
                self.speed_boost = 1.5
                self.speed_boost_time = 2.0
            elif platform.platform_type == 'bounce':
                if self.vy < 0:  # Only if falling down
                    self.vy = abs(self.vy) * 1.5 + 5.0  # Bounce up
            elif platform.platform_type == 'slippery':
                # Reduce friction temporarily
                self.friction = 0.95
    
    def get_color(self):
        """Get the ball's color with special effects"""
        if self.stunned:
            # Flash red when stunned
            import time
            if int(time.time() * 10) % 2:
                return (1.0, 0.3, 0.3)
        elif self.speed_boost > 1.0:
            # Glow effect when speed boosted
            return tuple(min(1.0, c * 1.3) for c in self.color)
        return self.color
    
    def get_position(self):
        """Get ball position as tuple"""
        return (self.x, self.y, self.z)
    
    def is_alive(self):
        """Check if ball is still alive"""
        return self.alive
    
    def reset(self, x=0, y=2, z=0):
        """Reset ball to starting position"""
        self.x = x
        self.y = y
        self.z = z
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.alive = True
        self.on_ground = True
        self.can_jump = True
        self.stunned = False
        self.stun_time = 0.0
        self.speed_boost = 1.0
        self.speed_boost_time = 0.0
    
    def jump(self):
        """Make the ball jump if it's on the ground"""
        if self.alive and self.on_ground and self.can_jump:
            self.vy = self.jump_force
            self.on_ground = False
            self.can_jump = False  # Prevent double jumping
            return True  # Jump successful
        return False  # Jump failed
    
    def stun(self, duration=1.0):
        """Stun the ball for a duration"""
        self.stunned = True
        self.stun_time = duration
        self.vx *= 0.5  # Reduce velocity when stunned
        self.vz *= 0.5
