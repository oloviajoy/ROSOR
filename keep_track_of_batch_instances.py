import subprocess
import time
import psutil
import win32gui
import win32process
import win32con
import win32api
import pywintypes





# ————————————————————————————————————————————————————————————————
# CONFIGURATION
EXE_PATH       = r"Y:\TECK_WHITE_EARTH\BatchProcessWidget.exe"
INSTANCE_COUNT = 3         # how many copies to launch
POLL_INTERVAL  = 0.5        # seconds between scans

# Only windows with exactly these titles drive the logic:
TREAT_TITLES = {
    "Headwall Batch Process Tool v0.60.1",
    "Create SWR From Highlighted Pixels",
    "Double-Click the desired tarp panel",
}
# ————————————————————————————————————————————————————————————————

def start_instances(exe_path, count):
    procs = []
    for i in range(count):
        p = subprocess.Popen([exe_path])
        print(f"→ Launched instance #{i+1}, PID={p.pid}")
        procs.append(p)
        time.sleep(0.2)   # let the windows appear
    return procs

def gather_tracked_pids(procs):
    tracked = set()
    for p in procs:
        if psutil.pid_exists(p.pid):
            proc = psutil.Process(p.pid)
            tracked.add(proc.pid)
            # include any child helpers
            for child in proc.children(recursive=True):
                tracked.add(child.pid)
    return tracked

def enum_tool_windows(tracked_pids):
    """
    Return only the visible top‐level windows whose titles
    are in TREAT_TITLES and belong to one of our PIDs.
    """
    hits = []
    def _cb(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
        except Exception:
            return
        if pid in tracked_pids:
            title = win32gui.GetWindowText(hwnd)
            if title in TREAT_TITLES:
                hits.append((hwnd, pid, title))
    win32gui.EnumWindows(_cb, None)
    return hits

def enum_all_windows(tracked_pids):
    """
    Return _all_ visible top‐level windows for each PID in tracked_pids.
    { pid: [hwnd, ...], ... }
    """
    all_by_pid = {}
    def _cb(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
        except Exception:
            return
        if pid in tracked_pids:
            all_by_pid.setdefault(pid, []).append(hwnd)
    win32gui.EnumWindows(_cb, None)
    return all_by_pid

def safe_set_foreground(hwnd):
    """
    Try to give focus; if Windows refuses, do a quick
    topmost→notopmost dance so it still rises above other apps.
    """
    try:
        win32gui.SetForegroundWindow(hwnd)
    except pywintypes.error:
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOPMOST,
                0,0,0,0,
                win32con.SWP_NOMOVE|win32con.SWP_NOSIZE
            )
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_NOTOPMOST,
                0,0,0,0,
                win32con.SWP_NOMOVE|win32con.SWP_NOSIZE
            )
        except Exception:
            pass

if __name__ == "__main__":
    procs = start_instances(EXE_PATH, INSTANCE_COUNT)
    if not procs:
        print("No instances launched; exiting.")
        exit(1)

    seen  = set()   # which (hwnd, pid) we've encountered
    state = {}      # (hwnd, pid) -> last minimize state

    print("\nEnforcing “one visible instance at a time”…\n")

    while True:
        tracked     = gather_tracked_pids(procs)
        tool_windows = enum_tool_windows(tracked)
        all_windows  = enum_all_windows(tracked)

        # quick lookup: group tool‐windows by PID
        tool_by_pid = {}
        for hwnd, pid, _ in tool_windows:
            tool_by_pid.setdefault(pid, []).append(hwnd)

        for hwnd, pid, title in tool_windows:
            key    = (hwnd, pid)
            is_min = win32gui.IsIconic(hwnd)

            # — First time we see this main window —
            if key not in seen:
                seen.add(key)
                state[key] = is_min
                print(f"[PID {pid}] New HWND=0x{hwnd:08X}  Title='{title}'")

                # 1) restore _all_ windows of this instance
                for w in all_windows.get(pid, []):
                    win32gui.ShowWindow(w, win32con.SW_RESTORE)

                # 2) bring our main window forward
                safe_set_foreground(hwnd)

                # 3) minimize _all_ windows of every other instance
                for other_pid, wins in all_windows.items():
                    if other_pid != pid:
                        for w in wins:
                            win32gui.ShowWindow(w, win32con.SW_MINIMIZE)

            else:
                prev_min = state[key]

                # — If this main window was just restored —
                if (not is_min) and prev_min:
                    # restore _all_ windows of this instance
                    for w in all_windows.get(pid, []):
                        win32gui.ShowWindow(w, win32con.SW_RESTORE)
                    safe_set_foreground(hwnd)
                    # minimize _all_ windows of every other instance
                    for other_pid, wins in all_windows.items():
                        if other_pid != pid:
                            for w in wins:
                                win32gui.ShowWindow(w, win32con.SW_MINIMIZE)

                # — If this main window was just minimized —
                if is_min and not prev_min:
                    # minimize _all_ windows of this instance
                    for w in all_windows.get(pid, []):
                        win32gui.ShowWindow(w, win32con.SW_MINIMIZE)

                state[key] = is_min

        time.sleep(POLL_INTERVAL)