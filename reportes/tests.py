"""
Tests para la app Reportes — Santiago Glass
=============================================
Cubre: Vista dashboard, Vista reporte con filtros.
"""
from decimal import Decimal
from django.test import TestCase, Client as HttpClient
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from clientes.models import Cliente
from cotizaciones.models import Cotizacion
from proyectos.models import Proyecto


class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test1234')
        self.http = HttpClient()
        self.http.login(username='test', password='test1234')
        self.cliente = Cliente.objects.create(
            nombre_completo="Dashboard Test", telefono="70000600"
        )

    def test_dashboard_requiere_login(self):
        c = HttpClient()
        resp = c.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 302)

    def test_dashboard_ok(self):
        resp = self.http.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_dashboard_contexto(self):
        resp = self.http.get(reverse('dashboard'))
        ctx = resp.context
        self.assertIn('saludo', ctx)
        self.assertIn('total_cotizaciones', ctx)
        self.assertIn('total_monto', ctx)
        self.assertIn('aprobadas', ctx)
        self.assertIn('proyectos_activos', ctx)
        self.assertIn('meses_labels', ctx)
        self.assertIn('meses_data', ctx)
        self.assertIn('estados_labels', ctx)
        self.assertIn('estados_data', ctx)
        self.assertIn('ultimas', ctx)

    def test_dashboard_saludo(self):
        resp = self.http.get(reverse('dashboard'))
        saludo = resp.context['saludo']
        self.assertIn(saludo, ['Buenos días', 'Buenas tardes', 'Buenas noches'])

    def test_dashboard_con_datos(self):
        cot = Cotizacion.objects.create(
            cliente=self.cliente,
            fecha=timezone.now().date(),
            numero="N°D001-2026",
            total=Decimal("5000"),
            estado='aprobada',
        )
        Proyecto.objects.create(cotizacion=cot, estado='en_instalacion')
        resp = self.http.get(reverse('dashboard'))
        ctx = resp.context
        self.assertEqual(ctx['total_cotizaciones'], 1)
        self.assertEqual(ctx['aprobadas'], 1)
        self.assertEqual(ctx['proyectos_activos'], 1)
        self.assertEqual(float(ctx['total_monto']), 5000.0)

    def test_dashboard_meses_labels_6(self):
        resp = self.http.get(reverse('dashboard'))
        self.assertEqual(len(resp.context['meses_labels']), 6)
        self.assertEqual(len(resp.context['meses_data']), 6)

    def test_dashboard_estados_4(self):
        resp = self.http.get(reverse('dashboard'))
        self.assertEqual(len(resp.context['estados_labels']), 4)
        self.assertEqual(len(resp.context['estados_data']), 4)

    def test_dashboard_ultimas_max_5(self):
        for i in range(7):
            Cotizacion.objects.create(
                cliente=self.cliente,
                fecha=timezone.now().date(),
                numero=f"N°U{i:03d}-2026",
            )
        resp = self.http.get(reverse('dashboard'))
        self.assertLessEqual(len(resp.context['ultimas']), 5)


class ReporteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test1234')
        self.http = HttpClient()
        self.http.login(username='test', password='test1234')
        self.cliente = Cliente.objects.create(
            nombre_completo="Reporte Test", telefono="70000700"
        )
        self.cot1 = Cotizacion.objects.create(
            cliente=self.cliente,
            fecha='2026-06-15',
            numero="N°R001-2026",
            total=Decimal("1000"),
            estado='emitida',
        )
        self.cot2 = Cotizacion.objects.create(
            cliente=self.cliente,
            fecha='2026-07-20',
            numero="N°R002-2026",
            total=Decimal("2000"),
            estado='aprobada',
        )

    def test_reporte_requiere_login(self):
        c = HttpClient()
        resp = c.get(reverse('reporte'))
        self.assertEqual(resp.status_code, 302)

    def test_reporte_sin_filtros(self):
        resp = self.http.get(reverse('reporte'))
        self.assertEqual(resp.status_code, 200)
        ctx = resp.context
        self.assertEqual(ctx['total_cantidad'], 2)
        self.assertEqual(ctx['total_monto'], Decimal("3000"))

    def test_reporte_filtro_fecha_desde(self):
        resp = self.http.get(reverse('reporte'), {'fecha_desde': '2026-07-01'})
        ctx = resp.context
        self.assertEqual(ctx['total_cantidad'], 1)
        self.assertEqual(ctx['total_monto'], Decimal("2000"))

    def test_reporte_filtro_fecha_hasta(self):
        resp = self.http.get(reverse('reporte'), {'fecha_hasta': '2026-06-30'})
        ctx = resp.context
        self.assertEqual(ctx['total_cantidad'], 1)
        self.assertEqual(ctx['total_monto'], Decimal("1000"))

    def test_reporte_filtro_estado(self):
        resp = self.http.get(reverse('reporte'), {'estado': 'aprobada'})
        ctx = resp.context
        self.assertEqual(ctx['total_cantidad'], 1)

    def test_reporte_filtro_combinado(self):
        resp = self.http.get(reverse('reporte'), {
            'fecha_desde': '2026-06-01',
            'fecha_hasta': '2026-06-30',
            'estado': 'emitida',
        })
        ctx = resp.context
        self.assertEqual(ctx['total_cantidad'], 1)
        self.assertEqual(ctx['total_monto'], Decimal("1000"))

    def test_reporte_sin_resultados(self):
        resp = self.http.get(reverse('reporte'), {
            'fecha_desde': '2030-01-01',
        })
        ctx = resp.context
        self.assertEqual(ctx['total_cantidad'], 0)
        self.assertEqual(ctx['total_monto'], 0)
