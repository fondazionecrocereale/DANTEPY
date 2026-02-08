#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba directa de la funcionalidad de optimización de subtítulos.
"""

from video_transcriber import VideoTranscriber
import json

def main():
    print("🔧 PRUEBA DE OPTIMIZACIÓN DE SUBTÍTULOS")
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
            "translationPR": "Eu acredito que é essencial falar aos jovens sua língua para não se esconder por trás do número, os dados estatísticos e matemáticos, acho que a mensagem é fazer com que todos consciem o respeito das reglas para torná -las internalizadas porque os jovens não estão inclinados a respeitar as reglas impostas",
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

if __name__ == "__main__":
    main()
