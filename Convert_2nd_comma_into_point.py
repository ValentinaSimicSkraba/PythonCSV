input_file  = "volumeCyl.csv"
output_file = "volumeCyl_fixed.csv"

with open(input_file, "r", encoding="utf-8") as fin, \
     open(output_file, "w", encoding="utf-8") as fout:

    for line in fin:
        # Only modify lines that contain at least two commas
        if line.count(",") >= 2:
            first, second, rest = line.split(",", 2)
            line = first + "," + second + "." + rest
        fout.write(line)

print("Done. Fixed file written to:", output_file)
