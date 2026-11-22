"""Explicit, local-only memories that can be reviewed and removed by the user."""

from datetime import date

from . import storage

MEMORY_FILE = "memory.json"
MAX_MEMORIES = 50
MAX_MEMORY_LENGTH = 500


def list_memories():
    """Return saved memories in the order they were added."""
    return storage.load_records(MEMORY_FILE)


def _clean_memory_text(text):
    cleaned = text.strip()
    if cleaned.casefold().startswith("that "):
        cleaned = cleaned[5:].strip()
    return cleaned


def add_memory(text):
    """Save a user-requested fact; return its number and whether it was new."""
    cleaned = _clean_memory_text(text)
    if not cleaned:
        raise ValueError("A memory needs some text.")
    if len(cleaned) > MAX_MEMORY_LENGTH:
        raise ValueError(f"Keep each memory under {MAX_MEMORY_LENGTH} characters.")

    memories = list_memories()
    for number, item in enumerate(memories, start=1):
        if item.get("text", "").casefold() == cleaned.casefold():
            return number, False

    if len(memories) >= MAX_MEMORIES:
        raise ValueError(f"JARVIS can keep up to {MAX_MEMORIES} memories. Remove one first.")

    memories.append({"text": cleaned, "saved_on": date.today().isoformat()})
    storage.save_records(MEMORY_FILE, memories)
    return len(memories), True


def forget_memory(number):
    """Remove one memory by its displayed, one-based number."""
    memories = list_memories()
    if number < 1 or number > len(memories):
        raise IndexError("That memory number does not exist.")

    forgotten = memories.pop(number - 1)
    storage.save_records(MEMORY_FILE, memories)
    return forgotten


def forget_memory_text(text):
    """Remove a memory when the user repeats its saved text exactly."""
    target = _clean_memory_text(text).casefold()
    for number, item in enumerate(list_memories(), start=1):
        if item.get("text", "").casefold() == target:
            return forget_memory(number)
    raise KeyError("No saved memory matched that text exactly.")


def clear_memories():
    """Delete all saved memories and return the number that was removed."""
    count = len(list_memories())
    storage.save_records(MEMORY_FILE, [])
    return count
