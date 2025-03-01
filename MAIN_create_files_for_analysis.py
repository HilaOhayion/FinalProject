from src.dataset_file_cleanup import create_participant_files
from src.data_cleanup import clean_all_participant_files
from src.data_analysis import create_experiment_statistics_file, analyze_saccades
from src.calculate_gaze_paths import create_average_paths_files, calculate_gaze_deviation
from src.data_analysis import calculate_experiment_deviation, calculate_participant_averages

def main():
    create_participant_files()
    clean_all_participant_files()
    create_experiment_statistics_file()
    analyze_saccades()
    create_average_paths_files()
    calculate_gaze_deviation()
    calculate_experiment_deviation()
    calculate_participant_averages()

if __name__ == "__main__":
    main()
