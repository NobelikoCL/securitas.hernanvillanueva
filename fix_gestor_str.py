import os
import sys

# Configurar el entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erpseguridad.settings')

import django
django.setup()

# Ahora podemos importar los modelos
from erp.models import GestorCliente

def fix_gestor_str():
    # Abrir el archivo models.py
    models_path = os.path.join(os.path.dirname(__file__), 'erp', 'models.py')
    
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar el método __str__
    old_str = '    def __str__(self):\n        return self.razon_social'
    new_str = '    def __str__(self):\n        return self.nombre'
    
    if old_str in content:
        content = content.replace(old_str, new_str)
        
        # Guardar los cambios
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("¡Método __str__ corregido exitosamente!")
    else:
        print("No se encontró el método __str__ a corregir. Verifica el archivo models.py manualmente.")

if __name__ == "__main__":
    fix_gestor_str()
