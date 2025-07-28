import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# === SWITCHES ===
custom_legend_names = False
plotting_for_presentation = True
enable_dual_y_axes = False  # Enable separate y-axis on the right side
custom_title = False

def plot_from_csv():
    # Create a Tkinter root window (hidden)
    root = Tk()
    root.withdraw()

    # File selection
    csv_file = askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not csv_file:
        print("No file selected.")
        return

    # Load CSV
    df = pd.read_csv(csv_file)
    # df = pd.read_csv(csv_file,delimiter = ';')
    
    # Show available columns
    print("\nAvailable columns:")
    for i, column in enumerate(df.columns):
        print(f"{i}: {column}")
    
    try:
        # Prompt for X-axis
        x_col_index = int(input("\nEnter the index of the column for the X axis: "))
        x_col = df.columns[x_col_index]

        # === Styling for presentation ===
        line_width = 2.0
        if plotting_for_presentation:
            plt.rcParams.update({
                'axes.labelsize': 16,
                'xtick.labelsize': 14,
                'ytick.labelsize': 14,
                'legend.fontsize': 14,
                'axes.titlesize': 18
            })
            line_width = 2.5

        # Color sets
        left_colors = plt.cm.tab10.colors
        right_colors = plt.cm.Set2.colors

        plt.figure(figsize=(12, 7))
        ax1 = plt.gca()
        ax2 = None

        # --- LEFT Y AXIS ---
        left_y_indices = input("Enter indices for left Y axis column(s) (comma-separated): ")
        left_y_cols = [df.columns[int(i.strip())] for i in left_y_indices.split(',')]
        left_label = input("Enter LEFT Y-axis label: ")
        left_units = input("Enter LEFT Y-axis units: ")

        if custom_legend_names:
            left_legends = [input(f"Legend for '{col}': ") for col in left_y_cols]
        else:
            left_legends = left_y_cols

        for idx, (col, legend) in enumerate(zip(left_y_cols, left_legends)):
            color = left_colors[idx % len(left_colors)]
            ax1.plot(df[x_col], df[col], label=legend, linewidth=line_width, color=color)

        ax1.set_ylabel(f"{left_label} [{left_units}]")
        ax1.set_xlabel(x_col)
        ax1.grid(True)

        # --- RIGHT Y AXIS ---
        if enable_dual_y_axes:
            ax2 = ax1.twinx()
            right_y_indices = input("Enter indices for right Y axis column(s) (comma-separated): ")
            right_y_cols = [df.columns[int(i.strip())] for i in right_y_indices.split(',')]
            right_label = input("Enter RIGHT Y-axis label: ")
            right_units = input("Enter RIGHT Y-axis units: ")

            if custom_legend_names:
                right_legends = [input(f"Legend for '{col}': ") for col in right_y_cols]
            else:
                right_legends = right_y_cols

            for idx, (col, legend) in enumerate(zip(right_y_cols, right_legends)):
                color = right_colors[idx % len(right_colors)]
                ax2.plot(df[x_col], df[col], label=legend, linewidth=line_width, color=color, linestyle='--')

            ax2.set_ylabel(f"{right_label} [{right_units}]")

        # Combine legends from both axes
        handles, labels = ax1.get_legend_handles_labels()
        if ax2:
            handles2, labels2 = ax2.get_legend_handles_labels()
            handles += handles2
            labels += labels2
        if custom_title:
            title = input("Enter title: ")
        else:
            title = f"{left_label} & {right_label if ax2 else ''} vs {x_col}"
            
        plt.title(title)
        plt.legend(handles, labels)
        plt.tight_layout()
        plt.show()

    except (IndexError, ValueError) as e:
        print(f"Error: {e}. Please enter valid column indices.")

if __name__ == "__main__":
    plot_from_csv()