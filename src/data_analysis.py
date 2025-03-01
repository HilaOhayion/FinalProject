import pandas as pd
import os
from src.load_data import *

def create_experiment_statistics_file():
    """
    Creates a file which contains a list of all possible combinations of participant, experiment 
    and stimulus.  
    """
    # Set to store unique combinations
    unique_combinations = set()

    # Process each CSV file
    for file in os.listdir(participant_dataset):
        if file.startswith("Participant_") and "unidentified" not in file.lower() and file.endswith(".csv"):
            file_path = os.path.join(participant_dataset, file)
            df = pd.read_csv(file_path, usecols=["Participant", "Experiment", "Stimulus"])

        # Ensure column ordering is consistent
        for row in df.itertuples(index=False):
            unique_combinations.add((row.Participant, row.Experiment, row.Stimulus))

    # Convert to DataFrame and sort by "Stimulus"
    unique_df = pd.DataFrame(list(unique_combinations), columns=["Participant", "Experiment", "Stimulus"])
    unique_df = unique_df.sort_values(by="Stimulus")

    # Save to the new CSV file
    unique_df.to_csv(experiment_statistics_file, index=False)

    print("Done. Created file:", experiment_statistics_file)

def compute_saccade_frequency(df_filtered):
    """Compute the frequency of saccades out of total saccades and fixations."""
    is_saccade = (df_filtered['Category Left'] == 'Saccade') | (df_filtered['Category Right'] == 'Saccade')
    is_fixation = (df_filtered['Category Left'] == 'Fixation') | (df_filtered['Category Right'] == 'Fixation')
    
    num_saccades = is_saccade.sum()
    num_fixations = is_fixation.sum()
    total_relevant = num_saccades + num_fixations
    
    return num_saccades / total_relevant if total_relevant > 0 else 0

def compute_avg_saccade_duration(df_filtered):
    """Compute the average saccade duration, excluding the first row where a saccade appears."""
    is_saccade = (df_filtered['Category Left'] == 'Saccade') | (df_filtered['Category Right'] == 'Saccade')
    saccade_durations = df_filtered['Duration'][is_saccade].shift(-1).dropna()
    
    return saccade_durations.mean() if not saccade_durations.empty else 0

def analyze_saccades():
    """Analyze saccade frequency and duration for each participant-experiment-stimulus combination
    and writes it to the experiment statistics file."""
    # Load the experiment statistics file
    experiment_stats = pd.read_csv(experiment_statistics_file)
    
    # Initialize new columns to store results
    experiment_stats['Saccade_Frequency'] = 0.0
    experiment_stats['Avg_Saccade_Duration'] = 0.0
    
    # Iterate over each row in experiment statistics
    for index, row in experiment_stats.iterrows():
        participant = row['Participant']
        experiment = row['Experiment']
        stimulus = row['Stimulus']
        
        # Construct the file path for the participant data
        file_path = os.path.join(participant_dataset, f"Participant_{participant}.csv")
        
        # Skip if the participant file does not exist
        if not os.path.exists(file_path):
            continue  
        
        # Load the participant's data file
        df = pd.read_csv(file_path)
        
        # Filter data for the specific experiment and stimulus
        df_filtered = df[(df['Experiment'] == experiment) & (df['Stimulus'] == stimulus)]
        
        # Skip if no relevant data is found
        if df_filtered.empty:
            continue
        
        # Compute saccade frequency and average saccade duration
        saccade_freq = compute_saccade_frequency(df_filtered)
        avg_saccade_duration = compute_avg_saccade_duration(df_filtered)
        
        # Store the computed values in the experiment statistics DataFrame
        experiment_stats.at[index, 'Saccade_Frequency'] = saccade_freq
        experiment_stats.at[index, 'Avg_Saccade_Duration'] = avg_saccade_duration
    
    # Save the updated experiment statistics back to CSV
    experiment_stats.to_csv(experiment_statistics_file, index=False)
    print("Saccade analysis complete. Results saved.")

def calculate_gaze_path_average(idx,filtered_data,experiment_stats):
    """Calculate overall average gaze coordinates (excluding zeros)"""
    overall_deviations = filtered_data[filtered_data["Overall Gaze Deviation"] > 0]["Overall Gaze Deviation"]
    if not overall_deviations.empty:
        experiment_stats.at[idx, "Avg_Gaze_Deviation"] = overall_deviations.mean()
  
def calculate_fixation_path_average(idx,filtered_data,experiment_stats):
    """Calculate average gaze coordinates but only for fixation (excluding zeros)"""
    fixation_mask = (
        (filtered_data["Category Left"] == "Fixation") | 
        (filtered_data["Category Right"] == "Fixation")
    ) & (filtered_data["Overall Gaze Deviation"] > 0)
    
    fixation_deviations = filtered_data[fixation_mask]["Overall Gaze Deviation"]
    if not fixation_deviations.empty:
        experiment_stats.at[idx, "Avg_Fixation_Deviation"] = fixation_deviations.mean()

def calculate_seccade_path_average(idx,filtered_data,experiment_stats):
    """Calculate average gaze coordinates but only for seccades (excluding zeros)"""
    saccade_mask = (
        (filtered_data["Category Left"] == "Saccade") | 
        (filtered_data["Category Right"] == "Saccade")
    ) & (filtered_data["Overall Gaze Deviation"] > 0)
    
    saccade_deviations = filtered_data[saccade_mask]["Overall Gaze Deviation"]
    if not saccade_deviations.empty:
        experiment_stats.at[idx, "Avg_Saccade_Deviation"] = saccade_deviations.mean()

def calculate_experiment_deviation():
    # Load experiment statistics file
    experiment_stats = pd.read_csv(experiment_statistics_file)
    
    # Initialize new columns for averages
    experiment_stats["Average Gaze Deviation"] = 0.0
    experiment_stats["Average Fixation Deviation"] = 0.0
    experiment_stats["Average Saccade Deviation"] = 0.0
    
    # Get list of all participant files
    participant_files = [os.path.join(participant_dataset, f) for f in os.listdir(participant_dataset) 
                        if f.startswith("Participant_") and f.endswith(".csv")]
    
    # Dictionary to store participant data
    all_data = {}
    
    # Load all participant data
    for participant_file in participant_files:
        try:
            participant_df = pd.read_csv(participant_file, low_memory=False)
            participant_num = int(os.path.basename(participant_file).split("_")[1].split(".")[0])
            all_data[participant_num] = participant_df
        except Exception as e:
            print(f"Error loading {os.path.basename(participant_file)}: {str(e)}")
    
    # Process each row in experiment statistics
    for idx, row in experiment_stats.iterrows():
        participant = row["Participant"]
        experiment = row["Experiment"]
        stimulus = row["Stimulus"]
        
        if participant not in all_data:
            print(f"Warning: Gaze coordinate data for Participant {participant} not found. Skipping.")
            continue
        
        # Get participant data
        participant_df = all_data[participant]
        
        # Filter for current experiment and stimulus
        mask = (
            (participant_df["Experiment"] == experiment) & 
            (participant_df["Stimulus"] == stimulus)
        )
        
        filtered_data = participant_df[mask]
        
        if filtered_data.empty:
            print(f"No data found for Participant {participant}, Experiment {experiment}, Stimulus '{stimulus}'")
            continue
        
        # Calculate the average deviations of the gaze during fixation, seccades and overall
        calculate_gaze_path_average(idx, filtered_data,experiment_stats)
        calculate_fixation_path_average(idx, filtered_data,experiment_stats)
        calculate_seccade_path_average(idx, filtered_data,experiment_stats)
    
    # Save updated experiment statistics
    experiment_stats.to_csv(experiment_statistics_file, index=False)
    print(f"Averages calculated and saved to {experiment_statistics_file}")

def calculate_participant_averages():
    # Load data
    experiment_stats = pd.read_csv(experiment_statistics_file)
    metadata = pd.read_csv(metadata_participants)
    
    # Columns to analyze
    columns_to_average = [
        "Avg_Gaze_Deviation",
        "Avg_Fixation_Deviation", 
        "Avg_Saccade_Deviation",
        "Saccade_Frequency",
        "Avg_Saccade_Duration"
    ]
    
    # Create output columns in metadata
    for col in columns_to_average:
        output_col = f"Avg_{col.replace('Average ', '')}"
        metadata[output_col] = 0.0
    
    # Process each participant
    for participant_id in metadata["ParticipantID"].unique():
        # Filter experiment stats for this participant
        participant_data = experiment_stats[experiment_stats["Participant"] == participant_id]
        
        if participant_data.empty:
            print(f"No data found for Participant {participant_id}")
            continue
        
        # Calculate averages for each column
        for col in columns_to_average:
            # Skip columns that don't exist yet
            if col not in participant_data.columns:
                print(f"Column {col} not found in experiment stats. Skipping.")
                continue
                
            # Calculate average (excluding zeros)
            non_zero_values = participant_data[participant_data[col] > 0][col]
            
            if not non_zero_values.empty:
                avg_value = non_zero_values.mean()
                output_col = f"{col.replace('Average ', '')}"
                
                # Update metadata
                metadata.loc[metadata["ParticipantID"] == participant_id, output_col] = avg_value
    
    # Save updated metadata
    metadata.to_csv(metadata_participants, index=False)
    print(f"Participant averages calculated and saved to {metadata_participants}")


