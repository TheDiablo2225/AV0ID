def generate_sliding_windows(df, window_size=50, step_size=10):
    """
    Generate sliding windows over connection records.

    Parameters:
    - df: pandas DataFrame (ordered connections)
    - window_size: number of connections per window
    - step_size: slide length

    Returns:
    - List of DataFrame windows
    """
    windows = []
    total_records = len(df)

    for start in range(0, total_records - window_size + 1, step_size):
        end = start + window_size
        window = df.iloc[start:end]
        windows.append(window)

    return windows
