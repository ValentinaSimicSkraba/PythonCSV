import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

def merge_csv_on_time_with_suffix_and_spacer():
    root = Tk()
    root.withdraw()

    print("Select the first CSV file...")
    file1 = askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file1:
        print("No file selected.")
        return
    suffix1 = input("Enter suffix for the first file (e.g., '_sim'): ")

    print("\nSelect the second CSV file...")
    file2 = askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file2:
        print("No file selected.")
        return
    suffix2 = input("Enter suffix for the second file (e.g., '_real'): ")

    # Load files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Rename columns except 'time'
    df1_renamed = df1.rename(columns={col: col + suffix1 for col in df1.columns if col != 'time'})
    df2_renamed = df2.rename(columns={col: col + suffix2 for col in df2.columns if col != 'time'})

    # Merge on 'time'
    df_merged = pd.merge(df1_renamed, df2_renamed, on='time', how='outer')

    # Reorder columns: time, df1 columns, spacer, df2 columns
    time_col = df_merged[['time']]
    df1_only_cols = [col for col in df1_renamed.columns if col != 'time']
    df2_only_cols = [col for col in df2_renamed.columns if col != 'time']

    df1_part = df_merged[df1_only_cols]
    df2_part = df_merged[df2_only_cols]

    spacer = pd.DataFrame({'': [''] * len(df_merged)})

    df_final = pd.concat([time_col, df1_part, spacer, df2_part], axis=1)

    # Save merged file
    print("\nSelect where to save the merged CSV...")
    save_path = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if save_path:
        df_final.to_csv(save_path, index=False)
        print(f"Merged file saved to: {save_path}")
    else:
        print("Save canceled.")

if __name__ == "__main__":
    merge_csv_on_time_with_suffix_and_spacer()