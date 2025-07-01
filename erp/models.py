from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

# --- Módulo: Gestión de Instalaciones ---
class CentroCosto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name='centros_costo')

    def __str__(self):
        return f"{self.nombre} ({self.cliente.razon_social})"

    class Meta:
        verbose_name = "Centro de Costo"
        verbose_name_plural = "Centros de Costo"


class Cliente(models.Model):
    # Información básica del cliente
    razon_social = models.CharField('Razón Social', max_length=200, unique=True)
    rut = models.CharField('RUT', max_length=12, unique=True)
    direccion = models.CharField('Dirección', max_length=255, blank=True)
    email_contacto = models.EmailField('Email de Contacto', blank=True)
    telefono_contacto = models.CharField('Teléfono de Contacto', max_length=20, blank=True)
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    @property
    def gestor_principal(self):
        return self.gestores.filter(es_principal=True).first()
    
    def __str__(self):
        return self.razon_social

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['razon_social']


class GestorCliente(models.Model):
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='gestores',
        verbose_name='Cliente'
    )
    nombre = models.CharField('Nombre del Gestor', max_length=200)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    cargo = models.CharField('Cargo', max_length=100, blank=True)
    es_principal = models.BooleanField('¿Gestor Principal?', default=False)
    activo = models.BooleanField('¿Activo?', default=True, 
                               help_text='Indica si el gestor está activo en el sistema')
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    def __str__(self):
        return self.nombre
    
    @property
    def tiene_instalaciones(self):
        return self.instalaciones.exists()
    
    @property
    def cantidad_instalaciones(self):
        return self.instalaciones.count()
    
    @property
    def personal_activo(self):
        return self.personal.filter(activo=True).count()
    
    @property
    def vehiculos_activos(self):
        return Vehiculo.objects.filter(
            requerimientos_cliente__instalacion__cliente=self,
            en_servicio=True
        ).count()

class Instalacion(models.Model):
    # Relaciones
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='instalaciones',
        verbose_name='Cliente'
    )
    gestor = models.ForeignKey(
        'GestorCliente',
        on_delete=models.SET_NULL,
        related_name='instalaciones',
        verbose_name='Gestor Asignado',
        null=True,
        blank=True
    )
    
    # Información básica
    nombre = models.CharField('Nombre de la Instalación', max_length=150)
    direccion = models.TextField('Dirección Completa')
    
    # Contacto local
    contacto_nombre = models.CharField('Nombre del Contacto', max_length=150, blank=True)
    contacto_telefono = models.CharField('Teléfono de Contacto', max_length=20, blank=True)
    contacto_email = models.EmailField('Email de Contacto', blank=True)
    
    # Estado
    activa = models.BooleanField('Activa', default=True)
    
    # Auditoría
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Instalación'
        verbose_name_plural = 'Instalaciones'
        ordering = ['cliente', 'nombre']
        unique_together = [['cliente', 'nombre']]
    
    def __str__(self):
        return f"{self.nombre} - {self.cliente.razon_social}"
    
    @property
    def tiene_requerimientos(self):
        return hasattr(self, 'requerimientos')


class RequerimientosCliente(models.Model):
    """
    Modelo para almacenar los requerimientos de personal y flota para una instalación.
    """
    # Relaciones
    instalacion = models.OneToOneField(
        Instalacion,
        on_delete=models.CASCADE,
        related_name='requerimientos',
        verbose_name='Instalación'
    )
    
    # Configuración de turnos
    sistema_turnos_4x4 = models.BooleanField(
        'Usar sistema 4x4 (4 días trabajo / 4 días libres)', 
        default=True
    )
    
    # Requerimientos de personal
    requiere_personal = models.BooleanField('¿Requiere personal?', default=True)
    personal_requerido = models.PositiveIntegerField(
        'Cantidad de personal requerido',
        default=1,
        validators=[MinValueValidator(0)],
        help_text='Número total de personas necesarias para cubrir la instalación'
    )
    personal_por_turno = models.PositiveIntegerField(
        'Personal por turno',
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Número de personas necesarias por turno'
    )
    
    # Requerimientos de vehículos
    requiere_vehiculos = models.BooleanField('¿Requiere vehículos?', default=False)
    cantidad_vehiculos = models.PositiveIntegerField(
        'Cantidad de vehículos requeridos',
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Número total de vehículos necesarios para la instalación'
    )
    
    # Requisitos especiales
    requisitos_especiales = models.TextField(
        'Requisitos especiales',
        blank=True,
        help_text='Cualquier requisito especial para el personal o vehículos (ej: certificaciones específicas, equipamiento especial, etc.)'
    )
    
    # Notas adicionales
    notas = models.TextField('Notas Adicionales', blank=True)
    
    # Auditoría
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Requerimientos del Cliente'
        verbose_name_plural = 'Requerimientos de Clientes'
    
    def __str__(self):
        return f"Requerimientos para {self.instalacion.nombre}"
    
    @property
    def cliente(self):
        return self.instalacion.cliente
    
    @property
    def personal_asignado(self):
        return self.instalacion.personal_asignado.count()
    
    @property
    def vehiculos_asignados(self):
        return self.vehiculos.count()
    
    @property
    def cumple_requerimientos(self):
        """Verifica si se cumplen los requerimientos de personal y vehículos"""
        if self.requiere_personal and self.personal_asignado == 0:
            return False
        if self.requiere_vehiculos and self.vehiculos_asignados < self.cantidad_vehiculos:
            return False
        return True

    def __str__(self):
        return f"{self.nombre} ({self.cliente.razon_social})"

# --- Módulo: Gestión de Personal ---
class Cargo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Personal(models.Model):
    ESTADO_CIVIL_CHOICES = [
        ('S', 'Soltero/a'), 
        ('C', 'Casado/a'), 
        ('D', 'Divorciado/a'), 
        ('V', 'Viudo/a'),
        ('U', 'Unión Civil'),
        ('O', 'Otro')
    ]
    
    # Relaciones
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='personal',
        verbose_name='Cliente',
        null=True,  # Temporal para la migración
        blank=True  # Temporal para la migración
    )
    usuario = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        help_text="Usuario para acceso al sistema (si aplica)"
    )
    cargo = models.ForeignKey(
        Cargo, 
        on_delete=models.PROTECT,
        verbose_name='Cargo o Función'
    )
    instalacion_asignada = models.ForeignKey(
        Instalacion, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="personal_asignado",
        verbose_name='Instalación Asignada'
    )
    centro_costo = models.ForeignKey(
        CentroCosto, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='personal',
        verbose_name='Centro de Costo'
    )
    
    # Información personal
    nombres = models.CharField('Nombres', max_length=100)
    apellidos = models.CharField('Apellidos', max_length=100)
    rut = models.CharField('RUT', max_length=12, unique=True)
    fecha_nacimiento = models.DateField('Fecha de Nacimiento', blank=True, null=True)
    estado_civil = models.CharField(
        'Estado Civil', 
        max_length=1, 
        choices=ESTADO_CIVIL_CHOICES, 
        blank=True
    )
    
    # Información de contacto
    direccion = models.TextField('Dirección', blank=True)
    telefono = models.CharField('Teléfono', max_length=15)
    telefono_emergencia = models.CharField('Teléfono de Emergencia', max_length=15, blank=True)
    email = models.EmailField('Correo Electrónico', blank=True)
    
    # Información laboral
    fecha_ingreso = models.DateField('Fecha de Ingreso', auto_now_add=True)
    fecha_contratacion = models.DateField('Fecha de Contratación', blank=True, null=True)
    activo = models.BooleanField('Activo', default=True)
    
    # Preferencias de comunicación
    acepta_whatsapp = models.BooleanField(
        'Acepta mensajería WhatsApp', 
        default=False
    )
    
    # Documentos (podrían ser archivos en un modelo aparte)
    licencia_conducir = models.CharField('Licencia de Conducir', max_length=20, blank=True)
    vencimiento_licencia = models.DateField('Vencimiento Licencia', blank=True, null=True)
    
    # Auditoría
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Personal'
        verbose_name_plural = 'Personal'
        ordering = ['apellidos', 'nombres']
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.rut})"
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def antiguedad(self):
        from datetime import date
        if self.fecha_ingreso:
            delta = date.today() - self.fecha_ingreso
            return delta.days
        return 0
    
    @property
    def edad(self):
        from datetime import date
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return None

# --- Módulo: Gestión de Flota ---
class TipoVehiculo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Vehiculo(models.Model):
    TIPO_COMBUSTIBLE = [
        ('G', 'Gasolina'),
        ('D', 'Diésel'),
        ('E', 'Eléctrico'),
        ('H', 'Híbrido'),
        ('GNC', 'Gas Natural Comprimido'),
        ('GLP', 'Gas Licuado de Petróleo'),
    ]
    
    ESTADO_VEHICULO = [
        ('D', 'Disponible'),
        ('M', 'En Mantenimiento'),
        ('R', 'En Reparación'),
        ('B', 'Dado de Baja'),
    ]
    
    # Relaciones
    requerimientos_cliente = models.ForeignKey(
        RequerimientosCliente,
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name='Requerimientos del Cliente',
        null=True,  # Temporal para la migración
        blank=True  # Temporal para la migración
    )
    tipo = models.ForeignKey(
        TipoVehiculo, 
        on_delete=models.PROTECT,
        verbose_name='Tipo de Vehículo'
    )
    instalacion_asignada = models.ForeignKey(
        Instalacion, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="vehiculos_asignados",
        verbose_name='Instalación Asignada'
    )
    
    # Información del vehículo
    patente = models.CharField('Patente', max_length=10, unique=True)
    numero_motor = models.CharField('N° Motor', max_length=50, blank=True)
    numero_chasis = models.CharField('N° Chasis', max_length=50, blank=True)
    marca = models.CharField('Marca', max_length=50)
    modelo = models.CharField('Modelo', max_length=50)
    ano = models.PositiveIntegerField('Año')
    color = models.CharField('Color', max_length=50, blank=True)
    tipo_combustible = models.CharField(
        'Tipo de Combustible',
        max_length=3,
        choices=TIPO_COMBUSTIBLE,
        default='G'
    )
    capacidad_tanque = models.PositiveIntegerField('Capacidad del Tanque (Lts)', default=0)
    
    # Estado y mantenimiento
    estado = models.CharField(
        'Estado',
        max_length=1,
        choices=ESTADO_VEHICULO,
        default='D'
    )
    en_servicio = models.BooleanField('En Servicio', default=True)
    kilometraje = models.PositiveIntegerField('Kilometraje Actual', default=0)
    kilometraje_mantenimiento = models.PositiveIntegerField(
        'Próximo Mantenimiento (km)',
        default=10000,
        help_text='Kilometraje para próximo mantenimiento programado'
    )
    
    # Seguros y documentación
    poliza_seguro = models.CharField('Póliza de Seguro', max_length=50, blank=True)
    vencimiento_seguro = models.DateField('Vencimiento del Seguro', null=True, blank=True)
    revision_tecnica = models.DateField('Vencimiento Revisión Técnica', null=True, blank=True)
    permiso_circulacion = models.DateField('Vencimiento Permiso de Circulación', null=True, blank=True)
    
    # Información adicional
    observaciones = models.TextField('Observaciones', blank=True)
    
    # Auditoría
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['marca', 'modelo', 'patente']
    
    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.patente})"
    
    @property
    def cliente(self):
        if self.requerimientos_cliente:
            return self.requerimientos_cliente.cliente
        return None
    
    @property
    def requiere_mantenimiento(self):
        return self.kilometraje >= self.kilometraje_mantenimiento
    
    @property
    def documentos_por_vencer(self):
        from datetime import date, timedelta
        hoy = date.today()
        proximo_mes = hoy + timedelta(days=30)
        
        documentos = []
        
        if self.vencimiento_seguro and hoy <= self.vencimiento_seguro <= proximo_mes:
            documentos.append(('Seguro', self.vencimiento_seguro))
            
        if self.revision_tecnica and hoy <= self.revision_tecnica <= proximo_mes:
            documentos.append(('Revisión Técnica', self.revision_tecnica))
            
        if self.permiso_circulacion and hoy <= self.permiso_circulacion <= proximo_mes:
            documentos.append(('Permiso de Circulación', self.permiso_circulacion))

    class Meta:
        verbose_name = "Configuración de Turno"
        verbose_name_plural = "Configuraciones de Turnos"

# --- Módulo: Configuración de Turnos ---
class ConfiguracionTurno(models.Model):
    TIPO_TURNO_CHOICES = [
        ('4x4', 'Sistema 4x4 (4 días trabajo / 4 días libres)'),
        ('5x2', 'Sistema 5x2 (5 días trabajo / 2 días libres)'),
        ('6x1', 'Sistema 6x1 (6 días trabajo / 1 día libre)'),
        ('4x3', 'Sistema 4x3 (4 días trabajo / 3 días libres)'),
        ('7x7', 'Sistema 7x7 (7 días trabajo / 7 días libres)'),
        ('otro', 'Otro sistema personalizado'),
    ]
    
    # Relación con RequerimientosCliente
    requerimientos = models.OneToOneField(
        RequerimientosCliente,
        on_delete=models.CASCADE,
        related_name='configuracion_turnos',
        verbose_name='Requerimientos del Cliente',
        null=True,  # Temporal para migración
        blank=True  # Temporal para migración
    )
    
    # Configuración general de turnos
    tipo_turno = models.CharField(
        'Sistema de Turnos',
        max_length=10, 
        choices=TIPO_TURNO_CHOICES, 
        default='4x4',
        help_text='Seleccione el sistema de turnos que aplica para este contrato'
    )
    
    # Horarios de turnos
    turno_mañana_inicio = models.TimeField(
        'Inicio Turno Mañana',
        default='08:00',
        help_text='Hora de inicio del turno mañana (formato HH:MM)'
    )
    turno_mañana_fin = models.TimeField(
        'Fin Turno Mañana',
        default='20:00',
        help_text='Hora de término del turno mañana (formato HH:MM)'
    )
    turno_tarde_inicio = models.TimeField(
        'Inicio Turno Tarde',
        default='20:00',
        help_text='Hora de inicio del turno tarde (formato HH:MM)'
    )
    turno_tarde_fin = models.TimeField(
        'Fin Turno Tarde',
        default='08:00',
        help_text='Hora de término del turno tarde (formato HH:MM)'
    )
    
    # Días de trabajo y descanso
    dias_trabajo = models.PositiveSmallIntegerField(
        'Días de Trabajo',
        default=4,
        help_text='Número de días consecutivos de trabajo'
    )
    dias_descanso = models.PositiveSmallIntegerField(
        'Días de Descanso',
        default=4,
        help_text='Número de días de descanso después del ciclo de trabajo'
    )
    
    # Personal por turno
    personal_requerido_por_turno = models.PositiveSmallIntegerField(
        'Personal Requerido por Turno',
        default=1,
        help_text='Número de personas necesarias por turno'
    )
    
    # Configuraciones adicionales
    incluir_festivos = models.BooleanField(
        'Incluir días festivos',
        default=True,
        help_text='Considerar días festivos en la programación de turnos'
    )
    
    # Notas y observaciones
    notas = models.TextField(
        'Notas Adicionales',
        blank=True,
        help_text='Cualquier información adicional relevante para la configuración de turnos'
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración de Turnos'
        verbose_name_plural = 'Configuraciones de Turnos'
        ordering = ['requerimientos__instalacion__cliente', 'tipo_turno']
    
    def __str__(self):
        if hasattr(self, 'requerimientos') and hasattr(self.requerimientos, 'instalacion'):
            return f"{self.get_tipo_turno_display()} - {self.requerimientos.instalacion.nombre}"
        return f"Configuración de turnos - {self.id}"
    
    @property
    def instalacion(self):
        """Método de compatibilidad hacia atrás"""
        if hasattr(self, 'requerimientos'):
            return self.requerimientos.instalacion
        return None
    
    @property
    def cliente(self):
        """Devuelve el cliente asociado a esta configuración"""
        if hasattr(self, 'requerimientos'):
            return self.requerimientos.cliente
        return None
    
    def duracion_turno_mañana(self):
        """Calcula la duración del turno mañana en horas"""
        from datetime import datetime, date
        if not all([self.turno_mañana_inicio, self.turno_mañana_fin]):
            return 0
            
        # Crear fechas arbitrarias para el cálculo
        hoy = date.today()
        inicio = datetime.combine(hoy, self.turno_mañana_inicio)
        fin = datetime.combine(hoy, self.turno_mañana_fin)
        
        # Si la hora de fin es menor que la de inicio, asumir que es al día siguiente
        if fin <= inicio:
            fin = datetime.combine(hoy.replace(day=hoy.day+1), self.turno_mañana_fin)
        
        diferencia = fin - inicio
        return round(diferencia.total_seconds() / 3600, 2)
    
    def duracion_turno_tarde(self):
        """Calcula la duración del turno tarde en horas"""
        from datetime import datetime, date
        if not all([self.turno_tarde_inicio, self.turno_tarde_fin]):
            return 0
            
        # Crear fechas arbitrarias para el cálculo
        hoy = date.today()
        inicio = datetime.combine(hoy, self.turno_tarde_inicio)
        fin = datetime.combine(hoy, self.turno_tarde_fin)
        
        # Si la hora de fin es menor que la de inicio, asumir que es al día siguiente
        if fin <= inicio:
            fin = datetime.combine(hoy.replace(day=hoy.day+1), self.turno_tarde_fin)
        
        diferencia = fin - inicio
        return round(diferencia.total_seconds() / 3600, 2)

# Usar strings para referencias de modelo que aún no están definidas
class Turno(models.Model):
    """
    Modelo que representa un turno asignado a un miembro del personal en una instalación.
    """
    TIPO_TURNO_CHOICES = [
        ('M', 'Mañana'),
        ('T', 'Tarde'),
        ('N', 'Noche'),
        ('C', 'Completo')
    ]
    
    ESTADO_TURNO_CHOICES = [
        ('P', 'Pendiente'),
        ('E', 'En Curso'),
        ('C', 'Completado'),
        ('A', 'Ausente'),
        ('J', 'Justificado'),
        ('X', 'Cancelado')
    ]
    
    # Relaciones
    personal = models.ForeignKey(
        'Personal',  # Usar string para evitar referencia circular
        on_delete=models.CASCADE, 
        related_name="turnos",
        verbose_name='Personal Asignado'
    )
    instalacion = models.ForeignKey(
        'Instalacion',  # Usar string para evitar referencia circular
        on_delete=models.CASCADE, 
        related_name="turnos",
        verbose_name='Instalación'
    )
    configuracion = models.ForeignKey(
        'ConfiguracionTurno',  # Usar string para evitar referencia circular
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='turnos_asignados',
        verbose_name='Configuración de Turno'
    )
    
    # Fechas y horarios
    fecha = models.DateField('Fecha del Turno', default=timezone.now)
    fecha_inicio = models.DateTimeField('Inicio del Turno')
    fecha_fin = models.DateTimeField('Fin del Turno')
    
    # Información del turno
    tipo_turno = models.CharField(
        'Tipo de Turno',
        max_length=1,
        choices=TIPO_TURNO_CHOICES,
        help_text='Tipo de turno asignado'
    )
    estado = models.CharField(
        'Estado del Turno',
        max_length=1,
        choices=ESTADO_TURNO_CHOICES,
        default='P',
        help_text='Estado actual del turno'
    )
    
    # Registro de horas
    horas_planificadas = models.DecimalField(
        'Horas Planificadas',
        max_digits=5, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Horas planificadas para este turno'
    )
    horas_reales = models.DecimalField(
        'Horas Reales',
        max_digits=5, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Horas reales trabajadas (se calculan automáticamente)'
    )
    
    # Control y auditoría
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='turnos_creados',
        verbose_name='Creado Por'
    )
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    # Notas y observaciones
    notas = models.TextField('Notas Adicionales', blank=True)
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['-fecha', 'fecha_inicio', 'personal']
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['personal']),
            models.Index(fields=['instalacion']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.personal} - {self.get_tipo_turno_display()} - {self.fecha.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        # Calcular horas planificadas si no están definidas
        if not self.horas_planificadas and self.fecha_inicio and self.fecha_fin:
            self.horas_planificadas = round((self.fecha_fin - self.fecha_inicio).total_seconds() / 3600, 2)
        
        # Si no hay horas reales, usar las planificadas
        if not self.horas_reales and self.horas_planificadas:
            self.horas_reales = self.horas_planificadas
        
        # Si el turno está completado y no hay horas reales, calcularlas
        if self.estado == 'C' and not self.horas_reales and self.fecha_inicio and self.fecha_fin:
            self.horas_reales = round((self.fecha_fin - self.fecha_inicio).total_seconds() / 3600, 2)
        
        super().save(*args, **kwargs)
    
    @property
    def cliente(self):
        """Devuelve el cliente asociado a este turno"""
        if hasattr(self, 'instalacion') and hasattr(self.instalacion, 'cliente'):
            return self.instalacion.cliente
        return None
    
    @property
    def duracion(self):
        """Devuelve la duración del turno en horas"""
        if self.fecha_inicio and self.fecha_fin:
            return round((self.fecha_fin - self.fecha_inicio).total_seconds() / 3600, 2)
        return 0
    
    @property
    def esta_activo(self):
        """Indica si el turno está actualmente en curso"""
        now = timezone.now()
        return self.fecha_inicio <= now <= self.fecha_fin
    
    def marcar_como_completado(self, horas_trabajadas=None):
        """Método para marcar el turno como completado"""
        self.estado = 'C'
        if horas_trabajadas is not None:
            self.horas_reales = horas_trabajadas
        self.save()
    
    def esta_superpuesto(self):
        """Verifica si este turno se superpone con otro turno del mismo personal"""
        from django.db.models import Q
        
        return self.__class__.objects.filter(
            personal=self.personal,
            estado__in=['P', 'E'],  # Solo verificar turnos pendientes o en curso
            fecha_inicio__lt=self.fecha_fin,
            fecha_fin__gt=self.fecha_inicio
        ).exclude(pk=self.pk).exists()

# --- Módulo: Gestión de Incidencias ---
class TipoIncidencia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Incidencia(models.Model):
    ESTADO_CHOICES = [('A', 'Abierta'), ('P', 'En Progreso'), ('C', 'Cerrada')]
    
    titulo = models.CharField(max_length=200)
    instalacion = models.ForeignKey(Instalacion, on_delete=models.PROTECT)
    tipo_incidencia = models.ForeignKey(TipoIncidencia, on_delete=models.PROTECT)
    fecha_hora_reporte = models.DateTimeField(auto_now_add=True)
    fecha_hora_suceso = models.DateTimeField()
    descripcion = models.TextField()
    personal_involucrado = models.ManyToManyField(Personal, blank=True)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='A')
    reportado_por = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"[{self.get_estado_display()}] {self.titulo} - {self.instalacion.nombre}"
