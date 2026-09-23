

// =====================================================
// JARVIS FRONTEND
// =====================================================


// =====================================================
// GLOBAL VARIABLES
// =====================================================

let searchEngine = "wikipedia";


// =====================================================
// DOM HELPERS
// =====================================================

function element(id) {

    return document.getElementById(id);

}



// =====================================================
// API REQUEST
// =====================================================

async function apiRequest(
    endpoint,
    method = "GET",
    data = null
) {

    try {

        const options = {

            method: method,

            headers: {
                "Content-Type": "application/json"
            }

        };


        if (data !== null) {

            options.body =
                JSON.stringify(data);

        }


        const response =
            await fetch(
                endpoint,
                options
            );


        // Read response body ONLY ONCE
        const responseText =
            await response.text();


        let result = {};

        if (responseText) {

            try {

                result =
                    JSON.parse(responseText);

            } catch {

                result = {
                    message: responseText
                };

            }

        }


        if (!response.ok) {

            throw new Error(
                result.detail ||
                result.message ||
                `API Error ${response.status}`
            );

        }


        return result;


    } catch (error) {

        console.error(
            "API Error:",
            error
        );

        throw error;

    }

}


// =====================================================
// NAVIGATION
// =====================================================

function showSection(sectionId) {

    const sections =
        document.querySelectorAll(".page-section");

    const navItems =
        document.querySelectorAll(".nav-item");


    sections.forEach(section => {

        section.classList.remove(
            "active-section"
        );

    });


    const target =
        element(sectionId);

    if (target) {

        target.classList.add(
            "active-section"
        );

    }


    navItems.forEach(item => {

        item.classList.remove("active");

        if (
            item.dataset.section ===
            sectionId
        ) {

            item.classList.add("active");

        }

    });


    const titleMap = {

        "dashboard": "Dashboard",

        "ask-ai": "Ask AI",

        "tasks": "Tasks",

        "email": "Send Email",

        "whatsapp": "WhatsApp",

        "search": "Search",

        // "image": "AI Image Generator",

        "time": "Current Time",

        "settings": "Settings"

    };


    element("page-title").textContent =
        titleMap[sectionId] || "Jarvis";

}


// =====================================================
// NAVIGATION EVENTS
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {


        document
            .querySelectorAll(
                "[data-section]"
            )
            .forEach(item => {

                item.addEventListener(
                    "click",
                    function () {

                        showSection(
                            this.dataset.section
                        );

                    }
                );

            });


        checkBackend();


        startLocalClock();

    }
);


// =====================================================
// ASK AI
// =====================================================

async function askAI() {

    const input =
        element("ai-input");

    const message =
        input.value.trim();


    if (!message) {

        return;

    }


    addChatMessage(
        message,
        "user"
    );


    input.value = "";


    const loading =
        addChatMessage(
            "Thinking...",
            "assistant"
        );


    try {

        const result =
            await apiRequest(
                "/ask-ai",
                "POST",
                {
                    user_text: message
                }
            );


        loading.remove();


        const answer =
            result.response ||
            result.answer ||
            result.message ||
            "No response received.";


        addChatMessage(
            answer,
            "assistant"
        );


    } catch (error) {

        loading.remove();


        addChatMessage(
            `Error: ${error.message}`,
            "assistant"
        );

    }

}


// =====================================================
// CHAT MESSAGE
// =====================================================

function addChatMessage(
    text,
    role
) {

    const container =
        element("chat-messages");


    const message =
        document.createElement("div");


    message.className =
        `message ${
            role === "user"
                ? "user-message"
                : "assistant-message"
        }`;


    const avatar =
        document.createElement("div");


    avatar.className =
        "message-avatar";


    avatar.textContent =
        role === "user"
            ? "👤"
            : "🤖";


    const content =
        document.createElement("div");


    content.className =
        "message-content";


    const name =
        document.createElement("span");


    name.className =
        "message-name";


    name.textContent =
        role === "user"
            ? "YOU"
            : "NEXA AI";


    const paragraph =
        document.createElement("p");


    paragraph.textContent =
        text;


    content.appendChild(name);

    content.appendChild(paragraph);


    message.appendChild(avatar);

    message.appendChild(content);


    container.appendChild(message);


    container.scrollTop =
        container.scrollHeight;


    return message;

}


// =====================================================
// ASK AI BUTTON
// =====================================================

element("send-ai")
    .addEventListener(
        "click",
        askAI
    );


// =====================================================
// ENTER KEY
// =====================================================

element("ai-input")
    .addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter"
            ) {

                event.preventDefault();

                askAI();

            }

        }
    );


// =====================================================
// CLEAR CHAT
// =====================================================

async function clearChat() {

    try {

        await apiRequest(
            "/clear-chat",
            "DELETE"
        );


        element(
            "chat-messages"
        ).innerHTML = "";


        addChatMessage(
            "Conversation memory cleared.",
            "assistant"
        );


    } catch (error) {

        console.error(error);

    }

}


// =====================================================
// CREATE TASK
// =====================================================

async function createTask() {

    const input =
        element("task-input");


    const task =
        input.value.trim();


    if (!task) {

        return;

    }


    try {

        const result =
            await apiRequest(
                "/create-task",
                "POST",
                {
                    task: task
                }
            );


        alert(
            result.message ||
            "Task created successfully."
        );


        input.value = "";


        loadTasks();


    } catch (error) {

        alert(
            `Error: ${error.message}`
        );

    }

}


// =====================================================
// LOAD TASKS
// =====================================================

async function loadTasks() {

    const container = element("task-list");

    container.innerHTML = "<p>Loading tasks...</p>";

    try {

        const result = await apiRequest(
            "/tasks",
            "GET"
        );

        const tasks = result.tasks || [];

        if (!tasks.length) {

            container.innerHTML =
                '<p class="empty-state">No tasks found.</p>';

            return;
        }

        container.innerHTML = "";

        tasks.forEach((task, index) => {

            const div = document.createElement("div");

            div.className = "task-item";

            const taskText = document.createElement("span");

            taskText.textContent =
                `${index + 1}. ${task}`;

            const deleteButton =
                document.createElement("button");

            deleteButton.textContent = "Delete";

            deleteButton.className =
                "delete-task-button";

            deleteButton.addEventListener(
                "click",
                () => deleteTask(index)
            );

            div.appendChild(taskText);
            div.appendChild(deleteButton);

            container.appendChild(div);

        });

    } catch (error) {

        container.innerHTML =
            `<p class="empty-state">
                Error: ${error.message}
             </p>`;

    }
}



// =====================================================
// DELETE TASK
// =====================================================
async function deleteTask(taskIndex) {
    const confirmed = confirm("Are you sure you want to delete this task?");

    if (!confirmed) {
        return;
    }

    try {
        const result = await apiRequest(
            `/delete-task/${taskIndex}`,
            "DELETE"
        );

        if (result.success) {
            alert(result.message || "Task deleted successfully.");
            loadTasks();
        }

    } catch (error) {
        alert(`Error deleting task: ${error.message}`);
    }
}


// ================================
// SEND EMAIL
// ================================

const sendEmailBtn = document.getElementById("sendEmailBtn");

if (sendEmailBtn) {
    sendEmailBtn.addEventListener("click", async () => {

        const senderEmail = document.getElementById("sender_email").value.trim();
        const appPassword = document.getElementById("app_password").value.trim();
        const receiverEmail = document.getElementById("receiver_email").value.trim();
        const subject = document.getElementById("email_subject").value.trim();
        const message = document.getElementById("email_message").value.trim();

        const emailStatus = document.getElementById("emailStatus");

        // Basic validation
        if (
            !senderEmail ||
            !appPassword ||
            !receiverEmail ||
            !subject ||
            !message
        ) {
            emailStatus.textContent = "Please fill in all fields.";
            return;
        }

        emailStatus.textContent = "Sending email...";
        sendEmailBtn.disabled = true;

        try {

            const response = await fetch("/send-email", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    sender_email: senderEmail,
                    app_password: appPassword,
                    receiver_email: receiverEmail,
                    subject: subject,
                    message: message
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {

                emailStatus.textContent = "Email sent successfully!";

                // Clear fields after successful sending
                document.getElementById("sender_email").value = "";
                document.getElementById("app_password").value = "";
                document.getElementById("receiver_email").value = "";
                document.getElementById("email_subject").value = "";
                document.getElementById("email_message").value = "";

            } else {

                emailStatus.textContent =
                    data.message || "Failed to send email.";
            }

        } catch (error) {

            console.error("Email Error:", error);

            emailStatus.textContent =
                "Could not connect to the Flask server.";

        } finally {

            sendEmailBtn.disabled = false;
        }
    });
}


// =====================================================
// SEND WHATSAPP
// =====================================================

const sendWhatsAppBtn = document.getElementById("sendWhatsAppBtn");

if (sendWhatsAppBtn) {
sendWhatsAppBtn.addEventListener("click", async () => {


    const countryCode =
        document.getElementById("country_code").value.trim();

    const phoneNumber =
        document.getElementById("whatsapp_number").value.trim();

    const message =
        document.getElementById("whatsapp_message").value.trim();

    const whatsappStatus =
        document.getElementById("whatsappStatus");

    // Check fields
    if (!countryCode || !phoneNumber || !message) {
        whatsappStatus.textContent =
            "Please fill in all fields.";
        return;
    }

    whatsappStatus.textContent =
        "Sending WhatsApp message...";

    sendWhatsAppBtn.disabled = true;

    try {

        const response = await fetch("/send-whatsapp", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                country_code: countryCode,
                phone_number: phoneNumber,
                message: message
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {

            whatsappStatus.textContent =
                "WhatsApp message sent successfully!";

            // Clear fields after success
            document.getElementById("country_code").value = "";
            document.getElementById("whatsapp_number").value = "";
            document.getElementById("whatsapp_message").value = "";

        } else {

            whatsappStatus.textContent =
                data.message || "Failed to send WhatsApp message.";
        }

    } catch (error) {

        console.error("WhatsApp Error:", error);

        whatsappStatus.textContent =
            "Could not connect to the Flask server.";

    } finally {

        sendWhatsAppBtn.disabled = false;
    }
});


}

// =====================================================
// RESULT BOX
// =====================================================

function showResult(
    box,
    message,
    success
) {

    box.textContent =
        message;


    box.className =
        success
            ? "result-box success"
            : "result-box error";

}


// =====================================================
// SEARCH
// =====================================================

async function performSearch() {

    const query =
        element(
            "search-input"
        ).value.trim();


    const resultBox =
        element(
            "search-result"
        );


    if (!query) {

        resultBox.textContent =
            "Please enter a search query.";

        return;

    }


    resultBox.textContent =
        "Searching...";


    try {

        let endpoint;


        if (
            searchEngine ===
            "wikipedia"
        ) {

            endpoint =
                "/search-wikipedia";

        } else {

            endpoint =
                "/search-google";

        }


        const result =
            await apiRequest(
                endpoint,
                "POST",
                {
                    query: query
                }
            );


        resultBox.textContent =
            result.result ||
            result.response ||
            result.message ||
            "No result received.";


    } catch (error) {

        resultBox.textContent =
            `Error: ${error.message}`;

    }

}


// =====================================================
// SEARCH ENGINE TABS
// =====================================================

element("wiki-tab")
    .addEventListener(
        "click",
        function () {

            searchEngine =
                "wikipedia";


            this.classList.add(
                "active"
            );


            element(
                "google-tab"
            ).classList.remove(
                "active"
            );

        }
    );


element("google-tab")
    .addEventListener(
        "click",
        function () {

            searchEngine =
                "google";


            this.classList.add(
                "active"
            );


            element(
                "wiki-tab"
            ).classList.remove(
                "active"
            );

        }
    );


// =====================================================
// IMAGE GENERATION
// =====================================================

// async function generateImage() {

//     const prompt =
//         element(
//             "image-prompt"
//         ).value.trim();


//     const resultBox =
//         element(
//             "image-result"
//         );


//     if (!prompt) {

//         resultBox.textContent =
//             "Please enter an image prompt.";

//         return;

//     }


//     resultBox.innerHTML =
//         "<p>Generating image...</p>";


//     try {

//         const result =
//             await apiRequest(
//                 "/generate-image",
//                 "POST",
//                 {
//                     prompt: prompt
//                 }
//             );


//         if (result.image_url) {

//             resultBox.innerHTML =
//                 `
//                 <img
//                     src="${result.image_url}"
//                     alt="Generated Image"
//                 >
//                 `;

//         } else {

//             resultBox.textContent =
//                 result.message ||
//                 "Image generation completed.";

//         }


//     } catch (error) {

//         resultBox.textContent =
//             `Error: ${error.message}`;

//     }

// }


// =====================================================
// SERVER TIME
// =====================================================

async function getServerTime() {

    try {

        const result =
            await apiRequest(
                "/time",
                "GET"
            );


        element(
            "current-time"
        ).textContent =
            result.time ||
            result.current_time ||
            "--:--:--";


    } catch (error) {

        element(
            "current-time"
        ).textContent =
            "API Error";

    }

}


// =====================================================
// LOCAL CLOCK
// =====================================================

function startLocalClock() {

    setInterval(
        function () {

            const now =
                new Date();


            const time =
                now.toLocaleTimeString();


            if (
                !element(
                    "current-time"
                ).textContent ||
                element(
                    "current-time"
                ).textContent ===
                "--:--:--"
            ) {

                element(
                    "current-time"
                ).textContent =
                    time;

            }

        },
        1000
    );

}


// =====================================================
// BACKEND CHECK
// =====================================================

async function checkBackend() {

    try {

        await apiRequest(
            "/"
        );


        element(
            "connection-text"
        ).textContent =
            "FastAPI Connected";


        if (
            element(
                "backend-status"
            )
        ) {

            element(
                "backend-status"
            ).textContent =
                "🟢 FastAPI is online";

        }


    } catch (error) {

        element(
            "connection-text"
        ).textContent =
            "FastAPI Offline";


        if (
            element(
                "backend-status"
            )
        ) {

            element(
                "backend-status"
            ).textContent =
                "🔴 FastAPI is offline";

        }

    }

}


// =====================================================
// MOBILE SIDEBAR
// =====================================================

element("mobile-menu")
    .addEventListener(
        "click",
        function () {

            document
                .querySelector(
                    ".sidebar"
                )
                .classList.toggle(
                    "open"
                );

        }
    );


// =====================================================
// BUTTON EVENTS
// =====================================================

element("create-task")
    .addEventListener(
        "click",
        createTask
    );


element("load-tasks")
    .addEventListener(
        "click",
        loadTasks
    );

element("search-button")
    .addEventListener(
        "click",
        performSearch
    );


// element("generate-image")
//     .addEventListener(
//         "click",
//         generateImage
//     );


element("get-time")
    .addEventListener(
        "click",
        getServerTime
    );


element("check-api")
    .addEventListener(
        "click",
        checkBackend
    );


// =====================================================
// ENTER KEY FOR SEARCH
// =====================================================

element("search-input")
    .addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter"
            ) {

                performSearch();

            }

        }
    );


// =====================================================
// VOICE INPUT
// =====================================================

const voiceButton =
    element("voice-button");


if (
    "webkitSpeechRecognition"
    in window
    ||
    "SpeechRecognition"
    in window
) {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    const recognition =
        new SpeechRecognition();


    recognition.lang =
        "en-US";


    recognition.continuous =
        false;


    recognition.interimResults =
        false;


    voiceButton.addEventListener(
        "click",
        function () {

            try {

                recognition.start();

                voiceButton.classList.add(
                    "listening"
                );

                voiceButton.textContent =
                    "🔴";

            } catch (error) {

                console.error(error);

            }

        }
    );


    recognition.onresult =
        function (event) {

            const transcript =
                event.results[0][0].transcript;


            element(
                "ai-input"
            ).value =
                transcript;


            askAI();

        };


    recognition.onend =
        function () {

            voiceButton.classList.remove(
                "listening"
            );

            voiceButton.textContent =
                "🎤";

        };


    recognition.onerror =
        function (event) {

            console.error(
                "Speech recognition error:",
                event.error
            );


            voiceButton.classList.remove(
                "listening"
            );

            voiceButton.textContent =
                "🎤";

        };

} else {

    voiceButton.disabled =
        true;


    voiceButton.title =
        "Speech recognition is not supported by this browser.";

}
