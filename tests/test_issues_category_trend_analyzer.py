import unittest
from collections import Counter
from datetime import datetime
from unittest.mock import patch

from analysis.issues_category_trend_analyzer import IssuesCategoryTrendAnalyzer
from model import Issue


def make_issue(created, labels):
    """Helper to quickly build Issue objects."""
    jobj = {
        "state": "open",
        "labels": labels,
        "created_date": created,
        "number": "1",
        "title": "dummy",
        "text": "dummy",
        "creator": "tester",
        "assignees": [],
        "timeline_url": "http://example.com",
        "events": [],
        "url": "http://example.com/1",
    }
    return Issue(jobj)


class TestIssuesCategoryTrendAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = IssuesCategoryTrendAnalyzer()

    def test_calculate_label_frequency_counts_labels(self):
        issues = [
            make_issue("2024-01-01T00:00:00Z", ["bug", "feature"]),
            make_issue("2024-02-01T00:00:00Z", ["bug"]),
            make_issue("2024-03-01T00:00:00Z", ["docs", "bug"]),
        ]
        counts = self.analyzer._calculate_label_frequency(issues)

        self.assertIsInstance(counts, Counter)
        self.assertEqual(counts["bug"], 3)
        self.assertEqual(counts["feature"], 1)
        self.assertEqual(counts["docs"], 1)

    @patch("matplotlib.pyplot.show")
    def test_analyze_top_label_trends_runs_without_error(self, mock_show):
        issues = [
            make_issue("2024-01-01T00:00:00Z", ["bug", "feature"]),
            make_issue("2024-04-01T00:00:00Z", ["bug"]),
            make_issue("2024-07-01T00:00:00Z", ["docs"]),
            Issue(),  
        ]

        self.analyzer.analyze_top_label_trends(issues, top_n=2)

        # Plot should have been requested
        mock_show.assert_called_once()

    @patch("matplotlib.pyplot.show")
    def test_run_uses_default_top_n_and_calls_trend_analysis(self, mock_show):
        issues = [
            make_issue("2024-01-01T00:00:00Z", ["bug"]),
            make_issue("2024-02-01T00:00:00Z", ["feature"]),
        ]

        # Just make sure .run delegates correctly
        self.analyzer.run(issues)

        mock_show.assert_called_once()
        
        
    #add
    def test_no_labels_crashes(self):
        analyzer = IssuesCategoryTrendAnalyzer()

        issues = [
            Issue({"state": "open", "created_date": "2024-01-01T00:00:00Z", "labels": []}),
            Issue({"state": "open", "created_date": "2024-01-02T00:00:00Z", "labels": []}),
        ]

        with self.assertRaises(KeyError):
            analyzer.analyze_top_label_trends(issues, top_n=3)


if __name__ == "__main__":
    unittest.main()
