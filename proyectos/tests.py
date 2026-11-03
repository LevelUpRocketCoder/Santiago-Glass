"""
Tests para la app Proyectos — Santiago Glass
=============================================
Cubre: Modelos (Proyecto, HistorialEstado), Vistas (tablero, crear, detalle, cambiar_estado).
"""
import json
from django.test import TestCase, Client as HttpClient
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from clientes.models import Cliente
from cotizaciones.models import Cotizacion
from .models import Proyecto, HistorialEstado


# ═══════════════════════════  MODELOS  ═══════════════════════════

class ProyectoModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre_completo="Proy Test", telefono="70000400"
        )
        self.cotizacion = Cotizacion.objects.create(
            cliente=self.cliente,
            fecha=timezone.now().date(),
            numero="N°P001-2026",
        )
        self.proyecto = Proyecto.objects.create(cotizacion=self.cotizacion)

    def test_estado_por_defecto(self):
        self.assertEqual(self.proyecto.estado, 'aprobado')

    def test_str(self):
        self.assertIn("N°P001-2026", str(self.proyecto))

    def test_color_estado(self):
        self.assertEqual(self.proyecto.color_estado, 'primary')  # aprobado
        self.proyecto.estado = 'entregado'
        self.assertEqual(self.proyecto.color_estado, 'success')
        self.proyecto.estado = 'en_instalacion'
        self.assertEqual(self.proyecto.color_estado, 'warning')
        self.proyecto.estado = 'cotizado'
        self.assertEqual(self.proyecto.color_estado, 'secondary')

    def test_dias_en_estado(self):
        dias = self.proyecto.dias_en_estado
        self.assertIsInstance(dias, int)
        self.assertGreaterEqual(dias, 0)


class HistorialEstadoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='hist', password='test1234')
        cliente = Cliente.objects.create(nombre_completo="Hist Test", telefono="70000401")
        cotizacion = Cotizacion.objects.create(
            cliente=cliente, fecha=timezone.now().date(), numero="N°H001-2026"
        )
        self.proyecto = Proyecto.objects.create(cotizacion=cotizacion)
        self.historial = HistorialEstado.objects.create(
            proyecto=self.proyecto,
            estado_anterior='aprobado',
            estado_nuevo='en_instalacion',
            observacion='Iniciando instalación',
            usuario=self.user,
        )

    def test_historial_creado(self):
        self.assertEqual(HistorialEstado.objects.count(), 1)

    def test_ordering(self):
        """Ordenados por -fecha_cambio."""
        h2 = HistorialEstado.objects.create(
            proyecto=self.proyecto,
            estado_anterior='en_instalacion',
            estado_nuevo='entregado',
            usuario=self.user,
        )
        ids = list(HistorialEstado.objects.values_list('id', flat=True))
        self.assertEqual(ids[0], h2.id)


# ═══════════════════════════  VISTAS  ═══════════════════════════

class ProyectoViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test1234')
        self.http = HttpClient()
        self.http.login(username='test', password='test1234')
        self.cliente = Cliente.objects.create(
            nombre_completo="VP Test", telefono="70000500"
        )
        self.cotizacion = Cotizacion.objects.create(
            cliente=self.cliente,
            fecha=timezone.now().date(),
            numero="N°V001-2026",
        )

    # ---------- Requiere login ----------
    def test_tablero_requiere_login(self):
        c = HttpClient()
        resp = c.get(reverse('tablero'))
        self.assertEqual(resp.status_code, 302)

    # ---------- Tablero ----------
    def test_tablero(self):
        resp = self.http.get(reverse('tablero'))
        self.assertEqual(resp.status_code, 200)

    # ---------- Crear proyecto ----------
    def test_crear_proyecto(self):
        resp = self.http.get(reverse('crear_proyecto', args=[self.cotizacion.pk]))
        self.assertEqual(resp.status_code, 302)
        # Proyecto creado
        self.assertTrue(Proyecto.objects.filter(cotizacion=self.cotizacion).exists())
        # Cotización en estado 'aprobada'
        self.cotizacion.refresh_from_db()
        self.assertEqual(self.cotizacion.estado, 'aprobada')

    def test_crear_proyecto_doble_no_duplica(self):
        """Llamar crear_proyecto dos veces no debe crear dos proyectos."""
        self.http.get(reverse('crear_proyecto', args=[self.cotizacion.pk]))
        self.http.get(reverse('crear_proyecto', args=[self.cotizacion.pk]))
        self.assertEqual(Proyecto.objects.filter(cotizacion=self.cotizacion).count(), 1)

    def test_crear_proyecto_historial(self):
        self.http.get(reverse('crear_proyecto', args=[self.cotizacion.pk]))
        proy = Proyecto.objects.get(cotizacion=self.cotizacion)
        self.assertEqual(proy.historial.count(), 1)

    # ---------- Detalle ----------
    def test_detalle_proyecto(self):
        proy = Proyecto.objects.create(cotizacion=self.cotizacion)
        resp = self.http.get(reverse('detalle_proyecto', args=[proy.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_detalle_404(self):
        resp = self.http.get(reverse('detalle_proyecto', args=[99999]))
        self.assertEqual(resp.status_code, 404)

    # ---------- Cambiar estado ----------
    def test_cambiar_estado_post(self):
        proy = Proyecto.objects.create(cotizacion=self.cotizacion)
        resp = self.http.post(reverse('cambiar_estado', args=[proy.pk]), {
            'estado': 'en_instalacion',
            'observacion': 'Cambio test',
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['ok'])
        proy.refresh_from_db()
        self.assertEqual(proy.estado, 'en_instalacion')

    def test_cambiar_estado_mismo_no_cambia(self):
        proy = Proyecto.objects.create(cotizacion=self.cotizacion)
        resp = self.http.post(reverse('cambiar_estado', args=[proy.pk]), {
            'estado': 'aprobado',  # mismo estado
            'observacion': '',
        })
        data = resp.json()
        self.assertTrue(data['ok'])
        # No se crea historial si el estado no cambió
        self.assertEqual(proy.historial.count(), 0)

    def test_cambiar_estado_get_falla(self):
        proy = Proyecto.objects.create(cotizacion=self.cotizacion)
        resp = self.http.get(reverse('cambiar_estado', args=[proy.pk]))
        data = resp.json()
        self.assertFalse(data['ok'])
