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
    id = models.AutoField(primary_key=True)  # Esto asegura que se use un campo ID automático
    especie = models.CharField(max_length=100)  # Campo para la especie
    edad = models.IntegerField()  # Campo para la edad
    mantenedor = models.CharField(max_length=100)  # Campo para el dueño/a

    def __str__(self):
        return f"{self.especie} - {self.mantenedor}"

class Videojuego(models.Model):
    DISPONIBILIDAD_CHOICES = [
        ('tienda', 'Disponible en Tienda'),
        ('envio', 'Solo Envío'),
        ('ambos', 'Tienda y Envío'),
        ('sin_stock', 'Sin Stock'),
    ]

    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField()
    consola = models.CharField(max_length=50)
    cantidad = models.IntegerField(default=0)
    disponibilidad = models.CharField(
        max_length=10, 
        choices=DISPONIBILIDAD_CHOICES, 
        default='ambos'
    )

    def __str__(self):
        return f"{self.nombre} - {self.consola}"
