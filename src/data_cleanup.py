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
