document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const chatBox = document.getElementById('chatBox');
    const messageForm = document.getElementById('messageForm');
    const messageInput = document.getElementById('messageInput');
    const deleteHistoryButton = document.getElementById('deleteHistory');

    // Make sessionId editable
    let sessionId = generateSessionId();
    
    // Initial message
    addWelcomeMessage();

    // Function to show welcome message
    function addWelcomeMessage() {
        addMessage("Hi! I'm your virtual assistant, how can I help you today?", true);
    }

    // Simplified function to clear the chat
    function clearChat() {
        // Clear the chat area
        chatBox.innerHTML = '';
        // Generate new session_id
        sessionId = generateSessionId();
        // Show welcome message
        addWelcomeMessage();
    }

    // Handle click on clear history button
    deleteHistoryButton.addEventListener('click', function() {
        try {
            clearChat();
        } catch (error) {
            console.error('Error while clearing history:', error);
            addMessage("Sorry, an error occurred while clearing the history. Please try again.", true);
        }
    });

    // Handle message submission
    messageForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;

        // Disable input and button while processing
        messageInput.disabled = true;
        messageInput.value = '';

        try {
            // Show user message
            addMessage(message, false);

            // Show loading indicator
            const loadingIndicator = addLoadingIndicator();

            // Send message to backend
            const response = await sendMessage(sessionId, message);
            
            // Remove loading indicator
            loadingIndicator.remove();

            // Process backend response
            if (response) {
                console.log('Backend response:', response); // For debugging
                let responseText = '';
                
                // Verify the specific structure of the response
                if (response.response && response.response.answer) {
                    responseText = response.response.answer;
                } else if (response.response) {
                    responseText = response.response;
                } else if (response.answer) {
                    responseText = response.answer;
                } else if (typeof response === 'string') {
                    responseText = response;
                } else {
                    console.log('Unrecognized response structure:', response);
                    throw new Error('Unrecognized response format');
                }

                if (responseText) {
                    addMessage(responseText, true);
                    // Ensure scroll after the response
                    scrollToBottom();
                }
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage("Sorry, an error occurred. Please try again.", true);
        } finally {
            // Re-enable input
            messageInput.disabled = false;
            messageInput.focus();
            // Ensure scroll to bottom
            scrollToBottom();
        }
    });

    // Improved function to scroll to the last message
    function scrollToBottom() {
        // Get the last message
        const messages = chatBox.getElementsByClassName('message');
        const lastMessage = messages[messages.length - 1];
        
        if (lastMessage) {
            // Use scrollIntoView for a more reliable scroll
            lastMessage.scrollIntoView({ behavior: 'smooth', block: 'end' });
            
            // Ensure it reaches the bottom after everything has been rendered
            setTimeout(() => {
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 100);
        }
    }

    // Function to add messages
    function addMessage(text, isBot) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isBot ? 'bot' : 'user'}`;

        if (isBot) {
            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'bot-avatar';
            const avatarImg = document.createElement('img');
            avatarImg.src = '/static/images/avatar.svg';
            avatarImg.alt = 'Bot Avatar';
            avatarDiv.appendChild(avatarImg);
            messageDiv.appendChild(avatarDiv);
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Process the text to convert <link> tags into hyperlinks
        const processLinks = (text) => {
            const linkRegex = /<link>(.*?)<\/link>/g;
            const parts = text.split(linkRegex);
            
            return parts.map((part, index) => {
                if (index % 2 === 0) {
                    // Normal text
                    const span = document.createElement('span');
                    span.textContent = part;
                    return span;
                } else {
                    // It's a link
                    const link = document.createElement('a');
                    link.href = part;
                    link.textContent = part;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.className = 'chat-link';
                    return link;
                }
            });
        };

        // Split the text into lines and process each one
        const lines = text.split(/\n/);
        
        lines.forEach((line, index) => {
            // Process the links in this line
            const elements = processLinks(line);
            
            // Add the elements of the line
            elements.forEach(element => {
                contentDiv.appendChild(element);
            });
            
            // Add a line break after each line, except the last one
            if (index < lines.length - 1) {
                contentDiv.appendChild(document.createElement('br'));
            }
        });

        messageDiv.appendChild(contentDiv);
        chatBox.appendChild(messageDiv);
        scrollToBottom();
    }

    function addLoadingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';

        // Add avatar
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'bot-avatar';
        const avatarImg = document.createElement('img');
        avatarImg.src = '/static/images/avatar.svg';
        avatarImg.alt = 'Bot Avatar';
        avatarDiv.appendChild(avatarImg);
        messageDiv.appendChild(avatarDiv);

        // Add loading indicator
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content loading';
        
        // Create the container of the writing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        
        // Add only the animated dots
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            dot.textContent = '.';
            typingDiv.appendChild(dot);
        }
        
        contentDiv.appendChild(typingDiv);
        messageDiv.appendChild(contentDiv);

        chatBox.appendChild(messageDiv);
        scrollToBottom();
        return messageDiv;
    }

    function generateSessionId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    async function sendMessage(sessionId, message) {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                sessionID: sessionId,
                query: message || ''
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }
});