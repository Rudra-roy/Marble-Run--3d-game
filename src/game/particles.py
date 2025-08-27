"""
Particle effects for enhanced visual feedback.
"""

import math
import random
from OpenGL.GL import *

class Particle:
    """Individual particle for effects"""
    
    def __init__(self, x, y, z, vx=0, vy=0, vz=0, color=(1,1,1), life=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.color = color
        self.life = life
        self.max_life = life
        self.size = random.uniform(0.05, 0.15)
    
    def update(self, dt):
        """Update particle position and life"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        
        # Apply gravity to particles
        self.vy -= 5.0 * dt
        
        # Reduce life
        self.life -= dt
        
        return self.life > 0
    
    def render(self):
        """Render the particle"""
        alpha = self.life / self.max_life
        glColor4f(self.color[0], self.color[1], self.color[2], alpha)
        
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glScalef(self.size, self.size, self.size)
        
        # Draw a simple quad for particle
        glBegin(GL_QUADS)
        glVertex3f(-0.5, -0.5, 0)
        glVertex3f(0.5, -0.5, 0)
        glVertex3f(0.5, 0.5, 0)
        glVertex3f(-0.5, 0.5, 0)
        glEnd()
        
        glPopMatrix()


class ParticleSystem:
    """Manages multiple particle effects"""
    
    def __init__(self):
        self.particles = []
    
    def add_explosion(self, x, y, z, color=(1.0, 0.8, 0.2), count=15):
        """Add explosion effect"""
        for _ in range(count):
            vx = random.uniform(-3, 3)
            vy = random.uniform(1, 4)
            vz = random.uniform(-3, 3)
            life = random.uniform(0.5, 1.5)
            
            particle = Particle(x, y, z, vx, vy, vz, color, life)
            self.particles.append(particle)
    
    def add_trail(self, x, y, z, color=(0.5, 0.8, 1.0)):
        """Add trail effect for ball movement"""
        if random.random() < 0.3:  # Don't spawn too many
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(-0.5, 0.5)
            vz = random.uniform(-0.5, 0.5)
            life = random.uniform(0.2, 0.8)
            
            particle = Particle(x, y, z, vx, vy, vz, color, life)
            self.particles.append(particle)
    
    def add_platform_hit(self, x, y, z, color=(0.8, 0.8, 0.8)):
        """Add effect when ball hits platform"""
        for _ in range(8):
            vx = random.uniform(-1, 1)
            vy = random.uniform(0.5, 2)
            vz = random.uniform(-1, 1)
            life = random.uniform(0.3, 0.8)
            
            particle = Particle(x, y, z, vx, vy, vz, color, life)
            self.particles.append(particle)
    
    def update(self, dt):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def render(self):
        """Render all particles"""
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for particle in self.particles:
            particle.render()
        
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
    
    def clear(self):
        """Clear all particles"""
        self.particles = []
