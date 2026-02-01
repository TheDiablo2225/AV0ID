from event_normalizer import normalize_event
from window_builder import build_windows
from feature_extractor import extract_features

raw_events = [...]  # your parsed logs
normalized = [normalize_event(e) for e in raw_events]
windows = build_windows(normalized)

vectors = [extract_features(w) for w in windows]
