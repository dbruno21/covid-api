from rest_framework import serializers

from covid_api.core.models import Dataset


class DatasetSerializer(serializers.ModelSerializer):
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
