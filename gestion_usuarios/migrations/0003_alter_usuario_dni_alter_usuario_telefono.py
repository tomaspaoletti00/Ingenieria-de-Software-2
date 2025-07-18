# Generated by Django 5.2.1 on 2025-05-29 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_usuarios', '0002_tokenverificacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='dni',
            field=models.PositiveIntegerField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='telefono',
            field=models.PositiveIntegerField(max_length=20),
        ),
    ]
