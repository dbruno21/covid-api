import numpy as np
import pandas as pd
import requests
from django import db
from datetime import datetime, timedelta
from postgres_copy import CopyManager

import xlrd
from django.db.models import Max, Count, Q

from covid_api.core.models import Province, Dataset, Stats, SummaryEntry


class DatasetWrapper:

    def __init__(self, dataset):
        self.dataset = dataset

    def count(self):
        # Count rows
        return self.dataset.count()

    def max(self, column):
        return self.dataset.aggregate(max=Max(column))['max']

    def group_by(self, columns):
        self.dataset = self.dataset.values(*columns)
        return self

    def annotate(self, aggregations):
        return self.dataset.annotate(**aggregations)

    def copy(self):
        return DatasetWrapper(self.dataset)

    def filter_eq(self, column, value):
        key = column
        self.dataset = self.dataset.filter(**{key: value})
        return self

    def filter_ge(self, column, value):
        key = f'{column}__gte'
        self.dataset = self.dataset.filter(**{key: value})
        return self

    def filter_le(self, column, value):
        key = f'{column}__lte'
        self.dataset = self.dataset.filter(**{key: value})
        return self


class CovidService:

    _raw_data = None

    data_url = 'https://sisa.msal.gov.ar/datos/descargas/covid-19/files/Covid19Casos.csv'

    # Refresh time in hours
    refresh_rate = 1

    last_refresh = None

    CSV_DTYPES = {
        'id_evento_caso': np.int64,
        'sexo': np.str,
        'edad': np.float64,
        'edad_años_meses': np.str,
        'residencia_pais_nombre': np.str,
        'residencia_provincia_nombre': np.str,
        'residencia_departamento_nombre': np.str,
        'carga_provincia_nombre': np.str,
        'fecha_inicio_sintomas': np.str,
        'fecha_apertura': np.str,
        'sepi_apertura': np.int64,
        'fecha_internacion': np.str,
        'cuidado_intensivo': np.str,
        'fecha_cui_intensivo': np.str,
        'fallecido': np.str,
        'fecha_fallecimiento': np.str,
        'asistencia_respiratoria_mecanica': np.str,
        'carga_provincia_id': np.int64,
        'origen_financiamiento': np.str,
        'clasificacion': np.str,
        'clasificacion_resumen': np.str,
        'residencia_provincia_id': np.int64,
        'fecha_diagnostico': np.str,
        'residencia_departamento_id': np.int64,
        'ultima_actualizacion': np.str,
    }

    @classmethod
    def get_data(cls) -> DatasetWrapper:
        return DatasetWrapper(Dataset.objects.all())

    @classmethod
    def has_data(cls) -> bool:
        return Dataset.objects.all().count() > 0

    @classmethod
    def delete_data(cls):
        Dataset.objects.all().delete()

    @classmethod
    def update_data(cls):
        cls.delete_data()

        print(f"Started dowloading dataset at: {datetime.now()}")
        response = requests.get(cls.data_url, stream=True)
        text_file = open("data.csv", "wb")
        for chunk in response.iter_content(chunk_size=1024):
            text_file.write(chunk)
        text_file.close()
        print(f"Finished dowloading dataset at: {datetime.now()}")

        print(f"Started uploading dataset to database at: {datetime.now()}")
        Dataset.objects.from_csv("data.csv", drop_constraints=False, drop_indexes=False)
        print(f"Finished uploading dataset to database at: {datetime.now()}")

    @classmethod
    def provinces_stats(cls, data):
        provinces_stats = []
        # Filter the data
        data = data.filter_eq('clasificacion_resumen', 'Confirmado')
        results = data.group_by(['carga_provincia_nombre']).annotate({"cases": Count('*'), "deaths": Count('fallecido', filter=Q(fallecido='SI'))})
        results_by_key = {result['carga_provincia_nombre']: result for result in results}
        population = cls.population_per_province()
        sum_cases = 0
        sum_deaths = 0
        for slug, province_name in Province.PROVINCES.items():
            sum_cases += results_by_key[province_name]['cases'] if province_name in results_by_key else 0
            sum_deaths += results_by_key[province_name]['deaths'] if province_name in results_by_key else 0
            params = {
                "province_name": province_name,
                "cases": results_by_key[province_name]['cases'] if province_name in results_by_key else 0,
                "deaths": results_by_key[province_name]['deaths'] if province_name in results_by_key else 0,
                "population": population[slug]
            }
            province_stats = Stats(**params)
            provinces_stats.append(province_stats)
        params = {
            "province_name": "Argentina",
            "cases": sum_cases,
            "deaths": sum_deaths,
            "population": population['ARG']
        }
        country_stats = Stats(**params)
        provinces_stats.insert(0, country_stats)
        return provinces_stats

    @classmethod
    def province_stats(cls, data, province_slug):
        # Filter the data
        data = data.filter_eq('clasificacion_resumen', 'Confirmado')
        province_name = Province.from_slug(province_slug)
        data = data.filter_eq(
            'carga_provincia_nombre',
            province_name
        )
        results = data.group_by(['carga_provincia_nombre']).annotate({"cases": Count('*'), "deaths": Count('fallecido', filter=Q(fallecido='SI'))})
        results_by_key = {result['carga_provincia_nombre']: result for result in results}
        params = {
            "province_name": province_name,
            "cases": results_by_key[province_name]['cases'] if province_name in results_by_key else 0,
            "deaths": results_by_key[province_name]['deaths'] if province_name in results_by_key else 0,
            "population": cls.population_per_province()[province_slug]
        }
        province_stats = Stats(**params)
        return province_stats

    @classmethod
    def population_per_province(cls):
        provinces_population = {}
        workbook = xlrd.open_workbook('poblacion.xls')
        for worksheet in workbook.sheets():
            split_name = worksheet.name.split('-')
            if len(split_name) < 2:
                continue
            province_slug = split_name[0]
            province_name = Province.from_slug(province_slug)
            if province_name:
                provinces_population[province_slug] = worksheet.cell(16, 1).value
                continue
            else:
                provinces_population['ARG'] = worksheet.cell(15, 1).value

        return provinces_population

    @classmethod
    def summary(cls, data, start_date, end_date, province_slug=None):
        start_date = start_date if start_date else '2020-02-11'
        if not end_date:
            end_date = data.max('ultima_actualizacion')

        raw_range = pd.date_range(start=start_date, end=end_date)
        range_strings = raw_range.format(formatter=lambda x: x.strftime('%Y-%m-%d'))
        population_per_province = cls.population_per_province()
        if province_slug:
            population = population_per_province[province_slug]
        else:
            population = population_per_province['ARG']

        cases_results = data.copy().group_by(['fecha_diagnostico']).annotate({"cases": Count('*')})
        cases_results_by_key = {cases_result['fecha_diagnostico']: cases_result for cases_result in cases_results}

        deaths_results = data.copy().group_by(['fecha_fallecimiento']).annotate({"deaths": Count('fallecido', filter=Q(fallecido='SI'))})
        deaths_results_by_key = {deaths_result['fecha_fallecimiento']: deaths_result for deaths_result in deaths_results}

        summary = []
        cases_acum = 0
        deaths_acum = 0
        for date in range_strings:
            if date in cases_results_by_key:
                cases_acum += cases_results_by_key[date]['cases']
            if date in deaths_results_by_key:
                deaths_acum += deaths_results_by_key[date]['deaths']
            params = {
                "date": date,
                "cases": cases_results_by_key[date]['cases'] if date in cases_results_by_key else 0,
                "deaths": deaths_results_by_key[date]['deaths'] if date in deaths_results_by_key else 0,
                "cases_acum": cases_acum,
                "deaths_acum": deaths_acum,
                "population": population
            }
            summary_entry = SummaryEntry(**params)
            summary.append(summary_entry)

        return summary
