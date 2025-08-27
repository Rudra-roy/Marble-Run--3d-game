# Marble Run - A Rolling Ball Adventure

A 3D OpenGL-based game inspired by Fall Guys, built with Python and PyOpenGL.

## Project Structure

```
marble_run/
├── main.py                    # Main entry point
├── assets/                    # Game assets (images, sounds, etc.)
│   └── bg_1.png              # Background image
├── src/                      # Source code
│   ├── core/                 # Core game systems
│   │   ├── __init__.py
│   │   ├── game_engine.py    # Main game engine
│   │   ├── state_manager.py  # Game state management
│   │   ├── opengl_manager.py # OpenGL initialization and management
│   │   ├── input_handler.py  # Input handling system
│   │   └── settings.py       # Game settings and configuration
│   ├── screens/              # Game screens
│   │   ├── __init__.py
│   │   ├── base_screen.py    # Base screen class
│   │   ├── loading_screen.py # Loading screen implementation
│   │   ├── main_menu_screen.py         # Main menu
│   │   ├── options_menu_screen.py      # Options menu
│   │   ├── game_mode_selection_screen.py # Game mode selection
│   │   └── game_3d_screen.py # 3D game space
│   ├── ui/                   # UI components and utilities
│   │   ├── __init__.py
│   │   └── renderer.py       # UI rendering utilities
│   └── game/                 # Game-specific logic (for future expansion)
│       └── __init__.py
└── README.md                 # This file
```

## Features

- **Loading Screen**: Animated loading screen with title and progress indicator
- **Main Menu**: Navigable main menu with keyboard controls
- **Options Menu**: Settings for sound volume, text size, and difficulty
- **Game Mode Selection**: Choose between single player and two player modes
- **3D Game Space**: Placeholder 3D environment with grid and camera setup
- **Smooth Transitions**: Animated transitions between screens
- **Modular Architecture**: Clean separation of concerns with organized code structure

## Controls

- **Arrow Keys**: Navigate menus
- **Enter**: Select menu items
- **Escape**: Go back or quit
- **Left/Right**: Adjust settings in options menu
- **WASD**: Move the ball in 3D game
- **Spacebar**: Jump (when ball is on ground)
- **R**: Restart game (when game over)

## Requirements

- Python 3.6+
- PyOpenGL
- PyOpenGL-accelerate (optional, for better performance)
- Pillow (PIL) for image loading

## Installation

1. Install dependencies:
   ```bash
   pip install PyOpenGL PyOpenGL-accelerate Pillow
   ```

2. Run the game:
   ```bash
   cd marble_run
   python main.py
   ```

## Architecture Overview

### Core Systems

- **GameEngine**: Main orchestrator that initializes and manages all subsystems
- **StateManager**: Handles game state transitions and animations
- **OpenGLManager**: Manages OpenGL initialization and texture loading
- **InputHandler**: Processes keyboard input and routes to appropriate handlers
- **GameSettings**: Centralized configuration management

### Screen System

All screens inherit from `BaseScreen` and implement the `render()` method. The screen system allows for:
- Easy addition of new screens
- Consistent state management
- Shared rendering utilities
- Smooth transitions between screens

### UI System

The UI system provides reusable components for:
- Text rendering with different fonts and styles
- Menu item highlighting and selection
- Animated backgrounds and effects
- Loading animations

## Future Expansion

The modular architecture makes it easy to add:
- **Physics System**: Ball physics and collision detection
- **Level System**: Level loading and progression
- **Audio System**: Sound effects and background music
- **Particle System**: Visual effects and polish
- **Networking**: Multiplayer support
- **Asset Manager**: Efficient resource loading and caching

## Development

To add a new screen:

1. Create a new class inheriting from `BaseScreen` in `src/screens/`
2. Implement the `render()` method
3. Add the screen to the game engine's screen initialization
4. Add appropriate input handling if needed

To add new UI components:
1. Add static methods to `UIRenderer` class in `src/ui/renderer.py`
2. Follow the existing patterns for consistency

## License

This project is open source and available under the MIT License.
