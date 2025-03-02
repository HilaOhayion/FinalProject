import pandas as pd
import glob
from src.load_data import *

def check_for_missing_columns(df,file_name):
    """
    Checks for the presence of required eye-tracking columns 
    (such as RecordingTime, Participant, etc.). Prints a warning 
    if any are missing.

    Parameters:
      df (pd.DataFrame): The DataFrame to check.
      file_name (str): The CSV file's name or path (used in the warning message).

    Returns:
      pd.DataFrame or None: 
        - The original DataFrame if columns are present.
        - None if required columns are missing.
    """
    # Standardize column names (removes extra spaces)
    df.columns = df.columns.str.strip()

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
    Removes 'Separator' rows, replaces NaN with 0, 
    and confirms columns are valid.

    Steps:
      1. check_for_missing_columns() is called to ensure required columns exist.
      2. Rows where both Category Right and Category Left are 'Separator' are removed.
      3. All NaN/missing values are filled with 0.

    Parameters:
      df (pd.DataFrame): The DataFrame to clean.
      file_name (str): The CSV file's name or path (used in warnings).

    Returns:
      pd.DataFrame: The cleaned DataFrame.
                    If columns are missing, a warning is printed and 
                    the original DataFrame is still returned (minus the 
                    separator rows).
    """

    check_for_missing_columns(df,file_name)

    # Remove rows where both categories are 'Separator'
    df = df[~((df["Category Right"] == "Separator") & (df["Category Left"] == "Separator"))].copy()

    # Replace NaN or missing values with 0
    df = df.fillna(0)

    return df

def normalize_recording_time(df):
    """
    Resets 'RecordingTime [ms]' to start from 0 for each (Participant, Experiment) combo.

    Parameters:
      df (pd.DataFrame): The cleaned DataFrame (with expected columns).

    Returns:
      pd.DataFrame: The same DataFrame with a modified 'RecordingTime [ms]' column.
    """
    # Ensure correct dtype
    df["RecordingTime [ms]"] = df["RecordingTime [ms]"].astype(float)

    # Normalize time per experiment
    df.loc[:, "RecordingTime [ms]"] = df.groupby(["Participant", "Experiment"])["RecordingTime [ms]"].transform(lambda x: x - x.min())

    return df

def normalize_recording_time_per_stimulus(df):
    """
    Creates 'RecordingTime Stimulus [ms]', 
    which starts from 0 for each participant-experiment-stimulus.

    Parameters:
      df (pd.DataFrame): The DataFrame with a normalized 'RecordingTime [ms]'.

    Returns:
      pd.DataFrame: The same DataFrame with an additional 
                    'RecordingTime Stimulus [ms]' column.
    """    
    df["RecordingTime Stimulus [ms]"] = df.groupby(["Participant", "Experiment", "Stimulus"])["RecordingTime [ms]"].transform(lambda x: x - x.min())

    return df

def calculate_duration(df):
    """
    Adds a 'Duration' column to indicate the time difference 
    between consecutive rows within each experiment.

    Parameters:
      df (pd.DataFrame): The DataFrame, expected to have 'RecordingTime [ms]' 
                         and 'Experiment'.

    Returns:
      pd.DataFrame: Updated with a 'Duration' column.
    """
    df["Duration"] = 0.0  # Initialize column
    df["Duration"] = df["Duration"].astype(float)  # Ensure correct dtype

    for exp, data in df.groupby("Experiment"):
        df.loc[data.index[:-1], "Duration"] = data["RecordingTime [ms]"].diff().shift(-1)

    return df

def calculate_snapped_time(df):
    """
    Creates a 'SnappedTime' column, rounding each row's 
    'RecordingTime Stimulus [ms]' to the closest multiple of 20 ms.

    Parameters:
      df (pd.DataFrame): The DataFrame with 'RecordingTime Stimulus [ms]'.

    Returns:
      pd.DataFrame: Same DataFrame, now containing 'SnappedTime'.
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
    Cleans and and extracts relevent data from the raw eye-tracking dataset.

    It creates or changes the following columns:
        "RecordingTime [ms]" - Now the recording time starts at 0 for each experiment
        "RecordingTime Stimulus [ms]" - Creates a column where the recording time starts 
        at 0 per each stimulus to allow for comparing stimulus
        "Duration" - Creates a column that counts how much time passed between one recording (row) 
        and the next
        "SnappedTime" - Creates a column which takes the recording time per stimulus and "snaps" it
        to the closest 20 increment integer (i.e. 20, 40, 80, etc.). This allows comparing between 
        different participants and stimulus.  
    
    Parameters:
      df (pd.DataFrame): The raw DataFrame for a single participant's data.
      file_name (str): The CSV filename (used for warnings).

    Returns:
      pd.DataFrame: The fully cleaned DataFrame (or None if missing columns).
    """

    clean_data(df, file_name)
    normalize_recording_time(df)
    normalize_recording_time_per_stimulus(df)
    calculate_duration(df)
    calculate_snapped_time(df)
    
    return df

def clean_all_participant_files():
    """
    Iterates over every CSV in 'participant_dataset' and applies 
    clean_and_extract_eyetracking_data() to each.

    Notes:
      - If any file is missing required columns, a warning is printed, 
        but the script continues processing other files.
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