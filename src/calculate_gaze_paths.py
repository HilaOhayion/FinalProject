import os
import pandas as pd
import numpy as np
import math
from src.load_data import *

def create_average_paths_files():
    """Compute the average gaze path for each stimulus and save as a new file."""
    os.makedirs(average_paths_folder, exist_ok=True)
    experiment_stats = pd.read_csv(experiment_statistics_file)
    
    grouped = experiment_stats.groupby('Stimulus')
    
    for stimulus, group in grouped:
        all_data = []
        
        for _, row in group.iterrows():
            participant = row['Participant']
            experiment = row['Experiment']
            file_path = os.path.join(participant_dataset, f"Participant_{participant}.csv")
            
            if not os.path.exists(file_path):
                continue
            
            df = pd.read_csv(file_path)
            df_filtered = df[(df['Experiment'] == experiment) & (df['Stimulus'] == stimulus)]
            
            # Excludes from the calculations lines which are categorized as blinks or are all 0
            df_filtered = df_filtered[(df_filtered['Category Left'] != 'Blink') & (df_filtered['Category Right'] != 'Blink')]
            df_filtered = df_filtered.loc[(df_filtered.iloc[:, 2:] != 0).any(axis=1)]
            
            # Convert gaze coordinates to numeric to prevent errors
            gaze_columns = ['Point of Regard Right X [px]', 'Point of Regard Right Y [px]',
                            'Point of Regard Left X [px]', 'Point of Regard Left Y [px]']
            df_filtered[gaze_columns] = df_filtered[gaze_columns].apply(pd.to_numeric, errors='coerce')
            
            all_data.append(df_filtered)
        
        if not all_data:
            continue
        
        # Averages all the gaze coordinates which has the same snapped time per stimulus 
        combined_df = pd.concat(all_data)
        avg_df = combined_df.groupby('SnappedTime')[gaze_columns].mean()

        rename_average_gaze_columns(avg_df)
        force_columns_to_numeric(avg_df)
                
        output_file = os.path.join(average_paths_folder, f"AveragePath_{stimulus}.csv")
        avg_df.to_csv(output_file)
    
    print("Average path calculations complete. Results saved.") 

def rename_average_gaze_columns(avg_df):
    """
    Rename columns to make calculations between these files and the participant files easier 
    in the following calculations    
    """
    avg_df.rename(columns={
        'Point of Regard Right X [px]': 'Avg Right X',
        'Point of Regard Right Y [px]': 'Avg Right Y',
        'Point of Regard Left X [px]': 'Avg Left X',
        'Point of Regard Left Y [px]': 'Avg Left Y'
    }, inplace=True)

def force_columns_to_numeric(avg_df):
    """forcing the results to be numeric to avoid type errors in the future"""
    avg_df['Avg Right X'] = pd.to_numeric(avg_df['Avg Right X'], errors='coerce')
    avg_df['Avg Right Y'] = pd.to_numeric(avg_df['Avg Right Y'], errors='coerce')
    avg_df['Avg Left X'] = pd.to_numeric(avg_df['Avg Left X'], errors='coerce')
    avg_df['Avg Left Y'] = pd.to_numeric(avg_df['Avg Left Y'], errors='coerce')

def calculate_gaze_deviation():
    """
    Calculates the distance of the participant's gaze from the average path for the stimulus for each 
    datapoint recorded. It then writes the results in three new columns in the participant files. 
    One column for the distance of the right eye, one for the distance of the left eye, and one for overall distance.
    The overall distance is calculated as either the average of both eyes or, if one of them is 0, 
    as equal to the one with the data.
    """
    # Get list of all participant files
    participant_files = [os.path.join(participant_dataset, f) for f in os.listdir(participant_dataset) 
                        if f.startswith("Participant_") and f.endswith(".csv")]
    
    for participant_file in participant_files:
        try:
            # Load participant data with mixed type handling
            participant_df = pd.read_csv(participant_file, low_memory=False)
            
            # Ensure numeric columns are properly converted
            for col in ["Point of Regard Right X [px]", "Point of Regard Right Y [px]", 
                       "Point of Regard Left X [px]", "Point of Regard Left Y [px]"]:
                participant_df[col] = pd.to_numeric(participant_df[col], errors='coerce')
            
            # Initialize new columns for deviations
            participant_df["Gaze Deviation Right"] = 0.0
            participant_df["Gaze Deviation Left"] = 0.0
            participant_df["Overall Gaze Deviation"] = 0.0
            
            # Process each stimulus separately
            for stimulus in participant_df["Stimulus"].unique():
                if pd.isna(stimulus):
                    print(f"Warning: Found NaN stimulus value. Skipping.")
                    continue
                
                # Load average path data for this stimulus
                avg_path_file = os.path.join(average_paths_folder, f"AveragePath_{stimulus}.csv")
                
                if not os.path.exists(avg_path_file):
                    print(f"Warning: Average path file for stimulus '{stimulus}' not found. Skipping.")
                    continue
                    
                avg_df = pd.read_csv(avg_path_file)
                
                # Ensure numeric columns in average data
                for col in ["Avg Right X", "Avg Right Y", "Avg Left X", "Avg Left Y"]:
                    avg_df[col] = pd.to_numeric(avg_df[col], errors='coerce')
                
                # Create a dictionary for faster lookup of average values by snapped time
                avg_lookup = {}
                for _, row in avg_df.iterrows():
                    time = row["SnappedTime"]
                    avg_lookup[time] = {
                        "right_x": row["Avg Right X"],
                        "right_y": row["Avg Right Y"],
                        "left_x": row["Avg Left X"],
                        "left_y": row["Avg Left Y"]
                    }
                
                # Filter participant data for current stimulus
                stimulus_mask = participant_df["Stimulus"] == stimulus
                
                # Loop through rows for this stimulus and calculate deviations
                for idx in participant_df[stimulus_mask].index:
                    row = participant_df.loc[idx]
                    snapped_time = row["SnappedTime"]
                    
                    # Skip if this snapped time doesn't exist in average data
                    if snapped_time not in avg_lookup:
                        continue
                    
                    # Skip if category is "blink"
                    if (row.get("Category Left") == "blink" or row.get("Category Right") == "blink"):
                        continue
                    
                    avg_data = avg_lookup[snapped_time]
                    
                    # Calculate Euclidean distance for each eye
                    right_dist = calculate_distance_per_eye(
                        row,
                        "Point of Regard Right X [px]", 
                        "Point of Regard Right Y [px]",
                        "right_x","right_y",
                        avg_data
                    )
                    left_dist = calculate_distance_per_eye(
                        row, 
                        "Point of Regard Left X [px]", 
                        "Point of Regard Left Y [px]",
                        "left_x","left_y",
                        avg_data
                    )

                    # Assign calculated values to the dataframe
                    participant_df.at[idx, "Gaze Deviation Right"] = right_dist
                    participant_df.at[idx, "Gaze Deviation Left"] = left_dist
                    
                    # Calculate overall deviation
                    if right_dist > 0 and left_dist > 0:
                        overall_dist = (right_dist + left_dist) / 2
                    elif right_dist > 0:
                        overall_dist = right_dist
                    elif left_dist > 0:
                        overall_dist = left_dist
                    else:
                        overall_dist = 0
                    
                    participant_df.at[idx, "Overall Gaze Deviation"] = overall_dist
            
            # Save the updated dataframe back to the original file
            participant_df.to_csv(participant_file, index=False)
            print(f"Completed calculating gaze deviations for: {os.path.basename(participant_file)}")
        
        except Exception as e:
            print(f"Error calculating gaze deviations for: {os.path.basename(participant_file)}: {str(e)}")
            continue

def calculate_distance_per_eye(row, x_coordinate_column, y_coordinate_column,avg_x,avg_y,avg_data):
    """Calculate Euclidean distance for each eye."""
    eye_distance = 0
    if not (pd.isna(row[x_coordinate_column]) or pd.isna(row[y_coordinate_column])):
        # Skip if coordinates are all zeros
        if row[x_coordinate_column] == 0 and row[y_coordinate_column] == 0:
            pass
        else:
            right_x_diff = float(row[x_coordinate_column]) - float(avg_data[avg_x])
            right_y_diff = float(row["Point of Regard Right Y [px]"]) - float(avg_data[avg_y])
            eye_distance = math.sqrt(right_x_diff**2 + right_y_diff**2)
    return eye_distance
    