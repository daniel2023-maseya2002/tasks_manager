import os
import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# configure openai from django settings(safe: check if key exists)
OPENAI_API_KEY = getattr(settings, "OPENAI_API_KEY", None)
OPENAI_MODEL = getattr(settings, "OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_MAX_TOKENS = getattr(settings, "OPENAI_MAX_TOKENS", 400)

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    # don't crash on import; log an explicit message
    logger.warning("OPENAI_API_KEY not set - AI features will not work.")

def build_tasks_prompt(tasks):
    """
    Build a compact prompt listing tasks. Keep it short to reduce tokens.

    """

    lines = []
    for t in tasks:
        due = t.due_date_isoformat() if getattr(t, "due_date", None) else "no due date"
        assigned = t.assigned_to.username if getattr(t, "assigned_to", None) else "Unassigned"
        #truncate description to safe lengyh
        desc = (t.description or "").replace("\n", " ").strip()[:200]
        lines.append(f"- Title: {t.title}; Due: {due}; Status: {t.status}; Assigned: {assigned}; Desc: {desc}")
    return "Here are the user's tasks:\n" + "\n".join(lines)

def generate_task_summary(tasks, max_tasks=12, temperature=0.2):
    """
    tasks: iterable of Task objects (ordered by due_date ideally)
    returns: summary text (string) or raises Exception

    """

    if OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    

    task_list = list(tasks)[:max_tasks]
    if not task_list:
        return "No tasks found."
    

    user_prompt = build_tasks_prompt(task_list)
    system_msg = (
        "You are a helpful assistant that reads a short list of tasks and returns:\n"
        "1) A 2-4 line summary showing how many tasks and urgent items.\n"
        "2) A prioritized bullets list (High/Medium/Low) with very short rationale.\n"
        "Be concise (no more than ~160-220 words)."
    )
    
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt},
    ]
    
    try:
        resp = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=temperature,
        )
        text = resp.choices[0].message.content.strip()
        return text
    except Exception as e:
        logger.exception("OpenAI call failed")
        raise