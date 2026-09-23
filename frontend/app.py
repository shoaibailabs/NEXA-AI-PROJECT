

from flask import Flask, render_template, request, jsonify
import requests


app = Flask(__name__)


# ==========================================
# FASTAPI BACKEND URL
# ==========================================

FASTAPI_URL = "http://127.0.0.1:8000"


# ==========================================
# HOME / FRONTEND PAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# ASK AI
# ==========================================

@app.route("/ask-ai", methods=["POST"])
def ask_ai():

    try:

        data = request.get_json()

        response = requests.post(
            f"{FASTAPI_URL}/ask-ai",
            json=data,
            timeout=60
        )

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:

        return jsonify({
            "error": "Could not connect to FastAPI",
            "details": str(e)
        }), 500


# ==========================================
# CREATE TASK
# ==========================================

@app.route("/create-task", methods=["POST"])
def create_task():

    try:

        data = request.get_json()

        response = requests.post(
            f"{FASTAPI_URL}/create-task",
            json=data,
            timeout=30
        )

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:

        return jsonify({
            "error": "Could not connect to FastAPI",
            "details": str(e)
        }), 500


# ==========================================
# GET TASKS
# ==========================================

@app.route("/tasks", methods=["GET"])
def get_tasks():

    try:

        response = requests.get(
            f"{FASTAPI_URL}/tasks",
            timeout=30
        )

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:

        return jsonify({
            "error": "Could not connect to FastAPI",
            "details": str(e)
        }), 500



# ==========================================
# DELETE TASK
# ==========================================

@app.route("/delete-task/<int:task_index>", methods=["DELETE"])
def delete_task(task_index):

    try:

        response = requests.delete(
            f"{FASTAPI_URL}/delete-task/{task_index}",
            timeout=30
        )

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:

        return jsonify({
            "error": "Could not connect to FastAPI",
            "details": str(e)
        }), 500


    

# ==========================================
# SEND EMAIL
# ==========================================

@app.route("/send-email", methods=["POST"])
def send_email():

    try:

        data = request.get_json()

        response = requests.post(
            f"{FASTAPI_URL}/send-email",
            json=data,
            timeout=60
        )

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:

        return jsonify({
            "error": "Could not connect to FastAPI",
            "details": str(e)
        }), 500


# ==========================================
# SEND WHATSAPP
# ==========================================

@app.route("/send-whatsapp", methods=["POST"])
def send_whatsapp():

    try:

        data = request.get_json()

        response = requests.post(
            f"{FASTAPI_URL}/send-whatsapp",
            json=data,
            timeout=60
        )

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:

        return jsonify({
            "error": "Could not connect to FastAPI",
            "details": str(e)
        }), 500


# ==========================================
# WIKIPEDIA SEARCH
# ==========================================

@app.route("/search-wikipedia", methods=["POST"])
def search_wikipedia():

    try:

        data = request.get_json()

        response = requests.post(
            f"{FASTAPI_URL}/search-wikipedia",
            json=data,
            timeout=60
        )

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:

        return jsonify({
            "error": "Could not connect to FastAPI",
            "details": str(e)
        }), 500


# ==========================================
# GOOGLE SEARCH
# ==========================================

@app.route("/search-google", methods=["POST"])
def search_google():

    try:

        data = request.get_json()

        response = requests.post(
            f"{FASTAPI_URL}/search-google",
            json=data,
            timeout=60
        )

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:

        return jsonify({
            "error": "Could not connect to FastAPI",
            "details": str(e)
        }), 500


# ==========================================
# IMAGE GENERATION
# ==========================================

# @app.route("/generate-image", methods=["POST"])
# def generate_image():

#     try:

#         data = request.get_json()

#         response = requests.post(
#             f"{FASTAPI_URL}/generate-image",
#             json=data,
#             timeout=120
#         )

#         return jsonify(response.json()), response.status_code

#     except requests.exceptions.RequestException as e:

#         return jsonify({
#             "error": "Could not connect to FastAPI",
#             "details": str(e)
#         }), 500


# ==========================================
# CLEAR CHAT / MEMORY
# ==========================================

@app.route("/clear-chat", methods=["DELETE"])
def clear_chat():

    try:

        response = requests.delete(
            f"{FASTAPI_URL}/clear-chat",
            timeout=30
        )

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:

        return jsonify({
            "error": "Could not connect to FastAPI",
            "details": str(e)
        }), 500


# ==========================================
# TIME
# ==========================================

@app.route("/time", methods=["GET"])
def get_time():

    try:

        response = requests.get(
            f"{FASTAPI_URL}/time",
            timeout=30
        )

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:

        return jsonify({
            "error": "Could not connect to FastAPI",
            "details": str(e)
        }), 500


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/health", methods=["GET"])
def health():

    try:

        response = requests.get(
            f"{FASTAPI_URL}/",
            timeout=10
        )

        return jsonify({
            "flask": "online",
            "fastapi": "online",
            "fastapi_status": response.status_code
        })

    except requests.exceptions.RequestException as e:

        return jsonify({
            "flask": "online",
            "fastapi": "offline",
            "details": str(e)
        }), 503


# ==========================================
# RUN FLASK
# ==========================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
