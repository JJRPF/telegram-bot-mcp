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

## The Telegram Interface (Background Watcher)

To run a headless agent that wakes up when you text it, you can run the provided **Watcher** script in the background.

When you send a message to the bot (e.g. `Deploy the new feature`), it automatically triggers a new headless Gemini CLI session in the background, passes your instructions to the AI, and the AI will execute the request and reply back directly to your phone via the MCP server.

**Run the watcher:**
```bash
uv run --with requests python watcher.py
```

## Interactive Remote Control (gemini-rc.py)

If you want the exact experience of **Claude Code Remote Control**, where you start a session in your terminal that you can control *both* locally and remotely via Telegram at the same time:

1. Open your terminal and start the remote control wrapper:
   ```bash
   uv run --with requests --with pexpect python gemini-rc.py
   ```
2. You will see the normal Gemini CLI prompt locally. You can type commands directly into your keyboard as usual.
3. If you step away from your computer, simply message your Telegram bot. The script will intercept your text, type it directly into the running terminal session, and tell Gemini to reply to your phone!
4. When you return to your computer, you will see all the work Gemini did right there on your screen, in the exact same session!

To stop the session, either type `exit` in the terminal, or text `/stop` on Telegram.
