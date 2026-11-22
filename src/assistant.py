import re
from datetime import date

from . import inquiries, lesson_planner, llm_client, memory, tasks


def show_tasks():
    task_list = tasks.list_tasks()
    if not task_list:
        return "Your task list is empty. Add one with: add <task>"

    lines = ["Here are your tasks:"]
    for number, task in enumerate(task_list, start=1):
        marker = "x" if task["done"] else " "
        lines.append(f"  {number}. [{marker}] {task['text']}")
    return "\n".join(lines)


def show_inquiries():
    inquiry_list = inquiries.list_inquiries()
    if not inquiry_list:
        return "No customer inquiries yet."

    lines = ["Here are your customer inquiries:"]
    for number, inquiry in enumerate(inquiry_list, start=1):
        status = inquiry["status"].upper()
        follow_up = inquiry.get("follow_up") or "not set"
        lines.append(
            f"  {number}. [{status}] {inquiry['customer']} — "
            f"{inquiry['request']} (received {inquiry['date']}; "
            f"follow-up: {follow_up})"
        )
    return "\n".join(lines)


def show_followups():
    open_followups = inquiries.get_open_followups()
    if not open_followups:
        return "All caught up. There are no open inquiries."

    lines = ["Open inquiries and their follow-up dates:"]
    for number, inquiry, label in open_followups:
        lines.append(
            f"  {number}. [{label}] {inquiry['customer']} — " f"{inquiry['request']}"
        )
    return "\n".join(lines)


def show_memories():
    saved_memories = memory.list_memories()
    if not saved_memories:
        return (
            "I don't have any saved memories yet. To save one, say: "
            "remember that I prefer short explanations. I only save details "
            "when you explicitly ask me to."
        )

    lines = ["Saved memories on this computer:"]
    for number, item in enumerate(saved_memories, start=1):
        lines.append(f"  {number}. {item['text']}")
    lines.append("Say 'forget 1' to remove a memory, or 'forget all' to clear them.")
    return "\n".join(lines)


def show_brief():
    today = date.today()
    task_list = tasks.list_tasks()
    open_tasks = [
        (number, task)
        for number, task in enumerate(task_list, start=1)
        if not task["done"]
    ]
    completed_count = len(task_list) - len(open_tasks)

    all_inquiries = inquiries.list_inquiries()
    open_followups = inquiries.get_open_followups(today=today)
    replied_count = len(all_inquiries) - len(open_followups)

    labels = [label for _, _, label in open_followups]
    overdue_count = sum(label.startswith("OVERDUE") for label in labels)
    due_today_count = labels.count("DUE TODAY")
    upcoming_count = sum(label.startswith("UPCOMING") for label in labels)
    no_date_count = labels.count("NO DATE SET")
    check_date_count = labels.count("CHECK DATE")

    lines = [
        f"Daily business brief for {today.strftime('%B %d, %Y')}",
        f"  Tasks: {len(open_tasks)} open, {completed_count} completed",
        f"  Inquiries: {len(open_followups)} open, {replied_count} replied",
        (
            f"  Follow-ups: {overdue_count} overdue, {due_today_count} due today, "
            f"{upcoming_count} upcoming, {no_date_count} without a date, "
            f"{check_date_count} to check"
        ),
    ]

    if open_tasks:
        lines.append("  Open tasks:")
        for number, task in open_tasks:
            lines.append(f"    {number}. {task['text']}")

    attention_items = [
        (number, inquiry, label)
        for number, inquiry, label in open_followups
        if (
            label.startswith("OVERDUE")
            or label in {"DUE TODAY", "NO DATE SET", "CHECK DATE"}
        )
    ]
    if attention_items:
        lines.append("  Customer inquiries needing attention:")
        for number, inquiry, label in attention_items:
            lines.append(
                f"    {number}. [{label}] {inquiry['customer']} — "
                f"{inquiry['request']}"
            )
    elif not open_tasks:
        lines.append("  Nothing needs attention right now.")
    return "\n".join(lines)


def _natural_request(message):
    """Match common read-only requests before sending text to the chat model."""
    normalized = re.sub(r"[^\w' ]", " ", message.lower())
    normalized = " ".join(normalized.split())

    daily_brief_requests = {
        "how is my day",
        "how's my day",
        "what should i focus on today",
        "what should i do today",
        "what needs my attention",
        "what needs my attention today",
        "what should i do next",
        "what do i need to do",
        "what do i need to work on",
        "what is due today",
        "what's due today",
        "what do i need to do today",
    }
    if normalized in daily_brief_requests:
        return show_brief()

    memory_requests = {
        "what do you remember",
        "what do you remember about me",
        "what have you remembered",
        "show my memories",
        "show me my memories",
        "list my memories",
        "list memories",
    }
    if normalized in memory_requests:
        return show_memories()

    task_list_requests = {
        "show me my tasks",
        "show my tasks",
        "what tasks do i have",
        "what are my tasks",
        "what's on my task list",
        "what is on my task list",
        "what's on my list",
        "what is on my list",
    }
    if normalized in task_list_requests:
        return show_tasks()

    inquiry_requests = {
        "show my inquiries",
        "show inquiries",
        "show me my inquiries",
        "show me inquiries",
        "what inquiries do i have",
        "what are my inquiries",
    }
    if normalized in inquiry_requests:
        return show_inquiries()

    followup_requests = {
        "who needs a follow up",
        "who needs follow ups",
        "who do i need to follow up with",
        "show my follow ups",
        "show follow ups",
        "show open follow ups",
        "what follow ups are due",
        "any follow ups due",
    }
    if normalized in followup_requests:
        return show_followups()

    lesson_topic = re.search(r"\b(limits?|derivatives?|integrals?)\b", normalized)
    lesson_actions = {"create", "give", "make", "plan", "prepare"}
    if (
        lesson_topic
        and "lesson" in normalized.split()
        and lesson_actions.intersection(normalized.split())
    ):
        return lesson_planner.create_lesson_plan(lesson_topic.group(1))

    return None


def _handle_message(message):
    parts = message.strip().split(maxsplit=1)
    command = parts[0] if parts else ""
    details = parts[1].strip() if len(parts) > 1 else ""
    command = command.lower()

    if command in {"quit", "exit"}:
        return "Your information is saved. Goodbye!", True

    if command == "help":
        return (
            "Try these commands:\n"
            "  add <task> - save a new task\n"
            "  list - show your tasks\n"
            "  done <number> - mark a task complete\n"
            "  inquiry <name> | <request> - record a customer inquiry\n"
            "  inquiries - show all customer inquiries\n"
            "  followup <number> YYYY-MM-DD - set a follow-up date\n"
            "  followups - show open inquiries and due dates\n"
            "  brief - summarize tasks and customer follow-ups\n"
            "  lesson <topic> - create a 60-minute lesson on limits or derivatives\n"
            "  replied <number> - record that you replied; it sends no message\n"
            "  remember <fact> - save a detail on this computer\n"
            "  memories - review saved details\n"
            "  forget <number or exact detail> - remove a saved detail\n"
            "  forget all - clear every saved detail\n"
            "  You can also ask naturally: 'What should I focus on today?'\n"
            "  or 'What do you remember about me?'\n"
            "  or 'Who needs a follow-up?' / 'Plan a lesson on derivatives.'\n"
            "  Ask any other question to chat with JARVIS's local AI model\n"
            "  quit - close JARVIS",
            False,
        )
    if command == "add":
        try:
            task_number = tasks.add_task(details)
        except ValueError:
            return (
                "Tell me the task after 'add'. Example: add prepare weekly report",
                False,
            )
        return f"Added task {task_number}: {details}", False
    if command in {"list", "tasks"}:
        return show_tasks(), False
    if command == "done":
        try:
            number = int(details)
            tasks.mark_task_done(number)
        except ValueError:
            return "Use 'done' followed by a task number. Example: done 1", False
        except IndexError:
            return (
                "I can't find that task number. Type 'list' to see your tasks.",
                False,
            )
        return f"Marked task {number} complete.", False
    if command == "inquiry":
        customer, separator, request = details.partition("|")
        if not separator:
            return (
                "Use this format: inquiry <name> | <what they need>\n"
                "  Example: inquiry Alex | interested in weekly algebra tutoring",
                False,
            )
        try:
            inquiry_number = inquiries.add_inquiry(customer, request)
        except ValueError:
            return "Include both a name and what the customer needs.", False
        return (
            f"Recorded inquiry {inquiry_number} for {customer.strip()}. "
            "No message was sent.",
            False,
        )
    if command == "inquiries":
        return show_inquiries(), False
    if command == "followup":
        parts = details.split(maxsplit=1)
        if len(parts) != 2:
            return (
                "Use 'followup' with an inquiry number and date. "
                "Example: followup 2 2026-11-20",
                False,
            )
        try:
            number = int(parts[0])
            inquiries.set_follow_up(number, parts[1])
        except ValueError:
            return "Check the inquiry number and use a date like 2026-11-20.", False
        except IndexError:
            return (
                "I can't find that inquiry number. Type 'inquiries' to see them.",
                False,
            )
        return f"Follow-up for inquiry {number} is set to {parts[1]}.", False
    if command == "followups":
        return show_followups(), False
    if command == "lesson":
        if not details:
            return (
                "Choose a Calculus I topic. Try: lesson limits or lesson derivatives",
                False,
            )
        return lesson_planner.create_lesson_plan(details), False
    if command in {"brief", "summary"}:
        return show_brief(), False
    if command == "replied":
        try:
            number = int(details)
            inquiries.mark_replied(number)
        except ValueError:
            return (
                "Use 'replied' followed by an inquiry number. Example: replied 1",
                False,
            )
        except IndexError:
            return (
                "I can't find that inquiry number. Type 'inquiries' to see them.",
                False,
            )
        return f"Marked inquiry {number} as replied. No message was sent.", False

    if command in {"remember", "memorize"}:
        if not details:
            return (
                "Tell me what to save after 'remember'. Example: "
                "remember that I prefer short explanations",
                False,
            )
        try:
            number, is_new = memory.add_memory(details)
        except ValueError as error:
            return str(error), False
        if is_new:
            return (
                f"Saved memory {number} on this computer. Say 'memories' to review "
                f"it or 'forget {number}' to remove it.",
                False,
            )
        return f"That detail is already saved as memory {number}.", False

    if command in {"memory", "memories"}:
        return show_memories(), False

    if command == "forget":
        if details.casefold() in {"all", "all memories", "everything"}:
            removed_count = memory.clear_memories()
            llm_client.clear_conversation()
            if removed_count == 0:
                return "There were no saved memories to clear; recent chat was reset.", False
            return (
                f"Cleared all {removed_count} saved memories from this computer "
                "and reset recent chat.",
                False,
            )

        memory_number = re.fullmatch(r"(?:memory\s+)?(\d+)", details, re.IGNORECASE)
        try:
            if memory_number:
                memory.forget_memory(int(memory_number.group(1)))
            elif details:
                memory.forget_memory_text(details)
            else:
                return (
                    "Say 'forget' followed by a memory number or its exact text. "
                    "Say 'forget all' to clear every saved memory.",
                    False,
                )
        except IndexError:
            return "I can't find that memory number. Say 'memories' to review the list.", False
        except KeyError:
            return (
                "I couldn't match that detail exactly. Say 'memories' to review the "
                "list, then tell me its number to forget it.",
                False,
            )
        llm_client.clear_conversation()
        return (
            "Removed that saved memory from this computer and cleared recent chat.",
            False,
        )

    natural_response = _natural_request(message)
    if natural_response is not None:
        return natural_response, False

    return llm_client.chat(message, memories=memory.list_memories()), False


def handle_message(message):
    """Handle a turn and retain recent replies for local follow-up questions."""
    response, should_exit = _handle_message(message)
    parts = message.strip().split(maxsplit=1)
    command = parts[0].casefold() if parts else ""
    if message.strip() and not should_exit and command != "forget":
        llm_client.remember_exchange(message, response)
    return response, should_exit


def main():
    print("JARVIS is online. Type 'help' to see what I can do, or 'quit' to exit.")
    while True:
        message = input("You: ").strip()
        if not message:
            continue
        response, should_exit = handle_message(message)
        print(f"JARVIS: {response}")
        if should_exit:
            break


if __name__ == "__main__":
    main()
