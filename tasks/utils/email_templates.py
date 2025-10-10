from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html
from email.mime.image import MIMEImage
from django.contrib.sites.models import Site
from django.conf import settings
import os


def get_site_url():
    """
    Returns your current site domain (using Sites Framework if available).
    Falls back to settings.SITE_DOMAIN or http://localhost:8000.
    """
    try:
        current_site = Site.objects.get_current()
        domain = current_site.domain
    except Exception:
        domain = getattr(settings, "SITE_DOMAIN", "http://localhost:8000")
    if not domain.startswith("http"):
        domain = f"https://{domain}"
    return domain


def send_task_notification(user, task, action="update"):
    """
    Sends an HTML email notification to a user depending on the action.
    """
    # 💬 Subject & message intro depending on action
    if action == "assign":
        subject = f"📋 Misala | New Task Assigned: {task.title}"
        intro = f"You've been assigned a new task titled <strong>{task.title}</strong>."
    elif action == "completed":
        subject = f"✅ Misala | Task Completed: {task.title}"
        intro = f"Your task <strong>{task.title}</strong> has been marked as completed."
    elif action == "reminder":
        subject = f"⏰ Misala | Task Reminder: {task.title}"
        intro = f"This is a friendly reminder that your task <strong>{task.title}</strong> is due soon."
    elif action == "collaborator_added":
        subject = f"👥 Misala | Added as Collaborator: {task.title}"
        intro = f"You have been added as a collaborator on the task <strong>{task.title}</strong>."
    elif action == "collaborator_removed":
        subject = f"👋 Misala | Removed from Task: {task.title}"
        intro = f"You have been removed as a collaborator from the task <strong>{task.title}</strong>."
    else:
        subject = f"🔔 Misala | Task Update: {task.title}"
        intro = f"Your task <strong>{task.title}</strong> has been updated."

    # 🧩 Task status color indicator
    status_color = (
        "#198754" if getattr(task, "status", "") == "completed"
        else "#ffc107" if getattr(task, "status", "") == "in_progress"
        else "#dc3545"
    )

    # 🔗 Task URL
    site_url = get_site_url()
    task_url = f"{site_url}/tasks/{task.id}/"

    # ✉️ Email HTML
    message_html = format_html(f"""
    <html>
    <body style="margin:0; padding:0; background-color:#f4f6f8; font-family:Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f8; padding:30px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:10px; overflow:hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background-color:#0d6efd; padding:20px 40px; text-align:center;">
                                <img src="cid:misala_logo" alt="Misala" width="120" style="display:block; margin:auto;">
                            </td>
                        </tr>

                        <!-- Body -->
                        <tr>
                            <td style="padding:40px;">
                                <h2 style="color:#333333;">Hello {user.username},</h2>
                                <p style="color:#555555; line-height:1.6; font-size:15px;">
                                    {intro}
                                </p>

                                <p style="margin:20px 0; color:#333333;">
                                    <strong>Status:</strong>
                                    <span style="color:{status_color}; font-weight:bold;">
                                        {getattr(task, "status", "Pending").replace('_', ' ').capitalize()}
                                    </span>
                                </p>

                                <div style="text-align:center; margin:40px 0;">
                                    <a href="{task_url}"
                                       style="background-color:#0d6efd; color:#ffffff; text-decoration:none;
                                              padding:12px 30px; border-radius:6px; display:inline-block; font-weight:bold;">
                                        View Task
                                    </a>
                                </div>

                                <p style="color:#555555; line-height:1.6; font-size:14px;">
                                    Stay productive with <strong>Misala</strong> — where smart teams get things done efficiently.
                                </p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background-color:#f1f3f5; text-align:center; padding:20px;">
                                <p style="color:#999999; font-size:13px; margin:0;">
                                    © 2025 <strong>Misala</strong> | Smart Task Management Platform
                                </p>
                                <p style="color:#bbbbbb; font-size:12px; margin-top:5px;">
                                    This is an automated email — please do not reply.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """)

    # 📨 Compose Email
    email = EmailMultiAlternatives(
        subject=subject,
        body="This email requires an HTML-compatible viewer.",
        from_email="Misala <no-reply@misala.com>",
        to=[user.email],
    )
    email.attach_alternative(message_html, "text/html")

    # ✅ Inline logo (optional)
    logo_path = os.path.join("static", "picture", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo = MIMEImage(f.read())
            logo.add_header("Content-ID", "<misala_logo>")
            logo.add_header("Content-Disposition", "inline", filename="logo.png")
            email.attach(logo)

    # ✅ Send
    email.send()
