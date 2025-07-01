from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from .models import Turno, Personal, Incidencia, Vehiculo

def get_current_turns():
    """Obtiene los turnos actuales"""
    now = timezone.now()
    return Turno.objects.filter(
        fecha_inicio__lte=now,
        fecha_fin__gte=now
    )

def get_personal_in_turn():
    """Obtiene el personal que está en turno"""
    return Personal.objects.filter(
        turnos__in=get_current_turns()
    ).distinct()

def get_turns_by_date(date):
    """Obtiene los turnos de una fecha específica"""
    return Turno.objects.filter(
        fecha_inicio__date=date,
        fecha_fin__date=date
    ).order_by('fecha_inicio')

def get_incidencias_abiertas():
    """Obtiene las incidencias abiertas"""
    return Incidencia.objects.filter(
        estado='A'
    ).order_by('-fecha_hora_reporte')[:10]

def get_stats():
    """Obtiene estadísticas generales"""
    return {
        'personal_activo': Personal.objects.filter(activo=True).count(),
        'vehiculos_en_servicio': Vehiculo.objects.filter(en_servicio=True).count(),
        'incidencias_abiertas': Incidencia.objects.filter(estado='A').count(),
        'personal_en_turno': get_personal_in_turn().count()
    }

def get_turns_calendar_data(start_date, end_date):
    """Obtiene datos para el calendario de turnos"""
    turns = Turno.objects.filter(
        Q(fecha_inicio__range=[start_date, end_date]) |
        Q(fecha_fin__range=[start_date, end_date])
    ).select_related('personal', 'instalacion')
    
    return [
        {
            'id': t.id,
            'title': f"{t.personal.nombres} {t.personal.apellidos}",
            'start': t.fecha_inicio.isoformat(),
            'end': t.fecha_fin.isoformat(),
            'color': '#007bff' if t.tipo_turno == 'D' else '#dc3545',
            'instalacion': str(t.instalacion)
        }
        for t in turns
    ]
