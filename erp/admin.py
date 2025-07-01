from django.contrib import admin
from .models import (
    Cliente, Instalacion, Cargo, Personal, TipoVehiculo, Vehiculo,
    TipoIncidencia, Incidencia, Turno
)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'rut', 'get_gestor_principal', 'email_contacto', 'telefono_contacto', 'fecha_creacion')
    search_fields = ('razon_social', 'rut', 'email_contacto')
    list_filter = ('fecha_creacion',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información Básica', {
            'fields': ('razon_social', 'rut')
        }),
        ('Información de Contacto', {
            'fields': ('direccion', 'email_contacto', 'telefono_contacto')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_gestor_principal(self, obj):
        gestor = obj.gestor_principal
        return gestor.nombre if gestor else "Sin gestor principal"
    get_gestor_principal.short_description = 'Gestor Principal'

@admin.register(Instalacion)
class InstalacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cliente', 'direccion', 'activa')
    search_fields = ('nombre', 'direccion')
    list_filter = ('cliente', 'activa')

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'rut', 'cargo', 'instalacion_asignada', 'activo')
    search_fields = ('nombres', 'apellidos', 'rut')
    list_filter = ('cargo', 'instalacion_asignada', 'activo')

@admin.register(TipoVehiculo)
class TipoVehiculoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('patente', 'marca', 'modelo', 'tipo', 'kilometraje', 'en_servicio')
    search_fields = ('patente', 'marca', 'modelo')
    list_filter = ('tipo', 'en_servicio')

@admin.register(TipoIncidencia)
class TipoIncidenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'instalacion', 'tipo_incidencia', 'fecha_hora_reporte', 'estado')
    search_fields = ('titulo', 'descripcion')
    list_filter = ('instalacion', 'tipo_incidencia', 'estado')

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('personal', 'instalacion', 'fecha', 'get_horario', 'tipo_turno', 'estado', 'horas_planificadas', 'horas_reales')
    search_fields = ('personal__nombres', 'personal__apellidos', 'instalacion__nombre')
    list_filter = ('instalacion', 'tipo_turno', 'estado', 'fecha')
    date_hierarchy = 'fecha'
    
    def get_horario(self, obj):
        """Método personalizado para mostrar el horario del turno"""
        if obj.fecha_inicio and obj.fecha_fin:
            return f"{obj.fecha_inicio.strftime('%H:%M')} - {obj.fecha_fin.strftime('%H:%M')}"
        return "-"
    get_horario.short_description = 'Horario'
    get_horario.admin_order_field = 'fecha_inicio'
