import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import memory, storage


class MemoryTests(unittest.TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        patcher = patch.object(storage, "DATA_DIR", Path(temporary_directory.name))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_add_memory_persists_and_avoids_duplicates(self):
        number, is_new = memory.add_memory("that I prefer short explanations")

        self.assertEqual(number, 1)
        self.assertTrue(is_new)
        duplicate_number, duplicate_is_new = memory.add_memory(
            "I prefer short explanations"
        )

        self.assertEqual(duplicate_number, 1)
        self.assertFalse(duplicate_is_new)
        self.assertEqual(
            memory.list_memories()[0]["text"], "I prefer short explanations"
        )

    def test_empty_or_oversized_memories_are_rejected(self):
        with self.assertRaises(ValueError):
            memory.add_memory("   ")
        with self.assertRaises(ValueError):
            memory.add_memory("x" * (memory.MAX_MEMORY_LENGTH + 1))

    def test_forget_by_number_and_exact_text(self):
        memory.add_memory("I prefer short explanations")
        memory.add_memory("I am studying calculus")

        forgotten = memory.forget_memory_text("that I am studying calculus")

        self.assertEqual(forgotten["text"], "I am studying calculus")
        self.assertEqual(len(memory.list_memories()), 1)
        self.assertEqual(memory.forget_memory(1)["text"], "I prefer short explanations")
        self.assertEqual(memory.list_memories(), [])

    def test_unknown_memory_number_is_rejected(self):
        with self.assertRaises(IndexError):
            memory.forget_memory(1)

    def test_clear_memories_returns_number_removed(self):
        memory.add_memory("I prefer short explanations")
        memory.add_memory("I am studying calculus")

        self.assertEqual(memory.clear_memories(), 2)
        self.assertEqual(memory.list_memories(), [])


if __name__ == "__main__":
    unittest.main()
