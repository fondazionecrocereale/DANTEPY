
import yt_dlp
import json
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
from deep_translator import GoogleTranslator
import re
import math
import tempfile
from typing import List, Dict, Any
import time
import subprocess
import requests

import whisper

class YtDlpLogger:
    def __init__(self, callback=None):
        self.callback = callback

    def debug(self, msg):
        # Para debug, podríamos imprimir o ignorar
        if msg.strip().startswith('[debug] '):
            pass
        else:
            self.check_auth(msg)

    def info(self, msg):
        self.check_auth(msg)
        print(msg)

    def warning(self, msg):
        self.check_auth(msg)
        print(msg)

    def error(self, msg):
        print(msg)

    def check_auth(self, msg):
        if self.callback and ("confirm you’re not a bot" in msg or "Sign in" in msg):
            self.callback(f"⚠️ YouTube requiere autenticación (Bot detection): {msg}")


class VideoTranscriber:
    def __init__(self):
        self.model = None
        self.temp_dir = tempfile.mkdtemp()
        self.cookie_temp_file = None

    def _get_cookiefile(self):
        """Obtiene el archivo de cookies."""
        # 1. Buscar en el mismo directorio que el script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_cookies = os.path.join(script_dir, 'cookies.txt')
        if os.path.exists(local_cookies):
            print(f"✅ Usando cookies locales: {local_cookies}")
            return local_cookies
            
        # 1b. También buscar en el directorio actual (por si acaso)
        cwd_cookies = os.path.join(os.getcwd(), 'cookies.txt')
        if os.path.exists(cwd_cookies) and cwd_cookies != local_cookies:
            print(f"✅ Usando cookies del CWD: {cwd_cookies}")
            return cwd_cookies
            
        # 2. Buscar en secrets de Render (/etc/secrets/cookies.txt)
        render_secret_cookies = '/etc/secrets/cookies.txt'
        if os.path.exists(render_secret_cookies):
             print(f"✅ Usando cookies desde Secret Files (Render): {render_secret_cookies}")
             return render_secret_cookies
        
        # 2. Buscar en variable de entorno
        cookies_content = os.environ.get('YOUTUBE_COOKIES')
        if cookies_content:
            try:
                # Crear archivo temporal
                fd, path = tempfile.mkstemp(suffix='.txt', text=True)
                with os.fdopen(fd, 'w') as tmp:
                    tmp.write(cookies_content)
                self.cookie_temp_file = path
                print(f"✅ Usando cookies desde variable de entorno. Longitud: {len(cookies_content)}")
                print(f"📄 Inicio del contenido de cookies: {cookies_content[:50]}...")
                print(f"📂 Archivo temporal de cookies creado en: {path}")
                return path
            except Exception as e:
                print(f"Error creando archivo de cookies temporal: {e}")
        
        print("⚠️ No se encontraron cookies (cookies.txt o YOUTUBE_COOKIES). La descarga podría fallar por bot detection.")
        return None

    def _get_model(self):
        """Carga el modelo Whisper bajo demanda si no está cargado"""
        if self.model is None:
            print("Cargando modelo Whisper (esto puede tardar un poco la primera vez)...")
            self.model = whisper.load_model("tiny")
        return self.model
        
    def _split_long_segment(self, segment, max_chars=80):
        """
        Divide un segmento largo en partes más pequeñas y legibles.
        Respetando los tiempos originales y dividiendo en puntos naturales.
        """
        text = segment['text']
        start_time = segment['startTime']
        end_time = segment['endTime']
        
        # Si el texto es suficientemente corto, no dividir
        if len(text) <= max_chars:
            return [segment]
        
        # Convertir tiempos a milisegundos para cálculos
        start_ms = self._time_to_milliseconds(start_time)
        end_ms = self._time_to_milliseconds(end_time)
        total_duration = end_ms - start_ms
        
        # Dividir el texto en frases naturales
        sentences = self._split_into_sentences(text)
        
        if len(sentences) == 1:
            # Si es una sola frase muy larga, dividir por palabras
            words = text.split()
            if len(words) <= 10:
                return [segment]
            
            # Dividir en grupos de palabras
            word_groups = self._split_words_into_groups(words, max_chars)
            segments = []
            
            for i, group in enumerate(word_groups):
                group_text = ' '.join(group)
                group_duration = (len(group_text) / len(text)) * total_duration
                
                if i == 0:
                    group_start = start_ms
                else:
                    # Calcular el tiempo de inicio basado en el tiempo de fin del segmento anterior
                    prev_end_time = self._time_to_milliseconds(segments[-1]['endTime'])
                    group_start = prev_end_time
                
                group_end = group_start + group_duration
                
                # Re-traducir cada segmento dividido
                translation_en = self.translate_text(group_text, 'en')
                translation_pt = self.translate_text(group_text, 'pt')
                translation_es = self.translate_text(group_text, 'es')
                
                segments.append({
                    'text': group_text,
                    'startTime': self._milliseconds_to_time(group_start),
                    'endTime': self._milliseconds_to_time(group_end),
                    'translation': translation_es,      # Traducción del texto de este segmento
                    'translationPR': translation_pt,   # Traducción del texto de este segmento
                    'translationEN': translation_en,   # Traducción del texto de este segmento
                    'isWordKey': segment['isWordKey']
                })
            
            # Ajustar el último segmento para que coincida exactamente con el tiempo final
            if segments:
                segments[-1]['endTime'] = end_time
            
            return segments
        
        else:
            # Dividir por frases naturales
            segments = []
            current_start = start_ms
            
            for i, sentence in enumerate(sentences):
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Calcular duración proporcional de la frase
                sentence_ratio = len(sentence) / len(text)
                sentence_duration = sentence_ratio * total_duration
                
                sentence_end = current_start + sentence_duration
                
                # Ajustar el último segmento para que coincida exactamente
                if i == len(sentences) - 1:
                    sentence_end = end_ms
                
                # Re-traducir cada frase dividida
                translation_en = self.translate_text(sentence, 'en')
                translation_pt = self.translate_text(sentence, 'pt')
                translation_es = self.translate_text(sentence, 'es')
                
                segments.append({
                    'text': sentence,
                    'startTime': self._milliseconds_to_time(current_start),
                    'endTime': self._milliseconds_to_time(sentence_end),
                    'translation': translation_es,      # Traducción del texto de esta frase
                    'translationPR': translation_pt,   # Traducción del texto de esta frase
                    'translationEN': translation_en,   # Traducción del texto de esta frase
                    'isWordKey': segment['isWordKey']
                })
                
                current_start = sentence_end
            
            return segments
    
    def _split_into_sentences(self, text):
        """Divide el texto en frases naturales usando puntuación italiana."""
        # Patrones de puntuación italiana
        sentence_endings = r'[.!?]+'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_words_into_groups(self, words, max_chars):
        """Divide palabras en grupos que no excedan max_chars."""
        groups = []
        current_group = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 por el espacio
            
            if current_length + word_length <= max_chars:
                current_group.append(word)
                current_length += word_length
            else:
                if current_group:
                    groups.append(current_group)
                current_group = [word]
                current_length = word_length
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _time_to_milliseconds(self, time_str):
        """Convierte tiempo en formato HH:MM:SS.mmm a milisegundos."""
        try:
            # Formato: HH:MM:SS.mmm
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds_parts = parts[2].split('.')
            seconds = int(seconds_parts[0])
            milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
            
            total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds
            return total_ms
        except:
            return 0
    
    def _milliseconds_to_time(self, ms):
        """Convierte milisegundos a formato HH:MM:SS.mmm."""
        total_seconds = int(ms // 1000)
        milliseconds = int(ms % 1000)
        
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    def _optimize_subtitles_for_ui(self, subtitles, max_chars=80):
        """
        Optimiza los subtítulos para mejor legibilidad en la UI.
        Divide segmentos largos en partes más pequeñas.
        """
        optimized_subtitles = []
        
        for subtitle in subtitles:
            # Dividir segmentos largos
            split_segments = self._split_long_segment(subtitle, max_chars)
            optimized_subtitles.extend(split_segments)
        
        return optimized_subtitles

    def download_youtube_video(self, url: str, output_path: str = None, status_callback=None) -> tuple:
        """Descarga un video de YouTube y extrae el audio, retorna también metadatos"""
        if output_path is None:
            output_path = os.path.join(self.temp_dir, "audio.wav")
            
        # Selector robusto: busca 480p, de lo contrario lo mejor disponible
        ydl_opts = {
            'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]/bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': output_path.replace('.wav', ''),
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'no_warnings': False,
            'quiet': False,
            'verbose': True,
            'extract_flat': False,
            'skip_download': False,
            'age_limit': None,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'source_address': '0.0.0.0',
            'extractor_args': {
                'youtube': {
                    'player_client': ['web', 'android', 'ios', 'mweb'],
                }
            },
            'logger': YtDlpLogger(status_callback)
        }

        # Configurar cookies
        cookie_file = self._get_cookiefile()
        
        # Intentar con cookies primero (si están disponibles)
        if cookie_file:
            print(f"DEBUG: Intentando descarga con cookies: {cookie_file}")
            ydl_opts['cookiefile'] = cookie_file
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    # Verificar si realmente hay formatos de video/audio (no solo imágenes)
                    formats = info.get('formats', [])
                    if any(f.get('vcodec') != 'none' or f.get('acodec') != 'none' for f in formats):
                        video_title = info.get('title', 'Video de YouTube')
                        thumbnail_url = info.get('thumbnail', '')
                        channel_url = info.get('channel_url') or info.get('uploader_url') or ""
                        duration = info.get('duration', 0)
                        categories = info.get('categories', [])
                        category = categories[0] if categories else "transcripción"
                        
                        ydl.download([url])
                        
                        if not duration or duration == 0:
                            try:
                                audio = AudioSegment.from_file(output_path)
                                duration = len(audio) / 1000.0
                            except: pass
                            
                        return output_path, video_title, thumbnail_url, channel_url, duration, category
                    else:
                        print("⚠️ La descarga con cookies solo encontró imágenes. Intentando sin cookies...")
            except Exception as e:
                print(f"⚠️ El intento con cookies falló: {e}. Intentando sin cookies...")

        # Intentar sin cookies (o como fallback)
        print("DEBUG: Intentando descarga anónima (sin cookies)...")
        ydl_opts.pop('cookiefile', None)
        ydl_opts.pop('cookiesfrombrowser', None)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Video de YouTube')
                thumbnail_url = info.get('thumbnail', '')
                channel_url = info.get('channel_url') or info.get('uploader_url') or ""
                duration = info.get('duration', 0)
                categories = info.get('categories', [])
                category = categories[0] if categories else "transcripción"
                
                ydl.download([url])
                
                if not duration or duration == 0:
                    try:
                        audio = AudioSegment.from_file(output_path)
                        duration = len(audio) / 1000.0
                    except: pass
                
                return output_path, video_title, thumbnail_url, channel_url, duration, category
        except Exception as e:
            print(f"La descarga anónima también falló: {e}")
            return None, None, None, None, 0, "transcripción"
    
    # Methods split_audio_into_chunks and transcribe_audio_chunk removed (legacy code)
    

    
    def translate_text(self, text: str, target_lang: str) -> str:
        """Traduce texto al idioma objetivo"""
        if not text.strip():
            return ""
        
        try:
            # Mapear códigos de idioma para deep-translator
            lang_map = {
                'en': 'en',
                'es': 'es', 
                'pt': 'pt',
                'it': 'it'
            }
            
            target_lang_code = lang_map.get(target_lang, target_lang)
            translator = GoogleTranslator(source='it', target=target_lang_code)
            translation = translator.translate(text)
            return translation
        except Exception as e:
            print(f"Error traduciendo a {target_lang}: {e}")
            return text
    
    def format_duration(self, seconds: float) -> str:
        """Convierte segundos a formato HH:MM:SS.mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    
    def convert_audio_to_wav(self, audio_file_path: str) -> str:
        """Convierte cualquier formato de audio a WAV"""
        try:
            # Si ya es WAV, no convertir
            if audio_file_path.lower().endswith('.wav'):
                return audio_file_path
            
            print(f"Convirtiendo {audio_file_path} a formato WAV...")
            
            # Cargar el archivo de audio
            audio = AudioSegment.from_file(audio_file_path)
            
            # Crear archivo WAV temporal
            wav_path = os.path.join(self.temp_dir, "converted_audio.wav")
            
            # Exportar como WAV
            audio.export(wav_path, format="wav")
            
            print("✅ Conversión completada")
            return wav_path
            
        except Exception as e:
            print(f"Error convirtiendo audio: {e}")
            return None
    
    def transcribe_audio_file(self, audio_file_path: str, output_json_path: str = "transcription.json", optimize_for_ui: bool = True) -> bool:
        """Transcribe un archivo de audio local"""
        print(f"Procesando archivo de audio: {audio_file_path}")
        
        if not os.path.exists(audio_file_path):
            print(f"Error: El archivo {audio_file_path} no existe")
            return False
        
        # Convertir a WAV si es necesario
        audio_path = self.convert_audio_to_wav(audio_file_path)
        
        if not audio_path:
            print("Error: No se pudo convertir el archivo de audio")
            return False
        
        return self._process_audio(audio_path, output_json_path, "Archivo de audio local", author_url="", optimize_for_ui=optimize_for_ui)
    
    def transcribe_audio_from_url(self, audio_url: str, output_json_path: str = "transcription.json", optimize_for_ui: bool = True) -> bool:
        """Transcribe un archivo de audio desde una URL (storage o web)"""
        print(f"Procesando audio desde URL: {audio_url}")
        
        # Descargar el archivo de audio
        audio_path = self.download_audio_from_url(audio_url)
        
        if not audio_path:
            print("Error: No se pudo descargar el archivo de audio")
            return False
            
        # Intentar extraer thumbnail si es un video
        thumbnail_path = ""
        lower_path = audio_path.lower()
        if lower_path.endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
            print("Detectado archivo de video, intentando extraer thumbnail...")
            thumbnail_path = self._extract_thumbnail(audio_path)
            if thumbnail_path:
                print(f"Thumbnail extraído: {thumbnail_path}")
        
        # Convertir a WAV si es necesario
        wav_path = self.convert_audio_to_wav(audio_path)
        
        if not wav_path:
            print("Error: No se pudo convertir el archivo de audio")
            return False
        
        return self._process_audio(wav_path, output_json_path, f"Audio desde URL: {audio_url}", thumbnail_url=thumbnail_path, author_url="", optimize_for_ui=optimize_for_ui)

    def _extract_thumbnail(self, video_path: str) -> str:
        """Extrae un thumbnail del video usando ffmpeg"""
        try:
            # Crear nombre para el thumbnail
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            thumbnail_path = os.path.join(self.temp_dir, f"{base_name}_thumb.jpg")
            
            # Comando ffmpeg para extraer un frame al segundo 1
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', '00:00:01.000',
                '-vframes', '1',
                thumbnail_path,
                '-y'  # Sobrescribir si existe
            ]
            
            # Ejecutar comando
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(thumbnail_path):
                return thumbnail_path
            return ""
            
        except Exception as e:
            print(f"Error extrayendo thumbnail: {e}")
            return ""

    def download_audio_from_url(self, url: str) -> str:
        """Descarga un archivo de audio desde una URL"""
        try:
            from urllib.parse import urlparse, unquote
            print("Descargando archivo de audio...")
            
            # Convertir URL de storage a descarga directa
            direct_url = self.get_direct_download_url(url)
            if direct_url != url:
                print(f"🔄 URL convertida: {direct_url}")
            
            # Crear nombre de archivo temporal
            parsed_url = urlparse(direct_url)
            path = unquote(parsed_url.path)
            filename = os.path.basename(path)
            
            # Si el nombre no tiene extensión o es muy largo/raro, intentar sacarlo del content-type después
            # Por ahora, si no tiene extensión, asumir mp3
            if not filename or '.' not in filename:
                filename = "downloaded_audio.mp3"
            
            # Ruta temporal para el archivo descargado
            temp_audio_path = os.path.join(self.temp_dir, filename)
            
            # Headers para simular un navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'audio/*, */*',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.google.com/',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Descargar el archivo
            response = requests.get(direct_url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # Intear deducir extensión del content-type si el archivo no la tiene bien
            content_type = response.headers.get('content-type', '').lower()
            
            # Si detectamos que es video y la extensión es incorrecta
            if 'video/' in content_type and not filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
                 if not temp_audio_path.lower().endswith('.mp4'):
                    temp_audio_path += ".mp4"
            
            if not any(t in content_type for t in ['audio/', 'video/', 'application/octet-stream', 'binary']):
                print("⚠️  Advertencia: El archivo puede no ser multimedia")
            
            # Guardar el archivo
            with open(temp_audio_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ Archivo descargado: {os.path.basename(temp_audio_path)}")
            return temp_audio_path
            
        except Exception as e:
            print(f"Error descargando audio: {e}")
            return None
    
    def get_direct_download_url(self, url: str) -> str:
        """Convierte URLs de storage a URLs de descarga directa"""
        try:
            # Google Drive
            if 'drive.google.com' in url:
                return self._convert_google_drive_url(url)
            
            # Dropbox
            elif 'dropbox.com' in url:
                return self._convert_dropbox_url(url)
            
            # OneDrive
            elif '1drv.ms' in url or 'onedrive.live.com' in url:
                return self._convert_onedrive_url(url)
            
            # Box
            elif 'box.com' in url:
                return self._convert_box_url(url)
            
            # URL directa (no necesita conversión)
            else:
                return url
                
        except Exception as e:
            print(f"Error convirtiendo URL: {e}")
            return url
    
    def _convert_google_drive_url(self, url: str) -> str:
        """Convierte URL de Google Drive a descarga directa"""
        try:
            # Extraer ID del archivo
            if '/file/d/' in url:
                file_id = url.split('/file/d/')[1].split('/')[0]
            elif 'id=' in url:
                file_id = url.split('id=')[1].split('&')[0]
            else:
                return url
            
            # Crear URL de descarga directa
            direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            print(f"🔄 URL de Google Drive convertida a descarga directa")
            return direct_url
            
        except Exception as e:
            print(f"Error convirtiendo URL de Google Drive: {e}")
            return url
    
    def _convert_dropbox_url(self, url: str) -> str:
        """Convierte URL de Dropbox a descarga directa"""
        try:
            # Convertir URL de Dropbox a descarga directa
            if '?dl=0' in url:
                direct_url = url.replace('?dl=0', '?dl=1')
            elif '?dl=' not in url:
                direct_url = url + '?dl=1'
            else:
                direct_url = url
            
            print(f"🔄 URL de Dropbox convertida a descarga directa")
            return direct_url
            
        except Exception as e:
            print(f"Error convirtiendo URL de Dropbox: {e}")
            return url
    
    def _convert_onedrive_url(self, url: str) -> str:
        """Convierte URL de OneDrive a descarga directa"""
        try:
            # OneDrive URLs son más complejas, intentar conversión básica
            if '1drv.ms' in url:
                # Redirigir a la URL completa
                import requests
                response = requests.head(url, allow_redirects=True)
                url = response.url
            
            # Agregar parámetro de descarga
            if 'download=1' not in url:
                separator = '&' if '?' in url else '?'
                direct_url = url + f"{separator}download=1"
            else:
                direct_url = url
            
            print(f"🔄 URL de OneDrive convertida a descarga directa")
            return direct_url
            
        except Exception as e:
            print(f"Error convirtiendo URL de OneDrive: {e}")
            return url
    
    def _convert_box_url(self, url: str) -> str:
        """Convierte URL de Box a descarga directa"""
        try:
            # Box URLs con parámetro de descarga
            if 'download=1' not in url:
                separator = '&' if '?' in url else '?'
                direct_url = url + f"{separator}download=1"
            else:
                direct_url = url
            
            print(f"🔄 URL de Box convertida a descarga directa")
            return direct_url
            
        except Exception as e:
            print(f"Error convirtiendo URL de Box: {e}")
            return url
    
    def format_video_duration(self, seconds: float) -> str:
        """Convierte segundos a formato para UI (minutos y segundos)"""
        if not seconds:
            return "0:00"
        
        seconds = int(round(seconds))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

    def transcribe_video(self, video_url: str, output_json_path: str = "transcription.json", optimize_for_ui: bool = True, status_callback=None) -> bool:
        """Proceso completo de transcripción y traducción de video de YouTube"""
        print("Descargando video de YouTube...")
        result = self.download_youtube_video(video_url, status_callback=status_callback)
        
        if result[0] is None:
            print("Error: No se pudo descargar el video")
            return False
        
        audio_path, video_title, thumbnail_url, author_url, duration_seconds, category_from_yt = result
        
        # Convert duration to string format for UI (e.g. 0:26)
        duration_str = self.format_video_duration(duration_seconds)
        
        return self._process_audio(audio_path, output_json_path, video_url, video_title, thumbnail_url, author_url, optimize_for_ui, duration=duration_str, category=category_from_yt)
    
    def _process_audio(self, audio_path: str, output_json_path: str, source_url: str, video_title: str = None, thumbnail_url: str = None, author_url: str = "", optimize_for_ui: bool = True, duration: str = "", category: str = "transcripción") -> bool:
        """Procesa el audio (común para video y archivos locales) usando Whisper"""
        
        try:
            print("Iniciando transcripción con Whisper (esto puede tardar unos minutos)...")
            # Transcribir directamente con Whisper
            # Transcribir directamente con Whisper
            # Whisper se encarga de dividir el audio y manejar tiempos internamente
            model = self._get_model()
            result = model.transcribe(audio_path, language="it")
            
            segments = result.get('segments', [])
            print(f"Whisper generó {len(segments)} segmentos base.")
            
            transcriptions = []
            
            print("Traduciendo segmentos...")
            for i, segment in enumerate(segments):
                # if i % 10 == 0:
                #    print(f"Procesando segmento {i+1}/{len(segments)}")
                
                segment_text = segment['text'].strip()
                if not segment_text:
                    continue
                    
                start_time = segment['start']
                end_time = segment['end']
                
                # Traducir texto
                translation_en = self.translate_text(segment_text, 'en')
                translation_pt = self.translate_text(segment_text, 'pt')
                translation_es = self.translate_text(segment_text, 'es')
                
                transcription_data = {
                    'text': segment_text,
                    'startTime': self.format_duration(start_time),
                    'endTime': self.format_duration(end_time),
                    'translation': translation_es,      # Traducción del texto de este segmento
                    'translationPR': translation_pt,   # Traducción del texto de este segmento
                    'translationEN': translation_en,   # Traducción del texto de este segmento
                    'isWordKey': False
                }
                
                transcriptions.append(transcription_data)
            
            # Optimizar subtítulos para mejor legibilidad en la UI
            if optimize_for_ui:
                print("🔧 Optimizando subtítulos para mejor legibilidad...")
                transcriptions = self._optimize_subtitles_for_ui(transcriptions, max_chars=80)
                print(f"✅ Subtítulos optimizados: {len(transcriptions)} segmentos")
            
            # Determinar el autor
            author_field = "DanteStudio"
            if author_url:
                author_field = author_url
            
            # Crear estructura final del JSON con metadatos correctos
            final_data = {
                'url': source_url,                                    # URL real del video
                'name': video_title if video_title else "Video de YouTube",  # Nombre real del video
                'description': "Transcripción automática del audio",
                'category': category,
                'image': thumbnail_url if thumbnail_url else "",       # Thumbnail del video
                'author': author_field,
                'chiave': "transcripción",
                'livello': "intermedio",
                'lingua': "it",
                'views': 0,
                'duration': duration,                                  # Duración del video
                'chiaveTranslation': "transcripción",
                'chiaveTranslationEN': "transcription",
                'chiaveTranslationPR': "transcrição",
                'subtitles': transcriptions
            }
            
            # Guardar en archivo JSON
            try:
                with open(output_json_path, 'w', encoding='utf-8') as f:
                    json.dump(final_data, f, ensure_ascii=False, indent=2)
                
                print(f"Transcripción completada y guardada en {output_json_path}")
                print(f"Total de segmentos transcritos: {len(transcriptions)}")
                return True
                
            except Exception as e:
                print(f"Error guardando archivo JSON: {e}")
                return False
            
        except Exception as e:
            print(f"Error durante el procesamiento con Whisper: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Limpiar archivos temporales
            if os.path.join(self.temp_dir) in audio_path: # Solo borrar si está en temp
                try:
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                except:
                    pass

    def cleanup(self):
        """Limpia archivos temporales"""
        import shutil
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass
        
        if self.cookie_temp_file and os.path.exists(self.cookie_temp_file):
            try:
                os.remove(self.cookie_temp_file)
            except:
                pass

    def download_video_file(self, youtube_url: str, output_path: str = None, status_callback=None) -> tuple:
        """
        Downloads video from YouTube and returns the filepath and metadata.
        """
        if output_path is None:
             output_path = os.path.join(self.temp_dir, "%(id)s.%(ext)s")

        ydl_opts = {
            # Selector robusto para descarga de video (prioriza 480p)
            'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]/bestvideo+bestaudio/best',
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': False,
            'verbose': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'geo_bypass': True,
            'source_address': '0.0.0.0',
            'extractor_args': {
                'youtube': {
                    'player_client': ['web', 'android', 'ios', 'mweb'],
                }
            }
        }
        
        ydl_opts['logger'] = YtDlpLogger(status_callback)

        # 1. Intentar con cookies
        cookie_file = self._get_cookiefile()
        if cookie_file:
            print(f"DEBUG: download_video_file intentando con cookies: {cookie_file}")
            ydl_opts['cookiefile'] = cookie_file
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    print(f"Descargando video de: {youtube_url} (con cookies)")
                    info = ydl.extract_info(youtube_url, download=True)
                    formats = info.get('formats', [])
                    if any(f.get('vcodec') != 'none' for f in formats):
                        filename = ydl.prepare_filename(info)
                        # ... validación de archivo existente ...
                        if self._verify_downloaded_file(filename):
                            return filename, info
                    print("⚠️ Descarga con cookies no encontró video. Intentando sin cookies...")
            except Exception as e:
                print(f"⚠️ Intento con cookies falló: {e}. Intentando sin cookies...")

        # 2. Intentar sin cookies
        print("DEBUG: download_video_file intentando descarga anónima...")
        ydl_opts.pop('cookiefile', None)
        ydl_opts.pop('cookiesfrombrowser', None)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Descargando video de: {youtube_url} (anónimo)")
            info = ydl.extract_info(youtube_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Verificar y buscar el archivo final (a veces cambia extensión)
            if not os.path.exists(filename):
                base = os.path.splitext(filename)[0]
                import glob
                files = glob.glob(f"{base}.*")
                if files: filename = files[0]
            
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                print(f"Video descargado en: {filename} (Tamaño: {size} bytes)")
            else:
                print(f"❌ ERROR: No se encontró el archivo: {filename}")
                
            return filename, info

    def _verify_downloaded_file(self, filename: str) -> bool:
        """Verifica que el archivo exista y no esté vacío."""
        if not os.path.exists(filename):
            base = os.path.splitext(filename)[0]
            import glob
            files = glob.glob(f"{base}.*")
            if files: filename = files[0]
        
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            return True
        return False

    def upload_file_to_backend(self, filepath: str, upload_endpoint: str) -> str:
        """Uploads the file to the backend and returns the public URL."""
        print(f"Subiendo {filepath} a {upload_endpoint}...")
        try:
            with open(filepath, 'rb') as f:
                # Add explict MIME type
                files = {'file': (os.path.basename(filepath), f, 'video/mp4')}
                # You can specify a bucket via query param: ?bucket=reels if not in endpoint
                response = requests.post(upload_endpoint, files=files)
            
            if response.status_code == 200:
                data = response.json()
                public_url = data.get('url')
                print(f"Subida exitosa: {public_url}")
                return public_url
            else:
                raise Exception(f"Upload failed: {response.text}")
        except Exception as e:
            print(f"Error subiendo archivo: {e}")
            raise e

