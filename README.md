# 🎥 Transcriptor de Videos de YouTube

Esta aplicación convierte automáticamente el audio de videos de YouTube a texto en italiano y genera traducciones a inglés, portugués y español, creando un archivo JSON compatible con el modelo `TranslationVideoModel`.

## ✨ Características

- **🎬 Descarga automática** de videos de YouTube
- **🎵 Archivos de audio locales** (MP3, WAV, M4A, AAC, FLAC, OGG, etc.)
- **☁️ Audio desde storage** (Google Drive, Dropbox, OneDrive, Box)
- **🌐 Audio desde URLs web** (descarga directa de archivos de audio)
- **🌍 Transcripción de audio a texto** en italiano usando Google Speech Recognition
- **🔄 Traducción automática** a inglés, portugués y español
- **📊 Generación de JSON** con formato compatible con `TranslationVideoModel`
- **⏱️ Manejo de tiempos** con formato HH:MM:SS.mmm
- **⚡ Procesamiento por chunks** para mejor precisión
- **🧹 Limpieza automática** de archivos temporales

## 🚀 Instalación

### 1. Requisitos del sistema

- Python 3.7 o superior
- FFmpeg instalado en el sistema
- Conexión a internet

### 2. Instalar FFmpeg

#### Windows:
```bash
# Usando Chocolatey
choco install ffmpeg

# O descargar desde: https://ffmpeg.org/download.html
```

#### macOS:
```bash
# Usando Homebrew
brew install ffmpeg
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

## 📖 Uso

### Uso interactivo (Recomendado para principiantes)

```bash
python main.py
```

Sigue las instrucciones en pantalla para:
1. Ingresar la URL del video de YouTube
2. Especificar el nombre del archivo JSON de salida
3. Esperar a que se complete la transcripción

### Uso programático

```python
from video_transcriber import VideoTranscriber

# Crear instancia
transcriber = VideoTranscriber()

# Transcribir video de YouTube
success = transcriber.transcribe_video(
    "https://www.youtube.com/watch?v=VIDEO_ID",
    "mi_transcripcion.json"
)

# Transcribir archivo de audio local
success = transcriber.transcribe_audio_file(
    "mi_audio.mp3",
    "audio_transcripcion.json"
)

# Transcribir audio desde URL (storage o web)
success = transcriber.transcribe_audio_from_url(
    "https://drive.google.com/file/d/FILE_ID/view",
    "drive_transcripcion.json"
)

# Limpiar archivos temporales
transcriber.cleanup()
```

### Ejemplos de uso

```bash
# Ejemplo básico
python example_usage.py

# Ejemplo con archivos de audio locales
python audio_example.py

# Ejemplo con audio desde URLs (storage/web)
python url_audio_example.py
```

## ☁️ **Servicios de Storage Soportados**

### **Google Drive**
- **Formato**: `https://drive.google.com/file/d/FILE_ID/view`
- **Conversión**: Automática a descarga directa
- **Ejemplo**: `https://drive.google.com/file/d/1ABC123DEF456/view?usp=sharing`

### **Dropbox**
- **Formato**: `https://www.dropbox.com/s/.../file.mp3?dl=0`
- **Conversión**: Automática a descarga directa
- **Ejemplo**: `https://www.dropbox.com/s/abc123/audio.mp3?dl=0`

### **OneDrive**
- **Formato**: `https://1drv.ms/...` o `https://onedrive.live.com/...`
- **Conversión**: Automática a descarga directa
- **Ejemplo**: `https://1drv.ms/u/s!ABC123DEF456`

### **Box**
- **Formato**: `https://app.box.com/file/...`
- **Conversión**: Automática a descarga directa
- **Ejemplo**: `https://app.box.com/file/123456789`

### **URLs Web Directas**
- **Formato**: `https://example.com/audio.mp3`
- **Conversión**: No necesaria (descarga directa)
- **Ejemplo**: `https://example.com/podcast.mp3`

> 💡 **Nota**: El sistema detecta automáticamente el tipo de URL y la convierte a descarga directa cuando es necesario.

## 📁 Estructura del JSON generado

El archivo JSON generado tiene la siguiente estructura:

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "name": "Nombre del video",
  "description": "Descripción",
  "category": "categoría",
  "image": "",
  "author": "Autor",
  "chiave": "clave",
  "livello": "nivel",
  "lingua": "it",
  "views": 0,
  "chiaveTranslation": "traducción",
  "chiaveTranslationEN": "translation",
  "chiaveTranslationPR": "tradução",
  "subtitles": [
    {
      "text": "Testo in italiano",
      "startTime": "00:00:00.000",
      "endTime": "00:00:03.500",
      "translation": "Texto en español",
      "translationPR": "Texto em português",
      "translationEN": "Text in English",
      "isWordKey": false
    }
  ]
}
```

## 🔧 Configuración avanzada

### Personalizar el procesamiento

```python
# Cambiar idioma de transcripción
text = recognizer.recognize_google(audio_data, language='es-ES')  # Para español

# Cambiar tamaño de chunks
chunks = transcriber.split_audio_into_chunks(audio_path, chunk_length_ms=15000)

# Personalizar detección de silencio
chunks = split_on_silence(
    audio,
    min_silence_len=1000,      # 1 segundo de silencio mínimo
    silence_thresh=-35,         # Umbral de silencio más sensible
    keep_silence=500            # Mantener 500ms de silencio
)
```

### Procesar archivos de audio locales

```python
# Para archivos MP3, WAV, etc.
audio = AudioSegment.from_file("mi_audio.mp3")
chunks = transcriber.split_audio_into_chunks("mi_audio.mp3")
```

## ⚠️ Limitaciones y consideraciones

1. **Calidad del audio**: Mejor calidad = mejor transcripción
2. **Idioma**: Optimizado para italiano, pero funciona con otros idiomas
3. **Duración**: Videos largos pueden tomar mucho tiempo
4. **Conexión**: Requiere conexión estable a internet
5. **API de Google**: Limitaciones de uso de la API gratuita

## 🐛 Solución de problemas

### Error: "No module named 'speech_recognition'"
```bash
pip install SpeechRecognition
```

### Error: "FFmpeg not found"
- Instalar FFmpeg siguiendo las instrucciones de instalación
- Verificar que esté en el PATH del sistema

### Error: "Audio file could not be read"
- Verificar que el archivo de audio sea válido
- Asegurar que FFmpeg esté instalado correctamente

### Transcripción vacía
- Verificar que el video tenga audio
- Comprobar que el idioma sea italiano
- Revisar la calidad del audio

## 📝 Notas técnicas

- **Formato de tiempo**: HH:MM:SS.mmm (horas:minutos:segundos.milisegundos)
- **Codificación**: UTF-8 para soporte completo de caracteres
- **Temporales**: Los archivos se limpian automáticamente
- **Memoria**: El procesamiento se hace por chunks para optimizar memoria

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de solución de problemas
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que FFmpeg esté funcionando
4. Abre un issue en el repositorio

---

**¡Disfruta transcribiendo tus videos de YouTube! 🎉**
