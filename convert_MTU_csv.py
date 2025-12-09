import os
import glob
import pandas as pd
from tkinter import Tk, filedialog

# ====== SETTINGS ======
CRANK_COL_NAME     = "CrankAngleSensor"        # name of the crank angle column
NEW_CRANK_COL_NAME = "CrankAngle [deg]"    # new modified crank angle column

INPUT_DELIM  = ";"                       # current delimiter in your files
OUTPUT_DELIM = ","                       # desired delimiter
FILE_PATTERN = "*.csv"

# how big a negative jump must be to be considered a wrap [deg]
WRAP_JUMP_THRESHOLD = -300.0
# =======================


def ask_folder(title="Select folder"):
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title=title)
    root.destroy()
    return folder


def adjust_crank_angle(series):
    """
    Detect where the crank angle wraps from ~720 back to ~0
    by looking for a large negative jump in the series.

    - Subtract 720 from all values up to and INCLUDING the row
      *before* the wrap (i.e. up to the 719.x row).
    - Keep values from the wrap row onward unchanged.

    If no wrap is detected, fall back to subtracting 720 from values > 720.
    """
    s = series.astype(float).copy()

    # first differences
    diff = s.diff()

    # candidates where crank angle suddenly drops (wrap)
    wrap_candidates = diff[diff < WRAP_JUMP_THRESHOLD]

    if not wrap_candidates.empty:
        # index label of the row where the drop is seen (small angle after 719.x)
        wrap_idx_label = wrap_candidates.index[0]

        # integer position of that row
        pos = s.index.get_loc(wrap_idx_label)

        if pos > 0:
            # previous row is the last one we want to shift (the 719.x row)
            last_to_shift_label = s.index[pos - 1]

            # subtract 720 for all rows up to and including that previous row
            s.loc[:last_to_shift_label] = s.loc[:last_to_shift_label] - 720
        # from wrap_idx_label onward we keep the original values
    else:
        # fallback: simple wrap if angles go above 720
        mask = s > 720.0
        s[mask] = s[mask] - 720.0

    return s


def remove_all_zero_rows(df):
    """
    Remove rows where all original numeric columns are zero.
    Ignore the synthetic NEW_CRANK_COL_NAME when checking.
    """
    cols_to_check = df.columns.tolist()
    if NEW_CRANK_COL_NAME in cols_to_check:
        cols_to_check.remove(NEW_CRANK_COL_NAME)

    numeric = df[cols_to_check].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    keep = (numeric != 0.0).any(axis=1)   # keep row if ANY numeric col is non-zero
    return df[keep]


def process_file(in_path, out_path):
    print(f"Processing: {os.path.basename(in_path)}")

    df = pd.read_csv(in_path, sep=INPUT_DELIM)

    if CRANK_COL_NAME not in df.columns:
        print(f"  WARNING: column '{CRANK_COL_NAME}' not found, skipping.")
        return

    # compute modified crank angle
    df[NEW_CRANK_COL_NAME] = adjust_crank_angle(df[CRANK_COL_NAME])

    # remove rows with all-zero original numeric data
    df = remove_all_zero_rows(df)

    # save with comma delimiter
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
        out_path = os.path.join(output_folder, os.path.basename(f))
        process_file(f, out_path)

    print("\nDone!")


if __name__ == "__main__":
    main()
