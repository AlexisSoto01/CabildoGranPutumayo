# urls

from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    #select2

    path("select2/", include("django_select2.urls")),
    
    #usuarios

    path('user/new/', views.crear_usuario, name='crear_usuario'),
    path('users/', views.listar_usuarios, name='listar_usuarios'),
    path('user/<int:pk>/', views.ver_usuario, name='ver_usuario'),
    path('user/<int:pk>/edit/', views.actualizar_usuario, name='actualizar_usuario'),
    path('user/<int:pk>/delete/', views.eliminar_usuario, name='eliminar_usuario'),
    path('get_localidades/', views.get_localidades, name='get_localidades'),

    # familias

    path('families/', views.listar_familias, name='listar_familias'),
    path('family/new/', views.crear_familia, name='crear_familia'),
    path('families/<int:pk>/edit/', views.actualizar_familia, name='actualizar_familia'),
    path('families/<int:pk>/delete/', views.eliminar_familia, name='eliminar_familia'),

    # usuarios familias

    path('user/family/', views.listar_usuario_familia, name='listar_usuario_familia'),
    path('user/family/new/', views.crear_usuario_familia, name='crear_usuario_familia'),
    path('user/family/<int:pk>/edit/', views.actualizar_usuario_familia, name='actualizar_usuario_familia'),
    path('user/family/<int:pk>/delete/', views.eliminar_usuario_familia, name='eliminar_usuario_familia'),

    # eventos

    path('events/', views.listar_eventos, name='listar_eventos'),
    path('event/new/', views.crear_evento, name='crear_evento'),
    path('event/<int:pk>/edit/', views.actualizar_evento, name='actualizar_evento'),
    path('event/<int:pk>/delete/', views.eliminar_evento, name='eliminar_evento'),

    # usuarios eventos

    path('users/events/', views.listar_usuarios_eventos, name='listar_usuarios_eventos'),
    path('user/events/new/', views.crear_usuario_evento, name='crear_usuario_evento'),
    path('user/events/<int:pk>/edit/', views.actualizar_usuario_evento, name='actualizar_usuario_evento'),
    path('user/events/<int:pk>/delete/', views.eliminar_usuario_evento, name='eliminar_usuario_evento'),
    path('events/<int:evento_id>/list/', views.listar_usuarios_por_evento, name='listar_usuarios_por_evento'),
    path('events/<int:evento_id>/registrar_usuario/', views.registrar_usuario_a_evento, name='registrar_usuario_a_evento'),
    path('assistance/user/<int:usuario_id>/', views.listar_asistencias_usuario, name='listar_asistencias_usuario'),
    
    # login

    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.signout, name='logout'),

    # ROL usuario

    path('myData/', views.ver_infopersonal, name='ver_infopersonal'),
    path('edit/', views.actualizar_infopersonal, name='actualizar_infopersonal'),

    # familia

    path('myFamily/', views.ver_mifamilia, name='ver_mifamilia'),

    #---------

    path('', views.index, name='index'), 
    path('history', views.historia, name='historia'), 
    path('events/schedule', views.cronograma_eventos, name='cronograma_eventos'),
    path('abouth',views.acerca_de, name='acerca_de'),

    # pdf


    path('usuarios/pdf/', views.generar_pdf_usuarios, name='generar_pdf_usuarios'),
path('evento/<int:evento_id>/asistencias/pdf/', views.generar_pdf_asistencias_evento, name='generar_pdf_asistencias_evento'), 

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])