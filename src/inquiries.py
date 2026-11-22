from datetime import date

from . import storage

INQUIRIES_FILE = "inquiries.json"


def list_inquiries():
    return storage.load_records(INQUIRIES_FILE)


def add_inquiry(customer, request):
    customer_name = customer.strip()
    request_text = request.strip()
    if not customer_name or not request_text:
        raise ValueError("A customer name and request are required.")

    inquiries = list_inquiries()
    inquiries.append(
        {
            "customer": customer_name,
            "request": request_text,
            "date": date.today().isoformat(),
            "follow_up": None,
            "status": "new",
        }
    )
    storage.save_records(INQUIRIES_FILE, inquiries)
    return len(inquiries)


def set_follow_up(number, due_date):
    try:
        normalized_date = date.fromisoformat(due_date).isoformat()
    except (TypeError, ValueError) as error:
        raise ValueError("Enter a date in YYYY-MM-DD format.") from error

    inquiries = list_inquiries()
    if number < 1 or number > len(inquiries):
        raise IndexError("That inquiry number does not exist.")

    inquiries[number - 1]["follow_up"] = normalized_date
    storage.save_records(INQUIRIES_FILE, inquiries)


def mark_replied(number):
    inquiries = list_inquiries()
    if number < 1 or number > len(inquiries):
        raise IndexError("That inquiry number does not exist.")

    inquiries[number - 1]["status"] = "replied"
    storage.save_records(INQUIRIES_FILE, inquiries)


def follow_up_label(inquiry, today=None):
    today = today or date.today()
    follow_up = inquiry.get("follow_up")
    if not follow_up:
        return "NO DATE SET"

    try:
        due_date = date.fromisoformat(follow_up)
    except (TypeError, ValueError):
        return "CHECK DATE"

    if due_date < today:
        return f"OVERDUE — due {due_date.isoformat()}"
    if due_date == today:
        return "DUE TODAY"
    return f"UPCOMING — due {due_date.isoformat()}"


def get_open_followups(today=None):
    today = today or date.today()
    open_followups = []
    for number, inquiry in enumerate(list_inquiries(), start=1):
        if inquiry.get("status") == "replied":
            continue
        open_followups.append(
            (number, inquiry, follow_up_label(inquiry, today))
        )
    return open_followups