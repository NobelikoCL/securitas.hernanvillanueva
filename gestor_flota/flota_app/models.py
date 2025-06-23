from django.db import models
from django.contrib.auth.models import User

class Vehiculo(models.Model):
    patente = models.CharField(max_length=10, unique=True, verbose_name="Patente")
    marca = models.CharField(max_length=50, verbose_name="Marca")
    modelo = models.CharField(max_length=50, verbose_name="Modelo")
    año = models.IntegerField(verbose_name="Año")
    kilometraje = models.IntegerField(verbose_name="Kilometraje")
    en_reparacion = models.BooleanField(default=False, verbose_name="En Reparación")

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.patente})"

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

class Personal(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario") # Puede ser nulo si no es un usuario del sistema
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, verbose_name="Apellido")
    legajo = models.CharField(max_length=20, unique=True, verbose_name="Legajo")
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso")
    # Los turnos realizados se calcularán dinámicamente o se almacenarán en AsignacionTurno

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.legajo})"

    def turnos_realizados_mes_actual(self, tipo_turno=None):
        from django.utils import timezone  # Mover imports locales si son específicos de un método
        from datetime import timedelta     # o mantenerlos globales si se usan en varios métodos.
        """
        Calcula los turnos realizados en el mes actual.
        Si tipo_turno no es None, filtra por ese tipo ('D', 'N', 'E').
        """
        hoy = timezone.now()
        inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Para el fin_mes, consideramos el primer día del siguiente mes y restamos un microsegundo,
        # o simplemente filtramos por mes y año.

        turnos_del_mes = self.turnos.filter(
            fecha_hora_inicio__year=inicio_mes.year,
            fecha_hora_inicio__month=inicio_mes.month
        )
        if tipo_turno:
            turnos_del_mes = turnos_del_mes.filter(tipo_turno=tipo_turno)
        return turnos_del_mes.count()

    def turnos_normales_realizados_mes_actual(self):
        """Calcula los turnos normales (Día o Noche) realizados en el mes actual."""
        hoy = timezone.now()
        inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        return self.turnos.filter(
            fecha_hora_inicio__year=inicio_mes.year,
            fecha_hora_inicio__month=inicio_mes.month,
            tipo_turno__in=['D', 'N'] # Filtra por turnos de Día o Noche
        ).count()

    def turnos_extras_realizados_mes_actual(self):
        """Calcula los turnos extras ('E') realizados en el mes actual."""
        return self.turnos_realizados_mes_actual(tipo_turno='E')

    class Meta:
        verbose_name = "Personal"
        verbose_name_plural = "Personal"

class Instalacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Instalación")
    direccion = models.CharField(max_length=200, verbose_name="Dirección")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Instalación"
        verbose_name_plural = "Instalaciones"

class Turno(models.Model):
    TIPO_TURNO_CHOICES = [
        ('D', 'Día (07:00 - 19:00)'),
        ('N', 'Noche (19:00 - 07:00)'),
        ('E', 'Extra'), # Para turnos extras
    ]
    tipo_turno = models.CharField(max_length=1, choices=TIPO_TURNO_CHOICES, verbose_name="Tipo de Turno")
    fecha_hora_inicio = models.DateTimeField(verbose_name="Fecha y Hora de Inicio")
    fecha_hora_fin = models.DateTimeField(verbose_name="Fecha y Hora de Fin")
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="turnos", verbose_name="Personal")
    instalacion = models.ForeignKey(Instalacion, on_delete=models.SET_NULL, null=True, blank=True, related_name="turnos_asignados", verbose_name="Instalación Asignada")

    def __str__(self):
        return f"Turno {self.get_tipo_turno_display()} para {self.personal} el {self.fecha_hora_inicio.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ['fecha_hora_inicio']

class AsignacionVehiculo(models.Model):
    # Para el historial de asignaciones de vehículo al personal
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="asignaciones_vehiculo", verbose_name="Personal")
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name="asignaciones", verbose_name="Vehículo")
    fecha_asignacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Asignación")
    fecha_devolucion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Devolución")
    # Podríamos añadir detalles como el motivo de la asignación o el estado al devolver

    def __str__(self):
        return f"{self.personal} asignado a {self.vehiculo} el {self.fecha_asignacion.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Asignación de Vehículo"
        verbose_name_plural = "Asignaciones de Vehículos"
        ordering = ['-fecha_asignacion']

class AsignacionInstalacion(models.Model):
    # Para el historial de asignaciones de personal a una instalación (si es diferente de un turno específico)
    # O para registrar patrulleros en un lugar específico en un día.
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="asignaciones_instalacion", verbose_name="Personal")
    instalacion = models.ForeignKey(Instalacion, on_delete=models.CASCADE, related_name="personal_asignado_historial", verbose_name="Instalación")
    fecha_inicio_asignacion = models.DateField(verbose_name="Fecha de Inicio de Asignación")
    fecha_fin_asignacion = models.DateField(null=True, blank=True, verbose_name="Fecha de Fin de Asignación")
    # Podríamos añadir el turno o rol específico si es necesario

    def __str__(self):
        return f"{self.personal} asignado a {self.instalacion} desde {self.fecha_inicio_asignacion}"

    class Meta:
        verbose_name = "Asignación de Instalación"
        verbose_name_plural = "Asignaciones de Instalaciones"
        ordering = ['-fecha_inicio_asignacion']


# Modelo para la gestión de transporte (ida y vuelta del personal)
class GestionTransporte(models.Model):
    TIPO_VIAJE_CHOICES = [
        ('I', 'Ida (Casa -> Trabajo)'),
        ('V', 'Vuelta (Trabajo -> Casa)'),
    ]
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="viajes_transporte", verbose_name="Personal")
    vehiculo_asignado = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name="transportes_realizados", verbose_name="Vehículo Asignado")
    turno_asociado = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name="transporte_asociado", verbose_name="Turno Asociado")
    tipo_viaje = models.CharField(max_length=1, choices=TIPO_VIAJE_CHOICES, verbose_name="Tipo de Viaje")
    fecha_hora_programada = models.DateTimeField(verbose_name="Fecha y Hora Programada")
    direccion_origen = models.CharField(max_length=200, verbose_name="Dirección Origen") # Podría autocompletarse desde Personal o Instalación
    direccion_destino = models.CharField(max_length=200, verbose_name="Dirección Destino") # Podría autocompletarse
    confirmado = models.BooleanField(default=False, verbose_name="Viaje Confirmado")
    realizado = models.BooleanField(default=False, verbose_name="Viaje Realizado")

    def __str__(self):
        return f"Transporte ({self.get_tipo_viaje_display()}) para {self.personal} el {self.fecha_hora_programada.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Gestión de Transporte"
        verbose_name_plural = "Gestiones de Transporte"
        ordering = ['-fecha_hora_programada']
