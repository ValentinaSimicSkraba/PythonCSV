import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

def column_operation():
    # Hide the root window
    root = Tk()
    root.withdraw()

    print("Select the CSV file...")
    csv_file = askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not csv_file:
        print("No file selected.")
        return

    df = pd.read_csv(csv_file)

    # Show available columns
    print("\nAvailable columns:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")

    print("\nChoose an operation:")
    print("1 = Add two columns")
    print("2 = Subtract column B from column A")
    print("3 = Multiply a column by a number")
    choice = input("Enter operation number (1, 2, or 3): ")

    try:
        choice = int(choice)
    except ValueError:
        print("Invalid choice.")
        return

    if choice in [1, 2]:
        col1_index = int(input("Enter the index of column A: "))
        col2_index = int(input("Enter the index of column B: "))
        col1 = df.columns[col1_index]
        col2 = df.columns[col2_index]

        if choice == 1:
            df["Result"] = df[col1] + df[col2]
            print(f"Added '{col1}' + '{col2}' into 'Result'")
        else:
            df["Result"] = df[col1] - df[col2]
            print(f"Subtracted '{col2}' from '{col1}' into 'Result'")

    elif choice == 3:
        col_index = int(input("Enter the index of the column to multiply: "))
        multiplier = float(input("Enter the number to multiply with: "))
        col = df.columns[col_index]
        df["Result"] = df[col] * multiplier
        print(f"Multiplied '{col}' by {multiplier} into 'Result'")

    else:
        print("Invalid operation selected.")
        return

    # Save the result
    print("\nSelect where to save the new CSV file...")
    save_path = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if save_path:
        df.to_csv(save_path, index=False)
        print(f"Modified file saved to: {save_path}")
    else:
        print("Save canceled.")

if __name__ == "__main__":
    column_operation()