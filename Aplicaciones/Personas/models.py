from django.db import models

# Create your models here.

class Personas(models.Model):
    id = models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=20)
    apellidos=models.CharField(max_length=20)
    edad = models.IntegerField()
    email = models.EmailField(max_length=100)  # Nuevo campo de email
    
    def __str__(self):
       texto = "{0} {1} ({2})"
       return texto.format(self.nombre, self.apellidos, self.email) 

class Animal(models.Model):
    nombre = models.CharField(max_length=50)  # Nuevo campo
    especie = models.CharField(max_length=50)
    edad = models.IntegerField()
    mantenedor = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Videojuego(models.Model):
    nombre = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=100, decimal_places=2)
    consola = models.CharField(max_length=50)
    cantidad = models.IntegerField()
    disponibilidad = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
