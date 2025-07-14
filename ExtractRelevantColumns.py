import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

def keep_selected_columns():
    # Hide the root window
    root = Tk()
    root.withdraw()

    print("Select the CSV file to filter...")
    csv_file = askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not csv_file:
        print("No file selected.")
        return

    # df = pd.read_csv(csv_file)
    df = pd.read_csv(csv_file, sep=';')

    # Display columns with indices
    print("\nAvailable columns:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")

    # Prompt user for indices to keep
    indices_to_keep = input(
        "\nEnter the indices of columns you want to KEEP (comma-separated): "
    )
    try:
        indices = [int(i.strip()) for i in indices_to_keep.split(",") if i.strip().isdigit()]
    except ValueError:
        print("Invalid input. Please enter integers separated by commas.")
        return

    columns_to_keep = [df.columns[i] for i in indices]
    print(f"\nKeeping columns: {columns_to_keep}")
    df_filtered = df[columns_to_keep]

    # Save filtered file
    print("\nSelect where to save the new CSV...")
    save_path = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if save_path:
        df_filtered.to_csv(save_path, index=False)
        print(f"Filtered file saved to: {save_path}")
    else:
        print("Save canceled.")

if __name__ == "__main__":
    keep_selected_columns()