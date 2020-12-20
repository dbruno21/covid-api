from rest_framework import serializers
import numpy as np

from covid_api.core.models import Dataset


class DatasetPaginatedSerializer(serializers.Serializer):
    page = serializers.SerializerMethodField()
    total_pages = serializers.SerializerMethodField()
    dataset = serializers.SerializerMethodField()

    def get_page(self, dataset_paginated):
        return dataset_paginated['page']

    def get_total_pages(self, dataset_paginated):
        return dataset_paginated['total_pages']

    def get_dataset(self, dataset_paginated):
        return DatasetSerializer(dataset_paginated['dataset'], many=True).data


class DatasetSerializer(serializers.ModelSerializer):
    edad = serializers.SerializerMethodField()
    fecha_inicio_sintomas = serializers.SerializerMethodField()
    fecha_apertura = serializers.SerializerMethodField()
    fecha_internacion = serializers.SerializerMethodField()
    fecha_cui_intensivo = serializers.SerializerMethodField()
    fecha_fallecimiento = serializers.SerializerMethodField()
    fecha_diagnostico = serializers.SerializerMethodField()
    ultima_actualizacion = serializers.SerializerMethodField()

    def get_edad(self, dataset):
        if np.isnan(dataset.edad):
            return 0
        return dataset.edad

    def get_fecha_inicio_sintomas(self, dataset):
        if dataset.fecha_inicio_sintomas == "nan":
            return None
        return dataset.fecha_inicio_sintomas

    def get_fecha_apertura(self, dataset):
        if dataset.fecha_apertura == "nan":
            return None
        return dataset.fecha_apertura

    def get_fecha_internacion(self, dataset):
        if dataset.fecha_internacion == "nan":
            return None
        return dataset.fecha_internacion

    def get_fecha_cui_intensivo(self, dataset):
        if dataset.fecha_cui_intensivo == "nan":
            return None
        return dataset.fecha_cui_intensivo

    def get_fecha_fallecimiento(self, dataset):
        if dataset.fecha_fallecimiento == "nan":
            return None
        return dataset.fecha_fallecimiento

    def get_fecha_diagnostico(self, dataset):
        if dataset.fecha_diagnostico == "nan":
            return None
        return dataset.fecha_diagnostico

    def get_ultima_actualizacion(self, dataset):
        if dataset.ultima_actualizacion == "nan":
            return None
        return dataset.ultima_actualizacion

    class Meta:
        model = Dataset
        fields = '__all__'


class CountSerializer(serializers.Serializer):
    count = serializers.IntegerField()


class LastUpdateSerializer(serializers.Serializer):
    last_update = serializers.CharField()


class ProvinceSerializer(serializers.Serializer):
    slug = serializers.CharField()
    province = serializers.CharField()


class StatsSerializer(serializers.Serializer):
    provincia = serializers.CharField()
    población = serializers.IntegerField()
    muertes_por_millón = serializers.IntegerField()
    muertes_cada_cien_mil = serializers.IntegerField()
    casos_por_millón = serializers.IntegerField()
    casos_cada_cien_mil = serializers.IntegerField()
    letalidad = serializers.FloatField()


class SummarySerializer(serializers.Serializer):
    fecha = serializers.CharField()
    casos = serializers.IntegerField()
    muertes = serializers.IntegerField()
    muertes_acum = serializers.IntegerField()
    casos_acum = serializers.IntegerField()
    casos_cada_cien_mil = serializers.IntegerField()
    muertes_cada_cien_mil = serializers.IntegerField()
    casos_acum_cada_cien_mil = serializers.IntegerField()
    muertes_acum_cada_cien_mil = serializers.IntegerField()
    casos_por_millón = serializers.IntegerField()
    muertes_por_millón = serializers.IntegerField()
    casos_acum_por_millón = serializers.IntegerField()
    muertes_acum_por_millón = serializers.IntegerField()
