# Generated by Django 2.2.6 on 2021-04-07 11:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created',), 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AlterModelTable(
            name='comment',
            table='Comments',
        ),
    ]