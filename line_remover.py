import pandas as pd
import csv

# Open the original CSV file and create a new CSV file to store corrected data
with open('FastTrackDeliverables.csv', 'r', encoding='utf-8') as f_in, \
     open('FastTrackDeliverables_corrected.csv', 'w', encoding='utf-8', newline='') as f_out:

    # Initialize a CSV reader and writer
    reader = pd.read_csv(f_in, sep=';', iterator=True, chunksize=1)
    writer = csv.writer(f_out, delimiter=';')

    # Write the header row
    header = next(reader)
    writer.writerow(header.columns)

    # Check each line for the number of fields
    expected_num_fields = 26
    line_number = 2  # Starting from line 2 because we've already read the header
    for chunk in reader:
        if len(chunk.columns) == expected_num_fields:
            writer.writerow(chunk.values.flatten())
        else:
            print(f"Skipping line {line_number} with {len(chunk.columns)} fields (expected {expected_num_fields} fields)")
        line_number += 1

print("Data processing complete.")
