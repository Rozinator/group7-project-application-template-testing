import unittest
from model import Issue, Event, State


class TestModelIssueAndEvent(unittest.TestCase):

    def test_issue_from_json_parses_valid_fields(self):
        jobj = {
            "url": "http://example.com/issue/1",
            "creator": "alice",
            "labels": ["bug", "feature"],
            "state": "open",
            "assignees": ["bob"],
            "title": "Sample issue",
            "text": "Something is broken",
            "number": "42",
            "created_date": "2024-01-01T12:00:00Z",
            "updated_date": "2024-01-02T13:00:00Z",
            "timeline_url": "http://example.com/issue/1/timeline",
            "events": [
                {
                    "event_type": "labeled",
                    "author": "alice",
                    "event_date": "2024-01-01T12:30:00Z",
                    "label": "bug",
                    "comment": "initial label",
                }
            ],
        }

        issue = Issue(jobj)

        self.assertEqual(issue.url, jobj["url"])
        self.assertEqual(issue.creator, "alice")
        self.assertEqual(issue.labels, ["bug", "feature"])
        self.assertEqual(issue.state, State.open)
        self.assertEqual(issue.assignees, ["bob"])
        self.assertEqual(issue.title, "Sample issue")
        self.assertEqual(issue.text, "Something is broken")
        self.assertEqual(issue.number, 42)
        self.assertIsNotNone(issue.created_date)
        self.assertIsNotNone(issue.updated_date)
        self.assertEqual(issue.timeline_url, jobj["timeline_url"])
        self.assertEqual(len(issue.events), 1)

        event = issue.events[0]
        self.assertEqual(event.event_type, "labeled")
        self.assertEqual(event.author, "alice")
        self.assertIsNotNone(event.event_date)
        self.assertEqual(event.label, "bug")
        self.assertEqual(event.comment, "initial label")

    def test_issue_from_json_handles_invalid_number_and_dates(self):
        jobj = {
            "state": "closed",
            "number": "not-a-number",
            "created_date": "not-a-date",
            "updated_date": None,
            "events": [{"event_date": "still-not-a-date"}],
        }

        issue = Issue(jobj)

        # number should stay at default -1
        self.assertEqual(issue.number, -1)
        # invalid dates should leave created/updated as None
        self.assertIsNone(issue.created_date)
        self.assertIsNone(issue.updated_date)

        # event with invalid date should not crash and event_date should be None
        self.assertEqual(len(issue.events), 1)
        self.assertIsNone(issue.events[0].event_date)

    def test_state_enum_values(self):
        self.assertEqual(State.open.value, "open")
        self.assertEqual(State.closed.value, "closed")


if __name__ == "__main__":
    unittest.main()


