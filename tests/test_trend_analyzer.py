import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

# Ensure Matplotlib writes cache to a writable temp directory during tests
os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp())

from analysis.trend_analyzer import TrendAnalyzer
from model import Issue


class TestTrendAnalyzer(unittest.TestCase):
    def test_run_returns_early_when_no_issue_dates(self):
        analyzer = TrendAnalyzer()
        issues = [Issue({"state": "open"}), Issue({"state": "closed"})]

        with patch("analysis.trend_analyzer.plt.show") as mock_show:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                analyzer.run(issues, events=[])

            output = stdout.getvalue()

        self.assertIn("No valid issue creation dates found in the dataset!", output)
        mock_show.assert_not_called()

    def test_run_plots_when_issue_dates_present(self):
        analyzer = TrendAnalyzer()
        issues = [
            Issue({"state": "open", "created_date": "2023-01-15T00:00:00Z"}),
            Issue({"state": "open", "created_date": "2023-01-20T00:00:00Z"}),
            Issue({"state": "open", "created_date": "2023-02-05T00:00:00Z"}),
        ]

        with patch("analysis.trend_analyzer.plt.show") as mock_show:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                analyzer.run(issues, events=[])

        mock_show.assert_called_once()
        self.assertIn("Running Trend Analysis", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
