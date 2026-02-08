from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import asyncio
import uuid
import json
import os
import time
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from video_transcriber import VideoTranscriber

# Initialize global transcriber instance
print("Initializing VideoTranscriber...")
transcriber = VideoTranscriber()

app = FastAPI(title="DanteStudio Transcription API", version="1.0.0")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar según tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend) - MOVED TO END
# app.mount("/", StaticFiles(directory=".", html=True), name="static")

# Configuración
GO_API_URL = os.getenv("GO_API_URL", "https://dantexxi-api.onrender.com")

# Modelos Pydantic
class TranscriptionRequest(BaseModel):
    url: str
    type: str = "youtube"
    language: str = "it"
    save_to_db: bool = True

class TranscriptionResponse(BaseModel):
    id: str
    status: str
    message: str

class TranscriptionStatus(BaseModel):
    id: str
    status: str
    progress: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Almacenamiento en memoria para transcripciones
transcriptions = {}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "transcription-api"}

@app.post("/transcribe", response_model=TranscriptionResponse)
async def start_transcription(request: TranscriptionRequest, background_tasks: BackgroundTasks):
    # Generar ID único
    task_id = str(uuid.uuid4())
    
    # Crear entrada inicial
    transcriptions[task_id] = {
        "id": task_id,
        "status": "pending",
        "progress": 0,
        "result": None,
        "error": None
    }
    
    # Iniciar transcripción en background
    background_tasks.add_task(process_transcription, task_id, request)
    
    return TranscriptionResponse(
        id=task_id,
        status="pending",
        message="Transcripción iniciada"
    )

@app.get("/status/{task_id}", response_model=TranscriptionStatus)
async def get_transcription_status(task_id: str):
    if task_id not in transcriptions:
        raise HTTPException(status_code=404, detail="Transcripción no encontrada")
    
    return TranscriptionStatus(**transcriptions[task_id])

async def process_transcription(task_id: str, request: TranscriptionRequest):
    try:
        # Actualizar estado
        transcriptions[task_id]["status"] = "processing"
        transcriptions[task_id]["progress"] = 10
        
        # Nombre de archivo temporal para el JSON
        output_file = f"transcription_{task_id}.json"
        
        # Ejecutar transcripción (que es bloqueante) en un thread pool
        # para no bloquear el loop de eventos principal
        loop = asyncio.get_running_loop()
        success = await loop.run_in_executor(
            None, 
            lambda: transcriber.transcribe_video(request.url, output_file, optimize_for_ui=True)
        )
        
        if not success:
            raise Exception("La transcripción no se pudo completar")
            
        transcriptions[task_id]["progress"] = 90
        
        # Leer el resultado del JSON generado
        result_data = {}
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            # Limpiar archivo JSON temporal
            os.remove(output_file)
        else:
             raise Exception("No se generó el archivo de salida")

        transcriptions[task_id]["result"] = result_data
        
        # Si se debe guardar en la base de datos
        if request.save_to_db:
            try:
                # Enviar a la API de Go
                await send_to_go_api(result_data, task_id)
            except Exception as e:
                print(f"Error enviando a API de Go: {e}")
                transcriptions[task_id]["error"] = f"Transcripción completada, pero falló envío a BD: {str(e)}"
        
        # Marcar como completado
        transcriptions[task_id]["status"] = "completed"
        transcriptions[task_id]["progress"] = 100
        
    except Exception as e:
        transcriptions[task_id]["status"] = "error"
        transcriptions[task_id]["error"] = str(e)
        print(f"Error en transcripción {task_id}: {e}")

async def send_to_go_api(transcription_data: Dict[str, Any], task_id: str):
    """Envía los datos de transcripción a la API de Go"""
    try:
        # Preparar datos para el modelo de Go
        go_data = {
            "author": transcription_data.get("author", "DanteStudio"),
            "category": transcription_data.get("category", "Education"),
            "chiave": transcription_data.get("chiave", "Transcripción automática"),
            "chiaveTranslation": transcription_data.get("chiaveTranslation", "Transcripción automática"),
            "chiaveTranslationEN": transcription_data.get("chiaveTranslationEN", "Automatic transcription"),
            "chiaveTranslationPR": transcription_data.get("chiaveTranslationPR", "Transcrição automática"),
            "description": transcription_data.get("description", "Transcripción generada automáticamente"),
            "image": transcription_data.get("image", "default_thumbnail.jpg"),
            "lingua": transcription_data.get("lingua", "it"),
            "livello": transcription_data.get("livello", "A1"),
            "name": transcription_data.get("name", "Video Transcrito"),
            "url": transcription_data.get("source_url", "") or transcription_data.get("url", ""),
            "views": transcription_data.get("views", 0),
            "subtitles": transcription_data.get("subtitles", []),
            "duration": transcription_data.get("duration", ""),
            "visible": False,  # Por defecto no visible hasta que se publique
            "isPremium": False
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(f"{GO_API_URL}/v1/reels", json=go_data)
            
            if response.status_code == 201:  # 201 Created según tu API
                result = response.json()
                print(f"✅ Transcripción enviada a API de Go: ID {result.get('id')}")
                
                # Guardar el ID del reel para referencia futura
                transcriptions[task_id]["result"]["go_reel_id"] = result.get("id")
                
            else:
                print(f"⚠️ Error enviando a API de Go: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                
    except Exception as e:
        print(f"Error al enviar a API de Go: {e}")

# Serve index.html explicitly
@app.get("/")
async def read_index():
    return FileResponse('index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
