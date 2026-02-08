#!/usr/bin/env python3
"""
Script interactivo para transcribir videos de YouTube
"""

from video_transcriber import VideoTranscriber
import os
import sys

def main():
    print("Transcriptor de Videos de YouTube")
    print("=" * 50)

    # Crear instancia del transcriptor
    transcriber = VideoTranscriber()

    try:
        # Solicitar URL del video
        while True:
            url = input("\nIngresa la URL del video de YouTube: ").strip()
            if url:
                break
            print("La URL no puede estar vacia. Intentelo de nuevo.")

        # Solicitar nombre del archivo de salida
        while True:
            output_file = input("\nIngresa el nombre del archivo JSON de salida (sin extension): ").strip()
            if output_file:
                if not output_file.endswith('.json'):
                    output_file += '.json'
                break
            print("El nombre del archivo no puede estar vacio. Intentelo de nuevo.")

        # Verificar si el archivo ya existe
        if os.path.exists(output_file):
            respuesta = input(f"\nEl archivo '{output_file}' ya existe. Quieres sobrescribirlo? (s/n): ").strip().lower()
            if respuesta not in ['s', 'si', 'yes', 'y']:
                print("Operacion cancelada.")
                return

        print(f"\nIniciando transcripcion de: {url}")
        print(f"Archivo de salida: {output_file}")
        print("\nEsto puede tomar varios minutos dependiendo de la duracion del video...")
        print("-" * 60)

        # Realizar la transcripción
        if "youtube.com" in url or "youtu.be" in url:
            success = transcriber.transcribe_video(url, output_file)
        else:
            success = transcriber.transcribe_audio_from_url(url, output_file)

        if success:
            print("\nTranscripcion completada exitosamente!")
            print(f"Archivo guardado: {output_file}")

            # Mostrar estadísticas básicas
            try:
                import json
                with open(output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    num_subtitles = len(data.get('subtitles', []))
                    print(f"Numero de subtitulos generados: {num_subtitles}")
            except:
                pass

        else:
            print("\nError durante la transcripcion. Revisa los mensajes de error arriba.")

    except KeyboardInterrupt:
        print("\n\nOperacion cancelada por el usuario.")
    except Exception as e:
        print(f"\nError inesperado: {e}")
    finally:
        # Limpiar archivos temporales
        print("\nLimpiando archivos temporales...")
        transcriber.cleanup()
        print("Limpieza completada.")

if __name__ == "__main__":
    main()