# 🅿️ Predictor de Ocupación de Parqueaderos - Chía

Aplicación web desarrollada con Python, Flask y Machine Learning que predice la ocupación de parqueaderos en el centro de Chía, Cundinamarca.

## 📋 Contenido del proyecto

```
proyecto_parqueo_chia/
│
├── app.py                  # Aplicación Flask principal
├── train_model.py          # Script de entrenamiento del modelo
├── requirements.txt        # Dependencias del proyecto
├── modelo_parqueo.pkl      # Modelo entrenado (se genera después de ejecutar train_model.py)
├── label_encoders.pkl      # Encoders de variables categóricas (se genera después de entrenar)
│
├── data/
│   └── parqueo_chia.csv    # Dataset sintético (se genera después de entrenar)
│
├── templates/
│   ├── base.html           # Template base con navbar compartida
│   ├── landing.html        # Landing page profesional del proyecto
│   ├── index.html          # Página del formulario de predicción
│   ├── resultado.html      # Página de resultado de predicción
│   └── estadisticas.html   # Página de estadísticas del dataset
│
├── static/
│   ├── style.css           # Estilos CSS para páginas de predicción
│   ├── css/
│   │   └── landing.css     # Estilos CSS para la landing page
│   └── js/
│       └── landing.js      # JavaScript para funcionalidades de landing
│
└── README.md               # Este archivo
```

## 🚀 Requisitos previos

- **Python 3.9 o superior**
- **pip** (gestor de paquetes de Python)
- Un navegador web moderno
- Visual Studio Code (recomendado)

## 📦 Instalación paso a paso

### 1. Clona o descarga este proyecto

```bash
cd c:\Users\tu_usuario\Documents\Universidad\DataMining
# Tu carpeta proyecto_parqueo_chia ya debe estar aquí
cd proyecto_parqueo_chia
```

### 2. Crea un entorno virtual (RECOMENDADO)

**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**En Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**En macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

**Dependencias que se instalarán:**
- Flask 2.3.2 - Framework web
- scikit-learn 1.3.0 - Machine Learning
- pandas 2.0.3 - Manejo de datos
- numpy 1.24.3 - Cálculos numéricos
- matplotlib 3.7.2 - Visualizaciones

## 🎓 Entrenar el modelo

Antes de ejecutar la aplicación web, debes entrenar el modelo:

```bash
python train_model.py
```

**¿Qué hace este script?**
1. Genera un dataset sintético de 800 registros con lógica realista
2. Crea columnas: día_semana, hora, zona, ocupacion
3. Implementa patrones reales:
   - Fines de semana más ocupados
   - Horas pico (8-10 AM, 12-2 PM, 5-7 PM)
   - Centro más ocupado que otras zonas
4. Entrena un modelo Random Forest con 100 árboles
5. Guarda el modelo como `modelo_parqueo.pkl`
6. Guarda los encoders como `label_encoders.pkl`
7. Guarda el dataset como `data/parqueo_chia.csv`

**Salida esperada:**
```
Generando dataset sintético...
✓ Dataset generado: data/parqueo_chia.csv
  Total de registros: 800

Distribución de ocupación:
Media    350
Baja     300
Alta     150

...

Entrenando modelo de Random Forest...
✓ Modelo entrenado correctamente
  Precisión en conjunto de prueba: 78.75%

Guardando artefactos del modelo...
✓ Modelo guardado: modelo_parqueo.pkl
✓ Encoders guardados: label_encoders.pkl

¡Entrenamiento completado exitosamente!
```

## ▶️ Ejecutar la aplicación web

Una vez entrenado el modelo:

```bash
python app.py
```

**Salida esperada:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Luego abre tu navegador en: **http://127.0.0.1:5000**

## 🎯 Funcionalidades principales

### 1. **Landing Page (/)** - Página de presentación profesional
- Hero section con título llamativo y llamada a la acción
- Sección explicando el problema real en Chía
- Pregunta problema del proyecto
- Objetivos general y específicos
- Tecnologías utilizadas con iconos
- Proceso de funcionamiento en 3 pasos
- Footer con información del proyecto

### 2. **Formulario de Predicción (/prediccion)**
- Formulario con tres selectores:
  - **Día de la semana:** Lunes a Domingo
  - **Hora:** 6:00 AM a 22:00 PM
  - **Zona:** Centro, Universidad, Alcaldía, Parque Principal
- Botón para hacer predicción

### 3. **Resultado de Predicción (/predecir - POST)**
Muestra:
- Emoji indicador (🟢 Baja, 🟡 Media, 🔴 Alta)
- Nivel de ocupación predicho
- Porcentaje de confianza del modelo
- Recomendación amigable personalizada
- Gráfico de ocupación por hora para esa zona y día

### 4. **Estadísticas (/estadisticas)**
Visualiza análisis completo del dataset:
- Distribución general de ocupación
- Ocupación por zona
- Ocupación por día
- Ocupación promedio por hora

## 📊 Estructura de datos

El dataset generado contiene:

| Campo | Valores | Descripción |
|-------|---------|-------------|
| `dia_semana` | Lunes-Domingo | Día de la semana |
| `hora` | 6-22 | Hora del día (enteros) |
| `zona` | Centro, Universidad, Alcaldía, Parque Principal | Zona de estacionamiento |
| `ocupacion` | Alta, Media, Baja | Nivel de ocupación (objetivo) |

## 🤖 Modelo de Machine Learning

**Algoritmo:** Random Forest Classifier
- **Árboles:** 100
- **Profundidad máxima:** 10
- **Precisión esperada:** 75-85%

El modelo aprende patrones como:
- Ocupación más alta en fines de semana
- Horas pico durante la mañana, mediodía y tarde
- Diferencias en ocupación por zona

## 🎨 Interfaz de usuario

- **Responsive:** Funciona en móviles, tablets y desktop
- **Bootstrap 5:** Interfaz moderna y atractiva
- **Emojis:** Indicadores visuales intuitivos
- **Gráficos:** Matplotlib integrado en base64

## 🔧 Solución de problemas

### Error: "Modelo o encoders no encontrados"
**Solución:** Ejecuta primero `python train_model.py`

### Error: "ModuleNotFoundError"
**Solución:** Verifica que instalaste las dependencias:
```bash
pip install -r requirements.txt
```

### Puerto 5000 en uso
**Solución:** Cambia el puerto en `app.py` línea 195:
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Usa otro puerto
```

### Entorno virtual no se activa
**Solución Windows (PowerShell):**
Si ves un error de "RemoteSigned", ejecuta:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📝 Archivos principales explicados

### `train_model.py`
Genera datos sintéticos y entrena el modelo. Ejecutar UNA SOLA VEZ.

**Pasos:**
1. Genera 800 registros con lógica realista
2. Codifica variables categóricas con LabelEncoder
3. Entrena Random Forest
4. Guarda modelo y encoders

### `app.py`
Aplicación Flask que sirve la interfaz web.

**Rutas principales:**
- `/` - Landing page profesional (GET)
- `/prediccion` - Formulario de predicción (GET)
- `/predecir` - Endpoint de predicción (POST)
- `/estadisticas` - Página de estadísticas (GET)
- `/estadisticas` - Página de estadísticas (GET)

### Templates HTML
- `index.html` - Formulario de entrada
- `resultado.html` - Página de resultado con gráfico
- `estadisticas.html` - Análisis del dataset

## 🖼️ Características de la UI

- ✅ Selectores con opciones validadas
- ✅ Gráficos generados dinámicamente
- ✅ Indicadores visuales de confianza
- ✅ Recomendaciones personalizadas
- ✅ Diseño responsive
- ✅ Navegación intuitiva

## 📚 Conceptos de Data Mining implementados

1. **Generación de datos sintéticos:** Simulación realista de patrones
2. **Codificación de variables:** Conversión de categóricas a numéricas
3. **División train/test:** 80% entrenamiento, 20% prueba
4. **Validación de modelo:** Métricas de precisión y reporte de clasificación
5. **Predicción:** Clasificación en nuevos datos
6. **Visualización:** Análisis exploratorio de datos

## 🎓 Notas pedagógicas

Este proyecto es educativo y demuestra:
- Ciclo completo de ML (datos → modelo → predicción)
- Integración de ML en aplicaciones web
- Buenas prácticas de código Python
- Interfaz web responsiva

## 📄 Licencia

Proyecto académico para materia de Data Mining.

## ✅ Checklist de uso

- [ ] Descargué el proyecto en `DataMining/proyecto_parqueo_chia/`
- [ ] Creé el entorno virtual con `python -m venv venv`
- [ ] Activé el entorno: `.\venv\Scripts\Activate.ps1` (Windows)
- [ ] Instalé dependencias: `pip install -r requirements.txt`
- [ ] Entrené el modelo: `python train_model.py`
- [ ] Ejecuté la app: `python app.py`
- [ ] Abrí http://127.0.0.1:5000 en el navegador

¡Listo! 🎉

## 🆘 Soporte

Si tienes problemas:
1. Verifica que Python 3.9+ está instalado: `python --version`
2. Confirma que estás en el entorno virtual (debe mostrar `(venv)` en la terminal)
3. Revisa los mensajes de error en la consola
4. Intenta reinstalar dependencias: `pip install --upgrade -r requirements.txt`

---

**Desarrollado con ❤️ para la materia de Data Mining**
