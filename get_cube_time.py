import os
import datetime

def acquisition_times(folder_path):
    """
    For each .hdr file in folder_path, read the 'acquisition time' field,
    parse it, and print year, month, day, hour, minute, second, and millisecond.
    """
    for fname in os.listdir(folder_path):
        if not fname.lower().endswith('.hdr'):
            continue

        fpath = os.path.join(folder_path, fname)
        try:
            with open(fpath, 'r') as hdr:
                for line in hdr:
                    # look for the acquisition time line (case‐insensitive)
                    if line.strip().lower().startswith('acquisition time'):
                        # split off the timestamp
                        _, ts = line.split('=', 1)
                        ts = ts.strip().rstrip('Z')  # remove trailing 'Z' if present

                        # parse into a datetime object
                        dt = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")

                        # print out the components
                        print(f"{fname}: "
                              f"year: {dt.year}, "
                              f"month: {dt.month}, "
                              f"day: {dt.day}, "
                              f"hour: {dt.hour}, "
                              f"min: {dt.minute}, "
                              f"second: {dt.second}, "
                              f"mili: {int(dt.microsecond/1000)}")
                        break  # move on to next file once we've found it
        except Exception as e:
            print(f"Error reading {fname}: {e}")

if __name__ == "__main__":
    folder = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0628\T7_VNIR\TECK_T7_F15_reflight_2025_06_28_22_38_46_698"
    acquisition_times(folder)

  # parse naive then attach UTC tzinfo
                        dt = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
                        dt = dt.replace(tzinfo=datetime.timezone.utc)