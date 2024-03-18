from django.shortcuts import render, HttpResponse
from .parser import run
from rest_framework import viewsets, filters
from .models import OnlinerModel
from .serializers import UserBaseSerializer
# Create your views here.


class BaseAPIViewSet(viewsets.ModelViewSet):
    queryset = OnlinerModel.objects.all()
    serializer_class = UserBaseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = (
            'id',
            'notebook_price',
        )
    ordering_fields = (
            'id',
            'url',
            'notebook_name',
            'notebook_description',
            'notebook_price',
            'notebook_all_price_link',
            'parse_datetime',
            'update_datetime',
        )


def start(requests):
    '''
    url по которому ведется парсинг находится в parser/base_parser URL
    '''
    parser = run.ParserOnlinerPostgres().run()
    return HttpResponse(
        f'''Парсинг прошел!<br><br>
            {'<br>'.join(parser)}
        '''
    )


