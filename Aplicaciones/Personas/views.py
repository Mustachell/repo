from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from .models import Personas, TablaImportada
from django.http import HttpResponseRedirect, JsonResponse
import pandas as pd
from sqlalchemy import create_engine
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db import connection
from urllib.parse import unquote
import logging
from django.template.response import TemplateResponse
import os
from django.apps import apps
import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse
import io
import hashlib

logger = logging.getLogger(__name__)

# Create your views here.

def home(request):
    personas = Personas.objects.all()  # Consultar todas las personas
    return render(request, 'gestionPersonas.html', {'personas': personas})

def index(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tablename 
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
            ORDER BY tablename;
        """)
        tablas = [row[0] for row in cursor.fetchall()]

    return render(request, 'index.html', {'tablas': tablas})

logger = logging.getLogger(__name__)

def crear_backup_tabla(nombre_tabla):
    """Helper function to create a backup of a table"""
    try:
        with connection.cursor() as cursor:
            logger.info(f"Iniciando creación de backup para tabla {nombre_tabla}")
            
            # Truncar el nombre si es necesario para que quepa el sufijo _bk
            max_length = 60  # 63 - 3 caracteres para '_bk'
            nombre_base = nombre_tabla[:max_length] if len(nombre_tabla) > max_length else nombre_tabla
            nombre_backup = f"{nombre_base}_bk"
            
            # Verificar si ya existe un backup
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, [nombre_backup])
            
            if cursor.fetchone()[0]:
                logger.info(f"El backup {nombre_backup} ya existe, no se creará uno nuevo")
                return False
            
            # Verificar si la tabla original existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, [nombre_tabla])
            
            if not cursor.fetchone()[0]:
                logger.error(f"La tabla original {nombre_tabla} no existe")
                return False

            try:
                # Verificar si podemos acceder a la tabla
                cursor.execute(f'SELECT * FROM "{nombre_tabla}" LIMIT 1')
                logger.info(f"Acceso exitoso a la tabla {nombre_tabla}")
            except Exception as e:
                logger.error(f"No se puede acceder a la tabla {nombre_tabla}: {str(e)}")
                return False
            
            try:
                # Obtener estructura de la tabla
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s 
                    ORDER BY ordinal_position
                """, [nombre_tabla])
                columnas = cursor.fetchall()
                logger.info(f"Estructura de tabla obtenida: {len(columnas)} columnas")
                
                if not columnas:
                    logger.error(f"No se encontraron columnas en la tabla {nombre_tabla}")
                    return False
                
                # Crear la tabla de backup con todas las columnas como TEXT
                create_columns = [f'"{col[0]}" TEXT' for col in columnas]
                
                # Crear nueva tabla de backup
                create_sql = f'CREATE TABLE "{nombre_backup}" ({", ".join(create_columns)})'
                cursor.execute(create_sql)
                logger.info(f"Nueva tabla de backup creada")
                
                # Copiar datos manteniendo el orden original
                cursor.execute(f'''
                    INSERT INTO "{nombre_backup}"
                    SELECT * FROM "{nombre_tabla}"
                    ORDER BY ctid
                ''')
                logger.info(f"Datos copiados exitosamente a la tabla de backup")
                
                return True
                
            except Exception as e:
                logger.error(f"Error durante la creación del backup: {str(e)}")
                # Intentar limpiar si algo salió mal
                cursor.execute(f'DROP TABLE IF EXISTS "{nombre_backup}"')
                return False
                
    except Exception as e:
        logger.error(f"Error general en crear_backup_tabla: {str(e)}")
        return False

def ver_backups(request):
    """View to list all backup tables"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name LIKE '%_bk'
                ORDER BY table_name
            """)
            backups = [row[0] for row in cursor.fetchall()]
        
        return render(request, 'ver_backups.html', {'backups': backups})
    except Exception as e:
        messages.error(request, f'Error al cargar los backups: {str(e)}')
        return redirect('index')

def ver_datos_backup(request, nombre_backup):
    """View to display backup table data (read-only)"""
    try:
        with connection.cursor() as cursor:
            # Verify backup exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, [nombre_backup])
            
            if not cursor.fetchone()[0]:
                messages.error(request, f'La tabla de backup "{nombre_backup}" no existe.')
                return redirect('ver_backups')
            
            # Get data from backup table
            cursor.execute(f'SELECT * FROM "{nombre_backup}" ORDER BY ctid')
            columnas = [desc[0] for desc in cursor.description]
            datos = cursor.fetchall()
            
            # Format data for display
            datos_formateados = []
            for fila in datos:
                datos_formateados.append([str(valor) if valor is not None else '' for valor in fila])
            
            return render(request, 'ver_backup.html', {
                'nombre_backup': nombre_backup,
                'columnas': columnas,
                'datos': datos_formateados
            })
            
    except Exception as e:
        messages.error(request, f'Error al cargar los datos del backup: {str(e)}')
        return redirect('ver_backups')

@csrf_exempt
def importar_datos_txt(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            file_name = file.name.lower()
            hojas_seleccionadas = request.POST.getlist('sheets[]')
            tablas_creadas = []
            backups_existentes = []

            if file_name.endswith(('.xls', '.xlsx')):
                try:
                    engine = 'openpyxl' if file_name.endswith('.xlsx') else 'xlrd'
                    excel_file = pd.ExcelFile(file, engine=engine)
                    
                    if len(excel_file.sheet_names) == 1 or not hojas_seleccionadas:
                        # Primera lectura para detectar estructura
                        df_preview = pd.read_excel(
                            file,
                            engine=engine,
                            nrows=2
                        )
                        
                        # Determinar el tipo de archivo basado en el número de columnas
                        num_columns = len(df_preview.columns)
                        
                        if num_columns == 1:
                            # Archivo de una columna - volver al formato original
                            df = pd.read_excel(
                                file,
                                engine=engine,
                                header=None
                            )
                            # Procesar la única columna como CSV
                            data_strings = df[df.columns[0]].astype(str).tolist()
                            reader = csv.reader([data_strings[0]], delimiter=',', quotechar='"')
                            columns = next(reader)
                            processed_rows = []
                            for row in data_strings[1:]:
                                reader = csv.reader([row], delimiter=',', quotechar='"')
                                processed_rows.extend(reader)
                            df = pd.DataFrame(processed_rows, columns=columns)
                        else:
                            # Archivo multicolumna - formato especial
                            df = pd.read_excel(
                                file,
                                engine=engine,
                                header=None
                            )
                            df.columns = df.iloc[0]
                            df = df.iloc[1:]
                        
                        # Limpiar nombres de columnas (sin convertir a minúsculas)
                        df.columns = [str(col).strip().replace(' ', '_') for col in df.columns]
                        
                        tabla_nombre = file_name.rsplit('.', 1)[0].lower().replace(' ', '_')
                        
                        # Guardar en base de datos
                        engine = create_engine('postgresql://postgres:123@db:5432/server')
                        df.to_sql(tabla_nombre, engine, if_exists='replace', index=False)
                        
                        # Crear backup después de crear la tabla
                        if crear_backup_tabla(tabla_nombre):
                            backups_existentes.append(tabla_nombre + "_bk")
                        
                        tablas_creadas.append(tabla_nombre)
                        
                    elif len(hojas_seleccionadas) > 7:
                        messages.error(request, 'No se pueden procesar más de 7 hojas a la vez.')
                        return redirect('importar_personas')
                    else:
                        for hoja in hojas_seleccionadas:
                            df_preview = pd.read_excel(
                                file,
                                sheet_name=hoja,
                                engine='openpyxl',
                                nrows=2
                            )
                            
                            num_columns = len(df_preview.columns)
                            
                            if num_columns == 1:
                                df = pd.read_excel(
                                    file,
                                    sheet_name=hoja,
                                    engine='openpyxl',
                                    header=None
                                )
                                data_strings = df[df.columns[0]].astype(str).tolist()
                                reader = csv.reader([data_strings[0]], delimiter=',', quotechar='"')
                                columns = next(reader)
                                processed_rows = []
                                for row in data_strings[1:]:
                                    reader = csv.reader([row], delimiter=',', quotechar='"')
                                    processed_rows.extend(reader)
                                df = pd.DataFrame(processed_rows, columns=columns)
                            else:
                                df = pd.read_excel(
                                    file,
                                    sheet_name=hoja,
                                    engine='openpyxl',
                                    header=None
                                )
                                df.columns = df.iloc[0]
                                df = df.iloc[1:]
                            
                            df.columns = [str(col).strip().replace(' ', '_') for col in df.columns]
                            
                            tabla_nombre = f"{file_name.rsplit('.', 1)[0]}_{hoja}".lower().replace(' ', '_')
                            
                            # Guardar en base de datos
                            engine = create_engine('postgresql://postgres:123@db:5432/server')
                            df.to_sql(tabla_nombre, engine, if_exists='replace', index=False)
                            
                            # Crear backup después de crear la tabla
                            if crear_backup_tabla(tabla_nombre):
                                backups_existentes.append(tabla_nombre + "_bk")
                            
                            tablas_creadas.append(tabla_nombre)

                except Exception as e:
                    messages.error(request, f'Error al leer el archivo Excel: {str(e)}')
                    return redirect('importar_personas')

            elif file_name.endswith('.csv'):
                try:
                    logger.info(f"Iniciando importación de CSV: {file_name}")
                    
                    # Intentar diferentes encodings
                    encodings = ['utf-8-sig', 'utf-8', 'latin1', 'iso-8859-1', 'cp1252']
                    content = None
                    
                    for encoding in encodings:
                        try:
                            file.seek(0)
                            content = file.read().decode(encoding)
                            logger.info(f"Archivo leído exitosamente con encoding: {encoding}")
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if content is None:
                        raise Exception("No se pudo leer el archivo con ningún encoding")

                    # Intentar detectar el delimitador
                    delimiters = [',', ';', '|', '\t']
                    delimiter = None
                    
                    for delim in delimiters:
                        try:
                            file.seek(0)
                            df = pd.read_csv(
                                io.StringIO(content),
                                sep=delim,
                                dtype=str,
                                nrows=5  # Solo leer primeras filas para prueba
                            )
                            if len(df.columns) > 1:  # Si encontramos más de una columna
                                delimiter = delim
                                logger.info(f"Delimitador detectado: {delimiter}")
                                break
                        except Exception:
                            continue

                    if delimiter is None:
                        raise Exception("No se pudo detectar el delimitador del archivo")

                    # Leer el CSV completo
                    df = pd.read_csv(
                        io.StringIO(content),
                        sep=delimiter,
                        dtype=str,  # Tratar todas las columnas como texto
                        na_filter=False  # No convertir valores vacíos a NaN
                    )
                    
                    # Limpiar nombres de columnas
                    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
                    df.columns = [col.replace('/', '_').replace('\\', '_') for col in df.columns]
                    
                    # Limpiar datos
                    df = df.fillna('')  # Reemplazar NaN con string vacío
                    
                    # Crear nombre de tabla
                    tabla_nombre = file_name.rsplit('.', 1)[0].lower()
                    tabla_nombre = ''.join(c if c.isalnum() or c == '_' else '_' for c in tabla_nombre)
                    logger.info(f"Nombre de tabla a crear: {tabla_nombre}")
                    
                    # Conectar a la base de datos y guardar
                    engine = create_engine('postgresql://postgres:123@db:5432/server')
                    df.to_sql(tabla_nombre, engine, if_exists='replace', index=False)
                    logger.info(f"Tabla {tabla_nombre} creada exitosamente")
                    
                    # Intentar crear backup
                    if crear_backup_tabla(tabla_nombre):
                        backups_existentes.append(tabla_nombre + "_bk")
                    
                    tablas_creadas.append(tabla_nombre)
                    
                except Exception as e:
                    logger.error(f"Error específico al procesar CSV: {str(e)}")
                    messages.error(request, f'Error al procesar CSV: {str(e)}')
                    return redirect('importar_personas')

            elif file_name.endswith('.txt'):
                try:
                    # Similar al CSV, intentar detectar el delimitador
                    txt_sample = file.read(1024).decode('utf-8')
                    file.seek(0)
                    
                    delimiters = ['|', '\t', ',', ';']
                    delimiter = None
                    for d in delimiters:
                        if d in txt_sample:
                            delimiter = d
                            break
                    
                    if not delimiter:
                        delimiter = '|'  # Usar pipe como delimitador por defecto para TXT
                    
                    df = pd.read_csv(
                        file, 
                        sep=delimiter,
                        encoding='utf-8-sig',
                        quotechar='"',
                        escapechar='\\',
                        on_bad_lines='skip'
                    )
                    
                    # Limpiar nombres de columnas
                    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
                    
                    tabla_nombre = file_name.rsplit('.', 1)[0].lower().replace(' ', '_')
                    engine = create_engine('postgresql://postgres:123@db:5432/server')
                    df.to_sql(tabla_nombre, engine, if_exists='replace', index=False)
                    tablas_creadas.append(tabla_nombre)
                except Exception as e:
                    messages.error(request, f'Error al leer el archivo TXT: {str(e)}')
                    return redirect('importar_personas')
            else:
                messages.error(request, 'Formato de archivo no soportado. Por favor, use CSV, Excel o TXT.')
                return redirect('importar_personas')

            # Mensajes de éxito
            for tabla_nombre in tablas_creadas:
                messages.success(request, f'Tabla {tabla_nombre} importada exitosamente')
                if tabla_nombre + "_bk" in backups_existentes:
                    messages.info(request, f'Se creó backup para {tabla_nombre}')
                else:
                    messages.warning(request, f'Ya se encuentra creado el backup para {tabla_nombre}')
                    logger.warning(f'Ya se encuentra creado el backup para {tabla_nombre}')


            request.session['tablas_importadas'] = tablas_creadas
            return redirect('importar_personas')

        except Exception as e:
            logger.error(f'Error en la importación: {str(e)}')
            messages.error(request, f'Error en la importación: {str(e)}')
            return redirect('importar_personas')

    return render(request, 'importar_personas.html')


def ver_datos_importados(request):
    try:
        tablas_importadas = request.session.get('tablas_importadas', [])
        
        if not tablas_importadas:
            messages.warning(request, 'No hay datos importados para mostrar')
            return render(request, 'ver_datos.html', {'datos': None, 'columnas': None})

        todas_las_tablas = []
        engine = create_engine('postgresql://postgres:123@db:5432/server')
        
        for tabla_nombre in tablas_importadas:
            try:
                # Leer la tabla de la base de datos
                df = pd.read_sql_table(tabla_nombre, engine)
                
                # Convertir DataFrame a lista de diccionarios
                datos = df.to_dict('records')
                columnas = df.columns.tolist()
                
                # Paginación
                paginator = Paginator(datos, 10)  # 10 items por página
                pagina = request.GET.get(f'pagina_{tabla_nombre}', 1)
                
                try:
                    datos_paginados = paginator.page(pagina)
                except:
                    datos_paginados = paginator.page(1)
                
                todas_las_tablas.append({
                    'nombre_tabla': tabla_nombre,
                    'datos': datos_paginados,
                    'columnas': columnas,
                    'total_paginas': paginator.num_pages
                })
                
            except Exception as e:
                logger.error(f"Error al cargar la tabla {tabla_nombre}: {str(e)}")
                continue
        
        return render(request, 'ver_datos.html', {
            'todas_las_tablas': todas_las_tablas
        })
        
    except Exception as e:
        logger.error(f"Error al cargar los datos: {str(e)}")
        messages.error(request, f'Error al cargar los datos: {str(e)}')
        return render(request, 'ver_datos.html', {'todas_las_tablas': []})

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
            
            # Verificar si existe la columna 'id'
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s 
                    AND column_name = 'id'
                )
            """, [nombre_tabla])
            tiene_id = cursor.fetchone()[0]
            
            # Obtener los datos ordenados por ctid y preservar el orden con ROW_NUMBER
            cursor.execute(f'''
                WITH numbered_rows AS (
                    SELECT *, ROW_NUMBER() OVER (ORDER BY ctid) as row_order
                    FROM "{nombre_tabla}"
                )
                SELECT * FROM numbered_rows
                ORDER BY row_order;
            ''')
            
            columnas = [desc[0] for desc in cursor.description if desc[0] not in ['ctid', 'row_order']]
            datos = cursor.fetchall()
            
            # Convertir los datos a un formato más amigable, excluyendo row_order
            datos_formateados = []
            for fila in datos:
                datos_formateados.append([str(valor) if valor is not None else '' for valor in fila[:-1]])
            
            return render(request, 'verDatosTabla.html', {
                'nombre_tabla': nombre_tabla,
                'columnas': columnas,
                'datos': datos_formateados,
                'error': None,
                'tiene_id': tiene_id
            })
            
    except Exception as e:
        return render(request, 'verDatosTabla.html', {
            'error': str(e),
            'nombre_tabla': nombre_tabla,
            'columnas': [],
            'datos': [],
            'tiene_id': False
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


def gestion_personas(request):
    # Obtener la lista de personas
    personas = Personas.objects.all()
    
    # Pasar la lista de personas al contexto
    context = {
        'personas': personas
    }
    
    return render(request, 'gestionPersonas.html', context)

def listar_tablas_importadas(request):
    with connection.cursor() as cursor:
        # Fetch tables excluding backups
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            AND tablename NOT LIKE '%(backup)'
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
            ORDER BY tablename;
        """)
        tablas = [row[0] for row in cursor.fetchall()]

    return render(request, 'listarTablasImportadas.html', {'tablas': tablas})

def listar_contenedores_tablas(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE '%_bk'
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
            ORDER BY tablename;
        """)
        tablas = [row[0] for row in cursor.fetchall()]

    return render(request, 'contenedores_tablas.html', {'tablas': tablas})

def editar_datos(request, tabla_nombre, id):
    try:
        with connection.cursor() as cursor:
            # Obtener el nombre de la primera columna
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s 
                ORDER BY ordinal_position 
                LIMIT 1
            """, [tabla_nombre])
            primera_columna = cursor.fetchone()[0]

            # Usar la primera columna para la búsqueda
            cursor.execute(f'SELECT * FROM "{tabla_nombre}" WHERE "{primera_columna}" = %s', [id])
            row = cursor.fetchone()
            if not row:
                messages.error(request, 'Registro no encontrado.')
                return redirect('verDatosTabla', nombre_tabla=tabla_nombre)
            
            columns = [col[0] for col in cursor.description]

        if request.method == 'POST':
            update_data = {}
            for column in columns:
                if column in request.POST:
                    update_data[column] = request.POST.get(column).strip()

            if not update_data:
                messages.error(request, 'No se recibieron datos para actualizar.')
                return redirect('editarDatos', tabla_nombre=tabla_nombre, id=id)

            set_clause = ', '.join([f'"{column}" = %s' for column in update_data.keys()])
            values = list(update_data.values()) + [id]

            try:
                with connection.cursor() as cursor:
                    # Realizar la actualización usando la primera columna
                    cursor.execute(f"""
                        UPDATE "{tabla_nombre}"
                        SET {set_clause}
                        WHERE "{primera_columna}" = %s
                    """, values)

                messages.success(request, 'Datos actualizados correctamente.')
                return redirect('verDatosTabla', nombre_tabla=tabla_nombre)

            except Exception as e:
                messages.error(request, f'Error al actualizar los datos: {str(e)}')
                return redirect('editarDatos', tabla_nombre=tabla_nombre, id=id)

        objeto = dict(zip(columns, row))
        return render(request, 'editar_datos.html', {
            'objeto': objeto,
            'tabla_nombre': tabla_nombre
        })

    except Exception as e:
        messages.error(request, f'Error al cargar los datos: {str(e)}')
        return redirect('verDatosTabla', nombre_tabla=tabla_nombre)

@csrf_exempt
def obtener_hojas_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            xl = pd.ExcelFile(file)
            sheets = xl.sheet_names  # Lista de nombres de hojas

            return JsonResponse({'sheets': sheets})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def detectar_hojas(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            file_name = file.name.lower()

            if file_name.endswith(('.xls', '.xlsx')):
                if file_name.endswith('.xlsx'):
                    xls = pd.ExcelFile(file, engine='openpyxl')
                else:  # .xls
                    xls = pd.ExcelFile(file, engine='xlrd')

                sheets = xls.sheet_names  # Obtener nombres de las hojas

                return JsonResponse({'success': True, 'sheets': sheets})

            else:
                return JsonResponse({'success': False, 'error': 'Formato de archivo no soportado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})


def redirect_with_error(request, error_message):
    messages.error(request, error_message)
    return redirect('importar_personas')  # Adjust the redirect target as needed

def auto_detect_delimiter(file):
    # Read a small portion of the file to detect the delimiter
    sample = file.read(1024).decode('utf-8')
    file.seek(0)  # Reset file pointer to the beginning
    sniffer = csv.Sniffer()
    delimiter = sniffer.sniff(sample).delimiter
    return delimiter

def redirect_with_success(request, success_message):
    messages.success(request, success_message)
    return redirect('importar_personas')  # Adjust the redirect target as needed

@csrf_exempt
def actualizar_orden_tabla(request, tabla_nombre):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                CREATE TABLE temp_table AS
                SELECT * FROM "{tabla_nombre}"
                ORDER BY CAST(id AS INTEGER);
                
                DROP TABLE "{tabla_nombre}";
                ALTER TABLE temp_table RENAME TO "{tabla_nombre}";
            """)
    except Exception as e:
        pass
    
    return redirect('verDatosTabla', nombre_tabla=tabla_nombre)

def descargar_backup(request, nombre_backup):
    try:
        with connection.cursor() as cursor:
            # Verificar si el backup existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, [nombre_backup])
            
            if not cursor.fetchone()[0]:
                messages.error(request, f'El backup "{nombre_backup}" no existe.')
                return redirect('ver_backups')
            
            # Obtener los datos del backup
            cursor.execute(f'SELECT * FROM "{nombre_backup}"')
            datos = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
            
            # Crear el contenido CSV
            output = io.StringIO()
            writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            # Escribir encabezados
            writer.writerow(columnas)
            
            # Escribir datos
            for fila in datos:
                writer.writerow([str(valor) if valor is not None else '' for valor in fila])
            
            # Crear la respuesta HTTP
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{nombre_backup}.csv"'
            
            return response
            
    except Exception as e:
        messages.error(request, f'Error al descargar el backup: {str(e)}')
        return redirect('ver_backups')