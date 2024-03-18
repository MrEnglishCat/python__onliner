from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import OnlinerMobel


class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlinerMobel
        fields = (
            'id',
            'url',
            'notebook_name',
            'notebook_description',
            'notebook_price',
            'notebook_all_price_link',
            'parse_datetime',
            'update_datetime',
        )