#!/usr/bin/env python3
import pexpect
import sys
import threading
import time
import os
import signal
import socket

SOCKET_FILE = "/tmp/gemini_telegram.sock"

def listen_for_remote(child):
    # Ensure any stale socket is removed
    if os.path.exists(SOCKET_FILE):
        try:
            os.remove(SOCKET_FILE)
        except Exception:
            pass
            
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_FILE)
    server.listen(1)
    server.settimeout(1.0)
    
    while child.isalive():
        try:
            try:
                conn, _ = server.accept()
            except socket.timeout:
                continue
                
            data = conn.recv(4096).decode('utf-8')
            conn.close()
            
            if data:
                if data.strip().lower() == "/stop":
                    child.sendline("Goodbye!")
                    child.sendeof()
                    break
                else:
                    # Use ANSI escape to clear the current line if the user was typing locally
                    sys.stdout.write('\r\x1b[K')
                    sys.stdout.flush()
                    
                    # Print locally so user sees what was received
                    print(f"\n[📱 Telegram]: {data}")
                    
                    # Inject into the active Gemini session
                    prompt = f"The user just sent you a message on Telegram: '{data}'. Please process their request. IMPORTANT: You MUST reply to them using the send_telegram_message MCP tool so they can read your response on their phone!"
                    child.send(prompt + '\r')
                    
        except Exception as e:
            pass
            
    # Cleanup socket when session dies
    try:
        os.remove(SOCKET_FILE)
    except Exception:
        pass

def main():
    print("======================================================")
    print("🚀 Gemini Interactive Remote Control is active!")
    print("You can use this terminal normally.")
    print("If you text your Telegram Bot while this is running,")
    print("your messages will be injected directly into this active session.")
    print("To stop, type 'exit' here or send /stop on Telegram.")
    print("======================================================\n")
    
    # Determine terminal dimensions so layout doesn't break
    try:
        rows, cols = os.popen('stty size', 'r').read().split()
        dimensions = (int(rows), int(cols))
    except Exception:
        dimensions = (24, 80)

    # Spawn gemini CLI
    args = sys.argv[1:]
    
    # Prepend system note to inform the agent it is in Remote Control mode
    system_note = (
        "SYSTEM NOTE: You are currently running in 'Gemini Remote Control' mode. "
        "The user is connected to this terminal session via Telegram. "
        "You MUST use the `send_telegram_message` tool to reply to the user if they message you from Telegram "
        "or if you finish a task while they are away. "
        "Any message starting with '[📱 Telegram]' indicates a remote message."
    )
    
    # We use -i (interactive prompt) to inject this instruction at the start of the session
    # We check if -i or -p is already present. If so, we prepend our note to it.
    prompt_found = False
    for i, arg in enumerate(args):
        if arg in ["-i", "--prompt-interactive", "-p", "--prompt"]:
            if i + 1 < len(args):
                args[i+1] = f"{system_note}\n\n{args[i+1]}"
                prompt_found = True
                break
    
    if not prompt_found:
        args.extend(["-i", system_note])

    child = pexpect.spawn('gemini', args=args, encoding='utf-8', dimensions=dimensions)
    
    # Handle terminal resize
    def sigwinch_passthrough(sig, data):
        try:
            r, c = os.popen('stty size', 'r').read().split()
            child.setwinsize(int(r), int(c))
        except Exception:
            pass
    signal.signal(signal.SIGWINCH, sigwinch_passthrough)

    # Start socket listening thread
    t = threading.Thread(target=listen_for_remote, args=(child,), daemon=True)
    t.start()
    
    # Interact loops forever, connecting stdin/out to the child
    try:
        child.interact()
    except Exception:
        pass
        
    print("\nRemote Control session ended.")

if __name__ == "__main__":
    main()
