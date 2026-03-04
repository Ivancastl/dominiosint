# DominiosINT

Aplicación web en Flask para monitorear dominios registrados por día y filtrarlos por palabras clave.

Permite consultar rangos de fechas y detectar dominios relacionados a términos específicos para tareas de OSINT, investigación o monitoreo.

---

## 🚀 Características

- Búsqueda por múltiples palabras clave
- Filtro inteligente (normaliza acentos y mayúsculas)
- Rango de fechas personalizable
- Exportación de resultados en archivo `.txt`
- Interfaz web simple y rápida
- Procesamiento optimizado para evitar duplicados

---

## 🧠 ¿Cómo funciona?

1. Consulta archivos diarios de dominios desde un repositorio público.
2. Limpia y normaliza texto.
3. Filtra dominios que contengan las palabras clave.
4. Agrupa resultados por fecha.
5. Permite descargar coincidencias.

---

## 🛠️ Instalación

Clona el repositorio:

```bash
git clone https://github.com/Ivancastl/dominiosint.git
```

2. Navega al directorio del proyecto:  
```bash
cd dominiosint
```

3. Instala las dependencias del proyecto (si tu proyecto tiene `requirements.txt`):  
```bash
pip install -r requirements.txt
```

4. Ejecuta la aplicación:  
```bash
python flask_app.py
```

5. Abre el navegador en:  
```
http://127.0.0.1:5000
```