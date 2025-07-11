from django import forms
from .models import Libro, Categoria

class FormularioLibro(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'autor', 'categoria', 'precio', 'precio_original', 'stock', 
                 'calificacion', 'descripcion', 'imagen', 'isbn', 'paginas', 'editorial', 
                 'fecha_publicacion']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del libro'}),
            'autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Autor del libro'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_original': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'calificacion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '5'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ISBN'}),
            'paginas': forms.NumberInput(attrs={'class': 'form-control'}),
            'editorial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Editorial'}),
            'fecha_publicacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
