from openai import OpenAI
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# ✅ Initialize OpenAI client
OPENAI_API_KEY = getattr(settings, "OPENAI_API_KEY", None)
OPENAI_MODEL = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
OPENAI_MAX_TOKENS = getattr(settings, "OPENAI_MAX_TOKENS", 400)

if not OPENAI_API_KEY:
    logger.warning("⚠️ OPENAI_API_KEY not set — AI features will not work.")
    client = None
else:
    client = OpenAI(api_key=OPENAI_API_KEY)


def build_tasks_prompt(tasks):
    """
    Build a compact task list to send to OpenAI.
    """
    lines = []
    for t in tasks:
        due = getattr(t, "due_date", None)
        due_str = due.isoformat() if due else "no due date"
        assigned = getattr(t.assigned_to, "username", "Unassigned")
        desc = (t.description or "").replace("\n", " ").strip()[:200]
        lines.append(f"- Title: {t.title}; Due: {due_str}; Status: {t.status}; Assigned: {assigned}; Desc: {desc}")
    return "Here are the user's tasks:\n" + "\n".join(lines)


def generate_task_summary(tasks, max_tasks=12, temperature=0.2):
    """
    Generate an AI summary of user tasks using the latest OpenAI API.
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not configured in settings.py")

    task_list = list(tasks)[:max_tasks]
    if not task_list:
        return "No tasks found."

    user_prompt = build_tasks_prompt(task_list)
    system_msg = (
        "You are a helpful assistant that reads a short list of tasks and returns:\n"
        "1) A 2–4 line summary showing how many tasks and urgent items.\n"
        "2) A prioritized bullets list (High/Medium/Low) with very short rationale.\n"
        "Be concise (no more than ~160–220 words)."
    )

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=temperature,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.exception("❌ OpenAI API call failed: %s", e)
        raise
