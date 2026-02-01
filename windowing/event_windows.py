def sliding_event_windows(event_stream, window_size=5000, step_size=1000):
    buffer = []

    for event in event_stream:
        buffer.append(event)

        if len(buffer) >= window_size:
            yield buffer[:window_size]
            buffer = buffer[step_size:]
