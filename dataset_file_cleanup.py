# This file is mostly for my own convinence so I can use files that are smaller
# and only contain the relevent data.
# What the code here does is take the original files (which are sorted by experiment number rather than
# participant number), takes only the relevant columns and creates new files which are sorted by participant. 



import pandas as pd
from pathlib import Path

# Define the columns to extract
columns_to_keep = [
    "RecordingTime [ms]", "Participant", "Stimulus", "Category Right", "Category Left",
    "Point of Regard Right X [px]", "Point of Regard Right Y [px]",
    "Point of Regard Left X [px]", "Point of Regard Left Y [px]"
]

# Define input and output folders
input_folder = Path("dataset_project/Eye-tracking Output")
output_folder = Path("clean_dataset")
output_folder.mkdir(parents=True, exist_ok=True)

# Dictionary to store participant data across experiments
participant_data = {}

# Process each file
for file in input_folder.glob("*.csv"):
    experiment_id = file.stem  # Extract experiment number from filename

    df = pd.read_csv(file)

    # Ensure column names match
    df = df[[col for col in columns_to_keep if col in df.columns]]
    df["Experiment"] = experiment_id  # Add experiment identifier

    # Group data by participant
    for participant, pdata in df.groupby("Participant"):
        if participant not in participant_data:
            participant_data[participant] = []
        participant_data[participant].append(pdata)

# Save data for each participant
for participant, dataframes in participant_data.items():
    participant_df = pd.concat(dataframes)

    # Check if all required columns are present
    missing_cols = [col for col in columns_to_keep + ["Experiment"] if col not in participant_df.columns]
    if missing_cols:
        print(f"❌ Skipping Participant_{participant}.csv: Missing columns {missing_cols}")
        continue  # Skip saving this participant's file

    participant_df.to_csv(output_folder / f"Participant_{participant}.csv", index=False)

print("Processing complete. Check output folder for results.")
