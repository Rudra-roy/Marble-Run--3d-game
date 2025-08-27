#!/usr/bin/env python3
"""
Marble Run - A Rolling Ball Adventure
Main entry point for the game.
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.game_engine import GameEngine

def main():
    """Main entry point for Marble Run"""
    print("Starting Marble Run...")
    
    # Create and run the game engine
    engine = GameEngine()
    engine.run()

if __name__ == "__main__":
    main()
