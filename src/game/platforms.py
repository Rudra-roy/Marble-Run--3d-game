"""
Platform and level generation system.
"""
        
        
from OpenGL.GL import *
import random
import math
from game.obstacles import Hammer, PushWall, SpinningBar

class Platform:
    """3D Platform obstacle"""
    
    def __init__(self, x, y, z, width=2.0, height=0.2, depth=2.0, color=(0.6, 0.6, 0.8), platform_type='normal'):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth
        self.color = color
        self.platform_type = platform_type  # normal, speed_boost, bounce, slippery, moving
        self.passed = False  # For scoring
        
        # Moving platform properties
        self.moving = platform_type == 'moving'
        self.move_speed = 2.0
        self.move_range = 3.0
        self.initial_x = x
        self.move_direction = 1
        
        # Animation
        self.animation_time = 0.0
    
    def render(self):
        """Render the platform"""
        
        current_color = self.get_visual_color()
        glColor3f(*current_color)
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glScalef(self.width, self.height, self.depth)
        
        # Draw a cube
        glBegin(GL_QUADS)
        
        # Top face
        glNormal3f(0, 1, 0)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        
        # Bottom face
        glNormal3f(0, -1, 0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, -0.5)
        
        # Front face
        glNormal3f(0, 0, 1)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        
        # Back face
        glNormal3f(0, 0, -1)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        
        # Left face
        glNormal3f(-1, 0, 0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        # Right face
        glNormal3f(1, 0, 0)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        
        glEnd()
        
        # Add special effects for certain platform types
        if self.platform_type in ['speed_boost', 'bounce']:
            # Add a glowing outline
            glDisable(GL_LIGHTING)
            glLineWidth(3.0)
            glColor3f(1.0, 1.0, 0.8)
            
            # Draw wireframe cube
            glBegin(GL_LINE_LOOP)
            glVertex3f(-0.5, 0.5, -0.5)
            glVertex3f(0.5, 0.5, -0.5)
            glVertex3f(0.5, 0.5, 0.5)
            glVertex3f(-0.5, 0.5, 0.5)
            glEnd()
            
            glLineWidth(1.0)
            glEnable(GL_LIGHTING)
        
        glPopMatrix()
    
    def update(self, dt):
        """Update platform (for moving platforms)"""
        self.animation_time += dt
        
        if self.moving:
            # Move platform back and forth
            self.x = self.initial_x + math.sin(self.animation_time * self.move_speed) * self.move_range
    
    def get_visual_color(self):
        """Get color with special effects"""
        if self.platform_type == 'speed_boost':
            # Pulsing yellow for speed boost
            pulse = 0.5 + 0.5 * math.sin(self.animation_time * 8)
            return (1.0, 1.0, pulse * 0.5)
        elif self.platform_type == 'bounce':
            # Pulsing green for bounce
            pulse = 0.5 + 0.5 * math.sin(self.animation_time * 6)
            return (0.3, 1.0, pulse * 0.5)
        elif self.platform_type == 'slippery':
            # Icy blue
            return (0.7, 0.9, 1.0)
        elif self.platform_type == 'moving':
            # Purple for moving platforms
            return (0.8, 0.4, 0.8)
        else:
            return self.color

class LevelGenerator:
    """Generates Fall Guys style platform levels"""
    
    def __init__(self):
        self.platforms = []
        self.obstacles = []  # Add obstacles list
        self.current_z = 0
        self.platform_spacing = 4.0
        self.difficulty_increase_rate = 0.1
        
    def generate_starting_platform(self):
        """Generate the starting platform"""
        platform = Platform(0, 0, 0, width=4.0, height=0.4, depth=4.0, color=(0.2, 0.8, 0.2))
        self.platforms.append(platform)
        self.current_z = -self.platform_spacing
    
    def generate_next_platforms(self, num_platforms=3):
        """Generate next set of platforms"""
        for i in range(num_platforms):
            self.current_z -= self.platform_spacing
            
            # Create multiple platform options at this level
            self._generate_platform_level()
    
    def _generate_platform_level(self):
        """Generate a level of platforms with gaps"""
        level_platforms = []
        
        # Determine difficulty based on distance
        difficulty = min(1.0, abs(self.current_z) * self.difficulty_increase_rate / 10.0)
        
        # Platform types based on difficulty
        if difficulty < 0.3:
            # Easy: Large platforms, small gaps
            level_platforms = self._generate_easy_level()
        elif difficulty < 0.6:
            # Medium: Medium platforms, medium gaps
            level_platforms = self._generate_medium_level()
        else:
            # Hard: Small platforms, large gaps, moving platforms
            level_platforms = self._generate_hard_level()
        
        self.platforms.extend(level_platforms)
        
        # Add obstacles based on difficulty
        if difficulty > 0.2 and random.random() < 0.3:  # 30% chance for obstacles
            self._add_obstacles_to_level(difficulty)
    
    def _generate_easy_level(self):
        """Generate easy level platforms"""
        platforms = []
        
        # Create 3-4 large platforms with occasional special ones
        positions = [(-3, 0), (0, 0), (3, 0)]
        
        for i, (x, z_offset) in enumerate(positions):
            if random.random() > 0.15:  # 85% chance for each platform
                # Occasionally add special platforms
                platform_type = 'normal'
                color = (0.6, 0.6, 0.8)
                
                if random.random() < 0.2:  # 20% chance for special
                    special_type = random.choice(['speed_boost', 'bounce'])
                    if special_type == 'speed_boost':
                        platform_type = 'speed_boost'
                        color = (1.0, 1.0, 0.5)
                    elif special_type == 'bounce':
                        platform_type = 'bounce'
                        color = (0.5, 1.0, 0.5)
                
                platform = Platform(x, 0, self.current_z + z_offset, 
                                  width=2.8, height=0.3, depth=2.8, 
                                  color=color, platform_type=platform_type)
                platforms.append(platform)
        
        return platforms
    
    def _generate_medium_level(self):
        """Generate medium difficulty platforms"""
        platforms = []
        
        # Create 2-3 medium platforms with gaps and more special types
        positions = [(-4, -1), (-1, 1), (2, -0.5), (4, 0.5)]
        
        for x, z_offset in positions:
            if random.random() > 0.35:  # 65% chance for each platform
                platform_type = 'normal'
                color = (0.6, 0.6, 0.8)
                
                # More special platforms in medium difficulty
                special_chance = random.random()
                if special_chance < 0.15:
                    platform_type = 'speed_boost'
                    color = (1.0, 1.0, 0.5)
                elif special_chance < 0.25:
                    platform_type = 'bounce'
                    color = (0.5, 1.0, 0.5)
                elif special_chance < 0.35:
                    platform_type = 'slippery'
                    color = (0.7, 0.9, 1.0)
                elif special_chance < 0.4:
                    platform_type = 'moving'
                    color = (0.8, 0.4, 0.8)
                
                platform = Platform(x, random.uniform(-0.5, 0.5), self.current_z + z_offset,
                                  width=2.2, height=0.3, depth=2.2, 
                                  color=color, platform_type=platform_type)
                platforms.append(platform)
        
        return platforms
    
    def _generate_hard_level(self):
        """Generate hard difficulty platforms"""
        platforms = []
        
        # Create 1-2 small platforms with large gaps and many special types
        positions = [(-3, -1.5), (0, 0.5), (3, -0.8), (-1.5, 1.2), (1.5, -1.0)]
        
        for x, z_offset in positions:
            if random.random() > 0.55:  # 45% chance for each platform
                platform_type = 'normal'
                color = (0.8, 0.4, 0.4)
                
                # Lots of special platforms in hard difficulty
                special_chance = random.random()
                if special_chance < 0.2:
                    platform_type = 'speed_boost'
                    color = (1.0, 1.0, 0.5)
                elif special_chance < 0.35:
                    platform_type = 'bounce'
                    color = (0.5, 1.0, 0.5)
                elif special_chance < 0.55:
                    platform_type = 'slippery'
                    color = (0.7, 0.9, 1.0)
                elif special_chance < 0.75:
                    platform_type = 'moving'
                    color = (0.8, 0.4, 0.8)
                
                y_offset = random.uniform(-1.2, 1.2)
                platform = Platform(x, y_offset, self.current_z + z_offset,
                                  width=1.8, height=0.3, depth=1.8, 
                                  color=color, platform_type=platform_type)
                platforms.append(platform)
        
        return platforms
    
    def _add_obstacles_to_level(self, difficulty):
        """Add obstacles to the current level"""
        obstacle_z = self.current_z
        
        if difficulty < 0.5:
            # Easy obstacles: simple spinning bars
            if random.random() < 0.5:
                obstacle = SpinningBar(0, 1.5, obstacle_z, rotation_speed=2.0)
                self.obstacles.append(obstacle)
        else:
            # Hard obstacles: hammers and push walls
            obstacle_type = random.choice(['hammer', 'push_wall', 'spinning_bar'])
            
            if obstacle_type == 'hammer':
                x_pos = random.choice([-2, 0, 2])
                obstacle = Hammer(x_pos, 1.0, obstacle_z, rotation_speed=random.uniform(1.5, 3.0))
                self.obstacles.append(obstacle)
            elif obstacle_type == 'push_wall':
                obstacle = PushWall(0, 1.0, obstacle_z, direction=random.choice([-1, 1]))
                self.obstacles.append(obstacle)
            else:
                obstacle = SpinningBar(0, 1.5, obstacle_z, rotation_speed=random.uniform(2.0, 4.0))
                self.obstacles.append(obstacle)
    
    def get_platforms(self):
        """Get all platforms"""
        return self.platforms
    
    def check_platform_passed(self, ball_z, score):
        """Check if ball has passed platforms and update score"""
        new_score = score
        for platform in self.platforms:
            if not platform.passed and ball_z < platform.z - 1.0:
                platform.passed = True
                new_score += 1
        return new_score
    
    def cleanup_distant_platforms(self, ball_z):
        """Remove platforms that are too far behind the ball"""
        self.platforms = [p for p in self.platforms if p.z > ball_z + 20.0]
        self.obstacles = [o for o in self.obstacles if o.z > ball_z + 20.0]
    
    def should_generate_more(self, ball_z):
        """Check if we need to generate more platforms ahead"""
        if not self.platforms:
            return True
        
        furthest_z = min(p.z for p in self.platforms)
        return ball_z < furthest_z + 15.0
    
    def update_platforms(self, dt):
        """Update all platforms and obstacles"""
        for platform in self.platforms:
            platform.update(dt)
        
        for obstacle in self.obstacles:
            obstacle.update(dt)
    
    def get_obstacles(self):
        """Get all obstacles"""
        return self.obstacles
