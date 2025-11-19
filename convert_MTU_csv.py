import os
import glob
import pandas as pd
from tkinter import Tk, filedialog

# ====== SETTINGS ======
CRANK_COL_NAME     = "CrankAngleSensor"        # column containing crank angle
NEW_CRANK_COL_NAME = "CrankAngle_mod"    # name of new modified CA column

INPUT_DELIM  = ";"                       # current delimiter
OUTPUT_DELIM = ","                       # desired delimiter
FILE_PATTERN = "*.csv"
# =======================


def ask_folder(title="Select folder"):
    """Open folder selection dialog."""
    root = Tk()
    root.withdraw()
    path = filedialog.askdirectory(title=title)
    root.destroy()
    return path


def adjust_crank_angle(series):
    """Subtract 720 from all crank angle values above 720 deg."""
    new = series.copy()
    mask = new > 720
    new[mask] = new[mask] - 720
    return new


def remove_all_zero_rows(df):
    """Remove rows where all numeric columns are zero."""
    numeric = df.select_dtypes(include="number")
    keep = (numeric != 0).any(axis=1)
    return df[keep]


def process_file(in_path, out_path):
    print(f"Processing: {os.path.basename(in_path)}")

    df = pd.read_csv(in_path, sep=INPUT_DELIM)

    if CRANK_COL_NAME not in df.columns:
        print(f"  WARNING: '{CRANK_COL_NAME}' not found. Skipping.")
        return

    df[NEW_CRANK_COL_NAME] = adjust_crank_angle(df[CRANK_COL_NAME].astype(float))
    df = remove_all_zero_rows(df)

    df.to_csv(out_path, sep=OUTPUT_DELIM, index=False)
    print(f"  Saved: {out_path}")


def main():
    print("Choose INPUT folder...")
    input_folder = ask_folder("Select INPUT folder with CSVs")

    print("Choose OUTPUT folder...")
    output_folder = ask_folder("Select OUTPUT folder")

    if not input_folder or not output_folder:
        print("Folder selection cancelled.")
        return

    files = glob.glob(os.path.join(input_folder, FILE_PATTERN))

    if not files:
        print("No CSV files found in input folder.")
        return

    os.makedirs(output_folder, exist_ok=True)

    for f in files:
        filename = os.path.basename(f)
        out_path = os.path.join(output_folder, filename)
        process_file(f, out_path)

    print("\nDone!")


if __name__ == "__main__":
    main()