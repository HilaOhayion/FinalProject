import pytest
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import pandas as pd

from tests.test_fixtures import setup_mock_environment
from src.data_visualization import (
    load_and_split_data_by_class,
    compare_all_metrics,
    plot_individual_boxplots,
    plot_significant_subplots,
    plot_distribution_kde_by_group
)

def test_load_and_split_data_by_class_positive(setup_mock_environment):
    """
    Positive test: 
    - The fixture creates a minimal Metadata_Participants.csv with 
      ParticipantID=101 (ASD) + 999 (TD).
    """
    df, asd, td = load_and_split_data_by_class()
    assert len(df) > 0, "Metadata is empty."
    assert len(asd) == 1, "Expected exactly one ASD participant (101)."
    assert len(td) == 1, "Expected exactly one TD participant (999)."

def test_compare_all_metrics_edge(setup_mock_environment):
    """
    Edge test: 
    - Possibly high or zero metrics in metadata. 
    - We just confirm no crash, and the result dict is well-formed.
    """
    _, asd, td = load_and_split_data_by_class()
    results = compare_all_metrics(asd, td)
    assert "Avg_Gaze_Deviation" in results
    assert "p_value" in results["Avg_Gaze_Deviation"]

def test_plot_individual_boxplots(setup_mock_environment):
    """
    Positive/Smoke test:
    - Ensure no crash when plotting.
    """
    _, asd, td = load_and_split_data_by_class()
    results = compare_all_metrics(asd, td)
    plot_individual_boxplots(asd, td, results)
    plt.close("all")

def test_plot_significant_subplots_null(setup_mock_environment, capsys):
    """
    Null test:
    - Force all p_values > 0.05, so it prints a 'No metrics are significant' message.
    """
    _, asd, td = load_and_split_data_by_class()
    results = compare_all_metrics(asd, td)
    # Overwrite p_values
    for metric in results:
        results[metric]["p_value"] = 0.99

    plot_significant_subplots(asd, td, results)
    captured = capsys.readouterr()
    assert "No metrics are significant at p<0.05." in captured.out

def test_plot_distribution_kde_by_group_performance(setup_mock_environment):
    """
    Performance-labeled test (just a placeholder).
    """
    df, _, _ = load_and_split_data_by_class()
    plot_distribution_kde_by_group(df, "Avg_Gaze_Deviation")
    plt.close("all")
    assert True
