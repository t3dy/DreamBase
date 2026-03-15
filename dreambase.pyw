"""
Dreambase Desktop — native window wrapper for the Flask app.
Uses flaskwebgui (Edge --app mode) + pystray (system tray icon).
"""

import os
import sys
import threading
import socket

# Ensure imports resolve from the script's directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from pystray import Icon, MenuItem, Menu
from PIL import Image

ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")


def find_free_port(preferred=5555):
    """Use preferred port if available, otherwise pick a random free one."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


def start_flask(port):
    """Run Flask in a background daemon thread."""
    app.run(host="127.0.0.1", port=port, use_reloader=False, debug=False)


def on_quit(icon):
    """Clean shutdown."""
    icon.stop()
    os._exit(0)


def main():
    port = find_free_port()

    # Start Flask in background
    flask_thread = threading.Thread(target=start_flask, args=(port,), daemon=True)
    flask_thread.start()

    # Load tray icon image
    tray_image = Image.open(ICON_PATH)

    # Build tray menu
    menu = Menu(
        MenuItem("Dreambase", lambda: None, enabled=False),
        Menu.SEPARATOR,
        MenuItem("Quit", lambda: on_quit(tray_icon)),
    )

    # Create system tray icon
    tray_icon = Icon("Dreambase", tray_image, "Dreambase", menu)

    # Start tray icon in its own thread
    tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
    tray_thread.start()

    # Open in Edge/Chrome --app mode via flaskwebgui
    from flaskwebgui import FlaskUI

    ui = FlaskUI(
        app=app,
        server="flask",
        port=port,
        width=1400,
        height=900,
    )
    ui.run()

    # If the browser window closes, exit
    os._exit(0)


if __name__ == "__main__":
    main()
