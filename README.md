# Marble Run - A 3D Fall Guys-Style Platformer

A 3D OpenGL-based platformer game inspired by Fall Guys, built with Python and PyOpenGL. Navigate a ball through challenging moving platforms with physics-based gameplay.

## 🎮 Game Overview

Marble Run is a Fall Guys-inspired 3D platformer where you control a ball through a series of challenging platforms. Each platform presents unique obstacles:

- **Static Platform**: Safe starting area (Green)
- **Moving Platform**: Slides side-to-side (Red) 
- **Tilting Platform**: Rocks back and forth (Blue)
- **Forward-Back Platform**: Moves in Z-direction (Yellow)
- **Rotating Tilt Platform**: Complex multi-axis tilting (Magenta)

### 🏆 Scoring System
- **100 points** for reaching Platform 1
- **200 points** for reaching Platform 2  
- **300 points** for reaching Platform 3
- **400 points** for reaching Platform 4
- **500 points** for reaching Platform 5
- **1000 bonus points** for completing all platforms
- **Timer tracking** for best completion times
- **High score tracking** across sessions

## 🎯 Features

### Core Gameplay
- **Physics-Based Ball Movement**: Realistic ball physics with gravity, friction, and momentum
- **Moving Platform Physics**: Ball moves with platforms when standing on them (80% coupling)
- **Enhanced Jump Mechanics**: Controlled jumping with ground detection
- **Fall Detection**: Game over when falling below platforms
- **Score Card UI**: Real-time display of score, timer, and progress

### Platform Mechanics
- **Dynamic Movement**: Platforms move using sine/cosine functions for smooth motion
- **Velocity Tracking**: Platform movement affects ball position
- **Collision Detection**: Precise ball-platform collision with bounce effects
- **Tilting Effects**: Platforms tilt and rotate adding challenge

### UI System
- **Loading Screen**: Animated loading with progress indicator
- **Main Menu**: Keyboard-navigable menu system
- **Options Menu**: Sound volume, text size, and difficulty settings
- **Game Mode Selection**: Single/multiplayer mode selection
- **In-Game HUD**: Score card, controls, position/velocity display
- **Game Over Screen**: Restart options and statistics

## 📁 Project Structure

```
Marble-Run--3d-game/
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies  
├── assets/                    # Game assets
│   └── bg_1.png              # Background texture
├── src/                      # Source code
│   ├── core/                 # Core game systems
│   │   ├── game_engine.py    # Main game orchestrator
│   │   ├── state_manager.py  # Screen state transitions
│   │   ├── opengl_manager.py # OpenGL setup and texture management
│   │   ├── input_handler.py  # Keyboard input processing
│   │   └── settings.py       # Game configuration
│   ├── screens/              # Game screens
│   │   ├── base_screen.py    # Base screen interface
│   │   ├── loading_screen.py # Loading screen with animations
│   │   ├── main_menu_screen.py         # Main menu
│   │   ├── options_menu_screen.py      # Settings menu
│   │   ├── game_mode_selection_screen.py # Mode selection
│   │   └── game_3d_screen.py # Main 3D game (PRIMARY GAMEPLAY)
│   ├── ui/                   # UI rendering utilities
│   │   └── renderer.py       # Text and UI component rendering
│   └── game/                 # Game-specific logic (future expansion)
└── OpenGL/                   # PyOpenGL library files
```

## 🕹️ Controls

### Menu Navigation
- **Arrow Keys**: Navigate menu options
- **Enter**: Select menu items  
- **Escape**: Go back or quit

### Game Controls
- **W**: Move ball forward (negative Z)
- **S**: Move ball backward (positive Z)
- **A**: Move ball left (negative X)
- **D**: Move ball right (positive X)
- **Spacebar**: Jump (only when on ground)
- **R**: Restart game (when game over)
- **Escape**: Return to main menu

## 🛠️ Technical Implementation

### Core Systems Architecture

#### GameEngine (`src/core/game_engine.py`)
- **Main Orchestrator**: Initializes all subsystems and manages main loop
- **Screen Management**: Handles screen initialization and transitions
- **Update Loop**: 60 FPS game loop with delta time calculations
- **Cleanup**: Proper resource management and shutdown

#### Game3DScreen (`src/screens/game_3d_screen.py`) - **PRIMARY COMPONENT**
The heart of the game containing:

**Physics System:**
```python
# Physics constants
gravity = -15.0
max_speed = 10.0 
acceleration = 18.0
jump_force = 8.0
ground_friction = 0.85
air_friction = 0.98
```

**Platform System:**
- Platform creation with movement types (static, horizontal, tilt, etc.)
- Real-time position and velocity tracking
- Ball-platform coupling for moving platforms

**Scoring System:**
- Platform progress tracking using `platforms_reached` set
- Point calculation: `(platform_index + 1) * 100`
- Timer management and best time tracking

**Rendering Pipeline:**
- 3D scene rendering with lighting
- Camera following ball movement  
- UI overlay with score card
- Debug information display

#### StateManager (`src/core/state_manager.py`)
- **State Transitions**: Smooth transitions between screens
- **Animation System**: Fade effects and timing
- **State Stack**: Manages current and previous states

#### OpenGLManager (`src/core/opengl_manager.py`)
- **OpenGL Initialization**: Window setup and OpenGL context
- **Projection Management**: 2D/3D projection switching
- **Texture Loading**: Image asset management with PIL

#### InputHandler (`src/core/input_handler.py`)
- **Keyboard Processing**: GLUT keyboard callback handling
- **Event Routing**: Routes input to appropriate screen handlers
- **Key State Management**: Tracks key press/release states

### Key Algorithms

**Platform Movement Calculation:**
```python
# Horizontal movement using sine wave
offset = math.sin(current_time * move_speed) * move_range
platform['x'] = base_x + offset

# Velocity calculation for ball coupling
platform['vel_x'] = (new_x - prev_x) / dt
```

**Ball-Platform Coupling:**
```python
# Apply 80% of platform velocity to ball
self.ball_x += platform_vel_x * dt * 0.8
```

**Collision Detection:**
```python
# Check if ball is within platform bounds
if (px - pw/2 <= ball_x <= px + pw/2 and
    pz - pd/2 <= ball_z <= pz + pd/2 and
    ball_bottom <= platform_top):
    # Handle collision
```

## 📋 Requirements

- **Python 3.6+**
- **PyOpenGL** - OpenGL bindings for Python
- **PyOpenGL-accelerate** (optional) - Performance improvements
- **Pillow (PIL)** - Image loading and processing

## 🚀 Installation & Running

1. **Install Dependencies:**
   ```bash
   pip install PyOpenGL PyOpenGL-accelerate Pillow
   ```

2. **Run the Game:**
   ```bash
   cd Marble-Run--3d-game
   python main.py
   ```

3. **Navigate to Game:**
   - Use arrow keys in menus
   - Select "Single Player" → "Start Game"
   - Use WASD + Spacebar to play

## 🎯 Game Design Features

### Physics Tuning
- **Reduced Jump Height**: `jump_force = 8.0` for more controlled movement
- **Speed Limiting**: `max_speed = 10.0` prevents excessive velocity
- **Platform Coupling**: 80% movement transfer feels natural
- **Friction System**: Different friction for ground vs. air

### Platform Design
- **Progressive Difficulty**: Platforms get more challenging
- **Strategic Spacing**: Platforms positioned for skilled but achievable jumps
- **Visual Coding**: Each platform type has distinct colors
- **Movement Patterns**: Predictable but challenging timing

### User Experience
- **Visual Feedback**: Score card, position display, velocity indicators  
- **Clear Controls**: Simple WASD + Space control scheme
- **Immediate Restart**: R key for quick restarts
- **Progress Tracking**: Persistent high scores and best times

## 🔧 Development Guide

### Adding New Platform Types
1. **Define Movement Type** in `_create_platforms()`:
   ```python
   'movement_type': 'your_new_type'
   ```

2. **Implement Movement Logic** in `_update_platform_movements()`:
   ```python
   elif movement_type == 'your_new_type':
       # Your movement code here
   ```

3. **Add Velocity Tracking** for ball coupling

### Adding New Screens
1. **Create Screen Class** inheriting from `BaseScreen`
2. **Implement `render()` method**  
3. **Add to GameEngine initialization**
4. **Define state constant** in StateManager

### Modifying Physics
Key physics values in `Game3DScreen.__init__()`:
- `gravity`: Downward acceleration
- `jump_force`: Initial jump velocity
- `max_speed`: Maximum horizontal velocity
- `acceleration`: Movement responsiveness
- `ground_friction`: Surface friction coefficient

## 🎮 Game Balance

The game is tuned for:
- **Challenging but Fair**: Requires skill but not frustration
- **Progressive Difficulty**: Each platform adds complexity
- **Risk/Reward**: Higher platforms give more points
- **Replayability**: Timer and score encourage multiple attempts

## 🚧 Future Enhancements

### Planned Features
- **Multiple Levels**: Additional platform courses
- **Power-ups**: Temporary abilities (higher jump, slower platforms)
- **Multiplayer**: Race against other players
- **Leaderboards**: Online score comparison
- **Custom Levels**: Level editor and sharing
- **Audio System**: Sound effects and background music
- **Particle Effects**: Visual polish and feedback
- **Mobile Controls**: Touch-based input support

### Technical Improvements
- **Asset Pipeline**: Better resource management
- **Save System**: Persistent player progress
- **Performance Optimization**: Better rendering efficiency  
- **Error Handling**: Robust error recovery
- **Configuration**: User-customizable settings
- **Accessibility**: Colorblind support, larger text options

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This game represents a complete transformation from a simple marble run to a fully-featured Fall Guys-style platformer with sophisticated physics, scoring, and user interface systems.
