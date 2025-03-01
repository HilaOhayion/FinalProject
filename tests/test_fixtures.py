import pytest
import os
from pathlib import Path

@pytest.fixture(scope="session")
def setup_mock_environment(tmp_path_factory, request, monkeypatch):
    """
    A single fixture that sets up:
    - A mock 'Eye-tracking Output' folder with CSVs for dataset_file_cleanup tests
    - A mock 'clean_dataset' folder with participant files for data_cleanup/data_analysis tests
    - experiment_statistics.csv and Metadata_Participants.csv for data_analysis and data_visualization
    - average_paths folder for calculate_gaze_paths
    - Potential edge/negative/boundary scenarios in one place

    The fixture uses 'session' scope so it can be reused across multiple test files
    without re-creating the data every time (optional).
    """

    # Create a base temporary directory
    base_dir = tmp_path_factory.mktemp("mock_project")

    # Create an 'Eye-tracking Output' folder for dataset_file_cleanup usage
    eye_tracking_folder = base_dir / "dataset_project/Eye-tracking Output"
    eye_tracking_folder.mkdir(parents=True)

    # Minimal positive data
    content_experiment_1 = """RecordingTime [ms],Participant,Stimulus,Category Right,Category Left,Point of Regard Right X [px],Point of Regard Right Y [px],Point of Regard Left X [px],Point of Regard Left Y [px]
0,101,StimA,Fixation,Fixation,100,200,110,210
30,101,StimA,Separator,Separator,0,0,0,0
"""
    (eye_tracking_folder / "1.csv").write_text(content_experiment_1)

    # A file with missing columns for negative test
    content_experiment_2 = """RecordingTime [ms],Participant,Stimulus
10,202,StimB
"""
    (eye_tracking_folder / "2.csv").write_text(content_experiment_2)

    # 'clean_dataset' folder for data_cleanup or as a starting point for data_analysis
    clean_dataset_folder = base_dir / "clean_dataset"
    clean_dataset_folder.mkdir()

    # Minimal CSV for participant_101
    content_participant_101 = """Participant,Experiment,Stimulus,Category Left,Category Right,Point of Regard Right X [px],Point of Regard Right Y [px],Point of Regard Left X [px],Point of Regard Left Y [px],SnappedTime,Duration,Overall Gaze Deviation
101,1,StimA,Fixation,Fixation,100,200,110,210,20,30,10
101,1,StimA,Saccade,Fixation,300,400,310,410,40,30,20
"""
    (clean_dataset_folder / "Participant_101.csv").write_text(content_participant_101)

    # Null/empty or boundary test
    (clean_dataset_folder / "Participant_999.csv").write_text("")

    # Partial example for missing columns
    content_participant_202 = """Participant,Experiment,Stimulus,Category Left,Category Right
202,2,StimB,Saccade,Fixation
"""
    (clean_dataset_folder / "Participant_202.csv").write_text(content_participant_202)

    # experiment_statistics.csv (we’ll leave it blank for now—some tests fill it in)
    stats_file = base_dir / "experiment_statistics.csv"
    stats_file.write_text("")

    # Metadata_Participants.csv for data_visualization or participant_averages
    meta_file = base_dir / "Metadata_Participants.csv"
    # Example includes one participant with partial data
    meta_file.write_text("""ParticipantID,Class,Avg_Gaze_Deviation,Saccade_Frequency
101,ASD,10,0.3
999,TD,0,0
""")

    # 'calculated_average_paths' for calculate_gaze_paths
    avg_folder = base_dir / "calculated_average_paths"
    avg_folder.mkdir()

    # Monkeypatch the load_data paths:
    from src import load_data  # or from your_package.load_data import ...
    monkeypatch.setattr(load_data, "original_dataset", str(eye_tracking_folder))
    monkeypatch.setattr(load_data, "participant_dataset", str(clean_dataset_folder))
    monkeypatch.setattr(load_data, "average_paths_folder", str(avg_folder))
    monkeypatch.setattr(load_data, "experiment_statistics_file", str(stats_file))
    monkeypatch.setattr(load_data, "metadata_participants", str(meta_file))

    # Return the base_dir or any relevant paths if the test files need them.
    return base_dir
