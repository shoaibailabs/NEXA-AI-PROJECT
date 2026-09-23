
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime
import random
import os
import webbrowser
import pyautogui
import wikipedia
import pywhatkit as pwk
from plyer import notification


import openai_request
# from image_generation import generate_image

from dotenv import load_dotenv
load_dotenv()
phone_number=os.getenv('phone_number')
gmail_password=os.getenv('gmail_password')
# from user_config import phone_number, gmail_password

import smtplib
from email.message import EmailMessage

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
    app_password: str
    receiver_email: EmailStr
    subject: str
    message: str

def send_email(sender_email, app_password, receiver_email, subject, message):
    try:
        # Create email
        email = EmailMessage()
        email["From"] = sender_email
        email["To"] = receiver_email
        email["Subject"] = subject
        email.set_content(message)

        # Connect to Gmail SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()

            # Login with sender Gmail + Gmail App Password
            server.login(sender_email, app_password)

            # Send email
            server.send_message(email)

        return {
            "success": True,
            "message": "Email sent successfully!"
        }

    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": "Gmail authentication failed. Check the email and Gmail App Password."
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

@app.post("/open")
def open_application(data: OpenAppRequest):

    application = data.application.strip()

    if application == "":
        raise HTTPException(
            status_code=400,
            detail="Application name cannot be empty"
        )

    try:

        pyautogui.press("super")
        pyautogui.typewrite(application)
        pyautogui.sleep(2)
        pyautogui.press("enter")

        return {
            "success": True,
            "message": f"Opening {application}"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

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


# =========================================================
# SEND EMAIL
# =========================================================

# @app.post("/send-email")
# def send_email(data: EmailRequest):

#     message = data.message.strip()

#     if message == "":
#         raise HTTPException(
#             status_code=400,
#             detail="Email message cannot be empty"
#         )

#     try:

#         pwk.send_mail(
#             "shaoibofficial059@gmail.com",
#             gmail_password,
#             "Hello",
#             message,
#             "headqurter1@gmail.com"
#         )

#         return {
#             "success": True,
#             "message": "Email sent successfully"
#         }

#     except Exception as e:

#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )

@app.post("/send-email")
def send_email_endpoint(data: EmailRequest):

    result = send_email(
        sender_email=data.sender_email,
        app_password=data.app_password,
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
