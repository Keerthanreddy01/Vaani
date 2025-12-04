import sys
import time
import threading

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        CYAN = YELLOW = GREEN = BLUE = MAGENTA = RED = WHITE = ""
    class Style:
        BRIGHT = RESET_ALL = ""

class BaseIndicator:
    def __init__(self, message, color, frames, interval=0.3):
        self.message = message
        self.color = color
        self.frames = frames
        self.interval = interval
        self.running = False
        self.thread = None
        self._stop_event = threading.Event()
    
    def _animate(self):
        frame_idx = 0
        while not self._stop_event.is_set():
            frame = self.frames[frame_idx % len(self.frames)]
            sys.stdout.write(f"\r{self.color}{frame} {self.message}{Style.RESET_ALL}")
            sys.stdout.flush()
            frame_idx += 1
            time.sleep(self.interval)
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()
    
    def start(self):
        if not self.running:
            self.running = True
            self._stop_event.clear()
            self.thread = threading.Thread(target=self._animate, daemon=True)
            self.thread.start()
    
    def stop(self):
        if self.running:
            self.running = False
            self._stop_event.set()
            if self.thread:
                self.thread.join(timeout=1)

class ListeningIndicator(BaseIndicator):
    def __init__(self):
        frames = ["●", "●", "●", "○", "○", "●"]
        super().__init__("Listening...", Fore.CYAN + Style.BRIGHT, frames, 0.25)

class ProcessingIndicator(BaseIndicator):
    def __init__(self):
        frames = ["○", "◔", "◑", "◕", "●", "◕", "◑", "◔"]
        super().__init__("Processing...", Fore.YELLOW, frames, 0.2)

class RespondingIndicator(BaseIndicator):
    def __init__(self):
        frames = ["◆", "◇", "◆", "◇"]
        super().__init__("Responding...", Fore.GREEN + Style.BRIGHT, frames, 0.3)

class ThinkingIndicator(BaseIndicator):
    def __init__(self):
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        super().__init__("Thinking...", Fore.BLUE, frames, 0.15)

