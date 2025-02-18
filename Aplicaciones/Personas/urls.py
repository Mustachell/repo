from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('importar/', views.importar_datos_txt, name='importar_personas'),
    path('obtener-hojas-excel/', views.obtener_hojas_excel, name='obtener_hojas_excel'),
    path('ver-datos/', views.ver_datos_importados, name='ver_datos_importados'),
    
    path('gestionPersonas/', views.gestion_personas, name='gestionPersonas'),

    path('listarTablasImportadas/', views.listar_tablas_importadas, name='listarTablasImportadas'),
    path('verDatosTabla/<str:nombre_tabla>/', views.ver_datos_tabla, name='verDatosTabla'),

    path('contenedoresTablas/', views.listar_contenedores_tablas, name='contenedoresTablas'),
    re_path(r'^editarDatos/(?P<tabla_nombre>[^/]+)/(?P<id>.+)/$', views.editar_datos, name='editar_datos'),
    path('detectar-hojas/', views.detectar_hojas, name='detectar_hojas'),

    path('backups/', views.ver_backups, name='ver_backups'),
    path('backup/<str:nombre_backup>/', views.ver_datos_backup, name='ver_datos_backup'),

    path('actualizar-orden/<str:tabla_nombre>/', views.actualizar_orden_tabla, name='actualizar_orden_tabla'),
    path('descargar_backup/<str:nombre_backup>/', views.descargar_backup, name='descargar_backup'),
]

    