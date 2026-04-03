import os
import time
import requests
import sys
import subprocess

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
STATE_FILE = ".telegram_offset"

def get_offset():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                pass
    return None

def save_offset(offset):
    with open(STATE_FILE, "w") as f:
        f.write(str(offset))

def poll_for_messages():
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
        sys.exit(1)
        
    print("Telegram Watcher is running. Waiting for messages... (Press Ctrl+C to stop)")
    while True:
        offset = get_offset()
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset

        try:
            res = requests.get(url, params=params, timeout=40)
            if res.ok:
                updates = res.json().get("result", [])
                highest_update_id = 0
                
                for u in updates:
                    update_id = u.get("update_id", 0)
                    if update_id > highest_update_id:
                        highest_update_id = update_id
                        
                    msg = u.get("message", {})
                    text = msg.get("text", "")
                    
                    if text:
                        print(f"\n[Telegram] Received: {text}")
                        # Check for /resume or other commands to trigger Gemini
                        if text.strip() == "/resume":
                            print("[Watcher] Triggering Gemini CLI...")
                            subprocess.run(["gemini", "I have resumed the session via Telegram! Please ping me on Telegram to ask what you can help with next."])
                        else:
                            print(f"[Watcher] Passing message to Gemini CLI...")
                            subprocess.run(["gemini", f"The user just sent you a message on Telegram: '{text}'. Please process their request, and when you are done, reply to them using the Telegram MCP send_telegram_message tool."])
                
                if highest_update_id > 0:
                    save_offset(highest_update_id + 1)
        except requests.exceptions.RequestException:
            pass
            
        time.sleep(2)

if __name__ == "__main__":
    poll_for_messages()
