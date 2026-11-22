from . import storage

TASKS_FILE = "tasks.json"


def list_tasks():
    return storage.load_records(TASKS_FILE)


def add_task(text):
    description = text.strip()
    if not description:
        raise ValueError("A task description is required.")

    tasks = list_tasks()
    tasks.append({"text": description, "done": False})
    storage.save_records(TASKS_FILE, tasks)
    return len(tasks)


def mark_task_done(number):
    tasks = list_tasks()
    if number < 1 or number > len(tasks):
        raise IndexError("That task number does not exist.")

    tasks[number - 1]["done"] = True
    storage.save_records(TASKS_FILE, tasks)