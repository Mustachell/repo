from django.urls import path
from . import views

    
urlpatterns = [
    path('', views.home),
    path('registrarPersona/', views.registrarPersona),
    path('edicionPersona/<id>', views.edicionPersona),
    path('editarPersona/', views.editarPersona),
    path('eliminacionPersona/<id>', views.eliminarPersona)
]
    
