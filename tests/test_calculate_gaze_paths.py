import pytest
import os
import pandas as pd
from src.calculate_gaze_paths import create_average_paths_files, calculate_gaze_deviation

def test_create_average_paths_files_positive(setup_mock_environment):
    """
    Positive Test Case:
    Uses the pre-built environment from test_fixtures.py. 
    We expect to find 'Participant_101.csv' referencing StimA.
    """
    create_average_paths_files()
    avg_folder = setup_mock_environment / "calculated_average_paths"
    output_path = avg_folder / "AveragePath_StimA.csv"
    assert output_path.exists(), "AveragePath_StimA.csv was not created."

    df = pd.read_csv(output_path)
    assert "Avg Right X" in df.columns, "Missing 'Avg Right X' in the average path file."


def test_calculate_gaze_deviation_negative(setup_mock_environment, capsys):
    """
    Negative Test:
    If there's a participant with a Stimulus that has no matching average path, 
    code should warn but not crash.
    """
    calculate_gaze_deviation()
    captured = capsys.readouterr()
    assert "Warning: Average path file for stimulus" in captured.out
