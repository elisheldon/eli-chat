import { pipeline } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.1';

let generator = null;
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

// Function to load the model asynchronously with a loading indicator
async function loadModel() {
    displayMessage("Loading model, please wait...", false);  // Initial loading message
    try {
        console.log('Loading model...');
        generator = await pipeline('text-generation', 'elisheldon/Meta-Llama3.2-1B-Instruct-FT', { dtype: 'q4f16', device: 'wasm' });
        //generator = await pipeline('text-generation', 'onnx-community/Llama-3.2-1B-Instruct-q4f16', { dtype: 'q4f16', device: 'webgpu' });
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

// Call the model loading function at the start of the script
loadModel();

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
                const output = await generator(messages, { max_new_tokens: 24 });
                const response = output[0].generated_text.at(-1).content;
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
