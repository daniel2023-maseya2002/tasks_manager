from django.core.management.base import BaseCommand
from tasks.utils import send_task_reminders

class Command(BaseCommand):
    help = 'Send and notification reminders for upcoming task deadlines.'

    def handle(self, *args, **options):
        send_task_reminders()
        self.stdout.write(self.style.SUCCESS('Task reminders sent successfully'))