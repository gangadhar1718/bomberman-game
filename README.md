
# Bomberman Game

A classic Bomberman-style game built with Pygame featuring multiple levels, enemies, and destructible environments.

![Bomberman Game Screenshot](screenshots/gameplay.png)

## Features

- Classic Bomberman arcade-style graphics with animated enemies
- Grid-based movement system
- Destructible and indestructible walls with improved textures
- Bomb placement and explosions with animations and sound effects
- Enemy AI with random movement and unique character designs
- Multiple levels with increasing difficulty
- Hidden exit gates to progress to the next level
- Win and lose conditions with game over screens
- Background music and sound effects

## File Structure

```
bomberman-game/
│
├── main.py                 # Main game file with all game logic
├── README.md               # This file
├── requirements.txt        # Python dependencies
│
├── assets/                 # Game assets directory
│   ├── enemy1.png           # Enemy sprite 1 (optional)
│   ├── enemy2.png           # Enemy sprite 2 (optional)
│   └── enemy3.png           # Enemy sprite 3 (optional)
│
└── screenshots/            # Screenshots for documentation
   └── gameplay.png        # Game screenshot for README
```

## Requirements

- Python 3.x
- Pygame

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/yourusername/bomberman-game.git
    cd bomberman-game
    ```

2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the game:

    ```bash
    python main.py
    ```

## How to Play

### Controls

- **Arrow Keys**: Move the player
- **X Key**: Place a bomb
- **I Key**: Enter the exit gate to proceed to next level
- **R**: Restart the game after losing
- **Escape**: Quit the game

### Game Rules

1. Navigate through the maze using the arrow keys
2. Place bombs with the X key to destroy destructible blocks and enemies
3. Avoid getting caught in your own bomb explosions
4. Avoid touching enemies - direct contact will kill you
5. Destroy all enemies to reveal the exit gate
6. Find the exit gate and press I to proceed to the next level
7. Each level has more enemies than the previous one
8. If you get caught in an explosion or touch an enemy, you lose

## Development Notes

The game is built entirely in Python using the Pygame library. All game logic is contained in `main.py` with the following key components:

- Grid-based game world (0=empty, 1=wall, 2=destructible block, 3=hidden gate, 4=visible gate)
- Player class with movement and collision detection
- Enemy class with simple AI for random movement
- Bomb class with explosion mechanics
- Level progression system

The game will use built-in fallback graphics if the asset files are not found, making it playable even without the optional asset files.

## Credits

This game was created as a learning project and is inspired by the classic Bomberman game series.

## License

[MIT License](LICENSE)

To complete the repository setup, you should also create:

1. A `requirements.txt` file with:
    ```
    pygame>=2.1.0
    ```

2. A `screenshots` folder with at least one gameplay screenshot (you can take this once your game is running)

3. Make sure your `assets` folder is included in the repository structure, even if it's empty. You can add a `.gitkeep` file to ensure the folder is tracked by Git.

This README provides clear instructions for anyone who wants to clone and run your game, explains the file structure, and includes detailed gameplay instructions. The development notes section gives other developers insight into how the game is structured if they want to modify or learn from your code.
