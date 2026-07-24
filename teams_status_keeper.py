"""
Teams Status Keeper - GUI Version 2 (Fixed)
---------------------------------------------
V1 me "Away" hone ka issue tha kyunki:
  1. Movement bahut chhota tha (2px)
  2. Interval bahut lamba tha (30-55s)
  3. Windows khud laptop ko sleep/lock kar deta tha, jisse koi bhi
     script kaam nahi karti (lock screen par synthetic input block hota hai)

Yeh version teeno cheezein fix karta hai:
  - Bada, zyada visible mouse movement + scroll lock key press (double signal)
  - Chhota interval (default 15-25 sec)
  - App chalte time Windows ko sleep/screen-lock hone se rokta hai
    (SetThreadExecutionState Windows API)

Requirements:
    pip install pyautogui pynput

Run:
    python teams_status_keeper_gui_v2.py
"""

import time
import random
import threading
import ctypes
import tkinter as tk
from tkinter import ttk
import pyautogui
from pynput.keyboard import Controller, Key

pyautogui.FAILSAFE = False
keyboard = Controller()

# ------------------ Default Settings ------------------
DEFAULT_MIN_INTERVAL = 15
DEFAULT_MAX_INTERVAL = 25
MOVE_DISTANCE = 15   # bada movement, zyada reliably detect hota hai
# --------------------------------------------------------

# Windows API constants to prevent sleep / screen lock while running
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


def prevent_sleep():
    """Windows ko batata hai ki system/display ko sleep na kare."""
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )


def allow_sleep():
    """Normal state wapas restore karta hai."""
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)


class StatusKeeperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Teams Status Keeper")
        self.root.geometry("380x330")
        self.root.resizable(False, False)

        self.running = False
        self.worker_thread = None
        self.jiggle_count = 0

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        title = ttk.Label(self.root, text="Teams Status Keeper", font=("Segoe UI", 14, "bold"))
        title.pack(pady=(15, 5))

        self.status_label = ttk.Label(self.root, text="● Stopped", foreground="red", font=("Segoe UI", 11))
        self.status_label.pack(pady=(0, 10))

        frame = ttk.Frame(self.root)
        frame.pack(**pad)

        ttk.Label(frame, text="Min interval (sec):").grid(row=0, column=0, sticky="w")
        self.min_var = tk.IntVar(value=DEFAULT_MIN_INTERVAL)
        ttk.Entry(frame, textvariable=self.min_var, width=6).grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Max interval (sec):").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.max_var = tk.IntVar(value=DEFAULT_MAX_INTERVAL)
        ttk.Entry(frame, textvariable=self.max_var, width=6).grid(row=1, column=1, padx=5, pady=(5, 0))

        self.toggle_btn = ttk.Button(self.root, text="Start", command=self.toggle)
        self.toggle_btn.pack(pady=15)

        self.log_var = tk.StringVar(value="Ready. Press Start to begin.")
        ttk.Label(self.root, textvariable=self.log_var, wraplength=340, justify="center").pack(pady=5)

        self.count_var = tk.StringVar(value="Total jiggles: 0")
        ttk.Label(self.root, textvariable=self.count_var).pack(pady=5)

        note = ttk.Label(
            self.root,
            text="Note: Agar laptop screen lock ho jaati hai to yeh kaam\nnahi karega. Lock hone se pehle hi yeh sleep rokta hai.",
            foreground="gray", font=("Segoe UI", 8), justify="center"
        )
        note.pack(pady=(10, 0))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        self.running = True
        self.toggle_btn.config(text="Stop")
        self.status_label.config(text="● Running", foreground="green")
        self.log_var.set("Keeping Teams status Available...")
        prevent_sleep()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def stop(self):
        self.running = False
        self.toggle_btn.config(text="Start")
        self.status_label.config(text="● Stopped", foreground="red")
        self.log_var.set("Stopped. Status will follow your real activity now.")
        allow_sleep()

    def _worker(self):
        while self.running:
            min_i = max(1, self.min_var.get())
            max_i = max(min_i, self.max_var.get())
            wait_time = random.uniform(min_i, max_i)

            slept = 0
            while slept < wait_time and self.running:
                time.sleep(0.5)
                slept += 0.5

            if not self.running:
                break

            self._jiggle()
            self.jiggle_count += 1
            ts = time.strftime("%H:%M:%S")
            self.count_var.set(f"Total jiggles: {self.jiggle_count}")
            self.log_var.set(f"Last activity simulated at {ts}")

    def _jiggle(self):
        # Bada mouse movement (aage-peeche)
        x, y = pyautogui.position()
        pyautogui.moveTo(x + MOVE_DISTANCE, y, duration=0.15)
        pyautogui.moveTo(x, y, duration=0.15)

        # Extra signal: Scroll Lock ko do baar press karo (harmless, kuch bhi
        # disturb nahi karta, kyunki turant wapas toggle ho jaata hai)
        try:
            keyboard.press(Key.scroll_lock)
            keyboard.release(Key.scroll_lock)
            time.sleep(0.05)
            keyboard.press(Key.scroll_lock)
            keyboard.release(Key.scroll_lock)
        except Exception:
            pass  # agar key simulate na ho paye to bhi mouse move to ho hi gaya

    def on_close(self):
        self.running = False
        allow_sleep()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = StatusKeeperApp(root)
    root.mainloop()