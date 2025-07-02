from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandParser

class Command(BaseCommand):
    help = "Fetch data from third-party APIs"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--date-range",
            type=lambda s: tuple(map(str.strip, s.split(","))),
            required=False,
            default=None,
            metavar="START_DATE,END_DATE",
            help="Date range in the format 'YYYY-MM-DD,YYYY-MM-DD' (e.g. 2024-01-01,2024-01-31)",
        )

    def handle(self, *args, **options):
        if not options["date_range"]:
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=1)
            self.stdout.write(f"Fetching data for today: {start_date}")
        else:
            start_date, end_date = options["date_range"]
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            self.stdout.write(f"Fetching data for date range: {start_date} to {end_date}")