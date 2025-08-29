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
- 📸 **Extracción de último frame** con control de calidad (alta/media/baja)
- 🎯 **Modo dual**: Concatenar videos O extraer frames por separado
- 🖼️ **Frames de alta calidad** con configuraciones optimizadas de FFmpeg

## 📋 Requisitos del Sistema

### Requisitos Obligatorios
- **Python 3.6 o superior** - [Descargar Python](https://www.python.org/downloads/)
- **FFmpeg** - [Descargar FFmpeg](https://www.ffmpeg.org/download.html)

### Dependencias de Python
- `psutil>=5.9.0` - Para monitoreo de CPU
- `tkinter` - Incluido con Python (interfaz gráfica)

## 🚀 Instalación y Configuración

### Instalación Simple 🔧

```bash
# 1. Descargar o clonar el proyecto
cd cocat

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar aplicación
python main.py
```

### 🛠️ Instalación de FFmpeg

#### Windows:
1. Descargar FFmpeg desde [ffmpeg.org](https://www.ffmpeg.org/download.html)
2. Extraer a `C:\ffmpeg\`
3. Agregar `C:\ffmpeg\bin\` al PATH del sistema
4. Verificar: abrir cmd y ejecutar `ffmpeg -version`

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS:
```bash
# Con Homebrew
brew install ffmpeg

# Con MacPorts
sudo port install ffmpeg
```

### ✅ Verificación de Instalación

Ejecuta el script de prueba para verificar que FFmpeg esté correctamente instalado:

```bash
python test_ffmpeg.py
```

## ⚙️ Variables de Entorno

La aplicación utiliza las siguientes variables de entorno opcionales:

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `FFMPEG_PATH` | Ruta al ejecutable de FFmpeg | `ffmpeg` |
| `MAX_CPU_USAGE` | Uso máximo de CPU permitido (%) | `80` |

### Configurar en Windows:
```cmd
set FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe
set MAX_CPU_USAGE=75
```

### Configurar en Linux/Mac:
```bash
export FFMPEG_PATH=/usr/local/bin/ffmpeg
export MAX_CPU_USAGE=75
```

## 📖 Guía de Uso Paso a Paso

### 🚀 Inicio Rápido

**Ejecutar la aplicación:**
```bash
python main.py
```

### 📝 Tutorial Completo

#### Paso 1: Agregar Videos 📁
1. **Abrir selector de archivos**: Haz clic en el botón **"Agregar Videos"**
2. **Seleccionar archivos**: 
   - Navega a la carpeta con tus videos
   - Selecciona múltiples archivos (Ctrl+clic en Windows/Linux, Cmd+clic en Mac)
   - Formatos soportados: MP4, AVI, MOV, MKV, WMV, FLV, WEBM, M4V
3. **Confirmar selección**: Los videos aparecerán en la lista principal

#### Paso 2: Ordenar Videos 🔄
1. **Seleccionar video**: Haz clic en un video de la lista para seleccionarlo
2. **Cambiar posición**:
   - **"Subir"**: Mueve el video seleccionado hacia arriba en la lista
   - **"Bajar"**: Mueve el video seleccionado hacia abajo en la lista
3. **Verificar orden**: El orden final en la lista será el orden de concatenación

#### Paso 3: Gestionar Lista 🗂️
- **Quitar video específico**: 
  1. Selecciona el video en la lista
  2. Haz clic en **"Quitar Seleccionado"**
- **Limpiar toda la lista**: Haz clic en **"Limpiar Lista"** para borrar todos los videos

#### Paso 4: Configurar Archivo de Salida 💾
1. **Abrir selector**: Haz clic en **"Seleccionar"** junto a "Archivo de salida"
2. **Elegir ubicación**: Navega a donde quieres guardar el video final
3. **Nombrar archivo**: 
   - Escribe el nombre deseado
   - **IMPORTANTE**: Incluye la extensión (ej: `mi_video.mp4`)
   - Si olvidas la extensión, la app te ofrecerá agregar `.mp4`

#### Paso 5: Configurar Rendimiento ⚙️
1. **Ajustar CPU**: En el campo "Uso máximo de CPU (%)"
   - **PC potente**: 85-90%
   - **PC normal**: 70-80% (recomendado)
   - **Laptop**: 60-70%
2. **Verificar ruta FFmpeg**: Normalmente no necesitas cambiar esto

#### Paso 6: Elegir Modo de Operación 🎯

**Opción A: Solo Extraer Últimos Frames 📸**
1. **Selecciona videos**: Agrega los videos de los cuales quieres extraer frames
2. **Haz clic en "Extraer Último Frame"**
3. **Selecciona carpeta**: Elige dónde guardar las imágenes PNG
4. **Procesamiento**: La app extraerá el último frame de cada video seleccionado

**Opción B: Concatenar Videos (con frame opcional) 🔗**
1. **Verificar configuración**:
   - ✅ Videos en la lista en orden correcto
   - ✅ Archivo de salida configurado
   - ✅ Configuración de CPU ajustada
2. **Configurar frame**: Marca/desmarca "También capturar frame al concatenar"
3. **Iniciar proceso**: Haz clic en **"Concatenar Videos"**
4. **Monitorear progreso**:
   - Observa la barra de progreso
   - Revisa el uso de CPU en tiempo real
   - La aplicación pausará FFmpeg si el CPU supera el límite

#### Paso 7: Finalización ✅

**Para Extracción de Frames:**
- **Éxito**: Mensaje con cantidad de frames extraídos y lista de archivos generados
- **Archivos**: Se guardan como `[nombre_video]_last_frame.png` en la carpeta seleccionada

**Para Concatenación:**
- **Éxito**: Mensaje "Videos concatenados exitosamente"
  - Si activaste la captura de frame, también se mostrará la ruta del archivo PNG generado
- **Archivos generados**:
  - Video concatenado: En la ubicación que especificaste
  - Último frame: `[nombre_video]_last_frame.png` (si está activado)

**En caso de Error:**
- Revisa los archivos de log (`ffmpeg_error.log`, `app_error.log`)

### 🎯 Consejos para Mejores Resultados

1. **Compatibilidad de videos**:
   - Usa videos con la misma resolución (ej: todos 1920x1080)
   - Preferible el mismo formato y codec
   - Si los videos son diferentes, FFmpeg intentará convertirlos automáticamente

2. **Orden de videos**:
   - El primer video en la lista será el primero en el archivo final
   - Verifica el orden antes de procesar

3. **Rendimiento**:
   - Videos más grandes tardan más
   - Ajusta el límite de CPU según tu necesidad de uso del PC
   - El proceso pausará automáticamente si el CPU está muy cargado

4. **Espacio en disco**:
   - Asegúrate de tener suficiente espacio para el archivo final
   - El video concatenado será aproximadamente la suma de todos los archivos

### 🔄 Interfaz de Usuario

```
┌───────────────────────────────────────────────────────────┐
│ Videos a concatenar:                                      │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ video1.mp4                                            │ │
│ │ video2.mp4                                            │ │
│ │ video3.mp4                                            │ │
│ └───────────────────────────────────────────────────────┘ │
│ [Agregar Videos] [Quitar] [Limpiar] [⬆] [⬇]               │
│                                                           │
│ Archivo de salida: [_______________] [Seleccionar]        │
│                                                           │
│ Configuración:                                            │
│ Uso máximo CPU (%): [80]                                  │
│ Ruta FFmpeg: [ffmpeg]                                     │
│                                                           │
│ Progreso: [████████████████████████████] CPU: 45%        │
│                                                           │
│ [Concatenar Videos] [Extraer Último Frame]                │
│                     ☑️ También capturar frame al concatenar│
└───────────────────────────────────────────────────────────┘
```

## 🎥 Formatos Soportados

### Entrada (Videos a concatenar):
- **MP4** - Más común y recomendado
- **AVI** - Compatible con la mayoría de codecs
- **MOV** - Formato de QuickTime
- **MKV** - Contenedor versátil
- **WMV** - Windows Media Video
- **FLV** - Flash Video
- **WEBM** - Formato web optimizado
- **M4V** - Variante de MP4

### Salida (Video concatenado):
Todos los formatos de entrada están soportados para salida. Se recomienda usar **MP4** para máxima compatibilidad.

## ⚡ Optimización de CPU

### ¿Cómo funciona?
- La aplicación monitorea el uso de CPU cada 100ms
- Si el uso supera el límite configurado (80% por defecto):
  - Pausa temporalmente el proceso de FFmpeg
  - Espera 500ms
  - Reanuda el proceso
- Esto mantiene el sistema responsive durante la concatenación

### Configuración Recomendada:
- **PC potente**: 85-90%
- **PC promedio**: 70-80%
- **Laptop/trabajo**: 60-70%

## 🐛 Solución de Problemas

### Errores Comunes

#### "FFmpeg no encontrado"
**Causa**: FFmpeg no está instalado o no está en el PATH
**Solución**: 
1. Verificar instalación: `ffmpeg -version`
2. Reinstalar FFmpeg siguiendo las instrucciones de instalación
3. Configurar variable `FFMPEG_PATH` con la ruta completa

#### "Error al concatenar videos"
**Causa**: Videos con diferentes especificaciones técnicas
**Solución**:
1. Verificar que todos los videos tengan la misma resolución
2. Usar videos con el mismo codec
3. Revisar `ffmpeg_error.log` para detalles específicos

#### "Archivos faltantes detectados"
**Causa**: Archivos de video movidos o eliminados después de agregarlos
**Solución**:
1. Verificar que los archivos existen en la ubicación original
2. Volver a agregar los archivos si fueron movidos

### Archivos de Log

- `ffmpeg_error.log`: Detalles de errores de FFmpeg
- `app_error.log`: Errores de la aplicación Python

## 📁 Estructura del Proyecto

```
cocat/
├── main.py                 # Aplicación principal
├── requirements.txt        # Dependencias Python
├── setup_venv.bat         # Configuración automática (Windows)
├── run.bat                # Ejecutor con entorno virtual (Windows)
├── test_ffmpeg.py         # Script de verificación de FFmpeg
├── README.md              # Documentación
├── venv/                  # Entorno virtual (creado automáticamente)
├── ffmpeg_error.log       # Log de errores FFmpeg (creado en runtime)
└── app_error.log          # Log de errores aplicación (creado en runtime)
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Créditos

- **FFmpeg**: [https://www.ffmpeg.org/](https://www.ffmpeg.org/)
- **Python**: [https://www.python.org/](https://www.python.org/)
- **Tkinter**: Interfaz gráfica estándar de Python
- **Psutil**: Monitoreo de sistema

## 🔗 Enlaces Útiles

- [Documentación de FFmpeg](https://www.ffmpeg.org/documentation.html)
- [Guía de formatos de video](https://www.ffmpeg.org/general.html#Video-Codecs)
- [Troubleshooting FFmpeg](https://www.ffmpeg.org/faq.html)

---

**Desarrollado con ❤️ para simplificar la concatenación de videos**