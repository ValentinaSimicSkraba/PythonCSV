import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def plot_from_csv():
    # Create a Tkinter root window (it will be hidden)
    root = Tk()
    root.withdraw()  # Hide the root window

    # Open a file dialog to select the CSV file
    csv_file = askopenfilename(filetypes=[("CSV files", "*.csv")])
    
    if not csv_file:
        print("No file selected.")
        return

    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Display the column names
    print("\nAvailable columns:")
    for i, column in enumerate(df.columns):
        print(f"{i}: {column}")
    
    try:
        # Prompt for X and Y column indices
        x_col_index = int(input("\nEnter the index of the column for the X axis: "))
        y_col_indices = input("Enter the indices of one or more Y axis columns (comma-separated): ")

        x_col = df.columns[x_col_index]
        y_cols = [df.columns[int(i.strip())] for i in y_col_indices.split(',')]

        # Plot the data
        plt.figure(figsize=(12, 7))
        for y_col in y_cols:
            plt.plot(df[x_col], df[y_col], label=y_col)

        plt.xlabel(x_col)
        plt.ylabel("Values")
        plt.title(f"Plot of {', '.join(y_cols)} vs {x_col}")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    
    except (IndexError, ValueError) as e:
        print(f"Error: {e}. Please enter valid column indices.")

if __name__ == "__main__":
    plot_from_csv()
