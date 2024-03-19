from django.contrib import admin

from .models import OnlinerModel
# Register your models here.

class UserAdminModel(admin.ModelAdmin):
    list_display_links = ('id', 'notebook_name',)
    list_editale = ('url', 'notebook_price', 'notebook_description')
    list_display = (
            'id',
            'url',
            'notebook_name',
            'notebook_description',
            'notebook_price',
            'is_discontinued',
            'notebook_all_price_link',
            'parse_datetime',
            'update_datetime',
        )
    list_filter = (
        'notebook_price',
        'parse_datetime',
        'update_datetime',
        'is_discontinued',
    )
    list_per_page = 25
    list_max_show_all = 5000
    ordering = ('notebook_price',)


admin.site.register(OnlinerModel, UserAdminModel)