from django.core.paginator import Paginator
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_csv.renderers import CSVRenderer

from .models import Province, Classification, CountModel, LastUpdate
from .parameters import DateParameter, ClassificationParameter
from .serializers import CountSerializer, StatsSerializer, LastUpdateSerializer, ProvinceSerializer, DatasetSerializer, \
    SummarySerializer
from .services.covid_service import CovidService, DatasetWrapper


# ----- GENERIC VIEWS ----- #
class ProcessDataView(APIView):

    renderer_classes = [JSONRenderer, CSVRenderer]

    def process_data(self, request, data: DatasetWrapper, **kwargs) -> DatasetWrapper:
        return data

    def filter_data(self, request, data: DatasetWrapper, **kwargs) -> DatasetWrapper:
        classification = request.GET.get('classification', None)
        if classification is not None:
            classification = Classification.translate(classification.lower())
            data.filter_eq('clasificacion_resumen', classification)
        icu = request.GET.get('icu', None)
        if icu is not None:
            value = 'SI' if icu.lower() == "true" else 'NO'
            data = data.filter_eq('cuidado_intensivo', value)
        respirator = request.GET.get('respirator', None)
        if respirator is not None:
            value = 'SI' if respirator.lower() == "true" else 'NO'
            data = data.filter_eq('asistencia_respiratoria_mecanica', value)
        dead = request.GET.get('dead', None)
        if dead is not None:
            value = 'SI' if dead.lower() == "true" else 'NO'
            data = data.filter_eq('fallecido', value)
        from_date = request.GET.get('from', None)
        if from_date is not None:
            if dead == 'true':
                data = data.filter_ge('fecha_fallecimiento', from_date)
            else:
                data = data.filter_ge('fecha_diagnostico', from_date)
        to_date = request.GET.get('to', None)
        if to_date is not None:
            if dead == 'true':
                data = data.filter_le('fecha_fallecimiento', to_date)
            else:
                data = data.filter_le('fecha_diagnostico', to_date)
        return data

    def create_response(self, request, data: DatasetWrapper, **kwargs) -> Response:
        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 1000)
        paginator = Paginator(data.dataset, per_page)
        return Response(DatasetSerializer(paginator.page(page), many=True).data)

    @swagger_auto_schema(
        manual_parameters=[
            Parameter("icu", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            Parameter("dead", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            Parameter("respirator", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            ClassificationParameter(),
            DateParameter("from"),
            DateParameter("to"),
            Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Used only by /province/{province_slug}/"),
            Parameter("per_page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Used only by /province/{province_slug}/")
        ],
    )
    def get(self, request, **kwargs):
        if not CovidService.has_data():
            return Response({"error": "Database is empty (probably updating).. Try again later"}, 503)
        data = CovidService.get_data()
        data = self.filter_data(request, data, **kwargs)
        data = self.process_data(request, data, **kwargs)
        response = self.create_response(request, data, **kwargs)
        return response


class CountView(ProcessDataView):
    """
    Returns the amount of cases after applying the filters
    """

    renderer_classes = [JSONRenderer, ]

    def create_response(self, request, data: DatasetWrapper, **kwargs) -> Response:
        count = CountModel(data)
        return Response(CountSerializer(count).data)


# --- PROVINCE VIEWS --- #

class ProvinceListView(ProcessDataView):
    """
    Returns the cases for the given province
    """

    def process_data(self, request, data: DatasetWrapper, province_slug=None, **kwargs) -> DatasetWrapper:
        province = Province.from_slug(province_slug)
        summary = data.filter_eq(
            'carga_provincia_nombre',
            province
        )
        return summary


class ProvinceCountView(ProvinceListView, CountView):
    """
    Returns the amount of cases after applying the filters for the given province
    """
    pass


class ProvinceSummaryView(ProcessDataView):

    def process_data(self, request, data: DatasetWrapper, province_slug=None, **kwargs) -> list:
        start_date = request.GET.get('from', None)
        end_date = request.GET.get('to', None)

        province = Province.from_slug(province_slug)

        province_data = data.filter_eq(
            'carga_provincia_nombre',
            province
        )

        if province:
            summary = CovidService.summary(province_data, start_date, end_date, province_slug)
            return summary

        return []

    def create_response(self, request, data: list, **kwargs) -> Response:
        return Response(SummarySerializer(data, many=True).data)


# --- PROVINCES VIEWS --- #

class ProvincesListView(APIView):
    """
    Returns the provinces with their respective slug
    """

    def get(self, request) -> Response:
        provinces = [Province(slug, province) for slug, province in Province.PROVINCES.items()]
        return Response(ProvinceSerializer(provinces, many=True).data)


# --- LAST UPDATE VIEW --- #

class LastUpdateView(APIView):
    """
    Returns the date that the file was last updated
    """

    def get(self, request, **kwargs):
        if not CovidService.has_data():
            return Response({"error": "Database is empty (probably updating).. Try again later"}, 503)
        data = CovidService.get_data()
        last_update = LastUpdate(data)
        return Response(LastUpdateSerializer(last_update).data)


# --- COUNTRY SUMMARY VIEW --- #

class CountrySummaryView(ProcessDataView):

    def process_data(self, request, data: DatasetWrapper, **kwargs) -> list:
        start_date = request.GET.get('from', None)
        end_date = request.GET.get('to', None)

        summary = CovidService.summary(data, start_date, end_date)
        return summary

    def create_response(self, request, data: list, **kwargs) -> Response:
        return Response(SummarySerializer(data, many=True).data)


# --- METRICS VIEW --- #
class StatsView(APIView):
    """
    Returns the provinces and country stats.
    """

    def get(self, requests):
        if not CovidService.has_data():
            return Response({"error": "Database is empty (probably updating).. Try again later"}, 503)
        data = CovidService.get_data()
        provinces_stats = CovidService.provinces_stats(data)
        return Response(StatsSerializer(provinces_stats, many=True).data)


class ProvinceStatsView(APIView):
    """
    Returns a province stats.
    """
    def get(self, requests, province_slug=None):
        if not CovidService.has_data():
            return Response({"error": "Database is empty (probably updating).. Try again later"}, 503)
        data = CovidService.get_data()
        province_stats = CovidService.province_stats(data, province_slug)
        return Response(StatsSerializer(province_stats).data)
