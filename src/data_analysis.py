import os
import pandas as pd
import numpy as np


def load_experiment_statistics(file_path):
    """Load the experiment_statistics.csv file and return it as a DataFrame."""
    return pd.read_csv(file_path)

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

def analyze_saccades(data_folder, experiment_stats_path):
    """Analyze saccade frequency and duration for each participant-experiment-stimulus combination."""
    # Load the experiment statistics file
    experiment_stats = load_experiment_statistics(experiment_stats_path)
    
    # Initialize new columns to store results
    experiment_stats['Saccade_Frequency'] = 0.0
    experiment_stats['Avg_Saccade_Duration'] = 0.0
    
    # Iterate over each row in experiment statistics
    for index, row in experiment_stats.iterrows():
        participant = row['Participant']
        experiment = row['Experiment']
        stimulus = row['Stimulus']
        
        # Construct the file path for the participant data
        file_path = os.path.join(data_folder, f"Participant_{participant}.csv")
        
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
    experiment_stats.to_csv(experiment_stats_path, index=False)
    print("Analysis complete. Results saved.")

def calculate_average_paths(data_folder, experiment_stats_path, output_folder):
    """Compute the average gaze path for each stimulus and save as a new file."""
    os.makedirs(output_folder, exist_ok=True)
    experiment_stats = load_experiment_statistics(experiment_stats_path)
    
    grouped = experiment_stats.groupby('Stimulus')
    
    for stimulus, group in grouped:
        all_data = []
        
        for _, row in group.iterrows():
            participant = row['Participant']
            experiment = row['Experiment']
            file_path = os.path.join(data_folder, f"Participant_{participant}.csv")
            
            if not os.path.exists(file_path):
                continue
            
            df = pd.read_csv(file_path)
            df_filtered = df[(df['Experiment'] == experiment) & (df['Stimulus'] == stimulus)]
            
            df_filtered = df_filtered[(df_filtered['Category Left'] != 'Blink') & (df_filtered['Category Right'] != 'Blink')]
            df_filtered = df_filtered.loc[(df_filtered.iloc[:, 2:] != 0).any(axis=1)]
            
            # Convert gaze coordinates to numeric to prevent errors
            gaze_columns = ['Point of Regard Right X [px]', 'Point of Regard Right Y [px]',
                            'Point of Regard Left X [px]', 'Point of Regard Left Y [px]']
            df_filtered[gaze_columns] = df_filtered[gaze_columns].apply(pd.to_numeric, errors='coerce')
            
            all_data.append(df_filtered)
        
        if not all_data:
            continue
        
        combined_df = pd.concat(all_data)
        avg_df = combined_df.groupby('SnappedTime')[gaze_columns].mean()

        # Rename columns to make calculations between these files and the participant files easier 
        # in the following calculations
        avg_df.rename(columns={
            'Point of Regard Right X [px]': 'Avg Right X',
            'Point of Regard Right Y [px]': 'Avg Right Y',
            'Point of Regard Left X [px]': 'Avg Left X',
            'Point of Regard Left Y [px]': 'Avg Left Y'
        }, inplace=True)

        # forcing the results to be numeric to avoid type errors
        avg_df['Avg Right X'] = pd.to_numeric(avg_df['Avg Right X'], errors='coerce')
        avg_df['Avg Right Y'] = pd.to_numeric(avg_df['Avg Right Y'], errors='coerce')
        avg_df['Avg Left X'] = pd.to_numeric(avg_df['Avg Left X'], errors='coerce')
        avg_df['Avg Left Y'] = pd.to_numeric(avg_df['Avg Left Y'], errors='coerce')
                
        output_file = os.path.join(output_folder, f"AveragePath_{stimulus}.csv")
        avg_df.to_csv(output_file)
    
    print("Average path calculations complete. Results saved.")

def calculate_gaze_deviation(data_folder, avg_paths_folder):
    """Calculate gaze deviation from the average path and update participant files."""
    for file in os.listdir(data_folder):
        if file.startswith("Participant_") and file.endswith(".csv"):
            file_path = os.path.join(data_folder, file)
            df = pd.read_csv(file_path)
            
            # Initialize new columns with NaN to ensure original file structure remains
            df['Gaze Deviation Right'] = np.nan
            df['Gaze Deviation Left'] = np.nan
            df['Overall Gaze Deviation'] = np.nan

            for stimulus in df['Stimulus'].unique():
                avg_path_file = os.path.join(avg_paths_folder, f"AveragePath_{stimulus}.csv")
                if not os.path.exists(avg_path_file):
                    continue
                
                avg_df = pd.read_csv(avg_path_file)
                
                for snapped_time in df['SnappedTime'].unique():
                    if pd.isna(snapped_time):
                        continue
                    
                    avg_row = avg_df[avg_df['SnappedTime'] == snapped_time]
                    if avg_row.empty:
                        continue
                    
                    avg_x_right = avg_row['Avg Right X'].values[0]
                    avg_y_right = avg_row['Avg Right Y'].values[0]
                    avg_x_left = avg_row['Avg Left X'].values[0]
                    avg_y_left = avg_row['Avg Left Y'].values[0]
                    
                    indices = df[(df['Stimulus'] == stimulus) & (df['SnappedTime'] == snapped_time)].index
                    
                    for idx in indices:
                        if (df.at[idx, 'Category Left'] == 'Blink' or df.at[idx, 'Category Right'] == 'Blink' or
                            (df.at[idx, 'Point of Regard Right X [px]'] == 0 and df.at[idx, 'Point of Regard Right Y [px]'] == 0 and
                             df.at[idx, 'Point of Regard Left X [px]'] == 0 and df.at[idx, 'Point of Regard Left Y [px]'] == 0)):
                            continue
                        
                        right_x = pd.to_numeric(df.at[idx, 'Point of Regard Right X [px]'], errors='coerce')
                        right_y = pd.to_numeric(df.at[idx, 'Point of Regard Right Y [px]'], errors='coerce')
                        left_x = pd.to_numeric(df.at[idx, 'Point of Regard Left X [px]'], errors='coerce')
                        left_y = pd.to_numeric(df.at[idx, 'Point of Regard Left Y [px]'], errors='coerce')

                        avg_x_right = pd.to_numeric(avg_x_right, errors='coerce')
                        avg_y_right = pd.to_numeric(avg_y_right, errors='coerce')
                        avg_x_left = pd.to_numeric(avg_x_left, errors='coerce')
                        avg_y_left = pd.to_numeric(avg_y_left, errors='coerce')
                                                
                        right_dist = np.sqrt((right_x - avg_x_right) ** 2 + (right_y - avg_y_right) ** 2)
                        left_dist = np.sqrt((left_x - avg_x_left) ** 2 + (left_y - avg_y_left) ** 2)
                        
                        df.at[idx, 'Gaze Deviation Right'] = right_dist
                        df.at[idx, 'Gaze Deviation Left'] = left_dist
                        df.at[idx, 'Overall Gaze Deviation'] = (right_dist + left_dist) / 2
            
            df.to_csv(file_path, index=False)
            print(f"Updated {file_path} with gaze deviations.")  

def calculate_experiment_deviation(data_folder, experiment_stats_path):
    """Calculate gaze deviation statistics and update experiment statistics."""
    experiment_stats = load_experiment_statistics(experiment_stats_path)
    experiment_stats['Fixation Deviation'] = np.nan
    experiment_stats['Saccade Deviation'] = np.nan
    experiment_stats['Overall Deviation'] = np.nan
    
    for file in os.listdir(data_folder):
        if file.startswith("Participant_") and file.endswith(".csv"):
            file_path = os.path.join(data_folder, file)
            df = pd.read_csv(file_path, low_memory=False)
            
            for index, row in experiment_stats.iterrows():
                participant, experiment, stimulus = row['Participant'], row['Experiment'], row['Stimulus']
                df_filtered = df[(df['Experiment'] == experiment) & (df['Stimulus'] == stimulus)]
                
                fixation_deviation = df_filtered.loc[df_filtered['Category Left'] == 'Fixation', 'Overall Gaze Deviation'].mean()
                saccade_deviation = df_filtered.loc[df_filtered['Category Left'] == 'Saccade', 'Overall Gaze Deviation'].mean()
                overall_deviation = df_filtered['Overall Gaze Deviation'].mean()
                
                experiment_stats.at[index, 'Fixation Deviation'] = fixation_deviation
                experiment_stats.at[index, 'Saccade Deviation'] = saccade_deviation
                experiment_stats.at[index, 'Overall Deviation'] = overall_deviation
    
    experiment_stats.to_csv(experiment_stats_path, index=False)
    print("Experiment deviation calculations complete.")

# Example usage:
data_folder = "clean_dataset"
experiment_stats_path = "experiment_statistics.csv"
output_folder = "calculated_average_paths"

#analyze_saccades(data_folder, experiment_stats_path)
calculate_average_paths(data_folder, experiment_stats_path, output_folder)
calculate_gaze_deviation(data_folder, output_folder)
calculate_experiment_deviation(data_folder, experiment_stats_path)