# models.py

from datetime import date
from django.db import models
from django.contrib.auth.models import User

# Modelo Zona
class Zona(models.Model):
    nombre = models.CharField(max_length=45, unique=True)
    codigo = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return f"{self.nombre}"

# Modelo Localidad
class Localidad(models.Model):
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE, related_name='localidades')  # Añadido related_name
    nombre = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return f"{self.nombre}"

# Modelo TipoIdentificacion
class TipoIdentificacion(models.Model):
    nombre = models.CharField(max_length=45, unique=True)
    codigo = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return f"{self.nombre}"

# Modelo TipoParentesco
class TipoParentesco(models.Model):
    nombre = models.CharField(max_length=45, unique=True)
    codigo = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return f"{self.nombre}"

# Modelo TipoGenero
class TipoGenero(models.Model):
    nombre = models.CharField(max_length=45, unique=True)
    codigo = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return f"{self.nombre}"

# Modelo TipoEstadoCivil
class TipoEstadoCivil(models.Model):
    nombre = models.CharField(max_length=45, unique=True)
    codigo = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return f"{self.nombre}"

# Modelo TipoEscolaridad
class TipoEscolaridad(models.Model):
    nombre = models.CharField(max_length=45, unique=True)
    codigo = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return f"{self.nombre}"

# Modelo TipoProfesion
class TipoProfesion(models.Model):
    nombre = models.CharField(max_length=45, unique=True)
    codigo = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return f"{self.nombre}"

# Modelo Usuario
class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=45)
    apellidos = models.CharField(max_length=45)
    n_documento = models.CharField(max_length=10, unique=True)
    fecha_nacimiento = models.DateField()
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE)
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=45, null=True, blank=True)
    telefono = models.CharField(max_length=10, null=True, blank=True)
    identificacion = models.ForeignKey(TipoIdentificacion, on_delete=models.CASCADE)
    genero = models.ForeignKey(TipoGenero, on_delete=models.CASCADE)
    estadoCivil = models.ForeignKey(TipoEstadoCivil, on_delete=models.CASCADE, null=True, blank=True)
    escolaridad = models.ForeignKey(TipoEscolaridad, on_delete=models.CASCADE, null=True, blank=True)
    profesion = models.ForeignKey(TipoProfesion, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    def calcular_edad(self):
        today = date.today()
        edad = today.year - self.fecha_nacimiento.year
        if (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        return edad

    def familias(self):
        return self.usuariofamilia_set.all()

# Modelo Familia
class Familia(models.Model):
    n_familia = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.n_familia

# Modelo UsuarioFamilia
class UsuarioFamilia(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    familia = models.ForeignKey(Familia, on_delete=models.CASCADE)
    parentesco = models.ForeignKey(TipoParentesco, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario} - {self.familia}"

# Modelo Evento
class Evento(models.Model):
    nombre = models.CharField(max_length=45)
    descripcion = models.TextField(null=True, blank=True)  
    imagen = models.ImageField(upload_to='eventos/', null=True, blank=True)  
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    es_favorito = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre
    
    @property
    def duracion_dias(self):
        if self.fecha_fin >= self.fecha_inicio:
            return (self.fecha_fin - self.fecha_inicio).days + 1
        else:
            return 0 

# Modelo UsuarioEvento
class UsuarioEvento(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    fecha_asistencia = models.DateField()  
    asistencia = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.usuario} - {self.evento} ({self.fecha_asistencia})"
    
    class Meta:
        unique_together = ('usuario', 'evento', 'fecha_asistencia')  # Un usuario no puede tener asistencia repetida para el mismo evento en la misma fecha

