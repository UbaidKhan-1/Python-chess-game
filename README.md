# Python Chess Game

A fully functional chess game built with Python and Pygame, featuring a complete GUI and an integrated AI bot for single-player gameplay.

## Overview

This is a complete chess game implementation that allows for both 2-player and single-player (vs AI) modes. The game includes a fully-featured graphical user interface built with Pygame and an integrated chess engine powered by minimax search with position evaluation.

## Features

- **Full Chess Game** - Complete 2-player chess gameplay with all standard rules
- **Graphical UI** - Intuitive Pygame-based interface for playing chess
- **Chess Bot** - AI opponent for single-player games with adjustable difficulty
- **Legal Move Generation** - Validates all chess moves according to official rules
- **Checkmate Detection** - Automatically detects checkmate and game end conditions
- **Position Evaluation** - Evaluates board positions to guide AI decision-making
- **Minimax Search** - AI uses minimax algorithm to find optimal moves
- **Adjustable Difficulty** - Tune bot strength by modifying the `depth` parameter in the `make_bot_move()` function

## How It Works

### Game Engine
The chess engine is built on core components:
- **Move Generation** - Generates all legal moves for the current board position
- **Evaluation Function** - Assigns numerical values to board positions
- **Minimax Algorithm** - Searches ahead to find the best move for the AI

### Adjusting Bot Difficulty
The bot's intelligence level is controlled by the `depth` parameter in the `make_bot_move()` function:
- Lower depth values = weaker, faster bot
- Higher depth values = stronger, slower bot

Experiment with different depth values to find the right difficulty level!

## Current Status

This is a foundational chess implementation that provides a complete, playable game. While fully functional, there are many opportunities for improvement:

### Future Improvements
- **Move Generation Optimization** - Improve efficiency of legal move generation
- **Enhanced Evaluation Function** - Develop more sophisticated position evaluation
- **Alpha-Beta Pruning** - Implement pruning to speed up AI search
- **Opening Book** - Add opening theory for stronger early-game play
- **Transposition Tables** - Cache evaluated positions to avoid redundant calculations
- **Move Ordering** - Improve search efficiency through better move ordering
- **UI Enhancements** - Add features like move history, game state saving, etc.

## Installation

### Requirements
- Python 3.x
- Pygame

### Setup

1. Clone the repository:
```bash
git clone https://github.com/UbaidKhan-1/Python-chess-engine.git
cd Python-chess-engine
```

2. Install dependencies:
```bash
pip install pygame
```

## Usage

Run the game with:
```bash
python chess.py
```

This will launch the chess game GUI where you can:
- Play 2-player chess
- Challenge the AI bot in single-player mode
- Adjust difficulty by modifying the `depth` parameter

## Technologies Used

- **Pygame** - For the graphical user interface
- **Python** - Core language
- **Math Module** - For handling infinity in evaluation functions
- **Time Module** - For timing and delays in gameplay

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

This is an educational hobby project. Feedback and suggestions for improvement are welcome! Feel free to open issues or submit pull requests with enhancements.