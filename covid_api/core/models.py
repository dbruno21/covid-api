from django.db import models
from postgres_copy import CopyManager

# Create your models here.


class Province:

    # Source: https://sitioanterior.indec.gob.ar/ftp/cuadros/menusuperior/clasificadores/anexo1_resol55_2019.pdf
    PROVINCES = {
        '02': 'CABA',
        '06': 'Buenos Aires',
        '10': 'Catamarca',
        '14': 'Córdoba',
        '18': 'Corrientes',
        '22': 'Chaco',
        '26': 'Chubut',
        '30': 'Entre Ríos',
        '34': 'Formosa',
        '38': 'Jujuy',
        '42': 'La Pampa',
        '46': 'La Rioja',
        '50': 'Mendoza',
        '54': 'Misiones',
        '58': 'Neuquén',
        '62': 'Río Negro',
        '66': 'Salta',
        '70': 'San Juan',
        '74': 'San Luis',
        '78': 'Santa Cruz',
        '82': 'Santa Fe',
        '86': 'Santiago del Estero',
        '90': 'Tucumán',
        '94': 'Tierra del Fuego',
    }

    @classmethod
    def from_slug(cls, slug):
        return cls.PROVINCES.get(slug, None)

    def __init__(self, slug, province):
        self.slug = slug
        self.province = province


class Classification:

    classifications = {
        'confirmed': 'Confirmado',
        'rejected': 'Descartado',
        'suspect': 'Sospechoso'
    }

    @classmethod
    def translate(cls, classification):
        data_classification = cls.classifications.get(classification)
        return data_classification


class Dataset(models.Model):
    id_evento_caso = models.IntegerField(primary_key=True)
    sexo = models.TextField(null=True)
    edad = models.FloatField(null=True)
    edad_años_meses = models.TextField(null=True)
    residencia_pais_nombre = models.TextField(null=True)
    residencia_provincia_nombre = models.TextField(null=True)
    residencia_departamento_nombre = models.TextField(null=True)
    carga_provincia_nombre = models.TextField(null=True)
    fecha_inicio_sintomas = models.TextField(null=True)
    fecha_apertura = models.TextField(null=True)
    sepi_apertura = models.IntegerField(null=True)
    fecha_internacion = models.TextField(null=True)
    cuidado_intensivo = models.TextField(null=True)
    fecha_cui_intensivo = models.TextField(null=True)
    fallecido = models.TextField(null=True)
    fecha_fallecimiento = models.TextField(null=True)
    asistencia_respiratoria_mecanica = models.TextField(null=True)
    carga_provincia_id = models.IntegerField(null=True)
    origen_financiamiento = models.TextField(null=True)
    clasificacion = models.TextField(null=True)
    clasificacion_resumen = models.TextField(null=True)
    residencia_provincia_id = models.IntegerField(null=True)
    fecha_diagnostico = models.TextField(null=True)
    residencia_departamento_id = models.IntegerField(null=True)
    ultima_actualizacion = models.TextField(null=True)

    objects = CopyManager()


class CountModel:
    def __init__(self, data):
        self.count = data.count()


class LastUpdate:
    def __init__(self, data):
        self.last_update = data.max('ultima_actualizacion')


class Stats:
    def __init__(self, province_name, province_data, population):
        # Get population from 2020
        cases_amount = province_data.count()
        print(cases_amount)
        cases_per_million = cases_amount * 1000000 / population
        cases_per_hundred_thousand = cases_amount * 100000 / population
        dead_amount = province_data.filter_eq('fallecido', 'SI').count()
        dead_per_million = dead_amount * 1000000 / population
        dead_per_hundred_thousand = dead_amount * 100000 / population
        self.provincia = province_name
        self.población = int(population)
        self.muertes_por_millón = round(dead_per_million)
        self.muertes_cada_cien_mil = round(dead_per_hundred_thousand)
        self.casos_por_millón = round(cases_per_million)
        self.casos_cada_cien_mil = round(cases_per_hundred_thousand)
        self.letalidad = round(dead_amount / cases_amount, 4)


class SummaryEntry:

    HUNDRED_THOUSAND = 100000
    MILLION = 1000000

    def __init__(self, date, cases, deaths, cases_acum, deaths_acum, population):
        self.fecha = date
        self.casos = cases
        self.muertes = deaths
        self.casos_acum = cases_acum
        self.muertes_acum = deaths_acum

        # per hundred thousand
        self.casos_cada_cien_mil = round(cases * self.HUNDRED_THOUSAND / population)
        self.muertes_cada_cien_mil = round(deaths * self.HUNDRED_THOUSAND / population)
        self.casos_acum_cada_cien_mil = round(cases_acum * self.HUNDRED_THOUSAND / population)
        self.muertes_acum_cada_cien_mil = round(deaths_acum * self.HUNDRED_THOUSAND / population)

        # per million
        self.casos_por_millón = round(cases * self.MILLION / population)
        self.muertes_por_millón = round(deaths * self.MILLION / population)
        self.casos_acum_por_millón = round(cases_acum * self.MILLION / population)
        self.muertes_acum_por_millón = round(deaths_acum * self.MILLION / population)
