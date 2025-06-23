"""
URL configuration for gestor_flota project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include # Asegurarse de que include esté importado
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("flota/", include("flota_app.urls", namespace="flota_app")), # Incluir las URLs de la app
    path("", RedirectView.as_view(url="/flota/vehiculos/", permanent=True)), # Redirigir la raíz a la lista de vehículos
    path("", include("pwa.urls")), # Incluir las URLs de PWA. Este path DEBE ir DESPUES del redirect para que el redirect funcione.
]
