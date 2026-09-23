# Nexa AI

## Smart Digital Workspace

Nexa AI is a Smart Digital Workspace designed to bring multiple useful digital tasks together in one application.

It provides a simple web-based interface where users can interact with AI through text and perform everyday digital tasks from a single workspace.

## Features

* **Ask AI** — Get AI-powered text responses
* **Task Management** — Create, view, and delete tasks
* **Email** — Send emails directly from the application
* **WhatsApp** — Send WhatsApp messages
* **Google Search** — Search the web through the application
* **Wikipedia Search** — Get information from Wikipedia
* **Time** — Get the current time
* **Clear Chat** — Clear the current AI conversation/memory

## Technologies Used

* Python
* FastAPI
* Flask
* HTML
* CSS
* JavaScript
* OpenAI API
* Requests
* python-dotenv

## Architecture

Nexa AI uses a Flask frontend connected to a FastAPI backend.

```text
User
  ↓
Flask Frontend
  ↓
FastAPI Backend
  ↓
AI & Digital Task Services
```

## Security

Sensitive information such as API keys, email credentials, and other secrets are stored using environment variables.

The `.env` file is excluded from version control using `.gitignore`.

## Installation

Clone the repository and install the required dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add the required environment variables.

Then run the Flask frontend and FastAPI backend.

## Purpose

Nexa AI is built as a practical Smart Digital Workspace that combines AI-powered assistance and useful digital services into one application.

## Disclaimer

This project is developed for learning, development, and demonstration purposes.
