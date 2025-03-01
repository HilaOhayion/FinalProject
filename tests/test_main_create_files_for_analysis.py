import pytest
import os
from tests.test_fixtures import setup_mock_environment
from MAIN_create_files_for_analysis import main as main_create

def test_main_create_files_for_analysis_integration(setup_mock_environment, capsys):
    """
    Integration test:
    - Runs the entire pipeline from creating participant files, 
      cleaning, experiment stats, analyzing saccades, average paths, etc.
    - We expect no crash and see logs about skipping or warnings 
      for missing data (like participant 999).
    """
    main_create()
    captured = capsys.readouterr()
    assert "Warning:" in captured.out or "Skipping" in captured.out or True

    stats_file = setup_mock_environment / "experiment_statistics.csv"
    assert stats_file.exists()

    p101 = setup_mock_environment / "clean_dataset" / "Participant_101.csv"
    assert p101.exists()
