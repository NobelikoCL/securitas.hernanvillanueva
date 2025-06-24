from django.contrib import admin
from .models import Vehiculo, Personal, Instalacion, Turno, AsignacionVehiculo, AsignacionInstalacion, GestionTransporte, CentroCosto, Cliente

# Registros simples para empezar
admin.site.register(Vehiculo)
# admin.site.register(Instalacion) # Se registrará con clase Admin personalizada
admin.site.register(Turno)
admin.site.register(AsignacionVehiculo)
admin.site.register(AsignacionInstalacion)
admin.site.register(GestionTransporte)
# admin.site.register(CentroCosto) # Se registrará con clase Admin personalizada

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'telefono', 'email')
    search_fields = ('nombre', 'rut')

@admin.register(CentroCosto)
class CentroCostoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'cliente')
    search_fields = ('nombre', 'codigo', 'cliente__nombre')
    list_filter = ('cliente',)

@admin.register(Instalacion)
class InstalacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'centro_costo')
    search_fields = ('nombre', 'direccion', 'centro_costo__nombre', 'centro_costo__cliente__nombre')
    list_filter = ('centro_costo__cliente', 'centro_costo')


# Configuración más detallada para Personal si es necesario
class PersonalAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'rut', 'legajo', 'instalacion_trabajo', 'centro_costo', 'usuario')
    search_fields = ('nombre', 'apellido', 'rut', 'legajo')
    list_filter = ('instalacion_trabajo', 'centro_costo', 'acepta_mensajeria_whatsapp')
    # raw_id_fields = ('usuario',) # Útil si hay muchos usuarios

admin.site.register(Personal, PersonalAdmin)
