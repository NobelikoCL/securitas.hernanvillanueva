from django.test import TestCase
from django.contrib.auth.models import User
from .models import Vehiculo, Personal, Turno, Instalacion
from django.utils import timezone
from datetime import timedelta, date

class VehiculoModelTest(TestCase):
    def setUp(self):
        Vehiculo.objects.create(
            patente="AB123CD",
            marca="Ford",
            modelo="Ranger",
            año=2020,
            kilometraje=50000
        )

    def test_vehiculo_creacion(self):
        vehiculo = Vehiculo.objects.get(patente="AB123CD")
        self.assertEqual(vehiculo.marca, "Ford")
        self.assertEqual(str(vehiculo), "Ford Ranger (AB123CD)")
        self.assertFalse(vehiculo.en_reparacion)

class PersonalModelTurnosTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.personal = Personal.objects.create(
            usuario=self.user,
            nombre="Juan",
            apellido="Perez",
            legajo="JP123",
            fecha_ingreso=date(2020, 1, 1)
        )
        self.instalacion = Instalacion.objects.create(nombre="Sitio A", direccion="Calle Falsa 123")

        # Turnos en el mes actual
        hoy = timezone.now()
        inicio_mes_actual = hoy.replace(day=1)

        Turno.objects.create(
            personal=self.personal,
            tipo_turno='D',
            fecha_hora_inicio=inicio_mes_actual + timedelta(days=1, hours=7),
            fecha_hora_fin=inicio_mes_actual + timedelta(days=1, hours=19),
            instalacion=self.instalacion
        )
        Turno.objects.create(
            personal=self.personal,
            tipo_turno='N',
            fecha_hora_inicio=inicio_mes_actual + timedelta(days=2, hours=19),
            fecha_hora_fin=inicio_mes_actual + timedelta(days=3, hours=7),
            instalacion=self.instalacion
        )
        Turno.objects.create(
            personal=self.personal,
            tipo_turno='E', # Turno extra
            fecha_hora_inicio=inicio_mes_actual + timedelta(days=4, hours=9),
            fecha_hora_fin=inicio_mes_actual + timedelta(days=4, hours=17),
            instalacion=self.instalacion
        )
        Turno.objects.create(
            personal=self.personal,
            tipo_turno='D', # Otro turno normal
            fecha_hora_inicio=inicio_mes_actual + timedelta(days=5, hours=7),
            fecha_hora_fin=inicio_mes_actual + timedelta(days=5, hours=19),
            instalacion=self.instalacion
        )

        # Turno en el mes anterior para asegurar que no se cuente
        mes_anterior = inicio_mes_actual - timedelta(days=15)
        Turno.objects.create(
            personal=self.personal,
            tipo_turno='D',
            fecha_hora_inicio=mes_anterior.replace(day=15, hour=7),
            fecha_hora_fin=mes_anterior.replace(day=15, hour=19),
            instalacion=self.instalacion
        )

    def test_turnos_normales_mes_actual(self):
        self.assertEqual(self.personal.turnos_normales_realizados_mes_actual(), 3) # 2 'D' + 1 'N'

    def test_turnos_extras_mes_actual(self):
        self.assertEqual(self.personal.turnos_extras_realizados_mes_actual(), 1)

    def test_total_turnos_mes_actual(self):
        # Este método no está explícitamente, pero podemos probar el general
        self.assertEqual(self.personal.turnos_realizados_mes_actual(), 4) # 3 normales + 1 extra

class VehiculoListViewTest(TestCase):
    def setUp(self):
        Vehiculo.objects.create(patente="AA000AA", marca="Toyota", modelo="Hilux", año=2021, kilometraje=10000)
        Vehiculo.objects.create(patente="BB111BB", marca="Chevrolet", modelo="S10", año=2019, kilometraje=120000)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/flota/vehiculos/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get('/flota/vehiculos/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flota_app/vehiculo_list.html')
        self.assertTemplateUsed(response, 'pwa_base.html') # Verifica que hereda de la base PWA

    def test_view_displays_all_vehiculos(self):
        response = self.client.get('/flota/vehiculos/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AA000AA")
        self.assertContains(response, "Toyota Hilux")
        self.assertContains(response, "BB111BB")
        self.assertContains(response, "Chevrolet S10")
        self.assertEqual(len(response.context['vehiculos']), 2)
        self.assertIn('titulo_pagina', response.context)
        self.assertEqual(response.context['titulo_pagina'], "Listado de Vehículos")
