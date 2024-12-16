from django.db import models

# Create your models here.

class Personas(models.Model):
    id = models.CharField(primary_key=True, max_length=2)
    nombre=models.CharField(max_length=20)
    apellidos=models.CharField(max_length=20)
    
    def __str__(self):
       texto = "{0} ({1})"
       return texto.format(self.nombre, self.apellidos) 