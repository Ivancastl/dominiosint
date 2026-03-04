# app.py
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime, timedelta
import requests
import unicodedata
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['UPLOAD_FOLDER'] = 'temp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Asegurar que existe la carpeta temporal
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# -------------------------
# FUNCIONES DE LIMPIEZA
# -------------------------

def limpiar_texto(texto):
    """
    Quita acentos, pasa a minúsculas
    CONSERVA . y - para no romper dominios
    """
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = texto.lower()

    # permitir solo letras, números, . y -
    texto = ''.join(
        c for c in texto
        if c.isalnum() or c in ".-"
    )

    return texto

# -------------------------
# DESCARGA
# -------------------------

def descargar_archivo(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        print(f"Error descargando {url}: {e}")
        return None

# -------------------------
# BUSQUEDA
# -------------------------

def buscar_palabras_clave(texto, palabras):
    """
    Devuelve dominios únicos relacionados a keywords reales
    """
    dominios = set()
    lineas = texto.splitlines()

    # limpiar, deduplicar, filtrar palabras cortas
    palabras_limpias = list(set(limpiar_texto(p) for p in palabras))
    palabras_limpias = [p for p in palabras_limpias if len(p) >= 3]
    palabras_limpias.sort(key=len, reverse=True)  # primero las más largas

    for linea in lineas:
        # descartar líneas que no parezcan dominio
        if "." not in linea:
            continue

        linea_limpia = limpiar_texto(linea)

        for palabra in palabras_limpias:
            if palabra == linea_limpia or palabra in linea_limpia:
                dominios.add(linea.strip())
                break  # evita duplicados

    return sorted(dominios)

# -------------------------
# FECHAS
# -------------------------

def generar_fechas(fecha_inicio, fecha_fin):
    fechas = []
    actual = fecha_inicio
    while actual <= fecha_fin:
        fechas.append(actual.strftime("%Y-%m-%d"))
        actual += timedelta(days=1)
    return fechas

# -------------------------
# PROCESO PRINCIPAL
# -------------------------

def buscar_en_dias(palabras, fecha_inicio, fecha_fin, progress_callback=None):
    fechas = generar_fechas(fecha_inicio, fecha_fin)
    resultados = {}
    total_fechas = len(fechas)
    
    for idx, fecha in enumerate(fechas):
        url = f"https://raw.githubusercontent.com/ccas10ca-prog/domain/main/dominios/{fecha}.txt"
        
        if progress_callback:
            progress_callback(idx + 1, total_fechas, fecha)
        
        contenido = descargar_archivo(url)
        if not contenido:
            continue
        
        dominios = buscar_palabras_clave(contenido, palabras)
        
        if dominios:
            resultados[fecha] = dominios
    
    return resultados

# -------------------------
# RUTAS DE LA APLICACIÓN
# -------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar():
    try:
        data = request.json
        palabras = [p.strip() for p in data.get('palabras', '').split(',') if p.strip()]
        fecha_inicio_str = data.get('fecha_inicio')
        fecha_fin_str = data.get('fecha_fin')
        
        if not palabras or not fecha_inicio_str or not fecha_fin_str:
            return jsonify({'error': 'Todos los campos son requeridos'}), 400
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
            fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({'error': 'Formato de fecha incorrecto'}), 400
        
        # Ejecutar búsqueda
        resultados = buscar_en_dias(palabras, fecha_inicio, fecha_fin)
        
        # Guardar resultados en archivo temporal
        archivo_resultado = os.path.join(app.config['UPLOAD_FOLDER'], 'resultados.txt')
        with open(archivo_resultado, 'w', encoding='utf-8') as f:
            for fecha, dominios in resultados.items():
                f.write(f"📅 {fecha}\n")
                for dominio in dominios:
                    f.write(f"{dominio}\n")
                f.write("\n")
        
        return jsonify({
            'success': True,
            'resultados': resultados,
            'total_fechas': len(resultados),
            'total_dominios': sum(len(d) for d in resultados.values())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/descargar')
def descargar():
    try:
        archivo_resultado = os.path.join(app.config['UPLOAD_FOLDER'], 'resultados.txt')
        if os.path.exists(archivo_resultado):
            return send_file(archivo_resultado, as_attachment=True, download_name='coincidencias.txt')
        return jsonify({'error': 'No hay resultados para descargar'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)