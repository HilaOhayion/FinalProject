import pytest
import pandas as pd

from tests.test_fixtures import setup_mock_environment
from src.data_cleanup import clean_all_participant_files

def test_clean_all_participant_files_positive(setup_mock_environment):
    """
    Positive test:
    - 'Participant_101.csv' has a 'Separator' row. 
    - After cleaning, 'Separator' row should be removed, and 
      numeric columns should be filled if there's missing data.
    """
    clean_all_participant_files()
    clean_dataset = setup_mock_environment / "clean_dataset"
    df_101 = pd.read_csv(clean_dataset / "Participant_101.csv")

    assert not df_101[(df_101["Category Right"] == "Separator")].any().any(), \
        "The 'Separator' row was not removed."

def test_clean_all_participant_files_missing_columns(setup_mock_environment, capsys):
    """
    Negative test:
    - 'Participant_202.csv' is missing certain columns. 
    - Should log a warning but not crash.
    """
    clean_all_participant_files()
    captured = capsys.readouterr()
    assert "Missing columns" in captured.out or "Warning:" in captured.out, \
        "Expected a warning regarding missing columns."
