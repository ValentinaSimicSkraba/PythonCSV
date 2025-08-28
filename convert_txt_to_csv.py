import os
import pandas as pd
from tkinter import Tk, filedialog

def convert_txt_to_csv():
    # Ask user to select the folder
    root = Tk()
    root.withdraw()  # Hide the main Tk window
    folder_path = filedialog.askdirectory(title="Select folder with TXT files")
    
    if not folder_path:
        print("No folder selected. Exiting.")
        return

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            txt_path = os.path.join(folder_path, filename)

            # Read TXT with space (or multiple spaces) as delimiter
            df = pd.read_csv(txt_path, delimiter=r"\s+", engine="python")

            # Create CSV filename
            csv_filename = os.path.splitext(filename)[0] + ".csv"
            csv_path = os.path.join(folder_path, csv_filename)

            # Save as CSV with comma delimiter
            df.to_csv(csv_path, index=False)

            print(f"Converted: {filename} -> {csv_filename}")

if __name__ == "__main__":
    convert_txt_to_csv()
