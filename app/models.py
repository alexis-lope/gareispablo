from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Categorías"

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_original = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    calificacion = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='libros/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    isbn = models.CharField(max_length=13, blank=True)
    paginas = models.IntegerField(null=True, blank=True)
    editorial = models.CharField(max_length=100, blank=True)
    fecha_publicacion = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.titulo
    
    @property
    def esta_en_oferta(self):
        return self.precio_original and self.precio_original > self.precio
    
    @property
    def stock_bajo(self):
        return self.stock < 5
    
    @property
    def descuento_porcentaje(self):
        if self.esta_en_oferta:
            return int(((self.precio_original - self.precio) / self.precio_original) * 100)
        return 0

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True)
    
    def __str__(self):
        return f"Pedido {self.id} - {self.libro.titulo} - {self.usuario.username}"
    
    class Meta:
        ordering = ['-fecha_creacion']