#!/usr/bin/env python3
"""
BlackJack Simulator Launcher
Choose between command-line and web versions
"""

import sys
import subprocess
import webbrowser
import time
import threading

def run_command_line():
    """Run the command-line version"""
    print("Starting command-line BlackJack simulator...")
    subprocess.run([sys.executable, "BlackJack Simulator.py"])

def run_web_app():
    """Run the web version"""
    print("Starting web BlackJack simulator...")
    print("The game will open in your browser at http://localhost:5000")
    
    # Start the Flask app in a separate thread
    def start_flask():
        subprocess.run([sys.executable, "app.py"])
    
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Wait a moment for Flask to start, then open browser
    time.sleep(2)
    webbrowser.open('http://localhost:5000')
    
    # Keep the main thread alive
    try:
        flask_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down...")

def main():
    print("🎲 Welcome to BlackJack Simulator! 🎲")
    print("\nChoose your preferred version:")
    print("1. Command-line version (terminal-based)")
    print("2. Web version (browser-based)")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            run_command_line()
            break
        elif choice == '2':
            run_web_app()
            break
        elif choice == '3':
            print("Thanks for playing! Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
