from django.urls import path
from . import views

urlpatterns = [
    path('', views.tablero, name='tablero'),
    path('crear/<int:pk>/', views.crear_proyecto, name='crear_proyecto'),
    path('<int:pk>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('<int:pk>/estado/', views.cambiar_estado, name='cambiar_estado'),
]
