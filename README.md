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

## Setup

1. Clone this repository.
2. Set your environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   export TELEGRAM_CHAT_ID="your_chat_id_here"
   ```
3. Run the server (or configure your MCP client to run it):
   ```bash
   uv run --with mcp --with requests python server.py
   ```

## Using with Gemini CLI

To permanently add this server to your Gemini CLI configuration:

```bash
gemini mcp add --scope user \
  -e TELEGRAM_BOT_TOKEN="your_bot_token_here" \
  -e TELEGRAM_CHAT_ID="your_chat_id_here" \
  telegram-bot uv run --with mcp --with requests python /path/to/telegram-mcp/server.py
```
