"""
Tests para la app Clientes — Santiago Glass
=============================================
Cubre: Modelo Cliente, Formulario ClienteForm, Vistas (lista, nuevo, editar, detalle).
"""
from django.test import TestCase, Client as HttpClient
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Cliente
from .forms import ClienteForm


# ─────────────────────────  MODELO  ─────────────────────────
class ClienteModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre_completo="Juan Pérez",
            telefono="70000000",
            email="juan@test.com",
            direccion="Calle Falsa 123",
        )

    def test_str(self):
        self.assertEqual(str(self.cliente), "Juan Pérez")

    def test_activo_por_defecto(self):
        self.assertTrue(self.cliente.activo)

    def test_fecha_registro_auto(self):
        self.assertIsNotNone(self.cliente.fecha_registro)

    def test_ordering(self):
        """Los clientes se ordenan por nombre_completo."""
        Cliente.objects.create(nombre_completo="Ana López", telefono="70000001")
        nombres = list(Cliente.objects.values_list('nombre_completo', flat=True))
        self.assertEqual(nombres, sorted(nombres))

    def test_email_puede_estar_vacio(self):
        c = Cliente.objects.create(nombre_completo="Sin Email", telefono="70000002")
        self.assertEqual(c.email, "")

    def test_direccion_puede_estar_vacia(self):
        c = Cliente.objects.create(nombre_completo="Sin Dir", telefono="70000003")
        self.assertEqual(c.direccion, "")


# ─────────────────────────  FORMULARIO  ─────────────────────────
class ClienteFormTest(TestCase):
    def test_form_valido(self):
        data = {
            'nombre_completo': 'Carlos García',
            'telefono': '70000010',
            'email': 'carlos@test.com',
            'direccion': 'Av. Siempre Viva',
        }
        form = ClienteForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_sin_nombre_invalido(self):
        data = {'telefono': '70000010', 'email': '', 'direccion': ''}
        form = ClienteForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre_completo', form.errors)

    def test_form_sin_telefono_invalido(self):
        data = {'nombre_completo': 'Test', 'email': '', 'direccion': ''}
        form = ClienteForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('telefono', form.errors)

    def test_form_email_invalido(self):
        data = {
            'nombre_completo': 'Test',
            'telefono': '700',
            'email': 'no-es-email',
            'direccion': '',
        }
        form = ClienteForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_widgets_tienen_class(self):
        form = ClienteForm()
        self.assertIn('form-control', form.fields['nombre_completo'].widget.attrs.get('class', ''))


# ─────────────────────────  VISTAS  ─────────────────────────
class ClienteViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test1234')
        self.http = HttpClient()
        self.http.login(username='test', password='test1234')
        self.cliente = Cliente.objects.create(
            nombre_completo="Vista Test", telefono="70000020"
        )

    # ---------- Sin autenticación ----------
    def test_lista_requiere_login(self):
        c = HttpClient()  # sin login
        resp = c.get(reverse('lista_clientes'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)

    # ---------- Lista ----------
    def test_lista_clientes_ok(self):
        resp = self.http.get(reverse('lista_clientes'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Vista Test")

    def test_lista_clientes_busqueda(self):
        resp = self.http.get(reverse('lista_clientes'), {'q': 'Vista'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Vista Test")

    def test_lista_clientes_busqueda_telefono(self):
        resp = self.http.get(reverse('lista_clientes'), {'q': '70000020'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Vista Test")

    def test_lista_clientes_busqueda_sin_resultados(self):
        resp = self.http.get(reverse('lista_clientes'), {'q': 'noexiste9999'})
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "Vista Test")

    # ---------- Nuevo ----------
    def test_nuevo_cliente_get(self):
        resp = self.http.get(reverse('nuevo_cliente'))
        self.assertEqual(resp.status_code, 200)

    def test_nuevo_cliente_post_valido(self):
        resp = self.http.post(reverse('nuevo_cliente'), {
            'nombre_completo': 'Nuevo Creado',
            'telefono': '70000030',
            'email': '',
            'direccion': '',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Cliente.objects.filter(nombre_completo='Nuevo Creado').exists())

    def test_nuevo_cliente_post_invalido(self):
        resp = self.http.post(reverse('nuevo_cliente'), {
            'nombre_completo': '',
            'telefono': '',
            'email': '',
            'direccion': '',
        })
        self.assertEqual(resp.status_code, 200)  # vuelve al form

    # ---------- Editar ----------
    def test_editar_cliente_get(self):
        resp = self.http.get(reverse('editar_cliente', args=[self.cliente.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_editar_cliente_post_valido(self):
        resp = self.http.post(reverse('editar_cliente', args=[self.cliente.pk]), {
            'nombre_completo': 'Editado',
            'telefono': '70000021',
            'email': '',
            'direccion': '',
        })
        self.assertEqual(resp.status_code, 302)
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.nombre_completo, 'Editado')

    # ---------- Detalle ----------
    def test_detalle_cliente(self):
        resp = self.http.get(reverse('detalle_cliente', args=[self.cliente.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Vista Test")

    def test_detalle_cliente_404(self):
        resp = self.http.get(reverse('detalle_cliente', args=[99999]))
        self.assertEqual(resp.status_code, 404)
