#!/usr/bin/env bash

# Telegram MCP Server Setup Script for Gemini CLI

echo "Welcome to the Telegram MCP Server Setup for Gemini CLI!"
echo ""

read -p "Please enter your Telegram Bot Token (from @BotFather): " BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
    echo "Error: Bot Token cannot be empty."
    exit 1
fi

read -p "Please enter your Telegram Chat ID: " CHAT_ID
if [ -z "$CHAT_ID" ]; then
    echo "Error: Chat ID cannot be empty."
    exit 1
fi

echo ""
echo "Adding Telegram MCP Server to your Gemini CLI configuration..."

gemini mcp add --scope user \
  -e TELEGRAM_BOT_TOKEN="$BOT_TOKEN" \
  -e TELEGRAM_CHAT_ID="$CHAT_ID" \
  telegram-bot uv run --with mcp --with requests python "$(pwd)/server.py"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully added the Telegram MCP server!"
    echo "You can now use Gemini CLI to send and receive Telegram messages."
    echo "Try asking Gemini: 'Ping me on Telegram.'"
else
    echo ""
    echo "❌ Failed to add the MCP server. Please check your Gemini CLI installation."
fi
