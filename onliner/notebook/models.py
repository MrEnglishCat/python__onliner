from django.db import models

# Create your models here.

class OnlinerModel(models.Model):
    url = models.URLField(verbose_name='Ссылка на товар')
    notebook_name = models.TextField(verbose_name='Название товара', null=True)
    notebook_description = models.TextField(verbose_name='Описание товара', null=True)
    notebook_price = models.DecimalField(max_digits=20, decimal_places=4, verbose_name='Цена товара(от)', null=True)
    notebook_all_price_link = models.URLField(verbose_name='Ccылка на всех продавцов', null=True)
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

    def __str__(self):
        return f"{self.notebook_name} | {self.notebook_price}"

    def get_absolute_url(self):
        return self.url

    def get_str(self):
        return f"{self.notebook_price}"

    class Meta:
        verbose_name = 'Ноутбук'
        verbose_name_plural = 'Ноутбуки'
        ordering = ('notebook_price',)

