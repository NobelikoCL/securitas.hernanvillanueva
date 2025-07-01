import os
import sys

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erpseguridad.settings')
import django
django.setup()

from erp.models import GestorCliente

# Actualizar el método __str__ para todos los gestores
def fix_gestor_str():
    # Usar raw SQL para actualizar el método __str__
    with connection.cursor() as cursor:
        # Obtener el ID de la tabla de migraciones
        cursor.execute("""
            SELECT id FROM django_migrations 
            WHERE app = 'erp' AND name = '0002_gestorcliente_instalacion_gestor';
        """)
        migration_id = cursor.fetchone()
        
        if migration_id:
            # Actualizar la migración para incluir el cambio en el método __str__
            cursor.execute("""
                UPDATE django_migrations
                SET name = '0002_gestorcliente_instalacion_gestor_fix_str'
                WHERE id = %s;
            """, [migration_id[0]])
            
            print("Se ha actualizado el nombre de la migración para incluir la corrección del método __str__")
        else:
            print("No se encontró la migración original. Creando una nueva migración...")
            
            # Crear una nueva migración para la corrección
            from django.core.management import call_command
            call_command('makemigrations', 'erp', name='fix_gestor_str', empty=True)
            
            print("Se ha creado una nueva migración para la corrección del método __str__")

if __name__ == "__main__":
    fix_gestor_str()
