from fastapi import FastAPI, HTTPException
from fastapi import Request
from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime
import random
import os
import webbrowser
# import pyautogui
import wikipedia

# import pywhatkit as pwk
import platform
if platform.system() == "Windows":
    import pywhatkit as pwk
else:
    pwk = None

from plyer import notification


# import openai_request
from . import openai_request
# from image_generation import generate_image

from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
import json
import secrets
import base64
from email.mime.text import MIMEText


GOOGLE_CLIENT_SECRET_FILE = os.getenv("GOOGLE_CLIENT_SECRET_JSON")

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]
oauth_sessions = {}

from dotenv import load_dotenv
load_dotenv()
phone_number=os.getenv('phone_number')
gmail_password=os.getenv('gmail_password')
# from user_config import phone_number, gmail_password

# import smtplib
# from email.message import EmailMessage
import resend

app = FastAPI(
    title="Jarvis Voice Assistant API",
    description="FastAPI backend for my Voice Assistant",
    version="1.0.0"
)


# =========================================================
# TEMPORARY CHAT MEMORY
# =========================================================

chat_history = []


# =========================================================
# PYDANTIC MODELS
# =========================================================

class AIRequest(BaseModel):
    user_text: str


class TaskRequest(BaseModel):
    task: str

class WhatsAppRequest(BaseModel):
    country_code: str
    phone_number: str
    message: str


def send_whatsapp(country_code: str, phone_number: str, message: str):
    try:
        # Remove spaces from country code and phone number
        country_code = country_code.strip().replace(" ", "")
        phone_number = phone_number.strip().replace(" ", "")

        # Country code must start with +
        if not country_code.startswith("+"):
            country_code = "+" + country_code

        # Remove leading 0 from local number
        if phone_number.startswith("0"):
            phone_number = phone_number[1:]

        # Final international WhatsApp number
        full_number = country_code + phone_number

        # Basic validation
        if not phone_number.isdigit():
            return {
                "success": False,
                "message": "Please enter a valid WhatsApp phone number."
            }

        if not country_code[1:].isdigit():
            return {
                "success": False,
                "message": "Please enter a valid country code, for example +92."
            }

        pwk.sendwhatmsg_instantly(
            full_number,
            message,
            wait_time=40,
            tab_close=True,
            close_time=3
        )

        return {
            "success": True,
            "message": "WhatsApp message sent successfully!"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"WhatsApp sending failed: {str(e)}"
        }


# class EmailRequest(BaseModel):
#     message: str


class EmailRequest(BaseModel):
    sender_email: EmailStr
    receiver_email: EmailStr
    subject: str
    message: str

def send_email(sender_email, receiver_email, subject, message):
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        if not os.path.exists("token.json"):
            return {
                "success": False,
                "message": "Gmail is not connected. Please connect Gmail first."
            }

        credentials = Credentials.from_authorized_user_file(
            "token.json",
            GOOGLE_SCOPES
        )

        if not credentials or not credentials.valid:
            return {
                "success": False,
                "message": "Gmail authorization is not valid. Please connect Gmail again."
            }

        service = build("gmail", "v1", credentials=credentials)

        email_message = MIMEText(message)
        email_message["to"] = receiver_email
        email_message["subject"] = subject

        encoded_message = base64.urlsafe_b64encode(
            email_message.as_bytes()
        ).decode()

        body = {
            "raw": encoded_message
        }

        sent_email = service.users().messages().send(
            userId="me",
            body=body
        ).execute()

        return {
            "success": True,
            "message": "Email sent successfully through Gmail!",
            "email_id": sent_email.get("id")
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Email sending failed: {str(e)}"
        }
# class ImageRequest(BaseModel):
#     prompt: str


class SearchRequest(BaseModel):
    query: str


class OpenAppRequest(BaseModel):
    application: str


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "Jarvis Voice Assistant API is running"
    }

@app.get("/health")
def health():
    return {"status": "ok"}


# =========================================================
# AI / OPENAI
# =========================================================

@app.post("/ask-ai")
def ask_ai(data: AIRequest):

    try:

        # Add user message to temporary memory
        chat_history.append({
            "role": "user",
            "content": data.user_text
        })

        # Send complete conversation to OpenAI
        response = openai_request.send_request(chat_history)

        # Save AI response
        chat_history.append({
            "role": "assistant",
            "content": response
        })

        return {
            "success": True,
            "user_text": data.user_text,
            "response": response
        }

    except Exception as e:

        # Remove last user message if request failed
        if chat_history and chat_history[-1]["role"] == "user":
            chat_history.pop()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# CLEAR AI CHAT
# =========================================================

@app.delete("/clear-chat")
def clear_chat():

    chat_history.clear()

    return {
        "success": True,
        "message": "Chat memory cleared successfully"
    }


# =========================================================
# GET CURRENT TIME
# =========================================================

@app.get("/time")
def get_time():

    current_time = datetime.datetime.now().strftime("%H:%M")

    return {
        "success": True,
        "time": current_time
    }


# =========================================================
# CREATE TASK
# =========================================================

@app.post("/create-task")
def create_task(data: TaskRequest):

    task = data.task.strip()

    if task == "":
        raise HTTPException(
            status_code=400,
            detail="Task cannot be empty"
        )

    try:

        with open("task.txt", "a", encoding="utf-8") as file:
            file.write(task + "\n")

        return {
            "success": True,
            "message": f"Task added: {task}"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# GET TASKS
# =========================================================

@app.get("/tasks")
def get_tasks():

    try:

        if not os.path.exists("task.txt"):
            return {
                "success": True,
                "tasks": []
            }

        with open("task.txt", "r", encoding="utf-8") as file:
            tasks = file.readlines()

        tasks = [task.strip() for task in tasks if task.strip()]

        return {
            "success": True,
            "tasks": tasks
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    

# =========================================================
# DELETE TASK
# =========================================================

@app.delete("/delete-task/{task_index}")
def delete_task(task_index: int):

    try:

        if not os.path.exists("task.txt"):
            raise HTTPException(
                status_code=404,
                detail="No tasks found"
            )

        # Read all tasks
        with open("task.txt", "r", encoding="utf-8") as file:
            tasks = [
                task.strip()
                for task in file.readlines()
                if task.strip()
            ]

        # Check task number
        if task_index < 0 or task_index >= len(tasks):
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        # Remove selected task
        deleted_task = tasks.pop(task_index)

        # Save remaining tasks
        with open("task.txt", "w", encoding="utf-8") as file:
            for task in tasks:
                file.write(task + "\n")

        return {
            "success": True,
            "message": f"Task deleted: {deleted_task}",
            "deleted_task": deleted_task
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )



    
# =========================================================
# SPEAK TASKS
# =========================================================

@app.get("/speak-tasks")
def speak_tasks():

    try:

        if not os.path.exists("task.txt"):
            return {
                "success": True,
                "message": "No tasks found"
            }

        with open("task.txt", "r", encoding="utf-8") as file:
            tasks = file.read()

        if tasks.strip() == "":
            return {
                "success": True,
                "message": "No tasks found"
            }

        return {
            "success": True,
            "message": f"Work we have to do today: {tasks}"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# SHOW TASK NOTIFICATION
# =========================================================

@app.post("/show-tasks")
def show_tasks():

    try:

        if not os.path.exists("task.txt"):
            return {
                "success": True,
                "message": "No tasks found"
            }

        with open("task.txt", "r", encoding="utf-8") as file:
            tasks = file.read()

        if tasks.strip() == "":
            return {
                "success": True,
                "message": "No tasks found"
            }

        notification.notify(
            title="Today's Tasks",
            message=tasks
        )

        return {
            "success": True,
            "message": "Task notification displayed"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# OPEN YOUTUBE
# =========================================================

@app.get("/open-youtube")
def open_youtube():

    try:

        webbrowser.open("https://www.youtube.com")

        return {
            "success": True,
            "message": "YouTube opened"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# OPEN APPLICATION / SEARCH FROM WINDOWS
# =========================================================

# @app.post("/open")
# def open_application(data: OpenAppRequest):

#     application = data.application.strip()

#     if application == "":
#         raise HTTPException(
#             status_code=400,
#             detail="Application name cannot be empty"
#         )

#     try:

        # pyautogui.press("super")
        # pyautogui.typewrite(application)
        # pyautogui.sleep(2)
        # pyautogui.press("enter")

        # return {
        #     "success": True,
        #     "message": f"Opening {application}"
        # }

    # except Exception as e:

    #     raise HTTPException(
    #         status_code=500,
    #         detail=str(e)
    #     )

# =========================================================
# WIKIPEDIA SEARCH
# =========================================================

@app.post("/search-wikipedia")
def search_wikipedia(data: SearchRequest):

    query = data.query.strip()

    # Empty query check
    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    try:

        # -------------------------------------------------
        # STEP 1: Try direct Wikipedia summary
        # -------------------------------------------------
        try:

            result = wikipedia.summary(
                query,
                sentences=5,
                auto_suggest=True,
                redirect=True
            )

            if result and result.strip():

                return {
                    "success": True,
                    "query": query,
                    "result": result
                }

        except Exception:
            pass


        # -------------------------------------------------
        # STEP 2: Search Wikipedia for related articles
        # -------------------------------------------------

        search_results = wikipedia.search(
            query,
            results=10,
            suggestion=True
        )

        # If nothing was found
        if not search_results:

            return {
                "success": False,
                "query": query,
                "result": (
                    f"No Wikipedia article was found for '{query}'. "
                    "Try using a more specific search term."
                )
            }


        # -------------------------------------------------
        # STEP 3: Try every search result
        # -------------------------------------------------

        for title in search_results:

            try:

                result = wikipedia.summary(
                    title,
                    sentences=5,
                    auto_suggest=False,
                    redirect=True
                )

                if result and result.strip():

                    return {
                        "success": True,
                        "query": query,
                        "matched_title": title,
                        "result": result
                    }

            except Exception:
                continue


        # -------------------------------------------------
        # STEP 4: Last fallback
        # -------------------------------------------------

        first_title = search_results[0]

        return {
            "success": True,
            "query": query,
            "matched_title": first_title,
            "result": (
                f"I found a related Wikipedia article: "
                f"{first_title}. "
                "Please search using this exact topic if you need "
                "more specific information."
            )
        }


    # -----------------------------------------------------
    # FINAL ERROR HANDLER
    # -----------------------------------------------------

    except Exception as e:

        return {
            "success": False,
            "query": query,
            "result": (
                "Wikipedia search could not be completed right now. "
                f"Error: {str(e)}"
            )
        }



# =========================================================
# GOOGLE SEARCH
# =========================================================

@app.post("/search-google")
def search_google(data: SearchRequest):

    query = data.query.strip()

    if query == "":
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    try:

        url = "https://www.google.com/search?q=" + query

        webbrowser.open(url)

        return {
            "success": True,
            "message": f"Google search opened for: {query}",
            "query": query
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# SEND WHATSAPP
# =========================================================

@app.post("/send-whatsapp")
def send_whatsapp_endpoint(data: WhatsAppRequest):

    result = send_whatsapp(
        country_code=data.country_code,
        phone_number=data.phone_number,
        message=data.message
    )

    return result


@app.post("/send-email")
def send_email_endpoint(data: EmailRequest):

    result = send_email(
        sender_email=data.sender_email,
        receiver_email=data.receiver_email,
        subject=data.subject,
        message=data.message
    )

    return result


# =========================================================
# GENERATE IMAGE
# =========================================================

# @app.post("/generate-image")
# def generate_image_api(data: ImageRequest):

#     prompt = data.prompt.strip()

#     if prompt == "":
#         raise HTTPException(
#             status_code=400,
#             detail="Image prompt cannot be empty"
#         )

#     try:

#         generate_image(prompt)

#         return {
#             "success": True,
#             "message": "Image generation request completed"
#         }

#     except Exception as e:

#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )


@app.get("/auth/gmail")
def gmail_login():
    flow = Flow.from_client_config(
        json.loads(GOOGLE_CLIENT_SECRET_FILE),
        scopes=GOOGLE_SCOPES,
        redirect_uri="https://nexa-ai-project.onrender.com/auth/gmail/callback"
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    oauth_sessions[state] = {
        "code_verifier": flow.code_verifier
    }

    return RedirectResponse(authorization_url)


@app.get("/auth/gmail/callback")
def gmail_callback(code: str, state: str):
    try:
        session_data = oauth_sessions.get(state)

        if not session_data:
            return {
                "success": False,
                "message": "OAuth session not found or expired."
            }

        flow = Flow.from_client_config(
            json.loads(GOOGLE_CLIENT_SECRET_FILE),
            scopes=GOOGLE_SCOPES,
            redirect_uri="https://nexa-ai-project.onrender.com/auth/gmail/callback",
            state=state
        )

        flow.code_verifier = session_data["code_verifier"]

        flow.fetch_token(code=code)

        credentials = flow.credentials

        with open("token.json", "w") as token:
            token.write(credentials.to_json())

        oauth_sessions.pop(state, None)

        return {
            "success": True,
            "message": "Gmail connected successfully!"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Gmail connection failed: {str(e)}"
        }