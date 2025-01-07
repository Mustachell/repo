from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from .models import Personas, Animal, Videojuego, TablaImportada
from django.http import HttpResponseRedirect, JsonResponse
import pandas as pd
from sqlalchemy import create_engine
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db import connection
from urllib.parse import unquote
import logging
from psycopg2.extensions import AsIs, quote_ident
from django.template.response import TemplateResponse

logger = logging.getLogger(__name__)

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
    
    if request.method == 'POST':
        # Actualizar la persona con los datos del formulario
        persona.nombre = request.POST.get('nombre')
        persona.apellidos = request.POST.get('apellidos')
        persona.edad = request.POST.get('edad')
        persona.email = request.POST.get('email')
        persona.save()
        
        # Redirigir a la página de origen
        source = request.POST.get('source', 'gestion')
        if source == 'prueba':
            return redirect('gestionPersonasPrueba')
        else:
            return redirect('gestionPersonas')
    
    return render(request, 'edicionPersona.html', {'persona': persona, 'source': request.GET.get('source', 'gestion')})

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
    consolas = {
        'Nintendo': ['Switch', 'Wii U', '3DS', 'Nintendo 64', 'GameCube', 'Wii', 'Game Boy', 'Game Boy Color', 'Game Boy Advance', 'DS', 'New 3DS'],
        'Xbox': ['Xbox', 'Xbox 360', 'Xbox One', 'Xbox Series S', 'Xbox Series X'],
        'PlayStation': ['PS1', 'PS2', 'PS3', 'PS4', 'PS5', 'PSP', 'PS Vita']
    }
    
    videojuegos = Videojuego.objects.all()
    return render(request, 'videojuegos.html', {
        'videojuegos': videojuegos,
        'consolas': consolas
    })

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
    consolas = {
        'Nintendo': ['Switch', 'Wii U', '3DS', 'Nintendo 64', 'GameCube', 'Wii', 'Game Boy', 'Game Boy Color', 'Game Boy Advance', 'DS', 'New 3DS'],
        'Xbox': ['Xbox', 'Xbox 360', 'Xbox One', 'Xbox Series S', 'Xbox Series X'],
        'PlayStation': ['PS1', 'PS2', 'PS3', 'PS4', 'PS5', 'PSP', 'PS Vita']
    }
    videojuego = Videojuego.objects.get(id=id)
    return render(request, "edicionVideojuego.html", {
        "videojuego": videojuego,
        "consolas": consolas
    })

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
        
        return render(request, 'ver_datos.html', {
            'datos': datos_paginados,
            'columnas': columnas,
            'tabla_nombre': tabla_nombre,
            'items_por_pagina': items_por_pagina,
            'columna_actual': columna_busqueda,
            'busqueda_actual': texto_busqueda
        })
        
    except Exception as e:
        messages.error(request, f'Error al cargar los datos: {str(e)}')
        return render(request, 'ver_datos.html', {'datos': None, 'columnas': None})

def ver_tablas(request):
    # Obtener lista de tablas de la base de datos
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            AND table_name NOT IN (
                'django_migrations',
                'auth_user',
                'django_session',
                'django_content_type',
                'auth_permission',
                'auth_group',
                'auth_group_permissions',
                'django_admin_log',
                'auth_user_groups',
                'auth_user_user_permissions'
            )
            ORDER BY table_name
        """)
        tablas = [row[0] for row in cursor.fetchall()]

    return render(request, 'lista_tablas.html', {'tablas': tablas})

def ver_datos_tabla(request, nombre_tabla):
    try:
        with connection.cursor() as cursor:
            # Verificar si la tabla existe
            cursor.execute("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename = %s
            """, [nombre_tabla])
            
            result = cursor.fetchone()
            
            if not result:
                return render(request, 'verDatosTabla.html', {
                    'error': f'La tabla "{nombre_tabla}" no existe.',
                    'nombre_tabla': nombre_tabla,
                    'columnas': [],
                    'datos': []
                })
            
            # Obtener los datos
            cursor.execute(f'SELECT * FROM "{nombre_tabla}" LIMIT 1000')
            columnas = [desc[0] for desc in cursor.description]
            datos = cursor.fetchall()
            
            # Convertir los datos a un formato más amigable
            datos_formateados = []
            for fila in datos:
                datos_formateados.append([str(valor) if valor is not None else '' for valor in fila])
            
            return render(request, 'verDatosTabla.html', {
                'nombre_tabla': nombre_tabla,
                'columnas': columnas,
                'datos': datos_formateados,
                'error': None
            })
            
    except Exception as e:
        return render(request, 'verDatosTabla.html', {
            'error': str(e),
            'nombre_tabla': nombre_tabla,
            'columnas': [],
            'datos': []
        })

def importar_personas(request):
    if request.method == 'POST' and request.FILES['archivo']:
        archivo = request.FILES['archivo']
        nombre_tabla = request.POST.get('nombre_tabla', '').lower()
        
        if not nombre_tabla:
            nombre_tabla = archivo.name.split('.')[0].lower()

        try:
            # Tu código existente de importación...
            
            # Después de importar exitosamente
            messages.success(request, f'Tabla "{nombre_tabla}" importada correctamente')
            return redirect('ver_datos', nombre_tabla=nombre_tabla)
            
        except Exception as e:
            messages.error(request, f'Error al importar: {str(e)}')
            return redirect('importar_personas')
    
    return render(request, 'importar.html')

def registrar_videojuego(request):
    consolas = {
        'Nintendo': ['Switch', 'Wii U', 'Wii', 'New 3DS', '3DS', 'Gameboy Advance'],
        'Xbox': ['Xbox One', 'Xbox 360', 'Xbox Series X'],
        'PlayStation': ['PS3', 'PS4', 'PS5', 'PS Vita']
    }
    
    if request.method == 'POST':
        # Procesar el formulario aquí
        pass

    return render(request, 'Aplicaciones/Personas/templates/videojuegos.html', {'consolas': consolas})

def gestion_personas_prueba(request):
    # Obtener la lista de personas
    personas = Personas.objects.all()
    
    # Pasar la lista de personas al contexto
    context = {
        'personas': personas
    }
    
    return render(request, 'GestionPersonasPrueba.html', context)

def gestion_personas(request):
    # Obtener la lista de personas
    personas = Personas.objects.all()
    
    # Pasar la lista de personas al contexto
    context = {
        'personas': personas
    }
    
    return render(request, 'gestionPersonas.html', context)

def edicion_persona(request, id):
    persona = get_object_or_404(Personas, id=id)
    
    if request.method == 'POST':
        # Actualizar la persona con los datos del formulario
        persona.nombre = request.POST.get('nombre')
        persona.apellidos = request.POST.get('apellidos')
        persona.edad = request.POST.get('edad')
        persona.email = request.POST.get('email')
        persona.save()
        
        # Redirigir a la página de origen
        source = request.POST.get('source', 'gestion')
        if source == 'prueba':
            return redirect('gestionPersonasPrueba')
        else:
            return redirect('gestionPersonas')
    
    return render(request, 'edicionPersona.html', {'persona': persona, 'source': request.GET.get('source', 'gestion')})

def listar_tablas_importadas(request):
    with connection.cursor() as cursor:
        # Obtener todas las tablas y organizarlas por tipo
        cursor.execute("""
            SELECT tablename, 
                   CASE 
                       WHEN tablename ILIKE 'personas_%' THEN 'Tablas del Sistema'
                       WHEN tablename ILIKE 'auth_%' OR tablename ILIKE 'django_%' THEN 'Tablas de Django'
                       ELSE 'Tablas Importadas'
                   END as tipo
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT IN (
                'django_migrations',
                'auth_user',
                'django_session',
                'django_content_type',
                'auth_permission',
                'auth_group',
                'auth_group_permissions',
                'django_admin_log',
                'auth_user_groups',
                'auth_user_user_permissions'
            )
            ORDER BY tipo, tablename;
        """)
        
        # Organizar las tablas por categorías
        tablas_por_tipo = {}
        for tabla, tipo in cursor.fetchall():
            if tipo not in tablas_por_tipo:
                tablas_por_tipo[tipo] = []
            tablas_por_tipo[tipo].append(tabla)
        
        return render(request, 'listarTablasImportadas.html', {
            'tablas_por_tipo': tablas_por_tipo
        })