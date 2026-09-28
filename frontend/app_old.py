
import streamlit as st
import requests


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Jarvis AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# FASTAPI URL
# =========================================================

API_URL = "http://127.0.0.1:8000"


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        margin-top: 0px;
        margin-bottom: 30px;
    }

    .status-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #444;
        margin-bottom: 20px;
    }

    .feature-box {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #444;
        min-height: 130px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# API HELPER
# =========================================================

def api_request(method, endpoint, json_data=None):

    try:

        if method == "GET":
            response = requests.get(
                f"{API_URL}{endpoint}",
                timeout=60
            )

        elif method == "POST":
            response = requests.post(
                f"{API_URL}{endpoint}",
                json=json_data,
                timeout=60
            )

        elif method == "DELETE":
            response = requests.delete(
                f"{API_URL}{endpoint}",
                timeout=60
            )

        else:
            return None, "Unsupported HTTP method"

        return response, None

    except requests.exceptions.ConnectionError:

        return None, (
            "Could not connect to FastAPI server. "
            "Make sure FastAPI is running."
        )

    except requests.exceptions.Timeout:

        return None, "Request timed out."

    except Exception as e:

        return None, str(e)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🤖 Jarvis")

    st.caption("AI Voice Assistant")

    st.divider()

    menu = st.radio(
        "MAIN MENU",
        [
            "🏠 Dashboard",
            "💬 Ask AI",
            "📝 Tasks",
            "📧 Send Email",
            "📱 WhatsApp",
            "🔎 Search",
            "🖼️ Generate Image",
            "⏰ Current Time",
            "⚙️ Settings"
        ]
    )

    st.divider()

    st.caption("Backend")

    if st.button("🔄 Check API"):

        response, error = api_request(
            "GET",
            "/"
        )

        if error:
            st.error(error)

        elif response.status_code == 200:
            st.success("FastAPI is Online ✅")

        else:
            st.error(
                f"API Error: {response.status_code}"
            )


# =========================================================
# DASHBOARD
# =========================================================

if menu == "🏠 Dashboard":

    st.markdown(
        '<p class="main-title">🤖 Jarvis AI Assistant</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">Your personal AI-powered assistant</p>',
        unsafe_allow_html=True
    )

    st.info(
        "Use the menu on the left to access Jarvis features."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            <div class="feature-box">
                <h3>💬 Ask AI</h3>
                <p>Chat with your AI assistant.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="feature-box">
                <h3>📝 Tasks</h3>
                <p>Create and view your tasks.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            """
            <div class="feature-box">
                <h3>📧 Communication</h3>
                <p>Send Email and WhatsApp messages.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    col4, col5, col6 = st.columns(3)

    with col4:

        st.markdown(
            """
            <div class="feature-box">
                <h3>🔎 Search</h3>
                <p>Search Google and Wikipedia.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col5:

        st.markdown(
            """
            <div class="feature-box">
                <h3>🖼️ Images</h3>
                <p>Generate images using AI.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col6:

        st.markdown(
            """
            <div class="feature-box">
                <h3>⏰ Time</h3>
                <p>Check the current time.</p>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# ASK AI
# =========================================================

elif menu == "💬 Ask AI":

    st.header("💬 Ask AI")

    st.write(
        "Ask anything and continue your conversation."
    )

    # Display frontend conversation
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.write(message["content"])

    user_text = st.chat_input(
        "Type your message..."
    )

    if user_text:

        # Show user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_text
            }
        )

        with st.chat_message("user"):
            st.write(user_text)

        response, error = api_request(
            "POST",
            "/ask-ai",
            {
                "user_text": user_text
            }
        )

        if error:

            st.error(error)

        elif response.status_code == 200:

            data = response.json()

            answer = data.get(
                "response",
                "No response received."
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            with st.chat_message("assistant"):
                st.write(answer)

        else:

            st.error(
                f"API Error {response.status_code}: "
                f"{response.text}"
            )

    st.divider()

    if st.button("🗑️ Clear AI Memory"):

        response, error = api_request(
            "DELETE",
            "/clear-chat"
        )

        if error:

            st.error(error)

        elif response.status_code == 200:

            st.session_state.messages = []

            st.success(
                "AI conversation memory cleared."
            )

            st.rerun()

        else:

            st.error(
                f"API Error: {response.status_code}"
            )


# =========================================================
# TASKS
# =========================================================

elif menu == "📝 Tasks":

    st.header("📝 Task Manager")

    task_menu = st.radio(
        "Choose an action",
        [
            "Create Task",
            "View Tasks",
            "Task Notification"
        ],
        horizontal=True
    )

    # -----------------------------------------------------
    # CREATE TASK
    # -----------------------------------------------------

    if task_menu == "Create Task":

        task = st.text_input(
            "Enter your task",
            placeholder="e.g. Study Python at 8 PM"
        )

        if st.button(
            "➕ Add Task",
            use_container_width=True
        ):

            if task.strip() == "":

                st.warning(
                    "Please enter a task."
                )

            else:

                response, error = api_request(
                    "POST",
                    "/create-task",
                    {
                        "task": task
                    }
                )

                if error:

                    st.error(error)

                elif response.status_code == 200:

                    data = response.json()

                    st.success(
                        data.get(
                            "message",
                            "Task added successfully."
                        )
                    )

                else:

                    st.error(
                        f"API Error {response.status_code}: "
                        f"{response.text}"
                    )

    # -----------------------------------------------------
    # VIEW TASKS
    # -----------------------------------------------------

    elif task_menu == "View Tasks":

        if st.button(
            "🔄 Load Tasks",
            use_container_width=True
        ):

            response, error = api_request(
                "GET",
                "/tasks"
            )

            if error:

                st.error(error)

            elif response.status_code == 200:

                data = response.json()

                tasks = data.get(
                    "tasks",
                    []
                )

                if tasks:

                    for index, task in enumerate(
                        tasks,
                        start=1
                    ):

                        st.write(
                            f"**{index}.** {task}"
                        )

                else:

                    st.info(
                        "No tasks found."
                    )

            else:

                st.error(
                    f"API Error {response.status_code}"
                )

    # -----------------------------------------------------
    # NOTIFICATION
    # -----------------------------------------------------

    elif task_menu == "Task Notification":

        st.write(
            "Show today's tasks as a desktop notification."
        )

        if st.button(
            "🔔 Show Tasks",
            use_container_width=True
        ):

            response, error = api_request(
                "POST",
                "/show-tasks"
            )

            if error:

                st.error(error)

            elif response.status_code == 200:

                data = response.json()

                st.success(
                    data.get(
                        "message",
                        "Notification sent."
                    )
                )

            else:

                st.error(
                    f"API Error {response.status_code}"
                )


# =========================================================
# SEND EMAIL
# =========================================================

elif menu == "📧 Send Email":

    st.header("📧 Send Email")

    st.write(
        "Send an email through your configured email account."
    )

    email_message = st.text_area(
        "Email Message",
        placeholder="Write your email message here...",
        height=180
    )

    if st.button(
        "📤 Send Email",
        use_container_width=True
    ):

        if email_message.strip() == "":

            st.warning(
                "Please enter a message."
            )

        else:

            response, error = api_request(
                "POST",
                "/send-email",
                {
                    "message": email_message
                }
            )

            if error:

                st.error(error)

            elif response.status_code == 200:

                data = response.json()

                st.success(
                    data.get(
                        "message",
                        "Email sent successfully."
                    )
                )

            else:

                st.error(
                    f"API Error {response.status_code}: "
                    f"{response.text}"
                )


# =========================================================
# WHATSAPP
# =========================================================

elif menu == "📱 WhatsApp":

    st.header("📱 Send WhatsApp")

    st.write(
        "Send a WhatsApp message using your configured number."
    )

    whatsapp_message = st.text_area(
        "WhatsApp Message",
        placeholder="Write your WhatsApp message...",
        height=180
    )

    if st.button(
        "📲 Send WhatsApp",
        use_container_width=True
    ):

        if whatsapp_message.strip() == "":

            st.warning(
                "Please enter a message."
            )

        else:

            response, error = api_request(
                "POST",
                "/send-whatsapp",
                {
                    "message": whatsapp_message
                }
            )

            if error:

                st.error(error)

            elif response.status_code == 200:

                data = response.json()

                st.success(
                    data.get(
                        "message",
                        "WhatsApp message scheduled."
                    )
                )

            else:

                st.error(
                    f"API Error {response.status_code}: "
                    f"{response.text}"
                )


# =========================================================
# SEARCH
# =========================================================

elif menu == "🔎 Search":

    st.header("🔎 Search")

    search_type = st.radio(
        "Search Engine",
        [
            "Wikipedia",
            "Google"
        ],
        horizontal=True
    )

    query = st.text_input(
        "Search Query",
        placeholder="Enter your search..."
    )

    if st.button(
        "🔍 Search",
        use_container_width=True
    ):

        if query.strip() == "":

            st.warning(
                "Please enter a search query."
            )

        else:

            if search_type == "Wikipedia":

                response, error = api_request(
                    "POST",
                    "/search-wikipedia",
                    {
                        "query": query
                    }
                )

                if error:

                    st.error(error)

                elif response.status_code == 200:

                    data = response.json()

                    st.subheader(
                        f"Result for: {query}"
                    )

                    st.write(
                        data.get(
                            "result",
                            "No result found."
                        )
                    )

                else:

                    st.error(
                        f"Wikipedia Error "
                        f"{response.status_code}: "
                        f"{response.text}"
                    )

            else:

                response, error = api_request(
                    "POST",
                    "/search-google",
                    {
                        "query": query
                    }
                )

                if error:

                    st.error(error)

                elif response.status_code == 200:

                    data = response.json()

                    st.success(
                        data.get(
                            "message",
                            "Google search opened."
                        )
                    )

                else:

                    st.error(
                        f"Google Error "
                        f"{response.status_code}"
                    )


# =========================================================
# IMAGE GENERATION
# =========================================================

elif menu == "🖼️ Generate Image":

    st.header("🖼️ AI Image Generation")

    st.write(
        "Describe the image you want to generate."
    )

    prompt = st.text_area(
        "Image Prompt",
        placeholder=(
            "Example: A futuristic city "
            "at sunset..."
        ),
        height=160
    )

    if st.button(
        "🎨 Generate Image",
        use_container_width=True
    ):

        if prompt.strip() == "":

            st.warning(
                "Please enter an image prompt."
            )

        else:

            response, error = api_request(
                "POST",
                "/generate-image",
                {
                    "prompt": prompt
                }
            )

            if error:

                st.error(error)

            elif response.status_code == 200:

                data = response.json()

                st.success(
                    data.get(
                        "message",
                        "Image generation completed."
                    )
                )

                st.info(
                    "The image generation module "
                    "handles the generated image."
                )

            else:

                st.error(
                    f"API Error {response.status_code}: "
                    f"{response.text}"
                )


# =========================================================
# CURRENT TIME
# =========================================================

elif menu == "⏰ Current Time":

    st.header("⏰ Current Time")

    st.write(
        "Get the current time from your FastAPI backend."
    )

    if st.button(
        "🕐 Get Current Time",
        use_container_width=True
    ):

        response, error = api_request(
            "GET",
            "/time"
        )

        if error:

            st.error(error)

        elif response.status_code == 200:

            data = response.json()

            st.metric(
                "Current Time",
                data.get(
                    "time",
                    "Unknown"
                )
            )

        else:

            st.error(
                f"API Error {response.status_code}"
            )


# =========================================================
# SETTINGS
# =========================================================

elif menu == "⚙️ Settings":

    st.header("⚙️ Settings")

    st.subheader("Backend Configuration")

    st.code(
        API_URL
    )

    st.write(
        "Your Streamlit frontend sends requests "
        "to this FastAPI backend."
    )

    st.divider()

    st.subheader("Available Endpoints")

    endpoints = [
        "GET  /",
        "POST /ask-ai",
        "DELETE /clear-chat",
        "GET  /time",
        "POST /create-task",
        "GET  /tasks",
        "POST /show-tasks",
        "GET  /open-youtube",
        "POST /open",
        "POST /search-wikipedia",
        "POST /search-google",
        "POST /send-whatsapp",
        "POST /send-email",
        "POST /generate-image"
    ]

    for endpoint in endpoints:

        st.code(endpoint)
