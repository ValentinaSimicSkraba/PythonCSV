import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from tkinter import Tk
from tkinter.filedialog import askdirectory
from scipy.interpolate import interp1d

# === SWITCHES ===
custom_legend_names = True
plotting_for_presentation = True
enable_dual_y_axes = False
prompt_for_title = True

def select_folder():
    root = Tk()
    root.withdraw()
    folder_path = askdirectory(title="Select folder containing CSV files")
    return folder_path

def load_all_csvs_from_folder(folder_path):
    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.csv')]
    csv_paths = [os.path.join(folder_path, f) for f in csv_files]
    dfs = [pd.read_csv(path, sep=';') for path in csv_paths]
    return dfs, csv_files

def choose_columns(df_sample):
    print("\nAvailable columns:")
    for i, col in enumerate(df_sample.columns):
        print(f"{i}: {col}")
    x_index = int(input("Enter index of X-axis column: "))
    y_index = int(input("Enter index of Y-axis column: "))
    return df_sample.columns[x_index], df_sample.columns[y_index]

def interpolate_to_common_x(x_target, x, y):
    f_interp = interp1d(x, y, bounds_error=False, fill_value=np.nan)
    return f_interp(x_target)

def compare_csvs_from_folder():
    folder_path = select_folder()
    if not folder_path:
        print("No folder selected.")
        return

    dfs, filenames = load_all_csvs_from_folder(folder_path)
    if len(dfs) < 2:
        print("At least two CSV files are required.")
        return

    x_col, y_col = choose_columns(dfs[0])

    legends = []
    for name in filenames:
        if custom_legend_names:
            legends.append(input(f"Enter legend name for {name}: "))
        else:
            legends.append(name)

    y_label = input("Enter Y-axis label (e.g. 'Fuel burn rate'): ")
    y_units = input("Enter Y-axis units (e.g. 'mg/ms'): ")

    x_base = dfs[0][x_col].values
    y_base = dfs[0][y_col].values
    y_all = [y_base]

    for df in dfs[1:]:
        x = df[x_col].values
        y = df[y_col].values
        y_interp = interpolate_to_common_x(x_base, x, y)
        y_all.append(y_interp)

    plt.figure(figsize=(12, 7))
    ax1 = plt.gca()
    ax2 = ax1.twinx() if enable_dual_y_axes else None

    line_width = 2.5 if plotting_for_presentation else 2.0
    font_settings = {
        'axes.labelsize': 16,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'legend.fontsize': 14,
        'axes.titlesize': 18
    } if plotting_for_presentation else {}

    plt.rcParams.update(font_settings)

    colors = plt.cm.tab10.colors

    for i in range(len(dfs)):
        color = colors[i % len(colors)]
        if enable_dual_y_axes and ax2 and i == 1:
            ax2.plot(x_base, y_all[i], label=legends[i], linewidth=line_width, linestyle='-', color=color)
        else:
            ax1.plot(x_base, y_all[i], label=legends[i], linewidth=line_width, linestyle='-' if i == 0 else '-', color=color)

    ax1.set_xlabel(x_col)
    ax1.set_ylabel(f"{y_label} [{y_units}]")
    if enable_dual_y_axes and ax2:
        ax2.set_ylabel(f"{y_label} [{y_units}]")

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
    compare_csvs_from_folder()