from datetime import datetime

from covid_api.core.services.covid_service import CovidService


def update_data():
    print(f"Started database update at: {datetime.now()}")
    CovidService.update_data()
    print(f"Finish database update at: {datetime.now()}")
