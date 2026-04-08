"""
Script de entrenamiento del modelo de predicción de ocupación de parqueaderos en Chía.
Genera un dataset sintético realista y entrena un Random Forest.
Ejecutar este archivo una sola vez para generar el modelo y los encoders.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

# Configurar semilla aleatoria para reproducibilidad
np.random.seed(42)

# ============================================================================
# 1. GENERAR DATASET SINTÉTICO REALISTA
# ============================================================================

print("Generando dataset sintético...")

# Definir parámetros
n_registros = 800
dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
horas = list(range(6, 23))  # 6 a 22
zonas = ['Centro', 'Universidad', 'Alcaldía', 'Parque Principal']

# Crear listas para el dataset
datos = []

for _ in range(n_registros):
    dia = np.random.choice(dias_semana)
    hora = np.random.choice(horas)
    zona = np.random.choice(zonas)
    
    # Lógica realista para la ocupación
    # Base: asignar probabilidades según el día y la hora
    
    es_finde = dia in ['Sábado', 'Domingo']
    es_hora_pico = hora in [8, 9, 10, 12, 13, 14, 17, 18, 19]
    es_madrugada = hora < 8 or hora > 20
    
    # Probabilidades de ocupación Alta, Media, Baja
    if es_madrugada:
        # Madrugada: siempre baja ocupación
        ocupacion = 'Baja'
    elif zona == 'Centro':
        # Centro es la más ocupada
        if es_finde and es_hora_pico:
            ocupacion = np.random.choice(['Alta', 'Media'], p=[0.7, 0.3])
        elif es_finde:
            ocupacion = np.random.choice(['Media', 'Alta', 'Baja'], p=[0.5, 0.3, 0.2])
        elif es_hora_pico:
            ocupacion = np.random.choice(['Alta', 'Media', 'Baja'], p=[0.6, 0.3, 0.1])
        else:
            ocupacion = np.random.choice(['Media', 'Baja'], p=[0.6, 0.4])
    elif zona == 'Universidad':
        # Universidad tiene buena ocupación en semana
        if es_finde:
            ocupacion = np.random.choice(['Baja', 'Media'], p=[0.6, 0.4])
        elif es_hora_pico:
            ocupacion = np.random.choice(['Media', 'Alta'], p=[0.6, 0.4])
        else:
            ocupacion = np.random.choice(['Baja', 'Media'], p=[0.5, 0.5])
    elif zona == 'Alcaldía':
        # Alcaldía con ocupación moderada (horario laboral)
        if es_finde:
            ocupacion = 'Baja'
        elif 8 <= hora <= 17:
            ocupacion = np.random.choice(['Media', 'Baja'], p=[0.6, 0.4])
        else:
            ocupacion = 'Baja'
    else:  # Parque Principal
        # Parque Principal más ocupado en fines de semana
        if es_finde and 10 <= hora <= 18:
            ocupacion = np.random.choice(['Media', 'Alta'], p=[0.7, 0.3])
        elif es_finde:
            ocupacion = np.random.choice(['Baja', 'Media'], p=[0.6, 0.4])
        else:
            ocupacion = 'Baja'
    
    datos.append({
        'dia_semana': dia,
        'hora': hora,
        'zona': zona,
        'ocupacion': ocupacion
    })

# Crear DataFrame
df = pd.DataFrame(datos)

# Guardar dataset en CSV
csv_path = os.path.join('data', 'parqueo_chia.csv')
df.to_csv(csv_path, index=False, encoding='utf-8')
print(f"✓ Dataset generado: {csv_path}")
print(f"  Total de registros: {len(df)}")
print(f"\nDistribución de ocupación:")
print(df['ocupacion'].value_counts())
print(f"\nPrimeras 5 filas del dataset:")
print(df.head())

# ============================================================================
# 2. PREPARAR DATOS Y ENTRENAR MODELO
# ============================================================================

print("\n" + "="*60)
print("Entrenando modelo de Random Forest...")
print("="*60)

# Separar features (X) de target (y)
X = df[['dia_semana', 'hora', 'zona']]
y = df['ocupacion']

# Crear encoders para variables categóricas
encoders = {}
X_encoded = X.copy()

# Codificar dia_semana
le_dia = LabelEncoder()
X_encoded['dia_semana'] = le_dia.fit_transform(X['dia_semana'])
encoders['dia_semana'] = le_dia

# Codificar zona
le_zona = LabelEncoder()
X_encoded['zona'] = le_zona.fit_transform(X['zona'])
encoders['zona'] = le_zona

# Codificar ocupacion (target)
le_ocupacion = LabelEncoder()
y_encoded = le_ocupacion.fit_transform(y)
encoders['ocupacion'] = le_ocupacion

# Dividir datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y_encoded, test_size=0.2, random_state=42
)

# Entrenar Random Forest
modelo = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)
modelo.fit(X_train, y_train)

# Evaluar modelo
y_pred = modelo.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n✓ Modelo entrenado correctamente")
print(f"  Precisión en conjunto de prueba: {accuracy:.2%}")
print(f"\nReporte de clasificación:")
print(classification_report(y_test, y_pred, target_names=le_ocupacion.classes_))

# ============================================================================
# 3. GUARDAR MODELO Y ENCODERS
# ============================================================================

print("\n" + "="*60)
print("Guardando artefactos del modelo...")
print("="*60)

# Guardar modelo
modelo_path = 'modelo_parqueo.pkl'
with open(modelo_path, 'wb') as f:
    pickle.dump(modelo, f)
print(f"✓ Modelo guardado: {modelo_path}")

# Guardar encoders
encoders_path = 'label_encoders.pkl'
with open(encoders_path, 'wb') as f:
    pickle.dump(encoders, f)
print(f"✓ Encoders guardados: {encoders_path}")

print("\n" + "="*60)
print("¡Entrenamiento completado exitosamente!")
print("El modelo está listo para hacer predicciones.")
print("="*60)
