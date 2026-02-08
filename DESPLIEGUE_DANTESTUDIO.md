# 🚀 **Guía de Despliegue Completo - DanteStudio**

## **📋 Estado Actual del Proyecto**

### **✅ APIs Desplegadas:**
- **API de Go**: `https://dantexxi-api.onrender.com` ✅
- **API de Python**: Pendiente de desplegar en Render.com
- **Flutter Web**: Pendiente de desplegar

### **🔧 Archivos Listos:**
- `api_transcriber.py` - API de transcripción con FastAPI
- `requirements_api.txt` - Dependencias de Python
- `render.yaml` - Configuración para Render.com
- `dante_studio_app.dart` - Aplicación Flutter (URLs actualizadas)

## **🌐 Paso 1: Desplegar API de Python en Render.com**

### **1.1 Ir a Render.com Dashboard**
1. Ve a [dashboard.render.com](https://dashboard.render.com)
2. Inicia sesión con tu cuenta
3. Haz clic en **"New +"** → **"Web Service"**

### **1.2 Conectar Repositorio**
1. **Conecta tu repositorio**: `fondazionecrocereale/DanteXXI-PYTHON`
2. **Selecciona rama**: `main`
3. **Render detectará automáticamente** el `render.yaml`

### **1.3 Configuración Automática**
Render debería configurar automáticamente:
- **Environment**: Python
- **Build Command**: `pip install -r requirements_api.txt`
- **Start Command**: `uvicorn api_transcriber:app --host 0.0.0.0 --port 8000`
- **Health Check Path**: `/health`

### **1.4 Variables de Entorno**
Verifica que estén configuradas:
```bash
GO_API_URL=https://dantexxi-api.onrender.com
CORS_ORIGINS=*
PORT=8000
```

### **1.5 Desplegar**
1. Haz clic en **"Create Web Service"**
2. Espera a que termine el build (puede tomar 5-10 minutos)
3. Anota la URL generada: `https://tu-api-python.onrender.com`

## **📱 Paso 2: Desplegar Flutter Web**

### **2.1 Opción A: Render.com (Recomendado)**
1. **Nuevo Web Service** en Render.com
2. **Environment**: Static Site
3. **Build Command**: `flutter build web --release`
4. **Publish Directory**: `build/web`

### **2.2 Opción B: GitHub Pages**
1. **Build de Flutter**:
   ```bash
   flutter build web --base-href /tu-repo/
   ```
2. **Subir a GitHub Pages** desde la rama `gh-pages`

### **2.3 Opción C: Netlify**
1. **Conectar repositorio** a Netlify
2. **Build Command**: `flutter build web`
3. **Publish Directory**: `build/web`

## **🔗 Paso 3: Verificar Integración**

### **3.1 Probar APIs**
```bash
# API de Go
curl https://dantexxi-api.onrender.com/health

# API de Python
curl https://tu-api-python.onrender.com/health
```

### **3.2 Probar Flutter Web**
1. Abre tu aplicación Flutter desplegada
2. Intenta crear un reel
3. Verifica que la transcripción funcione
4. Confirma que se guarde en la base de datos

## **⚙️ Paso 4: Configuración de Producción**

### **4.1 Variables de Entorno en Render.com**
```bash
# API de Python
GO_API_URL=https://dantexxi-api.onrender.com
CORS_ORIGINS=https://tu-flutter-web.onrender.com

# API de Go (si necesitas actualizar)
CORS_ORIGIN=https://tu-flutter-web.onrender.com
```

### **4.2 CORS Configuration**
Si tienes problemas de CORS, actualiza en ambas APIs:
```go
// Go API
handlers.AllowedOrigins([]string{
    "https://tu-flutter-web.onrender.com",
    "http://localhost:3000" // Para desarrollo local
})
```

```python
# Python API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tu-flutter-web.onrender.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## **🧪 Paso 5: Testing y Debugging**

### **5.1 Health Checks**
- **API de Go**: `/health`
- **API de Python**: `/health`
- **Flutter Web**: Verificar que cargue correctamente

### **5.2 Logs de Render.com**
1. Ve a tu servicio en Render.com
2. Haz clic en **"Logs"**
3. Verifica que no haya errores de build o runtime

### **5.3 Testing de Transcripción**
1. **Crear reel** desde Flutter
2. **Iniciar transcripción** con URL de YouTube
3. **Monitorear progreso** en tiempo real
4. **Verificar resultado** en la base de datos

## **📊 Paso 6: Monitoreo y Mantenimiento**

### **6.1 Métricas de Render.com**
- **Uptime**: Verificar que las APIs estén siempre disponibles
- **Response Time**: Monitorear tiempos de respuesta
- **Error Rate**: Revisar logs de errores

### **6.2 Base de Datos**
- **Conexiones**: Verificar que no se agoten las conexiones
- **Performance**: Monitorear consultas lentas
- **Backup**: Configurar backups automáticos

## **🚨 Solución de Problemas Comunes**

### **Problema 1: Build Falla en Render.com**
```bash
# Verificar requirements_api.txt
pip install -r requirements_api.txt

# Verificar sintaxis Python
python -m py_compile api_transcriber.py
```

### **Problema 2: CORS Errors**
```bash
# Verificar variables de entorno
echo $CORS_ORIGINS

# Verificar configuración en ambas APIs
```

### **Problema 3: Timeout en Transcripciones**
```bash
# Render.com tiene timeout de 30 segundos
# Para transcripciones largas, usar colas de trabajo
```

### **Problema 4: Base de Datos No Conecta**
```bash
# Verificar DATABASE_URL en Render.com
# Verificar que Supabase esté activo
```

## **🎯 Checklist de Despliegue**

- [ ] **API de Python** desplegada en Render.com
- [ ] **Flutter Web** desplegado y funcionando
- [ ] **Variables de entorno** configuradas correctamente
- [ ] **CORS** configurado para permitir comunicación
- [ ] **Health checks** respondiendo correctamente
- [ ] **Transcripción** funcionando end-to-end
- [ ] **Base de datos** guardando reels correctamente
- [ ] **Flutter** mostrando reels publicados

## **🔗 URLs Finales**

Una vez desplegado todo:
- **API de Go**: `https://dantexxi-api.onrender.com`
- **API de Python**: `https://tu-api-python.onrender.com`
- **Flutter Web**: `https://tu-flutter-web.onrender.com`

## **📞 Soporte**

Si encuentras problemas:
1. **Revisar logs** en Render.com
2. **Verificar variables** de entorno
3. **Probar endpoints** individualmente
4. **Revisar CORS** configuration

¡Tu proyecto DanteStudio estará completamente funcional! 🚀
