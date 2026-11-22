import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import assistant, llm_client, memory, storage


class AssistantMemoryTests(unittest.TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        patcher = patch.object(storage, "DATA_DIR", Path(temporary_directory.name))
        patcher.start()
        self.addCleanup(patcher.stop)
        llm_client.clear_conversation()
        self.addCleanup(llm_client.clear_conversation)

    def test_remember_command_saves_only_when_explicit(self):
        response, should_exit = assistant.handle_message(
            "remember that I prefer short explanations"
        )

        self.assertFalse(should_exit)
        self.assertIn("Saved memory 1", response)
        self.assertEqual(memory.list_memories()[0]["text"], "I prefer short explanations")

    def test_natural_memory_question_lists_saved_details(self):
        memory.add_memory("I am studying calculus")

        with patch.object(assistant.llm_client, "chat") as chat:
            response, _ = assistant.handle_message("What do you remember about me?")

        self.assertIn("1. I am studying calculus", response)
        chat.assert_not_called()

    def test_forgetting_clears_saved_and_recent_context(self):
        memory.add_memory("I prefer short explanations")
        llm_client.remember_exchange("old detail", "old answer")

        response, _ = assistant.handle_message("forget 1")

        self.assertIn("cleared recent chat", response)
        self.assertEqual(memory.list_memories(), [])
        self.assertEqual(llm_client._conversation, [])

    def test_forget_all_clears_every_memory_and_context(self):
        memory.add_memory("I prefer short explanations")
        memory.add_memory("I am studying calculus")
        llm_client.remember_exchange("old detail", "old answer")

        response, _ = assistant.handle_message("forget all")

        self.assertIn("Cleared all 2", response)
        self.assertEqual(memory.list_memories(), [])
        self.assertEqual(llm_client._conversation, [])


if __name__ == "__main__":
    unittest.main()
