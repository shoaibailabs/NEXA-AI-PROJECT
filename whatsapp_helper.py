from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pywhatkit as pwk


app = FastAPI(
    title="Nexa AI WhatsApp Helper"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5000",
        "http://localhost:5000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class WhatsAppRequest(BaseModel):
    country_code: str
    phone_number: str
    message: str


@app.get("/")
def home():
    return {
        "success": True,
        "message": "Nexa AI WhatsApp Helper is running"
    }


@app.post("/send-whatsapp")
def send_whatsapp(data: WhatsAppRequest):

    try:

        country_code = data.country_code.strip().replace(" ", "")
        phone_number = data.phone_number.strip().replace(" ", "")
        message = data.message.strip()

        if not country_code:
            return {
                "success": False,
                "message": "Country code is required."
            }

        if not phone_number:
            return {
                "success": False,
                "message": "WhatsApp number is required."
            }

        if not message:
            return {
                "success": False,
                "message": "Message is required."
            }

        if not country_code.startswith("+"):
            country_code = "+" + country_code

        if phone_number.startswith("0"):
            phone_number = phone_number[1:]

        if not country_code[1:].isdigit():
            return {
                "success": False,
                "message": "Invalid country code."
            }

        if not phone_number.isdigit():
            return {
                "success": False,
                "message": "Invalid WhatsApp number."
            }

        full_number = country_code + phone_number

        pwk.sendwhatmsg_instantly(
            full_number,
            message,
            wait_time=20,
            tab_close=False
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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5050
    )    