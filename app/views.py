from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Libro, Categoria, Pedido
from .forms import FormularioLibro
import json

def inicio(request):
    consulta_busqueda = request.GET.get('buscar', '')
    filtro_categoria = request.GET.get('categoria', '')
    
    libros = Libro.objects.all()
    
    if consulta_busqueda:
        libros = libros.filter(
            Q(titulo__icontains=consulta_busqueda) |
            Q(autor__icontains=consulta_busqueda) |
            Q(categoria__nombre__icontains=consulta_busqueda)
        )
    
    if filtro_categoria:
        libros = libros.filter(categoria__nombre=filtro_categoria)
    
    # Paginación
    paginador = Paginator(libros, 12)
    numero_pagina = request.GET.get('pagina')
    libros = paginador.get_page(numero_pagina)
    
    categorias = Categoria.objects.all()
    
    contexto = {
        'libros': libros,
        'categorias': categorias,
        'consulta_busqueda': consulta_busqueda,
        'filtro_categoria': filtro_categoria,
    }
    return render(request, 'index.html', contexto)

def detalle_libro(request, id_libro):
    libro = get_object_or_404(Libro, id=id_libro)
    libros_relacionados = Libro.objects.filter(categoria=libro.categoria).exclude(id=libro.id)[:4]
    
    contexto = {
        'libro': libro,
        'libros_relacionados': libros_relacionados,
    }
    return render(request, 'tienda/detalle_libro.html', contexto)

@login_required
def confirmar_compra(request, id_libro):
    libro = get_object_or_404(Libro, id=id_libro)
    
    if libro.stock <= 0:
        messages.error(request, 'Este libro está agotado.')
        return redirect('detalle_libro', id_libro=libro.id)
    
    cantidad = int(request.GET.get('cantidad', 1))
    
    if cantidad > libro.stock:
        messages.error(request, f'Solo tenemos {libro.stock} unidades disponibles.')
        return redirect('detalle_libro', id_libro=libro.id)
    
    total = libro.precio * cantidad
    
    contexto = {
        'libro': libro,
        'cantidad': cantidad,
        'total': total,
    }
    return render(request, 'tienda/confirmar_compra.html', contexto)

@login_required
def procesar_compra(request, id_libro):
    if request.method == 'POST':
        libro = get_object_or_404(Libro, id=id_libro)
        cantidad = int(request.POST.get('cantidad', 1))
        
        if libro.stock < cantidad:
            messages.error(request, 'Stock insuficiente.')
            return redirect('detalle_libro', id_libro=libro.id)
        
        # Crear el pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            libro=libro,
            cantidad=cantidad,
            precio_unitario=libro.precio,
            total=libro.precio * cantidad,
            notas=request.POST.get('notas', '')
        )
        
        # Reducir stock
        libro.stock -= cantidad
        libro.save()
        
        messages.success(request, '¡Compra realizada con éxito!')
        return redirect('pedido_exitoso', id_pedido=pedido.id)
    
    return redirect('inicio')

def pedido_exitoso(request, id_pedido):
    pedido = get_object_or_404(Pedido, id=id_pedido)
    # Solo el dueño del pedido o admin puede ver
    if request.user != pedido.usuario and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para ver este pedido.')
        return redirect('inicio')
    
    return render(request, 'tienda/pedidos_exitoso.html', {'pedido': pedido})

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user)
    contexto = {
        'pedidos': pedidos,
    }
    return render(request, 'tienda/mis_pedidos.html', contexto)

# Vistas de autenticación
def registro_usuario(request):
    if request.method == 'POST':
        formulario = UserCreationForm(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            username = formulario.cleaned_data.get('username')
            messages.success(request, f'Cuenta creada para {username}. ¡Ya puedes iniciar sesión!')
            return redirect('login_usuario')
    else:
        formulario = UserCreationForm()
    
    return render(request, 'tienda/registro.html', {'formulario': formulario})

def login_usuario(request):
    if request.method == 'POST':
        formulario = AuthenticationForm(request, data=request.POST)
        if formulario.is_valid():
            username = formulario.cleaned_data.get('username')
            password = formulario.cleaned_data.get('password')
            usuario = authenticate(username=username, password=password)
            if usuario is not None:
                login(request, usuario)
                messages.success(request, f'Bienvenido {username}!')
                # Redirigir a la página anterior o inicio
                siguiente = request.GET.get('next', 'inicio')
                return redirect(siguiente)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        formulario = AuthenticationForm()
    
    return render(request, 'tienda/login.html', {'formulario': formulario})

@login_required
def logout_usuario(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('inicio')
def login_admin(request):
    if request.method == 'POST':
        nombre_usuario = request.POST['nombre_usuario']
        contrasena = request.POST['contrasena']
        usuario = authenticate(request, username=nombre_usuario, password=contrasena)
        
        if usuario is not None and usuario.is_staff:
            login(request, usuario)
            return redirect('panel_admin')
        else:
            messages.error(request, 'Credenciales inválidas o no tienes permisos de administrador')
    
    return render(request, 'tienda/login_admin.html')
# Vistas de Administración
@login_required
def panel_admin(request):
    if not request.user.is_staff:
        return redirect('inicio')
    
    libros = Libro.objects.all().order_by('-fecha_creacion')
    pedidos_recientes = Pedido.objects.all().order_by('-fecha_creacion')[:10]
    
    # Estadísticas
    total_ventas = sum(pedido.total for pedido in Pedido.objects.all())
    libros_agotados = Libro.objects.filter(stock=0).count()
    
    contexto = {
        'libros': libros,
        'pedidos_recientes': pedidos_recientes,
        'total_libros': libros.count(),
        'total_pedidos': Pedido.objects.count(),
        'total_ventas': total_ventas,
        'libros_agotados': libros_agotados,
    }
    return render(request, 'tienda/panel_admin.html', contexto)

@login_required
def admin_agregar_libro(request):
    if not request.user.is_staff:
        return redirect('inicio')
    
    if request.method == 'POST':
        formulario = FormularioLibro(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Libro agregado exitosamente')
            return redirect('panel_admin')
    else:
        formulario = FormularioLibro()
    
    return render(request, 'tienda/formulario_libo_admin.html', {
        'formulario': formulario, 
        'titulo': 'Agregar Libro'
    })

@login_required
def admin_editar_libro(request, id_libro):
    if not request.user.is_staff:
        return redirect('inicio')
    
    libro = get_object_or_404(Libro, id=id_libro)
    
    if request.method == 'POST':
        formulario = FormularioLibro(request.POST, request.FILES, instance=libro)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Libro actualizado exitosamente')
            return redirect('panel_admin')
    else:
        formulario = FormularioLibro(instance=libro)
    
    return render(request, 'tienda/formulario_libo_admin.html', {
        'formulario': formulario, 
        'titulo': 'Editar Libro',
        'libro': libro
    })

@login_required
def admin_eliminar_libro(request, id_libro):
    if not request.user.is_staff:
        return redirect('inicio')
    
    libro = get_object_or_404(Libro, id=id_libro)
    libro.delete()
    messages.success(request, 'Libro eliminado exitosamente')
    return redirect('panel_admin')

@login_required
def admin_cambiar_estado_pedido(request, id_pedido):
    if not request.user.is_staff:
        return redirect('inicio')
    
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=id_pedido)
        nuevo_estado = request.POST.get('estado')
        
        if nuevo_estado in dict(Pedido.ESTADO_CHOICES):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado del pedido actualizado a {pedido.get_estado_display()}')
    
    return redirect('panel_admin')
