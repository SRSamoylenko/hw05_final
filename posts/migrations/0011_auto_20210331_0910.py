# Generated by Django 2.2.6 on 2021-03-31 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20210324_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(blank=True, help_text='Укажите адрес для страницы группы. Используйте только латиницу, цифры, дефисы и знаки подчёркивания.', max_length=100, unique=True, verbose_name='Адрес страницы с постами группы.'),
        ),
    ]
