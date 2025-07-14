import os
import csv
from tkinter import Tk
from tkinter.filedialog import askdirectory

def list_files_in_folder():
    # Ask user to select a folder
    root = Tk()
    root.withdraw()
    folder_path = askdirectory(title="Select Folder with Files")
    
    if not folder_path:
        print("No folder selected.")
        return

    # Get list of files (not folders)
    file_names = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Define output CSV path
    output_csv = os.path.join(folder_path, "file_list.csv")

    # Write to CSV
    with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename"])  # Header
        for name in file_names:
            writer.writerow([name])
    
    print(f"Saved file list to {output_csv}")

if __name__ == "__main__":
    list_files_in_folder()
