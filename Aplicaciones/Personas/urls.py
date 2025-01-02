from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('personas/', views.home, name='home'),
    path('registrarPersona/', views.registrarPersona, name='registrarPersona'),
    path('edicionPersona/<id>', views.edicionPersona, name='edicionPersona'),
    path('editarPersona/', views.editarPersona, name='editarPersona'),
    path('eliminacionPersona/<id>', views.eliminacionPersona, name='eliminacionPersona'),

    path('animales/', views.listar_animales, name='animales'),
    path('registrarAnimal/', views.registrarAnimal, name='registrarAnimal'),
    path('animales/edicionAnimal/<id>/', views.edicionAnimal, name='edicionAnimal'),
    path('editarAnimal/', views.editarAnimal, name='editarAnimal'),
    path('animales/eliminacionAnimal/<id>', views.eliminarAnimal, name='eliminacionAnimal'),
    
    path('videojuegos/', views.listar_videojuegos, name='videojuegos'),
    path('registrarVideojuego/', views.registrarVideojuego, name='registrarVideojuego'),
    path('videojuegos/edicionVideojuego/<id>/', views.edicionVideojuego, name='edicionVideojuego'),
    path('editarVideojuego/', views.editarVideojuego, name='editarVideojuego'),
    path('videojuegos/eliminacionVideojuego/<id>', views.eliminarVideojuego, name='eliminacionVideojuego'),

    path('importar/', views.importar_datos_txt, name='importar_personas'),
    path('ver-datos/', views.ver_datos_importados, name='ver_datos_importados'),
]

    
