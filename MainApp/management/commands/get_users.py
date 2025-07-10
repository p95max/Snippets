from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Get registered users'

    def add_args(self,parser):
        parser.add_argument(
            '--max_users',
            type=int,
            help='Limits number of users',
        )

    def handle(self, *args, **options):
        self.stdout.write('Getting registered users... \ndone!')

        self.stdout.write('--- Users list: ---')
        max_users = options.get('max_users')
        users = User.objects.all()[:max_users]

        for user in users:
            self.stdout.write(f"{user}")