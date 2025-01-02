from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponseRedirect
from .models import Personas, Animal, Videojuego
from django.http import HttpResponseRedirect
import pandas as pd
from sqlalchemy import create_engine
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

# Create your views here.

def home(request):
    personasLista = Personas.objects.all()
    # Limpiar cualquier mensaje previo al cargar la página principal
    storage = messages.get_messages(request)
    storage.used = True
    return render(request, "gestionPersonas.html", {"personas": personasLista})

# views.py
from django.shortcuts import render
from .models import Animal

def listar_animales(request):
    animales = Animal.objects.all()  # Obtener todos los animales
    print(animales)  # Verificar que los datos son correctos
    return render(request, 'animales.html', {'animales': animales})  # Pasar los animales al template



def registrarPersona(request):
    if request.method == 'POST':
        def smart_capitalize(text):
            words = text.split()
            return ' '.join(word if any(c.isupper() for c in word) else word.capitalize() for word in words)

        nombre = request.POST['txtNombre']
        apellidos = request.POST['txtApellidos']
        edad = request.POST['numEdad']
        email = request.POST['txtEmail']

        # Validación de nombre y apellidos
        if len(nombre.strip()) < 2 or len(apellidos.strip()) < 2 or not all(c.isalpha() or c.isspace() for c in nombre + apellidos):
            messages.warning(request, 'El nombre y apellidos deben contener al menos 2 letras y solo pueden contener letras')
            context = {
                'personas': Personas.objects.all(),
                'datos_form': {
                    'nombre': nombre,
                    'apellidos': apellidos,
                    'edad': edad,
                    'email': email
                }
            }
            return render(request, 'gestionPersonas.html', context)

        nombre = smart_capitalize(nombre)
        apellidos = smart_capitalize(apellidos)

        # Validación del email
        if '@' not in email or not any(email.endswith(domain) for domain in ['.com', '.net', '.org', '.edu', '.gov']):
            messages.error(request, 'El email debe contener un @ y terminar en .com, .net, .org, .edu o .gov')
            context = {
                'personas': Personas.objects.all(),
                'datos_form': {
                    'nombre': nombre,
                    'apellidos': apellidos,
                    'edad': edad,
                    'email': email
                }
            }
            return render(request, 'gestionPersonas.html', context)

        persona = Personas.objects.create(
            nombre=nombre,
            apellidos=apellidos,
            edad=edad,
            email=email
        )
        messages.success(request, '¡Persona registrada!')
        return redirect('/personas/')
    
    return redirect('/personas/')  # Si no es POST, redirigir a la lista

def registrarAnimal(request):
    def smart_capitalize(text):
        words = text.split()
        return ' '.join(word if any(c.isupper() for c in word) else word.capitalize() for word in words)
    
    nombre = smart_capitalize(request.POST['txtNombre'])
    especie = smart_capitalize(request.POST['txtEspecie'])
    edad = request.POST['numEdad']
    mantenedor = smart_capitalize(request.POST['txtMantenedor'])

    animal = Animal.objects.create(
        nombre=nombre,
        especie=especie,
        edad=edad,
        mantenedor=mantenedor
    )

    messages.success(request, 'Animal añadido exitosamente.')
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
    if '@' not in email or not any(email.endswith(domain) for domain in ['.com', '.net', '.org', '.edu', '.gov']):
        messages.success(request, 'El email debe contener un @ y terminar en .com, .net, .org, .edu o .gov')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    persona = Personas.objects.get(id=id)
    persona.nombre = nombre
    persona.apellidos = apellidos
    persona.edad = edad
    persona.email = email
    persona.save()

    messages.success(request, '¡Persona actualizada!')
    return redirect('home')

def editarAnimal(request):
    def smart_capitalize(text):
        words = text.split()
        return ' '.join(word if any(c.isupper() for c in word) else word.capitalize() for word in words)
    
    id = request.POST['numID']
    nombre = smart_capitalize(request.POST['txtNombre'])
    especie = smart_capitalize(request.POST['txtEspecie'])
    edad = request.POST['numEdad']
    mantenedor = smart_capitalize(request.POST['txtMantenedor'])
    
    animal = Animal.objects.get(id=id)
    animal.nombre = nombre
    animal.especie = especie
    animal.edad = edad
    animal.mantenedor = mantenedor
    animal.save()

    messages.success(request, "El animal ha sido editado con éxito.")
    return redirect('animales')  # Aseguramos que redirija a la página de animales

def eliminacionPersona(request, id):
    persona = Personas.objects.get(id=id)
    persona.delete()
    messages.success(request, '¡Persona eliminada!')
    return redirect('home')  # Cambiado de '/' a 'home'

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
    # Función para capitalizar solo palabras en minúsculas
    def smart_capitalize(text):
        words = text.split()
        return ' '.join(word if any(c.isupper() for c in word) else word.capitalize() for word in words)
    
    nombre = smart_capitalize(request.POST['txtNombre'])
    precio = request.POST['numPrecio']
    consola = smart_capitalize(request.POST['txtConsola'])
    cantidad = int(request.POST['numCantidad'])
    
    # Determinar disponibilidad basado en la cantidad
    disponibilidad = 'sin_stock' if cantidad == 0 else 'ambos'
    
    videojuego = Videojuego.objects.create(
        nombre=nombre,
        precio=precio,
        consola=consola,
        cantidad=cantidad,
        disponibilidad=disponibilidad
    )
    messages.success(request, '¡Videojuego registrado!')
    return redirect('videojuegos')

def edicionVideojuego(request, id):
    videojuego = Videojuego.objects.get(id=id)
    return render(request, "edicionVideojuego.html", {"videojuego": videojuego})

def editarVideojuego(request):
    # Función para capitalizar solo palabras en minúsculas
    def smart_capitalize(text):
        words = text.split()
        return ' '.join(word if any(c.isupper() for c in word) else word.capitalize() for word in words)
    
    id = request.POST['numID']
    nombre = smart_capitalize(request.POST['txtNombre'])
    precio = request.POST['numPrecio']
    consola = smart_capitalize(request.POST['txtConsola'])
    cantidad = int(request.POST['numCantidad'])
    disponibilidad = request.POST.get('selDisponibilidad', 'ambos')

    # Si la cantidad es 0, forzar sin_stock
    if cantidad == 0:
        disponibilidad = 'sin_stock'
    elif cantidad > 0 and disponibilidad == 'sin_stock':
        disponibilidad = 'ambos'

    videojuego = Videojuego.objects.get(id=id)
    videojuego.nombre = nombre
    videojuego.precio = precio
    videojuego.consola = consola
    videojuego.cantidad = cantidad
    videojuego.disponibilidad = disponibilidad
    videojuego.save()

    messages.success(request, '¡Videojuego actualizado!')
    return redirect('videojuegos')

def eliminarVideojuego(request, id):
    videojuego = Videojuego.objects.get(id=id)
    videojuego.delete()

    messages.success(request, 'Videojuego eliminado exitosamente.')
    return redirect("videojuegos")

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def importar_datos_txt(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            file_name = file.name.lower()
            
            # Detectar el tipo de archivo por su extensión
            if file_name.endswith('.csv'):
                # Intentar diferentes delimitadores para CSV
                try:
                    df = pd.read_csv(file, sep=',')
                except:
                    try:
                        df = pd.read_csv(file, sep=';')
                    except:
                        df = pd.read_csv(file, sep='|')
            elif file_name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            elif file_name.endswith('.txt'):
                df = pd.read_csv(file, sep='|')
            else:
                messages.error(request, 'Formato de archivo no soportado. Por favor, use CSV, Excel o TXT.')
                return redirect('importar_personas')
            
            # Generar nombre de tabla
            tabla_nombre = file_name.rsplit('.', 1)[0].lower().replace(' ', '_')
            
            # Crear conexión a la base de datos
            engine = create_engine('postgresql://postgres:123@db:5432/server')
            
            # Guardar el DataFrame en la base de datos
            df.to_sql(tabla_nombre, engine, if_exists='replace', index=False)
            
            # Guardar el nombre de la tabla en la sesión
            request.session['ultima_tabla'] = tabla_nombre
            
            messages.success(request, f'¡Archivo {file.name} importado exitosamente!')
            return redirect('ver_datos_importados')
            
        except Exception as e:
            messages.error(request, f'Error al importar el archivo: {str(e)}')
            return redirect('importar_personas')
    
    return render(request, 'importar_personas.html')

def ver_datos_importados(request):
    try:
        tabla_nombre = request.session.get('ultima_tabla')
        if not tabla_nombre:
            messages.warning(request, 'No hay datos importados para mostrar')
            return render(request, 'ver_datos.html', {'datos': None, 'columnas': None})

        engine = create_engine('postgresql://postgres:123@db:5432/server')
        df = pd.read_sql_table(tabla_nombre, engine)
        
        # Convertir fechas al formato correcto
        for columna in df.columns:
            if df[columna].dtype == 'object':
                try:
                    df[columna] = pd.to_datetime(df[columna]).dt.strftime('%Y-%m-%d')
                except:
                    pass

        # Filtrar datos según búsqueda
        columna_busqueda = request.GET.get('columna')
        texto_busqueda = request.GET.get('busqueda')
        
        if columna_busqueda and texto_busqueda:
            # Convertir a string para poder buscar en cualquier tipo de columna
            df[columna_busqueda] = df[columna_busqueda].astype(str)
            df = df[df[columna_busqueda].str.contains(texto_busqueda, case=False, na=False)]

        datos = df.to_dict('records')
        columnas = df.columns.tolist()
        
        # Paginación con valor por defecto de 5
        items_por_pagina = request.GET.get('items', '5')
        paginator = Paginator(datos, int(items_por_pagina))
        pagina = request.GET.get('pagina', 1)
        datos_paginados = paginator.get_page(pagina)
        
        # Detectar columnas de coordenadas
        coordenadas_columnas = []
        for columna in df.columns:
            muestra = df[columna].dropna().head(1)
            if len(muestra) > 0:
                valor = str(muestra.iloc[0])
                if ',' in valor:
                    try:
                        lat, lng = map(float, valor.split(','))
                        if -90 <= lat <= 90 and -180 <= lng <= 180:
                            coordenadas_columnas.append(columna)
                    except:
                        pass

        return render(request, 'ver_datos.html', {
            'datos': datos_paginados,
            'columnas': columnas,
            'tabla_nombre': tabla_nombre,
            'items_por_pagina': items_por_pagina,
            'coordenadas_columnas': coordenadas_columnas  # Agregar al contexto
        })
        
    except Exception as e:
        messages.error(request, f'Error al cargar los datos: {str(e)}')
        return render(request, 'ver_datos.html', {'datos': None, 'columnas': None})