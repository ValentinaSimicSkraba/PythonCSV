import pandas as pd
import numpy as np

# Replace with your filename
filename = 'ForwardCombustion_calculated_pressure_cleaned_file.csv'  # The file should have at least two columns: time and value

def differentiate(data, time_col, value_col):
    t = data[time_col].values
    y = data[value_col].values
    dy_dt = np.zeros_like(y)

    # Forward difference for first point
    dy_dt[0] = (y[1] - y[0]) / (t[1] - t[0])

    # Central difference for internal points
    for i in range(1, len(y)-1):
        dy_dt[i] = (y[i+1] - y[i-1]) / (t[i+1] - t[i-1])

    # Backward difference for last point
    dy_dt[-1] = (y[-1] - y[-2]) / (t[-1] - t[-2])

    return dy_dt

def main():
    # Load CSV
    df = pd.read_csv(filename)
    print("Columns in file:", list(df.columns))

    # Change these if your column names are different
    time_col = 'crank'
    value_col = 'Pressure'

    df['dvalue_dt'] = differentiate(df, time_col, value_col)

    # Save result
    output_filename = filename.replace('.csv', '_differentiated.csv')
    df.to_csv(output_filename, index=False)
    print(f"Saved differentiated data to {output_filename}")

if __name__ == '__main__':
    main()
