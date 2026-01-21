import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from scipy.interpolate import interp1d
import os

# === DELIMITER ===

# === SWITCHES ===
custom_legend_names = True          # If True, prompt for FILE-LEVEL legend names (used in both modes)
plotting_for_presentation = True    # If True, use thicker lines and larger fonts
enable_dual_y_axes = False           # Toggle dual right axis (created only if needed)
prompt_for_title = True             # Prompt for plot title
interpolate_second_to_first = True  # Put file #2 on file #1's X grid for clean overlay


def select_and_load_csv(prompt="Select a data file"):
    print(prompt)
    file_path = askopenfilename(filetypes=[("Data files", "*.csv *.txt")])
    if not file_path:
        print("No file selected.")
        return None, None

    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(file_path, delimiter=',')
        elif ext == ".txt":
            df = pd.read_csv(file_path, sep=r'\s+', engine='python')
        else:
            print("Unsupported file format.")
            return None, None
    except Exception as e:
        print(f"Failed to read file: {e}")
        return None, None

    return df, file_path

def list_columns(df, role):
    print(f"\nAvailable columns for {role}:")
    for i, column in enumerate(df.columns):
        print(f"{i}: {column}")

def get_index(prompt_text, df, allow_empty=False):
    """Return column name from index; if allow_empty and empty input, return None."""
    s = input(prompt_text).strip()
    if allow_empty and s == "":
        return None
    try:
        idx = int(s)
        return df.columns[idx]
    except Exception:
        print("Invalid selection. Skipping this field.")
        return None if allow_empty else df.columns[0]  # fall back to first col if not skippable

def choose_columns(df, role, dual_axes: bool):
    list_columns(df, role)
    x_col  = get_index(f"\nEnter index of X-axis column for {role}: ", df)
    if dual_axes:
        # Allow skipping EITHER Y on a per-file basis
        yl_col = get_index(f"Enter index of LEFT-Y column for {role} (solid, Enter to skip): ", df, allow_empty=True)
        yr_col = get_index(f"Enter index of RIGHT-Y column for {role} (dashed, Enter to skip): ", df, allow_empty=True)
    else:
        yl_col = get_index(f"Enter index of Y column for {role}: ", df, allow_empty=False)
        yr_col = None
    return x_col, yl_col, yr_col

def safe_interp(x_target, x_src, y_src):
    """Interpolate y_src(x_src) onto x_target; handles unsorted x_src and OOR with NaN."""
    order = np.argsort(x_src)
    x_src_sorted = np.asarray(x_src)[order]
    y_src_sorted = np.asarray(y_src)[order]
    f = interp1d(x_src_sorted, y_src_sorted, bounds_error=False, fill_value=np.nan)
    return f(x_target)

def first_non_none(handles):
    for h in handles:
        if h is not None:
            return h
    return None

def compare_two_csvs():
    # Tk root (hidden)
    root = Tk(); root.withdraw()

    # ---- Load files
    df1, path1 = select_and_load_csv("Select the FIRST CSV/TXT file")
    if df1 is None: return
    df2, path2 = select_and_load_csv("Select the SECOND CSV/TXT file")
    if df2 is None: return

    base1 = os.path.basename(path1)
    base2 = os.path.basename(path2)

    # ---- Choose columns
    x1_col, y1L_col, y1R_col = choose_columns(df1, "FIRST file", enable_dual_y_axes)
    x2_col, y2L_col, y2R_col = choose_columns(df2, "SECOND file", enable_dual_y_axes)

    # ---- Data arrays
    x1 = df1[x1_col].to_numpy()
    y1L = df1[y1L_col].to_numpy() if y1L_col else None
    y1R = df1[y1R_col].to_numpy() if (enable_dual_y_axes and y1R_col) else None

    x2 = df2[x2_col].to_numpy()
    y2L_raw = df2[y2L_col].to_numpy() if y2L_col else None
    y2R_raw = df2[y2R_col].to_numpy() if (enable_dual_y_axes and y2R_col) else None

    # ---- Interpolate file #2 onto file #1 x-grid if requested
    if interpolate_second_to_first:
        x_plot = x1
        y2L = safe_interp(x1, x2, y2L_raw) if y2L_raw is not None else None
        y2R = safe_interp(x1, x2, y2R_raw) if (enable_dual_y_axes and y2R_raw is not None) else None
    else:
        x_plot = None   # use native grids
        y2L, y2R = y2L_raw, y2R_raw

    # Determine which axes are actually needed
    any_left  = (y1L is not None) or (y2L is not None)
    any_right = enable_dual_y_axes and ((y1R is not None) or (y2R is not None))

    # ---- Axis labels (ask only for axes that will be used)
    yL_label = yL_units = ""
    yR_label = yR_units = ""
    if any_left:
        yL_label = (input("Left Y-axis label (e.g. Temperature): ").strip() or "Left Y")
        yL_units = input("Left Y-axis units (e.g. K): ").strip()
    if any_right:
        yR_label = (input("Right Y-axis label (e.g. Lambda): ").strip() or "Right Y")
        yR_units = input("Right Y-axis units (e.g. -): ").strip()

    # ---- FILE-LEVEL legend names
    if custom_legend_names:
        file_label_1 = input(f"Legend label for FILE 1 [{base1}]: ").strip() or base1
        file_label_2 = input(f"Legend label for FILE 2 [{base2}]: ").strip() or base2
    else:
        file_label_1 = base1
        file_label_2 = base2

    # === Plotting settings ===
    line_width = 2.8 if plotting_for_presentation else 2.0
    font_settings = {
        'axes.labelsize': 16,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'legend.fontsize': 14,
        'axes.titlesize': 18
    } if plotting_for_presentation else {}
    plt.rcParams.update(font_settings)

    fig = plt.figure(figsize=(12, 7))
    axL = plt.gca()
    axR = axL.twinx() if any_right else None  # create right axis ONLY if needed

    # Colors per file (same color for both lines of the same file)
    color1 = 'tab:blue'
    color2 = 'tab:orange'

    # ---- Plot File 1
    lines1 = []
    if any_left and (y1L is not None):
        l1, = axL.plot(
            x1, y1L, linewidth=line_width, linestyle='-',
            color=color1,
            label=(file_label_1 if not any_right else None)
        )
        lines1.append(l1)
    if any_right and (y1R is not None):
        l2, = axR.plot(
            x1, y1R, linewidth=line_width, linestyle='-',
            color=color1
        )
        lines1.append(l2)

    # ---- Plot File 2
    lines2 = []
    X2_for_plot = (x_plot if interpolate_second_to_first else x2)
    if any_left and (y2L is not None):
        l3, = axL.plot(
            X2_for_plot, y2L, linewidth=line_width, linestyle='-',
            color=color2,
            label=(file_label_2 if not any_right else None)
        )
        lines2.append(l3)
    if any_right and (y2R is not None):
        l4, = axR.plot(
            X2_for_plot, y2R, linewidth=line_width, linestyle='-',
            color=color2
        )
        lines2.append(l4)

    # ---- Labels
    axL.set_xlabel(x1_col)  # label x by File 1's x selection
    if any_left:
        axL.set_ylabel(f"{yL_label} [{yL_units}]" if yL_units else yL_label)
    if any_right and axR is not None:
        axR.set_ylabel(f"{yR_label} [{yR_units}]" if yR_units else yR_label)

    # ---- Grid & Legend
    axL.grid(True)

    if any_right:
        # Legend grouped per file (one entry per file)
        rep1 = first_non_none(lines1)
        rep2 = first_non_none(lines2)
        handles, labels = [], []
        if rep1 is not None:
            handles.append(rep1); labels.append(file_label_1)
        if rep2 is not None:
            handles.append(rep2); labels.append(file_label_2)
        if handles:
            plt.legend(handles, labels, loc='best')
    else:
        # Standard per-series legend (but since we label the single series per file, it's one entry per file)
        plt.legend(loc='best')

    # ---- Title
    title = input("Enter plot title: ") if prompt_for_title else f"{base1} vs {x1_col}"
    plt.title(title)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    compare_two_csvs()