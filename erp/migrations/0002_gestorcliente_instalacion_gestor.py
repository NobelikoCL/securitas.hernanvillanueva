from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GestorCliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre del Gestor')),
                ('telefono', models.CharField(blank=True, max_length=20, verbose_name='Teléfono')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('cargo', models.CharField(blank=True, max_length=100, verbose_name='Cargo')),
                ('es_principal', models.BooleanField(default=False, verbose_name='¿Gestor Principal?')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Última Actualización')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gestores', to='erp.cliente', verbose_name='Cliente')),
            ],
            options={
                'verbose_name': 'Gestor de Cliente',
                'verbose_name_plural': 'Gestores de Clientes',
                'ordering': ['-es_principal', 'nombre'],
            },
        ),
        migrations.AddField(
            model_name='instalacion',
            name='gestor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='instalaciones', to='erp.gestorcliente', verbose_name='Gestor Asignado'),
        ),
    ]
