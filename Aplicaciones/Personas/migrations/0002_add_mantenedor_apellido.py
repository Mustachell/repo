from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('Personas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='animal',
            name='mantenedor_apellido',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ] 