# Generated by Django 5.1.4 on 2024-12-12 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Personas',
            fields=[
                ('id', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20)),
                ('apellidos', models.CharField(max_length=20)),
            ],
        ),
    ]
