from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('', views.BaseAPIViewSet)
BASE_PATH_API = 'api/custom'

urlpatterns = [
    path('start_parser', views.start),
    path(f'{BASE_PATH_API}/', include(router.urls))
]