import os

# Ruta al archivo models.py
models_path = os.path.join('erp', 'models.py')

# Leer el contenido actual del archivo
with open(models_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar y corregir el método __str__ en la clase GestorCliente
gestor_class_start = None
for i, line in enumerate(lines):
    if 'class GestorCliente' in line:
        gestor_class_start = i
        break

if gestor_class_start is not None:
    # Buscar el método __str__ dentro de la clase GestorCliente
    in_gestor_class = False
    for i in range(gestor_class_start, len(lines)):
        line = lines[i]
        
        # Verificar si estamos dentro de la clase GestorCliente
        if 'class ' in line and i > gestor_class_start:
            break
            
        # Buscar el método __str__
        if 'def __str__' in line:
            # Verificar si la siguiente línea contiene 'return self.razon_social'
            if i + 1 < len(lines) and 'return self.razon_social' in lines[i + 1]:
                # Reemplazar la línea con el valor correcto
                lines[i + 1] = '        return self.nombre\n'
                print("¡Método __str__ corregido exitosamente!")
                break

# Guardar los cambios
with open(models_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
