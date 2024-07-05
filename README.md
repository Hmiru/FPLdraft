# FPLdraft

FPLdraft is a Fantasy Premier League draft system built using Python and Discord Bot. This project allows users to perform a fantasy draft where they can select players in turns, either manually or automatically by AI.

## Features

- **Discord Bot Integration**: Perform drafts within a Discord server.
- **AI Draft**: The AI can automatically select players based on predefined rules.
- **Snake Draft Order**: Implements snake draft order to ensure fairness.
- **Status Updates**: Provides real-time status updates during the draft process.
- **Draft Reset**: Ability to reset the draft and start over.

## Getting Started

### Prerequisites

Ensure you have the following installed:
- Python 3.8 or higher
- `pip` (Python package installer)

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/Hmiru/FPLdraft.git
    cd FPLdraft
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

### Setting Up the Discord Bot

1. Create a `.env` file in the project root directory and add your Discord bot token:

    ```sh
    DISCORD_BOT_TOKEN=your_discord_bot_token
    ```

2. Make sure to not commit your `.env` file by including it in your `.gitignore`.

### Running the Bot

To run the bot, use the following command:

```sh
python src/dbot.py
```

### Commands
```sh
!start_draft <total_players> <number_of_humans> <rounds>: Starts a new draft.
!show_status: Shows the current draft status.
!reset_draft: Resets the draft.
```

## Running Locally (without Discord)
You can also run the draft locally without using Discord. Run the following command to start the local draft:

```sh
python src/on_da_local.py
