from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0003_migrar_gestores'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cliente',
            name='gestor_email',
        ),
        migrations.RemoveField(
            model_name='cliente',
            name='gestor_nombre',
        ),
        migrations.RemoveField(
            model_name='cliente',
            name='gestor_telefono',
        ),
    ]
