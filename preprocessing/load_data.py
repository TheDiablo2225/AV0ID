import pandas as pd

# Official NSL-KDD column names
COLUMNS = [
    "duration","protocol_type","service","flag","src_bytes","dst_bytes",
    "land","wrong_fragment","urgent","hot","num_failed_logins",
    "logged_in","num_compromised","root_shell","su_attempted",
    "num_root","num_file_creations","num_shells","num_access_files",
    "num_outbound_cmds","is_host_login","is_guest_login",
    "count","srv_count","serror_rate","srv_serror_rate",
    "rerror_rate","srv_rerror_rate","same_srv_rate",
    "diff_srv_rate","srv_diff_host_rate","dst_host_count",
    "dst_host_srv_count","dst_host_same_srv_rate",
    "dst_host_diff_srv_rate","dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate","dst_host_serror_rate",
    "dst_host_srv_serror_rate","dst_host_rerror_rate",
    "dst_host_srv_rerror_rate","label","difficulty"
]

def load_dataset(path):
    """
    Load NSL-KDD dataset from .txt file
    """
    df = pd.read_csv(path, names=COLUMNS)
    df.reset_index(drop=True, inplace=True)
    return df

def load_normal_only(path):
    """
    Load only normal traffic (for baseline construction)
    """
    df = load_dataset(path)
    normal_df = df[df["label"] == "normal"].reset_index(drop=True)
    return normal_df
