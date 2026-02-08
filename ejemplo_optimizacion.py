#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo de uso de la nueva funcionalidad de optimización de subtítulos
para mejor legibilidad en la UI de DanteStudio.

Este script demuestra cómo dividir automáticamente segmentos largos
en partes más pequeñas y legibles, respetando los tiempos originales.
"""

from video_transcriber import VideoTranscriber
import json

def ejemplo_optimizacion_manual():
    """
    Ejemplo de optimización manual de subtítulos existentes.
    Útil cuando ya tienes un archivo JSON y quieres optimizarlo.
    """
    print("🔧 EJEMPLO DE OPTIMIZACIÓN MANUAL DE SUBTÍTULOS")
    print("=" * 60)
    
    # Crear instancia del transcriptor
    transcriber = VideoTranscriber()
    
    # Cargar subtítulos existentes (ejemplo del archivo transcription.json)
    subtitles_ejemplo = [
        {
            "text": "ritengo sia fondamentale parlare ai giovani il loro linguaggio non nascondersi dietro il numero la statistica i dati aridi e matematici credo che il messaggio sia quello di rendere tutti più consapevoli del rispetto delle regole di farle interiorizzare perché i giovani non sono propensi a rispettare le regoles imposte",
            "startTime": "00:00:00.000",
            "endTime": "00:00:22.120",
            "translation": "Creo que es esencial hablar con los jóvenes su idioma para no esconderse detrás del número de datos estadísticas y matemáticos, creo que el mensaje es hacer que todos sean más conscientes del respeto de las reglas para hacerlas internalizar porque los jóvenes no están inclinados a respetar las reglas impuestas",
            "translationPR": "Eu acredito que é essencial falar aos jovens sua língua para não se esconder por trás do número, os dados estatísticos e matemáticos, acho que a mensagem é fazer com que todos consciem o respeito das regras para torná -las internalizadas porque os jovens não estão inclinados a respeitar as regras impostas",
            "translationEN": "I believe it is essential to speak to young people their language not to hide behind the number the statistics arid and mathematical data I think the message is to make everyone more aware of the respect of the rules to make them internalize because young people are not inclined to respect the rules imposed",
            "isWordKey": False
        }
    ]
    
    print(f"📝 Segmento original:")
    print(f"   Texto: {subtitles_ejemplo[0]['text'][:100]}...")
    print(f"   Duración: {subtitles_ejemplo[0]['startTime']} - {subtitles_ejemplo[0]['endTime']}")
    print(f"   Caracteres: {len(subtitles_ejemplo[0]['text'])}")
    print()
    
    # Optimizar subtítulos para mejor legibilidad
    print("🔧 Optimizando para mejor legibilidad...")
    subtitles_optimizados = transcriber._optimize_subtitles_for_ui(subtitles_ejemplo, max_chars=80)
    
    print(f"✅ Subtítulos optimizados: {len(subtitles_optimizados)} segmentos")
    print()
    
    # Mostrar resultados
    for i, segmento in enumerate(subtitles_optimizados):
        print(f"📝 Segmento {i+1}:")
        print(f"   Texto: {segmento['text']}")
        print(f"   Tiempo: {segmento['startTime']} - {segmento['endTime']}")
        print(f"   Caracteres: {len(segmento['text'])}")
        print()
    
    # Guardar resultado optimizado
    resultado_optimizado = {
        "url": "Ejemplo de optimización",
        "name": "Subtítulos optimizados para UI",
        "description": "Ejemplo de división automática de segmentos largos",
        "category": "ejemplo",
        "image": "",
        "author": "Sistema automático",
        "chiave": "optimización",
        "livello": "intermedio",
        "lingua": "it",
        "views": 0,
        "chiaveTranslation": "optimización",
        "chiaveTranslationEN": "optimization",
        "chiaveTranslationPR": "otimização",
        "subtitles": subtitles_optimizados
    }
    
    with open("transcription_optimizada.json", "w", encoding="utf-8") as f:
        json.dump(resultado_optimizado, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Resultado guardado en: transcription_optimizada.json")
    print()
    
    # Limpiar recursos
    transcriber.cleanup()

def ejemplo_transcripcion_con_optimizacion():
    """
    Ejemplo de transcripción completa con optimización automática.
    """
    print("🎬 EJEMPLO DE TRANSCRIPCIÓN CON OPTIMIZACIÓN AUTOMÁTICA")
    print("=" * 60)
    
    # Crear instancia del transcriptor
    transcriber = VideoTranscriber()
    
    try:
        # Ejemplo con un video de YouTube (reemplaza con una URL real)
        video_url = "https://www.youtube.com/watch?v=example"
        
        print(f"🎥 Transcribiendo video: {video_url}")
        print("⚠️  NOTA: Este es un ejemplo. Reemplaza la URL con un video real.")
        print()
        
        # Transcribir con optimización automática (por defecto)
        print("🔧 La optimización automática está habilitada por defecto")
        print("   Los segmentos largos se dividirán automáticamente")
        print("   para mejor legibilidad en la UI.")
        print()
        
        # Para deshabilitar la optimización (si es necesario):
        # success = transcriber.transcribe_video(video_url, "transcription_sin_optimizar.json", optimize_for_ui=False)
        
        # Para habilitar la optimización (por defecto):
        # success = transcriber.transcribe_video(video_url, "transcription_optimizada.json", optimize_for_ui=True)
        
        print("✅ Transcripción completada con optimización automática")
        print("   Los subtítulos están listos para usar en tu app Flutter")
        
    except Exception as e:
        print(f"❌ Error en el ejemplo: {e}")
    
    finally:
        # Limpiar recursos
        transcriber.cleanup()

def mostrar_configuracion_optimizacion():
    """
    Muestra las opciones de configuración para la optimización.
    """
    print("⚙️  CONFIGURACIÓN DE OPTIMIZACIÓN")
    print("=" * 60)
    
    print("🔧 Parámetros configurables:")
    print("   - max_chars: Máximo de caracteres por segmento (por defecto: 80)")
    print("   - optimize_for_ui: Habilitar/deshabilitar optimización (por defecto: True)")
    print()
    
    print("📱 Beneficios para tu app Flutter:")
    print("   ✅ Texto más legible en pantallas pequeñas")
    print("   ✅ Mejor experiencia de usuario")
    print("   ✅ Tiempos sincronizados perfectamente")
    print("   ✅ Traducciones preservadas")
    print()
    
    print("🎯 Casos de uso:")
    print("   - Videos con habla rápida o larga")
    print("   - Entrevistas o presentaciones")
    print("   - Cualquier contenido con segmentos largos")
    print()
    
    print("💡 Recomendaciones:")
    print("   - max_chars=80: Para móviles y pantallas pequeñas")
    print("   - max_chars=100: Para tablets y pantallas medianas")
    print("   - max_chars=120: Para pantallas grandes (desktop)")

def main():
    """
    Función principal que ejecuta todos los ejemplos.
    """
    print("🚀 DANTESTUDIO - OPTIMIZACIÓN DE SUBTÍTULOS")
    print("=" * 60)
    print()
    
    while True:
        print("📋 Selecciona una opción:")
        print("1. Ejemplo de optimización manual")
        print("2. Ejemplo de transcripción con optimización")
        print("3. Mostrar configuración de optimización")
        print("4. Salir")
        print()
        
        opcion = input("Ingresa tu opción (1-4): ").strip()
        print()
        
        if opcion == "1":
            ejemplo_optimizacion_manual()
        elif opcion == "2":
            ejemplo_transcripcion_con_optimizacion()
        elif opcion == "3":
            mostrar_configuracion_optimizacion()
        elif opcion == "4":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida. Intenta de nuevo.")
        
        print()
        input("Presiona Enter para continuar...")
        print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    main()
