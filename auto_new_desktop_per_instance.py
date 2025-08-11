import os
import subprocess
import time
import sys
import threading
import traceback
from datetime import datetime

import psutil
import win32gui
import win32con
import win32api
import win32process
import ctypes
import win32clipboard

from pyvda import get_virtual_desktops, get_apps_by_z_order, VirtualDesktop

# ————————————————————————————————————————————————————————————————
# CONFIGURATION
FOLDERS = [
r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0711\T6_SWIR\100406_TECK_T6_F1_F2_F3_F4_2025_07_11_15_38_24",
r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0711\T6_SWIR\100410_TECK_T6_F5_F6_2025_07_11_16_25_55",
r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0711\T6_SWIR\100413_TECK_T6_F9_F10_2025_07_11_16_47_55",
r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0711\T6_SWIR\100415_TECK_T6_F19_F20_2025_07_11_17_12_25",
r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0711\T6_SWIR\100417_TECK_T6_F15_F16_2025_07_11_17_29_10",
r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0711\T6_SWIR\100431_TECH_T6_F13_F14_2025_07_11_22_14_27"
]
EXE_PATH       = r"Y:\TECK_WHITE_EARTH\BatchProcessWidget_v0p60.exe"
WINDOW_TITLE   = "Headwall Batch Process Tool v0.60"
BUTTON_INDEX   = 5
FIRST_TEXT     = "Rf"
ERROR_LOG      = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\over_night_error_log.txt"
POLL_INTERVAL  = 0.7  # seconds between enforcement passes

TREAT_TITLES = {
    "Headwall Batch Process Tool v0.60",
    "Create SWR From Highlighted Pixels",
    "Double-Click the desired tarp panel",
}
# ————————————————————————————————————————————————————————————————

current_desktop_idx = 0

def send_win_ctrl_right():
    win32api.keybd_event(win32con.VK_LWIN,    0, 0, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(win32con.VK_RIGHT,   0, 0, 0)
    win32api.keybd_event(win32con.VK_RIGHT,   0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_LWIN,    0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.2)

def create_new_desktop():
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(win32con.VK_LWIN,    0, 0, 0)
    win32api.keybd_event(ord('D'),            0, 0, 0)
    win32api.keybd_event(ord('D'),            0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_LWIN,    0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)

def ensure_desktops(count):
    desktops = get_virtual_desktops()
    while len(desktops) < count:
        create_new_desktop()
        time.sleep(0.1)
        desktops = get_virtual_desktops()
    return sorted(desktops, key=lambda d: d.number)

def gather_tracked_pids(root_procs):
    tracked = set()
    for p in root_procs:
        if psutil.pid_exists(p.pid):
            tracked.add(p.pid)
            try:
                proc = psutil.Process(p.pid)
                for child in proc.children(recursive=True):
                    tracked.add(child.pid)
            except psutil.NoSuchProcess:
                pass
    return tracked

def find_root_pid(pid, root_pids):
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

def enforcement_loop(procs, root_pids, pid_to_desktop, desktops):
    print("Entering enforcement loop (CTRL+C to quit)…")
    while True:
        tracked = gather_tracked_pids(procs)
        apps = get_apps_by_z_order(current_desktop=False)
        for app in apps:
            hwnd = app.hwnd
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
            except Exception:
                continue
            if pid not in tracked:
                continue
            title = win32gui.GetWindowText(hwnd)
            if title not in TREAT_TITLES:
                continue
            root = find_root_pid(pid, root_pids)
            if root is None:
                continue
            target_num = pid_to_desktop.get(root)
            if target_num is None or app.desktop.number == target_num:
                continue
            dest = next(d for d in desktops if d.number == target_num)
            app.move(dest)
        time.sleep(POLL_INTERVAL)

def enum_windows_by_title(title):
    hwnds = []
    def cb(h, _):
        if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h) == title:
            hwnds.append(h)
    win32gui.EnumWindows(cb, None)
    return hwnds

def bring_to_front(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    time.sleep(0.2)

def enum_button_children(parent_hwnd):
    btns = []
    def cb(h, _):
        if win32gui.GetClassName(h) == 'Button':
            btns.append(h)
    win32gui.EnumChildWindows(parent_hwnd, cb, None)
    return btns

def click_button(hwnd):
    orig = win32api.GetCursorPos()
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    cx, cy = (l + r)//2, (t + b)//2
    ctypes.windll.user32.SetCursorPos(cx, cy)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,   0, 0, 0, 0)
    time.sleep(0.1)
    win32api.SetCursorPos(orig)
    time.sleep(0.05)

def describe_buttons(hwnd):
    btns = enum_button_children(hwnd)
    for i, btn in enumerate(btns, start=1):
        cls  = win32gui.GetClassName(btn)
        txt  = win32gui.GetWindowText(btn)
        cid  = win32gui.GetDlgCtrlID(btn)
        l,t,r,b = win32gui.GetWindowRect(btn)
        print(f"[{i}] hwnd={btn}, class={cls!r}, id={cid}, text={txt!r}, rect=({l},{t})→({r},{b})")
    return btns

def paste_text(text):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
    win32clipboard.CloseClipboard()
    time.sleep(0.05)
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord('V'), 0, 0, 0)
    win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)

def send_ctrl_tab(times=1):
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    for _ in range(times):
        win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)

def do_gui_stuff(exe_path, window_title, button_index, first_text, second_text):
    proc = subprocess.Popen(
        [exe_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    error_event = threading.Event()
    error_lines = []

    def watch_errors(pipe):
        for line in pipe:
            if "Exception" in line or "Error" in line:
                error_lines.append(line.strip())
                error_event.set()
        pipe.close()

    watcher = threading.Thread(target=watch_errors, args=(proc.stderr,), daemon=True)
    watcher.start()

    original = set(enum_windows_by_title(window_title))
    new_hwnd = None
    for _ in range(100):
        if error_event.is_set():
            break
        time.sleep(0.1)
        diff = set(enum_windows_by_title(window_title)) - original
        if diff:
            new_hwnd = diff.pop()
            break

    if error_event.is_set():
        proc.kill()
        raise RuntimeError("Startup error: " + "; ".join(error_lines))
    if not new_hwnd:
        proc.kill()
        raise RuntimeError(f"Timed out waiting for {window_title}")

    bring_to_front(new_hwnd)
    send_ctrl_tab(6)
    paste_text(first_text)
    send_ctrl_tab(1)
    paste_text(second_text)

    # no longer waiting for any "Processing" dialog—just return immediately
    return proc

def process_folder(folder, desktops, idx, total, procs, root_pids, pid_to_desktop):
    global current_desktop_idx
    target = desktops[idx]
    try:
        target.go()
        time.sleep(0.5)
    except Exception:
        steps = idx - current_desktop_idx
        for _ in range(steps):
            send_win_ctrl_right()
    current_desktop_idx = idx

    proc = do_gui_stuff(EXE_PATH, WINDOW_TITLE, BUTTON_INDEX, FIRST_TEXT, folder)
    procs.append(proc)
    root_pids.add(proc.pid)
    pid_to_desktop[proc.pid] = target.number

def main():
    total = len(FOLDERS)
    if total == 0:
        print("No folders to process. Please populate FOLDERS.")
        sys.exit(0)

    desktops = ensure_desktops(total)
    procs = []
    root_pids = set()
    pid_to_desktop = {}

    enforcer = threading.Thread(
        target=enforcement_loop,
        args=(procs, root_pids, pid_to_desktop, desktops),
        daemon=False
    )
    enforcer.start()

    for idx, folder in enumerate(FOLDERS):
        process_folder(folder, desktops, idx, total, procs, root_pids, pid_to_desktop)

    print("All folders queued. Enforcement loop running. Press Ctrl+C to exit.")
    enforcer.join()

if __name__ == '__main__':
    main()
