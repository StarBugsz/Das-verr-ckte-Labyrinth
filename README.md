# Labyrinth Game

This project is a multiplayer labyrinth game implemented using Flask for the backend and WebSockets for real-time communication. The frontend is built using Babylon.js for rendering the game and react.js for the lobby selection.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [WebSocket API](#websocket-api)
- [Frontend](#frontend)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```sh
    git clone https://gitlab2.informatik.uni-wuerzburg.de/softwarepraktikum/ws24_labyrinth.git
    cd labyrinth-game
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```
### Docker
There is a Docker image available. You can use it by executing `docker load < ws24_labyrinth_dev_docker.tar`, then run it with the ports `docker run -p 5000:5000 -p 8765:8765 ws24_labyrinth/development`
## Usage

1. Start the Flask server:
    ```sh
    python app.py
    ```

2. Open your browser and navigate to `http://localhost:5000`.

## WebSocket API

### Messages

- **set_username:** Set the username for the player.
    ```json
    {
        "action": "set_username",
        "username": "player1"
    }
    ```

- **create_lobby:** Create a new lobby.
    ```json
    {
        "action": "create_lobby"
    }
    ```

- **join_lobby:** Join an existing lobby.
    ```json
    {
        "action": "join_lobby",
        "link": "lobby_link"
    }
    ```

- **start_game:** Start the game in the lobby.
    ```json
    {
        "action": "start_game"
    }
    ```

- **move:** Move the player to a new position.
    ```json
    {
        "action": "move",
        "position": "x,y"
    }
    ```

- **set_tile:** Set a tile on the board.
    ```json
    {
        "action": "set_tile",
        "position": "x,y"
    }
    ```

- **insert_tile:** Insert a tile on the board.
    ```json
    {
        "action": "insert_tile",
        "position": "x,y"
    }
    ```

- **rotate90:** Rotate the current tile by 90 degrees.
    ```json
    {
        "action": "rotate90"
    }
    ```

- **kick_player:** Kick a player from the lobby.
    ```json
    {
        "action": "kick_player",
        "player_number": "player_number"
    }
    ```

## Frontend

The frontend consists of two parts:
### Lobby
The lobby is built with react.js and vite. The project files are in `Frontend/`, the build in `Frontend/dist/`. The entry point is `Frontend/dist/index.html`, routed from `localhost:5000/`.
### Game
The game frontend is built using Babylon.js for rendering the game. The main entry point for the frontend is `static/index.html`. The external routing is `localhost:5000/game/{uid}`, with uid being the unique id the player receives on the lobby page. A valid uid (player must exist, be in a lobby, and the game must be started) is required, otherwise the page remains blank.
### WebSocket Communication

The frontend communicates with the backend using WebSockets. The `socket.onmessage` handler processes incoming messages and updates the game state accordingly.

## How to play
The goal is to collect all treasures. The current treasure is shown in the bar at the top, as is the current player. After all treasures are collected, the player has to return to his starting point. The first player to achieve this, wins.

### Tile insertion
Every round, a tile must be inserted by clickin on one of the arrows around the playing field. By clicking the large straight arrow at the bottom right, the tile is inserted. The circular arrow rotates the tile clockwise. The excess tile on the other side is ejected and becomes the new tile to insert. It is not allowed to insert the tile back to where it just ejected.
### Player Movement

The player can be moved by clicking on a target tile. If the tile is not in range, an error message is logged to the console and no action is executed. To move a player, a tile must first be inserted. If the tile contains the treasure the player is currently seeking, it is marked as found. If the game is over, a winning screen appears.
