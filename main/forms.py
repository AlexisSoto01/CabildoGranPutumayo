# forms

import re
from django import forms
from .models import Usuario, TipoIdentificacion, TipoParentesco, TipoGenero, TipoEstadoCivil, TipoEscolaridad, TipoProfesion, Familia, UsuarioFamilia, Evento, UsuarioEvento, Zona, Localidad
from django_select2 import forms as s2forms
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from datetime import date
from django.core.exceptions import ValidationError

# usuarios

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'nombres', 'apellidos', 'n_documento', 'fecha_nacimiento', 'zona', 'localidad', 'direccion', 'telefono', 'identificacion', 'genero', 'estadoCivil', 'escolaridad', 'profesion'
        ]
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el apellido'}),
            'n_documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'zona': forms.Select(attrs={'class': 'form-select', 'id': 'zona-select'}),
            'localidad': forms.Select(attrs={'class': 'form-select', 'id': 'localidad-select'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la dirección'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'}),
            'identificacion': forms.Select(attrs={'class': 'form-select'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'estadoCivil': forms.Select(attrs={'class': 'form-select'}),
            'escolaridad': forms.Select(attrs={'class': 'form-select'}),
            'profesion': forms.Select(attrs={'class': 'form-select'}),
        }

    identificacion = forms.ModelChoiceField(
        queryset=TipoIdentificacion.objects.all(),
        empty_label="Selecciona tipo de identificación",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    genero = forms.ModelChoiceField(
        queryset=TipoGenero.objects.all(),
        empty_label="Selecciona género",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    estadoCivil = forms.ModelChoiceField(
        queryset=TipoEstadoCivil.objects.all(),
        empty_label="Selecciona estado civil",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    escolaridad = forms.ModelChoiceField(
        queryset=TipoEscolaridad.objects.all(),
        empty_label="Selecciona nivel de escolaridad",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    profesion = forms.ModelChoiceField(
        queryset=TipoProfesion.objects.all(),
        empty_label="Selecciona profesión",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    zona = forms.ModelChoiceField(
        queryset=Zona.objects.all(),
        empty_label="Selecciona zona",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'zona-select'})
    )

    localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.none(), 
        empty_label="Selecciona localidad",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'localidad-select'})
    )

    # Validación de campos
    def clean_nombres(self):
        nombres = self.cleaned_data.get('nombres')
        if not nombres:
            raise ValidationError('El campo "Nombres" es obligatorio.')
        if not re.match(r'^[a-zA-ZñÑ\s]{3,}$', nombres):
            raise ValidationError('El campo "Nombres" solo puede contener letras y debe tener al menos 3 caracteres.')
        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos')
        if not apellidos:
            raise ValidationError('El campo "Apellidos" es obligatorio.')
        if not re.match(r'^[a-zA-Z\s]{3,}$', apellidos):
            raise ValidationError('El campo "Apellidos" solo puede contener letras y debe tener al menos 3 caracteres.')
        return apellidos

    def clean_n_documento(self):
        n_documento = self.cleaned_data.get('n_documento')
        if not n_documento:
            raise ValidationError('El campo "Número de Documento" es obligatorio.')
        
        if not re.match(r'^\d{7,10}$', n_documento):
            raise ValidationError('El "Número de Documento" debe tener entre 7 y 10 dígitos numéricos.')
        
        usuario_id = self.instance.id if self.instance else None

        if Usuario.objects.filter(n_documento=n_documento).exclude(id=usuario_id).exists():
            raise ValidationError('El "Número de Documento" ya se encuentra registrado en el sistema.')

        return n_documento

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not re.match(r'^\d{10}$', telefono):
            raise ValidationError('El "Teléfono" debe contener exactamente 10 dígitos numéricos.')
        return telefono

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if len(direccion) < 3:
            raise ValidationError('La "Dirección" debe contener al menos 3 caracteres.')
        return direccion    

    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        # Aquí puedes filtrar las localidades si es necesario
        if 'zona' in self.data:
            try:
                zona_id = int(self.data.get('zona'))
                self.fields['localidad'].queryset = Localidad.objects.filter(zona_id=zona_id).order_by('nombre')
            except (ValueError, TypeError):
                pass  # Si no hay zona seleccionada, no se cambia la localidad
        elif self.instance.pk:  # Si estamos editando un usuario existente
            self.fields['localidad'].queryset = self.instance.zona.localidades.all()  # Cambia según tu relación
        
# familia

class FamiliaForm(forms.ModelForm):
    class Meta:
        model = Familia
        fields = ['n_familia']

        widgets = {
            'n_familia': forms.TextInput(attrs={'class': 'form-control'}),
        }

# usuario familia

class UserSearch(s2forms.ModelSelect2Widget):
    search_fields = [
        'nombres__icontains',
        'apellidos__icontains',
        'n_documento__icontains',
    ]

    def label_from_instance(self, obj):
        return f"{obj.nombres} {obj.apellidos} - {obj.identificacion.codigo} - {obj.n_documento}"
    
class FamiliaSearch(s2forms.ModelSelect2Widget):
    search_fields = ['n_familia__icontains',]
        
class UsuarioFamiliaForm(forms.ModelForm):
    class Meta:
        model = UsuarioFamilia
        fields = ['usuario', 'familia', 'parentesco']

        widgets = {
            'usuario': UserSearch(attrs={'class': 'form-select'}),
            'familia': FamiliaSearch(attrs={'class': 'form-select'}),
            'parentesco': forms.Select(attrs={'class': 'form-select'}),
        }

    parentesco = forms.ModelChoiceField(
        queryset=TipoParentesco.objects.all(),
        empty_label="Selecciona parentesco",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

        
# evento

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nombre', 'descripcion', 'imagen', 'fecha_inicio', 'fecha_fin', 'es_favorito'] 

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'es_favorito': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super(EventoForm, self).__init__(*args, **kwargs)
        self.fields['fecha_inicio'].initial = date.today()
        self.fields['fecha_fin'].initial = date.today()

    def clean_nombres(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise ValidationError('El campo "Nombre" es obligatorio.')
        if not re.match(r'^[a-zA-ZñÑ0-9\s]{3,}$', nombre):
            raise ValidationError('El campo "Nombre" solo puede contener letras y debe tener al menos 3 caracteres.')
        return nombre

# usuario evento UsuarioEvento

class EventoSearch(s2forms.ModelSelect2Widget):
    search_fields = ['nombre__icontains',]

class UsuarioEventoForm(forms.ModelForm):
    class Meta:
        model = UsuarioEvento
        fields = ['usuario', 'evento', 'fecha_asistencia', 'asistencia']

        widgets = {
            'usuario': UserSearch(attrs={'class': 'form-select'}),
            'evento': EventoSearch(attrs={'class': 'form-select'}),
            'fecha_asistencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'asistencia': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super(UsuarioEventoForm, self).__init__(*args, **kwargs)
        self.fields['fecha_asistencia'].initial = date.today()
        
# login

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repite la contraseña'})
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
    
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Username'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Contraseña'})
    )

    class Meta:
        model = User
        fields = ['username', 'password']

