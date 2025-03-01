import pytest
import os
import pandas as pd

from tests.test_fixtures import setup_mock_environment
from src.dataset_file_cleanup import create_participant_files

def test_create_participant_files_positive(setup_mock_environment):
    """
    Positive test:
    - The fixture sets up 'Eye-tracking Output' with 1.csv, 2.csv.
    - We run create_participant_files() to see if it properly creates 
      'Participant_{X}.csv' in clean_dataset.
    """
    create_participant_files()
    clean_folder = setup_mock_environment / "clean_dataset"

    part_101 = clean_folder / "Participant_101.csv"
    assert part_101.exists(), "Participant_101.csv was not created."

def test_create_participant_files_missing_cols(setup_mock_environment, capsys):
    """
    Negative test:
    - 2.csv is missing many columns. Should skip or warn but not crash.
    """
    create_participant_files()
    captured = capsys.readouterr()
    assert "Missing columns" in captured.out or "Skipping" in captured.out
