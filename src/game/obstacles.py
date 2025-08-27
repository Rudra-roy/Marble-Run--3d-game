"""
Obstacles and hazards for Fall Guys-style gameplay.
"""

import math
import random
from OpenGL.GL import *

class Hammer:
    """Rotating hammer obstacle"""
    
    def __init__(self, x, y, z, rotation_speed=2.0):
        self.x = x
        self.y = y
        self.z = z
        self.rotation_speed = rotation_speed
        self.angle = 0.0
        self.radius = 3.0
        self.hammer_length = 2.5
        
    def update(self, dt):
        """Update hammer rotation"""
        self.angle += self.rotation_speed * dt
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
    
    def render(self):
        """Render the rotating hammer"""
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        # Draw center post
        glColor3f(0.4, 0.4, 0.4)
        glPushMatrix()
        glScalef(0.3, 3.0, 0.3)
        self._draw_cube()
        glPopMatrix()
        
        # Draw rotating hammer arm
        glRotatef(math.degrees(self.angle), 0, 1, 0)
        glColor3f(0.8, 0.2, 0.2)
        
        # Hammer head
        glPushMatrix()
        glTranslatef(self.hammer_length, 0, 0)
        glScalef(0.8, 0.5, 0.5)
        self._draw_cube()
        glPopMatrix()
        
        # Hammer handle
        glPushMatrix()
        glTranslatef(self.hammer_length/2, 0, 0)
        glScalef(self.hammer_length, 0.2, 0.2)
        self._draw_cube()
        glPopMatrix()
        
        glPopMatrix()
    
    def check_collision(self, ball_pos, ball_radius):
        """Check if ball collides with hammer"""
        # Calculate hammer head position
        hammer_head_x = self.x + math.cos(self.angle) * self.hammer_length
        hammer_head_z = self.z + math.sin(self.angle) * self.hammer_length
        
        # Check distance to hammer head
        dx = ball_pos[0] - hammer_head_x
        dy = ball_pos[1] - self.y
        dz = ball_pos[2] - hammer_head_z
        
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        return distance < (ball_radius + 0.8)
    
    def _draw_cube(self):
        """Draw a simple cube"""
        glBegin(GL_QUADS)
        
        # Front face
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        
        # Back face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        
        # Top face
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        
        # Bottom face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        # Right face
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        
        # Left face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        
        glEnd()


class PushWall:
    """Moving wall that pushes players"""
    
    def __init__(self, x, y, z, direction=1):
        self.x = x
        self.y = y
        self.z = z
        self.direction = direction  # 1 for right, -1 for left
        self.speed = 1.5
        self.width = 0.5
        self.height = 2.0
        self.depth = 6.0
        self.push_force = 8.0
        
    def update(self, dt):
        """Update wall position"""
        self.x += self.direction * self.speed * dt
        
        # Reverse direction at boundaries
        if abs(self.x) > 4.0:
            self.direction *= -1
    
    def render(self):
        """Render the push wall"""
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glScalef(self.width, self.height, self.depth)
        
        glColor3f(0.9, 0.4, 0.1)  # Orange color
        self._draw_cube()
        
        glPopMatrix()
    
    def check_collision(self, ball_pos, ball_radius):
        """Check collision and return push force if colliding"""
        dx = abs(ball_pos[0] - self.x)
        dy = abs(ball_pos[1] - self.y)
        dz = abs(ball_pos[2] - self.z)
        
        if (dx < self.width/2 + ball_radius and
            dy < self.height/2 + ball_radius and
            dz < self.depth/2 + ball_radius):
            
            # Return push force in wall's direction
            return (self.direction * self.push_force, 0)
        
        return (0, 0)
    
    def _draw_cube(self):
        """Draw a simple cube"""
        glBegin(GL_QUADS)
        
        # Front face
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        
        # Back face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        
        # Top face
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        
        # Bottom face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        # Right face
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        
        # Left face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        
        glEnd()


class SpinningBar:
    """Horizontal spinning bar obstacle"""
    
    def __init__(self, x, y, z, rotation_speed=3.0):
        self.x = x
        self.y = y
        self.z = z
        self.rotation_speed = rotation_speed
        self.angle = 0.0
        self.length = 4.0
        self.thickness = 0.3
        
    def update(self, dt):
        """Update bar rotation"""
        self.angle += self.rotation_speed * dt
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
    
    def render(self):
        """Render the spinning bar"""
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(math.degrees(self.angle), 0, 1, 0)
        
        glColor3f(0.6, 0.3, 0.8)  # Purple color
        glScalef(self.length, self.thickness, self.thickness)
        self._draw_cube()
        
        glPopMatrix()
    
    def check_collision(self, ball_pos, ball_radius):
        """Check if ball collides with spinning bar"""
        # Calculate bar endpoints
        bar_end1_x = self.x + math.cos(self.angle) * self.length/2
        bar_end1_z = self.z + math.sin(self.angle) * self.length/2
        bar_end2_x = self.x - math.cos(self.angle) * self.length/2
        bar_end2_z = self.z - math.sin(self.angle) * self.length/2
        
        # Check distance to bar line
        # Simplified collision: check distance to center and if within bar range
        dx = ball_pos[0] - self.x
        dy = ball_pos[1] - self.y
        dz = ball_pos[2] - self.z
        
        distance_to_center = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance_to_center < self.length/2 + ball_radius and abs(dy) < self.thickness + ball_radius:
            return True
        
        return False
    
    def _draw_cube(self):
        """Draw a simple cube"""
        glBegin(GL_QUADS)
        
        # All faces of the cube
        vertices = [
            (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),  # Front
            (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5),  # Back
            (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5),  # Top
            (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5),  # Bottom
            (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5),  # Right
            (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)  # Left
        ]
        
        for i in range(0, len(vertices), 4):
            for j in range(4):
                glVertex3f(*vertices[i + j])
        
        glEnd()
