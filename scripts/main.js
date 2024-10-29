import * as webllm from "https://esm.run/@mlc-ai/web-llm";

let engine;
const chatMessagesContainer = document.getElementById('chat-messages');
const messageInputField = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');

// Disable input and send button initially
messageInputField.disabled = true;
sendButton.disabled = true;

const messages = [
    { role: "system", content: "You are Eli Sheldon, husband of Chrissie. You are chatting with Chrissie in an online messaging platform. You live in Seattle. You have a 4-year-old named Gabe and a 7-month-old named Aya, and a dog named Gus. Respond as Eli." },
];

// Helper function to add user messages to the messages array
function addUserMessage(content) {
    messages.push({ role: 'user', content });
}

// Helper function to add assistant messages to the messages array
function addAssistantMessage(content) {
    messages.push({ role: 'assistant', content });
}

// Function to display a message in the chat area
function displayMessage(message, isUserMessage) {
    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    messageElement.className = isUserMessage ? 'user-message' : 'assistant-message';
    chatMessagesContainer.appendChild(messageElement);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

// Create MLCEngine with custom weights
async function loadModel() {
    const selectedModel = "Meta-Llama3.2-1B-Instruct-q4f16_1-FT-MLC"
    try {
        displayMessage('Loading ' + selectedModel + '. Please wait...', false);  // Initial loading message
        console.log('Loading ' + selectedModel);
        const appConfig = {
            model_list: 
            [
                {
                    model: "https://huggingface.co/elisheldon/Meta-Llama3.2-1B-Instruct-FT-q4f16_1-MLC",
                    model_id: "Meta-Llama3.2-1B-Instruct-q4f16_1-FT-MLC",
                    model_lib:
                      webllm.modelLibURLPrefix +
                      webllm.modelVersion +
                      "/Llama-3.2-1B-Instruct-q4f16_1-ctx4k_cs1k-webgpu.wasm",
                    vram_required_MB: 879.04,
                    low_resource_required: true,
                    overrides: {
                      context_window_size: 4096,
                    },
                }
            ]
        }
        engine = await webllm.CreateMLCEngine(
            selectedModel,
            { appConfig: appConfig },
        );
        console.log('Model loaded.');
        displayMessage("Model loaded! You can start chatting.", false);

        // Re-enable input and send button once model is ready
        messageInputField.disabled = false;
        sendButton.disabled = false;
    } catch (error) {
        console.error('Failed to load model:', error);
        displayMessage('Error: Failed to load model. Please try again later.', false);
    }
}

await loadModel();

// Function to generate a response from the AI model
async function generateResponse() {
    sendButton.disabled = true;
    messageInputField.disabled = true;

    const userInput = messageInputField.value.trim();
    if (userInput) {
        addUserMessage(userInput);
        displayMessage(userInput, true);
        messageInputField.value = '';

        const typingIndicator = document.createElement('div');
        typingIndicator.textContent = 'Typing...';
        typingIndicator.className = 'assistant-message';
        chatMessagesContainer.appendChild(typingIndicator);
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

        setTimeout(async () => {
            try {
                // Generate response using Web-LLM
                const reply = await engine.chat.completions.create({
                    messages,
                    temperature: 0.4,
                    max_tokens: 64,
                });
                console.log(reply)
                const response = reply.choices[0].message.content;
                addAssistantMessage(response);

                chatMessagesContainer.removeChild(typingIndicator);
                displayMessage(response, false);
            } catch (error) {
                console.error('Error generating response:', error);
                chatMessagesContainer.removeChild(typingIndicator);
                displayMessage('Error: Could not generate a response. Please try again.', false);
            }

            sendButton.disabled = false;
            messageInputField.disabled = false;
        }, 0);
    }
}

// Event listener to handle user message submission
sendButton.addEventListener('click', () => {
    generateResponse();
});

// Allow pressing Enter to send messages
messageInputField.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendButton.click();
    }
});
