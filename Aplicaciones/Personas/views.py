from django.shortcuts import render, redirect
from .models import Personas

# Create your views here.

def home(request):
    personasLista = Personas.objects.all()
    return render(request, "gestionPersonas.html", {"personas": personasLista})

def registrarPersona(request):
    id = request.POST['numID']
    nombre = request.POST['txtNombre']
    apellidos = request.POST['txtApellidos']
    
    persona = Personas.objects.create(id=id, nombre=nombre, apellidos=apellidos)
    return redirect('/')

def edicionPersona(request, id):
    persona =Personas.objects.get(id=id)
    return render(request, "edicionPersona.html", {"persona":persona})

def editarPersona(request):
    id = request.POST['numID']
    nombre = request.POST['txtNombre']
    apellidos = request.POST['txtApellidos']
    
    persona = Personas.objects.get(id=id)
    persona.nombre = nombre
    persona.apellidos = apellidos
    persona.save()
    
    return redirect("/")

def eliminarPersona(request, id):
    persona = Personas.objects.get(id=id)
    persona.delete()
    
    return redirect("/")