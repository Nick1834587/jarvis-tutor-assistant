import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import storage, tasks


class TaskTests(unittest.TestCase):
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

    def test_add_task_saves_it(self):
        number = tasks.add_task("Prepare a weekly report")

        self.assertEqual(number, 1)
        self.assertEqual(
            tasks.list_tasks(),
            [{"text": "Prepare a weekly report", "done": False}],
        )

    def test_mark_task_done_saves_completion(self):
        tasks.add_task("Prepare a weekly report")
        tasks.mark_task_done(1)

        self.assertTrue(tasks.list_tasks()[0]["done"])

    def test_unknown_task_number_is_rejected(self):
        with self.assertRaises(IndexError):
            tasks.mark_task_done(1)


if __name__ == "__main__":
    unittest.main()