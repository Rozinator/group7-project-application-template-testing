import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from collections import Counter
import numpy as np

from analysis.issue_resolution_time_analyzer import IssueResolutionTimeAnalyzer
from model import Issue, State


# Dummy Issue helper (avoids JSON)
class DummyIssue(Issue):
    def __init__(self, number=0, labels=None, state='open', created=None, updated=None):
        self.url = f"url/{number}"
        self.creator = "user"
        self.labels = labels or []
        self.state = State[state] if state in State.__members__ else state
        self.assignees = []
        self.title = ""
        self.text = ""
        self.number = number
        self.created_date = created
        self.updated_date = updated
        self.timeline_url = None
        self.events = []


class TestIssueResolutionTimeAnalyzer(unittest.TestCase):

    def setUp(self):
        self.an = IssueResolutionTimeAnalyzer()
        patcher = patch("matplotlib.pyplot.show")
        self.addCleanup(patcher.stop)
        patcher.start()

    # ------------------------------
    # _get_labels_for_issue
    # ------------------------------

    def test_get_labels_for_issue(self):
        issue = DummyIssue(labels=["a", "b"])
        out = self.an._get_labels_for_issue(issue)
        self.assertEqual(out, {"a", "b"})

        class X: pass
        self.assertEqual(self.an._get_labels_for_issue(X()), set())

        bad = DummyIssue()
        bad.labels = "not_list"
        self.assertEqual(self.an._get_labels_for_issue(bad), set())

    # ------------------------------
    # Label frequency
    # ------------------------------

    def test_label_frequency(self):
        issues = [
            DummyIssue(labels=["bug", "ui"]),
            DummyIssue(labels=["bug"]),
            DummyIssue(labels=["docs"])
        ]
        out = self.an._calculate_label_frequency(issues)
        self.assertEqual(out["bug"], 2)
        self.assertEqual(out["ui"], 1)
        self.assertEqual(out["docs"], 1)

    # ------------------------------
    # Avg resolution time (BUG DETECTED)
    # ------------------------------

    def test_avg_resolution_time_bug_detected(self):
        now = datetime.now()
        issues = []
        for i in range(12):
            c = now - timedelta(days=10+i)
            u = c + timedelta(days=(i % 3) + 1)
            issues.append(DummyIssue(number=i, labels=["bug"], state="closed",
                                     created=c, updated=u))

        out = self.an._calculate_avg_resolution_time(issues)

        # EXPECTED to be present → will FAIL because of bug in code
        self.assertIn("bug", out)

        expected = np.mean([(issues[i].updated_date - issues[i].created_date).days
                            for i in range(12)])
        self.assertAlmostEqual(out["bug"], expected, places=5)

    # ------------------------------
    # Labels < 10 should be ignored
    # ------------------------------

    def test_avg_resolution_time_ignores_less_than_10(self):
        now = datetime.now()
        issues = []

        # 5 issues with label "small" → should NOT show up
        for i in range(5):
            c = now - timedelta(days=5+i)
            u = c + timedelta(days=2)
            issues.append(DummyIssue(labels=["small"], state="closed", created=c, updated=u))

        out = self.an._calculate_avg_resolution_time(issues)
        self.assertNotIn("small", out)

    # ------------------------------
    # Plot functions
    # ------------------------------

    def test_plot_functions_do_not_crash(self):
        label_counts = Counter({"bug": 10})
        avg = {"bug": 3.0}
        self.an.plot_label_frequency(label_counts)
        self.an.plot_resolution_time_by_label(avg)
        self.an.plot_frequency_vs_resolution_time(label_counts, avg)

    # ------------------------------
    # Empty
    # ------------------------------

    def test_empty_inputs_do_not_crash(self):
        self.an.plot_label_frequency(Counter())
        self.an.plot_resolution_time_by_label({})
        self.an.plot_frequency_vs_resolution_time(Counter(), {})


if __name__ == "__main__":
    unittest.main()
