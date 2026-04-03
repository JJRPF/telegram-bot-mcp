# Telegram Bot MCP Server

A standalone Model Context Protocol (MCP) server that integrates with the Telegram Bot API. This server enables AI agents (like Gemini, Claude, etc.) to send real-time notifications to your Telegram account and read your replies, establishing a two-way communication channel between you and the agent.

## Features
- **Send Notifications:** The agent can proactively ping you when a long-running task is complete or if it needs your attention.
- **Read Messages:** The agent can poll for new messages you send to the bot, allowing you to provide feedback, approve actions, or issue new commands directly from your phone.

## Prerequisites
- Python 3.10+
- `uv` (recommended) or `pip`
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Your Telegram Chat ID (you can get this by messaging your bot and checking the `/getUpdates` API endpoint)

## Setup & Installation

We provide an interactive script to automatically configure the MCP server with the Gemini CLI.

1. Clone this repository:
   ```bash
   git clone https://github.com/JJRPF/telegram-bot-mcp.git
   cd telegram-bot-mcp
   ```
2. Run the interactive setup:
   ```bash
   ./setup.sh
   ```
   *The script will prompt you for your Telegram Bot Token and Chat ID, and will automatically configure your Gemini CLI.*

## The Telegram Interface (Agent Watcher)

To replicate the experience of a dedicated, always-on AI agent accessible via Telegram (similar to Telegram-native AI bots), you can run the provided **Watcher** script in the background.

The Watcher connects to your Telegram bot and listens for incoming messages. When you send a message to the bot (e.g. `/resume` or `Deploy the new feature`), it automatically triggers a new Gemini CLI session in the background, passes your instructions to the AI, and the AI will execute the request and reply back directly to your phone via the MCP server.

**Run the watcher:**
```bash
# Make sure your TELEGRAM_BOT_TOKEN environment variable is exported or present in a .env file
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
uv run --with requests python watcher.py
```

Now you can close your terminal session, open Telegram, and chat with your local AI agent from anywhere!
