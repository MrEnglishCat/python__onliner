from django.db import models

# Create your models here.

class OnlinerMobel(models.Model):
    url = models.URLField()
    notebook_name = models.TextField()
    notebook_description = models.TextField()
    notebook_price = models.DecimalField(max_digits=20, decimal_places=4)
    notebook_all_price_link = models.URLField()
    parse_datetime = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Дата парсинга'
    )
    update_datetime = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
        verbose_name='Дата внесения последних изменений'
    )

