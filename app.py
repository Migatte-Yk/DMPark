"""
Aplicación Flask para predicción de ocupación de parqueaderos en Chía.
Interfaz web que permite seleccionar día, hora y zona para obtener predicciones.
"""

from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
from datetime import datetime
import os

# Usar backend no interactivo para matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

# ============================================================================
# 1. CARGAR MODELO Y ENCODERS
# ============================================================================

def cargar_modelo_y_encoders():
    """Carga el modelo entrenado y los label encoders."""
    try:
        with open('modelo_parqueo.pkl', 'rb') as f:
            modelo = pickle.load(f)
        with open('label_encoders.pkl', 'rb') as f:
            encoders = pickle.load(f)
        return modelo, encoders
    except FileNotFoundError:
        print("ERROR: Modelo o encoders no encontrados.")
        print("Por favor, ejecuta 'python train_model.py' primero.")
        return None, None

# Cargar al iniciar la aplicación
modelo, encoders = cargar_modelo_y_encoders()

# ============================================================================
# 2. FUNCIONES AUXILIARES
# ============================================================================

def generar_grafico_base64(df_zone_day, zona, dia):
    """
    Genera un gráfico de ocupación por hora y lo retorna como base64.
    Esto permite mostrarlo directamente en HTML sin archivos temporales.
    """
    # Filtrar datos para la zona y día especificados
    datos_filtrados = df_zone_day[
        (df_zone_day['zona'] == zona) & 
        (df_zone_day['dia_semana'] == dia)
    ]
    
    if len(datos_filtrados) == 0:
        return None
    
    # Calcular ocupación promedio por hora
    ocupacion_por_hora = datos_filtrados.groupby('hora')['ocupacion_encoded'].mean()
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Colores según el nivel de ocupación
    colores = ['green' if x < 1 else 'yellow' if x < 2 else 'red' 
               for x in ocupacion_por_hora.values]
    
    ax.bar(ocupacion_por_hora.index, ocupacion_por_hora.values, color=colores, alpha=0.7)
    ax.set_xlabel('Hora del día', fontsize=12)
    ax.set_ylabel('Nivel de ocupación (promedio)', fontsize=12)
    ax.set_title(f'Ocupación por hora - {zona} ({dia})', fontsize=14, fontweight='bold')
    ax.set_xticks(range(6, 23))
    ax.grid(axis='y', alpha=0.3)
    
    # Agregar líneas de referencia
    ax.axhline(y=1, color='green', linestyle='--', alpha=0.3, label='Baja')
    ax.axhline(y=1.5, color='yellow', linestyle='--', alpha=0.3, label='Media')
    ax.axhline(y=2, color='red', linestyle='--', alpha=0.3, label='Alta')
    ax.legend()
    
    plt.tight_layout()
    
    # Convertir a base64
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return f"data:image/png;base64,{img_base64}"

def obtener_recomendacion(ocupacion_predicha, zona, hora):
    """Genera una recomendación amigable basada en la predicción."""
    zonas_recomendadas = {
        'Centro': 'Universidad o Alcaldía',
        'Universidad': 'Alcaldía o Parque Principal',
        'Alcaldía': 'Universidad o Parque Principal',
        'Parque Principal': 'Centro o Alcaldía'
    }
    
    if ocupacion_predicha == 'Alta':
        recom = f"Ocupación CRÍTICA. Intenta en {zonas_recomendadas[zona]} donde suele haber menos autos a esta hora."
    elif ocupacion_predicha == 'Media':
        recom = f"Moderadamente ocupada. Si lo deseas, prueba en {zonas_recomendadas[zona]}."
    else:  # Baja
        recom = f"Gran disponibilidad de parqueaderos. Puedes aparcar cómodamente aquí."
    
    return recom

# ============================================================================
# 3. RUTAS FLASK
# ============================================================================

@app.route('/')
def landing():
    """Ruta principal: muestra la landing page del proyecto."""
    return render_template('landing.html')

@app.route('/prediccion')
def prediccion():
    """Ruta del formulario de predicción."""
    if modelo is None:
        return """
        <div style="text-align: center; margin-top: 50px; font-family: Arial;">
            <h2>❌ Error: Modelo no cargado</h2>
            <p>Ejecuta primero: <code>python train_model.py</code></p>
        </div>
        """, 500

    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    horas = list(range(6, 23))
    zonas = ['Centro', 'Universidad', 'Alcaldía', 'Parque Principal']

    return render_template('index.html', dias=dias, horas=horas, zonas=zonas)

@app.route('/predecir', methods=['POST'])
def predecir():
    """
    Ruta para procesar predicciones.
    Recibe día, hora y zona, retorna predicción y gráfico.
    """
    if modelo is None:
        return jsonify({'error': 'Modelo no disponible'}), 500
    
    try:
        # Obtener datos del formulario
        dia = request.form.get('dia_semana')
        hora = int(request.form.get('hora'))
        zona = request.form.get('zona')
        
        # Validar entrada
        if not all([dia, zona]):
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        # Codificar entrada
        X_input = np.array([[
            encoders['dia_semana'].transform([dia])[0],
            hora,
            encoders['zona'].transform([zona])[0]
        ]])
        
        # Hacer predicción
        prediccion_encoded = modelo.predict(X_input)[0]
        prediccion_proba = modelo.predict_proba(X_input)[0]
        
        # Decodificar predicción
        ocupacion = encoders['ocupacion'].inverse_transform([prediccion_encoded])[0]
        
        # Calcular confianza (probabilidad de la clase predicha)
        confianza = max(prediccion_proba) * 100
        
        # Obtener recomendación
        recomendacion = obtener_recomendacion(ocupacion, zona, hora)
        
        # Generar gráfico
        # Cargar dataset para contexto
        df_dataset = pd.read_csv(os.path.join('data', 'parqueo_chia.csv'))
        
        # Codificar ocupacion en el dataset para el gráfico
        df_dataset['ocupacion_encoded'] = encoders['ocupacion'].transform(
            df_dataset['ocupacion']
        )
        
        grafico_base64 = generar_grafico_base64(df_dataset, zona, dia)
        
        # Determinar emoji según ocupación
        emoji = {
            'Baja': '🟢',
            'Media': '🟡',
            'Alta': '🔴'
        }.get(ocupacion, '⚪')
        
        return render_template(
            'resultado.html',
            emoji=emoji,
            ocupacion=ocupacion,
            confianza=confianza,
            recomendacion=recomendacion,
            zona=zona,
            dia=dia,
            hora=hora,
            grafico=grafico_base64
        )
    
    except Exception as e:
        print(f"Error en predicción: {str(e)}")
        return jsonify({'error': f'Error en predicción: {str(e)}'}), 500

@app.route('/estadisticas')
def estadisticas():
    """Ruta para mostrar estadísticas generales del dataset."""
    try:
        df = pd.read_csv(os.path.join('data', 'parqueo_chia.csv'))
        
        # Generar gráfico de distribución de ocupación
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Gráfico 1: Distribución general de ocupación
        ocupacion_counts = df['ocupacion'].value_counts()
        colors = ['red' if x == 'Alta' else 'yellow' if x == 'Media' else 'green' 
                 for x in ocupacion_counts.index]
        axes[0, 0].bar(ocupacion_counts.index, ocupacion_counts.values, color=colors, alpha=0.7)
        axes[0, 0].set_title('Distribución de ocupación', fontweight='bold')
        axes[0, 0].set_ylabel('Registros')
        
        # Gráfico 2: Ocupación por zona
        zona_ocu = pd.crosstab(df['zona'], df['ocupacion'])
        zona_ocu.plot(kind='bar', ax=axes[0, 1], color=['green', 'yellow', 'red'], alpha=0.7)
        axes[0, 1].set_title('Ocupación por zona', fontweight='bold')
        axes[0, 1].set_ylabel('Registros')
        axes[0, 1].legend(title='Ocupación')
        
        # Gráfico 3: Ocupación por día
        dia_ocu = pd.crosstab(df['dia_semana'], df['ocupacion'])
        dia_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dia_ocu = dia_ocu.reindex(dia_order)
        dia_ocu.plot(kind='bar', ax=axes[1, 0], color=['green', 'yellow', 'red'], alpha=0.7)
        axes[1, 0].set_title('Ocupación por día', fontweight='bold')
        axes[1, 0].set_ylabel('Registros')
        axes[1, 0].legend(title='Ocupación')
        
        # Gráfico 4: Promedio de ocupación por hora
        df['ocupacion_encoded'] = encoders['ocupacion'].transform(df['ocupacion'])
        hora_ocu = df.groupby('hora')['ocupacion_encoded'].mean()
        axes[1, 1].plot(hora_ocu.index, hora_ocu.values, marker='o', linewidth=2, markersize=6)
        axes[1, 1].fill_between(hora_ocu.index, hora_ocu.values, alpha=0.3)
        axes[1, 1].set_title('Ocupación promedio por hora', fontweight='bold')
        axes[1, 1].set_xlabel('Hora del día')
        axes[1, 1].set_ylabel('Nivel de ocupación')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Convertir a base64
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
        img.seek(0)
        img_base64 = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        grafico = f"data:image/png;base64,{img_base64}"
        
        return render_template('estadisticas.html', grafico=grafico)
    
    except Exception as e:
        return f"Error generando estadísticas: {str(e)}", 500

# ============================================================================
# 4. INICIAR APLICACIÓN
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
