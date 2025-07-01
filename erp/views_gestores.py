from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Cliente, GestorCliente
import json

@require_http_methods(["GET"])
def get_gestores_cliente(request):
    """Vista para obtener los gestores de un cliente específico"""
    cliente_id = request.GET.get('cliente_id')
    
    if not cliente_id:
        return JsonResponse({'error': 'Se requiere el ID del cliente'}, status=400)
    
    try:
        cliente = Cliente.objects.get(pk=cliente_id)
        gestores = list(cliente.gestores.values('id', 'nombre', 'cargo'))
        return JsonResponse({'gestores': gestores})
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def gestor_create_ajax(request):
    """Vista para crear un nuevo gestor vía AJAX"""
    try:
        data = request.POST
        cliente_id = data.get('cliente_id')
        
        if not cliente_id:
            return JsonResponse({'success': False, 'error': 'Se requiere el ID del cliente'}, status=400)
        
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        
        # Crear el nuevo gestor
        gestor = GestorCliente.objects.create(
            cliente=cliente,
            nombre=data.get('nombre'),
            cargo=data.get('cargo', ''),
            email=data.get('email', ''),
            telefono=data.get('telefono', ''),
            es_principal=bool(data.get('es_principal') == 'true')
        )
        
        # Si se marcó como principal, asegurarse de que sea el único principal
        if gestor.es_principal:
            GestorCliente.objects.filter(cliente=cliente, es_principal=True).exclude(pk=gestor.pk).update(es_principal=False)
        
        # Obtener la lista actualizada de gestores
        gestores = list(cliente.gestores.values('id', 'nombre', 'cargo'))
        
        return JsonResponse({
            'success': True,
            'gestor_id': gestor.id,
            'gestores': gestores
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
