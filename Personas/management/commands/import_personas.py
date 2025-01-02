from django.core.management.base import BaseCommand
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa datos de personas desde un archivo de texto a la base de datos'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Ruta al archivo de texto')

    def handle(self, *args, **options):
        try:
            # Leer el archivo
            df = pd.read_csv(options['file_path'], sep='|')

            # Convertir columnas de fecha
            date_columns = ['FECHA_NACIMIENTO', 'FECHA_DEFUNCION', 'FEC_MATRIMONIO']
            for col in date_columns:
                df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')

            # Convertir columnas numéricas
            numeric_columns = ['RENTA_EFX', 'RENTA_TOTAL_HH']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Crear conexión a la base de datos usando las configuraciones de Django
            engine = create_engine('postgresql://postgres:123@db:5432/server')

            # Convertir el DataFrame a una tabla SQL
            df.to_sql('personas', engine, if_exists='replace', index=False)

            self.stdout.write(self.style.SUCCESS('Datos importados exitosamente'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 