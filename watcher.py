import os
import time
import requests
import sys
import subprocess
import json

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
STATE_FILE = ".telegram_offset"
SESSION_STATE_FILE = ".telegram_session"

# Defaults
current_session = "latest"
current_model = None

def load_session_state():
    global current_session, current_model
    if os.path.exists(SESSION_STATE_FILE):
        try:
            with open(SESSION_STATE_FILE, "r") as f:
                state = json.load(f)
                current_session = state.get("active_session", "latest")
                current_model = state.get("active_model", None)
        except Exception:
            pass

def save_session_state():
    with open(SESSION_STATE_FILE, "w") as f:
        json.dump({"active_session": current_session, "active_model": current_model}, f)

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

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if not chat_id:
            print("[Watcher] Cannot send message: TELEGRAM_CHAT_ID is missing.")
            return
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"[Error sending Telegram message]: {e}")

def run_gemini_command(command_list):
    try:
        result = subprocess.run(command_list, capture_output=True, text=True)
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        return str(e)

def handle_command(text, chat_id):
    global current_session, current_model
    parts = text.strip().split()
    cmd = parts[0].lower()

    if cmd in ["/start", "/help"]:
        msg = (
            "🤖 *Gemini Remote Control*\n\n"
            "Available Commands:\n"
            "/new - Start a fresh session\n"
            "/sessions - List all local sessions\n"
            "/resume <id|latest> - Resume a specific session (default: latest)\n"
            "/model <name> - Set a specific model (e.g. gemini-2.5-pro)\n"
            "/status - Show current session and model\n"
            "/help - Show this message\n\n"
            "Any other text will be sent directly to the agent in the active session!"
        )
        send_telegram(msg)
        
    elif cmd == "/new":
        current_session = None
        save_session_state()
        send_telegram("✅ Ready! Your next message will start a brand new session.")
        
    elif cmd == "/sessions":
        send_telegram("⏳ Fetching sessions...")
        output = run_gemini_command(["gemini", "--list-sessions"])
        # Filter out annoying node/keytar warnings
        clean_output = "\n".join([line for line in output.split("\n") if "Keychain" not in line and "keytar" not in line and "fallback" not in line])
        send_telegram(f"📄 *Available Sessions:*\n{clean_output.strip()}")
        
    elif cmd == "/resume":
        if len(parts) > 1:
            current_session = parts[1]
        else:
            current_session = "latest"
        save_session_state()
        send_telegram(f"✅ Session resumed. Active session ID set to: `{current_session}`")
        
    elif cmd == "/model":
        if len(parts) > 1:
            current_model = parts[1]
            send_telegram(f"✅ Model set to: `{current_model}`")
        else:
            current_model = None
            send_telegram("✅ Model reset to default.")
        save_session_state()
        
    elif cmd == "/status":
        sess = current_session if current_session else "None (Next message starts new)"
        mod = current_model if current_model else "Default"
        send_telegram(f"📊 *Status*\nSession: `{sess}`\nModel: `{mod}`")
        
    else:
        # Treat as a regular message to the AI
        print(f"[Watcher] Forwarding to Gemini CLI...")
        
        # We need to construct the CLI arguments
        prompt = f"The user just sent you a message on Telegram: '{text}'. Please process their request. IMPORTANT: You MUST reply to them using the send_telegram_message MCP tool so they can read your response on their phone!"
        
        args = ["gemini", "--prompt", prompt]
        
        if current_session:
            args.extend(["--resume", current_session])
            
        if current_model:
            args.extend(["-m", current_model])
            
        # Send a quick acknowledgment so the user knows it's processing
        send_telegram("⏳ Processing your request...")
        
        subprocess.run(args)
        
        # If we just started a new session, lock back onto 'latest' so follow-ups continue it
        if current_session is None:
            current_session = "latest"
            save_session_state()

def poll_for_messages():
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
        sys.exit(1)
        
    load_session_state()
    
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
                    chat_id = msg.get("chat", {}).get("id")
                    
                    if text and chat_id:
                        # Auto-capture chat ID if not set
                        if not os.environ.get("TELEGRAM_CHAT_ID"):
                            os.environ["TELEGRAM_CHAT_ID"] = str(chat_id)
                            
                        print(f"\n[Telegram] Received: {text}")
                        handle_command(text, chat_id)
                
                if highest_update_id > 0:
                    save_offset(highest_update_id + 1)
        except requests.exceptions.RequestException:
            pass
            
        time.sleep(2)

if __name__ == "__main__":
    poll_for_messages()