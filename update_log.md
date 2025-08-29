# Marble Run - Local Multiplayer Split Screen Implementation

## Overview
Successfully implemented Local Multiplayer mode with split-screen functionality, allowing two players to play simultaneously on the same device.

## Key Features Added

### 1. Game Mode Selection
- Added support for Single Player (WASD + Space) and Two Player Mode (Split Screen)
- Game mode selection is stored in `game_settings` and immediately applied

### 2. Split Screen Rendering
- **Left Viewport**: Player 1 (Blue ball) - controlled with WASD + Space
- **Right Viewport**: Player 2 (Red ball) - controlled with Arrow Keys + Enter
- Each viewport has its own camera following the respective player
- Independent perspective matrices for proper aspect ratios

### 3. Two Player State Management
- **Player 1**: Original ball physics and scoring system
- **Player 2**: Complete duplicate state including:
  - Position, velocity, physics
  - Independent scoring and platform tracking
  - Separate game over state
  - High score and best time tracking

### 4. Input Handling Updates
- **Player 1 Controls**: WASD for movement, Space for jump
- **Player 2 Controls**: Arrow keys for movement, Enter for jump
- Added special key press/release handling for arrow keys
- Input routing through `InputHandler` to `Game3DScreen`

### 5. Physics and Gameplay
- Both players share the same platform layout and obstacles
- Independent collision detection and platform interaction
- Separate physics updates for each player
- Platform movement affects both players when standing on them

### 6. UI and HUD
- **Single Player**: Full score card with detailed stats
- **Two Player**: Minimal HUD per viewport showing:
  - Current score
  - Controls reminder
  - Position and velocity info
  - Game over state per player

### 7. Game State Management
- Automatic mode detection on screen enter/render
- Proper game reset for both players
- R key restarts the entire match in both modes
- ESC returns to main menu from either mode

## Technical Implementation

### Files Modified
1. **`src/core/game_engine.py`**
   - Added `glutSpecialUpFunc` registration for arrow key release

2. **`src/core/input_handler.py`**
   - Routed special key events to game screen
   - Added `special_keys_up` handler

3. **`src/screens/game_3d_screen.py`**
   - Added multiplayer state variables
   - Implemented split-screen rendering with viewports
   - Added Player 2 physics and collision systems
   - Created per-player UI rendering functions
   - Added special key handling for Player 2

### Core Changes
- **Split Screen**: Uses `glViewport()` to create two rendering areas
- **Camera System**: `_update_camera_for_player()` for per-player views
- **Physics Duplication**: Complete Player 2 physics mirroring Player 1
- **Input Mapping**: Arrow keys → Player 2 movement, Enter → Player 2 jump
- **State Synchronization**: Real-time mode switching based on `game_settings`

## User Experience
- **Single Player**: Unchanged gameplay with WASD + Space
- **Two Player**: 
  - Choose "Two Player Mode" in Game Mode Selection
  - Screen splits into left/right views
  - Both players can play simultaneously
  - Independent scoring and progress tracking
  - R key restarts both players when either dies

## Performance Considerations
- Efficient viewport switching with depth buffer clearing
- Shared platform rendering (drawn once per frame)
- Minimal UI overhead in multiplayer mode
- Proper OpenGL state management between viewports

## Future Enhancements
- Vertical split option (top/bottom)
- Visual divider line between viewports
- Cooperative gameplay mechanics
- Shared power-ups or obstacles
- Network multiplayer support
