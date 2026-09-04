# Laboratorio 6 — Análisis de redes sociales (YouTube)

CC3084 – Data Science, Semestre II 2026. Ver enunciado completo en
`Laboratorio_6_Analisis_de_redes_sociales_YouTube_2026.md`.

## Contenido

- `Laboratorio_6_Avance.ipynb` — Avance entregado el 3 de septiembre de 2026
  (ejercicios 1 a 4: carga e integración, calidad y limpieza, análisis
  exploratorio, red bipartita autor–video).
- `Laboratorio_6_Completo.ipynb` — Documento final completo (ejercicios 1 a
  10: incluye además proyecciones autor-autor y video-video, topología y
  fragmentación, detección de comunidades, centralidad y participantes
  puente, análisis de sentimiento, e interpretación/limitaciones/
  conclusiones).
- `data/youtube_videos.csv`, `data/youtube_comments.csv` — datos originales.
- `data/red_bipartita_nodos.csv`, `data/red_bipartita_aristas.csv` — tabla de
  nodos y aristas de la red bipartita autor–video.
- `data/*.png` — visualizaciones de la red bipartita, las proyecciones y las
  comunidades, generadas por `Laboratorio_6_Completo.ipynb`.
- `informe/informe.md` — informe completo del laboratorio en Markdown (con
  las mismas figuras en `informe/img/`), listo para convertirse a Word u
  otro formato de entrega.

## Requisitos

- Python 3.11 o 3.12. Se recomienda evitar 3.13+/3.14 en Windows: algunas
  dependencias de este proyecto (en particular las que trae `pysentimiento`
  para el análisis de sentimiento) no publican todavía binarios estables
  para esas versiones.
- Conexión a internet la primera vez que se ejecuta el notebook completo:
  descarga el listado de stopwords de `nltk` y el modelo de sentimiento en
  español de `pysentimiento` (RoBERTuito, ~500 MB, se cachea localmente para
  ejecuciones posteriores).

## Configuración del entorno

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (Git Bash) / Linux / macOS
source .venv/Scripts/activate   # o: source .venv/bin/activate

pip install -r requirements.txt
```

## Ejecutar el análisis

```bash
jupyter notebook Laboratorio_6_Completo.ipynb
```

Ejecutar todas las celdas en orden (`Kernel > Restart & Run All`). Ambos
notebooks leen los CSV desde `data/` con rutas relativas, por lo que deben
ejecutarse desde la raíz del repositorio. La primera ejecución del notebook
completo tarda más por la descarga del modelo de sentimiento; ejecuciones
posteriores lo reutilizan desde la caché local de Hugging Face.
