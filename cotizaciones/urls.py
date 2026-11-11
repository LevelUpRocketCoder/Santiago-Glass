from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_cotizaciones, name='lista_cotizaciones'),
    path('nueva/', views.nueva_cotizacion, name='nueva_cotizacion'),
    path('<int:pk>/', views.detalle_cotizacion, name='detalle_cotizacion'),
    path('<int:pk>/salida-articulos/', views.salida_articulos, name='salida_articulos'),
    path('pdf/<int:pk>/', views.pdf_cotizacion, name='pdf_cotizacion'),
    path('word/<int:pk>/', views.word_cotizacion, name='word_cotizacion'),
    path('pdf/<int:pk>/generar/', views.pdf_cotizacion, name='generar_pdf'),
    path('word/<int:pk>/generar/', views.word_cotizacion, name='generar_word'),
    
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/nuevo/', views.nuevo_producto, name='nuevo_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('api/precio_producto/<int:pk>/', views.api_precio_producto, name='api_precio_producto'),
    
    path('diseno/', views.diseno_wizard, name='diseno_wizard'),
    path('api/dibujo/', views.api_dibujo_ventana, name='api_dibujo'),
    path('api/dibujo_ia/', views.api_dibujo_ia, name='api_dibujo_ia'),
]
