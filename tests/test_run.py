import unittest
import sys
import importlib
from types import SimpleNamespace
from unittest.mock import patch


class TestRunModule(unittest.TestCase):

    def _import_run_with_feature(self, feature: int):
        """
        Import run.py with a mocked --feature value.
        This exercises runFeatures() but keeps analyzers mocked
        (except TrendAnalyzer; it's never called for these features).
        """
        if "run" in sys.modules:
            del sys.modules["run"]

        with patch("argparse.ArgumentParser.parse_args") as mock_parse, \
             patch("data_loader.DataLoader.get_issues", return_value=[]) as mock_get_issues, \
             patch("example_analysis.ExampleAnalysis.run") as mock_example_run, \
             patch("analysis.userAnalysis_Feature.CommentAnalysis.run") as mock_comment_run, \
             patch("analysis.issue_resolution_time_analyzer.IssueResolutionTimeAnalyzer.run") as mock_issue_res_run, \
             patch("analysis.issues_category_trend_analyzer.IssuesCategoryTrendAnalyzer.run") as mock_cat_run, \
             patch("builtins.print") as mock_print:

            mock_parse.return_value = SimpleNamespace(
                feature=feature,
                user=None,
                label=None,
            )

            run_module = importlib.import_module("run")

        return {
            "run_module": run_module,
            "mock_get_issues": mock_get_issues,
            "mock_example_run": mock_example_run,
            "mock_comment_run": mock_comment_run,
            "mock_issue_res_run": mock_issue_res_run,
            "mock_cat_run": mock_cat_run,
            "mock_print": mock_print,
        }

    def test_feature_0_calls_example_analysis(self):
        mocks = self._import_run_with_feature(0)
        mocks["mock_get_issues"].assert_called_once()
        mocks["mock_example_run"].assert_called_once()
        mocks["mock_comment_run"].assert_not_called()
        mocks["mock_issue_res_run"].assert_not_called()
        mocks["mock_cat_run"].assert_not_called()

    def test_feature_2_calls_comment_analysis(self):
        mocks = self._import_run_with_feature(2)
        mocks["mock_get_issues"].assert_called_once()
        mocks["mock_comment_run"].assert_called_once()
        mocks["mock_example_run"].assert_not_called()
        mocks["mock_issue_res_run"].assert_not_called()
        mocks["mock_cat_run"].assert_not_called()

    def test_feature_3_calls_issue_resolution_analysis(self):
        mocks = self._import_run_with_feature(3)
        mocks["mock_get_issues"].assert_called_once()
        mocks["mock_issue_res_run"].assert_called_once()
        mocks["mock_example_run"].assert_not_called()
        mocks["mock_comment_run"].assert_not_called()
        mocks["mock_cat_run"].assert_not_called()

    def test_feature_4_calls_category_trend_analysis(self):
        mocks = self._import_run_with_feature(4)
        mocks["mock_get_issues"].assert_called_once()
        mocks["mock_cat_run"].assert_called_once()
        mocks["mock_example_run"].assert_not_called()
        mocks["mock_comment_run"].assert_not_called()
        mocks["mock_issue_res_run"].assert_not_called()

    def test_invalid_feature_prints_message_and_calls_nothing(self):
        mocks = self._import_run_with_feature(99)
        mocks["mock_get_issues"].assert_called_once()
        mocks["mock_example_run"].assert_not_called()
        mocks["mock_comment_run"].assert_not_called()
        mocks["mock_issue_res_run"].assert_not_called()
        mocks["mock_cat_run"].assert_not_called()
        # else branch message
        mocks["mock_print"].assert_called()

    def test_feature_1_runs_real_trend_analyzer(self):
        """
        Hit the REAL TrendAnalyzer.run via run.py.
        Only mock:
          - argparse (to provide --feature=1)
          - matplotlib.pyplot.show (so no GUI)
        DataLoader and TrendAnalyzer are NOT mocked here.
        """
        if "run" in sys.modules:
            del sys.modules["run"]

        with patch("argparse.ArgumentParser.parse_args") as mock_parse, \
             patch("matplotlib.pyplot.show") as mock_show:

            mock_parse.return_value = SimpleNamespace(
                feature=1,
                user=None,
                label=None,
            )

            import run  # noqa: F401

        mock_show.assert_called_once()


    #add
    def test_import_run_raises_systemexit(self):
        if "run" in sys.modules:
            del sys.modules["run"]

        with self.assertRaises(SystemExit):
            importlib.import_module("run")
    
if __name__ == "__main__":
    unittest.main()
