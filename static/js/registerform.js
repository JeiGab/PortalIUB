$(document).ready(function() {
    // Función para manejar el envío del formulario de registro
    $('#register-form').on('submit', function(e) {
        e.preventDefault();
        if (!validateRegisterForm()) {
            return;
        }
        var email = document.forms["register-form"]["correo"].value;
        $.ajax({
            url: '/check_email',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ correo: email }),
            success: function(response) {
                if (response.exists) {
                    alert("El correo ya está registrado");
                } else {
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
        var passwordPattern = /^.{6,12}$/;
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
});
