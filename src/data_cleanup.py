<<<<<<< HEAD
import pandas as pd
import glob
from src.load_data import *

def check_for_missing_columns(df,file_name):
    """
    Checks for missing columns and prints a warning if any are missing
    """
    # Standardize column names
    df.columns = df.columns.str.strip()

    # Ensure required columns exist
    required_columns = [
        "RecordingTime [ms]", "Participant", "Experiment",
        "Category Right", "Category Left",
        "Point of Regard Right X [px]", "Point of Regard Right Y [px]",
        "Point of Regard Left X [px]", "Point of Regard Left Y [px]"
    ]
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols:
        print(f"Warning: Missing columns {missing_cols} in {file_name}")
        return None

    return df

def clean_data(df, file_name):
    """
    This function cleans the data by doing the following:
    1. Checks for missing columns
    2. Removes rows which are seperators and don't contain data
    3. Replaces missing values with 0 
    """

    check_for_missing_columns(df,file_name)

    # Remove rows where both categories are 'Separator'
    df = df[~((df["Category Right"] == "Separator") & (df["Category Left"] == "Separator"))].copy()

    # Replace NaN or missing values with 0
    df = df.fillna(0)

    return df

def normalize_recording_time(df):
    """
    Makes sure the recording time for each experiment is 0 
    """
    # Ensure correct dtype
    df["RecordingTime [ms]"] = df["RecordingTime [ms]"].astype(float)

    # Normalize time per experiment
    df.loc[:, "RecordingTime [ms]"] = df.groupby(["Participant", "Experiment"])["RecordingTime [ms]"].transform(lambda x: x - x.min())

    return df

def normalize_recording_time_per_stimulus(df):
    """Creates a column where the recording time starts at 0 per stimulus"""
    df["RecordingTime Stimulus [ms]"] = df.groupby(["Participant", "Experiment", "Stimulus"])["RecordingTime [ms]"].transform(lambda x: x - x.min())

    return df

def calculate_duration(df):
    """
    Add a column with a duration of each datapoint 
    Writes 0 at the last row per experiment
    """
    df["Duration"] = 0.0  # Initialize column
    df["Duration"] = df["Duration"].astype(float)  # Ensure correct dtype

    for exp, data in df.groupby("Experiment"):
        df.loc[data.index[:-1], "Duration"] = data["RecordingTime [ms]"].diff().shift(-1)

    return df

def calculate_snapped_time(df):
    """
    Creates a new column which calculates the closest 20 ms interval to the recording time per stimulus
    """
    # Initialize SnappedTime
    df["SnappedTime"] = None

    # Process each group separately
    for (participant, experiment, stimulus), group in df.groupby(["Participant", "Experiment", "Stimulus"]):
        times = group["RecordingTime Stimulus [ms]"].values
        intervals = {}  # interval -> (index, distance)
        
        # Find closest interval for each time
        for idx, t in enumerate(times):
            interval = round(t / 20) * 20
            distance = abs(t - interval)
            
            if interval not in intervals or distance < intervals[interval][1]:
                intervals[interval] = (group.index[idx], distance)
        
        # Assign values
        for interval, (idx, _) in intervals.items():
            df.loc[idx, "SnappedTime"] = interval

    return df

def clean_and_extract_eyetracking_data(df, file_name):
    """ 
    Cleans and and extracts relevent data from the raw eye-tracking dataset
    It creates or changes the following columns:
        "RecordingTime [ms]" - Now the recording time starts at 0 for each experiment
        "RecordingTime Stimulus [ms]" - Creates a column where the recording time starts 
        at 0 per each stimulus to allow for comparing stimulus
        "Duration" - Creates a column that counts how much time passed between one recording (row) 
        and the next
        "SnappedTime" - Creates a column which takes the recording time per stimulus and "snaps" it
        to the closest 20 increment integer (i.e. 20, 40, 80, etc.). This allows comparing between 
        different participants and stimulus.  
    """

    clean_data(df, file_name)
    normalize_recording_time(df)
    normalize_recording_time_per_stimulus(df)
    calculate_duration(df)
    calculate_snapped_time(df)
    
    return df

def clean_all_participant_files():
    """
    Goes over all the participant files and applies the clean_and_extract_eyetracking_data function 
    to them
    """
    # Load all participant files
    files = glob.glob(f"{participant_dataset}/*.csv")

    # Process each participant file
    for file in files:
        df = pd.read_csv(file)
        df_cleaned = clean_and_extract_eyetracking_data(df, file)

        if df_cleaned is not None:
            df_cleaned.to_csv(file, index=False)

    print("Data cleaning and extraction complete!")
=======
import pandas as pd
import glob

# Load all participant files
input_folder = "clean_dataset"
files = glob.glob(f"{input_folder}/*.csv")

def clean_eyetracking_data(df, file_name):
    """ Cleans and normalizes the eye-tracking dataset """
    # Standardize column names
    df.columns = df.columns.str.strip()

    # Debugging: Print column names
    print(f"Processing {file_name}")

    # Ensure required columns exist
    required_columns = [
        "RecordingTime [ms]", "Participant", "Experiment",
        "Category Right", "Category Left",
        "Point of Regard Right X [px]", "Point of Regard Right Y [px]",
        "Point of Regard Left X [px]", "Point of Regard Left Y [px]"
    ]
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols:
        print(f"❌ Warning: Missing columns {missing_cols} in {file_name}")
        return None

    # Remove rows where both categories are 'Separator'
    df = df[~((df["Category Right"] == "Separator") & (df["Category Left"] == "Separator"))].copy()

    # Replace NaN or missing values with 0
    df = df.fillna(0)

    # Ensure correct dtype
    df["RecordingTime [ms]"] = df["RecordingTime [ms]"].astype(float)

    # Normalize time per experiment
    df.loc[:, "RecordingTime [ms]"] = df.groupby(["Participant", "Experiment"])["RecordingTime [ms]"].transform(lambda x: x - x.min())

    # Normalize time per stimulus
    df["RecordingTime Stimulus [ms]"] = df.groupby(["Participant", "Experiment", "Stimulus"])["RecordingTime [ms]"].transform(lambda x: x - x.min())

    #Add a column with a duration of each datapoint
    df["Duration"] = 0.0  # Initialize column
    df["Duration"] = df["Duration"].astype(float)  # Ensure correct dtype

    for exp, data in df.groupby("Experiment"):
        df.loc[data.index[:-1], "Duration"] = data["RecordingTime [ms]"].diff().shift(-1)

    # Initialize SnappedTime
    df["SnappedTime"] = None

    # Process each group separately
    for (participant, experiment, stimulus), group in df.groupby(["Participant", "Experiment", "Stimulus"]):
        times = group["RecordingTime Stimulus [ms]"].values
        intervals = {}  # interval -> (index, distance)
        
        # Find closest interval for each time
        for idx, t in enumerate(times):
            interval = round(t / 20) * 20
            distance = abs(t - interval)
            
            if interval not in intervals or distance < intervals[interval][1]:
                intervals[interval] = (group.index[idx], distance)
        
        # Assign values
        for interval, (idx, _) in intervals.items():
            df.loc[idx, "SnappedTime"] = interval
    
    return df

# Process each participant file
for file in files:
    df = pd.read_csv(file)
    df_cleaned = clean_eyetracking_data(df, file)

    if df_cleaned is not None:
        df_cleaned.to_csv(file, index=False)

print("✅ Cleaning and normalization complete!")
>>>>>>> b4e42a073adaad8207ac0d71b71b8921f7e60850
