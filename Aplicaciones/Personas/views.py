from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Personas, Animal, Videojuego

# Create your views here.

def home(request):
    personasLista = Personas.objects.all()
    return render(request, "gestionPersonas.html", {"personas": personasLista})

# views.py
from django.shortcuts import render
from .models import Animal

def listar_animales(request):
    animales = Animal.objects.all()  # Obtener todos los animales
    print(animales)  # Verificar que los datos son correctos
    return render(request, 'animales.html', {'animales': animales})  # Pasar los animales al template



def registrarPersona(request):
    nombre = request.POST['txtNombre']
    apellidos = request.POST['txtApellidos']
    edad = request.POST['numEdad']
    email = request.POST['txtEmail']

    # Validación del email
    if '@' not in email:
        messages.error(request, 'El email debe contener un @')
        return redirect('/')

    persona = Personas.objects.create(
        nombre=nombre,
        apellidos=apellidos,
        edad=edad,
        email=email
    )
    messages.success(request, '¡Persona registrada!')
    return redirect('/')

def registrarAnimal(request):
    especie = request.POST.get('txtEspecie')
    edad = request.POST.get('numEdad')
    mantenedor = request.POST.get('txtMantenedor')

    # Elimina 'id' de la creación de persona, Django lo generará automáticamente
    animal = Animal.objects.create(especie=especie, edad=edad, mantenedor=mantenedor)

    # Añadir un mensaje de éxito
    messages.success(request, 'Animal añadida exitosamente.')
    return redirect('animales')

def edicionPersona(request, id):
    persona = Personas.objects.get(id=id)
    return render(request, "edicionPersona.html", {"persona": persona})

def edicionAnimal(request, id):
    animal =Animal.objects.get(id=id)
    return render(request, "edicionAnimal.html", {"animal":animal})

def editarPersona(request):
    id = request.POST['numID']
    nombre = request.POST['txtNombre']
    apellidos = request.POST['txtApellidos']
    edad = request.POST['numEdad']
    email = request.POST['txtEmail']

    # Validación del email
    if '@' not in email:
        messages.error(request, 'El email debe contener un @')
        return redirect(f'/edicionPersona/{id}')

    persona = Personas.objects.get(id=id)
    persona.nombre = nombre
    persona.apellidos = apellidos
    persona.edad = edad
    persona.email = email
    persona.save()

    messages.success(request, '¡Persona actualizada!')
    return redirect('/')

def editarAnimal(request):
    id = request.POST['numID']
    especie = request.POST['txtEspecie']
    edad = request.POST['numEdad']
    mantenedor = request.POST['txtMantenedor']
    
    animal = Animal.objects.get(id=id)
    animal.especie = especie
    animal.edad = edad
    animal.mantenedor = mantenedor
    animal.save()

    # Agregar el mensaje de éxito en la sesión
    messages.success(request, "El animal ha sido editado con éxito.")
    
    return redirect("animales")

def eliminarPersona(request, id):
    persona = Personas.objects.get(id=id)
    persona.delete()

    # Añadir mensaje de éxito
    messages.success(request, 'Persona eliminada exitosamente.')
    
    return redirect("/")

def eliminarAnimal(request, id):
    animal = Animal.objects.get(id=id)
    animal.delete()

    # Añadir mensaje de éxito
    messages.success(request, 'Animal eliminado exitosamente.')
    
    return redirect("animales")



def listar_videojuegos(request):
    videojuegos = Videojuego.objects.all()
    return render(request, 'videojuegos.html', {'videojuegos': videojuegos})

def registrarVideojuego(request):
    nombre = request.POST.get('txtNombre')
    precio = int(request.POST.get('numPrecio', 0))  # Convertir a entero
    consola = request.POST.get('txtConsola')
    cantidad = int(request.POST.get('numCantidad', 0))  # Convertir a entero
    disponibilidad = request.POST.get('selDisponibilidad')

    videojuego = Videojuego.objects.create(
        nombre=nombre,
        precio=precio,
        consola=consola,
        cantidad=cantidad,
        disponibilidad=disponibilidad
    )

    messages.success(request, 'Videojuego añadido exitosamente.')
    return redirect('videojuegos')

def edicionVideojuego(request, id):
    videojuego = Videojuego.objects.get(id=id)
    return render(request, "edicionVideojuego.html", {"videojuego": videojuego})

def editarVideojuego(request):
    id = request.POST['numID']
    nombre = request.POST['txtNombre']
    precio = int(request.POST['numPrecio'])  # Convertir a entero
    consola = request.POST['txtConsola']
    cantidad = int(request.POST['numCantidad'])  # Convertir a entero
    disponibilidad = request.POST['selDisponibilidad']
    
    videojuego = Videojuego.objects.get(id=id)
    videojuego.nombre = nombre
    videojuego.precio = precio
    videojuego.consola = consola
    videojuego.cantidad = cantidad
    videojuego.disponibilidad = disponibilidad
    videojuego.save()

    messages.success(request, "El videojuego ha sido editado con éxito.")
    return redirect("videojuegos")

def eliminarVideojuego(request, id):
    videojuego = Videojuego.objects.get(id=id)
    videojuego.delete()

    messages.success(request, 'Videojuego eliminado exitosamente.')
    return redirect("videojuegos")