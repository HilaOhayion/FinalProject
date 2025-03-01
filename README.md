
# Eye-Tracking Autism Analysis

This project analyzes eye-tracking data to explore potential differences in gaze and saccade patterns that may be related to Autism Spectrum Disorder (ASD). It includes scripts for data cleanup, statistics, and plotting results.

----------

## Contents

1.  [Overview](https://www.madeintext.com/text-to-markdown/#overview)
2.  [Code Pipeline](https://www.madeintext.com/text-to-markdown/#repository-layout)
3.  [Running the Project](https://www.madeintext.com/text-to-markdown/#running-the-project)
    -   [Option A: Run MAIN_analyze_data only](https://www.madeintext.com/text-to-markdown/#option-a-run-main_analyze_data-only)
    -   [Option B: Run MAIN_create_files_for_analysis + MAIN_analyze_data](https://www.madeintext.com/text-to-markdown/#option-b-run-main_create_files_for_analysis--main_analyze_data)
4.  [Dependencies](https://www.madeintext.com/text-to-markdown/#dependencies)
5.  [Additional Notes](https://www.madeintext.com/text-to-markdown/#additional-notes)

----------

## Overview

This project takes the dataset Eye Tracking Autism (https://www.kaggle.com/datasets/imtkaggleteam/eye-tracking-autism) and analyzes the data there to try and see if they're differences between the gazes of autistic and neurotypical people.

The project:

-   **Clean** raw eye-tracking data into a standardized format.
-   **Generate** participant-wise CSV files and computed average gaze paths.
-   **Calculate** key metrics such as gaze deviations, saccade frequencies, and seccade length.
-   **Perform** statistical analysis (Welch’s t-tests) on those metrics.
-   **Visualize** results with boxplots and KDE plots to highlight differences between ASD and NT participants.

Because the original dataset is large, only partial result files are provided in the repository. You can still run all analysis code on the included partial files, or download the entire dataset from Kaggle to generate everything from scratch.

----------

## Code Pipeline

-   **`MAIN_create_files_for_analysis.py`**  
    Runs the pipeline for creating the analysis files from the raw datafiles:
    
    1.  Create participant files from the experiment files
    2.  Clean them and normalizes the recording time per experiment
    3.  Calculates the duration of each recording and normalize recording time per stimulus
    4.  Build experiment_statistics.csv
    5.  Analyze saccades
    6.  Generate average gaze paths for each stimulus
    7.  Calculate gaze deviations for each participant
    8.  Calculate final metrics in experiment_statistics
    9.  Update participant-level averages in `Metadata_Participants.csv`
-   **`MAIN_analyze_data.py`**  
    Loads the resulting data from **`MAIN_create_files_for_analysis.py`**, runs statistical comparisons, and plots results.
    

----------

## Running the Project

You can run the code in **two** ways:

### Option A: Run `MAIN_analyze_data` Only

**Goal**: Quickly generate plots and stats with the partially processed files included here.

1.  **Clone** or download this repository.
2.  **Ensure** you have the dependencies installed (see [Dependencies](https://www.madeintext.com/text-to-markdown/#dependencies)).
3.  **Open** a terminal and navigate to the project root.
4.  **Run**: `python MAIN_analyze_data.py  
    `  
    This will:
    -   Load the computed data from `clean_dataset` & `calculated_average_paths`.
    -   Generate statistical comparisons (t-tests).
    -   Show the resulting plots.

**Note**: Since the included CSV files are already cleaned and processed, you do not need to run `MAIN_create_files_for_analysis`.

----------

### Option B: Run `MAIN_create_files_for_analysis` + `MAIN_analyze_data`

**Goal**: Reproduce the entire pipeline from scratch with the complete dataset.

1.  **Obtain the full dataset** from [Kaggle: Eye-Tracking Autism Dataset](https://www.kaggle.com/datasets/imtkaggleteam/eye-tracking-autism) (the original large files were too big to host on GitHub).
2.  **Extract** the Kaggle dataset into the folder: "dataset_project/Eye-tracking Output" so that it contains all raw CSVs named like `1.csv`, `2.csv`, etc.
3.  **Ensure** you have the file `Metadata_Participants.csv` in the **root** folder (the same folder as `MAIN_create_files_for_analysis.py`).
4.  **Install dependencies** (see below).
5.  **Run**: `python MAIN_create_files_for_analysis.py`  
      
    This will:  
    -   Run the pipeline described above.
    -   Create the files necessary for `MAIN_analyze_data.py`

6. **Finally**, run: `MAIN_analyze_data.py`to produce the final stats and plots.

----------

## Dependencies

The core libraries are:

-   **pandas**
-   **numpy**
-   **matplotlib** + **seaborn**
-   **scipy**

----------

## Additional Notes

1.  **Why `MAIN_create_files_for_analysis` won’t run by default**:
    
    -   The original large dataset is **not** included due to size constraints. Instead, partial CSV files are in the repo so you can still run `MAIN_analyze_data`.
2.  **Where to get the full dataset**:
    
    -   [Kaggle Eye-tracking Autism](https://www.kaggle.com/datasets/imtkaggleteam/eye-tracking-autism).
    -   Extract to `dataset_project/Eye-tracking Output` for the full pipeline.
3.  **Recommended Workflow**:
    
    -   If you want to replicate the entire data-cleaning pipeline, place the Kaggle dataset in the correct folder, ensure `Metadata_Participants.csv` is in the root, then run **`MAIN_create_files_for_analysis.py`** followed by **`MAIN_analyze_data.py`**.
4.  **Results**:
    
    -   The final graphs and plots are all included in the "output" folder.
