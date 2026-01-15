import pandas as pd
import os
# Load the file (update the filename and extension if needed)
filename = "INPUT_MTU_density.csv"  # or 'your_file.xlsx'
file_extension = filename.split('.')[-1]

# Read the file
if file_extension == 'csv':
    df = pd.read_csv(filename,encoding='windows-1252')
elif file_extension == 'xlsx':
    df = pd.read_excel(filename)
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
base_name, ext = os.path.splitext(filename)
output_filename = f"{base_name}_cleaned_file{ext}"

# Save the cleaned file
if file_extension == 'csv':
    df_cleaned.to_csv(output_filename, index=False)
elif file_extension == 'xlsx':
    df_cleaned.to_excel(output_filename, index=False)

print(f"\nDuplicate rows based on column(s) {selected_columns} removed.")
print(f"Cleaned data saved to '{output_filename}'.")

print(f"\nDuplicate rows based on column(s) {selected_columns} removed.")
print(f"Cleaned data saved to '{output_filename}'.")