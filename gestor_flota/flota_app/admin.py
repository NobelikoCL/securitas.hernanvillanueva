from django.contrib import admin
from .models import Vehiculo, Personal, Instalacion, Turno, AsignacionVehiculo, AsignacionInstalacion, GestionTransporte, CentroCosto

# Registros simples para empezar
admin.site.register(Vehiculo)
admin.site.register(Instalacion)
admin.site.register(Turno)
admin.site.register(AsignacionVehiculo)
admin.site.register(AsignacionInstalacion)
admin.site.register(GestionTransporte)
admin.site.register(CentroCosto)

# Configuración más detallada para Personal si es necesario
class PersonalAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'rut', 'legajo', 'instalacion_trabajo', 'centro_costo', 'usuario')
    search_fields = ('nombre', 'apellido', 'rut', 'legajo')
    list_filter = ('instalacion_trabajo', 'centro_costo', 'acepta_mensajeria_whatsapp')
    # raw_id_fields = ('usuario',) # Útil si hay muchos usuarios

admin.site.register(Personal, PersonalAdmin)
