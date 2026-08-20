# 🍔 Metacomida

Juego multijugador educativo sobre la **industria alimentaria**, diseñado para **16 participantes organizados en 4 equipos de 4**.

El presentador controla la partida desde su celular y cada equipo tiene un líder que responde desde otro celular.

## 🎮 Mecánica

- 4 equipos de 4 personas.
- 1 líder por equipo.
- Cronómetro de **15 segundos** por pregunta.
- Solo las respuestas correctas suman puntos.
- Correcta entre 0 y 5 s: **+3 PI**.
- Correcta después de 5 y hasta 10 s: **+2 PI**.
- Correcta después de 10 y hasta 15 s: **+1 PI**.
- Incorrecta o sin respuesta: **0 PI**.
- Cada equipo puede enviar una sola respuesta por pregunta.
- Marcador, tiempos, podio y ganador automáticos.

## 📱 Rutas

Una vez publicado:

- Presentador: `/presentador`
- Líder general: `/lider`
- Equipo 1: `/lider?equipo=1`
- Equipo 2: `/lider?equipo=2`
- Equipo 3: `/lider?equipo=3`
- Equipo 4: `/lider?equipo=4`
- Estado del servidor: `/health`

## 🔐 PIN del presentador

El servidor usa la variable de entorno `PRESENTER_PIN`.

Si no se configura, el PIN predeterminado es `2468`. Para publicar el juego conviene definir otro PIN en Render.

## ☁️ Render

El repositorio incluye `render.yaml` para desplegar Metacomida como Web Service de Python.

Configuración equivalente:

- Runtime: Python
- Plan: Free
- Build command: `pip install -r requirements.txt`
- Start command: `python metacomida_server.py`
- Health check: `/health`
- Variable secreta: `PRESENTER_PIN`

El servidor usa automáticamente la variable `PORT` proporcionada por el hosting.

## 🧪 Ejecutar localmente

```bash
python metacomida_server.py
```

Después abre `http://localhost:8080/presentador`.

## ✨ Diseño

Incluye lluvia animada de hamburguesas, música de fondo sintetizada, efectos de sonido, interfaz móvil, enlaces para líderes, marcador y podio final.

> Nota: el estado de la partida se mantiene en memoria. Si el servidor se reinicia durante una partida, el marcador se reinicia.
