import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from scipy.interpolate import interp1d
import os

# === SWITCHES ===
custom_legend_names = True
plotting_for_presentation = True
enable_dual_y_axes = False
prompt_for_title = False
xAxisLabelAutomatic = False   # <-- set to False to prompt for custom X-axis label
compareGroupsOfGraphs = False  # <<< NEW: group pairs of graphs with shared colors/linestyles


def select_and_load_csv(prompt):
    print(prompt)
    file_path = askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("No file selected.")
        return None, None
    df = pd.read_csv(file_path, sep=';')  # Assuming CSVs are comma-separated
    return df, os.path.basename(file_path)


def choose_columns(df, label):
    print(f"\nAvailable columns for {label}:")
    for i, column in enumerate(df.columns):
        print(f"{i}: {column}")
    x_index = int(input(f"Enter the index of the X-axis column for {label}: "))
    y_index = int(input(f"Enter the index of the Y-axis column for {label}: "))
    return df.columns[x_index], df.columns[y_index]


def interpolate_to_common_x(x_target, x, y):
    f_interp = interp1d(x, y, bounds_error=False, fill_value=np.nan)
    return f_interp(x_target)


def compare_multiple_csvs():
    # Hide Tkinter root
    root = Tk()
    root.withdraw()

    num_files = int(input("Enter the number of CSV files to compare: "))
    if num_files < 2:
        print("Need at least 2 files to compare.")
        return

    dfs = []
    x_cols = []
    y_cols = []
    legends = []
    filenames = []

    for i in range(num_files):
        df, filename = select_and_load_csv(f"Select CSV file {i + 1}")
        if df is None:
            return
        x_col, y_col = choose_columns(df, f"File {i + 1} ({filename})")
        dfs.append(df)
        x_cols.append(x_col)
        y_cols.append(y_col)
        filenames.append(filename)

        if custom_legend_names:
            legends.append(input(f"Enter legend name for {y_col} from file '{filename}': "))
        else:
            legends.append(y_col)

    # Axis labels
    if xAxisLabelAutomatic:
        x_label = x_cols[0]
    else:
        x_label = input(f"Enter X-axis label (default '{x_cols[0]}'): ") or x_cols[0]

    y_label = input("Enter Y-axis label (e.g. 'Fuel burn rate'): ")
    y_units = input("Enter Y-axis units (e.g. 'mg/ms'): ")

    # Base X and Y series
    x_base = dfs[0][x_cols[0]].values
    y_base = dfs[0][y_cols[0]].values

    # Interpolate all series to the base X
    y_all = [y_base]
    for i in range(1, num_files):
        x = dfs[i][x_cols[i]].values
        y = dfs[i][y_cols[i]].values
        y_interp = interpolate_to_common_x(x_base, x, y)
        y_all.append(y_interp)

    # === Grouping setup (for colors & linestyles) ===
    if compareGroupsOfGraphs:
        group_size = int(input("How many graphs should be grouped together (e.g. 2)? "))
        if group_size < 1:
            group_size = 1
    else:
        group_size = None  # no grouping

    # === Plotting ===
    plt.figure(figsize=(12, 7))
    ax1 = plt.gca()
    ax2 = ax1.twinx() if enable_dual_y_axes else None

    # Line width
    line_width = 2.5 if plotting_for_presentation else 2.0

    # Font sizes
    if plotting_for_presentation:
        label_size = 16
        tick_size = 14
        legend_size = 14
        title_size = 18
    else:
        label_size = 12
        tick_size = 10
        legend_size = 10
        title_size = 12

    colors = plt.cm.tab10.colors  # Up to 10 colors

    # Linestyle cycle within each group:
    # first solid, second dashed, then dotted, dashdot if group_size > 2
    linestyle_cycle = ['-', '--', ':', '-.']  # <<< NEW

    for i in range(num_files):
        # Decide color and linestyle
        if compareGroupsOfGraphs and group_size is not None:
            group_index = i // group_size                     # which group (0, 1, 2, ...)
            index_in_group = i % group_size                   # position inside group
            color = colors[group_index % len(colors)]         # same color within a group
            linestyle = linestyle_cycle[index_in_group % len(linestyle_cycle)]
        else:
            # Old behavior: each line its own color, solid
            color = colors[i % len(colors)]
            linestyle = '-'

        if enable_dual_y_axes and ax2 and i == 1:
            ax2.plot(
                x_base, y_all[i],
                label=legends[i],
                linewidth=line_width,
                linestyle=linestyle,
                color=color
            )
        else:
            ax1.plot(
                x_base, y_all[i],
                label=legends[i],
                linewidth=line_width,
                linestyle=linestyle,
                color=color
            )

    # Axis labels
    ax1.set_xlabel(x_label, fontsize=label_size)
    ax1.set_ylabel(f"{y_label} [{y_units}]", fontsize=label_size)
    if enable_dual_y_axes and ax2:
        ax2.set_ylabel(f"{y_label} [{y_units}]", fontsize=label_size)

    # Tick label sizes
    ax1.tick_params(axis='both', labelsize=tick_size)
    if ax2:
        ax2.tick_params(axis='both', labelsize=tick_size)

    ax1.grid(True)

    # Legend
    handles, labels = ax1.get_legend_handles_labels()
    if ax2:
        h2, l2 = ax2.get_legend_handles_labels()
        handles += h2
        labels += l2

    leg = ax1.legend(handles, labels, fontsize=legend_size)

    # Title (optional)
    if prompt_for_title:
        title = input("Enter plot title: ")
        if title:
            ax1.set_title(title, fontsize=title_size)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    compare_multiple_csvs()