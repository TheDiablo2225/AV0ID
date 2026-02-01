from preprocessing.load_data import load_normal_only
from windowing.sliding_window import generate_sliding_windows
import pandas as pd

normal_df = load_normal_only("archive/KDDTrain+.txt")

windows = generate_sliding_windows(
    normal_df,
    window_size=50,
    step_size=10
)

print(f"Generated {len(windows)} baseline windows")

# view a certain number of windows
for i in range(3):
    print(f"\n--- Window {i} ---")
    print(windows[i][["protocol_type", "service", "flag"]].head())

# view aggregated behavior
all_protocols = pd.concat(windows)["protocol_type"]
print(all_protocols.value_counts(normalize=True))