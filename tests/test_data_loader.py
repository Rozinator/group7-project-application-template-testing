import json
import os
import unittest

import data_loader
from model import Event, Issue


class TestDataLoader(unittest.TestCase):
    def setUp(self):
        self.config_path = os.environ.get("CONFIG_PATH")
        self.original_data_path = os.environ.get("ENPM611_PROJECT_DATA_PATH")
        data_loader._ISSUES = None

    def tearDown(self):
        if self.original_data_path is None:
            os.environ.pop("ENPM611_PROJECT_DATA_PATH", None)
        else:
            os.environ["ENPM611_PROJECT_DATA_PATH"] = self.original_data_path
        data_loader._ISSUES = None

    def test_init_reads_path_from_config(self):
        self.config_path = os.path.join("tests", "test_config.json")
        with open(self.config_path, 'r') as conf_in:
            conf = json.loads(conf_in.read())
        
        os.environ["ENPM611_PROJECT_DATA_PATH"] = conf.get("ENPM611_PROJECT_DATA_PATH")
        loader = data_loader.DataLoader()
        self.assertEqual(conf.get("ENPM611_PROJECT_DATA_PATH"), loader.data_path)
    
    def test_init_from_none_path(self):
        os.environ.pop("ENPM611_PROJECT_DATA_PATH", None)
        with open("config.json", "r") as conf_in:
            expected_path = json.loads(conf_in.read()).get("ENPM611_PROJECT_DATA_PATH")
        loader = data_loader.DataLoader()
        self.assertEqual(expected_path, loader.data_path)

    def test_get_issues_loads_expected_issue_objects(self):
        self.config_path = os.path.join("tests","test_config.json")
        with open(self.config_path, 'r') as conf_in:
            conf = json.loads(conf_in.read())
        
        os.environ["ENPM611_PROJECT_DATA_PATH"] = conf.get("ENPM611_PROJECT_DATA_PATH")

        loader = data_loader.DataLoader()
        issues = loader.get_issues()

        self.assertEqual(1, len(issues))
        issue = issues[0]
        self.assertIsInstance(issue, Issue)
        self.assertEqual("alice", issue.creator)
        self.assertEqual(["bug"], issue.labels)
        self.assertEqual(1, issue.number)
        self.assertEqual(1, len(issue.events))
        self.assertIsInstance(issue.events[0], Event)
        self.assertEqual("commented", issue.events[0].event_type)

    def test_get_issues_from_nonexistent_path(self):
        os.environ["ENPM611_PROJECT_DATA_PATH"] = "random.json"
        loader = data_loader.DataLoader()

        with self.assertRaises(FileNotFoundError):
            loader.get_issues()

if __name__ == "__main__":
    unittest.main()
