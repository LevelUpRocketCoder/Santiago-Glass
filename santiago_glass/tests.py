"""
Tests para santiago_glass/utils.py — Función numero_a_letras
=============================================================
"""
from django.test import TestCase
from santiago_glass.utils import numero_a_letras


class NumeroALetrasTest(TestCase):
    def test_cero(self):
        self.assertEqual(numero_a_letras(0), 'CERO 00/100')

    def test_uno(self):
        self.assertEqual(numero_a_letras(1), 'UN 00/100')

    def test_diez(self):
        self.assertEqual(numero_a_letras(10), 'DIEZ 00/100')

    def test_once(self):
        self.assertEqual(numero_a_letras(11), 'ONCE 00/100')

    def test_quince(self):
        self.assertEqual(numero_a_letras(15), 'QUINCE 00/100')

    def test_veintiuno(self):
        self.assertEqual(numero_a_letras(21), 'VEINTIUN 00/100')

    def test_treinta_y_cinco(self):
        self.assertEqual(numero_a_letras(35), 'TREINTA Y CINCO 00/100')

    def test_cien(self):
        self.assertEqual(numero_a_letras(100), 'CIEN 00/100')

    def test_ciento_uno(self):
        self.assertEqual(numero_a_letras(101), 'CIENTO UN 00/100')

    def test_quinientos(self):
        self.assertEqual(numero_a_letras(500), 'QUINIENTOS 00/100')

    def test_mil(self):
        self.assertEqual(numero_a_letras(1000), 'MIL 00/100')

    def test_mil_quinientos(self):
        result = numero_a_letras(1500)
        self.assertIn('MIL', result)
        self.assertIn('QUINIENTOS', result)

    def test_dos_mil(self):
        result = numero_a_letras(2000)
        self.assertIn('DOS MIL', result)

    def test_un_millon(self):
        result = numero_a_letras(1000000)
        self.assertIn('UN MILLON', result)

    def test_dos_millones(self):
        result = numero_a_letras(2000000)
        self.assertIn('MILLONES', result)

    def test_con_decimales(self):
        result = numero_a_letras(1500.50)
        self.assertIn('MIL', result)
        self.assertIn('50/100', result)

    def test_con_99_centavos(self):
        result = numero_a_letras(0.99)
        self.assertIn('CERO', result)
        self.assertIn('99/100', result)

    def test_valor_invalido(self):
        result = numero_a_letras('abc')
        self.assertEqual(result, 'CERO 00/100')

    def test_none(self):
        result = numero_a_letras(None)
        self.assertEqual(result, 'CERO 00/100')

    def test_decimal_object(self):
        from decimal import Decimal
        result = numero_a_letras(Decimal('2500'))
        self.assertIn('DOS MIL', result)
        self.assertIn('QUINIENTOS', result)

    def test_numero_grande(self):
        result = numero_a_letras(999999)
        self.assertIn('MIL', result)
