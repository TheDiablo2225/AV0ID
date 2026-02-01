def build_windows(events, window_size=50, step=25):
    windows = []
    for i in range(0, len(events) - window_size, step):
        windows.append(events[i:i + window_size])
    return windows
