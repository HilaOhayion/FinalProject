import pandas as pd
import os

# Define paths
data_folder = "clean_dataset"
output_file = "experiment_statistics.csv"

# Set to store unique combinations
unique_combinations = set()

# Process each CSV file
for file in os.listdir(data_folder):
    if file.startswith("Participant_") and "unidentified" not in file.lower() and file.endswith(".csv"):
        file_path = os.path.join(data_folder, file)
        df = pd.read_csv(file_path, usecols=["Participant", "Experiment", "Stimulus"])
        # Ensure column ordering is consistent
        for row in df.itertuples(index=False):
            unique_combinations.add((row.Participant, row.Experiment, row.Stimulus))

# Convert to DataFrame and sort by "Stimulus"
unique_df = pd.DataFrame(list(unique_combinations), columns=["Participant", "Experiment", "Stimulus"])
unique_df = unique_df.sort_values(by="Stimulus")

# Save to the new CSV file
unique_df.to_csv(output_file, index=False)

print("Done. Unique combinations saved to:", output_file)
