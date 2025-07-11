from django.urls import path
from . import views

urlpatterns = [
    # Tienda principal
    path('', views.inicio, name='inicio'),
    path('libro/<int:id_libro>/', views.detalle_libro, name='detalle_libro'),
    
    # Autenticación
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),
    
    # Compras
    path('confirmar-compra/<int:id_libro>/', views.confirmar_compra, name='confirmar_compra'),
    path('procesar-compra/<int:id_libro>/', views.procesar_compra, name='procesar_compra'),
    path('pedido-exitoso/<int:id_pedido>/', views.pedido_exitoso, name='pedido_exitoso'),
    path('mis-pedidos/',views.mis_pedidos, name='mis_pedidos'),
    
    # Admin
    path('admin-login/', views.login_admin, name='login_admin'),
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('agregar-libro/', views.admin_agregar_libro, name='agregar_libro'),
    path('editar-libro/<int:id_libro>/', views.admin_editar_libro, name='editar_libro'),
    path('admin_eliminar-libro/<int:id_libro>/', views.admin_eliminar_libro, name='admin_eliminar_libro'),
    path('cambiar-estado/<int:id_pedido>/', views.admin_cambiar_estado_pedido, name='cambiar_estado_pedido'),
]