from django.db import models

# Create your models here.

class Personas(models.Model):
    id = models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=20)
    apellidos=models.CharField(max_length=20)
    
    def __str__(self):
       texto = "{0} ({1})"
       return texto.format(self.nombre, self.apellidos) 