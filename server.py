from mcp.server.fastmcp import FastMCP
import requests
import json
import os

mcp = FastMCP("Telegram Bot")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
STATE_FILE = ".telegram_offset"

def get_offset():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return int(f.read().strip())
    return None

def save_offset(offset):
    with open(STATE_FILE, "w") as f:
        f.write(str(offset))

@mcp.tool()
def send_telegram_message(message: str) -> str:
    """Send a real-time notification to the user via Telegram."""
    if not BOT_TOKEN or not CHAT_ID:
        return "Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables are not set."
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    if response.ok:
        return "Message sent successfully."
    else:
        return f"Failed to send message: {response.text}"

@mcp.tool()
def read_telegram_messages() -> str:
    """Read new messages sent by the user to the bot since the last time this tool was called. Use this to poll for user feedback."""
    if not BOT_TOKEN:
        return "Error: TELEGRAM_BOT_TOKEN environment variable is not set."
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    offset = get_offset()
    params = {}
    if offset:
        params["offset"] = offset

    response = requests.get(url, params=params)
    if response.ok:
        updates = response.json().get("result", [])
        if not updates:
            return "No new messages from the user."
        
        messages = []
        highest_update_id = 0
        
        for u in updates:
            update_id = u.get("update_id", 0)
            if update_id > highest_update_id:
                highest_update_id = update_id
                
            msg = u.get("message", {})
            text = msg.get("text", "")
            if text:
                messages.append(text)
        
        # Save the next offset to mark these as read
        if highest_update_id > 0:
            save_offset(highest_update_id + 1)
            
        if not messages:
            return "No new text messages."
            
        return "New messages from the user:\n- " + "\n- ".join(messages)
        
    return f"Failed to read messages: {response.text}"

if __name__ == "__main__":
    # We clear the initial history so old messages (like /start) don't get pulled in later
    if BOT_TOKEN:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        res = requests.get(url)
        if res.ok:
            updates = res.json().get("result", [])
            if updates:
                highest_id = max(u.get("update_id", 0) for u in updates)
                save_offset(highest_id + 1)
            
    mcp.run(transport="stdio")
