"""
Tests para la app Cotizaciones — Santiago Glass
=================================================
Cubre: Modelos (Producto, Cotizacion, ItemCotizacion, Abertura),
       Forms (ProductoForm), Vistas y URLs.
"""
import json
from decimal import Decimal
from django.test import TestCase, Client as HttpClient
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from clientes.models import Cliente
from .models import Producto, Cotizacion, ItemCotizacion, Abertura
from .forms import ProductoForm


# ═══════════════════════════  MODELOS  ═══════════════════════════

class ProductoModelTest(TestCase):
    def setUp(self):
        self.prod = Producto.objects.create(
            nombre="Vidrio Templado 6mm",
            descripcion="Vidrio templado transparente",
            unidad_medida="m2",
            precio_unitario=Decimal("150.00"),
        )

    def test_str(self):
        self.assertIn("Vidrio Templado 6mm", str(self.prod))
        self.assertIn("150", str(self.prod))

    def test_activo_por_defecto(self):
        self.assertTrue(self.prod.activo)

    def test_ordering(self):
        Producto.objects.create(nombre="Aluminio Blanco", precio_unitario=Decimal("80"))
        nombres = list(Producto.objects.values_list('nombre', flat=True))
        self.assertEqual(nombres, sorted(nombres))


class CotizacionModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre_completo="Test Cliente", telefono="70000100"
        )
        self.cotizacion = Cotizacion.objects.create(
            cliente=self.cliente,
            fecha=timezone.now().date(),
        )

    def test_generar_numero(self):
        self.cotizacion.generar_numero()
        self.cotizacion.save()
        year = str(timezone.now().year)
        self.assertTrue(self.cotizacion.numero.startswith("N°"))
        self.assertTrue(self.cotizacion.numero.endswith(year))

    def test_generar_numero_consecutivo(self):
        c1 = Cotizacion(cliente=self.cliente, fecha=timezone.now().date())
        c1.generar_numero()
        c1.save()
        c2 = Cotizacion(cliente=self.cliente, fecha=timezone.now().date())
        c2.generar_numero()
        c2.save()
        # Extraer números
        n1 = int(c1.numero.split('N°')[1].split('-')[0])
        n2 = int(c2.numero.split('N°')[1].split('-')[0])
        self.assertEqual(n2, n1 + 1)

    def test_str(self):
        self.cotizacion.numero = "N°0001-2026"
        self.cotizacion.save()
        self.assertIn("N°0001-2026", str(self.cotizacion))
        self.assertIn("Test Cliente", str(self.cotizacion))

    def test_calcular_total(self):
        self.cotizacion.generar_numero()
        self.cotizacion.save()
        ItemCotizacion.objects.create(
            cotizacion=self.cotizacion,
            descripcion="Item 1",
            cantidad=Decimal("10"),
            precio_unitario=Decimal("100"),
        )
        ItemCotizacion.objects.create(
            cotizacion=self.cotizacion,
            descripcion="Item 2",
            cantidad=Decimal("5"),
            precio_unitario=Decimal("200"),
        )
        self.cotizacion.calcular_total()
        self.assertEqual(self.cotizacion.total, Decimal("2000"))

    def test_estado_por_defecto(self):
        self.assertEqual(self.cotizacion.estado, 'emitida')

    def test_total_letras(self):
        self.cotizacion.total = Decimal("1500")
        self.cotizacion.save()
        letras = self.cotizacion.total_letras
        self.assertIn("MIL", letras)
        self.assertIn("QUINIENTOS", letras)

    def test_ordering(self):
        """Ordenados por -fecha_creacion."""
        c2 = Cotizacion.objects.create(
            cliente=self.cliente, fecha=timezone.now().date(),
            numero="N°9999-2026",
        )
        ids = list(Cotizacion.objects.values_list('id', flat=True))
        self.assertEqual(ids[0], c2.id)  # el más reciente primero


class ItemCotizacionModelTest(TestCase):
    def setUp(self):
        cliente = Cliente.objects.create(nombre_completo="IC Test", telefono="70000200")
        self.cot = Cotizacion.objects.create(
            cliente=cliente, fecha=timezone.now().date(), numero="N°TEST-2026"
        )

    def test_total_item_auto(self):
        item = ItemCotizacion.objects.create(
            cotizacion=self.cot,
            descripcion="Prueba calc",
            cantidad=Decimal("3.5"),
            precio_unitario=Decimal("200"),
        )
        self.assertEqual(item.total_item, Decimal("700.0000"))

    def test_str(self):
        item = ItemCotizacion.objects.create(
            cotizacion=self.cot,
            descripcion="Descripción larga de un item especial",
            cantidad=Decimal("1"),
            precio_unitario=Decimal("50"),
        )
        self.assertIn("Bs", str(item))


class AberturaModelTest(TestCase):
    def test_str(self):
        ab = Abertura.objects.create(ancho_cm=120, alto_cm=150)
        self.assertIn("120", str(ab))
        self.assertIn("150", str(ab))

    def test_defaults(self):
        ab = Abertura.objects.create()
        self.assertEqual(ab.numero_hojas, 2)
        self.assertFalse(ab.con_rejilla)
        self.assertEqual(ab.color_aluminio, 'blanco')
        self.assertEqual(ab.tipo_vidrio, 'simple')
        self.assertEqual(ab.cantidad, 1)


# ═══════════════════════════  FORMULARIO  ═══════════════════════════

class ProductoFormTest(TestCase):
    def test_form_valido(self):
        data = {
            'nombre': 'Vidrio Test',
            'descripcion': 'Desc',
            'unidad_medida': 'm2',
            'precio_unitario': '100.00',
            'activo': True,
        }
        form = ProductoForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_sin_nombre(self):
        data = {
            'nombre': '',
            'descripcion': '',
            'unidad_medida': 'm2',
            'precio_unitario': '100.00',
            'activo': True,
        }
        form = ProductoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_form_sin_precio(self):
        data = {
            'nombre': 'Test',
            'descripcion': '',
            'unidad_medida': 'm2',
            'precio_unitario': '',
            'activo': True,
        }
        form = ProductoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio_unitario', form.errors)


# ═══════════════════════════  VISTAS  ═══════════════════════════

class CotizacionViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test1234')
        self.http = HttpClient()
        self.http.login(username='test', password='test1234')
        self.cliente = Cliente.objects.create(
            nombre_completo="Vista Cot Test", telefono="70000300"
        )
        self.producto = Producto.objects.create(
            nombre="Prod Test", precio_unitario=Decimal("100"),
        )
        self.cotizacion = Cotizacion.objects.create(
            cliente=self.cliente,
            fecha=timezone.now().date(),
            numero="N°0001-2026",
        )
        ItemCotizacion.objects.create(
            cotizacion=self.cotizacion,
            descripcion="Item Vista",
            cantidad=Decimal("2"),
            precio_unitario=Decimal("100"),
        )
        self.cotizacion.calcular_total()

    # ---------- Requiere login ----------
    def test_lista_requiere_login(self):
        c = HttpClient()
        resp = c.get(reverse('lista_cotizaciones'))
        self.assertEqual(resp.status_code, 302)

    # ---------- Lista ----------
    def test_lista_cotizaciones(self):
        resp = self.http.get(reverse('lista_cotizaciones'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "N°0001-2026")

    # ---------- Detalle ----------
    def test_detalle_cotizacion(self):
        resp = self.http.get(reverse('detalle_cotizacion', args=[self.cotizacion.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Item Vista")

    def test_detalle_404(self):
        resp = self.http.get(reverse('detalle_cotizacion', args=[99999]))
        self.assertEqual(resp.status_code, 404)

    # ---------- Nueva cotización ----------
    def test_nueva_cotizacion_get(self):
        resp = self.http.get(reverse('nueva_cotizacion'))
        self.assertEqual(resp.status_code, 200)

    def test_nueva_cotizacion_post_valido(self):
        items = [
            {
                'descripcion': 'Vidrio templado 6mm',
                'producto_id': self.producto.pk,
                'cantidad': '5',
                'precio': '100',
                'color': 'transparente',
                'detalles': 'laminado',
            }
        ]
        resp = self.http.post(reverse('nueva_cotizacion'), {
            'cliente_id': self.cliente.pk,
            'fecha': '2026-01-15',
            'observaciones': 'Prueba',
            'items_json': json.dumps(items),
        })
        self.assertEqual(resp.status_code, 302)
        # Debe existir la nueva cotización
        self.assertTrue(Cotizacion.objects.filter(observaciones='Prueba').exists())

    def test_nueva_cotizacion_sin_items(self):
        resp = self.http.post(reverse('nueva_cotizacion'), {
            'cliente_id': self.cliente.pk,
            'fecha': '2026-01-15',
            'observaciones': '',
            'items_json': '[]',
        })
        self.assertEqual(resp.status_code, 200)  # se queda en el form

    def test_nueva_cotizacion_json_invalido(self):
        resp = self.http.post(reverse('nueva_cotizacion'), {
            'cliente_id': self.cliente.pk,
            'fecha': '2026-01-15',
            'observaciones': '',
            'items_json': 'no-json',
        })
        self.assertEqual(resp.status_code, 302)  # redirect por error

    # ---------- PDF ----------
    def test_pdf_cotizacion(self):
        resp = self.http.get(reverse('generar_pdf', args=[self.cotizacion.pk]))
        # Puede devolver HTML si weasyprint no está instalado, pero no debe dar error
        self.assertIn(resp.status_code, [200])

    # ---------- Word ----------
    def test_word_cotizacion(self):
        resp = self.http.get(reverse('generar_word', args=[self.cotizacion.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp['Content-Type'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    # ---------- API Precio Producto ----------
    def test_api_precio_producto(self):
        resp = self.http.get(reverse('api_precio_producto', args=[self.producto.pk]))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['precio'], '100.00')
        self.assertEqual(data['unidad'], 'm2')

    def test_api_precio_producto_404(self):
        resp = self.http.get(reverse('api_precio_producto', args=[99999]))
        self.assertEqual(resp.status_code, 404)


class ProductoViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test1234')
        self.http = HttpClient()
        self.http.login(username='test', password='test1234')
        self.producto = Producto.objects.create(
            nombre="Aluminio Blanco", precio_unitario=Decimal("80"),
        )

    def test_lista_productos(self):
        resp = self.http.get(reverse('lista_productos'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Aluminio Blanco")

    def test_nuevo_producto_get(self):
        resp = self.http.get(reverse('nuevo_producto'))
        self.assertEqual(resp.status_code, 200)

    def test_nuevo_producto_post(self):
        resp = self.http.post(reverse('nuevo_producto'), {
            'nombre': 'Vidrio Nuevo',
            'descripcion': '',
            'unidad_medida': 'pza',
            'precio_unitario': '250.00',
            'activo': True,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Producto.objects.filter(nombre='Vidrio Nuevo').exists())

    def test_editar_producto_get(self):
        resp = self.http.get(reverse('editar_producto', args=[self.producto.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_editar_producto_post(self):
        resp = self.http.post(reverse('editar_producto', args=[self.producto.pk]), {
            'nombre': 'Aluminio Editado',
            'descripcion': '',
            'unidad_medida': 'm2',
            'precio_unitario': '90.00',
            'activo': True,
        })
        self.assertEqual(resp.status_code, 302)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, 'Aluminio Editado')


class DibujoVentanaViewTest(TestCase):
    """Tests para las APIs de dibujo SVG."""

    def test_api_dibujo_ventana(self):
        resp = self.client.get(reverse('api_dibujo'), {
            'ancho': '200',
            'alto': '150',
            'tipo': 'ventana',
            'estilo': 'corrediza',
            'rejilla': 'true',
            'color': 'blanco',
            'vidrio': 'simple',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'image/svg+xml')
        self.assertIn(b'<svg', resp.content)

    def test_api_dibujo_puerta(self):
        resp = self.client.get(reverse('api_dibujo'), {
            'ancho': '100',
            'alto': '200',
            'tipo': 'puerta',
            'estilo': 'fija',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'<svg', resp.content)

    def test_api_dibujo_ia(self):
        resp = self.client.get(reverse('api_dibujo_ia'), {
            'prompt': 'ventana corrediza blanca 200x150',
            'ancho': '200',
            'alto': '150',
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('svg', data)
        self.assertIn('interpretacion', data)

    def test_diseno_wizard_page(self):
        resp = self.client.get(reverse('diseno_wizard'))
        self.assertEqual(resp.status_code, 200)
