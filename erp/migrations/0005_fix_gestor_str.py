from django.db import migrations


def fix_gestor_str(apps, schema_editor):
    """
    Corrige el método __str__ del modelo GestorCliente para que devuelva self.nombre
    en lugar de self.razon_social que no existe.
    """
    # No necesitamos hacer nada en la migración de base de datos
    # ya que esto es solo un cambio en el código Python
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0004_remove_cliente_gestor_email_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_gestor_str, migrations.RunPython.noop),
    ]
