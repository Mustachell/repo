Inicialmente, si se descarga en ZIP y se extrae el archivo, fallara al usar el comando "Docker-compose up --build" ya que se "crea" otro "repo-master" dentro del original, por lo que lo necesario para correr la aplicacion en la terminal es usar el comando "cd". EJEMPLO :"C: \ Usuarios \ "nombre_usuario" \ "Descargas"\repo-master\repo-master", una vez hecho eso, usar el comando "docker-compose up --build".

En caso de no guardar el archivo en "Descargas", reemplaze con el lugar guardado elegido por usted.

Ahora el caso ideal de uso de la aplicacion de Gestor ly:

1. Entrar en "Importar Datos"
2. Importar un archivo excel, csv, xskx, o un archivo txt en "Seleccionar archivo"
3. Elegir cantidad de hojas que uno requiera en caso de que el archivo tenga mas de una hoja importable (maximo 7)
4. Importar datos.
5. Volver a "Inicio" y elegir "Ver Tablas Importadas". O hacer click en "Ver Tablas Importadas" desde la opciones de arriba.
6. Confirmar que las tablas fueron importadas en "Ver Tablas Importadas"
7. Ver la tabla importada, Revisar que se pueden editar los datos importados, con la accion de "Editar", que se encuentra en la columna final de la tabla.
8. En caso de querer editar un dato especifico, editar el dato y confirmar edición, haciendo click en "Guardar Cambios".
9. Revisar si el dato fue editado, El dato se movera al final de la lista en caso de confirmar una edición, hacer click a "siguiente" hasta llegar al ultimo dato en la lista u aumentar cantidad maxima de registros visibles haciendo click en el número que esta entre donde dice "Mostrar" y "registros"
10. Volver a "Inicio" y elegir "Ver Backups" o hacer click en "Ver Backups" desde las opciones de arriba.
11. Revisar si se creo el backup de la tabla importada en "Ver Backups" que en caso de tener un nombre muy largo (max 63 caracteres), se truncara la parte final con "_bk"
12. Finalmente, confirmar que en el backup no fue cambiado con la edición en caso de que se haya hecho una edición.
