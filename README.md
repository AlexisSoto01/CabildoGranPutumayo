# Proyecto Cabildo

## Introducción

El proyecto **Cabildo** es una aplicación web desarrollada en **Django** que permite la gestión eficiente de eventos y usuarios. Esta aplicación ofrece una interfaz de usuario intuitiva basada en plantillas HTML, facilitando la administración de eventos y la autenticación de usuarios. Además, incluye la funcionalidad de generación y descarga de informes en formato PDF utilizando la biblioteca **WeasyPrint**.

## Tecnologías Utilizadas

- **Python**
- **Django**
- **MySQL**

## Instalación

### Pasos de Instalación

Sigue los siguientes pasos para instalar y configurar el proyecto:

1. **Clona el repositorio**

   Abre tu terminal y ejecuta los siguientes comandos:

   ```bash
   cd cabildo_django
   ```

2. **Crea y activa un entorno virtual**

   Crea un entorno virtual y actívalo con los siguientes comandos:

   ```bash
   python -m venv env
   env\Scripts\activate
   ```

   - **¿Error al activar el entorno virtual?**

     Si experimentas un error al intentar activar el entorno virtual, abre PowerShell como administrador y ejecuta:

     ```bash
     Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```

     Luego, cierra PowerShell.

3. **Instala las dependencias**

   Instala todas las dependencias necesarias listadas en el archivo `requirements.txt` ejecutando:

   ```bash
   pip install -r requirements.txt
   ```

4. **Instala WeasyPrint en Windows**

   Para utilizar WeasyPrint en Windows, es necesario instalar algunas dependencias adicionales. Sigue estos pasos:

   - **Instala Pango y GTK** utilizando [MSYS2](https://www.msys2.org/). Descarga el instalador y sigue las instrucciones de instalación.
   - Después de la instalación, abre `MSYS2 UCRT64` e ingresa los siguientes comandos:

     ```bash
     pacman -S mingw-w64-x86_64-pango
     pacman -S mingw-w64-x86_64-gtk4
     ```

     Si deseas desarrollar con GTK3, también puedes ejecutar:

     ```bash
     pacman -S mingw-w64-ucrt-x86_64-gtk3
     ```

   - Agrega el directorio `bin` de GTK a tu variable de entorno `PATH` siguiendo estos pasos:

     1. Abre el cuadro de diálogo Ejecutar presionando `Win + R`.
     2. Escribe el siguiente comando y presiona Enter:

        ```bash
        sysdm.cpl
        ```

     3. En la ventana de Propiedades del sistema, ve a la pestaña `Opciones avanzadas`.
     4. Haz clic en el botón `Variables de entorno`.
     5. En `Variables del sistema`, selecciona `Path` y haz clic en `Editar`.
     6. Agrega la ruta al directorio `bin` de GTK:

        ```bash
        C:\msys64\ucrt64\bin
        ```

5. **Configura la base de datos**

   Asegúrate de configurar correctamente tu base de datos en el archivo `settings.py`.

6. **Aplica las migraciones**

   Ejecuta los siguientes comandos para aplicar las migraciones:

   ```bash
   python manage.py makemigrations 
   python manage.py migrate
   ```

7. **Inicia el servidor de desarrollo**

   Para iniciar el servidor de desarrollo, utiliza el siguiente comando:

   ```bash
   python manage.py runserver
   ```

## Estructura del Proyecto

La estructura del proyecto es la siguiente:

```bash
proyecto_cabildo/
├── .gitignore
├── env
└── media
│   └── eventos
│       └── eventos.jpg
├── CabildoGranPutumayo/
│   ├── __pycache__
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── main/
    ├── __pycache__
    ├── migrations/
    ├── static/
    │   └── img/
    ├── templates/
    │   ├── bases/
    │   │   └── etc.html
    │   ├── eventos/
    │   │   └── etc.html
    │   ├── login/
    │   │   └── etc.html
    │   └── usuarios/
    │       └── etc.html
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── context_processors/
    ├── forms/
    ├── models.py
    ├── tests.py
    ├── url.py
    └── views.py
```