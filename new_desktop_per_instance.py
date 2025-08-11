import subprocess
import time
import psutil
import win32gui
import win32process
import win32con
import win32api

from pyvda import (
    get_virtual_desktops,
    get_apps_by_z_order,
    VirtualDesktop,
)

"""
USE WIN+CTRL+ARROW to switch between desktops

"""


# ————————————————————————————————————————————————————————————————
# CONFIGURATION
EXE_PATH       = r"Y:\TECK_WHITE_EARTH\BatchProcessWidget.exe"
INSTANCE_COUNT = 6         # how many copies to launch
POLL_INTERVAL  = 0.7       # seconds between enforcement passes

# Only windows with exactly these titles will be corralled:
TREAT_TITLES = {
    "Headwall Batch Process Tool v0.60.1",
    "Create SWR From Highlighted Pixels",
    "Double-Click the desired tarp panel",
}
# ————————————————————————————————————————————————————————————————

def create_new_desktop():
    """Simulate Win+Ctrl+D to create a new virtual desktop."""
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(win32con.VK_LWIN,    0, 0, 0)
    win32api.keybd_event(ord('D'),            0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(ord('D'),            0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_LWIN,    0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

def ensure_desktops(count):
    """
    Make sure there are at least `count` virtual desktops.
    Returns the sorted list of VirtualDesktop objects.
    """
    desktops = get_virtual_desktops()
    while len(desktops) < count:
        create_new_desktop()
        time.sleep(0.1)
        desktops = get_virtual_desktops()
    return desktops

def start_instances(exe_path, count):
    """
    Create (if needed) `count` desktops, then launch one EXE on each desktop.
    Returns (process_list, desktops_list).
    """
    desktops = ensure_desktops(count)
    procs = []

    for idx in range(count):
        # switch to the desktop for this instance
        desktops[idx].go()
        time.sleep(0.1)

        # launch the process
        p = subprocess.Popen([exe_path])
        procs.append(p)
        print(f"→ Launched instance #{idx+1}, PID={p.pid}, on desktop #{desktops[idx].number}")
        time.sleep(0.2)

    return procs, desktops

def gather_tracked_pids(root_procs):
    """
    Return a set of all PIDs in the process trees of root_procs.
    """
    tracked = set()
    for p in root_procs:
        if psutil.pid_exists(p.pid):
            proc = psutil.Process(p.pid)
            tracked.add(proc.pid)
            for child in proc.children(recursive=True):
                tracked.add(child.pid)
    return tracked

def find_root_pid(pid, root_pids):
    """
    Walk up from `pid` until we hit one of the original root_pids.
    """
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return None

    while True:
        if proc.pid in root_pids:
            return proc.pid
        if proc.ppid() == 0:
            return None
        proc = proc.parent()

if __name__ == "__main__":
    # 1) Launch one instance per desktop
    procs, desktops = start_instances(EXE_PATH, INSTANCE_COUNT)
    root_pids = {p.pid for p in procs}
    pid_to_desktop_num = {p.pid: desktops[i].number for i, p in enumerate(procs)}

    print("\nEntering enforcement loop (CTRL+C to quit)…\n")
    while True:
        # 2) Gather all PIDs in each instance’s tree
        tracked = gather_tracked_pids(procs)

        # 3) Enumerate every window on every desktop
        apps = get_apps_by_z_order(current_desktop=False)

        for app in apps:
            hwnd = app.hwnd
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid not in tracked:
                continue

            title = win32gui.GetWindowText(hwnd)
            if title not in TREAT_TITLES:
                continue

            root = find_root_pid(pid, root_pids)
            if root is None:
                continue

            target_num = pid_to_desktop_num[root]
            # only move if it’s on the wrong desktop
            if app.desktop.number != target_num:
                dest = next(d for d in desktops if d.number == target_num)
                app.move(dest)

        # 4) Repeat
        time.sleep(POLL_INTERVAL)
