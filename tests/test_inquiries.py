import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from src import inquiries, storage


class InquiryTests(unittest.TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        patcher = patch.object(
            storage,
            "DATA_DIR",
            Path(temporary_directory.name),
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_add_inquiry_saves_it(self):
        number = inquiries.add_inquiry(
            "Alex",
            "Needs a tutoring estimate",
        )

        self.assertEqual(number, 1)
        saved = inquiries.list_inquiries()[0]
        self.assertEqual(saved["customer"], "Alex")
        self.assertEqual(saved["status"], "new")
        self.assertIsNone(saved["follow_up"])

    def test_followup_is_shown_as_overdue(self):
        inquiries.add_inquiry("Alex", "Needs an estimate")
        inquiries.set_follow_up(1, "2026-11-13")

        followups = inquiries.get_open_followups(today=date(2026, 11, 14))

        self.assertEqual(followups[0][0], 1)
        self.assertEqual(followups[0][2], "OVERDUE — due 2026-11-13")

    def test_replied_inquiry_is_removed_from_open_followups(self):
        inquiries.add_inquiry("Alex", "Needs an estimate")
        inquiries.mark_replied(1)

        self.assertEqual(inquiries.get_open_followups(), [])

    def test_invalid_followup_date_is_rejected(self):
        inquiries.add_inquiry("Alex", "Needs an estimate")

        with self.assertRaises(ValueError):
            inquiries.set_follow_up(1, "tomorrow")


if __name__ == "__main__":
    unittest.main()