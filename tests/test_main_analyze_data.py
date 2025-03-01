import pytest
import matplotlib
matplotlib.use("Agg")
from unittest.mock import patch

from tests.test_fixtures import setup_mock_environment
from MAIN_analyze_data import main as main_analyze

@patch("matplotlib.pyplot.show")
def test_main_analyze_data_positive(mock_show, setup_mock_environment):
    """
    Positive test:
    - We have minimal metadata with one ASD + one TD participant from fixture.
    - main_analyze_data plots boxplots + subplots. Mock out plt.show() to avoid UI.
    """
    main_analyze()
    assert mock_show.called, "Expected at least one plot call in main_analyze_data."
