# teams_status_keeper
# Teams Status Keeper (GUI v2)

A small Windows desktop utility (Tkinter GUI) that simulates periodic mouse movement and a harmless key press to keep Microsoft Teams — or any other activity-tracking app — from marking you "Away" while the app is running.

## Why this version exists

An earlier version had three problems:

1. Movement was too small (2px) to reliably register as activity.
2. The interval between movements was too long (30–55s).
3. Windows would put the laptop to sleep / lock the screen on its own, and no simulated input works once the screen is locked.

This version fixes all three:

- Larger, more visible mouse movement + a double Scroll Lock key press as a secondary signal.
- A shorter, randomized interval (default 15–25 seconds).
- Calls the Windows `SetThreadExecutionState` API while running, to stop the system from sleeping or locking the screen in the first place.

## Requirements

- Windows (uses `ctypes.windll`, so it will not run on macOS/Linux)
- Python 3.8+
- Dependencies:
  ```bash
  pip install pyautogui pynput
  ```

## Usage

```bash
python teams_status_keeper.py
```

1. Set the min/max interval (seconds) between simulated activity bursts.
2. Click **Start**. The status indicator turns green, and a background thread begins jiggling the mouse and tapping Scroll Lock at randomized intervals.
3. Click **Stop** (or close the window) to stop the simulation and let the real system sleep/lock behavior resume.

## How it works

| Component | Purpose |
|---|---|
| `prevent_sleep()` / `allow_sleep()` | Wraps the Windows `SetThreadExecutionState` API to block/allow automatic sleep and display-off while the app is active. |
| `_jiggle()` | Moves the mouse a few pixels and back, then double-taps Scroll Lock, to register as user activity. |
| `_worker()` | Runs on a daemon thread, sleeping for a random interval (checked in 0.5s ticks so Stop is responsive) between each jiggle. |
| Tkinter GUI | Lets you start/stop the loop, configure intervals, and see a live jiggle counter and last-activity timestamp. |

## Notes / Limitations

- If the screen locks *before* you click Start (or manually, via Win+L), the sleep-prevention API can't override an existing lock — simulated input is blocked at the lock screen by design.
- `pyautogui.FAILSAFE` is disabled, so moving the mouse to a screen corner won't abort the script — use the Stop button or close the window instead.
- This affects your own machine's idle/away detection. Be aware of your organization's IT and workplace policies before using a tool like this, since presence status is sometimes relied on by employers or teammates.

## License

No license specified — add one if you plan to share or publish this.
