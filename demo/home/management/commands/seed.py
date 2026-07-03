from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the demo user that the panel logs in as (LOGINOUT_USERNAME)."

    def handle(self, *args, **options):
        User = get_user_model()
        username = settings.LOGINOUT_USERNAME
        user, created = User.objects.get_or_create(
            **{User.USERNAME_FIELD: username}
        )
        if created:
            user.set_password("demo")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user {username!r}."))
        else:
            self.stdout.write(f"User {username!r} already exists.")
