$(document).ready(function() {
    $('#sidebarToggle').click(function() {
        $('.sidebar').toggleClass('active'); // Toggle para añadir o quitar la clase 'active' que muestra la barra lateral
    });

    // Función para manejar el envío del formulario de registro
    $('#register-form').on('submit', function(e) {
        e.preventDefault(); // Evitar que el formulario se envíe automáticamente
        
        if (!validateRegisterForm()) {
            return; // Si la validación del formulario falla, salir sin enviar
        }

        var email = document.forms["register-form"]["correo"].value;

        // Verificar si el correo ya está registrado
        $.ajax({
            url: '/check_email', // URL para verificar el correo
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ correo: email }),
            success: function(response) {
                if (response.exists) {
                    alert("El correo ya está registrado");
                } else {
                    // Si el correo no está registrado, enviar el formulario
                    $('#register-form')[0].submit();
                }
            },
            error: function(error) {
                console.error("Error al verificar el correo:", error);
            }
        });
    });

    // Función para validar el formulario de registro
    function validateRegisterForm() {
        var email = document.forms["register-form"]["correo"].value;
        var password = document.forms["register-form"]["password"].value;
        var emailPattern = /^[a-zA-Z0-9._%+-]+@unibarranquilla\.edu\.co$/;
        var passwordPattern = /^.{6,12}$/;  // Acepta cualquier carácter entre 6 y 12 caracteres

        if (!emailPattern.test(email)) {
            alert("El correo debe ser una dirección @unibarranquilla.edu.co");
            return false;
        }
        if (!passwordPattern.test(password)) {
            alert("La contraseña debe tener entre 6 y 12 caracteres.");
            return false;
        }
        return true;
    }

    // Funciones para el formulario de chat
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

        // Mostrar mensaje del usuario en el chat
        addMessage('user', message);

        // Enviar mensaje al servidor Flask
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'messageInput=' + encodeURIComponent(message)
        })
        .then(response => response.json())
        .then(data => {
            // Mostrar respuesta del chatbot
            var responses = data.response;
            responses.forEach(function(response) {
                if (typeof response === 'object' && response.hasOwnProperty('message') && response.hasOwnProperty('link')) {
                    addMessage('bot', response.message, response.link);
                } else {
                    addMessage('bot', response);
                }
            });

            // Limpiar campo de entrada
            messageInput.value = '';
        })
        .catch(error => {
            console.error('Error al enviar mensaje:', error);
        });
    }

    function addMessage(sender, message, link = null) {
        var messagesContainer = document.getElementById('messages');

        // Si hay contenido de bienvenida, eliminarlo al enviar el primer mensaje
        var placeholder = document.getElementById('placeholder');
        if (placeholder) {
            placeholder.remove();
        }

        var messageElement = document.createElement('div');
        messageElement.classList.add(sender === 'user' ? 'message-user' : 'message-bot');

        // Verificar si el mensaje incluye texto y un enlace
        if (link) {
            messageElement.innerHTML = `${message} <a href="${link}" target="_blank">${link}</a>`;
        } else {
            messageElement.textContent = message;
        }

        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Toggle para mostrar/ocultar la contraseña
    document.getElementById('togglePassword').addEventListener('click', function (e) {
        const password = document.getElementById('password');
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        this.classList.toggle('bi-eye');
        this.classList.toggle('bi-eye-slash');
    });
});

function showAlert() {
    // Crear el contenedor del desenfoque
    const blurOverlay = document.createElement('div');
    blurOverlay.className = 'blur-overlay';

    // Crear el contenedor de la alerta
    const alertContainer = document.createElement('div');
    alertContainer.className = 'alert-container';
    alertContainer.innerHTML = `
        <div class="alert-content">
            <div class="alert-header">
                <img src="/static/imagenes/crisis.png" alt="Advertencia" class="alert-icon"> 
                <h2>Advertencia</h2>
            </div>
            <p>Este NO es un bot conversacional y se encuentra en constante entrenamiento y mejora. 
            Si cuenta con alguna queja, problema, recomendación, crítica constructiva puede depositarlo en el apartado de Recomendaciones/Problemas. 
            El asistente virtual solo responde si la pregunta es específica y concreta. 
            Ten en cuenta que si necesitas más información de la que te puede brindar el asistente virtual, se recomienda que se acerque a bienestar en los horarios de 7:00 a.m - 7:00 p.m 
            o mandar un correo a bienestar@unibarranquilla.edu.co</p>
            <button class="alert-close" onclick="closeAlert();">Cerrar</button>
        </div>
    `;

    // Agregar el desenfoque y la alerta al body
    document.body.appendChild(blurOverlay);
    document.body.appendChild(alertContainer);
}

function closeAlert() {
    // Quitar la alerta y el desenfoque
    const alertContainer = document.querySelector('.alert-container');
    const blurOverlay = document.querySelector('.blur-overlay');
    if (alertContainer) {
        alertContainer.remove();
    }
    if (blurOverlay) {
        blurOverlay.remove();
    }
}
