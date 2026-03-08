# temporal_smoothing.py

class EMASmoother:
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.prev = 0

    def update(self, value):
        smoothed = self.alpha * value + (1 - self.alpha) * self.prev
        self.prev = smoothed
        return smoothed