$(document).ready(function() {
    $('#chat-form').on('submit', function(e) {
        e.preventDefault();
        sendMessage();
    });

    function sendMessage() {
        var messageInput = document.getElementById('messageInput');
        var message = messageInput.value.trim();
        if (message === '') {
            return;
        }
        addMessage('user', message);
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'messageInput=' + encodeURIComponent(message)
        })
        .then(response => response.json())
        .then(data => {
            var responses = data.response;

            responses.forEach(function(response) {
                if (typeof response === 'string') {
                    addMessage('bot', response);
                } else if (typeof response === 'object') {
                    addMessage('bot', response.message, response.link);
                }
            });

            messageInput.value = '';
        })
        .catch(error => {
            console.error('Error al enviar mensaje:', error);
        });
    }

    function addMessage(sender, message, link = null) {
        var messagesContainer = document.getElementById('messages');
        var placeholder = document.getElementById('placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        var messageElement = document.createElement('div');
        messageElement.classList.add(sender === 'user' ? 'message-user' : 'message-bot');
        if (link) {
            messageElement.innerHTML = `${message} <a href="${link}" target="_blank">${link}</a>`;
        } else {
            messageElement.textContent = message;
        }
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});
