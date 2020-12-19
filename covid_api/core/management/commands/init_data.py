from django.core.management import BaseCommand

from covid_api.core.cron import update_data
from covid_api.core.services.covid_service import CovidService


class Command(BaseCommand):
    help = 'Initialize the COVID-19 data'

    def handle(self, *args, **options):
        if CovidService.has_data():
            return
        print("Database is empty... starting update")
        update_data()
