import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from scipy.interpolate import interp1d

# === SWITCHES ===
custom_legend_names = True
plotting_for_presentation = True
enable_dual_y_axes = False  # Enable separate y-axis on the right side
prompt_for_title = True  # Prompt for plot title

def select_and_load_csv(prompt):
    print(prompt)
    file_path = askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("No file selected.")
        return None
    df = pd.read_csv(file_path)
    # df = pd.read_csv(file_path, delimiter = ";")

    return df

def choose_columns(df, role):
    print(f"\nAvailable columns for {role}:")
    for i, column in enumerate(df.columns):
        print(f"{i}: {column}")
    
    x_index = int(input(f"\nEnter the index of the X-axis column for {role}: "))
    y_index = int(input(f"Enter the index of the Y-axis column for {role}: "))
    
    x_col = df.columns[x_index]
    y_col = df.columns[y_index]
    return x_col, y_col

def interpolate_to_common_x(x1, y1, x2, y2):
    interp_func = interp1d(x2, y2, bounds_error=False, fill_value=np.nan)
    y2_interp = interp_func(x1)
    return y2_interp

def compare_two_csvs():
    # Tk root (hidden)
    root = Tk()
    root.withdraw()

    df1 = select_and_load_csv("Select the FIRST CSV file")
    if df1 is None: return

    df2 = select_and_load_csv("Select the SECOND CSV file")
    if df2 is None: return

    x1_col, y1_col = choose_columns(df1, "FIRST file")
    x2_col, y2_col = choose_columns(df2, "SECOND file")

    y_label = input("Enter Y-axis label (e.g. 'Fuel burn rate'): ")
    y_units = input("Enter Y-axis units (e.g. 'mg/ms'): ")

    x1 = df1[x1_col].values
    y1 = df1[y1_col].values

    x2 = df2[x2_col].values
    y2 = df2[y2_col].values

    # Interpolate y2 onto x1
    y2_interp = interpolate_to_common_x(x1, y1, x2, y2)

    # === Plotting settings ===
    line_width = 2.5 if plotting_for_presentation else 2.0
    font_settings = {
        'axes.labelsize': 16,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'legend.fontsize': 14,
        'axes.titlesize': 18
    } if plotting_for_presentation else {}

    plt.rcParams.update(font_settings)

    plt.figure(figsize=(12, 7))
    ax1 = plt.gca()
    ax2 = ax1.twinx() if enable_dual_y_axes else None

    # Legend names
    legend1 = input(f"Legend name for {y1_col}: ") if custom_legend_names else y1_col
    legend2 = input(f"Legend name for {y2_col} (interpolated): ") if custom_legend_names else y2_col

    # Colors
    color1 = 'tab:blue'
    color2 = 'tab:orange'

    # Plotting
    ax1.plot(x1, y1, label=legend1, linewidth=line_width, color=color1)
    if enable_dual_y_axes and ax2:
        ax2.plot(x1, y2_interp, label=legend2, linewidth=line_width, color=color2, linestyle='--')
    else:
        ax1.plot(x1, y2_interp, label=legend2, linewidth=line_width, color=color2, linestyle='--')

    ax1.set_xlabel(x1_col)
    ax1.set_ylabel(f"{y_label} [{y_units}]")
    if enable_dual_y_axes and ax2:
        ax2.set_ylabel(f"{y_label} [{y_units}]")

    # Grid and legend
    ax1.grid(True)
    handles, labels = ax1.get_legend_handles_labels()
    if ax2:
        h2, l2 = ax2.get_legend_handles_labels()
        handles += h2
        labels += l2

    if prompt_for_title:
        title = input("Enter plot title: ")
        plt.title(title)
    plt.legend(handles, labels)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    compare_two_csvs()
