from django.db import migrations

def migrar_gestores(apps, schema_editor):
    Cliente = apps.get_model('erp', 'Cliente')
    GestorCliente = apps.get_model('erp', 'GestorCliente')
    
    for cliente in Cliente.objects.all():
        # Verificar si el cliente tiene información de gestor
        if cliente.gestor_nombre:
            # Crear un gestor a partir de los datos antiguos
            GestorCliente.objects.create(
                cliente=cliente,
                nombre=cliente.gestor_nombre,
                telefono=cliente.gestor_telefono or '',
                email=cliente.gestor_email or '',
                es_principal=True,
                cargo='Gestor Principal'  # Valor por defecto
            )

def reverse_migrar_gestores(apps, schema_editor):
    # No hacemos nada en la migración inversa
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0002_gestorcliente_instalacion_gestor'),
    ]

    operations = [
        migrations.RunPython(migrar_gestores, reverse_migrar_gestores),
    ]
