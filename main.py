# ==========================================================
#  MY MARKET SERVER — Flask (для PythonAnywhere)
#  Отдаёт каталог приложений и сами файлы.
# ==========================================================

import os
import json
import hashlib

from flask import Flask, jsonify, send_from_directory, Response


# ==========================================================
#  НАСТРОЙКИ
# ==========================================================

БАЗА = os.path.dirname(os.path.abspath(__file__))

ПАПКА_ПРИЛОЖЕНИЙ = os.path.join(БАЗА, "apps")
ПАПКА_ИКОНОК = os.path.join(БАЗА, "icons")
ФАЙЛ_КАТАЛОГА = os.path.join(БАЗА, "catalog.json")

ВЕРСИЯ_СЕРВЕРА = "0.1.0"


# ==========================================================
#  ИНИЦИАЛИЗАЦИЯ
# ==========================================================

app = Flask(__name__)


def прочитать_каталог() -> dict:
    if not os.path.exists(ФАЙЛ_КАТАЛОГА):
        return {"приложения": []}
    try:
        with open(ФАЙЛ_КАТАЛОГА, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"приложения": [], "ошибка": str(e)}


def посчитать_хеш(путь: str) -> str:
    h = hashlib.sha256()
    with open(путь, "rb") as f:
        for блок in iter(lambda: f.read(8192), b""):
            h.update(блок)
    return h.hexdigest()


# ==========================================================
#  ЭНДПОИНТЫ
# ==========================================================

@app.route("/")
def корень():
    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>My Market Server</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #1e1e1e; color: #fff;
                display: flex; align-items: center;
                justify-content: center;
                height: 100vh; margin: 0;
            }}
            .card {{
                background: #2b2b2b; padding: 40px 60px;
                border-radius: 16px; text-align: center;
            }}
            h1 {{ margin: 0 0 10px 0; }}
            .status {{ color: #4CAF50; font-size: 20px; }}
            .info {{ color: #aaa; margin-top: 20px; font-size: 14px; }}
            a {{ color: #4CAF50; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🛒 My Market Server</h1>
            <p class="status">✅ Сервер работает</p>
            <p class="info">Версия: {ВЕРСИЯ_СЕРВЕРА}</p>
            <p class="info">
                <a href="/catalog">📦 Каталог</a> ·
                <a href="/health">💚 Health</a>
            </p>
        </div>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "версия": ВЕРСИЯ_СЕРВЕРА,
        "каталог_есть": os.path.exists(ФАЙЛ_КАТАЛОГА),
        "приложений_в_папке": len(os.listdir(ПАПКА_ПРИЛОЖЕНИЙ))
            if os.path.isdir(ПАПКА_ПРИЛОЖЕНИЙ) else 0,
    })


@app.route("/catalog")
def catalog():
    return jsonify(прочитать_каталог())


@app.route("/catalog/count")
def catalog_count():
    данные = прочитать_каталог()
    return jsonify({"всего": len(данные.get("приложения", []))})


# ⚠️ ВАЖНО: в URL-правилах Flask — только латиница!
@app.route("/file/<name>")
def скачать_файл(name):
    имя_безопасное = os.path.basename(name)
    путь = os.path.join(ПАПКА_ПРИЛОЖЕНИЙ, имя_безопасное)
    if not os.path.exists(путь):
        return jsonify({"ошибка": f"Файл {имя_безопасное} не найден"}), 404
    return send_from_directory(
        ПАПКА_ПРИЛОЖЕНИЙ, имя_безопасное,
        as_attachment=True,
        download_name=имя_безопасное,
    )


@app.route("/icon/<name>")
def скачать_иконку(name):
    имя_безопасное = os.path.basename(name)
    путь = os.path.join(ПАПКА_ИКОНОК, имя_безопасное)
    if not os.path.exists(путь):
        return jsonify({"ошибка": f"Иконка {имя_безопасное} не найдена"}), 404
    return send_from_directory(ПАПКА_ИКОНОК, имя_безопасное)


@app.route("/hash/<name>")
def хеш_файла(name):
    имя_безопасное = os.path.basename(name)
    путь = os.path.join(ПАПКА_ПРИЛОЖЕНИЙ, имя_безопасное)
    if not os.path.exists(путь):
        return jsonify({"ошибка": f"Файл {имя_безопасное} не найден"}), 404
    return jsonify({
        "файл": имя_безопасное,
        "хеш": посчитать_хеш(путь),
        "размер": os.path.getsize(путь),
    })


# ==========================================================
#  ЗАПУСК (для локальной отладки)
# ==========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
