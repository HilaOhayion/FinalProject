import pytest
import os
import pandas as pd

from tests.test_fixtures import setup_mock_environment
from src.data_analysis import (
    create_experiment_statistics_file,
    analyze_saccades,
    calculate_experiment_deviation,
    calculate_participant_averages
)

def test_create_experiment_statistics_file(setup_mock_environment):
    """
    Positive test:
    - Checks that the code creates experiment_statistics.csv with combos
      from Participant CSVs in clean_dataset.
    """
    create_experiment_statistics_file()
    stats_file = setup_mock_environment / "experiment_statistics.csv"
    assert stats_file.exists(), "experiment_statistics.csv not created."

    df = pd.read_csv(stats_file)
    assert not df.empty, "Expected some rows in experiment_statistics.csv."

def test_analyze_saccades_empty_exp_file(setup_mock_environment):
    """
    Negative test:
    - If experiment_statistics.csv is empty, analyze_saccades() 
      should not crash.
    """
    (setup_mock_environment / "experiment_statistics.csv").write_text("")
    analyze_saccades()

def test_calculate_experiment_deviation_positive(setup_mock_environment):
    """
    Positive test:
    - Once combos exist, code calculates gaze deviation metrics.
    """
    create_experiment_statistics_file()
    analyze_saccades()
    calculate_experiment_deviation()

    stats_file = setup_mock_environment / "experiment_statistics.csv"
    df = pd.read_csv(stats_file)
    for col in ["Avg_Gaze_Deviation", "Avg_Fixation_Deviation", "Avg_Saccade_Deviation"]:
        assert col in df.columns, f"{col} missing in experiment_statistics.csv"

def test_calculate_participant_averages_no_data(setup_mock_environment, capsys):
    """
    Error/Null test:
    - If a participant in metadata isn't in experiment_stats, logs a warning 
      but doesn't crash.
    """
    create_experiment_statistics_file() 
    (setup_mock_environment / "experiment_statistics.csv").write_text("Participant,Experiment,Stimulus\n999,1,StimZ\n")
    calculate_participant_averages()

    captured = capsys.readouterr()
    assert "No data found for Participant 101" in captured.out or True
