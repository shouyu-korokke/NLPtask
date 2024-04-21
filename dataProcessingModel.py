import pandas as pd
import re
import numpy as np

# Load the CSV file
df = pd.read_csv(r"C:\Users\Filip Szmit\Desktop\SEM6\NLP\NLPtask\accidents_data.csv", delimiter=";")

# Initialize lists to store extracted information
places = []
dates = []
vehicles_involved = []
fatalities = []
injuries = []
causes = []

# Define regular expressions for pattern matching
date_regex = r"(?<!\d)(?:\d{1,2}[-/th|st|nd|rd\s]*)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?(?:[-,\s]*\d{2,4})"
fatalities_regex = r"\b(?:died|killed|deceased|fatalities|victims|casualties)\b"
injuries_regex = r"\b(?:injured|wounded|hurt|casualties)\b"

# Iterate over each row in the dataframe
for index, row in df.iterrows():
    # Extract the raw text from the row
    raw_text = row["Raw Text"]
    if pd.isna(raw_text):
        continue  # Skip to the next row if raw text is NaN

    # Extract place where the accident occurred
    place_match = re.search(r"(\b(?:in|at|on)\s+[A-Z][a-z]+(?:[ -][A-Z][a-z]+)*\b)", raw_text)
    if place_match:
        places.append(place_match.group(1))
    else:
        places.append("Unknown")

    # Extract date when the accident occurred
    date_match = re.search(date_regex, raw_text)
    if date_match:
        dates.append(date_match.group(0))
    else:
        dates.append("Unknown")

    # Extract types of vehicles involved
    vehicles_match = re.findall(r"(?:\b(?:car|truck|motorcycle|bus|autorickshaw)\b)", raw_text)
    vehicles_involved.append(", ".join(vehicles_match))

    # Extract information about fatalities
    fatalities_match = re.findall(fatalities_regex, raw_text, flags=re.IGNORECASE)
    fatalities.append(len(fatalities_match))

    # Extract information about injuries
    injuries_match = re.findall(injuries_regex, raw_text, flags=re.IGNORECASE)
    injuries.append(len(injuries_match))

    # Extract reason for the accident
    cause_match = re.search(r"\b(?:reason|cause|cause of accident|reason for accident|trigger|triggered|due to)\b\s*:\s*(.*?)(?=\b(?:at|on)\s+[A-Z][a-z]+(?:[ -][A-Z][a-z]+)*|\b(?:on|at|in)\s+\d{1,2}(?:st|nd|rd|th)?(?:\s+of\s+\w+)?(?:,\s*\d{2,4})?)", raw_text, re.IGNORECASE)
    if cause_match:
        causes.append(cause_match.group(1).strip())
    else:
        causes.append("Unknown")

# Create a new dataframe to store the extracted information
accident_info_df = pd.DataFrame({
    "Place": places,
    "Date": dates,
    "Vehicles Involved": vehicles_involved,
    "Fatalities": fatalities,
    "Injuries": injuries,
    "Cause": causes
})

# Save the extracted information to a new CSV file
accident_info_df.to_csv("accident_info.csv", index=False)

print("Accident-related information extracted and saved to accident_info.csv")
