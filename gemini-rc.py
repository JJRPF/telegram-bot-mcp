#!/usr/bin/env python3
import pexpect
import sys
import threading
import time
import requests
import os
import signal

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
STATE_FILE = os.path.expanduser("~/.telegram_offset")

def get_offset():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            try: return int(f.read().strip())
            except: pass
    return None

def save_offset(offset):
    with open(STATE_FILE, "w") as f:
        f.write(str(offset))

def poll_telegram(child):
    while child.isalive():
        try:
            offset = get_offset()
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {"timeout": 30}
            if offset: params["offset"] = offset

            res = requests.get(url, params=params, timeout=40)
            if res.ok:
                updates = res.json().get("result", [])
                highest_id = 0
                for u in updates:
                    uid = u.get("update_id", 0)
                    if uid > highest_id: highest_id = uid
                    text = u.get("message", {}).get("text", "")
                    if text:
                        if text.strip().lower() == "/stop":
                            child.sendline("Goodbye!")
                            child.sendeof()
                            return
                        else:
                            # Use ANSI escape to clear the current line if the user was typing locally
                            sys.stdout.write('\r\x1b[K')
                            sys.stdout.flush()
                            
                            # Print locally so user sees what was received
                            print(f"\n[📱 Telegram]: {text}")
                            
                            # Send to Gemini
                            # We send it as a prompt, asking it to reply via the tool so the remote user gets the answer
                            prompt = f"{text}\n(Respond using the send_telegram_message MCP tool so I can see it on my phone!)"
                            child.sendline(prompt)
                            
                if highest_id > 0:
                    save_offset(highest_id + 1)
        except Exception:
            pass
        time.sleep(1)

def main():
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set. Please export it.")
        sys.exit(1)
        
    print("======================================================")
    print("🚀 Gemini Remote Control is active!")
    print("You can use this terminal normally, or send messages via Telegram.")
    print("To stop, type 'exit' here or send /stop on Telegram.")
    print("======================================================\n")
    
    # We clear the initial history so old messages don't get pulled in
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        res = requests.get(url, timeout=5)
        if res.ok:
            updates = res.json().get("result", [])
            if updates:
                highest_id = max(u.get("update_id", 0) for u in updates)
                save_offset(highest_id + 1)
    except:
        pass

    # Determine terminal dimensions so layout doesn't break
    try:
        rows, cols = os.popen('stty size', 'r').read().split()
        dimensions = (int(rows), int(cols))
    except:
        dimensions = (24, 80)

    # Spawn gemini CLI
    child = pexpect.spawn('gemini', encoding='utf-8', dimensions=dimensions)
    
    # Handle terminal resize
    def sigwinch_passthrough(sig, data):
        try:
            r, c = os.popen('stty size', 'r').read().split()
            child.setwinsize(int(r), int(c))
        except: pass
    signal.signal(signal.SIGWINCH, sigwinch_passthrough)

    # Start polling thread
    t = threading.Thread(target=poll_telegram, args=(child,), daemon=True)
    t.start()
    
    # Interact loops forever, connecting stdin/out to the child
    try:
        child.interact()
    except Exception:
        pass
    print("\nRemote Control session ended.")

if __name__ == "__main__":
    main()
