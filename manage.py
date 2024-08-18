#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import pynput 
from threading import Thread

ctrl_pressed = False;
alt_pressed = False;

def clean_logs():
    os.system("clear")

class KeyListener():
    def __init__(self) -> None:
        self.ctrl_pressed = False;
        self.alt_pressed = False;
    
    def hot_key(self, key):
        try:
            if key == pynput.keyboard.Key.ctrl_l or key == pynput.keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == pynput.keyboard.Key.alt_l or key == pynput.keyboard.Key.alt_r:
                self.alt_pressed = True
            elif self.ctrl_pressed and self.alt_pressed and key.char == 'l':
                clean_logs()
        except AttributeError:
            pass



    


def start_listener():
    listener = KeyListener()
    listener = pynput.keyboard.Listener(on_press=listener.hot_key)
    listener.start()
    listener.join()

def main():
    
    key_listener_thread = Thread(target=start_listener, daemon=True)
    key_listener_thread.start()

    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mockFactura.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
