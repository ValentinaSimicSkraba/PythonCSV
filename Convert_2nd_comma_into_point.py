from pathlib import Path

data_dir = Path("./data")

for input_path in data_dir.glob("*.csv"):

    # Skip already processed files
    if input_path.stem.endswith("_fixed"):
        continue

    output_path = input_path.with_name(input_path.stem + "_fixed.csv")

    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:

        for i, line in enumerate(fin):

            # Skip the second row
            if i == 1:
                continue

            # Only modify lines that contain at least two commas
            if line.count(",") >= 2:
                first, second, rest = line.split(",", 2)
                line = first + "," + second + "." + rest

            fout.write(line)

    print(f"Fixed: {input_path.name} → {output_path.name}")

print("Done. All CSV files processed.")
