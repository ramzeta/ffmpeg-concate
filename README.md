# 🎬 Video Concatenator (COCAT)

Una aplicación de escritorio con interfaz gráfica desarrollada en Python que permite concatenar múltiples archivos de video de forma sencilla usando FFmpeg, con optimización automática del uso de CPU para mantener la responsividad del sistema.

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## ✨ Características Principales

- 🖼️ **Interfaz gráfica intuitiva** con Tkinter (no requiere conocimientos técnicos)
- 🔗 **Concatenación de videos** usando FFmpeg con método "copy" para mayor velocidad
- 📊 **Monitoreo de CPU en tiempo real** con limitación automática (80% por defecto)
- ⚙️ **Variables de entorno** para configuración personalizada del sistema
- 🔄 **Reordenamiento fácil** de videos con botones "Subir" y "Bajar"
- 📁 **Validación automática** de archivos y extensiones
- 🛡️ **Manejo robusto de errores** con logging detallado
- 🧹 **Limpieza automática** de archivos temporales

## Requisitos

- Python 3.6 o superior
- FFmpeg instalado en el sistema
- Bibliotecas de Python: `psutil`

## Instalación

### Configuración automática (Windows):
1. Ejecuta `setup_venv.bat` para crear el entorno virtual e instalar dependencias
2. Asegúrate de tener FFmpeg instalado y accesible desde la línea de comandos

### Configuración manual:
1. Clona o descarga el proyecto
2. Crea un entorno virtual:
```bash
python -m venv venv
```
3. Activa el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instala las dependencias:
```bash
pip install -r requirements.txt
```
5. Asegúrate de tener FFmpeg instalado y accesible desde la línea de comandos

## Variables de Entorno

La aplicación utiliza las siguientes variables de entorno:

- `FFMPEG_PATH`: Ruta al ejecutable de FFmpeg (por defecto: 'ffmpeg')
- `MAX_CPU_USAGE`: Uso máximo de CPU permitido en porcentaje (por defecto: 80)

### Configurar variables de entorno en Windows:

```cmd
set FFMPEG_PATH=C:\path\to\ffmpeg.exe
set MAX_CPU_USAGE=75
```

### Configurar variables de entorno en Linux/Mac:

```bash
export FFMPEG_PATH=/usr/local/bin/ffmpeg
export MAX_CPU_USAGE=75
```

## Uso

### Con entorno virtual:
1. Windows: Ejecuta `run.bat` o activa manualmente el entorno y ejecuta `python main.py`
2. Linux/Mac: 
```bash
source venv/bin/activate
python main.py
```

2. Agrega videos usando el botón "Agregar Videos"
3. Reordena los videos usando los botones "Subir" y "Bajar"
4. Selecciona la ubicación del archivo de salida
5. Ajusta la configuración de CPU si es necesario
6. Haz clic en "Concatenar Videos"

## Optimización de CPU

La aplicación monitorea constantemente el uso de CPU y pausa temporalmente el proceso de FFmpeg cuando el uso excede el límite configurado. Esto asegura que el sistema mantenga su responsividad durante el procesamiento de videos.

## Formatos Soportados

- MP4
- AVI
- MOV
- MKV
- WMV
- FLV
- WEBM

## Notas

- Todos los videos deben tener las mismas especificaciones (resolución, codec, etc.) para una concatenación exitosa
- El proceso utiliza el método "copy" de FFmpeg para mayor velocidad
- Los archivos temporales se eliminan automáticamente después del procesamiento"# ffmpeg-concate" 
