import pandas as pd
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Hide the root tkinter window
root = Tk()
root.withdraw()

# Prompt user to select a file
print("Please select a CSV or Excel file:")
file_path = askopenfilename(filetypes=[("CSV and Excel files", "*.csv *.xlsx")])

if not file_path:
    print("No file selected. Exiting.")
    exit()

filename = os.path.basename(file_path)
file_extension = filename.split('.')[-1]

# Read the selected file
if file_extension == 'csv':
    df = pd.read_csv(file_path, encoding='windows-1252')
elif file_extension == 'xlsx':
    df = pd.read_excel(file_path)
else:
    raise ValueError("Unsupported file format. Use .csv or .xlsx")

# Show indexed column list
print("\nAvailable columns:")
for idx, col in enumerate(df.columns):
    print(f"{idx}: {col}")

# User selects by index
selected_indices = input("\nEnter index number(s) of columns to check for duplicates (comma-separated): ")
selected_indices = [int(i.strip()) for i in selected_indices.split(',')]

# Map indices to column names
selected_columns = [df.columns[i] for i in selected_indices]

# Drop duplicates
df_cleaned = df.drop_duplicates(subset=selected_columns)

# Construct output filename
base_name, ext = os.path.splitext(file_path)
output_filename = f"{base_name}_cleaned{ext}"

# Save the cleaned file
if file_extension == 'csv':
    df_cleaned.to_csv(output_filename, index=False)
elif file_extension == 'xlsx':
    df_cleaned.to_excel(output_filename, index=False)

print(f"\nDuplicate rows based on column(s) {selected_columns} removed.")
print(f"Cleaned data saved to '{output_filename}'.")