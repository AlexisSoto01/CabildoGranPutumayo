# views

from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Usuario, Familia, UsuarioFamilia, Evento, UsuarioEvento, Localidad
from .forms import UsuarioForm, FamiliaForm, UsuarioFamiliaForm, EventoForm, UsuarioEventoForm, CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.models import Group, User
from django.db import IntegrityError
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.utils.timezone import timedelta
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile

# ROL usuario

@login_required
def ver_infopersonal(request):
    try:
        # Obtener el perfil del usuario
        usuario = Usuario.objects.get(user=request.user)
    except Usuario.DoesNotExist:
        # Si no existe el perfil, pasar usuario como None para manejar en la plantilla
        usuario = None

    # Si el perfil existe, verificar si hay datos incompletos
    datos_incompletos = False
    if usuario:
        campos_requeridos = [
            usuario.nombres, usuario.apellidos, usuario.n_documento,
            usuario.fecha_nacimiento, usuario.direccion, usuario.telefono,
            usuario.identificacion, usuario.genero,
            usuario.estadoCivil, usuario.escolaridad, usuario.profesion
        ]
        datos_incompletos = any(campo in [None, ''] for campo in campos_requeridos)

    return render(request, 'usuarios/ver.html', {'usuario': usuario, 'datos_incompletos': datos_incompletos})

@login_required
def actualizar_infopersonal(request):
    # Obtener el usuario del modelo Usuario asociado al usuario autenticado
    usuario = get_object_or_404(Usuario, user=request.user)
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    
    return render(request, 'usuarios/actualizar.html', {'form': form})

@login_required
def crear_infopersonal(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)  # No guardar aún en la base de datos
            usuario.user = request.user  # Asignar el usuario actual
            usuario.save()  # Guardar en la base de datos
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/crear.html', {'form': form})

@login_required
def ver_mifamilia(request):
    try:
        # Obtener el perfil del usuario relacionado con el usuario autenticado
        usuario_actual = request.user.usuario
    except Usuario.DoesNotExist:
        # Si no existe el perfil, pasar como None para manejar en la plantilla
        usuario_actual = None
    
    # Inicializar variables para el contexto
    familia_actual = None
    usuario_familias = []

    if usuario_actual:
        try:
            # Intentar obtener la relación del usuario con su familia
            usuario_familia_actual = UsuarioFamilia.objects.get(usuario=usuario_actual)
            familia_actual = usuario_familia_actual.familia
            usuario_familias = UsuarioFamilia.objects.filter(familia=familia_actual)
        except UsuarioFamilia.DoesNotExist:
            # Si no existe la relación, mantener las variables vacías
            familia_actual = None
            usuario_familias = []

    context = {
        'usuario_familias': usuario_familias,
        'familia_actual': familia_actual,
        'usuario_actual': usuario_actual,  # Opcional, si quieres mostrar información del usuario
    }

    return render(request, 'usuarios/usuarios_familias/listar.html', context)

# ROL admin

# usuarios
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def ver_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, 'usuarios/ver.html', {'usuario': usuario})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def listar_usuarios(request):
    usuarios = Usuario.objects.all().select_related('identificacion', 'genero', 'estadoCivil', 'escolaridad', 'profesion')
    return render(request, 'usuarios/listar.html', {'usuarios': usuarios})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def crear_usuario(request):    
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        
        # Imprimir los datos que se están intentando guardar
        print("Datos del formulario:", request.POST)

        if form.is_valid():
            try:
                usuario = form.save(commit=False)
                n_documento = form.cleaned_data['n_documento']
                
                # Imprimir los datos que se guardarán
                print("Datos validados para guardar:", usuario)
                print("Número de documento:", n_documento)
                
                user, created = User.objects.get_or_create(
                    username=n_documento,
                    defaults={
                        'first_name': form.cleaned_data['nombres'],
                        'last_name': form.cleaned_data['apellidos']
                    }
                )
                
                if created:
                    user.set_password(n_documento)
                    user.save()
                    
                    try:
                        group = Group.objects.get(name='Usuario')
                        user.groups.add(group)
                        messages.success(request, 'El usuario se ha creado con éxito.')
                    except Group.DoesNotExist:
                        messages.warning(request, 'Error: El grupo "Usuario" no está configurado en el sistema.')
                else:
                    messages.warning(request, 'El usuario con este número de documento ya existe en el sistema.')

                usuario.user = user
                usuario.save()

                form = UsuarioForm()
            
            except Exception as e:
                messages.warning(request, f'Ocurrió un error inesperado al crear el usuario: {str(e)}')
                for field, errors in form.errors.items():
                    for error in errors:
                        print(f'Error en {field}: {error}')
        else:
            messages.warning(request, 'Hay errores en el formulario. Por favor corrige los campos indicados.')
            print("Errores del formulario:", form.errors)  # Imprimir los errores si el formulario no es válido
    else:
        form = UsuarioForm()
    
    return render(request, 'usuarios/crear.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def actualizar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioForm(instance=usuario)  # Cargar el formulario al inicio

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'El usuario se ha editado correctamente.')
            return redirect('listar_usuarios')
        else:
            messages.warning(request, 'Hay errores en el formulario. Por favor corrige los campos indicados.')  # Solo se muestra si hay errores

    return render(request, 'usuarios/actualizar.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    
    try:
        user = usuario.user
        user.delete()
        messages.success(request, 'El usuario se ha eliminado correctamente.')
    except Exception as e:
        print(f"Error al eliminar el usuario: {e}")

    usuario.delete()
    return redirect('listar_usuarios')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def get_localidades(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        zona_id = request.GET.get('zona', None)
        localidades = Localidad.objects.filter(zona_id=zona_id).values('id', 'nombre')
        return JsonResponse(list(localidades), safe=False)
    else:
        return JsonResponse({'error': 'No se permite esta solicitud'}, status=400)
        
# familias

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def listar_familias(request):
    familias = Familia.objects.all()
    return render(request, 'usuarios/familias/listar.html', {'familias': familias})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def crear_familia(request):
    if request.method == 'POST':
        form = FamiliaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'La Familia se ha creado con éxito.')
            form = FamiliaForm()
    else:
        form = FamiliaForm()
    return render(request, 'usuarios/familias/crear.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def actualizar_familia(request, pk):
    familia = get_object_or_404(Familia, pk=pk)
    if request.method == 'POST':
        form = FamiliaForm(request.POST, instance=familia)
        if form.is_valid():
            form.save()
            messages.success(request, f'La Familia se ha editado con éxito.')
            return redirect('listar_familias')
    else:
        form = FamiliaForm(instance=familia)
    return render(request, 'usuarios/familias/actualizar.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def eliminar_familia(request, pk):
    familia = get_object_or_404(Familia, pk=pk)
    familia.delete()
    messages.success(request, f'La Familia se ha eliminado con éxito.')
    return redirect('listar_familias')

# usuario familia 

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def listar_usuario_familia(request):
    usuario_familias = UsuarioFamilia.objects.all()
    return render(request, 'usuarios/usuarios_familias/listar.html', {'usuario_familias': usuario_familias})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def crear_usuario_familia(request):
    if request.method == 'POST':
        form = UsuarioFamiliaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'El Usuario y Familia se ha creado con éxito.')
            form = UsuarioFamiliaForm()
    else:
        form = UsuarioFamiliaForm()
    return render(request, 'usuarios/usuarios_familias/crear.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def actualizar_usuario_familia(request, pk):
    usuario_familia = get_object_or_404(UsuarioFamilia, pk=pk)
    if request.method == 'POST':
        form = UsuarioFamiliaForm(request.POST, instance=usuario_familia)
        if form.is_valid():
            form.save()
            messages.success(request, f'El Usuario y Familia se ha editado con éxito.')
            return redirect('listar_usuario_familia')
    else:
        form = UsuarioFamiliaForm(instance=usuario_familia)
    return render(request, 'usuarios/usuarios_familias/actualizar.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def eliminar_usuario_familia(request, pk):
    usuario_familia = get_object_or_404(UsuarioFamilia, pk=pk)
    usuario_familia.delete()
    messages.success(request, f'El Usuario y Familia se ha elimado con éxito.')
    return redirect('listar_usuario_familia')

# eventos

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def listar_eventos(request):
    eventos = Evento.objects.all()
    context = {'eventos': eventos}
    return render(request, 'eventos/listar.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def crear_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)  
        if form.is_valid():
            form.save()
            messages.success(request, f'El Evento se ha creado con éxito.')
            form = EventoForm()  
    else:
        form = EventoForm()
    
    context = {'form': form}
    return render(request, 'eventos/crear.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def actualizar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento) 
        if form.is_valid():
            form.save()
            messages.success(request, f'El Evento se ha editado con éxito.')
            return redirect('listar_eventos')
    else:
        form = EventoForm(instance=evento)
    
    context = {'form': form}
    return render(request, 'eventos/actualizar.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def eliminar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if evento.imagen:
        if default_storage.exists(evento.imagen.path):
            default_storage.delete(evento.imagen.path)
    
    evento.delete()
    messages.success(request, f'El Evento se ha eliminado con éxito.')

    return redirect('listar_eventos')

# usuarios eventos

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def crear_usuario_evento(request):
    if request.method == 'POST':
        form = UsuarioEventoForm(request.POST)
        if form.is_valid():

            usuario_evento = form.save(commit=False)
            usuario = usuario_evento.usuario
            evento = usuario_evento.evento

            duracion_evento = evento.duracion_dias

            for dia in range(duracion_evento):
                fecha_asistencia = evento.fecha_inicio + timedelta(days=dia)
                UsuarioEvento.objects.create(
                    usuario=usuario,
                    evento=evento,
                    fecha_asistencia=fecha_asistencia,
                    asistencia=False 
                )
            messages.success(request, f'Las Asistencias para el Usuario se han creado con éxito.')
            return redirect('listar_usuarios_eventos')
    else:
        form = UsuarioEventoForm()
        form.fields['fecha_asistencia'].widget = forms.HiddenInput()
        form.fields['asistencia'].widget = forms.HiddenInput()

    context = {'form': form}
    return render(request, 'eventos/asistencias/crear.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def listar_usuarios_eventos(request):
    usuarios_eventos = UsuarioEvento.objects.all()
    context = {'usuarios_eventos': usuarios_eventos}
    return render(request, 'eventos/asistencias/listar.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def actualizar_usuario_evento(request, pk):
    usuario_evento = get_object_or_404(UsuarioEvento, pk=pk)
    evento_id = usuario_evento.evento.pk
    usuario_id = usuario_evento.usuario.pk  # Esto asegura que tengas el usuario_id correcto

    if request.method == 'POST':
        form = UsuarioEventoForm(request.POST, instance=usuario_evento)
        if form.is_valid():
            form.save()
            messages.success(request, f'La Asistencia del Usuario se ha editado con éxito.')

            return redirect('listar_asistencias_usuario', usuario_id=usuario_id)  # Redirigir al listado de asistencias del usuario
    else:
        form = UsuarioEventoForm(instance=usuario_evento)

    form.fields['usuario'].widget = forms.HiddenInput() 
    form.fields['evento'].widget = forms.HiddenInput() 
    form.fields['fecha_asistencia'].widget = forms.HiddenInput()  

    context = {
        'form': form,
        'evento_id': evento_id,
        'usuario_id': usuario_id,  # Pasa el usuario_id al contexto
    }
    return render(request, 'eventos/asistencias/actualizar.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def eliminar_usuario_evento(request, pk):
    usuario_evento = get_object_or_404(UsuarioEvento, pk=pk)
    usuario_id = usuario_evento.usuario.pk
    usuario_evento.delete()
    messages.success(request, 'La Asistencia del Usuario se ha eliminado con éxito.')

    return redirect('listar_asistencias_usuario', usuario_id=usuario_id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def listar_usuarios_por_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    
    # Calcular las fechas del evento
    duracion_dias = (evento.fecha_fin - evento.fecha_inicio).days + 1
    fechas_evento = [(evento.fecha_inicio + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(duracion_dias)]

    # Obtener todas las asistencias del evento
    usuarios_eventos = UsuarioEvento.objects.filter(evento=evento).select_related('usuario')

    # Agrupar asistencias por usuario
    asistencias_por_usuario = {}
    for usuario_evento in usuarios_eventos:
        usuario = usuario_evento.usuario
        if usuario not in asistencias_por_usuario:
            # Inicializamos con todas las fechas en 'No Asistió'
            asistencias_por_usuario[usuario] = {'asistencias': [False] * len(fechas_evento), 'faltas': 0}
        
        # Marcamos las asistencias reales
        fecha_asistencia_str = usuario_evento.fecha_asistencia.strftime('%Y-%m-%d')
        if fecha_asistencia_str in fechas_evento:
            index = fechas_evento.index(fecha_asistencia_str)
            asistencias_por_usuario[usuario]['asistencias'][index] = usuario_evento.asistencia  # True si asistió, False si no
    
    # Contamos las veces que faltó cada usuario
    for usuario, data in asistencias_por_usuario.items():
        data['faltas'] = data['asistencias'].count(False)  # Cuenta los 'False' en la lista de asistencias

    context = {
        'evento': evento,
        'asistencias_por_usuario': asistencias_por_usuario.items(),  # Pasamos como items para iterar
        'fechas_evento': fechas_evento,
    }

    return render(request, 'eventos/asistencias/listar_filtro.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def registrar_usuario_a_evento(request, evento_id=None):
    evento = get_object_or_404(Evento, pk=evento_id)

    if request.method == 'POST':
        form = UsuarioEventoForm(request.POST)
        if form.is_valid():
            usuario_evento = form.save(commit=False)
            usuario = usuario_evento.usuario
            duracion_evento = evento.duracion_dias

            print(f"Duración del evento: {duracion_evento} días")
            
            registros = []
            registros_existentes = 0  # Contador de registros existentes

            for dia in range(duracion_evento):
                fecha_asistencia = evento.fecha_inicio + timedelta(days=dia)
                print(f"Verificando asistencia para el día: {fecha_asistencia}")

                # Revisar si ya existe el registro
                if not UsuarioEvento.objects.filter(usuario=usuario, evento=evento, fecha_asistencia=fecha_asistencia).exists():
                    print(f"Añadiendo registro para el día {fecha_asistencia}")
                    registros.append(UsuarioEvento(
                        usuario=usuario,
                        evento=evento,
                        fecha_asistencia=fecha_asistencia,
                        asistencia=False  # Inicialmente sin asistencia
                    ))
                else:
                    registros_existentes += 1  # Contamos cuántos registros ya existen

            # Si hay registros nuevos, los creamos
            if registros:
                print(f"Creando {len(registros)} registros nuevos...")
                UsuarioEvento.objects.bulk_create(registros)
                print(f"Asistencias nuevas registradas con éxito.")
                messages.success(request, f'Las Asistencias para el Usuario se han creado con éxito.')

            else:
                print(f"El usuario ya estaba registrado en todas las fechas del evento. Registros existentes: {registros_existentes}.")
            return redirect('listar_eventos')
        else:
            print("Formulario no válido, errores:", form.errors)
    else:
        form = UsuarioEventoForm(initial={'evento': evento})
        form.fields['evento'].widget = forms.HiddenInput()
        form.fields['asistencia'].widget = forms.HiddenInput()

    context = {
        'form': form,
        'evento': evento
    }
    return render(request, 'eventos/asistencias/crear_filtro.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def listar_asistencias_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)  
    asistencias = UsuarioEvento.objects.filter(usuario=usuario)  

    if asistencias.exists():
        evento_id = asistencias.first().evento.pk  
    else:
        evento_id = None  

    context = {
        'usuario': usuario,
        'usuarios_eventos': asistencias,
        'evento_id': evento_id, 
    }

    return render(request, 'eventos/asistencias/listar_filtro2.html', context)

# registrarse

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()  
                group = Group.objects.get(name='Usuario') 
                user.groups.add(group)
                login(request, user)  
                return redirect('myData')
            except IntegrityError:
                form.add_error(None, "El nombre de usuario ya existe.")
        else:
            return render(request, 'login/signup.html', {"form": form})

    else:
        form = CustomUserCreationForm()
    return render(request, 'login/signup.html', {"form": form})
        
# iniciar sesion

def signin(request):
    if request.method == 'GET':
        return render(request, 'login/signin.html', {"formAuth": CustomAuthenticationForm()})
    else:
        # Autenticar usuario
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login/signin.html', {"formAuth": CustomAuthenticationForm(), "error": "Usuario o contraseña incorrecta."})
        
        login(request, user)
        
        # Redirigir según grupo
        if user.groups.filter(name='Admin').exists():
            return redirect('listar_usuarios')  # Redirigir a vista de admin
        elif user.groups.filter(name='Usuario').exists():
            return redirect('ver_infopersonal')  # Redirigir a vista de usuario
        else:
            return redirect('index')  # Redirigir si no tiene grupo

# cerrar sesion

@login_required
def signout(request):
    logout(request)
    return redirect('index')

# -----------------

def index(request):
    eventos = Evento.objects.filter(es_favorito=True)
    return render(request, 'bases/landing/index.html', {'eventos': eventos})

def historia(request):
    return render(request, 'bases/landing/otros/historia.html')

def misionVision(request):
    return render(request, 'bases/landing/otros/misionVision.html')

def acerca_de(request):
    return render(request, 'bases/landing/otros/acerca_de.html')

def cronograma_eventos(request):
    eventos = Evento.objects.filter(es_favorito=True).order_by('-fecha_inicio') 
    return render(request, 'bases/landing/otros/cronograma.html', {'eventos': eventos})

# ------------------

# PDF

# views.py


from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm  # Asegúrate de que tu formulario esté importado correctamente.

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirigir al índice después de registrarse
            return redirect('index')  # Asegúrate de que 'index' es el nombre correcto de la ruta
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'login/signup.html', {'form': form})



def generar_pdf_usuarios(request):
    usuarios = Usuario.objects.all().select_related(
        'identificacion', 'genero', 'estadoCivil', 'escolaridad', 'profesion'
    )

    html_string = render_to_string('usuarios/listar_pdf.html', {'usuarios': usuarios})
    html = HTML(string=html_string)
    result = html.write_pdf()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="usuarios.pdf"'
    response.write(result)
    return response

def generar_pdf_asistencias_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    
    # Obtener todas las asistencias para el evento específico
    usuarios_eventos = UsuarioEvento.objects.filter(evento=evento).select_related('usuario')

    # Calcular las fechas del evento
    duracion_dias = (evento.fecha_fin - evento.fecha_inicio).days + 1
    fechas_evento = [(evento.fecha_inicio + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(duracion_dias)]

    # Agrupar asistencias por usuario
    asistencias_por_usuario = {}
    for usuario_evento in usuarios_eventos:
        usuario = usuario_evento.usuario
        if usuario not in asistencias_por_usuario:
            # Inicializamos con todas las fechas en 'No Asistió'
            asistencias_por_usuario[usuario] = {'asistencias': [False] * len(fechas_evento), 'faltas': 0}
        
        # Marcamos las asistencias reales
        fecha_asistencia_str = usuario_evento.fecha_asistencia.strftime('%Y-%m-%d')
        if fecha_asistencia_str in fechas_evento:
            index = fechas_evento.index(fecha_asistencia_str)
            asistencias_por_usuario[usuario]['asistencias'][index] = usuario_evento.asistencia  # True si asistió, False si no
    
    # Contamos las veces que faltó cada usuario
    for usuario, data in asistencias_por_usuario.items():
        data['faltas'] = data['asistencias'].count(False)  # Cuenta los 'False' en la lista de asistencias

    context = {
        'evento': evento,
        'asistencias_por_usuario': asistencias_por_usuario.items(),
        'fechas_evento': fechas_evento,
    }

    html_string = render_to_string('eventos/asistencias/listar_filtro_pdf.html', context)
    html = HTML(string=html_string)
    result = html.write_pdf()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{evento.nombre}_asistencias.pdf"'
    response.write(result)
    return response
