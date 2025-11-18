import os
import tempfile
import unittest
from unittest.mock import patch

# Ensure Matplotlib can write cache during tests
os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp())

from analysis.userAnalysis_Feature import CommentAnalysis
from model import Issue


class TestCommentAnalysis(unittest.TestCase):
    @patch("analysis.userAnalysis_Feature.plt.show")
    @patch("analysis.userAnalysis_Feature.DataLoader.get_issues")
    def test_run_draws_pie_for_commented_events(self, mock_get_issues, mock_show):
        issues = [
            Issue(
                {
                    "state": "open",
                    "events": [
                        {"event_type": "commented", "author": "alice"},
                        {"event_type": "commented", "author": "bob"},
                        {"event_type": "commented", "author": "alice"},
                    ],
                }
            )
        ]
        mock_get_issues.return_value = issues

        with patch("analysis.userAnalysis_Feature.plt.pie", return_value=([], [], [])) as mock_pie:
            CommentAnalysis().run()

        mock_get_issues.assert_called_once()
        mock_show.assert_called_once()
        # alice=2, bob=1, Others=0 -> values passed to pie should follow that order after sorting
        pie_args, _ = mock_pie.call_args
        self.assertEqual([2, 1, 0], list(pie_args[0]))

    @patch("analysis.userAnalysis_Feature.DataLoader.get_issues", return_value=[Issue({"state": "open", "events": []})])
    def test_run_without_comments_raises_due_to_zero_total(self, mock_get_issues):
        # No commented events means total_values becomes zero; current implementation currently crashes.
        # This test intentionally allows the ZeroDivisionError to surface to document the bug.
        CommentAnalysis().run()

    @patch("analysis.userAnalysis_Feature.plt.show")
    @patch("analysis.userAnalysis_Feature.plt.annotate")
    @patch("analysis.userAnalysis_Feature.DataLoader.get_issues")
    def test_run_handles_small_slices_with_annotations(self, mock_get_issues, mock_annotate, mock_show):
        # Create counts: big=20, small1=1, small2=1 so small slices fall below 5%
        events = [{"event_type": "commented", "author": "big"} for _ in range(20)]
        events += [
            {"event_type": "commented", "author": "small1"},
            {"event_type": "commented", "author": "small2"},
        ]
        mock_get_issues.return_value = [Issue({"state": "open", "events": events})]

        autotexts = []

        def fake_pie(values, *args, **kwargs):
            from unittest.mock import MagicMock

            for _ in values:
                m = MagicMock()
                m.get_position.return_value = (1.0, 1.0)
                m.get_text.return_value = "1.0%"
                autotexts.append(m)
            return ([], [], autotexts)

        with patch("analysis.userAnalysis_Feature.plt.pie", side_effect=fake_pie):
            CommentAnalysis().run()

        # Small slices should have set_visible(False) called during annotation
        # Index 0 corresponds to the largest slice; the rest are small
        mock_get_issues.assert_called_once()
        mock_show.assert_called_once()
        self.assertGreaterEqual(len(autotexts), 3)
        self.assertTrue(autotexts[1].set_visible.called)

if __name__ == "__main__":
    unittest.main()
