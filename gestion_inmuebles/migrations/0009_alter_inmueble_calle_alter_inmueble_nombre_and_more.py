# Generated by Django 5.2 on 2025-06-01 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_inmuebles', '0008_inmueble_activo_inmueblessimilares_habitaciones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inmueble',
            name='calle',
            field=models.CharField(default='-', max_length=100),
        ),
        migrations.AlterField(
            model_name='inmueble',
            name='nombre',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='inmueble',
            name='precio',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='inmueble',
            name='tiempo',
            field=models.CharField(choices=[('Por_hora', 'Por hora'), ('Por_semana', 'Por semana'), ('Por_mes', 'Por mes'), ('Por_noche', 'Por noche')], default='-'),
        ),
    ]
