from django.db import models

# Create your models here.

class Personas(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=40)
    localidad = models.CharField(max_length=40)
    edad = models.IntegerField()
    nacionalidad = models.CharField(max_length=40)
    coordenadas = models.CharField(max_length=40)

    
    def __str__(self):
        texto = "{0} {1} ({2})"
        return texto.format(self.nombre, self.localidad, self.edad)

class TablaImportada(models.Model):
    nombre = models.CharField(max_length=255)
    fecha_importacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '%(app_label)s_%(class)s'  # Esto asegura que el nombre de la tabla sea en minúsculas

    def __str__(self):
        return self.nombre
