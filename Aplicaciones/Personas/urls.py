from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('personas/', views.home, name='home'),
    path('registrarPersona/', views.registrarPersona, name='registrarPersona'),
    path('edicionPersona/<id>', views.edicionPersona2, name='edicionPersona'),
    path('editarPersona/', views.editarPersona, name='editarPersona'),
    path('eliminacionPersona/<id>', views.eliminacionPersona, name='eliminacionPersona'),

    path('animales/', views.listar_animales, name='animales'),
    path('registrarAnimal/', views.registrarAnimal, name='registrarAnimal'),
    path('animales/edicionAnimal/<id>/', views.edicionAnimal, name='edicionAnimal'),
    path('editarAnimal/', views.editarAnimal, name='editarAnimal'),
    path('animales/eliminacionAnimal/<id>', views.eliminarAnimal, name='eliminacionAnimal'),
    
    path('videojuegos/', views.listar_videojuegos, name='videojuegos'),
    path('registrar/', views.registrar_videojuego, name='registrarVideojuego'),
    path('videojuegos/edicionVideojuego/<id>/', views.edicionVideojuego, name='edicionVideojuego'),
    path('editarVideojuego/', views.editarVideojuego, name='editarVideojuego'),
    path('videojuegos/eliminacionVideojuego/<id>', views.eliminarVideojuego, name='eliminacionVideojuego'),

    path('importar/', views.importar_datos_txt, name='importar_personas'),
    path('obtener-hojas-excel/', views.obtener_hojas_excel, name='obtener_hojas_excel'),
    path('ver-datos/', views.ver_datos_importados, name='ver_datos_importados'),
    
    path('gestionPersonas/', views.gestion_personas, name='gestionPersonas'),
    path('gestionPersonasPrueba/', views.listar_mantenedores_animales, name='gestionPersonasPrueba'),
    path('edicionPersona/<int:id>/', views.edicion_persona, name='edicionPersona'),
    path('listarTablasImportadas/', views.listar_tablas_importadas, name='listarTablasImportadas'),
    path('verDatosTabla/<str:nombre_tabla>/', views.ver_datos_tabla, name='verDatosTabla'),
    path('edicionPersonaAnimal/<int:id>/', views.edicion_persona_animal, name='edicionPersonaAnimal'),
    path('editarPersonaAnimal/', views.editarPersonaAnimal, name='editarPersonaAnimal'),
    path('registrarAnimalPersonaExistente/', views.registrarAnimalPersonaExistente, name='registrarAnimalPersonaExistente'),
    path('contenedoresTablas/', views.listar_contenedores_tablas, name='contenedoresTablas'),
    re_path(r'^editarDatos/(?P<tabla_nombre>[^/]+)/(?P<id>.+)/$', views.editar_datos, name='editar_datos'),
    path('detectar-hojas/', views.detectar_hojas, name='detectar_hojas'),
    path('backups/', views.ver_backups, name='ver_backups'),
    path('backup/<str:nombre_backup>/', views.ver_datos_backup, name='ver_datos_backup'),
]

    

