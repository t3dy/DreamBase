"""Build Dreambase desktop app with PyInstaller."""

import PyInstaller.__main__

PyInstaller.__main__.run([
    "dreambase.pyw",
    "--name=Dreambase",
    "--onedir",             # Folder output (faster startup than --onefile for large apps)
    "--windowed",           # No console window
    "--icon=icon.ico",
    "--add-data=templates;templates",
    "--add-data=static;static",
    "--add-data=schema.py;.",
    "--add-data=icon.ico;.",
    "--hidden-import=flask",
    "--hidden-import=jinja2",
    "--hidden-import=pystray",
    "--hidden-import=pystray._win32",
    "--noconfirm",
])
