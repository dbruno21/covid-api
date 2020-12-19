from django.core.management import BaseCommand

from covid_api.core.services.covid_service import CovidService


class Command(BaseCommand):
    help = 'Delete the COVID-19 data'

    def handle(self, *args, **options):
        print("Started deleting data..")
        CovidService.delete_data()
        print("Finished deleting data")
